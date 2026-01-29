CREATE TABLE IF NOT EXISTS users (
    tg_user_id BIGINT PRIMARY KEY,
    timezone TEXT NOT NULL DEFAULT 'Europe/Moscow',
    default_calendar_id TEXT NOT NULL DEFAULT 'primary',
    created_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE TABLE IF NOT EXISTS oauth_state (
    state TEXT PRIMARY KEY,
    tg_user_id BIGINT NOT NULL REFERENCES users(tg_user_id) ON DELETE CASCADE,
    expires_at TIMESTAMPTZ NOT NULL,
    created_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE index IF NOT EXISTS idx_oauth_state_expires_at ON oauth_state (expires_at);

CREATE TABLE IF NOT EXISTS google_tokens (
    tg_user_id BIGINT PRIMARY KEY REFERENCES users(tg_user_id) ON DELETE CASCADE,
    refresh_token TEXT NOT NULL,
    access_token TEXT,
    access_expires_at TIMESTAMPTZ,
    scope TEXT,
    updated_at TIMESTAMPTZ NOT NULL DEFAULT now()
);