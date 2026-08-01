import os
from pathlib import Path
from flask import Flask, render_template
from config import config
from extensions import db, login_manager, csrf, migrate


def create_app(config_name=None):
    """Application factory for AI Resume Analyzer & ATS Optimizer."""
    if config_name is None:
        config_name = os.getenv("FLASK_ENV", "development")

    app = Flask(__name__, instance_relative_config=True)
    app.config.from_object(config.get(config_name, config["default"]))

    # Ensure required directories exist
    for folder in [app.config["INSTANCE_PATH"], app.config["UPLOAD_FOLDER"], app.config["REPORT_FOLDER"]]:
        Path(folder).mkdir(parents=True, exist_ok=True)

    # Initialize extensions
    db.init_app(app)
    login_manager.init_app(app)
    csrf.init_app(app)
    migrate.init_app(app, db)

    # Register Blueprints
    from routes import blueprints
    for blueprint, url_prefix in blueprints:
        app.register_blueprint(blueprint, url_prefix=url_prefix)

    # Register CLI commands
    from cli import init_cli
    init_cli(app)

    # Register Context Processors
    @app.context_processor
    def inject_globals():
        return {
            "app_name": "AI Resume Analyzer & ATS Optimizer",
            "groq_configured": bool(app.config.get("GROQ_API_KEY")),
            "openai_configured": bool(app.config.get("GROQ_API_KEY"))
        }

    # Health Check Endpoint for Render & Uptime Monitoring
    @app.route("/health")
    def health_check():
        from flask import jsonify
        return jsonify({"status": "ok", "app": "AI Resume Analyzer & ATS Optimizer"}), 200

    # Production Security Headers Middleware
    @app.after_request
    def set_security_headers(response):
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["X-Frame-Options"] = "DENY"
        response.headers["X-XSS-Protection"] = "1; mode=block"
        response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
        return response

    # Error handlers
    @app.errorhandler(400)
    def bad_request(e):
        return render_template("errors/404.html"), 400

    @app.errorhandler(403)
    def forbidden(e):
        return render_template("errors/403.html"), 403

    @app.errorhandler(404)
    def page_not_found(e):
        return render_template("errors/404.html"), 404

    @app.errorhandler(500)
    def internal_server_error(e):
        return render_template("errors/500.html"), 500

    # Auto-create database tables in development
    with app.app_context():
        import models  # Ensure all models are imported
        db.create_all()

    return app


# Create WSGI application for Gunicorn
app = create_app()

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
