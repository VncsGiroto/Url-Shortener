from flask import Flask
from app.router.urlShortenerRouter import url_Shortener

app = Flask(__name__)
app.register_blueprint(url_Shortener)