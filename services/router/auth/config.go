package auth

import (
	"golang.org/x/oauth2"
	"golang.org/x/oauth2/google"
)

var googleOAuthConfig = &oauth2.Config{
	ClientID:     "YOUR_CLIENT_ID",
	ClientSecret: "YOUR_CLIENT_SECRET",
	RedirectURL:  "https://mydomain.com/oauth/google/callback",
	Scopes: []string{
		"https://www.googleapis.com/auth/calendar",
		"https://www.googleapis.com/auth/tasks",
	},
	Endpoint: google.Endpoint,
}
