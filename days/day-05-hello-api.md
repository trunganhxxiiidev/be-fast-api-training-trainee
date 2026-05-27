# Day 5 — Hello API (Week 1 Deliverable)

> **Week 1 · Day 5** · ~6 hours · [← Week overview](../week-1-fundamentals.md) · **Friday deliverable**

## Objective

Turn yesterday's experimental hello-world into a small but *properly structured* FastAPI service with tests, logging middleware, environment-based config, and a real README. This is the artifact you'll demo at the Week 1 review.

## Why this matters

A senior engineer doesn't write code in a single file — they set up structure that makes the next ten files easy to add. Today you practice that. The exercise looks small, but it teaches: project layout, dependency management, environment config, request/response separation, middleware, structured logging, and tests that hit a real HTTP client. Every Week 2 day builds on this scaffolding.

## Spec

Build a FastAPI service named **`hello-api`** that meets all of these:

**Endpoints**

| Method | Path | Behavior |
|--------|------|----------|
| `GET` | `/health` | Returns `{"status": "ok"}`. Status 200. |
| `POST` | `/echo` | Accepts `{"message": str}`. Returns `{"echo": str, "received_at": ISO8601}`. Status 200. |
| `GET` | `/version` | Returns `{"version": str}` read from app config. Status 200. |

**Requirements**
- Bad request bodies on `POST /echo` return 422 with FastAPI's default Pydantic error envelope.
- A middleware logs every request as a single structured log line containing: method, path, status, duration_ms.
- Port comes from `PORT` env var (default 8000). App version from `APP_VERSION` env var (default `0.1.0`).
- Logs go to stdout. No `print()`.
- Tests cover both happy paths and the 422 case.

## Required reading (skim)

1. **FastAPI Tutorial: Bigger Applications** — https://fastapi.tiangolo.com/tutorial/bigger-applications/ — the canonical way to split routes.
2. **FastAPI: Middleware** — https://fastapi.tiangolo.com/tutorial/middleware/ — needed for the request-logging middleware.
3. **Pydantic Settings** — https://docs.pydantic.dev/latest/concepts/pydantic_settings/ — load config from env vars.
4. **`httpx` docs** — https://www.python-httpx.org — for `AsyncClient`, used in tests.

## Project layout

```
hello-api/
├── pyproject.toml
├── uv.lock
├── README.md
├── .env.example
├── .gitignore
├── .pre-commit-config.yaml
├── app/
│   ├── __init__.py
│   ├── main.py              ← app factory + middleware registration
│   ├── config.py            ← Pydantic Settings, reads env
│   ├── logging_setup.py     ← structlog or stdlib JSON config
│   ├── middleware.py        ← RequestLoggerMiddleware
│   ├── schemas.py           ← Pydantic models (EchoRequest, EchoResponse, ...)
│   └── routes/
│       ├── __init__.py
│       ├── health.py
│       ├── echo.py
│       └── version.py
└── tests/
    ├── __init__.py
    ├── conftest.py          ← FastAPI TestClient fixture
    ├── test_health.py
    ├── test_echo.py
    └── test_version.py
```

## Implementation hints

**`app/config.py`**
```python
from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    port: int = 8000
    app_version: str = "0.1.0"
    log_level: str = "INFO"

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")

settings = Settings()
```

**`app/middleware.py`** (sketch)
```python
import time, logging
from starlette.middleware.base import BaseHTTPMiddleware

logger = logging.getLogger("request")

class RequestLoggerMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request, call_next):
        start = time.perf_counter()
        response = await call_next(request)
        duration_ms = (time.perf_counter() - start) * 1000
        logger.info(
            "request_handled",
            extra={
                "method": request.method,
                "path": request.url.path,
                "status": response.status_code,
                "duration_ms": round(duration_ms, 2),
            },
        )
        return response
```

**`tests/conftest.py`**
```python
import pytest
from fastapi.testclient import TestClient
from app.main import create_app

@pytest.fixture
def client():
    app = create_app()
    return TestClient(app)
```

## Exercises (the deliverable itself)

1. **Scaffold** the project with `uv init hello-api && uv add fastapi uvicorn[standard] pydantic-settings`.
2. **Add dev deps**: `uv add --dev pytest httpx ruff pre-commit`.
3. **Implement** the three routes in their own modules and wire them into the app factory.
4. **Add the middleware** and verify logs appear when you `curl` an endpoint.
5. **Write the tests** — at least 2 per route (happy path + one edge case). For `/echo`, the edge case is the 422.
6. **README** with:
   - One-paragraph description.
   - Install: `uv sync`.
   - Run: `uv run uvicorn app.main:app --reload`.
   - Test: `uv run pytest`.
   - Env vars table (`PORT`, `APP_VERSION`, `LOG_LEVEL`) with defaults.
7. **Verify** Swagger UI at `/docs` shows clean models with correct examples.
8. **Open the PR** and request mentor review.

## Common pitfalls

- **Putting everything in `main.py`** — defeats the point of the exercise. Use the layout above.
- **Importing `app` at module top in tests** — couples tests to import-time side effects. Use a `create_app()` factory and a `client` fixture.
- **Logging with f-strings inside `logger.info(...)`** — interpolation happens even if the log level is off. Use `logger.info("event", extra={...})` instead.
- **Reading env vars with `os.getenv` scattered everywhere** — centralize in `Settings`.
- **Forgetting to `.gitignore`** `.env`, `.venv/`, `__pycache__/`, `*.pyc`, `.pytest_cache/`.

## Self-check

1. Why a `create_app()` factory instead of a module-level `app = FastAPI()`?
2. The mentor changes `APP_VERSION=2.0.0` in `.env` and restarts. Walk through how `Settings` picks that up.
3. Your middleware logs `duration_ms`. Where exactly does the timer start and stop?
4. The 422 test asserts on the response shape. What keys does FastAPI's default error envelope contain?
5. Why use `TestClient` (sync) when the app is async? When would you switch to `httpx.AsyncClient` instead?
6. Walk through one request from `curl http://localhost:8000/echo` to the JSON response — every layer it touches.

## Definition of done

- [ ] Project structure matches the layout above.
- [ ] All three endpoints work and are visible in `/docs`.
- [ ] `uv run pytest -v` — at least 6 tests, all passing.
- [ ] `ruff check .` clean.
- [ ] Middleware logs visible in the terminal when hitting endpoints.
- [ ] `.env.example` committed; `.env` ignored.
- [ ] README sufficient for the mentor to run the project from scratch.
- [ ] PR merged after review.

## Week 1 review focus

Demo the running service. Show:
1. The auto-generated `/docs`.
2. A request and its log line.
3. The 422 response for a bad payload.
4. Where you'd add a new endpoint, given your layout.

One concept from the week that didn't click — talk it through with the mentor.
