from datetime import datetime
from uuid import uuid4

from sqlalchemy import Select, delete, select
from sqlalchemy.orm import Session

from src.db.models import WatchHistory
from src.modules.auth.auth_repo import AuthRepo
from src.modules.history.history_types import (
    CreateWatchHistoryEventRequest,
    RemoveWatchHistoryResponse,
    WatchHistoryEventResponse,
    WatchHistoryListResponse,
    WatchHistoryMovieResponse,
)
from src.shared.errors.app_error import AppError
from src.shared.security.token import now_utc


class HistoryService:
    def __init__(self, db: Session):
        self.db = db
        self.auth_repo = AuthRepo(db)

    def list_watch_events(
        self,
        user_id: str,
        limit: int,
        page: int,
        cursor: datetime | None,
        from_date: datetime | None,
        to_date: datetime | None,
    ) -> WatchHistoryListResponse:
        self._ensure_user_exists(user_id)

        stmt: Select[tuple[WatchHistory]] = select(WatchHistory).where(
            WatchHistory.user_id == user_id
        )
        if from_date is not None:
            stmt = stmt.where(WatchHistory.watched_at >= from_date)
        if to_date is not None:
            stmt = stmt.where(WatchHistory.watched_at <= to_date)
        if cursor is not None:
            stmt = stmt.where(WatchHistory.watched_at < cursor)

        stmt = stmt.order_by(WatchHistory.watched_at.desc(), WatchHistory.created_at.desc())

        if cursor is None:
            offset = (page - 1) * limit
            stmt = stmt.offset(offset)

        rows = self.db.scalars(stmt.limit(limit + 1)).all()
        has_more = len(rows) > limit
        items = rows[:limit]
        next_cursor = items[-1].watched_at if has_more and items else None

        return WatchHistoryListResponse(
            items=[self._to_event_response(item) for item in items],
            limit=limit,
            page=page,
            nextCursor=next_cursor,
        )

    def create_watch_event(
        self,
        user_id: str,
        payload: CreateWatchHistoryEventRequest,
    ) -> WatchHistoryEventResponse:
        self._ensure_user_exists(user_id)

        event = WatchHistory(
            id=f"whe_{uuid4().hex[:16]}",
            user_id=user_id,
            movie_id=payload.movieId,
            watched_at=payload.watchedAt,
            completed=payload.completed,
            progress_pct=payload.progressPct,
            source=payload.source,
            created_at=now_utc(),
        )
        self.db.add(event)
        self.db.commit()
        self.db.refresh(event)

        return self._to_event_response(event)

    def get_watch_events_for_movie(self, user_id: str, movie_id: str) -> WatchHistoryMovieResponse:
        self._ensure_user_exists(user_id)

        items = self.db.scalars(
            select(WatchHistory)
            .where(WatchHistory.user_id == user_id, WatchHistory.movie_id == movie_id)
            .order_by(WatchHistory.watched_at.desc(), WatchHistory.created_at.desc())
        ).all()

        return WatchHistoryMovieResponse(
            movieId=movie_id,
            items=[self._to_event_response(item) for item in items],
        )

    def remove_watch_events_for_movie(self, user_id: str, movie_id: str) -> RemoveWatchHistoryResponse:
        self._ensure_user_exists(user_id)

        result = self.db.execute(
            delete(WatchHistory).where(
                WatchHistory.user_id == user_id,
                WatchHistory.movie_id == movie_id,
            )
        )
        self.db.commit()

        return RemoveWatchHistoryResponse(ok=True, deletedCount=result.rowcount or 0)

    def _ensure_user_exists(self, user_id: str) -> None:
        user = self.auth_repo.find_user_by_id(user_id)
        if user is None:
            raise AppError(
                code="USER_NOT_FOUND",
                message="User was not found",
                retryable=False,
                status_code=404,
            )

    @staticmethod
    def _to_event_response(item: WatchHistory) -> WatchHistoryEventResponse:
        return WatchHistoryEventResponse(
            id=item.id,
            userId=item.user_id,
            movieId=item.movie_id,
            watchedAt=item.watched_at,
            completed=item.completed,
            progressPct=item.progress_pct,
            source=item.source,
            createdAt=item.created_at,
        )
