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
	panic("not implemented")
}
