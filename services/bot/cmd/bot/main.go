package main

import (
	"context"
	"fmt"
	"log"
	"strings"
	"time"

	"bot/internal/analyzer"
	"bot/internal/config"
	"bot/internal/gateway"
	"sync"

	router_pb "calendar-management/proto/router"

	pb "github.com/andrepribavkin/calendar-management/proto/analyzer/v1"
	tgbotapi "github.com/go-telegram-bot-api/telegram-bot-api/v5"
	"google.golang.org/grpc"
	"google.golang.org/grpc/credentials/insecure"
	"google.golang.org/protobuf/types/known/timestamppb"
)

// Simple in-memory storage for user states
var (
	userStates = make(map[int64]*pb.CreateEvent)
	stateMu    sync.Mutex
)

func main() {
	cfg := config.Load()
	gw := gateway.New(cfg.GatewayBaseURL, cfg.BotSecret)

	var anlz *analyzer.Client
	if cfg.AnalyzerTarget != "" {
		var err error
		anlz, err = analyzer.New(cfg.AnalyzerTarget)
		if err != nil {
			log.Printf("warning: analyzer init failed: %v", err)
		} else {
			defer anlz.Close()
			log.Printf("analyzer connected at %s", cfg.AnalyzerTarget)
		}
	}

	// Connect to router
	routerConn, err := grpc.NewClient(cfg.RouterTarget, grpc.WithTransportCredentials(insecure.NewCredentials()))
	if err != nil {
		log.Printf("warning: router connect failed: %v", err)
	}
	routerClient := router_pb.NewSchedulerClient(routerConn)

	bot, err := tgbotapi.NewBotAPI(cfg.TelegramToken)
	if err != nil {
		log.Fatalf("telegram init: %v", err)
	}
	log.Printf("bot authorized as @%s", bot.Self.UserName)

	u := tgbotapi.NewUpdate(0)
	u.Timeout = 30

	updates := bot.GetUpdatesChan(u)

	for upd := range updates {
		if upd.CallbackQuery != nil {
			handleCallback(bot, routerClient, upd.CallbackQuery)
			continue
		}

		if upd.Message == nil {
			continue
		}
		if !upd.Message.IsCommand() {
			if anlz != nil {
				handleText(bot, anlz, upd.Message)
			} else {
				log.Printf("text message ignored (analyzer not configured): %s", upd.Message.Text)
			}
			continue
		}

		chatID := upd.Message.Chat.ID
		tgUserID := int64(upd.Message.From.ID)

		cmd := upd.Message.Command()
		switch cmd {
		case "start":
			send(bot, chatID,
				"Привет! Я помогу подключить Google Calendar.\n\nКоманды:\n/connect — подключить Google\n/status — статус подключения\n/test_add — тест создания события\n/help — помощь")

		case "help":
			send(bot, chatID,
				"/connect — получить ссылку на подключение Google\n/status — проверить, подключен ли Google\n/test_add — создать тестовое событие (завтра в 10:00)\n\nПосле подключения можно будет добавлять события текстом.")

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

		case "test_add":
			start := time.Now().Add(24 * time.Hour)
			end := start.Add(1 * time.Hour)

			req := &router_pb.CreateEventRequest{
				Title:       "Test Event from Bot",
				Description: "Created via /test_add bypassing NLP",
				UserId:      fmt.Sprintf("%d", tgUserID),
				Time: &router_pb.CreateEventRequest_Datetime{
					Datetime: &router_pb.DateTimeRange{
						StartDatetime: timestamppb.New(start),
						EndDatetime:   timestamppb.New(end),
					},
				},
			}

			ctx, cancel := context.WithTimeout(context.Background(), 5*time.Second)
			resp, err := routerClient.CreateEvent(ctx, req)
			cancel()

			if err != nil {
				send(bot, chatID, "❌ Ошибка router: "+err.Error())
				log.Printf("CreateEvent error: %v", err)
			} else {
				send(bot, chatID, fmt.Sprintf("✅ Событие создано! ID: %s, Success: %v", resp.Id, resp.Success))
			}

		default:
			send(bot, chatID, "Не знаю эту команду. /help")
		}
	}
}

func handleText(bot *tgbotapi.BotAPI, anlz *analyzer.Client, msg *tgbotapi.Message) {
	send(bot, msg.Chat.ID, "⏳ Анализирую...")

	resp, err := anlz.Analyze(context.Background(), int64(msg.From.ID), msg.Text)
	if err != nil {
		log.Printf("analyze error: %v", err)
		send(bot, msg.Chat.ID, "Ошибка анализа: "+err.Error())
		return
	}

	switch r := resp.Result.(type) {
	case *pb.AnalyzeTextResponse_CreateEvent:
		evt := r.CreateEvent
		start := evt.StartTime.AsTime()
		end := evt.EndTime.AsTime()

		// Save state for user
		stateMu.Lock()
		userStates[msg.From.ID] = evt
		stateMu.Unlock()

		txt := fmt.Sprintf("📅 Создать событие?\n\nНазвание: %s\nОписание: %s\nВремя: %s - %s",
			evt.Title, evt.Description,
			start.Format(time.RFC822),
			end.Format(time.RFC822))

		msgResp := tgbotapi.NewMessage(msg.Chat.ID, txt)
		msgResp.ReplyMarkup = tgbotapi.NewInlineKeyboardMarkup(
			tgbotapi.NewInlineKeyboardRow(
				tgbotapi.NewInlineKeyboardButtonData("✅ Да", "confirm_event"),
				tgbotapi.NewInlineKeyboardButtonData("❌ Нет", "cancel_event"),
			),
		)
		_, _ = bot.Send(msgResp)

	case *pb.AnalyzeTextResponse_NeedClarification:
		send(bot, msg.Chat.ID, "❓ "+r.NeedClarification.Question)

	case *pb.AnalyzeTextResponse_Error:
		send(bot, msg.Chat.ID, "❌ "+r.Error.Message)

	default:
		send(bot, msg.Chat.ID, "Непонятный ответ от сервера")
	}
}

func handleCallback(bot *tgbotapi.BotAPI, routerClient router_pb.SchedulerClient, cb *tgbotapi.CallbackQuery) {
	defer func() {
		// Answer callback to stop loading animation
		bot.Request(tgbotapi.NewCallback(cb.ID, ""))
	}()

	userID := cb.From.ID

	if cb.Data == "cancel_event" {
		stateMu.Lock()
		delete(userStates, userID)
		stateMu.Unlock()

		edit := tgbotapi.NewEditMessageText(cb.Message.Chat.ID, cb.Message.MessageID, "❌ Отменено.")
		bot.Send(edit)
		return
	}

	if cb.Data == "confirm_event" {
		stateMu.Lock()
		evt, ok := userStates[userID]
		delete(userStates, userID) // Clear state immediately
		stateMu.Unlock()

		if !ok {
			send(bot, cb.Message.Chat.ID, "Срок действия истёк или событие уже обработано.")
			return
		}

		req := &router_pb.CreateEventRequest{
			Title:       evt.Title,
			Description: evt.Description,
			UserId:      fmt.Sprintf("%d", userID),
			Time: &router_pb.CreateEventRequest_Datetime{
				Datetime: &router_pb.DateTimeRange{
					StartDatetime: evt.StartTime, // Already timestamppb
					EndDatetime:   evt.EndTime,
				},
			},
		}

		ctx, cancel := context.WithTimeout(context.Background(), 10*time.Second)
		resp, err := routerClient.CreateEvent(ctx, req)
		cancel()

		if err != nil {
			log.Printf("CreateEvent error: %v", err)
			send(bot, cb.Message.Chat.ID, "❌ Ошибка при создании: "+err.Error())
		} else {
			text := fmt.Sprintf("✅ Событие создано! (ID: %s)", resp.Id)
			edit := tgbotapi.NewEditMessageText(cb.Message.Chat.ID, cb.Message.MessageID, text)
			bot.Send(edit)
		}
	}
}

func send(bot *tgbotapi.BotAPI, chatID int64, text string) {
	text = strings.TrimSpace(text)
	msg := tgbotapi.NewMessage(chatID, text)
	_, _ = bot.Send(msg)
}
