import os
from pathlib import Path
from flask import Flask, jsonify

from src.captcha.service import CaptchaService
from src.common.http import HttpResponse
from src.config import config_by_name
from src.extensions import db, migrate, limiter

# Frontend estático servido na mesma origem (sem CORS, sem build)
FRONTEND_DIR = Path(__file__).resolve().parent.parent / "frontend"


def create_app(config_name: str | None = None) -> Flask:
    app = Flask(__name__, static_folder=str(FRONTEND_DIR), static_url_path="/assets")

    # Resolve config: explicit param > FLASK_ENV/ENV > default
    resolved = config_name or os.getenv("FLASK_ENV") or os.getenv("ENV") or "default"
    config_cls = config_by_name.get(resolved, config_by_name["default"])
    app.config.from_object(config_cls)

    # Extensions — SQLAlchemy QueuePool lives for the app lifecycle
    db.init_app(app)
    migrate.init_app(app, db)
    limiter.init_app(app)

    if not CaptchaService().enabled:
        app.logger.warning(
            "TURNSTILE_SECRET_KEY ausente — captcha em bypass (apenas dev)"
        )

    # Import models to register with db.metadata for Alembic autogenerate
    with app.app_context():
        import src.urls.models  # noqa: F401

    # Blueprints
    from src.captcha.routes import captcha_bp
    from src.urls.routes import urls_bp

    app.register_blueprint(captcha_bp)
    app.register_blueprint(urls_bp)

    @app.route("/")
    def index():
        return app.send_static_file("index.html")

    # Rate-limit errors in the standard envelope instead of HTML
    @app.errorhandler(429)
    def ratelimit_exceeded(e):
        body, status = HttpResponse.error(
            "Rate limit exceeded, try again later", 429
        )
        return jsonify(body), status

    return app
