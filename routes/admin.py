try:
    import psutil
except ImportError:
    psutil = None
from pathlib import Path
from flask import Blueprint, render_template, redirect, url_for, flash, request, current_app, jsonify
from flask_login import login_required, current_user
from extensions import db
from models.user import User
from models.resume import Resume
from models.report import Report
from models.job import JobMatch
from models.admin_log import AdminLog
from utils.security import admin_required, super_admin_required

admin_bp = Blueprint("admin", __name__)


@admin_bp.route("/")
@login_required
@admin_required
def index():
    """
    Admin Dashboard Overview.
    Does NOT show all users. Shows metrics, Latest 10 users, Latest uploads,
    Latest reports, System health, Storage & API usage.
    """
    total_users = User.query.count()
    total_resumes = Resume.query.count()
    total_reports = Report.query.count()
    total_matches = JobMatch.query.count()

    # Metrics by Role & Status
    active_users = User.query.filter_by(is_active=True).count()
    blocked_users = User.query.filter_by(is_active=False).count()
    total_admins = User.query.filter(User.role.in_([User.ROLE_SUPER_ADMIN, User.ROLE_ADMIN])).count()

    # Latest 10 users, uploads, reports
    latest_users = User.query.order_by(User.created_at.desc()).limit(10).all()
    latest_resumes = Resume.query.order_by(Resume.uploaded_at.desc()).limit(10).all()
    latest_reports = Report.query.order_by(Report.created_at.desc()).limit(10).all()
    latest_logs = AdminLog.query.order_by(AdminLog.timestamp.desc()).limit(10).all()

    # API & Storage usage calculation
    groq_key_set = bool(current_app.config.get("GROQ_API_KEY"))
    upload_dir = Path(current_app.config["UPLOAD_FOLDER"])
    storage_bytes = sum(f.stat().st_size for f in upload_dir.glob("*") if f.is_file()) if upload_dir.exists() else 0
    storage_mb = round(storage_bytes / (1024 * 1024), 2)

    # System Health Metrics (CPU, Memory, Storage)
    try:
        if psutil:
            cpu_usage = psutil.cpu_percent(interval=None)
            memory_info = psutil.virtual_memory()
            memory_usage = memory_info.percent
        else:
            cpu_usage = 15.0
            memory_usage = 42.0
    except Exception:
        cpu_usage = 15.0
        memory_usage = 42.0

    return render_template(
        "admin/dashboard.html",
        total_users=total_users,
        total_resumes=total_resumes,
        total_reports=total_reports,
        total_matches=total_matches,
        active_users=active_users,
        blocked_users=blocked_users,
        total_admins=total_admins,
        users=latest_users,
        resumes=latest_resumes,
        reports=latest_reports,
        logs=latest_logs,
        groq_key_set=groq_key_set,
        storage_mb=storage_mb,
        cpu_usage=cpu_usage,
        memory_usage=memory_usage
    )


@admin_bp.route("/users")
@login_required
@admin_required
def users_list():
    """
    Dedicated User Management Page.
    Supports Search, Pagination, and Role/Status Filters.
    """
    page = request.args.get("page", 1, type=int)
    search_q = request.args.get("q", "").strip()
    role_filter = request.args.get("role", "").strip()
    status_filter = request.args.get("status", "").strip()

    query = User.query

    if search_q:
        query = query.filter(
            (User.name.ilike(f"%{search_q}%")) | (User.email.ilike(f"%{search_q}%"))
        )

    if role_filter in User.ALL_ROLES:
        query = query.filter(User.role == role_filter)

    if status_filter == "active":
        query = query.filter(User.is_active == True)
    elif status_filter == "blocked":
        query = query.filter(User.is_active == False)

    pagination = query.order_by(User.created_at.desc()).paginate(page=page, per_page=15, error_out=False)
    users = pagination.items

    return render_template(
        "admin/users.html",
        users=users,
        pagination=pagination,
        search_q=search_q,
        role_filter=role_filter,
        status_filter=status_filter,
        all_roles=User.ALL_ROLES
    )


@admin_bp.route("/user/<int:user_id>/create-admin", methods=["POST"])
@login_required
@super_admin_required
def create_admin(user_id):
    """Only SUPER_ADMIN can elevate a user to ADMIN."""
    user = User.query.get_or_404(user_id)
    if user.role == User.ROLE_SUPER_ADMIN:
        flash("Super Admin role cannot be modified.", "warning")
        return redirect(url_for("admin.users_list"))

    user.role = User.ROLE_ADMIN
    db.session.commit()
    AdminLog.log("CREATE_ADMIN", user_id=current_user.id, target_type="User", target_id=user.id, details=f"Elevated {user.email} to ADMIN", ip_address=request.remote_addr)
    flash(f"User {user.email} promoted to ADMIN successfully.", "success")
    return redirect(url_for("admin.users_list"))


@admin_bp.route("/user/<int:user_id>/remove-admin", methods=["POST"])
@login_required
@super_admin_required
def remove_admin(user_id):
    """Only SUPER_ADMIN can demote an ADMIN to USER."""
    user = User.query.get_or_404(user_id)
    if user.role == User.ROLE_SUPER_ADMIN:
        flash("Cannot revoke privileges from SUPER_ADMIN.", "danger")
        return redirect(url_for("admin.users_list"))

    user.role = User.ROLE_USER
    db.session.commit()
    AdminLog.log("REMOVE_ADMIN", user_id=current_user.id, target_type="User", target_id=user.id, details=f"Demoted {user.email} to USER", ip_address=request.remote_addr)
    flash(f"ADMIN status removed for {user.email}.", "success")
    return redirect(url_for("admin.users_list"))


@admin_bp.route("/user/<int:user_id>/toggle-status", methods=["POST"])
@login_required
@admin_required
def toggle_user_status(user_id):
    """Toggles user active / blocked status."""
    user = User.query.get_or_404(user_id)
    if user.role == User.ROLE_SUPER_ADMIN:
        flash("SUPER_ADMIN account cannot be blocked or deactivated.", "danger")
        return redirect(url_for("admin.users_list"))

    if user.id == current_user.id:
        flash("You cannot deactivate your own account.", "warning")
        return redirect(url_for("admin.users_list"))

    # Only Super Admin can block an Admin
    if user.role == User.ROLE_ADMIN and current_user.role != User.ROLE_SUPER_ADMIN:
        flash("Only SUPER_ADMIN can block an ADMIN user.", "danger")
        return redirect(url_for("admin.users_list"))

    user.is_active = not user.is_active
    db.session.commit()
    action = "UNBLOCK_USER" if user.is_active else "BLOCK_USER"
    AdminLog.log(action, user_id=current_user.id, target_type="User", target_id=user.id, details=f"Changed status for {user.email} to active={user.is_active}", ip_address=request.remote_addr)
    flash(f"Status for {user.email} updated to {'Active' if user.is_active else 'Blocked'}.", "info")
    return redirect(url_for("admin.users_list"))


@admin_bp.route("/resumes")
@login_required
@admin_required
def resumes_list():
    """View uploads list."""
    page = request.args.get("page", 1, type=int)
    pagination = Resume.query.order_by(Resume.uploaded_at.desc()).paginate(page=page, per_page=20, error_out=False)
    return render_template("admin/resumes.html", resumes=pagination.items, pagination=pagination)


@admin_bp.route("/reports")
@login_required
@admin_required
def reports_list():
    """View reports list."""
    page = request.args.get("page", 1, type=int)
    pagination = Report.query.order_by(Report.created_at.desc()).paginate(page=page, per_page=20, error_out=False)
    return render_template("admin/reports.html", reports=pagination.items, pagination=pagination)


@admin_bp.route("/report/<int:report_id>/delete", methods=["POST"])
@login_required
@admin_required
def delete_report(report_id):
    """Admins can delete inappropriate reports."""
    report = Report.query.get_or_404(report_id)
    db.session.delete(report)
    db.session.commit()
    AdminLog.log("DELETE_REPORT", user_id=current_user.id, target_type="Report", target_id=report_id, details=f"Deleted Report #{report_id}", ip_address=request.remote_addr)
    flash(f"Report #{report_id} deleted successfully.", "success")
    return redirect(url_for("admin.reports_list"))


@admin_bp.route("/logs")
@login_required
@super_admin_required
def logs_list():
    """Only SUPER_ADMIN can view system audit logs."""
    page = request.args.get("page", 1, type=int)
    pagination = AdminLog.query.order_by(AdminLog.timestamp.desc()).paginate(page=page, per_page=25, error_out=False)
    return render_template("admin/logs.html", logs=pagination.items, pagination=pagination)


@admin_bp.route("/settings", methods=["GET", "POST"])
@login_required
@super_admin_required
def settings():
    """Only SUPER_ADMIN can manage system settings and API Keys."""
    if request.method == "POST":
        groq_key = request.form.get("groq_api_key", "").strip()
        groq_model = request.form.get("groq_model", "").strip()

        if groq_key:
            os.environ["GROQ_API_KEY"] = groq_key
            current_app.config["GROQ_API_KEY"] = groq_key
        if groq_model:
            os.environ["GROQ_MODEL"] = groq_model
            current_app.config["GROQ_MODEL"] = groq_model

        AdminLog.log("API_KEY_CHANGE", user_id=current_user.id, details="Updated Groq API configuration", ip_address=request.remote_addr)
        flash("System settings and API Keys updated successfully!", "success")
        return redirect(url_for("admin.settings"))

    return render_template(
        "admin/settings.html",
        groq_api_key=current_app.config.get("GROQ_API_KEY", ""),
        groq_model=current_app.config.get("GROQ_MODEL", "llama-3.3-70b-versatile")
    )
