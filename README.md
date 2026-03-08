# Whatflix Backend (`uv`)

This backend is managed with `uv`.

## Setup

```bash
uv sync
```

## Run API

```bash
uv run uvicorn src.index:app --reload --host 0.0.0.0 --port 8000
```

## Environment

Set these for movie search:

```bash
TMDB_API_KEY=your_tmdb_api_key
TMDB_BEARER=your_tmdb_v4_bearer_token
# optional
TMDB_BASE_URL=https://api.themoviedb.org/3
TMDB_TIMEOUT_SECONDS=5
```

## Movie Search Route

`GET /search/movies` (auth required)

Query params:
- `q` (string, required)
- `page` (int, default `1`)
- `includeAdult` (bool, default `false`)
- `language` (string, default `en-US`)

Response shape:

```json
{
  "provider": "tmdb",
  "page": 1,
  "totalPages": 100,
  "totalResults": 2000,
  "items": [
    {
      "movieId": "550",
      "title": "Fight Club",
      "overview": "An insomniac office worker...",
      "posterPath": "/path.jpg",
      "releaseDate": "1999-10-15",
      "voteAverage": 8.4,
      "voteCount": 29000,
      "popularity": 84.2,
      "adult": false,
      "originalLanguage": "en"
    }
  ]
}
```

## Run tests

```bash
uv run pytest
```

## Update lockfile

```bash
uv lock
```
