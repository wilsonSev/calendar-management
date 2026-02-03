package main

import (
	"calendar-management/router/v2/internal/app"
	"calendar-management/router/v2/internal/config"
	"context"
	"log/slog"
	"os"
	"os/signal"
	"syscall"
)

const (
	envLocal = "local"
	envProd  = "prod"
	envDev   = "dev"
)

func main() {
	cfg := config.MustLoad()

	log := setupLogger(cfg.Env)
	log.Info("starting router microservice",
		slog.Any("config", cfg),
	)

	ctx, cancel := signal.NotifyContext(context.Background(), syscall.SIGINT, syscall.SIGTERM)
	defer cancel()

	application := app.New(
		ctx,
		log,
		cfg.GRPC.Port,
		cfg.DatabaseURL,
		cfg.StorageTimeout,
		cfg.TokenTTL,
		cfg.Google,
	)

	go application.GRPCSrv.MustRun()

	<-ctx.Done()

	log.Info("stopping router microservice")
	application.GRPCSrv.Stop()
	log.Info("router microservice stopped")
}

func setupLogger(env string) *slog.Logger {
	var log *slog.Logger

	switch env {
	case envLocal:
		log = slog.New(
			slog.NewTextHandler(os.Stdout, &slog.HandlerOptions{Level: slog.LevelDebug}),
		)
	case envDev:
		log = slog.New(
			slog.NewJSONHandler(os.Stdout, &slog.HandlerOptions{Level: slog.LevelDebug}),
		)
	case envProd:
		log = slog.New(
			slog.NewJSONHandler(os.Stdout, &slog.HandlerOptions{Level: slog.LevelInfo}),
		)
	}

	return log
}
