package domain

import (
	"time"
)

type Event struct {
	Title        string
	Description  string
	Start        time.Time
	End          time.Time
	IsFullDay    bool
	Participants []string
}

func NewEvent(title string, start, end time.Time, opts ...EventOption) *Event {
	event := &Event{
		Title:        title,
		Description:  "",
		Start:        start,
		End:          end,
		IsFullDay:    false,
		Participants: make([]string, 0),
	}

	for _, opt := range opts {
		opt(event)
	}

	return event
}

type EventOption func(*Event)

func WithParticipants(part []string) EventOption {
	return func(event *Event) {
		event.Participants = part
	}
}

func WithFullDay() EventOption {
	return func(event *Event) {
		event.IsFullDay = true
	}
}

func WithDescriptionEvent(desc string) EventOption {
	return func(event *Event) {
		event.Description = desc
	}
}
