import secrets
import string
from typing import Optional

from src.urls.models import Url
from src.urls.repository import UrlRepository


class UrlService:
    def __init__(self):
        self.repository = UrlRepository()

    def create(self, original_url: str) -> Url:
        if not original_url:
            raise ValueError("original_url is required")
        short_code = self._generate_code()
        # Ensure uniqueness (retry on collision)
        while self.repository.get_by_code(short_code) is not None:
            short_code = self._generate_code()
        url = Url(original_url=original_url, short_code=short_code)
        return self.repository.save(url)

    def resolve(self, short_code: str) -> Optional[Url]:
        return self.repository.get_by_code(short_code)

    @staticmethod
    def _generate_code(length: int = 6) -> str:
        alphabet = string.ascii_letters + string.digits
        return "".join(secrets.choice(alphabet) for _ in range(length))
