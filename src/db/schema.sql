CREATE TABLE IF NOT EXISTS users (
  id VARCHAR(64) PRIMARY KEY,
  email VARCHAR(255) UNIQUE,
  display_name VARCHAR(120),
  full_name VARCHAR(120),
  apple_sub VARCHAR(255) UNIQUE NOT NULL,
  created_at TIMESTAMPTZ NOT NULL
);

ALTER TABLE users
  ADD COLUMN IF NOT EXISTS full_name VARCHAR(120);

CREATE TABLE IF NOT EXISTS sessions (
  id VARCHAR(64) PRIMARY KEY,
  user_id VARCHAR(64) NOT NULL REFERENCES users(id) ON DELETE CASCADE,
  refresh_token_hash VARCHAR(255) NOT NULL UNIQUE,
  device_id VARCHAR(255),
  device_platform VARCHAR(64),
  app_version VARCHAR(64),
  expires_at TIMESTAMPTZ NOT NULL,
  revoked_at TIMESTAMPTZ,
  created_at TIMESTAMPTZ NOT NULL
);

CREATE INDEX IF NOT EXISTS idx_sessions_user_id ON sessions(user_id);
CREATE INDEX IF NOT EXISTS idx_sessions_expires_at ON sessions(expires_at);

CREATE TABLE IF NOT EXISTS watchlist (
  user_id VARCHAR(64) NOT NULL REFERENCES users(id) ON DELETE CASCADE,
  movie_id VARCHAR(64) NOT NULL,
  added_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
  notes TEXT,
  priority SMALLINT,
  PRIMARY KEY (user_id, movie_id)
);

CREATE INDEX IF NOT EXISTS idx_watchlist_user_added_at
  ON watchlist(user_id, added_at DESC);

CREATE TABLE IF NOT EXISTS catalogs (
  id VARCHAR(64) PRIMARY KEY,
  owner_user_id VARCHAR(64) NOT NULL REFERENCES users(id) ON DELETE CASCADE,
  name VARCHAR(120) NOT NULL,
  description TEXT,
  is_public BOOLEAN NOT NULL DEFAULT FALSE,
  created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
  updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS catalog_items (
  catalog_id VARCHAR(64) NOT NULL REFERENCES catalogs(id) ON DELETE CASCADE,
  movie_id VARCHAR(64) NOT NULL,
  added_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
  added_by_user_id VARCHAR(64) REFERENCES users(id) ON DELETE SET NULL,
  PRIMARY KEY (catalog_id, movie_id)
);

CREATE INDEX IF NOT EXISTS idx_catalogs_owner ON catalogs(owner_user_id);
CREATE INDEX IF NOT EXISTS idx_catalog_items_catalog ON catalog_items(catalog_id);

CREATE TABLE IF NOT EXISTS history (
  id VARCHAR(64) PRIMARY KEY,
  user_id VARCHAR(64) REFERENCES users(id) ON DELETE SET NULL,
  scheme VARCHAR(64) NOT NULL,
  route VARCHAR(255) NOT NULL,
  method VARCHAR(10),
  source VARCHAR(32) NOT NULL DEFAULT 'manual',
  rationale TEXT,
  created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_history_user_created
  ON history(user_id, created_at DESC);
CREATE INDEX IF NOT EXISTS idx_history_scheme_route
  ON history(scheme, route);

CREATE TABLE IF NOT EXISTS watch_history (
  id VARCHAR(64) PRIMARY KEY,
  user_id VARCHAR(64) NOT NULL REFERENCES users(id) ON DELETE CASCADE,
  movie_id VARCHAR(64) NOT NULL,
  watched_at TIMESTAMPTZ NOT NULL,
  completed BOOLEAN NOT NULL DEFAULT FALSE,
  progress_pct SMALLINT NOT NULL DEFAULT 0,
  source VARCHAR(32) NOT NULL DEFAULT 'manual',
  created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_watch_history_user_watched
  ON watch_history(user_id, watched_at DESC, created_at DESC);
CREATE INDEX IF NOT EXISTS idx_watch_history_user_movie
  ON watch_history(user_id, movie_id);
