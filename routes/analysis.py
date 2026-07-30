from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify
from flask_login import login_required, current_user
from extensions import db
from models.resume import Resume
from models.report import Report
from models.job import JobDescription, JobMatch
from models.tool_outputs import CoverLetter, InterviewPrep
from services.groq_service import GroqService
from services.ats_analyzer import ATSAnalyzer
from services.job_matcher import JobMatcher
from services.content_generators import ContentGenerator

analysis_bp = Blueprint("analysis", __name__)


@analysis_bp.route("/analyze/<int:resume_id>", methods=["GET", "POST"])
@login_required
def analyze(resume_id):
    """Run full Groq ATS Analysis on a resume."""
    resume = Resume.query.filter_by(id=resume_id, user_id=current_user.id).first_or_404()

    if request.method == "POST":
        groq_svc = GroqService()
        ai_result = groq_svc.analyze_resume(resume.raw_text, resume.parsed_json)
        scores = ATSAnalyzer.calculate_scores(resume.raw_text, resume.parsed_json, ai_result)

        report = Report(
            resume_id=resume.id,
            user_id=current_user.id,
            ats_score=scores["overall_ats"],
            formatting_score=scores["formatting_score"],
            skills_score=scores["skills_score"],
            experience_score=scores["experience_score"],
            keywords_score=scores["keywords_score"],
            readability_score=scores["readability_score"],
            summary=ai_result.get("executive_summary", "")
        )
        report.analysis_json = ai_result

        db.session.add(report)
        db.session.commit()

        flash("ATS Analysis completed successfully!", "success")
        return redirect(url_for("reports.view_report", report_id=report.id))

    return render_template("analysis_confirm.html", resume=resume)


@analysis_bp.route("/job-match", methods=["GET", "POST"])
@login_required
def job_match():
    """Compare candidate resume against Job Description."""
    resumes = Resume.query.filter_by(user_id=current_user.id).order_by(Resume.uploaded_at.desc()).all()

    if request.method == "POST":
        resume_id = request.form.get("resume_id")
        jd_title = request.form.get("title", "").strip() or "Target Job"
        jd_company = request.form.get("company", "").strip() or "Target Company"
        jd_content = request.form.get("content", "").strip()

        if not resume_id or not jd_content:
            flash("Please select a resume and paste the job description text.", "danger")
            return render_template("job_match.html", resumes=resumes)

        resume = Resume.query.filter_by(id=resume_id, user_id=current_user.id).first_or_404()

        # Create Job Description record
        jd = JobDescription(
            user_id=current_user.id,
            title=jd_title,
            company=jd_company,
            content=jd_content
        )
        db.session.add(jd)
        db.session.flush()

        # Run Job Match service
        match_result = JobMatcher.match(resume.raw_text, resume.parsed_json, jd_content)

        job_match_obj = JobMatch(
            resume_id=resume.id,
            jd_id=jd.id,
            user_id=current_user.id,
            match_percentage=match_result.get("match_percentage", 0),
            missing_keywords=match_result.get("missing_keywords", []),
            missing_skills=match_result.get("missing_skills", [])
        )
        job_match_obj.analysis_json = match_result

        db.session.add(job_match_obj)
        db.session.commit()

        flash("Job Description matching completed!", "success")
        return redirect(url_for("analysis.job_match_result", match_id=job_match_obj.id))

    return render_template("job_match.html", resumes=resumes)


@analysis_bp.route("/job-match/<int:match_id>")
@login_required
def job_match_result(match_id):
    """View job match analysis result and skill gap roadmap."""
    match = JobMatch.query.filter_by(id=match_id, user_id=current_user.id).first_or_404()
    return render_template("job_match_result.html", match=match)


@analysis_bp.route("/cover-letter", methods=["GET", "POST"])
@login_required
def cover_letter():
    """Generate personalized cover letter."""
    resumes = Resume.query.filter_by(user_id=current_user.id).order_by(Resume.uploaded_at.desc()).all()

    if request.method == "POST":
        resume_id = request.form.get("resume_id")
        company = request.form.get("company", "").strip()
        job_role = request.form.get("job_role", "").strip()

        if not resume_id or not company or not job_role:
            flash("All fields are required to generate a cover letter.", "danger")
            return render_template("cover_letter_form.html", resumes=resumes)

        resume = Resume.query.filter_by(id=resume_id, user_id=current_user.id).first_or_404()
        generator = ContentGenerator()
        letter_content = generator.generate_cover_letter(resume.raw_text, company, job_role)

        cl = CoverLetter(
            resume_id=resume.id,
            user_id=current_user.id,
            company=company,
            job_role=job_role,
            content=letter_content
        )
        db.session.add(cl)
        db.session.commit()

        flash("Cover letter generated!", "success")
        return render_template("cover_letter_result.html", cover_letter=cl)

    return render_template("cover_letter_form.html", resumes=resumes)


@analysis_bp.route("/interview-prep", methods=["GET", "POST"])
@login_required
def interview_prep():
    """Generate interview preparation questions and answers with 5 dynamic questions per batch."""
    resumes = Resume.query.filter_by(user_id=current_user.id).order_by(Resume.uploaded_at.desc()).all()

    if request.method == "POST":
        resume_id = request.form.get("resume_id")
        job_role = request.form.get("job_role", "").strip() or "Software Engineer"
        batch_offset = int(request.form.get("batch_offset", 0))

        if request.form.get("action") == "next_questions":
            batch_offset += 1

        if not resume_id:
            flash("Please select a resume.", "danger")
            return render_template("interview_prep_form.html", resumes=resumes)

        resume = Resume.query.filter_by(id=resume_id, user_id=current_user.id).first_or_404()
        groq_svc = GroqService()
        questions = groq_svc.generate_interview_prep(resume.raw_text, job_role, offset=batch_offset)

        prep = InterviewPrep(
            resume_id=resume.id,
            user_id=current_user.id,
            job_role=job_role
        )
        prep.questions_json = questions

        db.session.add(prep)
        db.session.commit()

        return render_template(
            "interview_prep_result.html",
            prep=prep,
            resume_id=resume.id,
            job_role=job_role,
            batch_offset=batch_offset
        )

    return render_template("interview_prep_form.html", resumes=resumes)
