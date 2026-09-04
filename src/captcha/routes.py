import os

from flask import Blueprint, jsonify

captcha_bp = Blueprint("captcha", __name__)


@captcha_bp.route("/api/config", methods=["GET"])
def get_config():
    # Site key é pública por desenho — o segredo nunca sai do backend.
    return jsonify({"turnstile_site_key": os.getenv("TURNSTILE_SITE_KEY", "")})
