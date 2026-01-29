package main

import (
	"context"
	"log"
	"net/http"
	"time"

	"github.com/jackc/pgx/v5/pgxpool"

	"github.com/wilsonSev/calendar-management/services/gateway/internal/config"
	"github.com/wilsonSev/calendar-management/services/gateway/internal/google"
	"github.com/wilsonSev/calendar-management/services/gateway/internal/httpapi"
)


func main() {
	cfg := config.Load()

	ctx, cancel := context.WithTimeout(context.Background(), 5*time.Second)
	defer cancel()

	db, err := pgxpool.New(ctx, cfg.DbURL)
	if err != nil {
		log.Fatalf("db connect: %v", err)
	}
	defer db.Close()

	if err := db.Ping(ctx); err != nil {
		log.Fatalf("db ping: %v", err)
	}
	log.Println("DB ping OK")

	oauth := google.NewOAuth(cfg.GoogleClientID, cfg.GoogleClientSecret, cfg.GoogleRedirectURI, cfg.GoogleScopes)
	srv := httpapi.New(db, oauth, cfg.BotSecret)

	addr := ":" + cfg.Port
	log.Printf("listening on %s", addr)
	if err := http.ListenAndServe(addr, srv.Routes()); err != nil {
		log.Fatalf("http server: %v", err)
	}
}