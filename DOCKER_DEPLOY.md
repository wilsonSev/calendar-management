# Docker deployment

## What is included

- `postgres` - PostgreSQL 16
- `gateway-migrate` - runs SQL migrations once on startup
- `router` - gRPC scheduler service
- `gateway` - HTTP gateway exposed on the host
- `nlp` - Python analyzer gRPC service
- `bot` - Telegram bot

## Required files

1. Create `.env` from `.env.example`

For Docker deployment the compose file reads values from the root `.env` file. At minimum set:

- `GOOGLE_CLIENT_ID`
- `GOOGLE_CLIENT_SECRET`
- `GOOGLE_REDIRECT_URI`
- `BOT_SECRET`
- `OPENROUTER_API_KEY`
- `TELEGRAM_BOT_TOKEN`

Recommended values:

- `PORT=8081`
- `GOOGLE_REDIRECT_URI=https://your-domain.example/google/callback`
- `GATEWAY_BASE_URL=http://gateway:8080` for the bot inside Docker
- `ANALYZER_TARGET=nlp:50052`
- `ROUTER_TARGET=router:50051`

Database options:

- Set `DATABASE_URL` to an external PostgreSQL/Supabase instance to minimize local dependencies.
- If `DATABASE_URL` is omitted, the stack falls back to the local `postgres` container.

## Start

```bash
cp .env.example .env
# edit .env and fill real secrets
docker compose up -d --build
```

On first start Compose will:

- start PostgreSQL
- run SQL migrations once via `gateway-migrate`
- start `router`, `gateway`, `nlp`, and `bot`
- wait for internal health checks before starting the bot

## Logs

```bash
docker compose logs -f gateway router nlp bot
```

## Status

```bash
docker compose ps
```

## Stop

```bash
docker compose down
```

## Notes

- `gateway` is the only service published publicly by default.
- `postgres` is bound to `127.0.0.1` on the server.
- `router`, `nlp`, and `postgres` stay inside the Docker network.
- OAuth redirect must point to the public URL of `gateway` on your server.
- The bot still calls gateway over the internal Docker network using `http://gateway:8080`.
- To rebuild a single service after code changes, run `docker compose up -d --build <service-name>`.