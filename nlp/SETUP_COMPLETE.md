# ✓ Настройка Python NLP сервиса завершена!

## Что было сделано

### 1. Структура проекта
- ✓ Создана структура для Python сервиса
- ✓ Настроено виртуальное окружение
- ✓ Установлены все зависимости

### 2. gRPC интеграция
- ✓ Сгенерированы Python файлы из proto (router/scheduler)
- ✓ Создан `SchedulerClient` для взаимодействия с Go-сервисом
- ✓ Исправлены импорты в сгенерированных файлах
- ✓ Настроен автоматический скрипт генерации proto

### 3. Конфигурация
- ✓ Создан `config.py` с настройками
- ✓ Обновлен `.env.example` с переменными для Python
- ✓ Настроены константы для подключения к Scheduler

### 4. Основной функционал
- ✓ Обновлен `main.py` с интеграцией gRPC клиента
- ✓ Исправлен `openrouter.py` для совместимости с Python 3.9+
- ✓ Создана функция `process_user_message()` для обработки сообщений

### 5. Утилиты и примеры
- ✓ `example.py` - примеры использования клиента
- ✓ `test_connection.py` - тест подключения к gRPC
- ✓ `check_services.py` - проверка статуса сервисов
- ✓ `generate_proto.sh` - автоматическая генерация proto

### 6. Документация
- ✓ `README.md` - полная документация
- ✓ `QUICKSTART.md` - быстрый старт
- ✓ `.gitignore` - игнорирование служебных файлов

## Что нужно сделать тебе

### 1. Настроить .env файл

В корне проекта (не в nlp/) создай/обнови `.env`:

```bash
# Добавь свой OpenRouter API ключ
openrouter=твой_ключ_здесь

# Укажи правильный порт для Scheduler сервиса
SCHEDULER_HOST=localhost
SCHEDULER_PORT=50052  # <-- ИЗМЕНИ НА ПРАВИЛЬНЫЙ ПОРТ
```

### 2. Запустить Go Scheduler сервис

Убедись, что Scheduler сервис (Go) запущен и слушает на порту, указанном в `.env`.

### 3. Проверить подключение

```bash
cd nlp
source venv/bin/activate
python check_services.py
```

Если всё ОК, увидишь:
```
✓ Scheduler service is reachable at localhost:50052
✓ All services are reachable!
```

### 4. Протестировать

```bash
# Тест создания событий
python test_connection.py

# Примеры использования
python example.py

# Основной скрипт (требует OpenRouter API ключ)
python main.py
```

## Как использовать

### Вариант 1: Через context manager (рекомендуется)

```python
from scheduler_client import SchedulerClient
from datetime import datetime, timedelta

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

### Вариант 2: Через main.py (с OpenRouter)

```python
from main import process_user_message

success, event_id = process_user_message(
    user_message="Встреча завтра в 15:00, продлится 2 часа",
    user_id="123456",
    username="Иван"
)
```

## Структура файлов

```
nlp/
├── main.py                    # Основная точка входа
├── scheduler_client.py        # gRPC клиент ⭐
├── config.py                  # Конфигурация
├── openrouter.py             # OpenRouter LLM
├── event.py                  # Модели событий
├── message.py                # Модели сообщений
│
├── example.py                # Примеры использования
├── test_connection.py        # Тест gRPC
├── check_services.py         # Проверка сервисов
│
├── generate_proto.sh         # Генерация proto
├── requirements.txt          # Зависимости
├── README.md                 # Документация
├── QUICKSTART.md            # Быстрый старт
│
├── venv/                     # Виртуальное окружение
└── lib/                      # Сгенерированные proto
    └── router/
        └── proto/
            └── router/
                ├── router_pb2.py
                └── router_pb2_grpc.py
```

## Troubleshooting

### Не могу подключиться к Scheduler

1. Проверь, что Go сервис запущен
2. Проверь порт в `.env`
3. Запусти `python check_services.py`

### Ошибки импорта

```bash
source venv/bin/activate
pip install -r requirements.txt
```

### Нужно обновить proto-файлы

```bash
bash generate_proto.sh
```

## Следующие шаги

1. Интегрируй с Telegram ботом
2. Добавь обработку ошибок
3. Настрой логирование
4. Добавь retry логику для gRPC
5. Настрой мониторинг

## Вопросы?

Проверь:
- `README.md` - полная документация
- `QUICKSTART.md` - быстрый старт
- `example.py` - примеры кода

---

**Готово к использованию!** 🚀
