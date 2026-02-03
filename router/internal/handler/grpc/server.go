package grpc

import (
	"context"

	"calendar-management/router/v2/internal/domain"
	routerv0 "calendar-management/proto/router" 

	"google.golang.org/grpc"
)

// SchedulerService описывает методы бизнес-логики, необходимые хендлеру
type SchedulerService interface {
	CreateEvent(ctx context.Context, userID string, event domain.Event) (string, error)
	CreateTask(ctx context.Context, userID string, task domain.Task) (string, error)
}

// Handler реализует gRPC интерфейс SchedulerServer
type Handler struct {
	routerv0.UnimplementedSchedulerServer
	service SchedulerService
}

// New создает новый хендлер
func New(service SchedulerService) *Handler {
	return &Handler{
		service: service,
	}
}

// Register регистрирует хендлер на gRPC сервере
func Register(gRPC *grpc.Server, service SchedulerService) {
	routerv0.RegisterSchedulerServer(gRPC, New(service))
}
