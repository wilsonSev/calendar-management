package google

import (
	"context"
	"encoding/json"
	"errors"
	"net/http"
	"net/url"
	"strings"
	"time"
)

type OAuth struct {
	ClientID     string
	ClientSecret string
	RedirectURI  string
	Scopes       []string
}

func NewOAuth(clientID, clientSecret, redirectURI, scopes string) *OAuth {
	parts := strings.Fields(scopes)
	return &OAuth{
		ClientID:     clientID,
		ClientSecret: clientSecret,
		RedirectURI:  redirectURI,
		Scopes:       parts,
	}
}

func (o *OAuth) BuildAuthURL(state string) string {
	u, _ := url.Parse("https://accounts.google.com/o/oauth2/v2/auth")
	q := u.Query()
	q.Set("client_id", o.ClientID)
	q.Set("redirect_uri", o.RedirectURI)
	q.Set("response_type", "code")
	q.Set("scope", strings.Join(o.Scopes, " "))
	q.Set("state", state)
	q.Set("include_granted_scopes", "true")
	q.Set("access_type", "offline")
	q.Set("prompt", "consent")
	u.RawQuery = q.Encode()
	return u.String()
}

type TokenResponse struct {
	AccessToken  string `json:"access_token"`
	ExpiresIn    int64  `json:"expires_in"`
	RefreshToken string `json:"refresh_token"`
	Scope        string `json:"scope"`
	TokenType    string `json:"token_type"`
}

func (o *OAuth) ExchangeCode(ctx context.Context, code string) (TokenResponse, error) {
	form := url.Values{}
	form.Set("client_id", o.ClientID)
	form.Set("client_secret", o.ClientSecret)
	form.Set("redirect_uri", o.RedirectURI)
	form.Set("grant_type", "authorization_code")
	form.Set("code", code)

	req, _ := http.NewRequestWithContext(ctx, http.MethodPost, "https://oauth2.googleapis.com/token", strings.NewReader(form.Encode()))
	req.Header.Set("Content-Type", "application/x-www-form-urlencoded")

	resp, err := http.DefaultClient.Do(req)
	if err != nil {
		return TokenResponse{}, err
	}
	defer resp.Body.Close()

	if resp.StatusCode < 200 || resp.StatusCode >= 300 {
		return TokenResponse{}, errors.New("google token exchange failed: " + resp.Status)
	}

	var tr TokenResponse
	if err := json.NewDecoder(resp.Body).Decode(&tr); err != nil {
		return TokenResponse{}, err
	}
	return tr, nil
}

func ExpiresAt(expiresInSec int64) time.Time {
	return time.Now().Add(time.Duration(expiresInSec-30) * time.Second)
}
