import secrets
import string
from typing import Optional
from urllib.parse import urlparse

from sqlalchemy.exc import IntegrityError

from src.urls.models import Url
from src.urls.repository import UrlRepository

MAX_URL_LENGTH = 2048
MAX_CODE_ATTEMPTS = 5


class UrlService:
    def __init__(self, repository: Optional[UrlRepository] = None):
        self.repository = repository or UrlRepository()

    def create(self, original_url: str) -> Url:
        url = self._validate_url(original_url)
        # Tenta gerar código único; em corrida, o unique do banco levanta
        # IntegrityError (com rollback no repository) e regeneramos o código
        for _ in range(MAX_CODE_ATTEMPTS):
            short_code = self._generate_code()
            if self.repository.get_by_code(short_code) is not None:
                continue
            try:
                return self.repository.save(
                    Url(original_url=url, short_code=short_code)
                )
            except IntegrityError:
                continue
        raise ValueError("could not generate a unique short code")

    def resolve(self, short_code: str) -> Optional[Url]:
        return self.repository.get_by_code(short_code)

    @staticmethod
    def _validate_url(original_url: str) -> str:
        url = (original_url or "").strip()
        if not url:
            raise ValueError("original_url is required")
        if len(url) > MAX_URL_LENGTH:
            raise ValueError(f"original_url exceeds {MAX_URL_LENGTH} characters")
        parsed = urlparse(url)
        if parsed.scheme not in ("http", "https") or not parsed.netloc:
            raise ValueError("original_url must be a valid http(s) URL")
        return url

    @staticmethod
    def _generate_code(length: int = 6) -> str:
        alphabet = string.ascii_letters + string.digits
        return "".join(secrets.choice(alphabet) for _ in range(length))
