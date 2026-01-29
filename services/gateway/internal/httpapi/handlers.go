package httpapi

import (
	"context"
	"crypto/rand"
	"encoding/base64"
	"encoding/json"
	"log"
	"net/http"
	"time"

	"github.com/jackc/pgx/v5/pgxpool"

	"github.com/wilsonSev/calendar-management/services/gateway/internal/google"
	"github.com/wilsonSev/calendar-management/services/gateway/internal/store"
)


type Server struct {
	Store     *store.Store
	OAuth     *google.OAuth
	BotSecret string
}

func New(db *pgxpool.Pool, oauth *google.OAuth, botSecret string) *Server {
	return &Server{
		Store:     store.New(db),
		OAuth:     oauth,
		BotSecret: botSecret,
	}
}

func (s *Server) Routes() http.Handler {
	mux := http.NewServeMux()
	mux.HandleFunc("/healthz", s.healthz)
	mux.HandleFunc("/google/auth/start", s.authStart)
	mux.HandleFunc("/google/callback", s.callback)
	return mux
}

func (s *Server) checkBotSecret(w http.ResponseWriter, r *http.Request) bool {
	if s.BotSecret == "" {
		return true
	}
	if r.Header.Get("X-Bot-Secret") != s.BotSecret {
		http.Error(w, "unauthorized", http.StatusUnauthorized)
		return false
	}
	return true
}

func (s *Server) healthz(w http.ResponseWriter, r *http.Request) {
	w.WriteHeader(http.StatusOK)
	w.Write([]byte("ok"))
}

type authStartReq struct {
	TgUserID int64 `json:"tg_user_id"`
}

type authStartResp struct {
	URL string `json:"url"`
}

func randomState(n int) (string, error) {
	b := make([]byte, n)
	if _, err := rand.Read(b); err != nil {
		return "", err
	}
	return base64.RawURLEncoding.EncodeToString(b), nil
}

func (s *Server) authStart(w http.ResponseWriter, r *http.Request) {
	if r.Method != http.MethodPost {
		http.Error(w, "method not allowed", http.StatusMethodNotAllowed)
		return
	}
	if !s.checkBotSecret(w, r) {
		return
	}

	var req authStartReq
	if err := json.NewDecoder(r.Body).Decode(&req); err != nil || req.TgUserID == 0 {
		http.Error(w, "bad request", http.StatusBadRequest)
		return
	}

	ctx, cancel := context.WithTimeout(r.Context(), 5*time.Second)
	defer cancel()

	if err := s.Store.EnsureUser(ctx, req.TgUserID); err != nil {
		http.Error(w, "db error", http.StatusInternalServerError)
		return
	}

	state, err := randomState(32)
	if err != nil {
		http.Error(w, "state gen error", http.StatusInternalServerError)
		return
	}

	if err := s.Store.SaveState(ctx, state, req.TgUserID, time.Now().Add(10*time.Minute)); err != nil {
		http.Error(w, "db error", http.StatusInternalServerError)
		return
	}

	url := s.OAuth.BuildAuthURL(state)

	w.Header().Set("Content-Type", "application/json")
	json.NewEncoder(w).Encode(authStartResp{URL: url})
}

func (s *Server) callback(w http.ResponseWriter, r *http.Request) {
	q := r.URL.Query()
	code := q.Get("code")
	state := q.Get("state")
	if code == "" || state == "" {
		http.Error(w, "missing code/state", http.StatusBadRequest)
		return
	}

	ctx, cancel := context.WithTimeout(r.Context(), 10*time.Second)
	defer cancel()

	tgUserID, ok, err := s.Store.ConsumeState(ctx, state)
	if err != nil {
		http.Error(w, "db error", http.StatusInternalServerError)
		return
	}
	if !ok {
		http.Error(w, "invalid/expired state", http.StatusBadRequest)
		return
	}

	tr, err := s.OAuth.ExchangeCode(ctx, code)
	if err != nil {
		log.Printf("exchange code error: %v", err)
		http.Error(w, "token exchange failed", http.StatusBadGateway)
		return
	}

	tokens := store.GoogleTokens{
		AccessToken:     tr.AccessToken,
		RefreshToken:    tr.RefreshToken,
		AccessExpiresAt: google.ExpiresAt(tr.ExpiresIn),
		Scope:           tr.Scope,
	}

	if err := s.Store.UpsertTokens(ctx, tgUserID, tokens); err != nil {
		http.Error(w, "db error", http.StatusInternalServerError)
		return
	}

	w.WriteHeader(http.StatusOK)
	w.Write([]byte("Google connected успешно. Можно закрыть эту страницу."))
}