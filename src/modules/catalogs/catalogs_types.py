from datetime import datetime

from pydantic import BaseModel, Field


class CreateCatalogRequest(BaseModel):
    name: str = Field(min_length=1, max_length=120)
    description: str | None = None
    isPublic: bool = False


class CatalogResponse(BaseModel):
    id: str
    ownerUserId: str
    name: str
    description: str | None = None
    isPublic: bool
    createdAt: datetime
    updatedAt: datetime


class RemoveCatalogResponse(BaseModel):
    ok: bool


class AddCatalogMovieRequest(BaseModel):
    movieId: str = Field(min_length=1, max_length=64)


class CatalogMovieResponse(BaseModel):
    catalogId: str
    movieId: str
    addedAt: datetime
    addedByUserId: str | None = None


class RemoveCatalogMovieResponse(BaseModel):
    ok: bool
