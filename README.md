# Task Tracker

Клиент: **Vue 3**, **TypeScript**, **Vite 5**, **Nuxt UI** (Vue), **TipTap** (редактор с заголовками, списками, кодом, ссылками и изображениями).

Сервер: **FastAPI**, **PostgreSQL**, JWT-авторизация, загрузка изображений для вставки в описание задачи.

## Статусы задач

- Ознакомление (`familiarization`)
- Разработка (`development`)
- Тестирование (`testing`)
- Развёртывание (`deployment`)
- Готово (`done`)

При старте API автоматически выполняется донастройка схемы (`app/schema_patch.py`: колонки `users.avatar_filename`, `users.hourly_rate`, таблица `task_comments`). При желании тот же SQL лежит в `backend/migrations/001_add_profile_and_comments.sql`.

## Запуск базы данных

Без запущенного PostgreSQL API при старте завершится с ошибкой подключения (`ConnectionResetError` / `ConnectionDoesNotExistError`).

Из корня проекта:

```bash
docker compose up -d
```

Проверка: `docker ps` — контейнер `postgres` в статусе `Up`. В `docker-compose.yml` Postgres с хоста доступен на **5433** (внутри контейнера по-прежнему 5432), чтобы не конфликтовать с отдельной установкой PostgreSQL на Windows, которая часто занимает **5432**. В `backend/.env` должен быть `...@localhost:5433/...`.

## Backend

Сначала создайте venv и **обязательно обновите pip** (старый pip 19.x не умеет читать `pyproject.toml` у `cryptography` и падает с `TomlError`).

**Windows (PowerShell):**

```powershell
cd backend
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip setuptools wheel
pip install -r requirements.txt
copy .env.example .env
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

Либо из каталога `backend`: `.\install-deps.ps1`

Рекомендуется **Python 3.10+** (для 3.8 возможны лишние ограничения по зависимостям).

По умолчанию API: `http://localhost:8000`, документация OpenAPI: `/docs`.

## Frontend

```bash
cd frontend
npm install
npm run dev
```

Приложение: `http://localhost:5173`. Запросы к `/api` и `/static` проксируются на backend (см. `vite.config.ts`).

Для продакшена задайте `VITE_API_URL` (полный URL API), если фронт и API на разных доменах.

## Учёт времени

У пользователя может быть активен только один таймер. Старт/стоп вызывают `POST /api/tasks/{id}/time/start` и `.../time/stop`.

## Редактор

Содержимое хранится как JSON TipTap (`content_json`). Изображения загружаются на сервер (`POST /api/upload`) и вставляются в документ по URL.

Рекомендуется **Node.js 20.19+** или **22.12+** (для новых мажорных версий Vite). В проекте зафиксирован **Vite 5** для совместимости с более старыми LTS.
