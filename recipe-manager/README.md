# Recipe Manager

A self-hosted web app for personal recipes, running on a home server.

## Features

- **Recipes** with grouped ingredients, numbered steps, notes, servings and a photo
- **Tags** to organise recipes and browse by tag; **search** by name
- **AI recipe scanner**: photograph a recipe and a vision model (any OpenAI-compatible API) fills in the form
- **Meal planner** for the week
- **Backups**: daily database dump, JSON export and photo archive, copied to Google Drive

## Stack

Python 3.11, FastAPI, Jinja2 and Bootstrap 5, SQLAlchemy 2 with Alembic migrations, MySQL 8.0. It runs in Podman on the server and Docker Compose for development.

## Documentation

| | |
|---|---|
| [DEPLOY.md](DEPLOY.md) | Installing, updating and running it on the server (Podman + Quadlet) |
| [BACKUP.md](BACKUP.md) | What's backed up, the schedule, Google Drive, restoring, restore test |
| [CLAUDE.md](CLAUDE.md) | Architecture and code conventions |

## Local development

Requires Docker with Compose.

```bash
cp .env.example .env   # optional; add AI_API_KEY to try the scanner
docker compose up --build -d
```

Open `http://localhost:8010`. The code in `app/` is mounted into the container and reloads on save. `docker compose down` stops everything; add `-v` to also delete the dev database.

`docker-compose.yml` is for development only. The server uses the units in `deploy/quadlet/`.

## Tests

```bash
python3.11 -m venv .venv
.venv/bin/pip install -r requirements-dev.txt
.venv/bin/pytest
```

The tests use SQLite, so they don't need MySQL or Docker. The planner date tests also need Node; they're skipped if it isn't installed.

## Project layout

```
app/                  FastAPI application
  main.py             routes
  crud.py             database operations
  models.py           SQLAlchemy models
  schemas.py          Pydantic schemas
  ai_service.py       AI recipe scanner
  migrations/         Alembic migrations (run automatically at startup)
  templates/, static/ pages, CSS and JavaScript
backup_app.py         backup script
import_recipes.py     restore/update recipes from a JSON export
deploy/quadlet/       Podman Quadlet units and settings templates for the server
deploy/systemd/       daily backup timer
tests/                pytest suite
docker-compose.yml    local development
```
