package bot

import (
	"log"

	tgbotapi "github.com/go-telegram-bot-api/telegram-bot-api/v5"
)

type Bot struct {
	api    *tgbotapi.BotAPI
	router *Router
}

func New(token string) (*Bot, error) {
	api, err := tgbotapi.NewBotAPI(token)
	if err != nil {
		return nil, err
	}
	bot := &Bot{
		api:    api,
		router: NewRouter(api),
	}
	return bot, nil
}

func (b *Bot) Start() {
	log.Printf("Authorized as %s", b.api.Self.UserName)

	u := tgbotapi.NewUpdate(0)
	u.Timeout = 30

	updates := b.api.GetUpdatesChan(u)
	for upd := range updates {
		b.router.Handle(upd)
	}
}
