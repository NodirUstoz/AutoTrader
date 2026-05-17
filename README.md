<div align="center">

# AutoTrader

**Комплексная платформа автомобильного маркетплейса для покупки, продажи и сравнения транспортных средств — ваш собственный AutoTrader / Cars.com под полным контролем.**

<br/>

![Python](https://img.shields.io/badge/Python-3.12+-3776AB?style=for-the-badge&logo=python&logoColor=white)
![Django](https://img.shields.io/badge/Django-5.0-092E20?style=for-the-badge&logo=django&logoColor=white)
![DRF](https://img.shields.io/badge/DRF-3.15-FF1709?style=for-the-badge&logo=django&logoColor=white)
![React](https://img.shields.io/badge/React-18-61DAFB?style=for-the-badge&logo=react&logoColor=black)
![PostgreSQL](https://img.shields.io/badge/PostgreSQL-16-4169E1?style=for-the-badge&logo=postgresql&logoColor=white)
![Redis](https://img.shields.io/badge/Redis-7-DC382D?style=for-the-badge&logo=redis&logoColor=white)
![Celery](https://img.shields.io/badge/Celery-5-37814A?style=for-the-badge&logo=celery&logoColor=white)
![Elasticsearch](https://img.shields.io/badge/Elasticsearch-8-005571?style=for-the-badge&logo=elasticsearch&logoColor=white)
![Docker](https://img.shields.io/badge/Docker_Compose-3.9-2496ED?style=for-the-badge&logo=docker&logoColor=white)
![Nginx](https://img.shields.io/badge/Nginx-1.25-009639?style=for-the-badge&logo=nginx&logoColor=white)
![License](https://img.shields.io/badge/License-Proprietary-555555?style=for-the-badge)



</div>

---

## Содержание

1. [О проекте](#1-о-проекте)
2. [Ключевые возможности](#2-ключевые-возможности)
3. [Технологический стек](#3-технологический-стек)
4. [Структура репозитория](#4-структура-репозитория)
5. [Архитектура и как это работает](#5-архитектура-и-как-это-работает)
6. [Доменная модель (крупными блоками)](#6-доменная-модель-крупными-блоками)
7. [Сервисы в Docker Compose](#7-сервисы-в-docker-compose)
8. [Быстрый старт (локально, Docker)](#8-быстрый-старт-локально-docker)
9. [Основные команды Makefile](#9-основные-команды-makefile)
10. [Ручной запуск frontend и backend](#10-ручной-запуск-frontend-и-backend)
11. [Конфигурация и переменные окружения](#11-конфигурация-и-переменные-окружения)
12. [API, очереди и интеграции](#12-api-очереди-и-интеграции)
13. [Мониторинг и эксплуатация](#13-мониторинг-и-эксплуатация)
14. [CI/CD](#14-cicd)
15. [Безопасность и хранение файлов](#15-безопасность-и-хранение-файлов)
16. [Роли компонентов в продакшене](#16-роли-компонентов-в-продакшене)
17. [Лицензия](#17-лицензия)
18. [Поддержка](#18-поддержка)

---

## 1. О проекте

**AutoTrader** — это полнофункциональная SaaS-платформа автомобильного маркетплейса: размещение объявлений, расширенный поиск, сравнение автомобилей, финансирование, запросы покупателей и аналитика для дилеров. Платформа рассчитана на три аудитории:

| Аудитория | Сценарий использования |
|-----------|------------------------|
| **Покупатели** | Поиск, фильтрация, сравнение, сохранённые поиски, запросы и тест-драйвы |
| **Дилеры** | Управление инвентарём, профиль дилера, публикация объявлений, аналитика |
| **Интеграторы** | Версионированный REST API, OpenAPI/Swagger, JWT-аутентификация |

### Что это за тип системы

AutoTrader — **распределённая мультисервисная платформа**, а не монолитное SPA-приложение. Бизнес-логика сосредоточена в Django API, тяжёлые и отложенные операции вынесены в Celery, полнотекстовый поиск — в Elasticsearch, клиентский интерфейс — в React SPA за Nginx reverse proxy.

| Аспект | Описание |
|--------|----------|
| **Продукт** | B2C/B2B маркетплейс транспортных средств: объявления, VIN-декодер, сравнение, финансирование, история цен |
| **Архитектура** | Multi-service: Django REST API + React SPA + Celery workers + Elasticsearch + Nginx |
| **Хранилище** | PostgreSQL (метаданные и транзакции) + Redis (кэш и брокер Celery) + Elasticsearch (поиск) + локальные/media volumes (фото) |

---

## 2. Ключевые возможности

| Модуль | Возможности |
|--------|-------------|
| **Объявления** | Создание, черновики, публикация, статусы (active / sold / expired), featured-листинги, история цен |
| **Каталог ТС** | Иерархия марка → модель, характеристики, галерея изображений, теги опций |
| **Поиск** | Фильтры по марке, модели, году, цене, пробегу, кузову, топливу, КПП; индексация в Elasticsearch |
| **VIN-декодер** | Автоматическая расшифровка VIN через NHTSA API |
| **Дилеры** | Верифицированные профили, инвентарь, аналитика просмотров и запросов |
| **Сравнение** | Side-by-side сравнение до четырёх автомобилей |
| **Финансирование** | Калькулятор ежемесячного платежа, заявки на кредит |
| **Сохранённые поиски** | Email-уведомления при появлении новых объявлений (Celery Beat) |
| **Запросы** | Сообщения продавцу, заявки на тест-драйв |
| **UI** | Адаптивный React-интерфейс, Redux Toolkit, toast-уведомления |

---

## 3. Технологический стек

### Backend

| Компонент | Технология | Назначение |
|-----------|------------|------------|
| Framework | Django 5.0 | ORM, admin, middleware |
| API | Django REST Framework 3.15 | REST endpoints, сериализаторы, permissions |
| Auth | SimpleJWT + django-allauth | JWT access/refresh, регистрация |
| DB | PostgreSQL 16 | Основное хранилище |
| Cache | django-redis | Кэширование сессий и запросов |
| Queue | Celery 5 + django-celery-beat | Фоновые задачи и расписание |
| Search | Elasticsearch 8 + django-elasticsearch-dsl | Полнотекстовый поиск объявлений |
| Docs | drf-spectacular | OpenAPI 3, Swagger UI, ReDoc |
| Media | Pillow + django-imagekit | Обработка изображений |
| Server | Gunicorn | WSGI в production |

### Frontend

| Компонент | Технология |
|-----------|------------|
| UI | React 18 |
| State | Redux Toolkit |
| Routing | React Router 6 |
| HTTP | Axios (interceptors для JWT refresh) |
| UX | react-toastify |

### Инфраструктура

| Компонент | Технология |
|-----------|------------|
| Контейнеризация | Docker Compose 3.9 |
| Reverse proxy | Nginx 1.25 |
| Quality | flake8, black, isort, pytest |

---

## 4. Структура репозитория

```
AutoTrader/
├── backend/                          # Django + DRF API
│   ├── apps/
│   │   ├── accounts/                 # User, DealerProfile, BuyerProfile, JWT auth
│   │   ├── vehicles/                 # Каталог: марки, модели, Vehicle, изображения
│   │   ├── listings/                 # Объявления, PriceHistory, SavedSearch, Celery tasks
│   │   ├── inquiries/                # Запросы покупателей, тест-драйвы
│   │   ├── comparisons/              # Сравнение автомобилей
│   │   └── financing/                # Калькулятор и заявки на кредит
│   ├── config/
│   │   ├── settings/                 # base · development · production
│   │   ├── urls.py                   # /api/v1/*, Swagger, ReDoc
│   │   ├── celery.py                 # Celery app
│   │   ├── wsgi.py / asgi.py
│   ├── utils/                        # pagination, VIN decoder, exceptions
│   ├── manage.py
│   └── requirements.txt
├── frontend/                         # React SPA
│   ├── src/
│   │   ├── api/                      # Axios clients (auth, listings, vehicles)
│   │   ├── components/               # UI: auth, vehicles, search, dealer, financing
│   │   ├── pages/                    # Dashboard, Settings
│   │   ├── store/                    # Redux slices
│   │   ├── hooks/
│   │   └── styles/
│   └── package.json
├── nginx/
│   └── nginx.conf                    # Reverse proxy: /api, /admin, /static, /media, SPA
├── docker-compose.yml
├── Makefile
├── .env.example
└── README.md
```

---

## 5. Архитектура и как это работает

### Общая схема

```
┌─────────────┐     ┌─────────────┐     ┌──────────────────────────────────────┐
│   Browser   │────▶│    Nginx    │────▶│  React SPA (frontend:3000)           │
│   Client    │     │   :80/:443  │     │  Redux · Router · Axios              │
└─────────────┘     └──────┬──────┘     └──────────────────────────────────────┘
                           │
                           │  /api/v1/*  /admin/  /static/  /media/
                           ▼
                    ┌─────────────┐
                    │   Backend   │
                    │  Gunicorn   │
                    │   :8000     │
                    └──────┬──────┘
           ┌───────────────┼───────────────┐
           ▼               ▼               ▼
    ┌────────────┐  ┌────────────┐  ┌─────────────────┐
    │ PostgreSQL │  │   Redis    │  │ Elasticsearch   │
    │    :5432   │  │   :6379    │  │     :9200       │
    └────────────┘  └─────┬──────┘  └─────────────────┘
                          │
              ┌───────────┴───────────┐
              ▼                       ▼
       ┌─────────────┐         ┌─────────────┐
       │Celery Worker│         │ Celery Beat │
       │  (async)    │         │ (schedule)  │
       └─────────────┘         └─────────────┘
```

### Поток запроса (типичный сценарий)

1. Пользователь открывает SPA через Nginx (`/`).
2. React запрашивает данные у `/api/v1/` с JWT в заголовке `Authorization`.
3. DRF обрабатывает запрос: permissions → serializer → ORM → PostgreSQL.
4. Поисковые запросы дополнительно обращаются к Elasticsearch-индексу.
5. Долгие операции (email, истечение объявлений, статистика) — в Celery через Redis broker.
6. Медиафайлы отдаются Nginx из volume `/media/`.

### Версионирование API

Все публичные endpoints — под префиксом **`/api/v1/`**. Схема OpenAPI: `/api/v1/schema/`, интерактивная документация: `/api/v1/docs/`.

---

## 6. Доменная модель (крупными блоками)

```
┌─────────────────────────────────────────────────────────────────┐
│                         ACCOUNTS                                 │
│  User (buyer | dealer | admin)                                  │
│  ├── DealerProfile   (верификация, адрес, рейтинг)              │
│  └── BuyerProfile    (предпочтения, сохранённые объявления)     │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│                         VEHICLES                                 │
│  VehicleMake → VehicleModel → Vehicle                           │
│  ├── VehicleImage                                               │
│  └── VehicleFeature                                             │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│                         LISTINGS                                 │
│  Listing (price, status, location, engagement metrics)          │
│  ├── PriceHistory                                               │
│  └── SavedSearch (filters JSON, notify_email, frequency)        │
└─────────────────────────────────────────────────────────────────┘
         │                    │                    │
         ▼                    ▼                    ▼
   INQUIRIES            COMPARISONS           FINANCING
   (messages,           (up to 4 vehicles)   (calculator,
    test drives)                             loan applications)
```

### Статусы объявления

| Статус | Описание |
|--------|----------|
| `draft` | Черновик, не виден в каталоге |
| `pending` | На модерации |
| `active` | Опубликовано |
| `sold` | Продано |
| `expired` | Истёк срок (Celery Beat) |
| `removed` | Снято продавцом |

---

## 7. Сервисы в Docker Compose

| Сервис | Образ / сборка | Порт | Назначение |
|--------|----------------|------|------------|
| `db` | postgres:16-alpine | 5432 | Основная БД |
| `redis` | redis:7-alpine | 6379 | Кэш + Celery broker |
| `elasticsearch` | ES 8.12 | 9200 | Полнотекстовый поиск |
| `backend` | `./backend` | 8000 | Django API (Gunicorn) |
| `celery_worker` | `./backend` | — | Асинхронные задачи |
| `celery_beat` | `./backend` | — | Периодические задачи (DatabaseScheduler) |
| `frontend` | `./frontend` | 3000 | React dev/build server |
| `nginx` | nginx:1.25-alpine | 80, 443 | Единая точка входа |

### Volumes

| Volume | Содержимое |
|--------|------------|
| `postgres_data` | Данные PostgreSQL |
| `redis_data` | Persistence Redis |
| `elasticsearch_data` | Индексы ES |
| `static_volume` | Django staticfiles |
| `media_volume` | Загруженные фото ТС и аватары |

---

## 8. Быстрый старт (локально, Docker)

### Требования

- Docker Engine **24+** и Docker Compose **v2.20+**
- GNU Make (рекомендуется)
- ~4 GB свободной RAM (Elasticsearch)

### Запуск за 5 минут

```bash
# 1. Клонировать репозиторий
git clone https://github.com/NodirOdilov/AutoTrader.git
cd AutoTrader

# 2. Подготовить окружение
cp .env.example .env
# Отредактируйте SECRET_KEY и пароли для production

# 3. Собрать и запустить стек
make build
make up

# 4. Применить миграции и создать администратора
make migrate
make superuser
```

### Точки доступа

| Сервис | URL |
|--------|-----|
| **Веб-приложение (через Nginx)** | http://localhost |
| **Frontend (напрямую)** | http://localhost:3000 |
| **REST API** | http://localhost/api/v1/ |
| **Django Admin** | http://localhost/admin/ |
| **Swagger UI** | http://localhost/api/v1/docs/ |
| **ReDoc** | http://localhost/api/v1/redoc/ |
| **Elasticsearch** | http://localhost:9200 |

> Первый запуск Elasticsearch может занять 1–2 минуты. Backend дождётся healthcheck всех зависимостей.

---

## 9. Основные команды Makefile

```bash
make help              # Список всех команд с описанием

# Жизненный цикл
make build             # Собрать Docker-образы
make up                # Запустить все сервисы (-d)
make down              # Остановить стек
make restart           # Перезапустить сервисы
make status            # docker compose ps
make clean             # Удалить контейнеры, volumes и образы (⚠️ destructive)

# База данных и Django
make migrate           # python manage.py migrate
make makemigrations    # Создать новые миграции
make superuser         # Создать суперпользователя
make shell             # Django shell_plus
make dbshell           # psql через Django
make flush             # Очистить БД (⚠️ destructive)
make collectstatic     # Собрать staticfiles

# Качество кода и тесты
make test              # pytest -v
make test-cov          # pytest с coverage
make lint              # flake8 + isort + black --check
make format            # isort + black (автоформат)

# Логи и отладка
make logs              # Все сервисы
make logs-backend      # Только backend
make logs-celery       # Только celery_worker

# Данные
make seed              # loaddata fixtures/*.json
make dump              # Экспорт accounts, vehicles, listings

# Контейнеры
make backend-shell     # bash в backend
make frontend-shell    # sh в frontend
make redis-cli         # Redis CLI
```

---

## 10. Ручной запуск frontend и backend

Используйте, если разрабатываете без полного Docker-стека или отлаживаете отдельный сервис.

### Backend (локально)

```bash
cd backend
python -m venv .venv
source .venv/bin/activate          # Windows: .venv\Scripts\activate
pip install -r requirements.txt

export DJANGO_SETTINGS_MODULE=config.settings.development
export DATABASE_URL=postgres://autotrader:autotrader_secret@localhost:5432/autotrader
export REDIS_URL=redis://localhost:6379/0
export ELASTICSEARCH_URL=http://localhost:9200

python manage.py migrate
python manage.py runserver 0.0.0.0:8000
```

### Celery (отдельные терминалы)

```bash
celery -A config.celery worker -l info --concurrency=4
celery -A config.celery beat -l info --scheduler django_celery_beat.schedulers:DatabaseScheduler
```

### Frontend (локально)

```bash
cd frontend
npm install
REACT_APP_API_URL=http://localhost:8000/api/v1 npm start
```

---

## 11. Конфигурация и переменные окружения

Скопируйте `.env.example` → `.env`. Полный список переменных — в файле; ключевые группы:

### Django

| Переменная | Описание | Пример |
|------------|----------|--------|
| `DJANGO_SETTINGS_MODULE` | Модуль настроек | `config.settings.development` |
| `SECRET_KEY` | Секрет Django | длинная случайная строка |
| `DEBUG` | Режим отладки | `True` / `False` |
| `ALLOWED_HOSTS` | Разрешённые хосты | `localhost,127.0.0.1` |
| `CORS_ALLOWED_ORIGINS` | CORS для SPA | `http://localhost:3000` |

### База данных и кэш

| Переменная | Описание |
|------------|----------|
| `POSTGRES_DB` / `POSTGRES_USER` / `POSTGRES_PASSWORD` | Учётные данные PostgreSQL |
| `DATABASE_URL` | Connection string (dj-database-url) |
| `REDIS_URL` | Redis для кэша |
| `CELERY_BROKER_URL` | Redis DB для Celery (обычно `/1`) |

### Поиск и интеграции

| Переменная | Описание |
|------------|----------|
| `ELASTICSEARCH_URL` | URL кластера ES |
| `VIN_API_URL` | NHTSA VIN Decoder API |
| `REACT_APP_API_URL` | Base URL API для frontend |

### JWT и медиа

| Переменная | Описание | По умолчанию |
|------------|----------|--------------|
| `JWT_ACCESS_TOKEN_LIFETIME_MINUTES` | Время жизни access-токена | 60 |
| `JWT_REFRESH_TOKEN_LIFETIME_DAYS` | Время жизни refresh-токена | 7 |
| `MAX_UPLOAD_SIZE_MB` | Лимит загрузки файлов | 10 |

### Email

| Переменная | Описание |
|------------|----------|
| `EMAIL_BACKEND` | Backend (console для dev) |
| `EMAIL_HOST` / `EMAIL_PORT` / `EMAIL_USE_TLS` | SMTP для production |

---

## 12. API, очереди и интеграции

### REST API (v1)

<details>
<summary><b>Аутентификация</b></summary>

| Метод | Endpoint | Описание |
|-------|----------|----------|
| `POST` | `/api/v1/auth/register/` | Регистрация |
| `POST` | `/api/v1/auth/login/` | Получить JWT pair |
| `POST` | `/api/v1/auth/token/refresh/` | Обновить access token |
| `GET` | `/api/v1/auth/profile/` | Профиль текущего пользователя |

</details>

<details>
<summary><b>Транспортные средства</b></summary>

| Метод | Endpoint | Описание |
|-------|----------|----------|
| `GET` | `/api/v1/vehicles/` | Список с фильтрацией |
| `POST` | `/api/v1/vehicles/` | Создать (только дилеры) |
| `GET` | `/api/v1/vehicles/{id}/` | Детали |
| `GET` | `/api/v1/vehicles/makes/` | Все марки |
| `GET` | `/api/v1/vehicles/models/` | Все модели |
| `GET` | `/api/v1/vehicles/vin/{vin}/` | Декодировать VIN |

</details>

<details>
<summary><b>Объявления</b></summary>

| Метод | Endpoint | Описание |
|-------|----------|----------|
| `GET` | `/api/v1/listings/` | Каталог активных объявлений |
| `POST` | `/api/v1/listings/` | Создать объявление |
| `GET` | `/api/v1/listings/{id}/` | Детали + история цен |
| `GET/POST` | `/api/v1/listings/saved-searches/` | Сохранённые поиски |

</details>

<details>
<summary><b>Запросы · Сравнение · Финансирование</b></summary>

| Метод | Endpoint | Описание |
|-------|----------|----------|
| `POST` | `/api/v1/inquiries/` | Запрос продавцу |
| `POST` | `/api/v1/inquiries/test-drives/` | Заявка на тест-драйв |
| `POST` | `/api/v1/comparisons/` | Создать сравнение |
| `GET` | `/api/v1/comparisons/{id}/` | Результат сравнения |
| `POST` | `/api/v1/financing/calculate/` | Расчёт платежа |
| `POST` | `/api/v1/financing/apply/` | Заявка на кредит |

</details>

### Celery-задачи (listings)

| Задача | Расписание | Действие |
|--------|------------|----------|
| `expire_stale_listings` | Ежедневно | Перевод просроченных объявлений в `expired` |
| `send_saved_search_notifications` | По расписанию | Email при новых совпадениях |
| `update_listing_statistics` | Периодически | Синхронизация счётчиков запросов |

### Внешние интеграции

| Сервис | Назначение |
|--------|------------|
| **NHTSA VPIC API** | Декодирование VIN |
| **SMTP** | Уведомления о сохранённых поисках |
| **Elasticsearch** | Индексация и быстрый поиск объявлений |

---

## 13. Мониторинг и эксплуатация

### Healthchecks

Все критичные сервисы в `docker-compose.yml` имеют healthcheck:

- **PostgreSQL** — `pg_isready`
- **Redis** — `redis-cli ping`
- **Elasticsearch** — `/_cluster/health`

Backend стартует только после успешных проверок зависимостей (`depends_on: condition: service_healthy`).

### Логи

```bash
make logs                  # Весь стек
make logs-backend          # API-запросы, ошибки Django
make logs-celery           # Фоновые задачи
docker compose logs -f nginx
```

### Рекомендации для production

| Область | Рекомендация |
|---------|--------------|
| **БД** | Регулярные бэкапы `postgres_data`, connection pooling (PgBouncer) |
| **Redis** | Persistence AOF, отдельный инстанс для Celery |
| **Elasticsearch** | Кластер ≥3 нод, включить security (xpack) |
| **Медиа** | S3-совместимое хранилище вместо локального volume |
| **SSL** | Terminate TLS на Nginx, редирект HTTP → HTTPS |

---

## 14. CI/CD

> Pipeline в репозитории подготавливается. Рекомендуемый workflow:

```yaml
# .github/workflows/ci.yml (рекомендуемая структура)
name: CI
on: [push, pull_request]
jobs:
  backend:
    steps:
      - make lint
      - make test-cov
  frontend:
    steps:
      - npm run lint
      - npm test -- --watchAll=false
  docker:
    steps:
      - docker compose build
      - docker compose up -d
      - make migrate
```

### Чеклист перед деплоем

- [ ] `DJANGO_SETTINGS_MODULE=config.settings.production`
- [ ] Уникальный `SECRET_KEY`, сильные пароли БД
- [ ] `DEBUG=False`
- [ ] `ALLOWED_HOSTS` и `CORS_ALLOWED_ORIGINS` настроены
- [ ] HTTPS в Nginx
- [ ] `make collectstatic`
- [ ] SMTP для email-уведомлений

---

## 15. Безопасность и хранение файлов

### Аутентификация и авторизация

- **JWT** (access + refresh) через `djangorestframework-simplejwt`
- Роли: `buyer`, `dealer`, `admin` — permissions на уровне DRF
- CORS ограничен списком `CORS_ALLOWED_ORIGINS`

### Хранение файлов

| Тип | Путь | Лимит |
|-----|------|-------|
| Фото ТС | `media/vehicles/` | `MAX_UPLOAD_SIZE_MB` (10 MB) |
| Аватары | `media/avatars/` | то же |
| Static | `staticfiles/` → Nginx `/static/` | — |

Nginx: `client_max_body_size 100M` для загрузки галерей.

### Практики безопасности

- Никогда не коммитьте `.env` в git
- Ротация `SECRET_KEY` и JWT lifetime в production
- Валидация VIN на стороне API перед обращением к NHTSA
- Rate limiting на уровне Nginx/API Gateway (рекомендуется)

---

## 16. Роли компонентов в продакшене

| Компонент | Роль | Масштабирование |
|-----------|------|-----------------|
| **Nginx** | TLS termination, static/media, reverse proxy | Горизонтально за load balancer |
| **Backend (Gunicorn)** | Stateless API, 4 workers по умолчанию | `replicas: N` в orchestrator |
| **Celery Worker** | Email, expiry, статистика | Увеличить `--concurrency` или replicas |
| **Celery Beat** | **Один** инстанс (singleton scheduler) | Только 1 replica |
| **PostgreSQL** | Source of truth | Primary + read replicas |
| **Redis** | Cache + broker | Sentinel / Cluster |
| **Elasticsearch** | Search index | Dedicated cluster |
| **Frontend** | Static build (`npm run build`) | CDN или Nginx `root` |

### Production checklist

```bash
# В .env
DJANGO_SETTINGS_MODULE=config.settings.production
DEBUG=False

make collectstatic
make migrate
# Deploy через orchestrator (Kubernetes, ECS, etc.)
```

---

## 17. Лицензия

Проект распространяется как **проприетарное программное обеспечение**. Все права защищены.

Для получения коммерческой лицензии или white-label развёртывания — свяжитесь с владельцем репозитория.

---

## 18. Поддержка

| Канал | Действие |
|-------|----------|
| **Issues** | [GitHub Issues](https://github.com/NodirOdilov/AutoTrader/issues) — баги и feature requests |
| **Документация API** | http://localhost/api/v1/docs/ после запуска |
| **Makefile** | `make help` — справка по командам |

---

<div align="center">

**AutoTrader** — современный маркетплейс транспортных средств, готовый к масштабированию.

*Сделано с вниманием к архитектуре, DX и production-ready эксплуатации.*


</div>
