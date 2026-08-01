import os
import re
from functools import wraps
from flask import render_template, redirect, url_for, flash, request, abort, current_app
from flask_login import current_user
from werkzeug.utils import secure_filename
from models.user import User


def role_required(*roles):
    """
    Decorator to restrict route access to specific roles.
    Returns 403 Forbidden page if current user role is not authorized.
    """
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if not current_user.is_authenticated:
                flash("Please log in to access this page.", "warning")
                return redirect(url_for("auth.login", next=request.url))
            if not current_user.is_active:
                flash("Your account has been deactivated. Please contact support.", "danger")
                return redirect(url_for("auth.logout"))
            if current_user.role not in roles:
                return render_template("errors/403.html"), 403
            return f(*args, **kwargs)
        return decorated_function
    return decorator


def super_admin_required(f):
    """Decorator restricting route access exclusively to SUPER_ADMIN."""
    return role_required(User.ROLE_SUPER_ADMIN)(f)


def admin_required(f):
    """Decorator restricting route access to SUPER_ADMIN and ADMIN."""
    return role_required(User.ROLE_SUPER_ADMIN, User.ROLE_ADMIN)(f)


def scan_file_for_threats(file_path: str) -> tuple[bool, str]:
    """
    Modular virus/threat scan hook for uploaded files.
    Expandable to ClamAV or external API security scanners.
    Returns (is_clean, message).
    """
    if not os.path.exists(file_path):
        return False, "File does not exist."

    # Inspect file header magic bytes for PDF and DOCX/ZIP
    try:
        with open(file_path, "rb") as f:
            header = f.read(10)
            if file_path.endswith(".pdf"):
                if not header.startswith(b"%PDF"):
                    return False, "Invalid PDF header magic bytes detected."
            elif file_path.endswith(".docx"):
                if not header.startswith(b"PK"):
                    return False, "Invalid DOCX archive magic bytes detected."
    except Exception as e:
        return False, f"Failed to inspect file magic bytes: {str(e)}"

    return True, "File clean"


def sanitize_input(text: str) -> str:
    """Removes potentially dangerous HTML/script tags from user string input."""
    if not text:
        return ""
    clean = re.sub(r"<script.*?>.*?</script>", "", text, flags=re.DOTALL | re.IGNORECASE)
    clean = re.sub(r"<[^>]*>", "", clean)
    return clean.strip()
