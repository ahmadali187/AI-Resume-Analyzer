from datetime import datetime
import json
from extensions import db


class CoverLetter(db.Model):
    """Generated Cover Letter model."""

    __tablename__ = "cover_letters"

    id = db.Column(db.Integer, primary_key=True)
    resume_id = db.Column(db.Integer, db.ForeignKey("resumes.id"), nullable=False, index=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False, index=True)
    company = db.Column(db.String(200), nullable=False)
    job_role = db.Column(db.String(200), nullable=False)
    content = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)

    def __repr__(self):
        return f"<CoverLetter {self.job_role} at {self.company}>"


class InterviewPrep(db.Model):
    """Generated Interview Prep Q&A model."""

    __tablename__ = "interview_preps"

    id = db.Column(db.Integer, primary_key=True)
    resume_id = db.Column(db.Integer, db.ForeignKey("resumes.id"), nullable=False, index=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False, index=True)
    job_role = db.Column(db.String(200), nullable=True)
    questions_json_str = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)

    @property
    def questions_json(self):
        if self.questions_json_str:
            try:
                return json.loads(self.questions_json_str)
            except Exception:
                return []
        return []

    @questions_json.setter
    def questions_json(self, value):
        self.questions_json_str = json.dumps(value)

    def __repr__(self):
        return f"<InterviewPrep for Resume {self.resume_id}>"
