from src.common.http import HttpResponse
from src.urls.services import UrlService


class UrlController:
    @staticmethod
    def create_url(data):
        try:
            if not data or not data.get("url"):
                return HttpResponse.error("url is required", 400)
            service = UrlService()
            url = service.create(data["url"])
            return HttpResponse.success(
                {"short_code": url.short_code, "original_url": url.original_url},
                "URL shortened successfully",
                201,
            )
        except ValueError as e:
            return HttpResponse.error(str(e), 400)
        except Exception as e:
            return HttpResponse.error("Internal server error", 500)

    @staticmethod
    def resolve_url(short_code: str):
        try:
            service = UrlService()
            url = service.resolve(short_code)
            if not url:
                return HttpResponse.error("URL not found", 404)
            return HttpResponse.success(
                {"original_url": url.original_url}, "URL found", 200
            )
        except Exception:
            return HttpResponse.error("Internal server error", 500)


# Alias for backwards compatibility
UrlServiceAlias = UrlService
