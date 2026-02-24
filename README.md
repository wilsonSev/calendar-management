# calendar-management

## 🚀 Quick Start with VS Code (Recommended)

### Запуск сервисов для тестирования:

1. **Cmd + Shift + P** → **Tasks: Run Task**
2. Запусти:
   - **Run NLP Service** (Mock Scheduler на порту 50051)
   - **Test Mock Scheduler** (отправит тестовые запросы)

### Запуск всех сервисов (production):

1. **Cmd + Shift + P** → **Tasks: Run Task**
2. Запусти по порядку:
   - **Run Router** (настоящий Scheduler, порт 50051)
   - **Run Gateway** (порт 8081)
   - **Run Bot** (Telegram бот)

📖 Подробнее: [VSCODE_TASKS.md](VSCODE_TASKS.md)

## Mock Server для тестирования

Python mock gRPC сервер, который притворяется Scheduler'ом:
- Принимает запросы от твоего микросервиса
- Логирует все в терминал
- Всегда возвращает success
- Не нужна база данных

```bash
# Запуск mock server
cd nlp && source venv/bin/activate && python mock_scheduler_server.py

# Тестирование
python test_mock_scheduler.py
```

📖 Документация: [nlp/MOCK_SERVER.md](nlp/MOCK_SERVER.md)

## Services Overview

| Service | Port | Description |
|---------|------|-------------|
| Router | 50051 | gRPC service for event management |
| Gateway | 8081 | HTTP API Gateway |
| NLP Service | - | Python service for text parsing via LLM |
| Bot | - | Telegram bot |

## Python NLP Service

Python сервис для обработки текстовых сообщений и взаимодействия с Router через gRPC.

### Setup:
```bash
cd nlp
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
bash generate_proto.sh
```

### Configuration:
Добавь в `.env`:
```
openrouter=your_api_key_here
SCHEDULER_HOST=localhost
SCHEDULER_PORT=50051
```

📖 Документация: [nlp/README.md](nlp/README.md)

---

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
