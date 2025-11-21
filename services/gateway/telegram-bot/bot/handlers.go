package bot

import (
	"fmt"
	"log"
	"strconv"

	tgbotapi "github.com/go-telegram-bot-api/telegram-bot-api/v5"
)

var authLink string = `https://accounts.google.com/o/oauth2/v2/auth
  ?client_id=465451993798-v9dv5s1lo0099oedh6pc0k4hma201a1d.apps.googleusercontent.com
  &redirect_uri=https://mydomain.com/oauth/google/callback
  &response_type=code
  &scope=https%3A%2F%2Fwww.googleapis.com%2Fauth%2Fcalendar%20https%3A%2F%2Fwww.googleapis.com%2Fauth%2Ftasks
  &access_type=offline
  &prompt=consent
  &state=`

type Handlers struct {
	api *tgbotapi.BotAPI
}

func NewHandlers(api *tgbotapi.BotAPI) *Handlers {
	return &Handlers{api: api}
}

func (h *Handlers) Start(msg *tgbotapi.Message) {
	log.Println("Hey")
	var fullAuthLink string = authLink + strconv.FormatInt(msg.From.ID, 10)
	var greetingMessage string = fmt.Sprintf("Привет! Добро пожаловать в твой собственный менеджер Google Calendar! \n"+
		"Для авторизации перейдите по [ссылке](%s)", fullAuthLink)
	resp := tgbotapi.NewMessage(msg.Chat.ID, greetingMessage)
	resp.ParseMode = "Markdown"
	m, err := h.api.Send(resp)
	log.Println(m)
	if err != nil {
		log.Println(err)
	}
}

func (h *Handlers) Unknown(msg *tgbotapi.Message) {
	resp := tgbotapi.NewMessage(msg.Chat.ID, "Я не знаю такую команду 🤔")
	h.api.Send(resp)
}
