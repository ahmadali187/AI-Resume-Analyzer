from datetime import datetime
import json
from extensions import db


class Resume(db.Model):
    """Uploaded Resume metadata and extracted content model."""

    __tablename__ = "resumes"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False, index=True)
    filename = db.Column(db.String(255), nullable=False)
    filepath = db.Column(db.String(512), nullable=False)
    file_type = db.Column(db.String(10), nullable=False)  # 'pdf' or 'docx'
    file_size = db.Column(db.Integer, nullable=False, default=0)
    uploaded_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    raw_text = db.Column(db.Text, nullable=True)
    parsed_json_str = db.Column(db.Text, nullable=True)

    # Relationships
    reports = db.relationship("Report", backref="resume", lazy=True, cascade="all, delete-orphan")
    job_matches = db.relationship("JobMatch", backref="resume", lazy=True, cascade="all, delete-orphan")
    cover_letters = db.relationship("CoverLetter", backref="resume", lazy=True, cascade="all, delete-orphan")
    interview_preps = db.relationship("InterviewPrep", backref="resume", lazy=True, cascade="all, delete-orphan")

    @property
    def parsed_json(self):
        """Deserializes JSON string to Python dict."""
        if self.parsed_json_str:
            try:
                return json.loads(self.parsed_json_str)
            except Exception:
                return {}
        return {}

    @parsed_json.setter
    def parsed_json(self, data):
        """Serializes Python dict to JSON string."""
        self.parsed_json_str = json.dumps(data)

    def __repr__(self):
        return f"<Resume {self.filename} (User {self.user_id})>"
