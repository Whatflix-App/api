from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from src.db.client import get_db
from src.modules.auth.auth_service import AuthService
from src.modules.auth.auth_types import (
    AppleLoginRequest,
    AuthSuccessResponse,
    LogoutRequest,
    RefreshRequest,
    RefreshTokensResponse,
)

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/apple", response_model=AuthSuccessResponse)
def apple_login(payload: AppleLoginRequest, db: Session = Depends(get_db)) -> AuthSuccessResponse:
    """
    Exchange Apple identity credentials for app session tokens.

    Example:
        /auth/apple {provider, identityToken, authorizationCode, device{id, platform, appVersion}}
    """
    service = AuthService(db)
    return service.login_apple(payload)


@router.post("/refresh", response_model=RefreshTokensResponse)
def refresh(payload: RefreshRequest, db: Session = Depends(get_db)) -> RefreshTokensResponse:
    """
    Refresh expired access credentials using a valid refresh token.

    Example:
        /auth/refresh {refreshToken, sessionId}
    """
    service = AuthService(db)
    return service.refresh(payload)


@router.post("/logout")
def logout(payload: LogoutRequest, db: Session = Depends(get_db)) -> dict:
    """
    Revoke refresh token and terminate the current session.

    Example:
        /auth/logout {refreshToken, sessionId}
    """
    service = AuthService(db)
    return service.logout(payload)
