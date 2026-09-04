import json
import os
from urllib.parse import urlencode
from urllib.request import Request, urlopen

VERIFY_URL = "https://challenges.cloudflare.com/turnstile/v0/siteverify"


class CaptchaService:
    """Valida tokens do Cloudflare Turnstile (stdlib, sem dependência nova)."""

    def __init__(self, secret_key: str | None = None, timeout: int = 5):
        self.secret_key = (
            secret_key if secret_key is not None else os.getenv("TURNSTILE_SECRET_KEY")
        )
        self.timeout = timeout

    @property
    def enabled(self) -> bool:
        return bool(self.secret_key)

    def verify(self, token: str | None) -> bool:
        # Sem secret configurado: bypass em dev (com aviso no log do app).
        if not self.enabled:
            return True
        if not token:
            return False
        payload = urlencode({"secret": self.secret_key, "response": token}).encode()
        req = Request(VERIFY_URL, data=payload, method="POST")
        try:
            with urlopen(req, timeout=self.timeout) as resp:
                result = json.loads(resp.read().decode())
        except Exception:
            return False
        return bool(result.get("success"))
