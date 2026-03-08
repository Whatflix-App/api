from uuid import uuid4

from sqlalchemy import select
from sqlalchemy.orm import Session

from src.db.models import Catalog, CatalogItem
from src.modules.auth.auth_repo import AuthRepo
from src.modules.catalogs.catalogs_types import (
    AddCatalogMovieRequest,
    CatalogMovieResponse,
    CatalogResponse,
    CreateCatalogRequest,
    RemoveCatalogMovieResponse,
    RemoveCatalogResponse,
)
from src.shared.errors.app_error import AppError
from src.shared.security.token import now_utc


class CatalogsService:
    def __init__(self, db: Session):
        self.db = db
        self.auth_repo = AuthRepo(db)

    def create_catalog(self, user_id: str, payload: CreateCatalogRequest) -> CatalogResponse:
        user = self.auth_repo.find_user_by_id(user_id)
        if user is None:
            raise AppError(
                code="USER_NOT_FOUND",
                message="User was not found",
                retryable=False,
                status_code=404,
            )

        now = now_utc()
        catalog = Catalog(
            id=f"cat_{uuid4().hex[:16]}",
            owner_user_id=user_id,
            name=payload.name,
            description=payload.description,
            is_public=payload.isPublic,
            created_at=now,
            updated_at=now,
        )
        self.db.add(catalog)
        self.db.commit()
        self.db.refresh(catalog)

        return CatalogResponse(
            id=catalog.id,
            ownerUserId=catalog.owner_user_id,
            name=catalog.name,
            description=catalog.description,
            isPublic=catalog.is_public,
            movieIds=[],
            createdAt=catalog.created_at,
            updatedAt=catalog.updated_at,
        )

    def list_catalogs(self, user_id: str) -> list[CatalogResponse]:
        catalogs = self.db.scalars(
            select(Catalog)
            .where(Catalog.owner_user_id == user_id)
            .order_by(Catalog.updated_at.desc())
        ).all()

        catalog_ids = [catalog.id for catalog in catalogs]
        movies_by_catalog: dict[str, list[str]] = {catalog_id: [] for catalog_id in catalog_ids}
        if catalog_ids:
            rows = self.db.execute(
                select(CatalogItem.catalog_id, CatalogItem.movie_id).where(
                    CatalogItem.catalog_id.in_(catalog_ids)
                )
            ).all()
            for catalog_id, movie_id in rows:
                movies_by_catalog[catalog_id].append(movie_id)

        return [
            CatalogResponse(
                id=catalog.id,
                ownerUserId=catalog.owner_user_id,
                name=catalog.name,
                description=catalog.description,
                isPublic=catalog.is_public,
                movieIds=movies_by_catalog.get(catalog.id, []),
                createdAt=catalog.created_at,
                updatedAt=catalog.updated_at,
            )
            for catalog in catalogs
        ]

    def remove_catalog(self, user_id: str, catalog_id: str) -> RemoveCatalogResponse:
        catalog = self.db.get(Catalog, catalog_id)
        if catalog is None:
            return RemoveCatalogResponse(ok=True)

        if catalog.owner_user_id != user_id:
            raise AppError(
                code="FORBIDDEN",
                message="Not allowed to modify this catalog",
                retryable=False,
                status_code=403,
            )

        self.db.delete(catalog)
        self.db.commit()
        return RemoveCatalogResponse(ok=True)

    def add_movie(self, user_id: str, catalog_id: str, payload: AddCatalogMovieRequest) -> CatalogMovieResponse:
        catalog = self.db.get(Catalog, catalog_id)
        if catalog is None:
            raise AppError(
                code="CATALOG_NOT_FOUND",
                message="Catalog was not found",
                retryable=False,
                status_code=404,
            )

        if catalog.owner_user_id != user_id:
            raise AppError(
                code="FORBIDDEN",
                message="Not allowed to modify this catalog",
                retryable=False,
                status_code=403,
            )

        existing = self.db.get(CatalogItem, (catalog_id, payload.movieId))
        if existing is None:
            item = CatalogItem(
                catalog_id=catalog_id,
                movie_id=payload.movieId,
                added_at=now_utc(),
                added_by_user_id=user_id,
            )
            self.db.add(item)
        else:
            item = existing

        catalog.updated_at = now_utc()
        self.db.add(catalog)
        self.db.commit()
        self.db.refresh(item)

        return CatalogMovieResponse(
            catalogId=item.catalog_id,
            movieId=item.movie_id,
            addedAt=item.added_at,
            addedByUserId=item.added_by_user_id,
        )

    def remove_movie(self, user_id: str, catalog_id: str, movie_id: str) -> RemoveCatalogMovieResponse:
        catalog = self.db.get(Catalog, catalog_id)
        if catalog is None:
            return RemoveCatalogMovieResponse(ok=True)

        if catalog.owner_user_id != user_id:
            raise AppError(
                code="FORBIDDEN",
                message="Not allowed to modify this catalog",
                retryable=False,
                status_code=403,
            )

        item = self.db.get(CatalogItem, (catalog_id, movie_id))
        if item is not None:
            self.db.delete(item)

        catalog.updated_at = now_utc()
        self.db.add(catalog)
        self.db.commit()
        return RemoveCatalogMovieResponse(ok=True)
