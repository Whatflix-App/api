from fastapi import APIRouter, Depends, Path
from sqlalchemy.orm import Session

from src.db.client import get_db
from src.middleware.auth_middleware import get_current_user_id
from src.modules.watchlist.watchlist_service import WatchlistService
from src.modules.watchlist.watchlist_types import (
    AddWatchlistRequest,
    RemoveWatchlistResponse,
    WatchlistItemResponse,
)

router = APIRouter(prefix="/watchlist", tags=["watchlist"])


@router.get("", response_model=list[WatchlistItemResponse])
def list_watchlist_items(
    user_id: str = Depends(get_current_user_id),
    db: Session = Depends(get_db),
) -> list[WatchlistItemResponse]:
    service = WatchlistService(db)
    return service.list_items(user_id)


@router.post("", response_model=WatchlistItemResponse)
def add_watchlist_item(
    payload: AddWatchlistRequest,
    user_id: str = Depends(get_current_user_id),
    db: Session = Depends(get_db),
) -> WatchlistItemResponse:
    service = WatchlistService(db)
    return service.add_item(user_id, payload)


@router.delete("/{movie_id}", response_model=RemoveWatchlistResponse)
def delete_watchlist_item(
    movie_id: str = Path(min_length=1, max_length=64),
    user_id: str = Depends(get_current_user_id),
    db: Session = Depends(get_db),
) -> RemoveWatchlistResponse:
    service = WatchlistService(db)
    return service.remove_item(user_id, movie_id)
