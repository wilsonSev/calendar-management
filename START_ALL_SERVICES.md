# Запуск всех сервисов

## 🚀 Быстрый старт через VS Code (рекомендуется)

### Запуск всех сервисов по очереди:

1. Открой Command Palette: `Cmd + Shift + P` (macOS) или `Ctrl + Shift + P` (Windows/Linux)
2. Выбери: `Tasks: Run Task`
3. Запусти задачи в следующем порядке:
   - **Run Router** (обязательно первым)
   - **Run Gateway** (обязательно вторым)
   - **Run NLP Service** (третьим)
   - **Run Bot** (последним)

Каждый сервис запустится в отдельном терминале.

### Проверка статуса:

`Cmd + Shift + P` → `Tasks: Run Task` → `Check Services Status`

### Тестирование NLP:

`Cmd + Shift + P` → `Tasks: Run Task` → `Test NLP Connection`

## Вариант 2: Вручную (для разработки)

Открой 3 терминала:

#### Терминал 1: Router (Scheduler) Service
```bash
cd router
go run cmd/router/main.go
```

Должен увидеть:
```
INFO starting router microservice
INFO gRPC server started port=50051
```

#### Терминал 2: Gateway Service (опционально)
```bash
cd services/gateway
go run cmd/server/main.go
```

#### Терминал 3: Python NLP Service (тестирование)
```bash
cd nlp
source venv/bin/activate

# Проверка подключения
python check_services.py

# Тест парсинга через OpenRouter
python main.py

# Тест создания события через gRPC
python test_connection.py
```

### Вариант 2: Docker Compose (если настроен)

```bash
docker-compose up
```

## Проверка что всё работает

### 1. Проверить порты

```bash
# Router должен слушать на 50051
lsof -i :50051

# Gateway должен слушать на 8081 (если запущен)
lsof -i :8081
```

### 2. Проверить Python подключение

```bash
cd nlp
source venv/bin/activate
python check_services.py
```

Ожидаемый результат:
```
✓ Scheduler service is reachable at localhost:50051
✓ All services are reachable!
```

### 3. Протестировать создание события

```bash
cd nlp
source venv/bin/activate
python test_connection.py
```

## Остановка сервисов

В каждом терминале нажми `Ctrl+C`

## Troubleshooting

### Router не запускается

**Проблема:** База данных недоступна
```bash
# Проверь router/config/local.yaml
cat router/config/local.yaml | grep database_url
```

**Проблема:** Порт занят
```bash
# Найди процесс
lsof -i :50051
# Убей процесс
kill -9 <PID>
```

### Python не подключается

**Проблема:** Router не запущен
```bash
# Проверь что Router работает
lsof -i :50051
```

**Проблема:** Неправильный порт в .env
```bash
# Должно быть 50051
cat .env | grep SCHEDULER_PORT
```

### OpenRouter не работает

**Проблема:** Нет API ключа
```bash
# Проверь .env
cat .env | grep openrouter

# Проверь загрузку
cd nlp && source venv/bin/activate && python test_config.py
```

## Минимальная конфигурация для работы

Для работы Python NLP сервиса нужен только:

1. **Router service** (Go) на порту 50051
2. **OpenRouter API ключ** в `.env`

Gateway и другие сервисы опциональны для тестирования NLP.

## Порядок запуска

1. ✅ Router (обязательно) - порт 50051
2. ⚠️ Gateway (опционально) - порт 8081  
3. ✅ Python NLP (для тестирования)

## Быстрая команда для проверки

```bash
# Проверить что Router запущен
lsof -i :50051 && echo "✓ Router running" || echo "✗ Router not running"

# Проверить Python конфигурацию
cd nlp && source venv/bin/activate && python test_config.py
```
