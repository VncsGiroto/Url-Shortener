from flask import Blueprint, jsonify, request

from src.urls.controller import UrlController

urls_bp = Blueprint("urls", __name__)

# Backwards compat
url_Shortener = urls_bp

@urls_bp.route("/urls/shorten", methods=["POST"])
def shorten_url():
    data = request.get_json()
    response = UrlController.create_url(data)
    return jsonify(response), response.get("status_code", 200)