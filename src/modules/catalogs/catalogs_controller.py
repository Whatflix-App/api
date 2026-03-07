from fastapi import APIRouter, Depends, Path
from sqlalchemy.orm import Session

from src.db.client import get_db
from src.middleware.auth_middleware import get_current_user_id
from src.modules.catalogs.catalogs_service import CatalogsService
from src.modules.catalogs.catalogs_types import (
    AddCatalogMovieRequest,
    CatalogMovieResponse,
    CatalogResponse,
    CreateCatalogRequest,
    RemoveCatalogMovieResponse,
    RemoveCatalogResponse,
)

router = APIRouter(prefix="/catalogs", tags=["catalogs"])


@router.get("", response_model=list[CatalogResponse])
def list_catalogs(
    user_id: str = Depends(get_current_user_id),
    db: Session = Depends(get_db),
) -> list[CatalogResponse]:
    service = CatalogsService(db)
    return service.list_catalogs(user_id)


@router.post("", response_model=CatalogResponse)
def create_catalog(
    payload: CreateCatalogRequest,
    user_id: str = Depends(get_current_user_id),
    db: Session = Depends(get_db),
) -> CatalogResponse:
    service = CatalogsService(db)
    return service.create_catalog(user_id, payload)


@router.delete("/{catalog_id}", response_model=RemoveCatalogResponse)
def delete_catalog(
    catalog_id: str = Path(min_length=1, max_length=64),
    user_id: str = Depends(get_current_user_id),
    db: Session = Depends(get_db),
) -> RemoveCatalogResponse:
    service = CatalogsService(db)
    return service.remove_catalog(user_id, catalog_id)


@router.post("/{catalog_id}/movies", response_model=CatalogMovieResponse)
def add_movie_to_catalog(
    catalog_id: str,
    payload: AddCatalogMovieRequest,
    user_id: str = Depends(get_current_user_id),
    db: Session = Depends(get_db),
) -> CatalogMovieResponse:
    service = CatalogsService(db)
    return service.add_movie(user_id, catalog_id, payload)


@router.delete("/{catalog_id}/movies/{movie_id}", response_model=RemoveCatalogMovieResponse)
def remove_movie_from_catalog(
    catalog_id: str,
    movie_id: str,
    user_id: str = Depends(get_current_user_id),
    db: Session = Depends(get_db),
) -> RemoveCatalogMovieResponse:
    service = CatalogsService(db)
    return service.remove_movie(user_id, catalog_id, movie_id)
