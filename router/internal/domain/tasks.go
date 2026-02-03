package domain

type Task struct {
	Title       string
	Description string
}

func NewTask(title string, opts ...TaskOption) *Task {
	task := &Task{
		Title:       title,
		Description: "",
	}

	for _, opt := range opts {
		opt(task)
	}

	return task
}

type TaskOption func(*Task)

func WithDescriptionTask(desc string) TaskOption {
	return func(event *Task) {
		event.Description = desc
	}
}
