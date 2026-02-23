package config

import (
	"log"
	"os"
	"strings"

	"github.com/joho/godotenv"
)

type Config struct {
	TelegramToken string
	GatewayBaseURL string
	BotSecret string
	AnalyzerTarget string
	RouterTarget string
}

func mustEnv(name string) string {
	v := strings.TrimSpace(os.Getenv(name))
	if v == "" {
		log.Fatalf("env %s must be set", name)
	}
	return v
}

func Load() Config {
	if p := strings.TrimSpace(os.Getenv("ENV_FILE")); p != "" {
		if err := godotenv.Load(p); err != nil {
			log.Fatalf("failed to load env file %s: %v", p, err)
		}
	} else {
		_ = godotenv.Load()
	}

	return Config{
		TelegramToken:  mustEnv("TELEGRAM_BOT_TOKEN"),
		GatewayBaseURL: mustEnv("GATEWAY_BASE_URL"),
		BotSecret:      mustEnv("BOT_SECRET"),
		AnalyzerTarget: os.Getenv("ANALYZER_TARGET"),
		RouterTarget:   "localhost:50051",
	}
}