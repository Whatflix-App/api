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

## Run tests

```bash
uv run pytest
```

## Update lockfile

```bash
uv lock
```
