package scheduler

import (
	"context"
	"fmt"
	"time"

	"calendar-management/router/v2/internal/domain"
	"calendar-management/router/v2/internal/service/clients"

	"google.golang.org/api/calendar/v3"
	"google.golang.org/api/tasks/v1"
)

type Scheduler struct {
	provider *clients.Provider
}

func New(provider *clients.Provider) *Scheduler {
	return &Scheduler{
		provider: provider,
	}
}

func (s *Scheduler) CreateEvent(ctx context.Context, userID string, event domain.Event) (string, error) {
	calService, _, err := s.provider.GetClients(ctx, userID)
	if err != nil {
		// TODO: log
		return "", fmt.Errorf("failed to get google clients: %w", err)
	}

	googleEvent := &calendar.Event{
		Summary:     event.Title,
		Description: event.Description,
		Attendees:   make([]*calendar.EventAttendee, 0, len(event.Participants)),
	}

	for _, email := range event.Participants {
		googleEvent.Attendees = append(googleEvent.Attendees, &calendar.EventAttendee{Email: email})
	}

	if event.IsFullDay {
		googleEvent.Start = &calendar.EventDateTime{
			Date: event.Start.Format("2006-01-02"),
		}
		googleEvent.End = &calendar.EventDateTime{
			Date: event.End.Format("2006-01-02"),
		}
	} else {
		googleEvent.Start = &calendar.EventDateTime{
			DateTime: event.Start.Format(time.RFC3339),
		}
		googleEvent.End = &calendar.EventDateTime{
			DateTime: event.End.Format(time.RFC3339),
		}
	}

	createdEvent, err := calService.Events.Insert("primary", googleEvent).Do()
	if err != nil {
		// TODO: log
		return "", fmt.Errorf("failed to insert event into calendar: %w", err)
	}

	return createdEvent.Id, nil
}

func (s *Scheduler) CreateTask(ctx context.Context, userID string, task domain.Task) (string, error) {
	_, tasksService, err := s.provider.GetClients(ctx, userID)
	if err != nil {
		// TODO: log
		return "", fmt.Errorf("failed to get google clients: %w", err)
	}

	googleTask := &tasks.Task{
		Title: task.Title,
		Notes: task.Description,
	}

	createdTask, err := tasksService.Tasks.Insert("@default", googleTask).Do()
	if err != nil {
		// TODO: log
		return "", fmt.Errorf("failed to insert task: %w", err)
	}

	return createdTask.Id, nil
}
