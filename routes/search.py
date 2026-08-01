from flask import Blueprint, render_template, request
from flask_login import login_required, current_user
from models.resume import Resume
from models.report import Report
from models.job import JobMatch, JobDescription
from models.tool_outputs import CoverLetter
from utils.security import sanitize_input

search_bp = Blueprint("search", __name__)


@search_bp.route("/search")
@login_required
def search():
    """
    Global Search endpoint.
    Searches across uploaded Resumes, Companies, Skills, Cover Letters, and Job Roles.
    """
    query = sanitize_input(request.args.get("q", "")).strip()
    matched_resumes = []
    matched_reports = []
    matched_matches = []
    matched_letters = []

    if query:
        q_wild = f"%{query}%"

        # Search User Resumes
        matched_resumes = Resume.query.filter(
            Resume.user_id == current_user.id,
            (Resume.filename.ilike(q_wild)) | (Resume.raw_text.ilike(q_wild)) | (Resume.parsed_json_str.ilike(q_wild))
        ).order_by(Resume.uploaded_at.desc()).all()

        # Search ATS Reports
        matched_reports = Report.query.filter(
            Report.user_id == current_user.id,
            (Report.summary.ilike(q_wild)) | (Report.analysis_json_str.ilike(q_wild))
        ).order_by(Report.created_at.desc()).all()

        # Search Job Matches
        matched_matches = JobMatch.query.join(JobDescription).filter(
            JobMatch.user_id == current_user.id,
            (JobDescription.title.ilike(q_wild)) | (JobDescription.company.ilike(q_wild)) | (JobDescription.content.ilike(q_wild))
        ).order_by(JobMatch.created_at.desc()).all()

        # Search Cover Letters
        matched_letters = CoverLetter.query.filter(
            CoverLetter.user_id == current_user.id,
            (CoverLetter.company.ilike(q_wild)) | (CoverLetter.job_role.ilike(q_wild)) | (CoverLetter.content.ilike(q_wild))
        ).order_by(CoverLetter.created_at.desc()).all()

    return render_template(
        "search_results.html",
        query=query,
        resumes=matched_resumes,
        reports=matched_reports,
        matches=matched_matches,
        letters=matched_letters,
        total_results=len(matched_resumes) + len(matched_reports) + len(matched_matches) + len(matched_letters)
    )
