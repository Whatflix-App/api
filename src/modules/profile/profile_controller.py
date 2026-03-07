from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from src.db.client import get_db
from src.middleware.auth_middleware import get_current_user_id
from src.modules.profile.profile_service import ProfileService
from src.modules.profile.profile_types import ProfileResponse, UpdateProfileRequest

router = APIRouter(prefix="/profile", tags=["profile"])


@router.get("", response_model=ProfileResponse)
def get_profile(user_id: str = Depends(get_current_user_id), db: Session = Depends(get_db)) -> ProfileResponse:
    """
    Get the authenticated user's profile.

    Example:
        /profile {user_id(from access token)}
    """
    service = ProfileService(db)
    return service.get_profile(user_id)


@router.patch("", response_model=ProfileResponse)
def patch_profile(
    payload: UpdateProfileRequest,
    user_id: str = Depends(get_current_user_id),
    db: Session = Depends(get_db),
) -> ProfileResponse:
    """
    Update profile fields for the authenticated user.

    Example:
        /profile {user_id(from access token), displayName}
    """
    service = ProfileService(db)
    return service.update_profile(user_id, payload)
