import os
from werkzeug.utils import secure_filename
from flask import current_app

ALLOWED_EXTENSIONS = {"pdf", "docx", "doc", "txt", "png", "jpg", "jpeg"}
MAX_FILE_SIZE_MB = 10


def allowed_file(filename: str) -> bool:
    """Checks if file extension is allowed."""
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS


def validate_file(file_obj) -> tuple[bool, str]:
    """
    Validates uploaded file for existence, allowed extension, and size limit.
    Returns (is_valid, error_message).
    """
    if not file_obj or file_obj.filename == "":
        return False, "No file selected."

    filename = secure_filename(file_obj.filename)
    if not allowed_file(filename):
        return False, "Invalid file format. Only PDF and DOCX files are allowed."

    # Seek end of file to check size
    file_obj.seek(0, os.SEEK_END)
    file_size = file_obj.tell()
    file_obj.seek(0)  # Reset pointer

    max_bytes = current_app.config.get("MAX_CONTENT_LENGTH", MAX_FILE_SIZE_MB * 1024 * 1024)
    if file_size > max_bytes:
        return False, f"File size exceeds maximum limit of {MAX_FILE_SIZE_MB} MB."

    if file_size == 0:
        return False, "Uploaded file is empty."

    return True, ""
