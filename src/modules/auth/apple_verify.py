import base64
import json

from src.shared.errors.app_error import AppError


class AppleIdentity:
    def __init__(self, sub: str, email: str | None, display_name: str | None):
        self.sub = sub
        self.email = email
        self.display_name = display_name


def verify_apple_identity(identity_token: str, _: str) -> AppleIdentity:
    token_parts = identity_token.split(".")
    if len(token_parts) != 3:
        raise AppError(
            code="INVALID_APPLE_TOKEN",
            message="Apple identity token is invalid",
            retryable=False,
            status_code=401,
        )

    try:
        payload_segment = token_parts[1]
        padded = payload_segment + "=" * (-len(payload_segment) % 4)
        decoded = base64.urlsafe_b64decode(padded.encode("utf-8"))
        payload = json.loads(decoded.decode("utf-8"))
    except Exception as exc:
        raise AppError(
            code="INVALID_APPLE_TOKEN",
            message="Apple identity token is invalid",
            retryable=False,
            status_code=401,
        ) from exc

    sub = payload.get("sub")
    if not isinstance(sub, str) or not sub:
        raise AppError(
            code="INVALID_APPLE_TOKEN",
            message="Apple identity token is invalid",
            retryable=False,
            status_code=401,
        )

    email = payload.get("email") if isinstance(payload.get("email"), str) else None
    return AppleIdentity(sub=sub, email=email, display_name="Apple User")
