// апи слой который взаимодействует с БД посредством sql запросов
package store

import (
	"context"
	"time"

	"github.com/jackc/pgx/v5/pgxpool"
)

type Store struct {
	db *pgxpool.Pool
}

func New(db *pgxpool.Pool) *Store {
	return &Store{db: db}
}

func (s *Store) EnsureUser(ctx context.Context, tgUserID int64) error {
	_, err := s.db.Exec(ctx, `
		INSERT INTO users (tg_user_id)
		VALUES ($1)
		ON CONFLICT (tg_user_id) DO NOTHING`,
		tgUserID)
	return err
}

func (s *Store) SaveState(ctx context.Context, state string, tgUserID int64, expiresAt time.Time) error{
	_, err := s.db.Exec(ctx, `
	    INSERT INTO oauth_state (state, tg_user_id, expires_at)
		VALUES ($1, $2, $3)
	`, state, tgUserID, expiresAt)
	return err
}

func (s *Store) ConsumeState(ctx context.Context, state string) (tgUserID int64, ok bool, err error) {
	err = s.db.QueryRow(ctx, `
		DELETE FROM oauth_state
		WHERE state = $1 and expires_at > now()
		RETURNING tg_user_id
	`, state).Scan(&tgUserID)

	if err != nil {
		return 0, false, nil
	}
	return tgUserID, true, nil
}

type GoogleTokens struct {
	AccessToken       string
	RefreshToken      string
	AccessExpiresAt   time.Time
	Scope             string
}

func (s *Store) UpsertTokens(ctx context.Context, tgUserID int64, t GoogleTokens) error {
	_, err := s.db.Exec(ctx, `
		INSERT INTO google_tokens (tg_user_id, refresh_token, access_token, access_expires_at, scope)
		VALUES ($1, $2, $3, $4, $5)
		ON CONFLICT (tg_user_id) DO UPDATE SET
			access_token = EXCLUDED.access_token,
			access_expires_at = EXCLUDED.access_expires_at,
			updated_at = now(),
			scope = EXCLUDED.scope,
			refresh_token = coalesce(nullif(EXCLUDED.refresh_token, ''), google_tokens.refresh_token)
	`, tgUserID, t.RefreshToken, t.AccessToken, t.AccessExpiresAt, t.Scope)
	return err
}

func (s *Store) IsConnected(ctx context.Context, tgUserID int64) (bool, error) {
	var exists bool
	err := s.db.QueryRow(ctx, `
		SELECT exists(
			SELECT 1 FROM google_tokens
			WHERE tg_user_id = $1 AND length(refresh_token) > 0
		)
	`, tgUserID).Scan(&exists)
	return exists, err
}