from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin
from extensions import db, login_manager


class User(UserMixin, db.Model):
    """User account model."""

    __tablename__ = "users"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.String(256), nullable=False)
    is_admin = db.Column(db.Boolean, default=False, nullable=False)
    bio = db.Column(db.Text, nullable=True)
    job_title = db.Column(db.String(120), nullable=True)
    location = db.Column(db.String(120), nullable=True)
    portfolio = db.Column(db.String(255), nullable=True)
    github = db.Column(db.String(255), nullable=True)
    linkedin = db.Column(db.String(255), nullable=True)
    preferred_role = db.Column(db.String(120), nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    updated_at = db.Column(
        db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False
    )

    # Relationships
    resumes = db.relationship("Resume", backref="user", lazy=True, cascade="all, delete-orphan")
    job_descriptions = db.relationship("JobDescription", backref="user", lazy=True, cascade="all, delete-orphan")
    job_matches = db.relationship("JobMatch", backref="user", lazy=True, cascade="all, delete-orphan")
    cover_letters = db.relationship("CoverLetter", backref="user", lazy=True, cascade="all, delete-orphan")
    interview_preps = db.relationship("InterviewPrep", backref="user", lazy=True, cascade="all, delete-orphan")

    def set_password(self, password: str):
        """Hashes and sets user password."""
        self.password_hash = generate_password_hash(password)

    def check_password(self, password: str) -> bool:
        """Verifies given password against stored hash."""
        return check_password_hash(self.password_hash, password)

    def __repr__(self):
        return f"<User {self.email}>"


@login_manager.user_loader
def load_user(user_id):
    """Flask-Login user loader callback."""
    return User.query.get(int(user_id))
