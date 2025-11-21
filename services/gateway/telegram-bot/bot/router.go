package bot

import tgbotapi "github.com/go-telegram-bot-api/telegram-bot-api/v5"

type Router struct {
	handlers *Handlers
}

func NewRouter(api *tgbotapi.BotAPI) *Router {
	return &Router{NewHandlers(api)}
}

func (r *Router) Handle(update tgbotapi.Update) {
	if update.Message != nil {
		r.handleMessage(update)
	}
}

func (r *Router) handleMessage(update tgbotapi.Update) {
	msg := update.Message

	switch msg.Text {
	case "/start":
		r.handlers.Start(msg)
	default:
		r.handlers.Unknown(msg)
	}
}
