from typing import Optional

from src.extensions import db
from src.urls.models import Url


class UrlRepository:
    """Persistence for Url — thin wrapper over db.session (S, I)."""

    def save(self, url: Url) -> Url:
        db.session.add(url)
        db.session.commit()
        return url

    def get_by_code(self, short_code: str) -> Optional[Url]:
        return Url.query.filter_by(short_code=short_code).first()

    def get_by_url(self, original_url: str) -> Optional[Url]:
        return Url.query.filter_by(original_url=original_url).first()
