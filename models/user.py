from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin
from extensions import db, login_manager


class User(UserMixin, db.Model):
    """User account model supporting SUPER_ADMIN, ADMIN, USER, RECRUITER roles."""

    __tablename__ = "users"

    # Role Constants
    ROLE_SUPER_ADMIN = "SUPER_ADMIN"
    ROLE_ADMIN = "ADMIN"
    ROLE_USER = "USER"
    ROLE_RECRUITER = "RECRUITER"
    ALL_ROLES = [ROLE_SUPER_ADMIN, ROLE_ADMIN, ROLE_USER, ROLE_RECRUITER]

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.String(256), nullable=False)
    role = db.Column(db.String(20), default=ROLE_USER, nullable=False, index=True)
    is_active = db.Column(db.Boolean, default=True, nullable=False)
    photo = db.Column(db.String(255), nullable=True)
    skills_str = db.Column(db.Text, nullable=True)
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

    @property
    def is_admin(self) -> bool:
        """Backward compatible helper property for admin access."""
        return self.role in [self.ROLE_SUPER_ADMIN, self.ROLE_ADMIN]

    @is_admin.setter
    def is_admin(self, value: bool):
        """Setter for backward compatibility."""
        if value:
            if self.role != self.ROLE_SUPER_ADMIN:
                self.role = self.ROLE_ADMIN
        else:
            if self.role != self.ROLE_SUPER_ADMIN:
                self.role = self.ROLE_USER

    def is_super_admin(self) -> bool:
        return self.role == self.ROLE_SUPER_ADMIN

    def is_admin_user(self) -> bool:
        return self.role in [self.ROLE_SUPER_ADMIN, self.ROLE_ADMIN]

    def is_recruiter(self) -> bool:
        return self.role == self.ROLE_RECRUITER

    def can_manage_admins(self) -> bool:
        return self.role == self.ROLE_SUPER_ADMIN

    def can_view_admin_panel(self) -> bool:
        return self.role in [self.ROLE_SUPER_ADMIN, self.ROLE_ADMIN]

    def __repr__(self):
        return f"<User {self.email} Role:{self.role}>"


@login_manager.user_loader
def load_user(user_id):
    """Flask-Login user loader callback."""
    return User.query.get(int(user_id))
