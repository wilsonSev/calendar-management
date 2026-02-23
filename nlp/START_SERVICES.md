# Запуск и проверка сервисов

## Статус сервисов

### 1. Router (Scheduler) - Go gRPC сервис
- **Порт:** 50051
- **Протокол:** gRPC
- **Назначение:** Управление событиями и задачами

### 2. NLP Service - Python
- **Зависит от:** Router service
- **Назначение:** Парсинг текста через LLM и отправка в Router

## Запуск сервисов

### Шаг 1: Запустить Router (Go)

```bash
# Из корня проекта
cd router
go run cmd/router/main.go
```

Должен увидеть:
```
INFO starting router microservice
INFO gRPC server started port=50051
```

### Шаг 2: Проверить подключение к Router

В новом терминале:

```bash
cd nlp
source venv/bin/activate
python check_services.py
```

Должен увидеть:
```
✓ Scheduler service is reachable at localhost:50051
✓ All services are reachable!
```

### Шаг 3: Протестировать NLP сервис

```bash
# Тест только парсинга (без gRPC)
python main.py

# Тест создания события через gRPC
python test_connection.py

# Примеры использования
python example.py
```

## Проверка портов

```bash
# Проверить, что Router запущен на 50051
lsof -i :50051

# Или
netstat -an | grep 50051
```

## Troubleshooting

### Router не запускается

**Ошибка:** `database connection failed`
- Проверь `router/config/local.yaml`
- Убедись, что database_url правильный

**Ошибка:** `port already in use`
```bash
# Найти процесс на порту 50051
lsof -i :50051
# Убить процесс
kill -9 <PID>
```

### Python не может подключиться

**Ошибка:** `Timeout: Cannot connect to Scheduler service`

1. Проверь, что Router запущен:
   ```bash
   lsof -i :50051
   ```

2. Проверь порт в `.env`:
   ```bash
   cat ../.env | grep SCHEDULER_PORT
   # Должно быть: SCHEDULER_PORT=50051
   ```

3. Проверь конфигурацию:
   ```bash
   python test_config.py
   ```

### OpenRouter API ошибки

**Ошибка:** `OPENROUTER_API_KEY is not set`

1. Проверь `.env` в корне проекта:
   ```bash
   cat ../.env | grep openrouter
   ```

2. Убедись, что ключ правильный (начинается с `sk-or-v1-`)

3. Проверь загрузку:
   ```bash
   python test_config.py
   ```

## Быстрая проверка всех сервисов

```bash
# Терминал 1: Запуск Router
cd router && go run cmd/router/main.go

# Терминал 2: Проверка
cd nlp && source venv/bin/activate && python check_services.py

# Если всё ОК:
python test_connection.py
```

## Остановка сервисов

### Router (Go)
- Нажми `Ctrl+C` в терминале где запущен

### Python
- Скрипты завершаются автоматически
- Для прерывания: `Ctrl+C`

## Логи

### Router
- Логи выводятся в stdout
- Уровень: DEBUG (local), INFO (prod)

### Python
- Логи выводятся в stdout
- Файл `dump.json` содержит последний ответ от OpenRouter

## Порты по умолчанию

| Сервис | Порт | Протокол |
|--------|------|----------|
| Router (gRPC) | 50051 | gRPC |
| Gateway (HTTP) | 8081 | HTTP |
| PostgreSQL | 5432 | TCP |

## Конфигурация

### Router
- Файл: `router/config/local.yaml`
- Порт gRPC: 50051

### Python NLP
- Файл: `.env` (в корне проекта)
- Переменные:
  - `SCHEDULER_HOST=localhost`
  - `SCHEDULER_PORT=50051`
  - `openrouter=sk-or-v1-...`
