import json
from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from urllib.error import HTTPError, URLError
from urllib.parse import urlencode
from urllib.request import Request, urlopen

from src.config.env import settings
from src.shared.errors.app_error import AppError


@dataclass
class TmdbMovie:
    id: int
    title: str
    overview: str
    backdrop_path: str | None
    release_date: str | None
    vote_average: float
    vote_count: int
    popularity: float
    adult: bool
    original_language: str | None
    genre_ids: list[int]
    genres: list[str]


@dataclass
class TmdbSearchResult:
    page: int
    total_pages: int
    total_results: int
    items: list[TmdbMovie]


class TmdbClient:
    _genre_map_cache: dict[str, dict[int, str]] = {}
    _genre_map_expires_at: dict[str, datetime] = {}

    def search_movies(
        self,
        query: str,
        page: int = 1,
        include_adult: bool = False,
        language: str = "en-US",
    ) -> TmdbSearchResult:
        api_key = settings.tmdb_api_key
        bearer = settings.tmdb_bearer
        if not api_key and not bearer:
            raise AppError(
                code="TMDB_NOT_CONFIGURED",
                message="TMDB credentials are not configured",
                retryable=False,
                status_code=500,
            )

        genre_map = self._get_genre_map(language=language)

        params: dict[str, str | int] = {
            "query": query,
            "page": page,
            "include_adult": str(include_adult).lower(),
            "language": language,
        }
        if api_key:
            params["api_key"] = api_key
        query_params = urlencode(params)
        base_url = settings.tmdb_base_url.rstrip("/")
        url = f"{base_url}/search/movie?{query_params}"
        payload = self._fetch_json(url)

        results = payload.get("results")
        if not isinstance(results, list):
            raise AppError(
                code="TMDB_INVALID_RESPONSE",
                message="TMDB returned an invalid payload",
                retryable=True,
                status_code=502,
            )

        items: list[TmdbMovie] = []
        for raw in results:
            movie_id = raw.get("id")
            title = raw.get("title")
            if not isinstance(movie_id, int) or not isinstance(title, str):
                continue
            raw_genre_ids = raw.get("genre_ids")
            genre_ids = []
            if isinstance(raw_genre_ids, list):
                genre_ids = [genre_id for genre_id in raw_genre_ids if isinstance(genre_id, int)]

            items.append(
                TmdbMovie(
                    id=movie_id,
                    title=title,
                    overview=raw.get("overview") if isinstance(raw.get("overview"), str) else "",
                    backdrop_path=raw.get("backdrop_path") if isinstance(raw.get("backdrop_path"), str) else None,
                    release_date=raw.get("release_date") if isinstance(raw.get("release_date"), str) else None,
                    vote_average=float(raw.get("vote_average") or 0),
                    vote_count=int(raw.get("vote_count") or 0),
                    popularity=float(raw.get("popularity") or 0),
                    adult=bool(raw.get("adult") is True),
                    original_language=raw.get("original_language")
                    if isinstance(raw.get("original_language"), str)
                    else None,
                    genre_ids=genre_ids,
                    genres=[genre_map[genre_id] for genre_id in genre_ids if genre_id in genre_map],
                )
            )

        return TmdbSearchResult(
            page=int(payload.get("page") or page),
            total_pages=int(payload.get("total_pages") or 0),
            total_results=int(payload.get("total_results") or 0),
            items=items,
        )

    def get_movie(self, movie_id: str, language: str = "en-US") -> TmdbMovie:
        api_key = settings.tmdb_api_key
        params: dict[str, str] = {"language": language}
        if api_key:
            params["api_key"] = api_key

        genre_map = self._get_genre_map(language=language)
        base_url = settings.tmdb_base_url.rstrip("/")
        url = f"{base_url}/movie/{movie_id}?{urlencode(params)}"
        payload = self._fetch_json(url)

        raw_id = payload.get("id")
        title = payload.get("title")
        if not isinstance(raw_id, int) or not isinstance(title, str):
            raise AppError(
                code="TMDB_INVALID_RESPONSE",
                message="TMDB returned an invalid movie payload",
                retryable=True,
                status_code=502,
            )

        genres_raw = payload.get("genres")
        genre_ids: list[int] = []
        genres: list[str] = []
        if isinstance(genres_raw, list):
            for entry in genres_raw:
                if not isinstance(entry, dict):
                    continue
                genre_id = entry.get("id")
                name = entry.get("name")
                if isinstance(genre_id, int):
                    genre_ids.append(genre_id)
                    if isinstance(name, str) and name:
                        genres.append(name)
                    elif genre_id in genre_map:
                        genres.append(genre_map[genre_id])

        return TmdbMovie(
            id=raw_id,
            title=title,
            overview=payload.get("overview") if isinstance(payload.get("overview"), str) else "",
            backdrop_path=payload.get("backdrop_path") if isinstance(payload.get("backdrop_path"), str) else None,
            release_date=payload.get("release_date") if isinstance(payload.get("release_date"), str) else None,
            vote_average=float(payload.get("vote_average") or 0),
            vote_count=int(payload.get("vote_count") or 0),
            popularity=float(payload.get("popularity") or 0),
            adult=bool(payload.get("adult") is True),
            original_language=payload.get("original_language")
            if isinstance(payload.get("original_language"), str)
            else None,
            genre_ids=genre_ids,
            genres=genres,
        )

    def _get_genre_map(self, language: str) -> dict[int, str]:
        now = datetime.now(timezone.utc)
        expires_at = self._genre_map_expires_at.get(language)
        if expires_at and expires_at > now:
            return self._genre_map_cache.get(language, {})

        api_key = settings.tmdb_api_key
        params: dict[str, str] = {"language": language}
        if api_key:
            params["api_key"] = api_key

        base_url = settings.tmdb_base_url.rstrip("/")
        url = f"{base_url}/genre/movie/list?{urlencode(params)}"

        try:
            payload = self._fetch_json(url)
            genres_raw = payload.get("genres")
            if not isinstance(genres_raw, list):
                return self._genre_map_cache.get(language, {})

            genre_map: dict[int, str] = {}
            for entry in genres_raw:
                genre_id = entry.get("id")
                name = entry.get("name")
                if isinstance(genre_id, int) and isinstance(name, str) and name:
                    genre_map[genre_id] = name

            self._genre_map_cache[language] = genre_map
            self._genre_map_expires_at[language] = now + timedelta(hours=24)
            return genre_map
        except AppError:
            return self._genre_map_cache.get(language, {})

    def _fetch_json(self, url: str) -> dict:
        bearer = settings.tmdb_bearer
        headers = {"Accept": "application/json"}
        if bearer:
            headers["Authorization"] = f"Bearer {bearer}"
        request = Request(url, headers=headers)

        try:
            with urlopen(request, timeout=settings.tmdb_timeout_seconds) as response:
                payload = json.loads(response.read().decode("utf-8"))
                if not isinstance(payload, dict):
                    raise AppError(
                        code="TMDB_INVALID_RESPONSE",
                        message="TMDB returned an invalid payload",
                        retryable=True,
                        status_code=502,
                    )
                return payload
        except HTTPError as exc:
            status = exc.code if isinstance(exc.code, int) else 502
            message = "TMDB request failed"
            if 400 <= status < 500:
                message = "TMDB request rejected"
            raise AppError(
                code="TMDB_REQUEST_FAILED",
                message=message,
                retryable=status >= 500,
                status_code=502 if status >= 500 else 400,
            ) from exc
        except URLError as exc:
            raise AppError(
                code="TMDB_UNAVAILABLE",
                message="TMDB is unavailable",
                retryable=True,
                status_code=503,
            ) from exc
        except (json.JSONDecodeError, UnicodeDecodeError) as exc:
            raise AppError(
                code="TMDB_INVALID_RESPONSE",
                message="TMDB returned an invalid response",
                retryable=True,
                status_code=502,
            ) from exc
