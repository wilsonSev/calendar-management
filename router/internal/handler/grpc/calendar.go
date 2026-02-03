package grpc

import (
	"context"

	routerv0 "calendar-management/proto/router"
	"calendar-management/router/v2/internal/domain"

	"google.golang.org/grpc/codes"
	"google.golang.org/grpc/status"
)

func (h *Handler) CreateEvent(ctx context.Context, req *routerv0.CreateEventRequest) (*routerv0.CreateEventResponse, error) {
	if req.GetTitle() == "" {
		// TODO: log
		return nil, status.Error(codes.InvalidArgument, ErrTitleRequired)
	}

	if req.Time == nil {
		// TODO: log
		return nil, status.Error(codes.InvalidArgument, ErrTimeRangeRequired)
	}

	domainEvent := domain.Event{
		Title:        req.GetTitle(),
		Description:  req.GetDescription(),
		Participants: req.GetParticipants(),
	}

	switch t := req.Time.(type) {
	case *routerv0.CreateEventRequest_Date:
		if t.Date.StartDate == nil || t.Date.EndDate == nil {
			return nil, status.Error(codes.InvalidArgument, ErrDateRangeRequired)
		}
		domainEvent.Start = t.Date.StartDate.AsTime()
		domainEvent.End = t.Date.EndDate.AsTime()
		domainEvent.IsFullDay = true

	case *routerv0.CreateEventRequest_Datetime:
		if t.Datetime.StartDatetime == nil || t.Datetime.EndDatetime == nil {
			// TODO: log
			return nil, status.Error(codes.InvalidArgument, ErrDateTimeRequired)
		}
		domainEvent.Start = t.Datetime.StartDatetime.AsTime()
		domainEvent.End = t.Datetime.EndDatetime.AsTime()
		domainEvent.IsFullDay = false

	default:
		// TODO: log
		return nil, status.Error(codes.InvalidArgument, ErrUnknownTimeFormat)
	}

	id, err := h.service.CreateEvent(ctx, req.GetUserId(), domainEvent)
	if err != nil {
		return nil, status.Errorf(codes.Internal, ErrCreateEventFailed, err)
	}

	return &routerv0.CreateEventResponse{
		Success: true,
		Id:      id,
	}, nil
}
