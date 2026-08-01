from pathlib import Path
from flask import Blueprint, render_template, redirect, url_for, flash, send_file, Response, current_app, request
from flask_login import login_required, current_user
from extensions import db
from models.report import Report
from models.resume import Resume
from services.report_generator import ReportGenerator

reports_bp = Blueprint("reports", __name__)


@reports_bp.route("/")
@login_required
def list_reports():
    """List user reports."""
    user_reports = Report.query.filter_by(user_id=current_user.id).order_by(Report.created_at.desc()).all()
    return render_template("reports_list.html", reports=user_reports)


@reports_bp.route("/<int:report_id>")
@login_required
def view_report(report_id):
    """View report detail."""
    report = Report.query.filter_by(id=report_id, user_id=current_user.id).first_or_404()
    resume = Resume.query.get(report.resume_id)
    return render_template("report_detail.html", report=report, resume=resume)


@reports_bp.route("/<int:report_id>/download/<fmt>")
@login_required
def download(report_id, fmt):
    """Download report as PDF, DOCX, Markdown, or HTML."""
    report = Report.query.filter_by(id=report_id, user_id=current_user.id).first_or_404()
    resume = Resume.query.get(report.resume_id)

    fmt_lower = fmt.lower()
    out_dir = Path(current_app.config["REPORT_FOLDER"])
    out_dir.mkdir(exist_ok=True, parents=True)

    if fmt_lower == "pdf":
        pdf_path = out_dir / f"report_{report.id}.pdf"
        ReportGenerator.generate_pdf(report, resume, current_user, pdf_path)
        return send_file(pdf_path, as_attachment=True, download_name=f"ATS_Report_{resume.filename}.pdf")

    elif fmt_lower == "docx":
        docx_path = out_dir / f"report_{report.id}.docx"
        ReportGenerator.generate_docx(report, resume, current_user, docx_path)
        return send_file(docx_path, as_attachment=True, download_name=f"ATS_Report_{resume.filename}.docx")

    elif fmt_lower in ["md", "markdown"]:
        md_text = ReportGenerator.generate_markdown(report, resume, current_user)
        return Response(
            md_text,
            mimetype="text/markdown",
            headers={"Content-disposition": f"attachment; filename=ATS_Report_{report.id}.md"}
        )

    elif fmt_lower == "html":
        html_text = ReportGenerator.generate_html(report, resume, current_user)
        return Response(
            html_text,
            mimetype="text/html",
            headers={"Content-disposition": f"attachment; filename=ATS_Report_{report.id}.html"}
        )

    flash("Unsupported format.", "danger")
    return redirect(url_for("reports.view_report", report_id=report.id))


@reports_bp.route("/compare")
@login_required
def compare():
    """Compare multiple reports."""
    report_ids = request.args.getlist("id")
    if not report_ids:
        user_reports = Report.query.filter_by(user_id=current_user.id).order_by(Report.created_at.desc()).all()
        return render_template("reports_compare_select.html", reports=user_reports)

    reports = Report.query.filter(Report.id.in_(report_ids), Report.user_id == current_user.id).all()
    return render_template("reports_compare.html", reports=reports)


@reports_bp.route("/<int:report_id>/delete", methods=["POST"])
@login_required
def delete(report_id):
    """Delete report."""
    report = Report.query.filter_by(id=report_id, user_id=current_user.id).first_or_404()
    db.session.delete(report)
    db.session.commit()
    flash("Report deleted.", "info")
    return redirect(url_for("reports.list_reports"))
