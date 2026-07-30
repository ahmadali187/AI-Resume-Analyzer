from flask import Blueprint, render_template, Response

main_bp = Blueprint("main", __name__)


@main_bp.route("/")
def index():
    """Landing Page route."""
    return render_template("landing.html")


@main_bp.route("/robots.txt")
def robots():
    """Returns robots.txt for search engines."""
    content = "User-agent: *\nAllow: /\nDisallow: /admin/\nSitemap: http://127.0.0.1:5000/sitemap.xml\n"
    return Response(content, mimetype="text/plain")


@main_bp.route("/sitemap.xml")
def sitemap():
    """Returns sitemap.xml for search engines."""
    content = """<?xml version="1.0" encoding="UTF-8"?>
<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">
    <url><loc>http://127.0.0.1:5000/</loc><changefreq>weekly</changefreq><priority>1.0</priority></url>
    <url><loc>http://127.0.0.1:5000/auth/login</loc><changefreq>monthly</changefreq><priority>0.8</priority></url>
    <url><loc>http://127.0.0.1:5000/auth/register</loc><changefreq>monthly</changefreq><priority>0.8</priority></url>
</urlset>"""
    return Response(content, mimetype="application/xml")
