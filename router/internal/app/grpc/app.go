package grpcapp

import (
	"fmt"
	"log/slog"
	"net"
	"time"

	"calendar-management/router/v2/internal/config"
	handler "calendar-management/router/v2/internal/handler/grpc"
	"calendar-management/router/v2/internal/repository"
	"calendar-management/router/v2/internal/service/clients"
	"calendar-management/router/v2/internal/service/scheduler"

	"google.golang.org/grpc"
)

type App struct {
	log        *slog.Logger
	gPRCServer *grpc.Server
	port       int
	ttl        time.Duration
}

func New(
	log *slog.Logger,
	port int,
	ttl time.Duration,
	googleCfg config.GoogleConfig,
	repo repository.Repository,
) *App {
	gRPCServer := grpc.NewServer()

	provider := clients.NewProvider(googleCfg.ClientID, googleCfg.ClientSecret, repo)

	schedulerService := scheduler.New(provider)

	handler.Register(gRPCServer, schedulerService)

	return &App{
		log:        log,
		gPRCServer: gRPCServer,
		port:       port,
		ttl:        ttl,
	}
}

func (a *App) MustRun() {
	if err := a.Run(); err != nil {
		panic(err)
	}
}

func (a *App) Run() error {
	const op = "grpcapp.Run"

	log := a.log.With(slog.String(op, "op"), slog.Int("port", a.port))

	lis, err := net.Listen("tcp", fmt.Sprintf(":%d", a.port))
	if err != nil {
		return fmt.Errorf("%s : %w", op, err)
	}

	log.Info("gRPC server is running", slog.String("address", lis.Addr().String()))

	if err := a.gPRCServer.Serve(lis); err != nil {
		return fmt.Errorf("%s : %w", op, err)
	}

	return nil
}

func (a *App) Stop() {
	const op = "grpcapp.Stop"

	a.log.With(slog.String(op, "op")).Info("stopping gRPC server", slog.Int("port", a.port))

	a.log.Info("gRPC server stopping")
	a.gPRCServer.GracefulStop()
	a.log.Info("gRPC server stopped")
}
