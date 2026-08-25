from flask import Blueprint, jsonify, request
from app.controller.urlShortenerController import UrlShortenerController

url_Shortener = Blueprint('url_shortener', __name__)

@url_Shortener.route('/shorten', methods=['POST'])
def shorten_url():
    data = request.get_json(silent=True) or {}
    url = data.get('url') if isinstance(data, dict) else None
    response, status_code = UrlShortenerController.shorten_url(url)
    return jsonify(response), status_code

@url_Shortener.route('/<short_url>', methods=['GET'])
def redirect_url(short_url):
    response, status_code = UrlShortenerController.redirect_url(short_url)
    return jsonify(response), status_code