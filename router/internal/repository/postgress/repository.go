package postgress

import (
	"context"
	"fmt"

	"github.com/jackc/pgx/v5"
)

type Repository struct {
	db *pgx.Conn
}

func NewStorage(ctx context.Context, dsn string) (*Repository, error) {
	db, err := pgx.Connect(ctx, dsn)
	if err != nil {
		return nil, fmt.Errorf("failed to connect to database: %w", err)
	}

	return &Repository{db: db}, nil
}

func (r *Repository) Close(ctx context.Context) error {
	return r.db.Close(ctx)
}

func (r *Repository) GetRefreshToken(ctx context.Context, userID string) (string, error) {
	var refreshToken string

	query := `
        SELECT refresh_token 
        FROM google_tokens 
        WHERE tg_user_id = $1
    `

	err := r.db.QueryRow(ctx, query, userID).Scan(&refreshToken)
	if err != nil {
		if err == pgx.ErrNoRows {
			return "", fmt.Errorf("refresh token not found for user %s", userID)
		}
		return "", fmt.Errorf("failed to get refresh token: %w", err)
	}

	return refreshToken, nil
}
