package gateway

import (
	"bytes"
	"context"
	"encoding/json"
	"errors"
	"net/http"
	"net/url"
	"time"
)

type Client struct {
	BaseURL string
	Secret  string
	http    *http.Client
}

func New(baseURL, secret string) *Client {
	return &Client{
		BaseURL: baseURL,
		Secret: secret,
		http: &http.Client{
			Timeout: 7 * time.Second,
		},
	}
}

type authStartReq struct {
	TgUserID int64 `json:"tg_user_id"`
}
type authStartResp struct {
	URL string `json:"url"`
}

func (c *Client) AuthStart(ctx context.Context, tgUserID int64) (string, error) {
	body, _ := json.Marshal(authStartReq{TgUserID: tgUserID})

	req, _ := http.NewRequestWithContext(ctx, http.MethodPost, c.BaseURL+"/google/auth/start", bytes.NewReader(body))
	req.Header.Set("Content-Type", "application/json")
	req.Header.Set("X-Bot-Secret", c.Secret)

	resp, err := c.http.Do(req)
	if err != nil {
		return "", err
	}
	defer resp.Body.Close()

	if resp.StatusCode != 200 {
		return "", errors.New("gateway auth/start failed: " + resp.Status)
	}

	var out authStartResp
	if err := json.NewDecoder(resp.Body).Decode(&out); err != nil {
		return "", err
	}
	if out.URL == "" {
		return "", errors.New("empty url from gateway")
	}
	return out.URL, nil
}

type statusResp struct {
	Connected bool `json:"connected"`
}

func (c *Client) Status(ctx context.Context, tgUserID int64) (bool, error) {
	u, _ := url.Parse(c.BaseURL + "/google/status")
	q := u.Query()
	q.Set("tg_user_id", toStr(tgUserID))
	u.RawQuery = q.Encode()

	req, _ := http.NewRequestWithContext(ctx, http.MethodGet, u.String(), nil)
	req.Header.Set("X-Bot-Secret", c.Secret)

	resp, err := c.http.Do(req)
	if err != nil {
		return false, err
	}
	defer resp.Body.Close()

	if resp.StatusCode != 200 {
		return false, errors.New("gateway status failed: " + resp.Status)
	}

	var out statusResp
	if err := json.NewDecoder(resp.Body).Decode(&out); err != nil {
		return false, err
	}
	return out.Connected, nil
}

func toStr(x int64) string {
	if x == 0 {
		return "0"
	}
	var buf [32]byte
	i := len(buf)
	for x > 0 {
		i--
		buf[i] = byte('0' + x%10)
		x /= 10
	}
	return string(buf[i:])
}