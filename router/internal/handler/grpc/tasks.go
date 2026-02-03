package grpc

import (
	"context"

	routerv0 "calendar-management/proto/router"
	"calendar-management/router/v2/internal/domain"

	"google.golang.org/grpc/codes"
	"google.golang.org/grpc/status"
)

func (h *Handler) CreateTask(ctx context.Context, req *routerv0.CreateTaskRequest) (*routerv0.CreateTaskResponse, error) {
	if req.GetTitle() == "" {
		// TODO: log
		return nil, status.Error(codes.InvalidArgument, ErrTitleRequired)
	}

	task := domain.Task{
		Title:       req.GetTitle(),
		Description: req.GetDescription(),
	}

	id, err := h.service.CreateTask(ctx, req.GetUserId(), task)
	if err != nil {
		// TODO: log
		return nil, status.Errorf(codes.Internal, ErrCreateTaskFailed, err)
	}

	return &routerv0.CreateTaskResponse{
		Success: true,
		Id:      id,
	}, nil
}
