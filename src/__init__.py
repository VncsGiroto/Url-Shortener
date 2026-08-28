import os
from flask import Flask

from src.config import Config
from src.extensions import db


def create_app(config_name: str | None = None) -> Flask:
    app = Flask(__name__)
    app.config.from_object(Config)

    # Extensions
    db.init_app(app)

    # Blueprints
    from src.urls.routes import urls_bp

    app.register_blueprint(urls_bp)

    return app
