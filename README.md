# Smart Travel Companion API

Backend API для планирования путешествий с ИИ-ассистентом. Позволяет создавать поездки, управлять маршрутами, получать контекстные предупреждения и общаться с AI-консьержем.

## 🚀 Features

- **User Authentication**: JWT-based registration and login
- **Trip Management**: Create, update, delete trips with destinations
- **POI & Rules**: Points of interest with contextual rules (mandatory/recommended)
- **AI Route Generation**: Generates optimized daily itineraries based on interests
- **AI Chat Assistant**: WebSocket-based conversational assistant for trip planning
- **Geospatial Support**: PostgreSQL + PostGIS for nearby place searches
- **Multi-day Routing**: Day-by-day itinerary management with sequence optimization

## 🏗 Architecture

```
app/
├── api/          # FastAPI routers (HTTP endpoints)
├── services/     # Business logic layer
├── repositories/ # Data access layer (SQLAlchemy)
├── models/       # SQLAlchemy ORM models
├── schemas/      # Pydantic schemas (validation/serialization)
├── core/         # Security, DB, exceptions, utilities
└── config.py     # Settings management (pydantic-settings)
```

**Pattern**: Clean Architecture with Repository pattern, async/await throughout.

## 📋 Requirements

- Python 3.12+
- PostgreSQL 14+ with PostGIS extension
- UV package manager (recommended) or pip

## ⚡ Quick Start

### 1. Clone & Install

```bash
# Clone repository
cd TRAVEL

# Install dependencies with UV
uv sync

# Or with pip (if requirements.txt is provided)
pip install -r requirements.txt
```

### 2. Configure Environment

```bash
# Copy env template
cp .env.example .env

# Edit .env with your values:
# - DATABASE_URL (PostgreSQL with asyncpg)
# - SECRET_KEY (generate: uv run python -c "import secrets; print(secrets.token_hex(32))")
# - AI_API_KEY (OpenAI-compatible API)
# - GOOGLE_MAPS_API_KEY (optional, for place search)
```

### 3. Database Setup

```bash
# Create PostgreSQL database with PostGIS
createdb travel_db
psql -d travel_db -c "CREATE EXTENSION postgis;"

# Run migrations
uv run alembic upgrade head

# Seed with sample data (China cities, POIs, rules)
uv run python -m scripts.seed
```

### 4. Run Development Server

```bash
uv run uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

API docs available at:
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

## 🔑 Environment Variables

| Variable | Required | Description | Example |
|----------|----------|-------------|---------|
| `DATABASE_URL` | ✅ | PostgreSQL asyncpg connection string | `postgresql+asyncpg://user:pass@localhost:5432/travel_db` |
| `SECRET_KEY` | ✅ | JWT signing secret (32+ chars) | `secrets.token_hex(32)` |
| `ALGORITHM` | ❌ | JWT algorithm | `HS256` |
| `ACCESS_TOKEN_EXPIRE_MINUTES` | ❌ | Token lifetime | `60` |
| `DEBUG` | ❌ | Enable SQL echo & debug mode | `false` |
| `CORS_ORIGINS` | ❌ | Allowed CORS origins (CSV or JSON) | `http://localhost:3000` |
| `AI_API_KEY` | ✅ | AI provider API key | `sk-...` |
| `AI_BASE_URL` | ❌ | AI API base URL | `https://api.openai.com/v1` |
| `AI_MODEL` | ❌ | AI model to use | `gpt-4o-mini` |
| `GOOGLE_MAPS_API_KEY` | ❌ | Google Places API key | `...` |

## 📚 API Endpoints

### Authentication
- `POST /auth/register` — Register new user
- `POST /auth/login` — Login and get JWT token

### Trips
- `GET /trips` — List user's trips
- `POST /trips` — Create new trip
- `GET /trips/{id}` — Get trip details with POIs
- `PUT /trips/{id}` — Update trip
- `DELETE /trips/{id}` — Delete trip

### POIs (Points of Interest)
- `POST /trips/{id}/pois` — Add POI to trip (returns contextual warnings)
- `DELETE /trips/{id}/pois/{poi_id}` — Remove POI from trip

### AI Route Generation
- `POST /trips/{id}/generate` — Generate full route with AI
- `POST /trips/{id}/days/{day}/finalize` — Manual route finalization (user selects POIs)
- `POST /trips/{id}/days/{day}/finalize/auto-main` — Auto-finalize using only "main" POIs

### Chat
- `WS /trips/{id}/chat?token=<jwt>` — WebSocket chat with AI assistant

### System
- `GET /health` — Health check (DB + server status)

## 🧪 Testing

```bash
# Run all tests
uv run pytest

# With coverage
uv run pytest --cov=app --cov-report=html --cov-report=term

# Specific test file
uv run pytest tests/api/test_trips.py -v
```

Tests use a separate test database defined in `TEST_DATABASE_URL`.

## 🗄️ Database Migrations

```bash
# Create new migration after model changes
uv run alembic revision --autogenerate -m "description"

# Apply migrations
uv run alembic upgrade head

# Downgrade one revision
uv run alembic downgrade -1

# Show history
uv run alembic history
```

## 📊 Data Model

### Core Entities

- **User** — account (email + hashed password)
- **Country** — destination country with general rules
- **City** — city within country, belongs to country, has rules
- **POI** — point of interest (attraction, restaurant, etc.) with GPS coordinates
- **Trip** — user's journey (user → country + city + dates)
- **TripPOI** — many-to-many linking POIs to trips with order, day_number, time
- **Rule** — reusable rule text (can belong to Country, City, or POI)
- **CountryRule / CityRule / POIRule** — association tables with `is_strict` flag

### Key Constraints

- **Composite PKs**: `TripPOI` (trip_id+poi_id), rule associations (X_id+rule_id)
- **CHECK constraints**: `end_date >= start_date`, `group_size >= 1`, `sequence_order > 0`
- **ENUMs**: `trip_purpose` (leisure/business/education/other), `budget_level` (low/medium/high), `poi_status` (main/additional)
- **ON DELETE**: CASCADE for dependent objects (cities→POIs, trips→TripPOIs), RESTRICT for countries/trips

## 🔐 Security

- **Passwords**: bcrypt hashing (60-char hash)
- **JWT**: HS256 with configured `SECRET_KEY`, 60-minute expiration
- **Password Policy**:
  - Min 12 characters
  - At least 1 uppercase, 1 lowercase, 1 digit, 1 special char
- **Ownership Checks**: All trip endpoints verify user owns the trip
- **CORS**: Configurable allowed origins
- **Rate Limiting**: 5 requests/minute on `/auth/*` endpoints

## 🤖 AI Integration

### Route Generation (`services/ai.py`)
- Uses OpenAI-compatible API (works with OpenAI, DeepSeek, Groq, etc.)
- Prompt includes all available POIs, city rules, user preferences
- Returns JSON with multi-day structure: main POIs + backup POIs per day
- Fallback to safe empty structure on JSON parse error

### Chat Assistant (`services/chat_agent.py`)
- WebSocket endpoint with JWT auth
- System prompt with trip context and tool calling capabilities
- Tools:
  - `tool_auto_finalize_day` — auto-route optimization for a day
  - `tool_update_trip_info` — change budget/purpose
  - `tool_remove_poi_from_day` — remove a POI from route
- Supports multi-turn conversation with history

## 📍 Geospatial Features

- **PostGIS** geometry column (`POI.geom`) with SRID 4326 (WGS84)
- **Spatial queries**: `ST_DWithin` for nearby POI search
- **Distance calculation**: Haversine formula implemented in Python for TSP
- **Indoor/Outdoor flag**: `POI.is_indoor` used in routing logic

## 🐛 Troubleshooting

### Database connection errors
- Check `DATABASE_URL` is correct and DB is running
- Ensure PostGIS extension: `CREATE EXTENSION postgis;`

### AI generation returns empty
- Verify `AI_API_KEY` and `AI_BASE_URL` are set
- Check AI provider has available quota
- Review server logs for JSON parse errors

### CORS errors in frontend
- Add your frontend URL to `CORS_ORIGINS` in `.env`
- Format: CSV `http://localhost:3000,https://myapp.com` or JSON `'["http://localhost:3000"]'`

### Migrations fail on spatial_ref_sys
- This is a PostGIS system table; migrations should NOT touch it
- Check your alembic version files don't try to drop/create it

### Redis for rate limiting (production)
Replace in-memory limiter with Redis backend:
```python
from slowapi.extension import Limiter
from slowapi.util import get_remote_address
from slowapi.storage import RedisStorage

limiter = Limiter(
    key_func=get_remote_address,
    storage=RedisStorage(redis_url="redis://localhost:6379")
)
```

## 📦 Dependencies

Key packages:
- **fastapi** — web framework
- **sqlalchemy[asyncio]** — ORM with async support
- **asyncpg** — async PostgreSQL driver
- **alembic** — migrations
- **pydantic-settings** — config management
- **bcrypt** — password hashing
- **pyjwt** — JWT tokens
- **geoalchemy2** — PostGIS integration
- **openai** — AI client (OpenAI-compatible)
- **slowapi** — rate limiting
- **httpx** — async HTTP client (maps, AI)

Dev: pytest, pytest-asyncio, httpx

## 🧹 Code Quality

- **Type hints**: Full mypy coverage (mostly)
- **Docstrings**: Google-style for all public methods
- **Error handling**: Custom exception classes with RFC 7807 format
- **Logging**: Standard library logging (configure in production)

## 🔄 Future Improvements

- [ ] Refresh token flow
- [ ] Email verification
- [ ] Password reset
- [ ] User profile with preferences
- [ ] Soft deletes
- [ ] Request ID tracing middleware
- [ ] Structured JSON logging
- [ ] Docker + docker-compose
- [ ] CI/CD pipeline (GitHub Actions)
- [ ] Pre-commit hooks (black, ruff, mypy)
- [ ] API versioning (v1 prefix)
- [ ] Redis caching for AI queries
- [ ] Prometheus metrics
- [ ] OpenTelemetry tracing

## 📄 License

Proprietary. All rights reserved.

---

**Questions?** Open an issue in the repository.
