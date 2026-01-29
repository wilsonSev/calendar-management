package config

import (
	"log"
	"os"
	"strings"

	"github.com/joho/godotenv"
)

type Config struct {
	Port string
	DbURL string

	GoogleClientID     string
	GoogleClientSecret string
	GoogleRedirectURI  string
	GoogleScopes       string

	BotSecret string
}

func envDefault(name, def string) string {
	v := strings.TrimSpace(os.Getenv(name))
	if v == "" {
		return def
	}
	return v
}

func mustEnv(name string) string {
	v := strings.TrimSpace(os.Getenv(name))
	if v == "" {
		log.Fatalf("environment variable %s must be set", name)
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
		Port: envDefault("PORT", "8080"),
		DbURL: mustEnv("DATABASE_URL"),

		GoogleClientID:     mustEnv("GOOGLE_CLIENT_ID"),
		GoogleClientSecret: mustEnv("GOOGLE_CLIENT_SECRET"),
		GoogleRedirectURI:  mustEnv("GOOGLE_REDIRECT_URI"),
		GoogleScopes:       envDefault("GOOGLE_SCOPES", "https://www.googleapis.com/auth/calendar https://www.googleapis.com/auth/tasks"),

		BotSecret: envDefault("BOT_SECRET", ""),
	}
}
