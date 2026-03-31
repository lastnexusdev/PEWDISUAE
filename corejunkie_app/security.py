import base64
import hashlib
import hmac
import json
import os
from typing import Optional

SECRET_KEY = os.getenv("SECRET_KEY", "dev-secret-change-me").encode("utf-8")
COOKIE_NAME = "cj_session"


def hash_password(password: str, salt: Optional[bytes] = None) -> str:
    salt = salt or os.urandom(16)
    pwd_hash = hashlib.pbkdf2_hmac("sha256", password.encode("utf-8"), salt, 200_000)
    return base64.b64encode(salt).decode() + ":" + base64.b64encode(pwd_hash).decode()


def verify_password(password: str, stored: str) -> bool:
    salt_b64, hash_b64 = stored.split(":", 1)
    salt = base64.b64decode(salt_b64)
    expected = base64.b64decode(hash_b64)
    actual = hashlib.pbkdf2_hmac("sha256", password.encode("utf-8"), salt, 200_000)
    return hmac.compare_digest(actual, expected)


def _sign(data: bytes) -> str:
    return hmac.new(SECRET_KEY, data, hashlib.sha256).hexdigest()


def make_session_token(user_id: int) -> str:
    payload = json.dumps({"user_id": user_id}, separators=(",", ":")).encode("utf-8")
    payload_b64 = base64.urlsafe_b64encode(payload).decode("utf-8")
    sig = _sign(payload)
    return f"{payload_b64}.{sig}"


def parse_session_token(token: str) -> Optional[int]:
    try:
        payload_b64, sig = token.split(".", 1)
        payload = base64.urlsafe_b64decode(payload_b64.encode("utf-8"))
    except Exception:
        return None

    if not hmac.compare_digest(sig, _sign(payload)):
        return None

    try:
        parsed = json.loads(payload.decode("utf-8"))
        return int(parsed["user_id"])
    except Exception:
        return None
