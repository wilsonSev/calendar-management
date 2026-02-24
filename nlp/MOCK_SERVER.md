# 🎭 Mock Scheduler Server

Mock gRPC сервер, который притворяется настоящим Scheduler'ом для тестирования.

## Зачем это нужно?

Вместо того чтобы запускать настоящий Router (Go), ты можешь запустить mock server:
- Он принимает те же gRPC запросы
- Логирует все запросы в терминал
- Всегда возвращает success
- Не создает реальные события
- Идеально для тестирования твоего микросервиса

## Архитектура

### Обычная:
```
Твой микросервис → Router (Go:50051) → База данных
```

### С mock server:
```
Твой микросервис → Mock Server (Python:50051) → Логи в терминал
```

## Запуск

### Через VS Code (рекомендуется):

**Cmd + Shift + P** → **Tasks: Run Task** → **Run NLP Service**

Mock server запустится на порту **50051** (как настоящий Router).

### Вручную:

```bash
cd nlp
source venv/bin/activate
python mock_scheduler_server.py
```

## Тестирование

### Через VS Code:

**Cmd + Shift + P** → **Tasks: Run Task** → **Test Mock Scheduler**

### Вручную:

```bash
cd nlp
source venv/bin/activate

# Отправить тестовые запросы
python test_mock_scheduler.py

# Непрерывное тестирование (каждые 2 секунды)
python test_mock_scheduler.py --continuous
```

## Что увидишь

### В терминале mock server:

```
======================================================================
🎭 Mock Scheduler gRPC Server
======================================================================
Port: 50051
Status: Running
======================================================================

This is a MOCK server - it doesn't create real events!
It just logs requests and returns success.

Waiting for requests from your microservice...
Press Ctrl+C to stop and see statistics


======================================================================
📅 CreateEvent Request Received
======================================================================
Event ID: mock_event_1
Title: Встреча с командой
Description: Обсуждение проекта
User ID: user_123
Participants: None
Start: 2026-02-25 16:00:00
End: 2026-02-25 17:00:00
Duration: 1:00:00
======================================================================

✓ Event stored (total events: 1)
```

### В терминале клиента:

```
======================================================================
Testing Mock Scheduler Server
======================================================================

📤 Sending event 1/3: Встреча с командой
✓ Response: success=True, id=mock_event_1

📤 Sending event 2/3: Созвон с клиентом
✓ Response: success=True, id=mock_event_2

📤 Sending event 3/3: Обед
✓ Response: success=True, id=mock_event_3

======================================================================
✓ All events sent!
======================================================================
```

## Использование с твоим микросервисом

Твой микросервис должен подключаться к `localhost:50051` (как обычно).

Mock server будет:
1. Принимать все запросы
2. Логировать их в терминал
3. Возвращать success с mock ID

### Пример (Go):

```go
// Подключение к mock server (тот же код, что и для настоящего)
conn, err := grpc.Dial("localhost:50051", grpc.WithInsecure())
client := routerv0.NewSchedulerClient(conn)

// Отправка запроса
resp, err := client.CreateEvent(ctx, &routerv0.CreateEventRequest{
    Title:       "Test Event",
    Description: "Testing mock server",
    UserId:      "test_user",
    // ...
})

// Получишь: success=true, id="mock_event_1"
```

### Пример (Python):

```python
from scheduler_client import SchedulerClient

with SchedulerClient() as client:
    success, event_id = client.create_event(
        title="Test Event",
        description="Testing",
        user_id="test_user",
        start_time=datetime.now(),
        end_time=datetime.now() + timedelta(hours=1)
    )
    
    print(f"Success: {success}")  # True
    print(f"ID: {event_id}")      # mock_event_1
```

## Статистика

При остановке (Ctrl+C) mock server покажет статистику:

```
🛑 Shutting down...

======================================================================
📊 Mock Scheduler Statistics
======================================================================
Total Events: 15
Total Tasks: 3
======================================================================

Last 5 events:
  - mock_event_11: Встреча (user: user_123)
  - mock_event_12: Созвон (user: user_456)
  - mock_event_13: Обед (user: user_789)
  - mock_event_14: Test Event #1 (user: test_user_1)
  - mock_event_15: Test Event #2 (user: test_user_2)

Last 5 tasks:
  - mock_task_1: Написать документацию (user: user_123)
  - mock_task_2: Code review (user: user_456)
  - mock_task_3: Тестирование (user: user_789)
```

## Режимы тестирования

### 1. Одиночный тест (по умолчанию)

```bash
python test_mock_scheduler.py
```

Отправит:
- 3 события
- 2 задачи
- Покажет результаты

### 2. Непрерывный тест

```bash
python test_mock_scheduler.py --continuous
```

Отправляет запросы каждые 2 секунды до Ctrl+C.
Полезно для:
- Стресс-тестирования
- Проверки стабильности
- Демонстрации

## Переключение между mock и настоящим Router

### Использовать mock server:

```bash
# Запусти mock server на 50051
python mock_scheduler_server.py
```

### Использовать настоящий Router:

```bash
# Запусти Router на 50051
cd router
go run cmd/router/main.go
```

Твой микросервис не заметит разницы - оба на порту 50051!

## Преимущества mock server

✅ Не нужна база данных
✅ Не нужен настоящий Router (Go)
✅ Быстрый запуск
✅ Подробные логи
✅ Всегда возвращает success
✅ Идеально для разработки и тестирования
✅ Можно видеть все запросы в реальном времени

## Когда использовать

### Mock server:
- Разработка нового функционала
- Тестирование интеграции
- Отладка запросов
- Демонстрация
- CI/CD тесты

### Настоящий Router:
- Production
- Интеграционные тесты с базой
- Проверка реальной логики

## Troubleshooting

### Порт занят

```bash
# Найди процесс на 50051
lsof -i :50051

# Убей процесс
kill -9 <PID>
```

### Клиент не подключается

```bash
# Проверь что mock server запущен
lsof -i :50051

# Проверь логи в терминале mock server
```

## Файлы

- `mock_scheduler_server.py` - Mock gRPC сервер
- `test_mock_scheduler.py` - Тестовый клиент
- `scheduler_client.py` - Клиент (работает с обоими)

## Готово! 🎉

Теперь ты можешь тестировать свой микросервис без запуска настоящего Router!

Запускай mock server и смотри все запросы в реальном времени.
