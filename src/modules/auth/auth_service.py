from datetime import UTC, datetime
from uuid import uuid4

from sqlalchemy.orm import Session

from src.modules.auth.apple_verify import verify_apple_identity
from src.modules.auth.auth_repo import AuthRepo
from src.modules.auth.auth_types import (
    AppleLoginRequest,
    AuthSession,
    AuthSuccessResponse,
    AuthUser,
    LogoutRequest,
    RefreshRequest,
    RefreshTokensResponse,
    TokenPair,
)
from src.shared.errors.app_error import AppError
from src.shared.security.token import (
    hash_token,
    issue_access_token,
    issue_refresh_token,
    now_utc,
    refresh_expires_at,
)


def _user_id() -> str:
    return f"usr_{uuid4().hex[:16]}"


def _session_id() -> str:
    return f"sess_{uuid4().hex[:16]}"


class AuthService:
    def __init__(self, db: Session):
        self.db = db
        self.repo = AuthRepo(db)

    def login_apple(self, payload: AppleLoginRequest) -> AuthSuccessResponse:
        apple_identity = verify_apple_identity(payload.identityToken, payload.authorizationCode)
        user = self.repo.find_user_by_apple_sub(apple_identity.sub)
        is_new_user = False

        if user is None:
            is_new_user = True
            now = datetime.now(UTC)
            user = self.repo.create_user(
                user_id=_user_id(),
                email=apple_identity.email,
                display_name=apple_identity.display_name,
                apple_sub=apple_identity.sub,
                created_at=now,
            )

        return self._issue_auth_response(
            user_id=user.id,
            email=user.email,
            display_name=user.display_name,
            auth_provider="apple",
            device_id=payload.device.id,
            device_platform=payload.device.platform,
            app_version=payload.device.appVersion,
            is_new_user=is_new_user,
        )

    def refresh(self, payload: RefreshRequest) -> RefreshTokensResponse:
        session = self.repo.find_session(payload.sessionId)
        if session is None:
            raise AppError(
                code="INVALID_SESSION",
                message="Session is invalid",
                retryable=False,
                status_code=401,
            )

        now = now_utc()
        if session.revoked_at is not None or session.expires_at < now:
            raise AppError(
                code="SESSION_EXPIRED",
                message="Session has expired",
                retryable=False,
                status_code=401,
            )

        if hash_token(payload.refreshToken) != session.refresh_token_hash:
            raise AppError(
                code="INVALID_SESSION",
                message="Session is invalid",
                retryable=False,
                status_code=401,
            )

        new_refresh = issue_refresh_token()
        new_refresh_exp = refresh_expires_at()
        session.refresh_token_hash = hash_token(new_refresh)
        session.expires_at = new_refresh_exp
        self.db.add(session)
        self.db.commit()

        access_token, access_exp = issue_access_token(user_id=session.user_id, session_id=session.id)
        return RefreshTokensResponse(
            tokens=TokenPair(
                accessToken=access_token,
                accessTokenExpiresAt=access_exp,
                refreshToken=new_refresh,
                refreshTokenExpiresAt=new_refresh_exp,
            )
        )

    def logout(self, payload: LogoutRequest) -> dict:
        session = self.repo.find_session(payload.sessionId)
        if session and hash_token(payload.refreshToken) == session.refresh_token_hash:
            self.repo.revoke_session(session, revoked_at=now_utc())
            self.db.commit()

        return {"ok": True}

    def _issue_auth_response(
        self,
        user_id: str,
        email: str | None,
        display_name: str | None,
        auth_provider: str,
        device_id: str,
        device_platform: str,
        app_version: str,
        is_new_user: bool,
    ) -> AuthSuccessResponse:
        session_id = _session_id()
        issued_at = now_utc()
        access_token, access_exp = issue_access_token(user_id=user_id, session_id=session_id)
        refresh_token = issue_refresh_token()
        refresh_exp = refresh_expires_at()

        self.repo.create_session(
            session_id=session_id,
            user_id=user_id,
            refresh_token_hash=hash_token(refresh_token),
            device_id=device_id,
            device_platform=device_platform,
            app_version=app_version,
            expires_at=refresh_exp,
            created_at=issued_at,
        )
        self.db.commit()

        return AuthSuccessResponse(
            user=AuthUser(
                id=user_id,
                email=email,
                displayName=display_name,
                authProvider=auth_provider,
            ),
            tokens=TokenPair(
                accessToken=access_token,
                accessTokenExpiresAt=access_exp,
                refreshToken=refresh_token,
                refreshTokenExpiresAt=refresh_exp,
            ),
            session=AuthSession(id=session_id, issuedAt=issued_at),
            isNewUser=is_new_user,
        )
