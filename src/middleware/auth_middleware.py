from fastapi import Header

from src.shared.errors.app_error import AppError
from src.shared.security.token import decode_access_token


def get_current_user_id(authorization: str | None = Header(default=None)) -> str:
    if not authorization or not authorization.startswith("Bearer "):
        raise AppError(
            code="MISSING_AUTHORIZATION",
            message="Authorization header is required",
            retryable=False,
            status_code=401,
        )

    token = authorization.removeprefix("Bearer ").strip()
    if not token:
        raise AppError(
            code="MISSING_AUTHORIZATION",
            message="Authorization header is required",
            retryable=False,
            status_code=401,
        )

    payload = decode_access_token(token)
    user_id = payload.get("sub")
    if not isinstance(user_id, str) or not user_id:
        raise AppError(
            code="INVALID_ACCESS_TOKEN",
            message="Access token is invalid",
            retryable=False,
            status_code=401,
        )

    return user_id
