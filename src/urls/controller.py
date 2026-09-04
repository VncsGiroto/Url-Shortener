from typing import Optional

from src.common.http import HttpResponse
from src.urls.services import UrlService


class UrlController:
    """HTTP mapping over UrlService — orquestra e traduz erros em status (S)."""

    def __init__(self, service: Optional[UrlService] = None):
        self.service = service or UrlService()

    def create_url(self, data):
        try:
            if not data or not data.get("url"):
                return HttpResponse.error("url is required", 400)
            url = self.service.create(data["url"])
            return HttpResponse.success(
                url.to_dict(),
                "URL shortened successfully",
                201,
            )
        except ValueError as e:
            return HttpResponse.error(str(e), 400)
        except Exception:
            return HttpResponse.error("Internal server error", 500)

    def resolve_url(self, short_code: str):
        try:
            if not short_code or len(short_code) > 16 or not short_code.isalnum():
                return HttpResponse.error("URL not found", 404)
            url = self.service.resolve(short_code)
            if not url:
                return HttpResponse.error("URL not found", 404)
            return HttpResponse.success(
                {"original_url": url.original_url}, "URL found", 200
            )
        except Exception:
            return HttpResponse.error("Internal server error", 500)


# Alias for backwards compatibility
UrlServiceAlias = UrlService
