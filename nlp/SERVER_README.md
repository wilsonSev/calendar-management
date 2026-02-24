# 🚀 Analyzer gRPC Server - Готов к запуску!

## Что это?

Python gRPC сервер, который:
1. Принимает текстовые сообщения от Bot
2. Парсит их через OpenRouter LLM
3. Создает события в Scheduler (Go)
4. Возвращает результат Bot'у

## Быстрый старт

### 1. Запуск через VS Code (рекомендуется):

**Cmd + Shift + P** → **Tasks: Run Task** → Запусти по порядку:

1. **Run Router** (порт 50051) - обязательно первым!
2. **Run NLP Service** (порт 50053) - Analyzer server

### 2. Тестирование:

**Cmd + Shift + P** → **Tasks: Run Task** → **Test Analyzer Service**

Или вручную:
```bash
cd nlp
source venv/bin/activate
python test_analyzer_client.py
```

## Что увидишь

### При запуске сервера:

```
✓ Connected to Scheduler service

============================================================
Analyzer gRPC Server started on port 50053
============================================================

Waiting for requests...
Press Ctrl+C to stop
```

### При получении запроса:

```
============================================================
Received request from user 123456
Text: Встреча завтра в 15:00
Timezone: Europe/Moscow
============================================================

→ Parsing text with OpenRouter LLM...
→ Calling OpenRouter API...
← Response status: 200
✓ Parsed event: Встреча
  Start: 2026-02-25 15:00:00
  End: 2026-02-25 17:00:00

→ Creating event in Scheduler...
✓ Event created successfully! ID: evt_abc123
```

## Тестовый клиент

Запусти `test_analyzer_client.py` - он отправит 3 тестовых запроса:

1. "Встреча с командой завтра в 15:00, продлится 2 часа"
2. "Созвон в понедельник в 10 утра"
3. "Обед сегодня в 13:00"

Для каждого увидишь:
- Запрос
- Ответ от сервера
- Созданное событие

## Интеграция с Bot

Bot должен подключаться к `localhost:50053`:

```go
// В bot/internal/analyzer/client.go
conn, err := grpc.Dial("localhost:50053", grpc.WithInsecure())
client := analyzerv1.NewAnalyzerServiceClient(conn)

resp, err := client.AnalyzeText(ctx, &analyzerv1.AnalyzeTextRequest{
    TgUserId: userID,
    Text:     message,
    Timezone: "Europe/Moscow",
    ChatId:   chatID,
})
```

## Порты

| Сервис | Порт | Описание |
|--------|------|----------|
| Router | 50051 | Go gRPC (Scheduler) |
| Analyzer | 50053 | Python gRPC (NLP) |
| Gateway | 8081 | HTTP API |

## Файлы

- `analyzer_server.py` - gRPC сервер
- `test_analyzer_client.py` - тестовый клиент
- `lib/analyzer/v1/` - сгенерированные proto файлы

## Troubleshooting

### Сервер не запускается

```bash
# Проверь что Router запущен
lsof -i :50051

# Проверь что порт 50053 свободен
lsof -i :50053

# Проверь конфигурацию
python test_config.py
```

### Тест не работает

```bash
# Убедись что сервер запущен
lsof -i :50053

# Проверь логи сервера в терминале
```

## Готово! 🎉

Всё настроено и готово к использованию:

1. ✅ gRPC сервер создан
2. ✅ Тестовый клиент готов
3. ✅ VS Code tasks настроены
4. ✅ Документация написана

Запускай и тестируй!
