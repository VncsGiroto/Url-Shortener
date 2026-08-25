
from app.utils.response import Response


class UrlShortenerController:
    @staticmethod
    def shorten_url(url):
        shortened_url = "http://short.url/abc123"
        if url:
            return Response.success(shortened_url, "URL shortened successfully", status_code=200)
        return Response.error("Invalid URL provided", status_code=400)

    @staticmethod
    def redirect_url(short_url):
        original_url = "http://original.url/xyz789"
        if short_url:
            return Response.success(original_url, "Redirecting to original URL", status_code=200)
        return Response.error("Short URL not found", status_code=404)


# Backwards compat for old import name
urlShortenerController = UrlShortenerController
