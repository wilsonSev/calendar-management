package grpc

const (
	ErrTitleRequired     = "title is required"
	ErrTimeRangeRequired = "time range (date or datetime) is required"
	ErrDateRangeRequired = "start_date and end_date are required for DateRange"
	ErrDateTimeRequired  = "start_datetime and end_datetime are required for DateTimeRange"
	ErrUnknownTimeFormat = "unknown time format"
	ErrCreateEventFailed = "failed to create event: %v"
	ErrCreateTaskFailed  = "failed to create task: %v"
)
