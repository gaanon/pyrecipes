# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Running the Application

```bash
# Build and start all services (app + MySQL)
docker-compose up --build -d

# View logs
docker-compose logs -f app

# Restart app after code changes (hot-reload is enabled via volume mount)
docker-compose restart app

# Stop everything
docker-compose down
```

The app runs at `http://localhost:8000`. The `app/` directory is volume-mounted, so Python source changes trigger automatic uvicorn reload without rebuilding the image.

## Database

MySQL 8.0 runs as the `db` service. Tables are auto-created at startup via `models.Base.metadata.create_all()` in `app/main.py`'s lifespan handler — there are no migration files.

```bash
# Manual DB backup
docker-compose exec db mysqldump -u root -p'rootpassword' recipe_db > backup.sql

# Connect to MySQL shell
docker-compose exec db mysql -u user -ppassword recipe_db
```

## Environment Variables

| Variable | Purpose |
|---|---|
| `DATABASE_URL` | SQLAlchemy connection string (defaults to the docker-compose MySQL) |
| `OPENAI_API_KEY` | Fallback API key for OpenAI (used if `AI_API_KEY` is not set) |
| `AI_API_KEY` | API key for the AI provider; falls back to `OPENAI_API_KEY` |
| `AI_API_BASE_URL` | Optional base URL for an OpenAI-compatible provider (e.g. Ollama, Groq, OpenRouter); omit to use the default OpenAI endpoint |
| `AI_MODEL` | Model name to use; defaults to `gpt-4o-mini` |

## Architecture

**Stack:** FastAPI + Jinja2 templates + Bootstrap 5 + SQLAlchemy (sync) + MySQL

**`app/` module layout:**
- `main.py` — FastAPI app, route definitions, static/template mounting
- `models.py` — SQLAlchemy ORM models (`Recipe`, `Ingredient`, `Instruction`, `Note`, `Tag`, `RecipeTag`, `MealPlan`)
- `schemas.py` — Pydantic schemas for request/response validation
- `crud.py` — All database operations; update pattern is delete-and-recreate for relationships
- `database.py` — Engine + session factory; `DATABASE_URL` from env
- `ai_service.py` — Calls an OpenAI-compatible vision API to parse a recipe image into a `RecipeCreate` schema; provider, model, and key are configured via env vars
- `utils.py` — Template helpers (e.g., `get_color_from_string` for tag colors)

**Data model:** `Recipe` has one-to-many relationships with `Ingredient`, `Instruction`, and `Note`, all using `cascade="all, delete-orphan"`. Tags use a many-to-many join table (`recipe_tags`) with `Tag` as the canonical tag entity; tags are created on-demand in `crud.create_tag`.

**Photo uploads:** Stored under `./uploads/` (volume-mounted). Paths saved as `uploads/<uuid>.<ext>` in `Recipe.photo_path`. Served by FastAPI's `StaticFiles` at `/uploads`.

**Form submission flow:** HTML forms POST JSON-encoded ingredient/instruction/note arrays as hidden fields (serialized by frontend JS), then `main.py` deserializes them with `json.loads()` before building Pydantic schemas.

**AI recipe import:** `POST /api/process-recipe-image` accepts an image upload, sends it base64-encoded to GPT-4o-mini, and returns a pre-filled `RecipeCreate` JSON that the frontend uses to populate the recipe form.

**Meal planner:** JSON API only (`/api/meal-plan` GET/POST/DELETE) — no dedicated UI template, intended to be consumed by a frontend widget.
