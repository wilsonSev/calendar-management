package main

import (
	"context"
	"log"
	"strings"
	"time"

	tgbotapi "github.com/go-telegram-bot-api/telegram-bot-api/v5"

	"bot/internal/config"
	"bot/internal/gateway"
)

func main() {
	cfg := config.Load()
	gw := gateway.New(cfg.GatewayBaseURL, cfg.BotSecret)

	bot, err := tgbotapi.NewBotAPI(cfg.TelegramToken)
	if err != nil {
		log.Fatalf("telegram init: %v", err)
	}
	log.Printf("bot authorized as @%s", bot.Self.UserName)

	u := tgbotapi.NewUpdate(0)
	u.Timeout = 30

	updates := bot.GetUpdatesChan(u)

	for upd := range updates {
		if upd.Message == nil {
			continue
		}
		if !upd.Message.IsCommand() {
			continue
		}

		chatID := upd.Message.Chat.ID
		tgUserID := int64(upd.Message.From.ID)

		cmd := upd.Message.Command()
		switch cmd {
		case "start":
			send(bot, chatID,
				"Привет! Я помогу подключить Google Calendar.\n\nКоманды:\n/connect — подключить Google\n/status — статус подключения\n/help — помощь")

		case "help":
			send(bot, chatID,
				"/connect — получить ссылку на подключение Google\n/status — проверить, подключен ли Google\n\nПосле подключения можно будет добавлять события текстом.")

		case "connect":
			ctx, cancel := context.WithTimeout(context.Background(), 10*time.Second)
			defer cancel()

			link, err := gw.AuthStart(ctx, tgUserID)
			if err != nil {
				send(bot, chatID, "Не смог получить ссылку на подключение. Проверь, что gateway запущен.")
				log.Printf("auth start error: %v", err)
				continue
			}

			msg := tgbotapi.NewMessage(chatID, "Нажми кнопку ниже, чтобы подключить Google:")
			msg.ReplyMarkup = tgbotapi.NewInlineKeyboardMarkup(
				tgbotapi.NewInlineKeyboardRow(
					tgbotapi.NewInlineKeyboardButtonURL("Connect Google", link),
				),
			)
			_, _ = bot.Send(msg)

			msg = tgbotapi.NewMessage(chatID, `Если кнопка не открылась, <a href="`+link+`">вот ссылка</a>.`)
			msg.ParseMode = "HTML"
			_, _ = bot.Send(msg)

		case "status":
			ctx, cancel := context.WithTimeout(context.Background(), 6*time.Second)
			defer cancel()

			ok, err := gw.Status(ctx, tgUserID)
			if err != nil {
				send(bot, chatID, "Не смог проверить статус. Проверь gateway.")
				log.Printf("status error: %v", err)
				continue
			}
			if ok {
				send(bot, chatID, "✅ Google подключен.")
			} else {
				send(bot, chatID, "❌ Google не подключен. Нажми /connect")
			}

		default:
			send(bot, chatID, "Не знаю эту команду. /help")
		}
	}
}

func send(bot *tgbotapi.BotAPI, chatID int64, text string) {
	text = strings.TrimSpace(text)
	msg := tgbotapi.NewMessage(chatID, text)
	_, _ = bot.Send(msg)
}
