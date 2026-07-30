from functools import wraps
from flask import Blueprint, render_template, redirect, url_for, flash, request, current_app
from flask_login import login_required, current_user
from extensions import db
from models.user import User
from models.resume import Resume
from models.report import Report
from models.job import JobMatch

admin_bp = Blueprint("admin", __name__)


def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated or not current_user.is_admin:
            flash("Admin access required.", "danger")
            return redirect(url_for("dashboard.index"))
        return f(*args, **kwargs)
    return decorated_function


@admin_bp.route("/")
@login_required
@admin_required
def index():
    """Admin dashboard overview."""
    total_users = User.query.count()
    total_resumes = Resume.query.count()
    total_reports = Report.query.count()
    total_matches = JobMatch.query.count()

    users = User.query.order_by(User.created_at.desc()).all()
    resumes = Resume.query.order_by(Resume.uploaded_at.desc()).limit(10).all()
    reports = Report.query.order_by(Report.created_at.desc()).limit(10).all()

    api_key_configured = bool(current_app.config.get("GROQ_API_KEY"))

    return render_template(
        "admin/dashboard.html",
        total_users=total_users,
        total_resumes=total_resumes,
        total_reports=total_reports,
        total_matches=total_matches,
        users=users,
        resumes=resumes,
        reports=reports,
        api_key_configured=api_key_configured
    )


@admin_bp.route("/users")
@login_required
@admin_required
def users_list():
    users = User.query.order_by(User.created_at.desc()).all()
    return render_template("admin/users.html", users=users)


@admin_bp.route("/resumes")
@login_required
@admin_required
def resumes_list():
    resumes = Resume.query.order_by(Resume.uploaded_at.desc()).all()
    return render_template("admin/resumes.html", resumes=resumes)


@admin_bp.route("/reports")
@login_required
@admin_required
def reports_list():
    reports = Report.query.order_by(Report.created_at.desc()).all()
    return render_template("admin/reports.html", reports=reports)


@admin_bp.route("/user/<int:user_id>/toggle-admin", methods=["POST"])
@login_required
@admin_required
def toggle_admin(user_id):
    user = User.query.get_or_404(user_id)
    if user.id == current_user.id:
        flash("You cannot revoke your own admin rights.", "warning")
        return redirect(url_for("admin.users_list"))
    user.is_admin = not user.is_admin
    db.session.commit()
    flash(f"Admin status updated for {user.email}.", "success")
    return redirect(url_for("admin.users_list"))
