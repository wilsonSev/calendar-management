package main

import (
	"log"

	"github.com/wilsonSev/calendar-management/services/gateway/config"
	"github.com/wilsonSev/calendar-management/services/gateway/telegram-bot/bot"
)

func main() {
	config := config.Config{}
	bot, err := bot.New(config.Token)
	if err != nil {
		log.Fatal("failed to create bot:", err)
	}

	bot.Start()
}
