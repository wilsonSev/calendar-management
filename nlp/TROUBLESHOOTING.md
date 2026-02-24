# Troubleshooting NLP Service

## Проблема: NLP сервис зависает после "Input message"

### Причины:

1. **OpenRouter API медленно отвечает** (5-15 секунд это нормально)
2. **Неправильный API ключ**
3. **Нет интернета**
4. **OpenRouter API недоступен**

### Решение:

#### 1. Проверь API ключ

```bash
cd nlp
source venv/bin/activate
python test_config.py
```

Должен увидеть:
```
✓ API key loaded successfully (length: 73 chars)
```

#### 2. Быстрый тест OpenRouter

```bash
cd nlp
source venv/bin/activate
python test_openrouter.py
```

Это займет 5-15 секунд. Если работает, увидишь:
```
✓ SUCCESS!
Parsed event:
  Name: Встреча
  Start: 2026-02-25 14:00:00
  End: 2026-02-25 14:00:00
```

#### 3. Проверь интернет

```bash
curl -I https://openrouter.ai
```

Должен вернуть `HTTP/2 200`

#### 4. Проверь что ключ валидный

Зайди на https://openrouter.ai/keys и проверь свой ключ.

## Проблема: "OPENROUTER_API_KEY is not set"

### Решение:

1. Проверь `.env` в корне проекта:
```bash
cat .env | grep openrouter
```

2. Должна быть строка:
```
openrouter=sk-or-v1-...
```

3. Если нет, добавь:
```bash
echo "openrouter=твой_ключ" >> .env
```

## Проблема: "Cannot connect to Scheduler service"

### Решение:

1. Запусти Router:
```bash
cd router
go run cmd/router/main.go
```

2. Проверь что Router работает:
```bash
lsof -i :50051
```

3. Проверь порт в `.env`:
```bash
cat .env | grep SCHEDULER_PORT
# Должно быть: SCHEDULER_PORT=50051
```

## Проблема: Timeout после 30 секунд

### Причины:
- OpenRouter API перегружен
- Медленный интернет

### Решение:

1. Попробуй другую модель (быстрее):
```python
# В openrouter.py измени:
model=Models.Stepfun.value  # Вместо Llama
```

2. Увеличь timeout:
```python
# В openrouter.py:
timeout=60  # Вместо 30
```

## Проблема: "Failed to parse JSON"

### Причины:
- LLM вернул невалидный JSON
- LLM не понял запрос

### Решение:

1. Проверь `dump.json` - там последний ответ от API
2. Попробуй другую модель
3. Улучши промпт в `openrouter.py`

## Быстрая диагностика

```bash
cd nlp
source venv/bin/activate

# 1. Проверка конфигурации
python test_config.py

# 2. Проверка OpenRouter API
python test_openrouter.py

# 3. Проверка подключения к Router
python check_services.py

# 4. Полный тест
python test_connection.py
```

## Логи

### Где смотреть:

1. **Вывод в терминале** - основные логи
2. **dump.json** - последний ответ от OpenRouter
3. **VS Code Terminal** - если запускал через Task

### Что искать:

- `Response status: 200` - API работает
- `Response status: 401` - неправильный ключ
- `Response status: 429` - превышен лимит запросов
- `Timeout` - API не отвечает

## Полезные команды

```bash
# Проверить все сервисы
./check_status.sh

# Проверить порты
lsof -i :50051  # Router
lsof -i :8081   # Gateway

# Проверить .env
cat .env | grep -E "openrouter|SCHEDULER"

# Тест интернета
ping -c 3 8.8.8.8
curl -I https://openrouter.ai
```

## Если ничего не помогает

1. Удали и пересоздай venv:
```bash
cd nlp
rm -rf venv
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

2. Перегенерируй proto:
```bash
bash generate_proto.sh
```

3. Проверь версию Python:
```bash
python --version  # Должна быть 3.9+
```

4. Проверь зависимости:
```bash
pip list | grep -E "grpc|requests|protobuf"
```
