import os
from pathlib import Path
from flask import Blueprint, render_template, redirect, url_for, flash, request, current_app
from flask_login import login_user, logout_user, login_required, current_user
from werkzeug.utils import secure_filename
from extensions import db
from models.user import User
from models.admin_log import AdminLog
from utils.security import sanitize_input

auth_bp = Blueprint("auth", __name__)


@auth_bp.route("/register", methods=["GET", "POST"])
def register():
    if current_user.is_authenticated:
        return redirect(url_for("dashboard.index"))

    if request.method == "POST":
        name = sanitize_input(request.form.get("name", ""))
        email = sanitize_input(request.form.get("email", "")).lower()
        password = request.form.get("password", "")
        confirm_password = request.form.get("confirm_password", "")

        if not name or not email or not password:
            flash("All fields are required.", "danger")
            return render_template("auth/register.html")

        if password != confirm_password:
            flash("Passwords do not match.", "danger")
            return render_template("auth/register.html")

        if len(password) < 6:
            flash("Password must be at least 6 characters long.", "danger")
            return render_template("auth/register.html")

        existing_user = User.query.filter_by(email=email).first()
        if existing_user:
            flash("An account with this email already exists.", "warning")
            return render_template("auth/register.html")

        # STRICT RULE: Registration ALWAYS creates role = User.ROLE_USER
        user = User(
            name=name,
            email=email,
            role=User.ROLE_USER,
            is_active=True
        )
        user.set_password(password)

        db.session.add(user)
        db.session.commit()

        AdminLog.log("REGISTER", user_id=user.id, details=f"User {email} registered", ip_address=request.remote_addr)

        flash("Registration successful! You can now log in.", "success")
        return redirect(url_for("auth.login"))

    return render_template("auth/register.html")


@auth_bp.route("/login", methods=["GET", "POST"])
def login():
    if current_user.is_authenticated:
        return redirect(url_for("dashboard.index"))

    if request.method == "POST":
        email = sanitize_input(request.form.get("email", "")).lower()
        password = request.form.get("password", "")
        remember = bool(request.form.get("remember"))

        user = User.query.filter_by(email=email).first()

        if not user or not user.check_password(password):
            flash("Invalid email or password.", "danger")
            return render_template("auth/login.html")

        if not user.is_active:
            flash("Your account has been deactivated. Please contact support.", "danger")
            return render_template("auth/login.html")

        login_user(user, remember=remember)
        AdminLog.log("LOGIN", user_id=user.id, details=f"User {user.email} logged in", ip_address=request.remote_addr)

        next_page = request.args.get("next")
        flash(f"Welcome back, {user.name}!", "success")
        return redirect(next_page or url_for("dashboard.index"))

    return render_template("auth/login.html")


@auth_bp.route("/logout")
@login_required
def logout():
    AdminLog.log("LOGOUT", user_id=current_user.id, details=f"User {current_user.email} logged out", ip_address=request.remote_addr)
    logout_user()
    flash("You have been logged out.", "info")
    return redirect(url_for("main.index"))


@auth_bp.route("/profile", methods=["GET", "POST"])
@login_required
def profile():
    if request.method == "POST":
        name = sanitize_input(request.form.get("name", ""))
        email = sanitize_input(request.form.get("email", "")).lower()

        if not name or not email:
            flash("Name and email are required.", "danger")
            return render_template("profile.html")

        existing = User.query.filter(User.email == email, User.id != current_user.id).first()
        if existing:
            flash("Email address is already taken by another account.", "danger")
            return render_template("profile.html")

        current_user.name = name
        current_user.email = email
        current_user.job_title = sanitize_input(request.form.get("job_title", ""))
        current_user.location = sanitize_input(request.form.get("location", ""))
        current_user.portfolio = sanitize_input(request.form.get("portfolio", ""))
        current_user.github = sanitize_input(request.form.get("github", ""))
        current_user.linkedin = sanitize_input(request.form.get("linkedin", ""))
        current_user.preferred_role = sanitize_input(request.form.get("preferred_role", ""))
        current_user.bio = sanitize_input(request.form.get("bio", ""))
        current_user.skills_str = sanitize_input(request.form.get("skills", ""))

        # Profile photo upload handler
        if "photo" in request.files:
            file = request.files["photo"]
            if file and file.filename:
                ext = file.filename.rsplit(".", 1)[-1].lower() if "." in file.filename else ""
                if ext in ["png", "jpg", "jpeg", "webp"]:
                    filename = secure_filename(f"user_{current_user.id}_avatar.{ext}")
                    upload_dir = Path(current_app.config["UPLOAD_FOLDER"]) / "avatars"
                    upload_dir.mkdir(parents=True, exist_ok=True)
                    saved_path = upload_dir / filename
                    file.save(saved_path)
                    current_user.photo = f"avatars/{filename}"

        db.session.commit()

        flash("Profile updated successfully!", "success")
        return redirect(url_for("auth.profile"))

    return render_template("profile.html")


@auth_bp.route("/change-password", methods=["POST"])
@login_required
def change_password():
    current_password = request.form.get("current_password", "")
    new_password = request.form.get("new_password", "")
    confirm_password = request.form.get("confirm_password", "")

    if not current_user.check_password(current_password):
        flash("Current password is incorrect.", "danger")
        return redirect(url_for("auth.profile"))

    if new_password != confirm_password:
        flash("New passwords do not match.", "danger")
        return redirect(url_for("auth.profile"))

    if len(new_password) < 6:
        flash("New password must be at least 6 characters long.", "danger")
        return redirect(url_for("auth.profile"))

    current_user.set_password(new_password)
    db.session.commit()
    AdminLog.log("CHANGE_PASSWORD", user_id=current_user.id, details="Changed password", ip_address=request.remote_addr)

    flash("Password changed successfully!", "success")
    return redirect(url_for("auth.profile"))


@auth_bp.route("/forgot-password", methods=["GET", "POST"])
def forgot_password():
    if request.method == "POST":
        email = sanitize_input(request.form.get("email", "")).lower()
        user = User.query.filter_by(email=email).first()
        if user:
            flash("Password reset instructions have been sent to your email (simulated).", "info")
        else:
            flash("If that email exists in our system, reset instructions have been sent.", "info")
        return redirect(url_for("auth.login"))

    return render_template("auth/forgot_password.html")
