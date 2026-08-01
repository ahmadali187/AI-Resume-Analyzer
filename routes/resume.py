import os
from pathlib import Path
from flask import Blueprint, render_template, request, redirect, url_for, flash, current_app, Response, jsonify
from flask_login import login_required, current_user
from werkzeug.utils import secure_filename
from extensions import db
from models.resume import Resume
from utils.validators import validate_file
from utils.security import sanitize_input, scan_file_for_threats
from services.resume_parser import ResumeParser

resume_bp = Blueprint("resume", __name__)


@resume_bp.route("/upload", methods=["GET", "POST"])
@login_required
def upload():
    """Upload PDF or DOCX resume."""
    if request.method == "POST":
        if "file" not in request.files:
            flash("No file part in the request.", "danger")
            return redirect(request.url)

        file = request.files["file"]
        is_valid, err_msg = validate_file(file)
        if not is_valid:
            flash(err_msg, "danger")
            return render_template("upload.html")

        # Save file securely
        filename = secure_filename(file.filename)
        ext = filename.rsplit(".", 1)[1].lower()
        upload_dir = Path(current_app.config["UPLOAD_FOLDER"])
        upload_dir.mkdir(exist_ok=True, parents=True)

        saved_path = upload_dir / f"user_{current_user.id}_{filename}"
        file.save(saved_path)

        # Threat scan
        is_clean, scan_msg = scan_file_for_threats(str(saved_path))
        if not is_clean:
            if saved_path.exists():
                saved_path.unlink()
            flash(f"Security validation failed: {scan_msg}", "danger")
            return render_template("upload.html")

        file_size = saved_path.stat().st_size

        try:
            # Extract raw text and parse JSON
            raw_text = ResumeParser.extract_text(str(saved_path), ext)
            if not raw_text.strip():
                flash("Failed to extract readable text from file. Please ensure the document is not an image-only scan.", "warning")

            parsed_data = ResumeParser.parse_resume(raw_text)

            resume = Resume(
                user_id=current_user.id,
                filename=filename,
                filepath=str(saved_path),
                file_type=ext,
                file_size=file_size,
                raw_text=raw_text,
            )
            resume.parsed_json = parsed_data

            db.session.add(resume)
            db.session.commit()

            flash(f"Resume '{filename}' successfully uploaded and parsed!", "success")
            return redirect(url_for("resume.detail", resume_id=resume.id))

        except Exception as e:
            if saved_path.exists():
                saved_path.unlink()
            flash(f"Error processing document: {str(e)}", "danger")
            return render_template("upload.html")

    return render_template("upload.html")


@resume_bp.route("/list")
@login_required
def list_resumes():
    """List all uploaded resumes for current user."""
    resumes = Resume.query.filter_by(user_id=current_user.id).order_by(Resume.uploaded_at.desc()).all()
    return render_template("resumes_list.html", resumes=resumes)


@resume_bp.route("/<int:resume_id>")
@login_required
def detail(resume_id):
    """View detailed parsed resume information."""
    resume = Resume.query.filter_by(id=resume_id, user_id=current_user.id).first_or_404()
    return render_template("resume_detail.html", resume=resume)


@resume_bp.route("/<int:resume_id>/rename", methods=["POST"])
@login_required
def rename(resume_id):
    """Rename an existing uploaded resume."""
    resume = Resume.query.filter_by(id=resume_id, user_id=current_user.id).first_or_404()
    new_name = sanitize_input(request.form.get("filename", "")).strip()

    if new_name:
        if not new_name.endswith(f".{resume.file_type}"):
            new_name = f"{new_name}.{resume.file_type}"
        resume.filename = secure_filename(new_name)
        db.session.commit()
        flash("Resume renamed successfully.", "success")
    else:
        flash("Filename cannot be empty.", "warning")

    return redirect(url_for("resume.detail", resume_id=resume.id))


@resume_bp.route("/<int:resume_id>/replace", methods=["POST"])
@login_required
def replace(resume_id):
    """Replace document file of an existing resume."""
    resume = Resume.query.filter_by(id=resume_id, user_id=current_user.id).first_or_404()

    if "file" not in request.files:
        flash("No file selected.", "danger")
        return redirect(url_for("resume.detail", resume_id=resume.id))

    file = request.files["file"]
    is_valid, err_msg = validate_file(file)
    if not is_valid:
        flash(err_msg, "danger")
        return redirect(url_for("resume.detail", resume_id=resume.id))

    filename = secure_filename(file.filename)
    ext = filename.rsplit(".", 1)[1].lower()
    upload_dir = Path(current_app.config["UPLOAD_FOLDER"])

    # Remove old file if exists
    if os.path.exists(resume.filepath):
        try:
            os.remove(resume.filepath)
        except Exception:
            pass

    saved_path = upload_dir / f"user_{current_user.id}_{filename}"
    file.save(saved_path)

    raw_text = ResumeParser.extract_text(str(saved_path), ext)
    parsed_data = ResumeParser.parse_resume(raw_text)

    resume.filename = filename
    resume.filepath = str(saved_path)
    resume.file_type = ext
    resume.file_size = saved_path.stat().st_size
    resume.raw_text = raw_text
    resume.parsed_json = parsed_data

    db.session.commit()
    flash("Resume replaced and re-analyzed successfully!", "success")
    return redirect(url_for("resume.detail", resume_id=resume.id))


@resume_bp.route("/<int:resume_id>/preview")
@login_required
def preview(resume_id):
    """Preview document text or download stream."""
    resume = Resume.query.filter_by(id=resume_id, user_id=current_user.id).first_or_404()
    return jsonify({
        "id": resume.id,
        "filename": resume.filename,
        "file_type": resume.file_type,
        "uploaded_at": resume.uploaded_at.strftime('%b %d, %Y'),
        "raw_text": resume.raw_text[:3000] if resume.raw_text else "No preview content available."
    })


@resume_bp.route("/<int:resume_id>/delete", methods=["POST"])
@login_required
def delete(resume_id):
    """Delete uploaded resume and associated file."""
    resume = Resume.query.filter_by(id=resume_id, user_id=current_user.id).first_or_404()
    
    # Remove file from disk if present
    if os.path.exists(resume.filepath):
        try:
            os.remove(resume.filepath)
        except Exception:
            pass

    db.session.delete(resume)
    db.session.commit()

    flash("Resume deleted successfully.", "info")
    return redirect(url_for("resume.list_resumes"))


@resume_bp.route("/compare", methods=["GET", "POST"])
@login_required
def compare():
    """Side-by-side comparison of two uploaded resumes."""
    resumes = Resume.query.filter_by(user_id=current_user.id).order_by(Resume.uploaded_at.desc()).all()

    r1_id = request.values.get("r1_id")
    r2_id = request.values.get("r2_id")

    r1 = Resume.query.filter_by(id=r1_id, user_id=current_user.id).first() if r1_id else None
    r2 = Resume.query.filter_by(id=r2_id, user_id=current_user.id).first() if r2_id else None

    comparison_data = None
    if r1 and r2:
        r1_json = r1.parsed_json or {}
        r2_json = r2.parsed_json or {}

        s1 = set()
        for cat, list_s in r1_json.get("skills", {}).items():
            if isinstance(list_s, list):
                s1.update([x.lower() for x in list_s])

        s2 = set()
        for cat, list_s in r2_json.get("skills", {}).items():
            if isinstance(list_s, list):
                s2.update([x.lower() for x in list_s])

        common_skills = s1.intersection(s2)
        r1_unique = s1 - s2
        r2_unique = s2 - s1

        comparison_data = {
            "r1": r1,
            "r2": r2,
            "r1_skill_count": len(s1),
            "r2_skill_count": len(s2),
            "common_skills": sorted([x.title() for x in common_skills]),
            "r1_unique_skills": sorted([x.title() for x in r1_unique]),
            "r2_unique_skills": sorted([x.title() for x in r2_unique]),
            "r1_exp_count": len(r1_json.get("experience", [])),
            "r2_exp_count": len(r2_json.get("experience", [])),
            "r1_proj_count": len(r1_json.get("projects", [])),
            "r2_proj_count": len(r2_json.get("projects", [])),
        }

    return render_template("compare.html", resumes=resumes, r1=r1, r2=r2, comp=comparison_data)


@resume_bp.route("/<int:resume_id>/export/<string:fmt>")
@login_required
def export(resume_id, fmt):
    """Export parsed resume in JSON, Markdown, or HTML format."""
    import json
    resume = Resume.query.filter_by(id=resume_id, user_id=current_user.id).first_or_404()
    pdata = resume.parsed_json or {}
    contact = pdata.get("contact_info", {})
    name = contact.get("name", "Candidate")

    if fmt == "json":
        return Response(
            json.dumps(pdata, indent=2),
            mimetype="application/json",
            headers={"Content-Disposition": f"attachment;filename=resume_{resume_id}.json"}
        )

    elif fmt in ["md", "markdown"]:
        md_text = f"# {name}\n"
        if contact.get("email"): md_text += f"- Email: {contact.get('email')}\n"
        if contact.get("phone"): md_text += f"- Phone: {contact.get('phone')}\n"
        md_text += "\n## Skills\n"
        for cat, sks in pdata.get("skills", {}).items():
            if sks:
                md_text += f"- **{cat.title()}**: {', '.join(sks)}\n"
        
        md_text += "\n## Work Experience\n"
        for exp in pdata.get("experience", []):
            md_text += f"### {exp.get('title', 'Role')} - {exp.get('company', 'Company')}\n"
            for b in exp.get("responsibilities", []):
                md_text += f"- {b}\n"

        return Response(
            md_text,
            mimetype="text/markdown",
            headers={"Content-Disposition": f"attachment;filename=resume_{resume_id}.md"}
        )

    elif fmt == "html":
        html_content = f"<html><head><title>{name} - Resume</title></head><body style='font-family:sans-serif;padding:20px;'>"
        html_content += f"<h1>{name}</h1><p>{contact.get('email', '')} | {contact.get('phone', '')}</p>"
        html_content += "<h2>Skills</h2><ul>"
        for cat, sks in pdata.get("skills", {}).items():
            if sks:
                html_content += f"<li><strong>{cat.title()}</strong>: {', '.join(sks)}</li>"
        html_content += "</ul></body></html>"

        return Response(
            html_content,
            mimetype="text/html",
            headers={"Content-Disposition": f"attachment;filename=resume_{resume_id}.html"}
        )

    flash("Unsupported export format.", "warning")
    return redirect(url_for("resume.detail", resume_id=resume_id))


@resume_bp.route("/load-sample", methods=["POST"])
@login_required
def load_sample():
    """1-Click Sample Demo Loader: auto-loads high-quality candidate resume data."""
    sample_filename = "Sample_Alex_Morgan_Senior_Engineer.pdf"
    
    # Check if sample resume already exists for current user
    existing = Resume.query.filter_by(user_id=current_user.id, filename=sample_filename).first()
    if existing:
        flash("Sample resume loaded!", "info")
        return redirect(url_for("resume.detail", resume_id=existing.id))

    upload_dir = Path(current_app.config["UPLOAD_FOLDER"])
    upload_dir.mkdir(exist_ok=True, parents=True)
    saved_path = upload_dir / f"user_{current_user.id}_{sample_filename}"

    sample_text = """
Alex Morgan
San Francisco, CA | (555) 234-5678 | alex.morgan@example.com | linkedin.com/in/alexmorgan-dev | github.com/alexmorgan-dev

PROFESSIONAL SUMMARY
Senior Full-Stack Engineer with 6+ years of experience architecting high-throughput cloud applications, microservices, and modern web applications using Python, Flask, React, PostgreSQL, Docker, and AWS. Proven track record of optimizing database performance by 40% and leading CI/CD automation pipelines.

SKILLS
Programming Languages: Python, JavaScript, TypeScript, SQL, HTML5, CSS3, Bash
Frameworks & Libraries: Flask, Django, FastAPI, React, Redux, Next.js, Node.js, Bootstrap
Databases: PostgreSQL, MySQL, Redis, MongoDB, SQLite
DevOps & Cloud: AWS (S3, EC2, Lambda), Docker, Kubernetes, GitHub Actions, CI/CD, NGINX
Developer Tools: Git, GitHub, VS Code, Postman, Pytest, Jest, Swagger

WORK EXPERIENCE
Senior Software Engineer | TechCorp Inc. | San Francisco, CA | 2021 - Present
- Architected RESTful microservices using Flask and PostgreSQL handling 5M+ daily requests with 99.95% uptime.
- Spearheaded database query optimization and indexing strategy, reducing P99 latency by 42%.
- Engineered automated CI/CD pipeline using GitHub Actions and Docker, reducing deployment cycle times from 45 mins to 8 mins.
- Led a team of 5 engineers, establishing strict code review standards and unit test coverage requirements (>85%).

Full-Stack Developer | Innovate Soft | Austin, TX | 2018 - 2021
- Developed responsive single-page web applications using React, Redux, and Python Flask REST APIs.
- Implemented JWT authentication, role-based access control (RBAC), and AES-256 encrypted payload handling.
- Optimized frontend asset bundle sizes using Webpack, improving Google Lighthouse performance score from 62 to 94.

EDUCATION
B.S. in Computer Science | University of California, Berkeley | 2014 - 2018
- Graduated with Honors (GPA: 3.8/4.0)

PROJECTS
AI Resume Analyzer & ATS Optimizer | Python, Flask, Groq API, PostgreSQL, Docker
- Built intelligent ATS resume parsing and scoring system analyzing candidates against job descriptions.
- Integrated LLM API for dynamic cover letter generation and technical interview practice flashcards.
"""

    parsed_data = ResumeParser.parse_resume(sample_text)
    
    # Save mock file on disk if not present
    if not saved_path.exists():
        with open(saved_path, "w", encoding="utf-8") as f:
            f.write(sample_text)

    resume = Resume(
        user_id=current_user.id,
        filename=sample_filename,
        filepath=str(saved_path),
        file_type="pdf",
        file_size=len(sample_text.encode('utf-8')),
        raw_text=sample_text.strip(),
    )
    resume.parsed_json = parsed_data

    db.session.add(resume)
    db.session.commit()

    flash("Sample resume successfully loaded for Demo Mode!", "success")
    return redirect(url_for("resume.detail", resume_id=resume.id))

