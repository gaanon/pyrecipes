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

## Tests

```bash
python3.11 -m venv .venv && .venv/bin/pip install -r requirements-dev.txt
.venv/bin/pytest
```

Tests use an in-memory SQLite database (see `tests/conftest.py`), overriding the `get_db` dependency, so no MySQL is needed.

## Dependencies

`requirements.in` lists top-level deps; `requirements.txt` is the fully pinned set the Dockerfile installs (regeneration command in its header). Add or bump deps in `requirements.in`, regenerate, then run the tests.

## Database

MySQL 8.0 runs as the `db` service. The schema is managed by Alembic (`app/migrations/`): on startup, `app/main.py`'s lifespan calls `db_migrate.run_migrations()`, which upgrades to the latest revision. A database created before Alembic (tables present, no `alembic_version` table) is first stamped at `0001_baseline` rather than recreated.

To change the schema, edit `app/models.py`, then generate and review a migration (autogenerate against a scratch SQLite DB, or the real MySQL):

```bash
DATABASE_URL=sqlite:////tmp/scratch.db .venv/bin/alembic upgrade head
DATABASE_URL=sqlite:////tmp/scratch.db .venv/bin/alembic revision --autogenerate -m "describe change"
```

Inside the container: `docker-compose exec app alembic current` / `alembic history`.

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
| `AI_TIMEOUT_SECONDS` | How long to wait for the AI provider before giving up (HTTP 504); defaults to `60` |
| `UPLOAD_DIR` | Folder recipe photos are saved to and served from at `/uploads`; defaults to `uploads` (`/code/uploads` in the container). `backup_app.py` archives the same folder |

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

**Data model:** `Recipe` has one-to-many relationships with `Ingredient`, `Instruction`, and `Note`, all using `cascade="all, delete-orphan"`. Tags use a many-to-many join table (`recipe_tags`) with `Tag` as the canonical tag entity; tags are created on-demand in `crud.create_tag`. Tag lookup is case-insensitive and a recipe links each tag once (`crud._link_tags`). Deleting a recipe keeps its meal-plan entries as custom meals with the recipe's name.

**Photo uploads:** Stored in `UPLOAD_DIR` (`./uploads/`, volume-mounted). Paths saved as `uploads/<uuid>.<ext>` in `Recipe.photo_path`. Served by FastAPI's `StaticFiles` at `/uploads`. A replaced or deleted recipe's photo file is removed after the database commit.

**Saving:** `crud._save_recipe` writes a recipe and all its children in one transaction (rolled back on error, removing any newly uploaded photo). Missing records return 404; malformed form data returns 422.

**Form submission flow:** HTML forms POST JSON-encoded ingredient/instruction/note arrays as hidden fields (serialized by frontend JS), then `main.py` deserializes them with `json.loads()` before building Pydantic schemas.

**AI recipe import:** `POST /api/process-recipe-image` accepts an image upload and sends it base64-encoded (with its real content type) to the configured vision model through the async OpenAI client, so it doesn't block other requests. It returns a pre-filled `RecipeCreate` JSON that the frontend uses to populate the recipe form. Provider errors return 502, timeouts 504, and an answer that isn't a valid recipe 502, each with a `detail` message the page shows. Routes that use the database are plain `def` (FastAPI runs them in a thread pool); only non-DB routes are `async`.

**Meal planner:** JSON API only (`/api/meal-plan` GET/POST/DELETE) — no dedicated UI template, intended to be consumed by a frontend widget.
