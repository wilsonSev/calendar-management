# NLP Service

Python-сервис для обработки текстовых сообщений и взаимодействия с Go-сервисами через gRPC.

## Функциональность

- Парсинг текстовых сообщений через OpenRouter LLM
- Создание событий и задач в Scheduler сервисе через gRPC/protobuf
- Поддержка асинхронной обработки сообщений
- Автоматическая генерация Python кода из proto-файлов

## Быстрый старт

```bash
# 1. Установка
cd nlp
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# 2. Настройка .env (в корне проекта)
cp ../.env.example ../.env
# Добавь свой openrouter API ключ

# 3. Генерация proto-файлов
bash generate_proto.sh

# 4. Проверка подключения
python check_services.py

# 5. Запуск примеров
python example.py
```

Подробнее: [QUICKSTART.md](QUICKSTART.md)

## Архитектура

```
User Message → OpenRouter LLM → Event Parser → gRPC Client → Scheduler Service (Go)
```

## Основные модули

### scheduler_client.py
gRPC клиент для взаимодействия со Scheduler сервисом:

```python
from scheduler_client import SchedulerClient
from datetime import datetime, timedelta

with SchedulerClient() as client:
    success, event_id = client.create_event(
        title="Встреча",
        description="Обсуждение проекта",
        user_id="123",
        start_time=datetime.now() + timedelta(hours=1),
        end_time=datetime.now() + timedelta(hours=2)
    )
```

### main.py
Основная логика обработки сообщений:

```python
from main import process_user_message

success, event_id = process_user_message(
    user_message="Встреча завтра в 15:00",
    user_id="123456",
    username="Иван"
)
```

### openrouter.py
Интеграция с OpenRouter LLM для парсинга естественного языка.

## Конфигурация

Переменные окружения в `.env` (в корне проекта):

```env
# OpenRouter API
openrouter=your_api_key_here

# Scheduler gRPC service
SCHEDULER_HOST=localhost
SCHEDULER_PORT=50052
```

## Генерация proto-файлов

При изменении proto-файлов запусти:

```bash
bash generate_proto.sh
```

Скрипт автоматически:
- Генерирует Python код из `.proto` файлов
- Создает необходимые `__init__.py`
- Исправляет импорты для корректной работы

## Тестирование

### Проверка подключения к сервисам
```bash
python check_services.py
```

### Тест создания событий/задач
```bash
python test_connection.py
```

### Примеры использования
```bash
python example.py
```

## Структура проекта

```
nlp/
├── main.py                 # Основная точка входа
├── scheduler_client.py     # gRPC клиент для Scheduler
├── openrouter.py          # Интеграция с OpenRouter LLM
├── config.py              # Конфигурация
├── event.py               # Модели событий
├── message.py             # Модели сообщений
├── example.py             # Примеры использования
├── test_connection.py     # Тест подключения к gRPC
├── check_services.py      # Проверка статуса сервисов
├── generate_proto.sh      # Скрипт генерации proto
├── requirements.txt       # Python зависимости
├── venv/                  # Виртуальное окружение
└── lib/                   # Сгенерированные proto-файлы
    ├── router/
    │   └── proto/
    │       └── router/
    │           ├── router_pb2.py       # Protobuf messages
    │           ├── router_pb2_grpc.py  # gRPC stubs
    │           └── router_pb2.pyi      # Type hints
    └── google/
        └── protobuf/       # Google protobuf types
```

## API Reference

### SchedulerClient

#### create_event()
Создает событие в календаре.

**Параметры:**
- `title` (str): Название события
- `description` (str): Описание
- `user_id` (str): ID пользователя
- `start_time` (datetime): Время начала
- `end_time` (datetime): Время окончания
- `participants` (list[str], optional): Список участников

**Возвращает:**
- `tuple[bool, str]`: (успех, ID события)

#### create_task()
Создает задачу.

**Параметры:**
- `title` (str): Название задачи
- `description` (str): Описание
- `user_id` (str): ID пользователя

**Возвращает:**
- `tuple[bool, str]`: (успех, ID задачи)

## Troubleshooting

### gRPC connection failed
```
grpc._channel._InactiveRpcError
```
**Решение:** Убедись, что Scheduler сервис запущен и доступен на указанном хосте/порту.

### Module import errors
```
ModuleNotFoundError: No module named 'grpc'
```
**Решение:** Активируй venv и установи зависимости:
```bash
source venv/bin/activate
pip install -r requirements.txt
```

### Proto import errors
```
ModuleNotFoundError: No module named 'router'
```
**Решение:** Перегенерируй proto-файлы:
```bash
bash generate_proto.sh
```

## Зависимости

- `grpcio` - gRPC framework
- `grpcio-tools` - Protobuf compiler
- `protobuf` - Protocol Buffers
- `python-dotenv` - Environment variables
- `requests` - HTTP client для OpenRouter

## Разработка

### Добавление новых proto-файлов

1. Добавь `.proto` файл в `../proto/`
2. Обнови `generate_proto.sh`
3. Запусти генерацию: `bash generate_proto.sh`
4. Создай клиент аналогично `scheduler_client.py`

### Обновление зависимостей

```bash
pip install --upgrade -r requirements.txt
pip freeze > requirements.txt
```

## Лицензия

См. корневой README проекта.
