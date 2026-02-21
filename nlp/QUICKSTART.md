# Quick Start Guide

## Быстрая настройка

### 1. Установка зависимостей

```bash
cd nlp
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### 2. Настройка окружения

Создай файл `.env` в корне проекта (или используй существующий):

```bash
# В корне проекта (не в nlp/)
cp .env.example .env
```

Добавь в `.env`:
```
openrouter=your_api_key_here
SCHEDULER_HOST=localhost
SCHEDULER_PORT=50052
```

### 3. Генерация proto-файлов

```bash
bash generate_proto.sh
```

### 4. Тестирование

Проверь подключение к Scheduler сервису:

```bash
python test_connection.py
```

Запусти примеры:

```bash
python example.py
```

## Использование в коде

### Простой пример

```python
from scheduler_client import SchedulerClient
from datetime import datetime, timedelta

# Создание события
with SchedulerClient() as client:
    success, event_id = client.create_event(
        title="Встреча",
        description="Важная встреча",
        user_id="123",
        start_time=datetime.now() + timedelta(hours=1),
        end_time=datetime.now() + timedelta(hours=2)
    )
    print(f"Event ID: {event_id}")
```

### Интеграция с OpenRouter

```python
from main import process_user_message

# Обработка сообщения пользователя
success, event_id = process_user_message(
    user_message="Встреча завтра в 15:00",
    user_id="123456",
    username="Иван"
)
```

## Структура проекта

```
nlp/
├── main.py                 # Основная точка входа
├── scheduler_client.py     # gRPC клиент для Scheduler
├── openrouter.py          # Интеграция с LLM
├── config.py              # Конфигурация
├── event.py               # Модели событий
├── message.py             # Модели сообщений
├── example.py             # Примеры использования
├── test_connection.py     # Тест подключения
├── generate_proto.sh      # Скрипт генерации proto
├── requirements.txt       # Зависимости
└── lib/                   # Сгенерированные proto-файлы
    └── router/
        └── proto/
            └── router/
                ├── router_pb2.py
                └── router_pb2_grpc.py
```

## Troubleshooting

### Ошибка подключения к gRPC

```
grpc._channel._InactiveRpcError: <_InactiveRpcError ...>
```

**Решение:**
1. Убедись, что Scheduler сервис запущен
2. Проверь `SCHEDULER_HOST` и `SCHEDULER_PORT` в `.env`
3. Проверь firewall/сетевые настройки

### Ошибка импорта модулей

```
ModuleNotFoundError: No module named 'grpc'
```

**Решение:**
```bash
source venv/bin/activate
pip install -r requirements.txt
```

### Проблемы с proto-файлами

```
ModuleNotFoundError: No module named 'router'
```

**Решение:**
```bash
bash generate_proto.sh
```

## Следующие шаги

1. Настрой OpenRouter API ключ для парсинга сообщений
2. Интегрируй с Telegram ботом или другим интерфейсом
3. Добавь обработку ошибок и логирование
4. Настрой мониторинг gRPC соединений
