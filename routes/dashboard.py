from flask import Blueprint, render_template
from flask_login import login_required, current_user
from models.resume import Resume
from models.report import Report
from models.job import JobMatch

dashboard_bp = Blueprint("dashboard", __name__)


@dashboard_bp.route("/")
@login_required
def index():
    """Main dashboard page."""
    user_resumes = Resume.query.filter_by(user_id=current_user.id).order_by(Resume.uploaded_at.desc()).all()
    user_reports = Report.query.filter_by(user_id=current_user.id).order_by(Report.created_at.desc()).all()
    user_matches = JobMatch.query.filter_by(user_id=current_user.id).order_by(JobMatch.created_at.desc()).all()

    total_resumes = len(user_resumes)
    total_reports = len(user_reports)
    total_matches = len(user_matches)

    latest_report = user_reports[0] if user_reports else None
    latest_ats_score = latest_report.ats_score if latest_report else 0

    ats_scores = [r.ats_score for r in user_reports if r.ats_score is not None]
    avg_ats_score = round(sum(ats_scores) / len(ats_scores), 1) if ats_scores else 0
    highest_ats_score = max(ats_scores) if ats_scores else 0

    match_pcts = [m.match_percentage for m in user_matches if m.match_percentage is not None]
    avg_job_match = round(sum(match_pcts) / len(match_pcts), 1) if match_pcts else 0

    # Chart data
    valid_reports = [r for r in user_reports if r.ats_score is not None and r.created_at is not None]
    ats_history_labels = [r.created_at.strftime('%m/%d') for r in reversed(valid_reports[:7])]
    ats_history_data = [r.ats_score for r in reversed(valid_reports[:7])]

    return render_template(
        "dashboard.html",
        resumes=user_resumes[:5],
        reports=user_reports[:5],
        matches=user_matches[:5],
        total_resumes=total_resumes,
        total_reports=total_reports,
        total_matches=total_matches,
        latest_ats_score=latest_ats_score,
        avg_ats_score=avg_ats_score,
        highest_ats_score=highest_ats_score,
        avg_job_match=avg_job_match,
        latest_report=latest_report,
        ats_history_labels=ats_history_labels,
        ats_history_data=ats_history_data
    )
