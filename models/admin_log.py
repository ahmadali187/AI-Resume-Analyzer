from datetime import datetime
import json
from extensions import db


class AdminLog(db.Model):
    """Audit log model for administrative and security actions."""

    __tablename__ = "admin_logs"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=True, index=True)
    action = db.Column(db.String(100), nullable=False, index=True)
    target_type = db.Column(db.String(50), nullable=True)
    target_id = db.Column(db.Integer, nullable=True)
    details = db.Column(db.Text, nullable=True)
    ip_address = db.Column(db.String(45), nullable=True)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow, nullable=False, index=True)

    user = db.relationship("User", backref="admin_logs", lazy=True)

    @classmethod
    def log(cls, action, user_id=None, target_type=None, target_id=None, details=None, ip_address=None):
        """Helper method to record an audit log entry."""
        if isinstance(details, (dict, list)):
            details_str = json.dumps(details)
        else:
            details_str = str(details) if details is not None else ""

        entry = cls(
            user_id=user_id,
            action=action,
            target_type=target_type,
            target_id=target_id,
            details=details_str,
            ip_address=ip_address,
        )
        db.session.add(entry)
        try:
            db.session.commit()
        except Exception:
            db.session.rollback()
        return entry

    def __repr__(self):
        return f"<AdminLog {self.action} by User {self.user_id} at {self.timestamp}>"
