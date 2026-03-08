from fastapi import APIRouter, Depends, Path, Query

from src.middleware.auth_middleware import get_current_user_id
from src.modules.search.search_service import SearchService
from src.modules.search.search_types import SearchMovieItem, SearchMovieQuery, SearchMoviesResponse

router = APIRouter(prefix="/search", tags=["search"])


@router.get("/movies", response_model=SearchMoviesResponse)
def search_movies(
    q: str = Query(min_length=1, max_length=200),
    page: int = Query(default=1, ge=1, le=1000),
    include_adult: bool = Query(default=False, alias="includeAdult"),
    language: str = Query(default="en-US", min_length=2, max_length=12),
    _: str = Depends(get_current_user_id),
) -> SearchMoviesResponse:
    payload = SearchMovieQuery(
        q=q,
        page=page,
        includeAdult=include_adult,
        language=language,
    )
    service = SearchService()
    return service.search_movies(payload)


@router.get("/movies/{movie_id}", response_model=SearchMovieItem)
def get_movie(
    movie_id: str = Path(min_length=1, max_length=64),
    language: str = Query(default="en-US", min_length=2, max_length=12),
    _: str = Depends(get_current_user_id),
) -> SearchMovieItem:
    service = SearchService()
    return service.get_movie(movie_id=movie_id, language=language)
