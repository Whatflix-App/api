from datetime import datetime

from sqlalchemy import select
from sqlalchemy.orm import Session

from src.db.models import Session as SessionModel
from src.db.models import User


class AuthRepo:
    def __init__(self, db: Session):
        self.db = db

    def find_user_by_apple_sub(self, apple_sub: str) -> User | None:
        return self.db.scalar(select(User).where(User.apple_sub == apple_sub))

    def find_user_by_id(self, user_id: str) -> User | None:
        return self.db.scalar(select(User).where(User.id == user_id))

    def create_user(
        self,
        user_id: str,
        email: str | None,
        display_name: str | None,
        full_name: str | None,
        apple_sub: str,
        created_at: datetime,
    ) -> User:
        user = User(
            id=user_id,
            email=email,
            display_name=display_name,
            full_name=full_name,
            apple_sub=apple_sub,
            created_at=created_at,
        )
        self.db.add(user)
        self.db.flush()
        return user

    def create_session(
        self,
        session_id: str,
        user_id: str,
        refresh_token_hash: str,
        device_id: str,
        device_platform: str,
        app_version: str,
        expires_at: datetime,
        created_at: datetime,
    ) -> SessionModel:
        session = SessionModel(
            id=session_id,
            user_id=user_id,
            refresh_token_hash=refresh_token_hash,
            device_id=device_id,
            device_platform=device_platform,
            app_version=app_version,
            expires_at=expires_at,
            revoked_at=None,
            created_at=created_at,
        )
        self.db.add(session)
        self.db.flush()
        return session

    def find_session(self, session_id: str) -> SessionModel | None:
        return self.db.scalar(select(SessionModel).where(SessionModel.id == session_id))

    def revoke_session(self, session: SessionModel, revoked_at: datetime) -> None:
        session.revoked_at = revoked_at
        self.db.add(session)
        self.db.flush()

    def update_user_display_name(self, user: User, display_name: str | None) -> User:
        user.display_name = display_name
        self.db.add(user)
        self.db.flush()
        return user
