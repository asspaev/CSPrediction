# 🧠 CSPrediction

Fullstack ML веб-приложение, предсказывающее победителя матча по CS:GO на основе статистических данных о игроках и командах.
Интеграция ML-модели с полноценным интерфейсом, фоновыми задачами, базой данных и API.

## 🚀 Технологии

**Backend:** FastAPI, Celery, SQLAlchemy, Alembic

**ML-интеграция:** Встроенные ML-модели для предсказаний

**Frontend:** Jinja2 + чистая вёрстка

**DevOps:** Docker Compose, Poetry, MySQL

## 📁 Структура проекта

```
├── app/
│   ├── main.py               # Запуск FastAPI-приложения
│   ├── celery_app.py         # Инициализация Celery
│   ├── api/                  # Роуты API
│   ├── core/                 # Настройки и конфигурации
│   ├── cruds/                # Операции с БД
│   ├── data/                 # Статические CSV/JSON-данные
│   ├── ml_models/            # ML-модели и пайплайны
│   ├── schemas/              # Pydantic-схемы
│   ├── sql_models/           # SQLAlchemy-модели
│   ├── static/               # CSS, JS и изображения
│   ├── tasks/                # Celery-задачи
│   ├── templates/            # Jinja2-шаблоны
│   ├── utils/                # Утилиты и вспомогательные функции
│   └── views/                # Обработчики страниц
├── web/                      # Полная вёрстка сайта
├── docs/                     # Документация
├── docker-compose.yml        # Docker конфигурация
├── poetry.lock               # Poetry lock-файл
├── pyproject.toml            # Зависимости и настройки проекта
└── .gitignore
```

## ⚙️ Запуск проекта

Запуск осуществлять из `app`

### 1. 📦 Поднять Docker Compose

```bash
docker compose up -d
```

### 2. 🧵 Запустить Celery

```bash
celery -A celery_app worker --pool=solo --loglevel=info
```

### 3. 🚀 Запустить FastAPI-приложение

```bash
python main.py
```

## 🧠 Описание ML-модели

ML-модель обучена на статистике матчей и игроков (рейтинги, убийства, смерти, K/D, карты и т.п.)
Используется для предсказания вероятного победителя между двумя командами на основе их состава.

## 📄 Лицензия

MIT License