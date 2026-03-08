from src.modules.search.search_service import SearchService
from src.modules.search.search_types import SearchMovieQuery
from src.shared.clients.tmdb_client import TmdbMovie, TmdbSearchResult


class FakeTmdbClient:
    def __init__(self):
        self.calls: list[dict] = []

    def search_movies(self, query: str, page: int = 1, include_adult: bool = False, language: str = "en-US") -> TmdbSearchResult:
        self.calls.append(
            {
                "query": query,
                "page": page,
                "include_adult": include_adult,
                "language": language,
            }
        )
        return TmdbSearchResult(
            page=page,
            total_pages=12,
            total_results=240,
            items=[
                TmdbMovie(
                    id=550,
                    title="Fight Club",
                    overview="An insomniac office worker...",
                    genre_ids=[18, 53],
                    genres=["Drama", "Thriller"],
                    backdrop_path="/pB8BM7pdSp6B6Ih7QZ4DrQ3PmJK.jpg",
                    release_date="1999-10-15",
                    vote_average=8.4,
                    vote_count=29000,
                    popularity=84.2,
                    adult=False,
                    original_language="en",
                )
            ],
        )


def test_search_movies_maps_payload_and_response() -> None:
    tmdb = FakeTmdbClient()
    service = SearchService(tmdb_client=tmdb)

    result = service.search_movies(
        SearchMovieQuery(
            q="  fight club  ",
            page=2,
            includeAdult=False,
            language="en-US",
        )
    )

    assert tmdb.calls == [
        {
            "query": "fight club",
            "page": 2,
            "include_adult": False,
            "language": "en-US",
        }
    ]
    assert result.provider == "tmdb"
    assert result.page == 2
    assert result.totalPages == 12
    assert result.totalResults == 240
    assert len(result.items) == 1
    assert result.items[0].movieId == "550"
    assert result.items[0].title == "Fight Club"
    assert result.items[0].genreIds == [18, 53]
    assert result.items[0].genres == ["Drama", "Thriller"]
