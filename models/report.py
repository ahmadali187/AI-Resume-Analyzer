from datetime import datetime
import json
from extensions import db


class Report(db.Model):
    """ATS Analysis Report model."""

    __tablename__ = "reports"

    id = db.Column(db.Integer, primary_key=True)
    resume_id = db.Column(db.Integer, db.ForeignKey("resumes.id"), nullable=False, index=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False, index=True)
    
    # Quantitative Scores (0-100)
    ats_score = db.Column(db.Integer, nullable=False, default=0)
    formatting_score = db.Column(db.Integer, nullable=False, default=0)
    skills_score = db.Column(db.Integer, nullable=False, default=0)
    experience_score = db.Column(db.Integer, nullable=False, default=0)
    keywords_score = db.Column(db.Integer, nullable=False, default=0)
    readability_score = db.Column(db.Integer, nullable=False, default=0)

    # Detailed Analysis JSON & Summaries
    analysis_json_str = db.Column(db.Text, nullable=True)
    summary = db.Column(db.Text, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)

    @property
    def analysis_json(self):
        """Deserializes analysis JSON string to Python dict."""
        if self.analysis_json_str:
            try:
                return json.loads(self.analysis_json_str)
            except Exception:
                return {}
        return {}

    @analysis_json.setter
    def analysis_json(self, data):
        """Serializes analysis dict to JSON string."""
        self.analysis_json_str = json.dumps(data)

    def __repr__(self):
        return f"<Report ATS:{self.ats_score}% (Resume {self.resume_id})>"
