from flask import Blueprint, render_template, Response, request

main_bp = Blueprint("main", __name__)


@main_bp.route("/")
def index():
    """Landing Page route."""
    return render_template("landing.html")


@main_bp.route("/robots.txt")
def robots():
    """Returns robots.txt for search engines pointing to dynamic sitemap."""
    base_url = request.url_root.rstrip('/')
    content = f"User-agent: *\nAllow: /\nDisallow: /admin/\nDisallow: /auth/\nSitemap: {base_url}/sitemap.xml\n"
    return Response(content, mimetype="text/plain")


@main_bp.route("/sitemap.xml")
def sitemap():
    """Returns dynamic sitemap.xml for search engines."""
    base_url = request.url_root.rstrip('/')
    content = f"""<?xml version="1.0" encoding="UTF-8"?>
<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">
    <url><loc>{base_url}/</loc><changefreq>weekly</changefreq><priority>1.0</priority></url>
    <url><loc>{base_url}/auth/login</loc><changefreq>monthly</changefreq><priority>0.8</priority></url>
    <url><loc>{base_url}/auth/register</loc><changefreq>monthly</changefreq><priority>0.8</priority></url>
</urlset>"""
    return Response(content, mimetype="application/xml")
