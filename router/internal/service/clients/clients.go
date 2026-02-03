package clients

import (
	"calendar-management/router/v2/internal/repository"
	"context"
	"fmt"

	"golang.org/x/oauth2"
	"golang.org/x/oauth2/google"
	"google.golang.org/api/calendar/v3"
	"google.golang.org/api/option"
	"google.golang.org/api/tasks/v1"
)

type Provider struct {
	clientConfig *oauth2.Config
	tokenRepo    repository.Repository
}

func NewProvider(clientID, clientSecret string, repo repository.Repository) *Provider {
	return &Provider{
		clientConfig: &oauth2.Config{
			ClientID:     clientID,
			ClientSecret: clientSecret,
			Endpoint:     google.Endpoint,
		},
		tokenRepo: repo,
	}
}

func (p *Provider) GetClients(ctx context.Context, userID string) (*calendar.Service, *tasks.Service, error) {
	refreshToken, err := p.tokenRepo.GetRefreshToken(ctx, userID)
	if err != nil {
		return nil, nil, fmt.Errorf("failed to get token: %w", err)
	}

	token := &oauth2.Token{RefreshToken: refreshToken}
	tokenSource := p.clientConfig.TokenSource(ctx, token)

	calSvc, err := calendar.NewService(ctx, option.WithTokenSource(tokenSource))
	if err != nil {
		return nil, nil, err
	}

	tasksSvc, err := tasks.NewService(ctx, option.WithTokenSource(tokenSource))
	if err != nil {
		return nil, nil, err
	}

	return calSvc, tasksSvc, nil
}
