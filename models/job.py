from datetime import datetime
import json
from extensions import db


class JobDescription(db.Model):
    """Job Description Model."""

    __tablename__ = "job_descriptions"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False, index=True)
    title = db.Column(db.String(200), nullable=True)
    company = db.Column(db.String(200), nullable=True)
    content = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)

    matches = db.relationship("JobMatch", backref="job_description", lazy=True, cascade="all, delete-orphan")

    def __repr__(self):
        return f"<JobDescription {self.title or 'Untitled'} (User {self.user_id})>"


class JobMatch(db.Model):
    """Resume vs Job Description Match Results Model."""

    __tablename__ = "job_matches"

    id = db.Column(db.Integer, primary_key=True)
    resume_id = db.Column(db.Integer, db.ForeignKey("resumes.id"), nullable=False, index=True)
    jd_id = db.Column(db.Integer, db.ForeignKey("job_descriptions.id"), nullable=False, index=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False, index=True)

    match_percentage = db.Column(db.Integer, nullable=False, default=0)
    missing_keywords_json_str = db.Column(db.Text, nullable=True)
    missing_skills_json_str = db.Column(db.Text, nullable=True)
    analysis_json_str = db.Column(db.Text, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)

    @property
    def missing_keywords(self):
        if self.missing_keywords_json_str:
            try:
                return json.loads(self.missing_keywords_json_str)
            except Exception:
                return []
        return []

    @missing_keywords.setter
    def missing_keywords(self, value):
        self.missing_keywords_json_str = json.dumps(value)

    @property
    def missing_skills(self):
        if self.missing_skills_json_str:
            try:
                return json.loads(self.missing_skills_json_str)
            except Exception:
                return []
        return []

    @missing_skills.setter
    def missing_skills(self, value):
        self.missing_skills_json_str = json.dumps(value)

    @property
    def analysis_json(self):
        if self.analysis_json_str:
            try:
                return json.loads(self.analysis_json_str)
            except Exception:
                return {}
        return {}

    @analysis_json.setter
    def analysis_json(self, value):
        self.analysis_json_str = json.dumps(value)

    def __repr__(self):
        return f"<JobMatch {self.match_percentage}% (Resume {self.resume_id} - JD {self.jd_id})>"
