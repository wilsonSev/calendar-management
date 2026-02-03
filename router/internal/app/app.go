package app

import (
	routerrpc "calendar-management/router/v2/internal/app/grpc"
	"calendar-management/router/v2/internal/config"
	"calendar-management/router/v2/internal/repository/postgress"
	"context"

	"log/slog"
	"time"
)

type App struct {
	GRPCSrv *routerrpc.App
}

func New(
	ctx context.Context,
	log *slog.Logger,
	grpcPort int,
	dsn string,
	storageTimeout time.Duration,
	tokenTTL time.Duration,
	googleCfg config.GoogleConfig,
) *App {
	initCtx, cancel := context.WithTimeout(ctx, storageTimeout)
	defer cancel()

	repo, err := postgress.NewStorage(initCtx, dsn)
	if err != nil {
		panic("failed to init storage: " + err.Error())
	}

	grpcApp := routerrpc.New(log, grpcPort, tokenTTL, googleCfg, repo)

	return &App{
		GRPCSrv: grpcApp,
	}
}
