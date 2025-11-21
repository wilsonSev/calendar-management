package config

import (
	"github.com/joho/godotenv"
	"log"
	"os"
)

type Config struct {
	Token string
}

func MustLoad() Config {
	err := godotenv.Load()
	if err != nil {
		log.Printf("Error loading .env file")
	}
	token := os.Getenv("TELEGRAM_BOT_TOKEN")
	if token == "" {
		log.Fatal("TELEGRAM_BOT_TOKEN environment variable not set")
	}
	return Config{token}
}
