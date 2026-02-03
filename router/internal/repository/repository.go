package repository

import "context"

type Repository interface {
	Close(ctx context.Context) error
	GetRefreshToken(ctx context.Context, userID string) (string, error)
}
