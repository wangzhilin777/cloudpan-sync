from __future__ import annotations

import base64
import hashlib
import hmac

from .config import SESSION_SECRET


def build_session_token(username: str) -> str:
    payload = username.encode("utf-8")
    signature = hmac.new(
        SESSION_SECRET.encode("utf-8"),
        payload,
        hashlib.sha256,
    ).hexdigest()
    token_raw = payload + b"." + signature.encode("ascii")
    return base64.urlsafe_b64encode(token_raw).decode("ascii")


def verify_session_token(token: str) -> bool:
    if not token:
        return False
    try:
        token_raw = base64.urlsafe_b64decode(token.encode("ascii"))
        payload, signature = token_raw.rsplit(b".", 1)
    except Exception:
        return False
    expected = hmac.new(
        SESSION_SECRET.encode("utf-8"),
        payload,
        hashlib.sha256,
    ).hexdigest().encode("ascii")
    return hmac.compare_digest(signature, expected)
