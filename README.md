# calendar-management

## Quick start (local)

1. Fill env files:
`cp .env.example .env`
`cp services/bot/.env.example services/bot/.env`

2. Set real values:
- `.env`: `GOOGLE_CLIENT_ID`, `GOOGLE_CLIENT_SECRET`, `BOT_SECRET`
- `services/bot/.env`: `TELEGRAM_BOT_TOKEN`, same `BOT_SECRET` as in `.env`

3. Start stack:
`./scripts/local-up.sh`

The script does:
- `docker compose up -d postgres`
- runs SQL migrations from `supabase/migrations`
- starts `gateway` (`services/gateway/cmd/server`) and `bot` (`services/bot/cmd/bot`)

Stop with `Ctrl+C` (postgres container keeps running). To stop DB:
`docker compose down`

## One-button control (no Docker)

Use one script to manage all required app services (`gateway` + `bot`):

- Start: `./scripts/stack.sh start`
- Stop: `./scripts/stack.sh stop`
- Restart: `./scripts/stack.sh restart`
- Status: `./scripts/stack.sh status`
- Logs: `./scripts/stack.sh logs`

Notes:
- `start` and `restart` run DB migrations automatically.
- This mode is convenient when DB is remote (for example Supabase).

## Manual run

- Gateway:
`ENV_FILE=.env go run ./services/gateway/cmd/server/main.go`
- Bot:
`ENV_FILE=services/bot/.env go run ./services/bot/cmd/bot/main.go`
- Migrations only:
`ENV_FILE=.env go run ./services/gateway/cmd/migrate`

## Router service

Router module is in `router/` and can be started from repo root:
`go run ./router/cmd/router -config router/config/local.yaml`

Update `router/config/local.yaml` with valid Google credentials before production usage.
