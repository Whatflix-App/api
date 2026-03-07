from src.db.models import WatchlistItem
from src.modules.auth.auth_repo import AuthRepo
from src.modules.watchlist.watchlist_types import (
    AddWatchlistRequest,
    RemoveWatchlistResponse,
    WatchlistItemResponse,
)
from src.shared.errors.app_error import AppError
from src.shared.security.token import now_utc


class WatchlistService:
    def __init__(self, db):
        self.db = db
        self.auth_repo = AuthRepo(db)

    def add_item(self, user_id: str, payload: AddWatchlistRequest) -> WatchlistItemResponse:
        user = self.auth_repo.find_user_by_id(user_id)
        if user is None:
            raise AppError(
                code="USER_NOT_FOUND",
                message="User was not found",
                retryable=False,
                status_code=404,
            )

        existing = self.db.get(WatchlistItem, (user_id, payload.movieId))
        if existing is None:
            item = WatchlistItem(
                user_id=user_id,
                movie_id=payload.movieId,
                added_at=now_utc(),
                notes=payload.notes,
                priority=payload.priority,
            )
            self.db.add(item)
        else:
            existing.notes = payload.notes
            existing.priority = payload.priority
            item = existing

        self.db.commit()
        self.db.refresh(item)

        return WatchlistItemResponse(
            userId=item.user_id,
            movieId=item.movie_id,
            addedAt=item.added_at,
            notes=item.notes,
            priority=item.priority,
        )

    def remove_item(self, user_id: str, movie_id: str) -> RemoveWatchlistResponse:
        item = self.db.get(WatchlistItem, (user_id, movie_id))
        if item is not None:
            self.db.delete(item)
            self.db.commit()

        return RemoveWatchlistResponse(ok=True)
