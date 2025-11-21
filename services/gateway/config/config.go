package config

import (
	"log"
	"os"

	"github.com/joho/godotenv"
)

type Config struct {
	Token string
}

func MustLoad() Config {
	err := godotenv.Load()
	if err != nil {
		log.Printf("Error loading .env file: " + err.Error())
	}
	token := os.Getenv("TELEGRAM_BOT_TOKEN")
	if token == "" {
		log.Fatal("TELEGRAM_BOT_TOKEN environment variable not set")
	}
	return Config{token}
}
