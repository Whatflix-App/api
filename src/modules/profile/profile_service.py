from sqlalchemy.orm import Session

from src.modules.auth.auth_repo import AuthRepo
from src.modules.profile.profile_types import ProfileResponse, UpdateProfileRequest
from src.shared.errors.app_error import AppError


class ProfileService:
    def __init__(self, db: Session):
        self.db = db
        self.repo = AuthRepo(db)

    def get_profile(self, user_id: str) -> ProfileResponse:
        user = self.repo.find_user_by_id(user_id)
        if user is None:
            raise AppError(
                code="USER_NOT_FOUND",
                message="User was not found",
                retryable=False,
                status_code=404,
            )

        return ProfileResponse(id=user.id, email=user.email, displayName=user.display_name)

    def update_profile(self, user_id: str, payload: UpdateProfileRequest) -> ProfileResponse:
        user = self.repo.find_user_by_id(user_id)
        if user is None:
            raise AppError(
                code="USER_NOT_FOUND",
                message="User was not found",
                retryable=False,
                status_code=404,
            )

        updated = self.repo.update_user_display_name(user, payload.displayName)
        self.db.commit()
        return ProfileResponse(id=updated.id, email=updated.email, displayName=updated.display_name)
