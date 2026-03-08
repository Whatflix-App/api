from datetime import datetime

from fastapi import APIRouter, Depends, Path, Query
from sqlalchemy.orm import Session

from src.db.client import get_db
from src.middleware.auth_middleware import get_current_user_id
from src.modules.history.history_service import HistoryService
from src.modules.history.history_types import (
    CreateWatchHistoryEventRequest,
    RemoveWatchHistoryResponse,
    WatchHistoryEventResponse,
    WatchHistoryListResponse,
    WatchHistoryMovieResponse,
)

router = APIRouter(prefix="/history", tags=["history"])


@router.get("/watch", response_model=WatchHistoryListResponse)
def list_watch_history(
    limit: int = Query(default=20, ge=1, le=100),
    page: int = Query(default=1, ge=1),
    cursor: datetime | None = Query(default=None),
    from_date: datetime | None = Query(default=None, alias="from"),
    to_date: datetime | None = Query(default=None, alias="to"),
    user_id: str = Depends(get_current_user_id),
    db: Session = Depends(get_db),
) -> WatchHistoryListResponse:
    service = HistoryService(db)
    return service.list_watch_events(
        user_id=user_id,
        limit=limit,
        page=page,
        cursor=cursor,
        from_date=from_date,
        to_date=to_date,
    )


@router.post("/watch", response_model=WatchHistoryEventResponse)
def create_watch_history_event(
    payload: CreateWatchHistoryEventRequest,
    user_id: str = Depends(get_current_user_id),
    db: Session = Depends(get_db),
) -> WatchHistoryEventResponse:
    service = HistoryService(db)
    return service.create_watch_event(user_id, payload)


@router.get("/watch/{movie_id}", response_model=WatchHistoryMovieResponse)
def get_watch_history_for_movie(
    movie_id: str = Path(min_length=1, max_length=64),
    user_id: str = Depends(get_current_user_id),
    db: Session = Depends(get_db),
) -> WatchHistoryMovieResponse:
    service = HistoryService(db)
    return service.get_watch_events_for_movie(user_id, movie_id)


@router.delete("/watch/{movie_id}", response_model=RemoveWatchHistoryResponse)
def delete_watch_history_for_movie(
    movie_id: str = Path(min_length=1, max_length=64),
    user_id: str = Depends(get_current_user_id),
    db: Session = Depends(get_db),
) -> RemoveWatchHistoryResponse:
    service = HistoryService(db)
    return service.remove_watch_events_for_movie(user_id, movie_id)
