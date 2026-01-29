package main

import (
	"context"
	"log"
	"os"
	"strings"
	"time"
	"github.com/jackc/pgx/v5/pgxpool"
	"github.com/joho/godotenv"
)

type APIConfig struct {
	Port             string
	DbURL            string
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

func MustLoadAPI() APIConfig {
	if err := godotenv.Load("/Users/andrepribavkin/calendar-management/calendar-management/.env"); err != nil {
		log.Printf("error loading .env: %v", err)
	}

	return APIConfig{
		Port:  envDefault("PORT", "8080"),
		DbURL: mustEnv("DATABASE_URL"),
	}
}

func main() {
	config := MustLoadAPI()
	ctx, cancel := context.WithTimeout(context.Background(), 5*time.Second)
	defer cancel()

	db, err := pgxpool.New(ctx, config.DbURL)
	if err != nil {
		log.Fatalf("db connect: %v", err)
	}
	defer db.Close()
	
	if err := db.Ping(ctx); err != nil {
		log.Fatalf("db ping: %v", err)
	}
	log.Println("DB ping OK")

}
