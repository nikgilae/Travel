# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

**Tourry** is a Smart Travel Companion — a full-stack app for AI-assisted trip planning. Users create trips, AI generates a pool of POIs (Points of Interest) based on preferences, and an AI agent chat helps manage the itinerary.

- **Backend**: FastAPI + PostgreSQL (async SQLAlchemy + asyncpg), Python 3.12+
- **Frontend**: React 19 + Vite (currently minimal — single onboarding page)
- **Package manager**: `uv` (Python), `npm` (frontend)

## Commands

### Backend

```bash
# Run dev server
uv run uvicorn app.main:app --reload

# Run all tests
uv run pytest

# Run a single test file
uv run pytest tests/api/test_auth.py

# Run a single test by name
uv run pytest tests/api/test_trips.py::test_create_trip

# Apply DB migrations
uv run alembic upgrade head

# Generate a new migration after model changes
uv run alembic revision --autogenerate -m "description"

# Seed the database with test data
uv run python -m scripts.seed
```

### Frontend

```bash
cd frontend
npm install
npm run dev      # Vite dev server
npm run build
npm run lint
```

## Architecture

### Backend Layer Structure

Each domain follows: **API router → Service → Repository → ORM Model**

- `app/api/` — FastAPI routers (HTTP layer, request/response only)
- `app/services/` — Business logic; orchestrate multiple repositories; own `session.commit()`
- `app/repositories/` — DB access; all inherit from `BaseRepository` (`app/repositories/base.py`) which provides generic `get_by_id`, `get_all`, `create`, `update`, `delete`; use `flush()` not `commit()` internally
- `app/models/` — SQLAlchemy ORM models (all inherit from `Base` in `app/core/database.py`)
- `app/schemas/` — Pydantic schemas for request/response validation
- `app/core/` — Shared infrastructure: `database.py` (engine, session, `Base`), `security.py` (JWT), `exceptions.py` (custom exceptions), `maps.py` (Google Maps adapter)
- `app/dependencies.py` — `get_current_user` FastAPI dependency (JWT → User ORM object)
- `app/config.py` — `Settings` via pydantic-settings; all env vars accessed via `settings` singleton

### AI Layer (Two Separate Services)

1. **`app/services/ai.py`** (`generate_trip` function) — Stateless call to OpenAI-compatible API. Generates a pool of POIs for a trip based on city POIs from DB, user preferences, and rules. Called by `TripAIService`.

2. **`app/services/chat_agent.py`** (`TravelAgentService`) — Stateful AI agent with tool use. Manages conversation history, injects trip context (current POIs with IDs) into every message, and can call three tools: `tool_update_trip_info`, `tool_auto_finalize_day`, `tool_remove_poi_from_day`. Tools delegate back to `TripService` methods.

Both use `AsyncOpenAI` client pointed at `AI_BASE_URL` (currently proxied to `google/gemini-2.5-flash`).

### Geography & Rules System

- Geography hierarchy: `Country → City → POI`
- Each level can have `Rules` (e.g., visa requirements, cultural norms, POI-specific warnings)
- When a POI is added to a trip, applicable rules are surfaced as warnings — country-level, city-level, and POI-level rules all compose

### Trip & POI Flow

1. User creates a `Trip` (country, city, purpose, budget, group_size, dates)
2. `POST /trips/{id}/generate` — `TripAIService` sends all city POIs + rules to AI, which returns a ranked selection; results saved as `TripPOI` records with `day_number` and `status` (`main`/`additional`)
3. User/AI can finalize days (`auto_finalize_main_pois`), reorder, or remove POIs
4. Chat endpoint (`/chat`) maintains conversation history client-side; each message includes full trip context injected server-side

### Error Handling

Custom exceptions in `app/core/exceptions.py` (`NotFoundException`, `AlreadyExistsException`, `UnauthorizedException`, `ForbiddenException`) are handled globally in `app/main.py` with RFC 7807-style JSON responses.

### Testing

Tests use a real PostgreSQL test database (not mocks). `conftest.py` creates all tables before each test and truncates them after. Fixtures: `db_session`, `client` (ASGI test client with `get_db` overridden), `auth_headers`, `test_user`, `test_country`, `test_city`. Tests require `TEST_DATABASE_URL` in `.env`.

## Environment Setup

Copy `.env.example` to `.env` and fill in:
- `DATABASE_URL` / `TEST_DATABASE_URL` — PostgreSQL with asyncpg driver (`postgresql+asyncpg://...`)
- `SECRET_KEY` — JWT signing key (generate: `uv run python -c "import secrets; print(secrets.token_hex(32))"`)
- `AI_API_KEY` / `AI_BASE_URL` / `AI_MODEL` — OpenAI-compatible endpoint
- `GOOGLE_MAPS_API_KEY` — for `GoogleMapsClient` in `app/core/maps.py`

## Key Conventions

- Repositories use `flush()` (not `commit()`); services own `commit()` after all operations
- All primary keys are UUIDs
- CORS is configured for `localhost:3000` — frontend dev server port
- API docs available at `/docs` (Swagger) and `/redoc` when server is running
