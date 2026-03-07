from datetime import datetime

from pydantic import BaseModel, Field


class AddWatchlistRequest(BaseModel):
    movieId: str = Field(min_length=1, max_length=64)
    notes: str | None = None
    priority: int | None = Field(default=None, ge=0, le=5)


class WatchlistItemResponse(BaseModel):
    userId: str
    movieId: str
    addedAt: datetime
    notes: str | None = None
    priority: int | None = None


class RemoveWatchlistResponse(BaseModel):
    ok: bool
