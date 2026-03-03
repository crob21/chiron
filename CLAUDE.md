# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## What This Is

Chiron is an AI fitness mentor: a FastAPI backend that syncs workout data from TrueCoach and nutrition data from MyFitnessPal, then exposes both as context to Google Gemini (`gemini-1.5-pro`) via function calling. Users interact through `chiron_client.py` (async Python) or the REST API directly.

## Commands

### Run the server
```bash
# Development (with auto-reload)
uvicorn main:app --reload

# Or via Python
python main.py
```

### Docker (easiest local setup)
```bash
cp .env.example .env   # fill in your keys
docker-compose up
```

### Database setup
```bash
python scripts/init_db.py          # Initialize tables
python scripts/create_user.py <email>  # Create a user (returns user ID + API key)
```

### Integration test
```bash
# Requires a running server and CHIRON_USER_ID / CHIRON_API_KEY env vars
python scripts/test_integration.py
```

No test suite, no linter configuration, no Alembic migrations configured.

## Architecture

```
main.py          FastAPI app + APScheduler (sync_all_users every 30 min)
config.py        Pydantic-settings, loaded via @lru_cache get_settings()
database/db.py   SQLAlchemy engine + SessionLocal + get_db() dependency
models/          SQLAlchemy ORM models (User, Workout, Nutrition)
api/routes.py    All REST endpoints under /api/v1
services/        External integrations (TrueCoach, MyFitnessPal, Gemini)
tasks/sync.py    Background sync logic called by APScheduler
chiron_client.py Standalone async client with embedded Gemini function calling
```

**AI chat data flow:**
1. User sends message to `ChironChat.send_message()` or `POST /api/v1/chat`
2. Gemini receives it with tool definitions: `get_todays_fitness`, `get_weekly_fitness`, `get_fitness_trends`
3. Gemini issues a function call → client hits the REST endpoint → JSON fed back as `FunctionResponse`
4. Gemini generates a natural-language answer grounded in real data

## Environment Variables

| Variable | Required | Default |
|---|---|---|
| `DATABASE_URL` | no | `postgresql://localhost:5432/chiron` |
| `GEMINI_API_KEY` | yes | — |
| `API_SECRET_KEY` | yes | — |
| `TRUECOACH_CLIENT_ID` | no | `""` |
| `TRUECOACH_CLIENT_SECRET` | no | `""` |
| `SYNC_INTERVAL_MINUTES` | no | `30` |
| `LOG_LEVEL` | no | `INFO` |

`LOG_LEVEL=DEBUG` also enables SQLAlchemy query echo.

## Key Patterns and Gotchas

**Authentication**: All API endpoints require `?api_key=<uuid>` as a query parameter — not a header. User IDs and API keys are UUID strings generated at user creation.

**Schema management**: Tables created at startup via `Base.metadata.create_all()` in the `lifespan` handler. Alembic is in `requirements.txt` but completely unconfigured — no migration files exist. Schema changes require manual SQL or drop/recreate.

**Sync deduplication**: TrueCoach workouts deduplicated by `external_id`. MyFitnessPal nutrition by `(user_id, date)`. Both use query-first then update-or-insert.

**Background task sessions**: `get_db()` is a FastAPI dependency for request-scoped sessions. Background sync tasks create their own `SessionLocal()` directly since they run outside the request lifecycle.

**MyFitnessPal is a stub**: `services/mfp.py` `authenticate()` logs a warning and returns `False`. `get_nutrition()` returns zeros. Sync appears to work but produces no data silently.

**TrueCoach OAuth is incomplete**: `/auth/truecoach` and `/auth/truecoach/callback` return stub JSON. Token exchange logic exists in `TrueCoachClient` but is never wired to store tokens on the `User` record.

**CORS is wide open**: `allow_origins=["*"]` in `main.py` — must be locked down before production.

**`Workout.exercises`**: Stored as an unvalidated `JSON` column containing a list of exercise dicts from TrueCoach. No sub-model or schema enforcement.
