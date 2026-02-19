package main

import (
	"log"
	"os"
	"strings"

	"github.com/wilsonSev/calendar-management/services/gateway/telegram-bot/bot"
)

func main() {
	token := strings.TrimSpace(os.Getenv("TELEGRAM_BOT_TOKEN"))
	if token == "" {
		log.Fatal("TELEGRAM_BOT_TOKEN must be set")
	}

	bot, err := bot.New(token)
	if err != nil {
		log.Fatal("failed to create bot:", err)
	}

	bot.Start()
}
