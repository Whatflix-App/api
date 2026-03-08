from datetime import datetime

from pydantic import BaseModel, Field


class CreateWatchHistoryEventRequest(BaseModel):
    movieId: str = Field(min_length=1, max_length=64)
    watchedAt: datetime
    completed: bool = False
    progressPct: int = Field(default=0, ge=0, le=100)
    source: str = Field(default="manual", min_length=1, max_length=32)


class WatchHistoryEventResponse(BaseModel):
    id: str
    userId: str
    movieId: str
    watchedAt: datetime
    completed: bool
    progressPct: int
    source: str
    createdAt: datetime


class WatchHistoryListResponse(BaseModel):
    items: list[WatchHistoryEventResponse]
    limit: int
    page: int
    nextCursor: datetime | None = None


class WatchHistoryMovieResponse(BaseModel):
    movieId: str
    items: list[WatchHistoryEventResponse]


class RemoveWatchHistoryResponse(BaseModel):
    ok: bool
    deletedCount: int
