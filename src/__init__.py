import os
from flask import Flask

from src.config import config_by_name
from src.extensions import db, migrate


def create_app(config_name: str | None = None) -> Flask:
    app = Flask(__name__)

    # Resolve config: explicit param > FLASK_ENV/ENV > default
    resolved = config_name or os.getenv("FLASK_ENV") or os.getenv("ENV") or "default"
    config_cls = config_by_name.get(resolved, config_by_name["default"])
    app.config.from_object(config_cls)

    # Extensions — SQLAlchemy QueuePool lives for the app lifecycle
    db.init_app(app)
    migrate.init_app(app, db)

    # Import models to register with db.metadata for Alembic autogenerate
    with app.app_context():
        import src.urls.models  # noqa: F401

    # Blueprints
    from src.urls.routes import urls_bp

    app.register_blueprint(urls_bp)

    return app
