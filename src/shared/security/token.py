import hashlib
import secrets
from datetime import UTC, datetime, timedelta

from jose import jwt
from jose.exceptions import JWTError

from src.config.env import settings
from src.shared.errors.app_error import AppError

ALGORITHM = "HS256"


def now_utc() -> datetime:
    return datetime.now(UTC)


def issue_access_token(user_id: str, session_id: str) -> tuple[str, datetime]:
    expires_at = now_utc() + timedelta(minutes=settings.access_token_ttl_minutes)
    payload = {
        "sub": user_id,
        "sid": session_id,
        "exp": int(expires_at.timestamp()),
    }
    return jwt.encode(payload, settings.jwt_secret, algorithm=ALGORITHM), expires_at


def issue_refresh_token() -> str:
    return secrets.token_urlsafe(48)


def hash_token(raw_token: str) -> str:
    return hashlib.sha256(raw_token.encode("utf-8")).hexdigest()


def refresh_expires_at() -> datetime:
    return now_utc() + timedelta(days=settings.refresh_token_ttl_days)


def decode_access_token(token: str) -> dict:
    try:
        return jwt.decode(token, settings.jwt_secret, algorithms=[ALGORITHM])
    except JWTError as exc:
        raise AppError(
            code="INVALID_ACCESS_TOKEN",
            message="Access token is invalid",
            retryable=False,
            status_code=401,
        ) from exc
