from flask import Blueprint, jsonify, request, redirect

from src.urls.controller import UrlController

urls_bp = Blueprint("urls", __name__)

# Backwards compat
url_Shortener = urls_bp


@urls_bp.route("/urls/shorten", methods=["POST"])
def shorten_url():
    data = request.get_json(silent=True)
    body, status = UrlController.create_url(data)
    return jsonify(body), status


@urls_bp.route("/<short_code>", methods=["GET"])
def resolve_short_url(short_code: str):
    body, status = UrlController.resolve_url(short_code)
    # If found, redirect to original URL (common shortener behavior)
    if status == 200:
        return redirect(body["data"]["original_url"])
    return jsonify(body), status
