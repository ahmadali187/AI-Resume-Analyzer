from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_user, logout_user, login_required, current_user
from extensions import db
from models.user import User

auth_bp = Blueprint("auth", __name__)


@auth_bp.route("/register", methods=["GET", "POST"])
def register():
    if current_user.is_authenticated:
        return redirect(url_for("dashboard.index"))

    if request.method == "POST":
        name = request.form.get("name", "").strip()
        email = request.form.get("email", "").strip().lower()
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

        # Create user (first registered user becomes admin)
        is_first_user = User.query.count() == 0
        user = User(name=name, email=email, is_admin=is_first_user)
        user.set_password(password)

        db.session.add(user)
        db.session.commit()

        flash("Registration successful! You can now log in.", "success")
        return redirect(url_for("auth.login"))

    return render_template("auth/register.html")


@auth_bp.route("/login", methods=["GET", "POST"])
def login():
    if current_user.is_authenticated:
        return redirect(url_for("dashboard.index"))

    if request.method == "POST":
        email = request.form.get("email", "").strip().lower()
        password = request.form.get("password", "")
        remember = bool(request.form.get("remember"))

        user = User.query.filter_by(email=email).first()

        if not user or not user.check_password(password):
            flash("Invalid email or password.", "danger")
            return render_template("auth/login.html")

        login_user(user, remember=remember)
        next_page = request.args.get("next")
        flash(f"Welcome back, {user.name}!", "success")
        return redirect(next_page or url_for("dashboard.index"))

    return render_template("auth/login.html")


@auth_bp.route("/logout")
@login_required
def logout():
    logout_user()
    flash("You have been logged out.", "info")
    return redirect(url_for("main.index"))


@auth_bp.route("/profile", methods=["GET", "POST"])
@login_required
def profile():
    if request.method == "POST":
        name = request.form.get("name", "").strip()
        email = request.form.get("email", "").strip().lower()

        if not name or not email:
            flash("Name and email are required.", "danger")
            return render_template("profile.html")

        existing = User.query.filter(User.email == email, User.id != current_user.id).first()
        if existing:
            flash("Email address is already taken by another account.", "danger")
            return render_template("profile.html")

        current_user.name = name
        current_user.email = email
        current_user.job_title = request.form.get("job_title", "").strip()
        current_user.location = request.form.get("location", "").strip()
        current_user.portfolio = request.form.get("portfolio", "").strip()
        current_user.github = request.form.get("github", "").strip()
        current_user.linkedin = request.form.get("linkedin", "").strip()
        current_user.preferred_role = request.form.get("preferred_role", "").strip()
        current_user.bio = request.form.get("bio", "").strip()

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

    flash("Password changed successfully!", "success")
    return redirect(url_for("auth.profile"))


@auth_bp.route("/forgot-password", methods=["GET", "POST"])
def forgot_password():
    if request.method == "POST":
        email = request.form.get("email", "").strip().lower()
        user = User.query.filter_by(email=email).first()
        if user:
            flash("Password reset instructions have been sent to your email (simulated).", "info")
        else:
            flash("If that email exists in our system, reset instructions have been sent.", "info")
        return redirect(url_for("auth.login"))

    return render_template("auth/forgot_password.html")
