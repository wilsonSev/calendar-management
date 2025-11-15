package main

import (
	"log"
	"os"

	tgbotapi "github.com/go-telegram-bot-api/telegram-bot-api/v5"
	"github.com/joho/godotenv"
)

var greetingMassage string = "Привет! Добро пожаловать в твой собственный менеджер Google Calendar!"

func main() {
	err := godotenv.Load()
	if err != nil {
		log.Printf("Error loading .env file")
	}
	bot, err := tgbotapi.NewBotAPI(os.Getenv("TELEGRAM_BOT_TOKEN"))
	if err != nil {
		panic(err)
	}
	bot.Debug = true

	u := tgbotapi.NewUpdate(0)
	u.Timeout = 30

	updates := bot.GetUpdatesChan(u)

	for upd := range updates {
		if upd.Message == nil {
			continue
		}

		if upd.Message.IsCommand() {
			switch upd.Message.Command() {
			case "start":
				_, _ = bot.Send(tgbotapi.NewMessage(upd.Message.Chat.ID, greetingMassage))
			default:
				_, _ = bot.Send(tgbotapi.NewMessage(upd.Message.Chat.ID, "Неизвестная команда"))
			}
			continue
		}

		if upd.Message.Text != "" {
			user := upd.Message.From
			log.Printf("from @%s (%d): %s", user.UserName, upd.Message.Chat.ID, upd.Message.Text)

			msg := tgbotapi.NewMessage(upd.Message.Chat.ID, "Вы написали: "+upd.Message.Text)
			msg.ReplyToMessageID = upd.Message.MessageID
			if _, err := bot.Send(msg); err != nil {
				log.Printf("send failed: %v", err)
			}
		}
	}

}
