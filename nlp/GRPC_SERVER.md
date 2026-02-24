# Analyzer gRPC Server

Python gRPC сервер, который принимает запросы на анализ текста и создает события в Scheduler.

## Архитектура

```
Bot/Client → Analyzer gRPC Server (Python) → OpenRouter LLM
                     ↓
              Scheduler gRPC (Go)
```

## Запуск

### Через VS Code Tasks (рекомендуется):

1. **Cmd + Shift + P** → **Tasks: Run Task**
2. Запусти по порядку:
   - **Run Router** (порт 50051)
   - **Run NLP Service** (порт 50053)

### Вручную:

```bash
cd nlp
source venv/bin/activate
python analyzer_server.py
```

Сервер запустится на порту **50053**.

## Тестирование

### Через VS Code Task:

**Cmd + Shift + P** → **Tasks: Run Task** → **Test Analyzer Service**

### Вручную:

```bash
cd nlp
source venv/bin/activate
python test_analyzer_client.py
```

## API

### AnalyzeText

Анализирует текст и создает событие.

**Request:**
```protobuf
message AnalyzeTextRequest {
  int64 tg_user_id = 1;
  string text = 2;
  string timezone = 3;
  int64 chat_id = 4;
}
```

**Response:**
```protobuf
message AnalyzeTextResponse {
  oneof result {
    CreateEvent create_event = 1;
    NeedClarification need_clarification = 2;
    Error error = 3;
  }
}
```

## Примеры

### Python клиент:

```python
import grpc
from lib.analyzer.v1 import analyzer_pb2, analyzer_pb2_grpc

channel = grpc.insecure_channel('localhost:50053')
stub = analyzer_pb2_grpc.AnalyzerServiceStub(channel)

request = analyzer_pb2.AnalyzeTextRequest(
    tg_user_id=123456,
    text="Встреча завтра в 15:00",
    timezone="Europe/Moscow",
    chat_id=123
)

response = stub.AnalyzeText(request)

if response.HasField('create_event'):
    event = response.create_event
    print(f"Event: {event.title}")
    print(f"Start: {event.start_time.ToDatetime()}")
```

### Go клиент:

```go
conn, _ := grpc.Dial("localhost:50053", grpc.WithInsecure())
client := analyzerv1.NewAnalyzerServiceClient(conn)

resp, _ := client.AnalyzeText(ctx, &analyzerv1.AnalyzeTextRequest{
    TgUserId: 123456,
    Text:     "Встреча завтра в 15:00",
    Timezone: "Europe/Moscow",
    ChatId:   123,
})
```

## Логи

Сервер выводит подробные логи:

```
==============================================================
Received request from user 123456
Text: Встреча завтра в 15:00
Timezone: Europe/Moscow
==============================================================

→ Parsing text with OpenRouter LLM...
→ Calling OpenRouter API (model: meta-llama/llama-3.3-70b-instruct:free)...
← Response status: 200
→ Parsing response...
✓ Parsed event: Встреча
  Start: 2026-02-25 15:00:00
  End: 2026-02-25 17:00:00

→ Creating event in Scheduler...
✓ Event created successfully! ID: evt_abc123
```

## Конфигурация

### Порт сервера:

По умолчанию: **50053**

Изменить в `analyzer_server.py`:
```python
serve(port=50053)  # Измени порт здесь
```

### Подключение к Scheduler:

Настраивается в `.env`:
```
SCHEDULER_HOST=localhost
SCHEDULER_PORT=50051
```

### OpenRouter API:

```
openrouter=sk-or-v1-...
```

## Troubleshooting

### Сервер не запускается

**Ошибка:** "port already in use"
```bash
lsof -i :50053
kill -9 <PID>
```

**Ошибка:** "Cannot connect to Scheduler"
- Убедись что Router запущен на порту 50051
- Проверь `.env`: `SCHEDULER_PORT=50051`

### Клиент не может подключиться

**Ошибка:** "failed to connect to all addresses"
- Убедись что Analyzer server запущен
- Проверь порт: `lsof -i :50053`

### OpenRouter ошибки

**Ошибка:** "OPENROUTER_API_KEY is not set"
- Добавь ключ в `.env`: `openrouter=sk-or-v1-...`

## Производительность

- **Concurrent requests:** 10 workers (ThreadPoolExecutor)
- **Timeout:** 30 секунд на OpenRouter API
- **Latency:** 5-15 секунд (зависит от OpenRouter)

## Мониторинг

### Проверка статуса:

```bash
# Проверить что сервер запущен
lsof -i :50053

# Проверить логи
# Смотри вывод в терминале где запущен сервер
```

### Метрики:

Сервер выводит:
- Количество запросов
- Время обработки
- Ошибки

## Интеграция с Bot

Bot должен отправлять запросы на `localhost:50053`:

```go
// В bot сервисе
analyzerClient := analyzerv1.NewAnalyzerServiceClient(conn)

resp, err := analyzerClient.AnalyzeText(ctx, &analyzerv1.AnalyzeTextRequest{
    TgUserId: update.Message.From.ID,
    Text:     update.Message.Text,
    Timezone: "Europe/Moscow",
    ChatId:   update.Message.Chat.ID,
})
```

## Следующие шаги

1. ✅ Запусти Router
2. ✅ Запусти Analyzer server
3. ✅ Протестируй через test_analyzer_client.py
4. ⚠️ Интегрируй с Bot
5. ⚠️ Добавь логирование в файл
6. ⚠️ Добавь метрики (Prometheus)
7. ⚠️ Добавь health check endpoint
