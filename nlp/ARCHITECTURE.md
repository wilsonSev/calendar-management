# Архитектура NLP Service

## Общая схема

```
┌─────────────┐
│   User      │
│  Message    │
└──────┬──────┘
       │
       ▼
┌─────────────────────────────────────────┐
│         Python NLP Service              │
│                                         │
│  ┌──────────────────────────────────┐  │
│  │  main.py                         │  │
│  │  process_user_message()          │  │
│  └────────┬─────────────────────────┘  │
│           │                             │
│           ▼                             │
│  ┌──────────────────────────────────┐  │
│  │  openrouter.py                   │  │
│  │  parse_message() → Event         │  │
│  │  (LLM парсинг)                   │  │
│  └────────┬─────────────────────────┘  │
│           │                             │
│           ▼                             │
│  ┌──────────────────────────────────┐  │
│  │  scheduler_client.py             │  │
│  │  SchedulerClient                 │  │
│  │  - create_event()                │  │
│  │  - create_task()                 │  │
│  └────────┬─────────────────────────┘  │
│           │                             │
└───────────┼─────────────────────────────┘
            │ gRPC/Protobuf
            │ (router.proto)
            ▼
┌─────────────────────────────────────────┐
│      Go Scheduler Service               │
│                                         │
│  - CreateEvent(CreateEventRequest)      │
│  - CreateTask(CreateTaskRequest)        │
│                                         │
│  → Google Calendar API                  │
│  → Database                             │
└─────────────────────────────────────────┘
```

## Компоненты

### 1. main.py
**Назначение:** Основная точка входа, оркестрация процесса

**Функции:**
- `process_user_message(message, user_id, username)` - обработка сообщения пользователя

**Поток:**
1. Получает текстовое сообщение
2. Парсит через OpenRouter LLM
3. Отправляет в Scheduler через gRPC
4. Возвращает результат

### 2. scheduler_client.py
**Назначение:** gRPC клиент для Scheduler сервиса

**Класс:** `SchedulerClient`

**Методы:**
- `connect()` - установка соединения
- `close()` - закрытие соединения
- `create_event(...)` - создание события
- `create_task(...)` - создание задачи

**Особенности:**
- Context manager support (`with` statement)
- Автоматическая конвертация datetime → protobuf Timestamp
- Обработка gRPC ошибок

### 3. openrouter.py
**Назначение:** Интеграция с OpenRouter LLM

**Функции:**
- `parse_message(message, add_info)` - парсинг текста в Event

**Процесс:**
1. Формирует промпт для LLM
2. Отправляет запрос в OpenRouter API
3. Парсит JSON ответ
4. Возвращает объект Event

### 4. config.py
**Назначение:** Централизованная конфигурация

**Переменные:**
- `SCHEDULER_HOST` - хост Scheduler сервиса
- `SCHEDULER_PORT` - порт Scheduler сервиса
- `OPENROUTER_API_KEY` - API ключ для LLM

### 5. event.py
**Назначение:** Модели данных

**Классы:**
- `Event` - dataclass для событий
  - `name: str`
  - `start_time: datetime`
  - `finish_time: datetime`

### 6. lib/router/proto/router/
**Назначение:** Сгенерированные protobuf файлы

**Файлы:**
- `router_pb2.py` - protobuf messages
- `router_pb2_grpc.py` - gRPC stubs
- `router_pb2.pyi` - type hints

**Сообщения:**
- `CreateEventRequest`
- `CreateEventResponse`
- `CreateTaskRequest`
- `CreateTaskResponse`
- `DateTimeRange`

## Протокол взаимодействия

### gRPC Service: Scheduler

```protobuf
service Scheduler {
  rpc CreateEvent(CreateEventRequest) returns (CreateEventResponse);
  rpc CreateTask(CreateTaskRequest) returns (CreateTaskResponse);
}
```

### CreateEvent Request

```python
request = CreateEventRequest(
    title="Meeting",
    description="Team sync",
    user_id="123",
    participants=["user@example.com"],
    datetime=DateTimeRange(
        start_datetime=Timestamp(...),
        end_datetime=Timestamp(...)
    )
)
```

### CreateEvent Response

```python
response = CreateEventResponse(
    success=True,
    id="event_abc123"
)
```

## Поток данных

### Сценарий 1: Создание события из текста

```
1. User: "Встреча завтра в 15:00"
   ↓
2. main.process_user_message()
   ↓
3. openrouter.parse_message()
   → OpenRouter API
   ← Event(name="Встреча", start_time=..., end_time=...)
   ↓
4. scheduler_client.create_event()
   → gRPC: CreateEventRequest
   ← gRPC: CreateEventResponse(success=True, id="...")
   ↓
5. Return: (True, "event_id")
```

### Сценарий 2: Прямое создание события

```
1. Code: SchedulerClient().create_event(...)
   ↓
2. Convert datetime → Timestamp
   ↓
3. Build CreateEventRequest
   ↓
4. gRPC call → Scheduler Service
   ↓
5. Return: (success, event_id)
```

## Обработка ошибок

### gRPC ошибки

```python
try:
    response = stub.CreateEvent(request)
except grpc.RpcError as e:
    print(f"gRPC error: {e.code()} - {e.details()}")
    # UNAVAILABLE, DEADLINE_EXCEEDED, etc.
```

### OpenRouter ошибки

```python
if response.status_code != 200:
    raise Exception(f"OpenRouter API error: {response.text}")
```

## Конфигурация

### Environment Variables

```bash
# .env
openrouter=sk-or-v1-...
SCHEDULER_HOST=localhost
SCHEDULER_PORT=50052
```

### Defaults

```python
# config.py
SCHEDULER_HOST = getenv("SCHEDULER_HOST", "localhost")
SCHEDULER_PORT = getenv("SCHEDULER_PORT", "50052")
```

## Зависимости

### Python Packages

```
grpcio==1.60.0          # gRPC framework
grpcio-tools==1.60.0    # Proto compiler
protobuf==4.25.1        # Protobuf runtime
python-dotenv==1.0.0    # .env support
requests==2.31.0        # HTTP client
```

### External Services

- **OpenRouter API** - LLM для парсинга текста
- **Scheduler Service (Go)** - gRPC сервис для управления событиями

## Расширение

### Добавление нового gRPC метода

1. Обнови `proto/router/proto/router/router.proto`
2. Перегенерируй: `bash generate_proto.sh`
3. Добавь метод в `SchedulerClient`:

```python
def new_method(self, ...):
    request = router_pb2.NewRequest(...)
    response = self.stub.NewMethod(request)
    return response
```

### Добавление нового сервиса

1. Создай новый proto файл
2. Обнови `generate_proto.sh`
3. Создай новый клиент (аналог `scheduler_client.py`)

## Мониторинг

### Health Check

```python
# check_services.py
grpc.channel_ready_future(channel).result(timeout=5)
```

### Logging

Добавь логирование:

```python
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

logger.info(f"Creating event: {title}")
logger.error(f"gRPC error: {e}")
```

## Безопасность

### API Keys

- Храни в `.env`, не коммить в git
- Используй `.env.example` для шаблона

### gRPC

- Текущая версия: `insecure_channel`
- Для production: используй TLS/SSL

```python
credentials = grpc.ssl_channel_credentials()
channel = grpc.secure_channel(address, credentials)
```

## Performance

### Connection Pooling

```python
# Переиспользуй соединение
client = SchedulerClient()
client.connect()

for event in events:
    client.create_event(...)

client.close()
```

### Async Support

Для высокой нагрузки рассмотри `grpcio-async`:

```python
import grpc.aio

async def create_event_async(...):
    async with grpc.aio.insecure_channel(address) as channel:
        stub = router_pb2_grpc.SchedulerStub(channel)
        response = await stub.CreateEvent(request)
```

## Тестирование

### Unit Tests

```python
# test_scheduler_client.py
import unittest
from unittest.mock import Mock, patch

class TestSchedulerClient(unittest.TestCase):
    @patch('grpc.insecure_channel')
    def test_create_event(self, mock_channel):
        # Mock gRPC response
        ...
```

### Integration Tests

```python
# test_connection.py
def test_create_event():
    with SchedulerClient() as client:
        success, event_id = client.create_event(...)
        assert success
        assert event_id
```

## Deployment

### Docker

```dockerfile
FROM python:3.9-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .
CMD ["python", "main.py"]
```

### Environment

```bash
# Production
SCHEDULER_HOST=scheduler.prod.example.com
SCHEDULER_PORT=443
```
