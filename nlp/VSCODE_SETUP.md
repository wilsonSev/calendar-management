# VS Code Setup для NLP Service

## ✅ Всё готово!

Python NLP сервис полностью настроен и интегрирован с VS Code Tasks.

## 🎯 Как запустить

### Через VS Code Tasks (рекомендуется):

1. **Cmd + Shift + P** (или **Ctrl + Shift + P**)
2. Выбери: **Tasks: Run Task**
3. Запусти по порядку:
   ```
   1. Run Router       ← gRPC сервис (порт 50051)
   2. Run Gateway      ← HTTP API (порт 8081)
   3. Run NLP Service  ← Python парсинг
   4. Run Bot          ← Telegram бот
   ```

### Проверка:

**Cmd + Shift + P** → **Tasks: Run Task** → **Check Services Status**

Должен увидеть:
```
✓ Router Service (gRPC) - Running on port 50051
✓ Gateway Service (HTTP) - Running on port 8081
✓ .env file exists with openrouter key
✓ Virtual environment exists
```

## 📁 Что было настроено

### 1. VS Code Tasks (`.vscode/tasks.json`)
- ✅ Run Router
- ✅ Run Gateway
- ✅ Run NLP Service
- ✅ Run Bot
- ✅ Check Services Status
- ✅ Test NLP Connection
- ✅ Test NLP Parsing

### 2. Python NLP Service (`nlp/`)
- ✅ Виртуальное окружение (`venv/`)
- ✅ Зависимости установлены (`requirements.txt`)
- ✅ gRPC клиент для Router (`scheduler_client.py`)
- ✅ Интеграция с OpenRouter LLM (`openrouter.py`)
- ✅ Конфигурация (`.env` загрузка)
- ✅ Proto-файлы сгенерированы (`lib/router/`)
- ✅ Тесты и примеры

### 3. Конфигурация (`.env`)
- ✅ `openrouter` - API ключ для LLM
- ✅ `SCHEDULER_HOST=localhost`
- ✅ `SCHEDULER_PORT=50051`

### 4. Документация
- ✅ `nlp/README.md` - полная документация
- ✅ `nlp/QUICKSTART.md` - быстрый старт
- ✅ `nlp/ARCHITECTURE.md` - архитектура
- ✅ `VSCODE_TASKS.md` - VS Code tasks
- ✅ `START_ALL_SERVICES.md` - запуск сервисов

## 🧪 Тестирование

### 1. Проверка подключения к Router:
**Cmd + Shift + P** → **Tasks: Run Task** → **Test NLP Connection**

### 2. Тест парсинга через OpenRouter:
**Cmd + Shift + P** → **Tasks: Run Task** → **Test NLP Parsing**

### 3. Тест создания события:
```bash
cd nlp
source venv/bin/activate
python test_connection.py
```

### 4. Примеры использования:
```bash
cd nlp
source venv/bin/activate
python example.py
```

## 🔧 Использование в коде

### Простой пример:

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

### С парсингом через LLM:

```python
from main import process_user_message

success, event_id = process_user_message(
    user_message="Встреча завтра в 15:00",
    user_id="123456",
    username="Иван"
)
```

## 🐛 Troubleshooting

### NLP Service не запускается через Task

**Проблема:** "venv not found"
```bash
cd nlp
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

**Проблема:** "Cannot connect to Scheduler"
- Убедись что Router запущен (задача "Run Router")
- Проверь что порт 50051 свободен: `lsof -i :50051`

**Проблема:** "OPENROUTER_API_KEY is not set"
- Добавь ключ в `.env`: `openrouter=sk-or-v1-...`
- Проверь: `cd nlp && source venv/bin/activate && python test_config.py`

### Proto-файлы не найдены

```bash
cd nlp
source venv/bin/activate
bash generate_proto.sh
```

## 📝 Следующие шаги

1. ✅ Запусти Router через VS Code Task
2. ✅ Проверь подключение: **Test NLP Connection**
3. ✅ Протестируй парсинг: **Test NLP Parsing**
4. ✅ Интегрируй с Telegram ботом
5. ⚠️ Добавь обработку ошибок и логирование
6. ⚠️ Настрой мониторинг

## 🎉 Готово!

Всё настроено и готово к использованию. Запускай сервисы через VS Code Tasks и тестируй!

**Полезные команды:**
- Проверка статуса: `./check_status.sh`
- Документация: `nlp/README.md`
- VS Code Tasks: `VSCODE_TASKS.md`
