from routes.main import main_bp
from routes.auth import auth_bp
from routes.dashboard import dashboard_bp
from routes.resume import resume_bp
from routes.analysis import analysis_bp
from routes.reports import reports_bp
from routes.admin import admin_bp

blueprints = [
    (main_bp, ""),
    (auth_bp, "/auth"),
    (dashboard_bp, "/dashboard"),
    (resume_bp, "/resume"),
    (analysis_bp, "/analysis"),
    (reports_bp, "/reports"),
    (admin_bp, "/admin"),
]
