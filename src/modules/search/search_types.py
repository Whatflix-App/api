from pydantic import BaseModel, Field


class SearchMovieQuery(BaseModel):
    q: str = Field(min_length=1, max_length=200)
    page: int = Field(default=1, ge=1, le=1000)
    includeAdult: bool = False
    language: str = Field(default="en-US", min_length=2, max_length=12)


class SearchMovieItem(BaseModel):
    movieId: str
    title: str
    overview: str
    genreIds: list[int] = Field(default_factory=list)
    genres: list[str] = Field(default_factory=list)
    backdropPath: str | None = None
    releaseDate: str | None = None
    voteAverage: float
    voteCount: int
    popularity: float
    adult: bool
    originalLanguage: str | None = None


class SearchMoviesResponse(BaseModel):
    provider: str
    page: int
    totalPages: int
    totalResults: int
    items: list[SearchMovieItem]
