from flask import Blueprint, render_template
from flask_login import login_required, current_user
from models.resume import Resume
from models.report import Report
from models.job import JobMatch

dashboard_bp = Blueprint("dashboard", __name__)


@dashboard_bp.route("/")
@login_required
def index():
    """Main dashboard overview for logged in candidate."""
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

    # Chart 1: ATS Score History Trend
    valid_reports = [r for r in user_reports if r.ats_score is not None and r.created_at is not None]
    ats_history_labels = [r.created_at.strftime('%m/%d') for r in reversed(valid_reports[:7])]
    ats_history_data = [r.ats_score for r in reversed(valid_reports[:7])]

    # Chart 2: Skill Category Distribution across uploaded resumes
    skill_categories = {}
    for r in user_resumes:
        pdata = r.parsed_json or {}
        skills = pdata.get("skills", {})
        if isinstance(skills, dict):
            for cat, s_list in skills.items():
                if isinstance(s_list, list):
                    cat_title = cat.replace("_", " ").title()
                    skill_categories[cat_title] = skill_categories.get(cat_title, 0) + len(s_list)

    cat_labels = list(skill_categories.keys())[:6]
    cat_counts = [skill_categories[k] for k in cat_labels]

    # Combine Recent Activity Stream (Uploads, Reports, Matches)
    activity_stream = []
    for r in user_resumes[:5]:
        activity_stream.append({
            "type": "upload",
            "title": f"Uploaded '{r.filename}'",
            "time": r.uploaded_at,
            "badge": "UPLOAD",
            "color": "primary",
            "url": f"/resume/{r.id}"
        })
    for rep in user_reports[:5]:
        activity_stream.append({
            "type": "report",
            "title": f"Generated ATS Report (Score: {rep.ats_score}%)",
            "time": rep.created_at,
            "badge": "REPORT",
            "color": "success",
            "url": f"/reports/{rep.id}"
        })
    for m in user_matches[:5]:
        activity_stream.append({
            "type": "match",
            "title": f"Job Match Evaluation ({m.match_percentage}% Match)",
            "time": m.created_at,
            "badge": "JOB MATCH",
            "color": "warning",
            "url": f"/analysis/job-match/{m.id}"
        })

    activity_stream.sort(key=lambda x: x["time"], reverse=True)

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
        ats_history_data=ats_history_data,
        cat_labels=cat_labels,
        cat_counts=cat_counts,
        activity_stream=activity_stream[:8]
    )
