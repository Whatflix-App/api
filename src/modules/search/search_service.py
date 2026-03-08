from src.modules.search.search_types import SearchMovieItem, SearchMovieQuery, SearchMoviesResponse
from src.shared.clients.tmdb_client import TmdbClient


class SearchService:
    def __init__(self, tmdb_client: TmdbClient | None = None):
        self.tmdb_client = tmdb_client or TmdbClient()

    def search_movies(self, payload: SearchMovieQuery) -> SearchMoviesResponse:
        result = self.tmdb_client.search_movies(
            query=payload.q.strip(),
            page=payload.page,
            include_adult=payload.includeAdult,
            language=payload.language,
        )

        return SearchMoviesResponse(
            provider="tmdb",
            page=result.page,
            totalPages=result.total_pages,
            totalResults=result.total_results,
            items=[
                SearchMovieItem(
                    movieId=str(movie.id),
                    title=movie.title,
                    overview=movie.overview,
                    genreIds=movie.genre_ids,
                    genres=movie.genres,
                    backdropPath=movie.backdrop_path,
                    releaseDate=movie.release_date,
                    voteAverage=movie.vote_average,
                    voteCount=movie.vote_count,
                    popularity=movie.popularity,
                    adult=movie.adult,
                    originalLanguage=movie.original_language,
                )
                for movie in result.items
            ],
        )

    def get_movie(self, movie_id: str, language: str = "en-US") -> SearchMovieItem:
        movie = self.tmdb_client.get_movie(movie_id=movie_id, language=language)
        return SearchMovieItem(
            movieId=str(movie.id),
            title=movie.title,
            overview=movie.overview,
            genreIds=movie.genre_ids,
            genres=movie.genres,
            backdropPath=movie.backdrop_path,
            releaseDate=movie.release_date,
            voteAverage=movie.vote_average,
            voteCount=movie.vote_count,
            popularity=movie.popularity,
            adult=movie.adult,
            originalLanguage=movie.original_language,
        )
