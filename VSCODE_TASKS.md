# VS Code Tasks - Запуск сервисов

## 🎯 Быстрый старт

### Запуск всех сервисов:

1. **Cmd + Shift + P** (macOS) или **Ctrl + Shift + P** (Windows/Linux)
2. Выбери: **Tasks: Run Task**
3. Запусти в следующем порядке:

```
1. Run Router       ← Запусти первым (порт 50051)
2. Run Gateway      ← Запусти вторым (порт 8081)
3. Run NLP Service  ← Запусти третьим
4. Run Bot          ← Запусти последним
```

Каждый сервис откроется в отдельном терминале.

## 📋 Доступные задачи

### Основные сервисы:

| Задача | Описание | Порт |
|--------|----------|------|
| **Run Router** | gRPC сервис для управления событиями | 50051 |
| **Run Gateway** | HTTP API Gateway | 8081 |
| **Run NLP Service** | Python сервис для парсинга текста | - |
| **Run Bot** | Telegram бот | - |

### Утилиты:

| Задача | Описание |
|--------|----------|
| **Check Services Status** | Проверка статуса всех сервисов |
| **Test NLP Connection** | Тест подключения NLP к Router |
| **Test NLP Parsing** | Тест парсинга через OpenRouter |

## 🔍 Проверка что всё работает

### После запуска Router и Gateway:

1. **Cmd + Shift + P** → **Tasks: Run Task** → **Check Services Status**

Должен увидеть:
```
✓ Router Service (gRPC) - Running on port 50051
✓ Gateway Service (HTTP) - Running on port 8081
```

### Тест NLP подключения:

1. **Cmd + Shift + P** → **Tasks: Run Task** → **Test NLP Connection**

Должен увидеть:
```
✓ Scheduler service is reachable at localhost:50051
✓ All services are reachable!
```

## 🛑 Остановка сервисов

В каждом терминале нажми **Ctrl + C**

Или закрой терминалы через VS Code:
- Нажми на иконку корзины в панели терминала

## ⚙️ Конфигурация

Все задачи настроены в `.vscode/tasks.json`

### Порядок запуска важен:

1. **Router** - должен запуститься первым (другие сервисы зависят от него)
2. **Gateway** - зависит от Router
3. **NLP Service** - зависит от Router
4. **Bot** - зависит от Gateway

## 🐛 Troubleshooting

### Задача не запускается

**Проблема:** "command not found: go"
- Установи Go: https://go.dev/dl/

**Проблема:** "python: command not found"
- Активируй venv: `cd nlp && source venv/bin/activate`

### Router не запускается

**Проблема:** "database connection failed"
- Проверь `router/config/local.yaml`
- Убедись что database_url правильный

**Проблема:** "port already in use"
```bash
# Найди процесс
lsof -i :50051
# Убей процесс
kill -9 <PID>
```

### NLP Service не подключается

**Проблема:** "Cannot connect to Scheduler service"
- Убедись что Router запущен (задача "Run Router")
- Проверь порт в `.env`: `SCHEDULER_PORT=50051`

**Проблема:** "OPENROUTER_API_KEY is not set"
- Добавь ключ в `.env`: `openrouter=sk-or-v1-...`

## 📝 Примечания

### NLP Service в tasks.json

По умолчанию запускает `main.py` (тест парсинга).

Для других режимов запуска:
- Тест подключения: используй задачу **Test NLP Connection**
- Примеры: `cd nlp && source venv/bin/activate && python example.py`

### Логи

Все логи выводятся в соответствующие терминалы VS Code.

### Переменные окружения

Загружаются из `.env` в корне проекта.

## 🎨 Кастомизация

Чтобы изменить задачи:
1. Открой `.vscode/tasks.json`
2. Измени нужную задачу
3. Сохрани файл

Пример - изменить команду для NLP:
```json
{
  "label": "Run NLP Service",
  "command": "source venv/bin/activate && python your_script.py",
  ...
}
```

## 🔗 Полезные ссылки

- [VS Code Tasks Documentation](https://code.visualstudio.com/docs/editor/tasks)
- [START_ALL_SERVICES.md](START_ALL_SERVICES.md) - альтернативные способы запуска
- [nlp/README.md](nlp/README.md) - документация NLP сервиса
