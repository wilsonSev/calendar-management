# 🧪 Testing Guide

Полное руководство по тестированию NLP сервиса и интеграции с микросервисами.

## Быстрый старт

### 1. Запуск Mock Server

**Cmd + Shift + P** → **Tasks: Run Task** → **Run NLP Service**

Или:
```bash
cd nlp
source venv/bin/activate
python mock_scheduler_server.py
```

Mock server запустится на порту **50051** (как настоящий Router).

### 2. Отправка тестовых запросов

**Cmd + Shift + P** → **Tasks: Run Task** → **Test Mock Scheduler**

Или:
```bash
cd nlp
source venv/bin/activate
python test_mock_scheduler.py
```

## Что тестируется

### Mock Scheduler Server

✅ Принимает gRPC запросы CreateEvent
✅ Принимает gRPC запросы CreateTask
✅ Логирует все запросы в терминал
✅ Возвращает success с mock ID
✅ Собирает статистику

### Test Client

✅ Отправляет 3 тестовых события
✅ Отправляет 2 тестовые задачи
✅ Проверяет ответы
✅ Показывает результаты

## Сценарии тестирования

### Сценарий 1: Базовое тестирование

```bash
# Терминал 1: Запусти mock server
python mock_scheduler_server.py

# Терминал 2: Отправь тесты
python test_mock_scheduler.py
```

**Ожидаемый результат:**
- Mock server логирует 5 запросов (3 события + 2 задачи)
- Клиент получает success для всех запросов
- Все ID начинаются с "mock_"

### Сценарий 2: Непрерывное тестирование

```bash
# Терминал 1: Mock server
python mock_scheduler_server.py

# Терминал 2: Непрерывные запросы
python test_mock_scheduler.py --continuous
```

**Ожидаемый результат:**
- Запросы отправляются каждые 2 секунды
- Mock server логирует каждый запрос
- Счетчик событий растет

### Сценарий 3: Тестирование твоего микросервиса

```bash
# Терминал 1: Mock server
python mock_scheduler_server.py

# Терминал 2: Твой микросервис
cd ../router
go run cmd/router/main.go
# или
cd ../services/bot
go run cmd/bot/main.go
```

**Ожидаемый результат:**
- Твой микросервис отправляет запросы в mock server
- Mock server логирует все запросы
- Ты видишь что именно отправляет твой микросервис

## Проверка результатов

### В терминале Mock Server:

```
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

### В терминале Test Client:

```
📤 Sending event 1/3: Встреча с командой
✓ Response: success=True, id=mock_event_1
```

### Статистика при остановке:

```
📊 Mock Scheduler Statistics
======================================================================
Total Events: 15
Total Tasks: 3
```

## Интеграция с твоим кодом

### Python:

```python
from scheduler_client import SchedulerClient

# Подключится к localhost:50051 (mock server)
with SchedulerClient() as client:
    success, event_id = client.create_event(
        title="Test",
        description="Testing",
        user_id="test",
        start_time=datetime.now(),
        end_time=datetime.now() + timedelta(hours=1)
    )
    
    print(f"Success: {success}")  # True
    print(f"ID: {event_id}")      # mock_event_1
```

### Go:

```go
conn, _ := grpc.Dial("localhost:50051", grpc.WithInsecure())
client := routerv0.NewSchedulerClient(conn)

resp, _ := client.CreateEvent(ctx, &routerv0.CreateEventRequest{
    Title:       "Test",
    Description: "Testing",
    UserId:      "test",
    // ...
})

fmt.Println(resp.Success) // true
fmt.Println(resp.Id)      // mock_event_1
```

## Переключение между mock и production

### Mock (для тестирования):

```bash
# Запусти mock server на 50051
python mock_scheduler_server.py
```

### Production (настоящий Router):

```bash
# Запусти Router на 50051
cd router
go run cmd/router/main.go
```

Твой код не меняется - оба на порту 50051!

## Отладка

### Проверка что mock server запущен:

```bash
lsof -i :50051
```

Должен увидеть Python процесс.

### Проверка запросов:

Все запросы логируются в терминал mock server в реальном времени.

### Проверка ответов:

Mock server всегда возвращает:
- `success = true`
- `id = "mock_event_N"` или `"mock_task_N"`

## Автоматизация

### Скрипт для CI/CD:

```bash
#!/bin/bash

# Запуск mock server в фоне
cd nlp
source venv/bin/activate
python mock_scheduler_server.py &
MOCK_PID=$!

# Ждем запуска
sleep 2

# Запуск тестов
python test_mock_scheduler.py

# Результат
TEST_RESULT=$?

# Остановка mock server
kill $MOCK_PID

exit $TEST_RESULT
```

## Метрики

Mock server собирает:
- Количество событий
- Количество задач
- Последние 5 событий
- Последние 5 задач

Статистика показывается при остановке (Ctrl+C).

## Troubleshooting

### Mock server не запускается

```bash
# Проверь что порт свободен
lsof -i :50051

# Убей процесс если занят
kill -9 <PID>
```

### Клиент не подключается

```bash
# Проверь что mock server запущен
lsof -i :50051

# Проверь логи mock server
```

### Запросы не приходят

```bash
# Проверь что клиент подключается к правильному порту
# В .env должно быть:
SCHEDULER_PORT=50051
```

## Полезные команды

```bash
# Запуск mock server
python mock_scheduler_server.py

# Одиночный тест
python test_mock_scheduler.py

# Непрерывный тест
python test_mock_scheduler.py --continuous

# Проверка порта
lsof -i :50051

# Проверка конфигурации
python test_config.py
```

## Следующие шаги

1. ✅ Запусти mock server
2. ✅ Отправь тестовые запросы
3. ✅ Проверь логи
4. ⚠️ Интегрируй с твоим микросервисом
5. ⚠️ Запусти твой микросервис с mock server
6. ⚠️ Проверь что запросы корректные
7. ⚠️ Переключись на настоящий Router

## Готово! 🎉

Теперь ты можешь тестировать интеграцию без запуска настоящего Router!
