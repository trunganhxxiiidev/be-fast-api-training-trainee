# Day 13 — Docker & docker compose

> **Week 3 · Day 13** · ~6 hours · [← Week overview](../week-3-advanced.md)

## Objective

Containerize the FastAPI service with a small, secure multi-stage Dockerfile. Stand up the whole stack — app + Postgres + Redis — with one `docker compose up` command. Understand layers, caching, and why your production image shouldn't ship build tools.

## Why this matters

"Works on my machine" is the first lie in software. Docker is how teams agree on what "the machine" looks like. Beyond that, the patterns here — multi-stage builds, non-root users, healthchecks, `.dockerignore` — are the difference between a 1.2 GB image with a giant attack surface and a 150 MB image that boots in 2 seconds. Tomorrow you'll deploy this image to AWS; today you make it deployable.

## Concepts

**Image vs container**

An **image** is a layered filesystem snapshot, like a class. A **container** is a running instance, like an object. You build images, you run containers. `docker images` lists images; `docker ps` lists running containers.

**Layers and caching**

Each `RUN`, `COPY`, `ADD` instruction creates a new layer. Docker caches them: if the inputs haven't changed, the layer is reused. The implication: order your Dockerfile from least-changing to most-changing.

```dockerfile
# Bad: app code goes in early, so every code change invalidates the dep install layer
COPY . .
RUN pip install -r requirements.txt
```

```dockerfile
# Good: deps install in a separate layer, cached across code changes
COPY pyproject.toml uv.lock ./
RUN uv sync --frozen --no-dev --no-install-project
COPY app/ ./app/
RUN uv sync --frozen --no-dev  # installs the project itself, fast
```

**Multi-stage builds**

A multi-stage Dockerfile has multiple `FROM` lines. The final stage copies only what it needs from earlier stages. The result: build tools (`gcc`, compilers, build-essentials) never make it into the production image.

```dockerfile
# ─── Stage 1: builder ─────────────────────────────────────
FROM python:3.12-slim AS builder

# uv binary from the official image
COPY --from=ghcr.io/astral-sh/uv:latest /uv /bin/uv

ENV UV_COMPILE_BYTECODE=1 \
    UV_LINK_MODE=copy \
    UV_PYTHON_DOWNLOADS=never

WORKDIR /app
COPY pyproject.toml uv.lock ./

# Install deps into /app/.venv. Cache mount keeps the uv cache across builds.
RUN --mount=type=cache,target=/root/.cache/uv \
    uv sync --frozen --no-dev --no-install-project

COPY app/ ./app/
COPY migrations/ ./migrations/
COPY alembic.ini ./

RUN --mount=type=cache,target=/root/.cache/uv \
    uv sync --frozen --no-dev

# ─── Stage 2: runtime ─────────────────────────────────────
FROM python:3.12-slim AS runtime

# Non-root user
RUN groupadd -r app && useradd -r -g app app

WORKDIR /app
COPY --from=builder --chown=app:app /app /app

ENV PATH="/app/.venv/bin:$PATH" \
    PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1

USER app
EXPOSE 8000

HEALTHCHECK --interval=30s --timeout=3s --start-period=10s --retries=3 \
    CMD python -c "import urllib.request, sys; sys.exit(0) if urllib.request.urlopen('http://localhost:8000/health').status == 200 else sys.exit(1)"

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

What this gets you:
- `python:3.12-slim` instead of `python:3.12` — ~80 MB smaller.
- Build tools and the uv cache stay in the builder stage.
- Runs as non-root (`USER app`). If your container is compromised, the attacker isn't root.
- A healthcheck so Docker (and orchestrators) know if the app is alive.
- `--mount=type=cache` keeps the uv cache across builds without baking it into the image.

**`.dockerignore`**

```
.git/
.venv/
__pycache__/
*.pyc
.pytest_cache/
.ruff_cache/
.env
.env.*
*.md
tests/
```

Without this, `COPY . .` ships your `.venv`, `.git`, secrets, and test fixtures into every image. `.dockerignore` is read at build time and skips matched paths.

**`docker compose` — the dev stack**

```yaml
# docker-compose.yml
services:
  api:
    build: .
    ports:
      - "8000:8000"
    environment:
      DATABASE_URL: postgresql+asyncpg://postgres:dev@db:5432/app
      REDIS_URL: redis://cache:6379/0
      JWT_SECRET: dev-only-not-for-prod
    depends_on:
      db:
        condition: service_healthy
      cache:
        condition: service_started
    # Dev convenience: bind-mount code so reloads work
    volumes:
      - ./app:/app/app
    command: uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload

  db:
    image: postgres:16
    environment:
      POSTGRES_PASSWORD: dev
      POSTGRES_DB: app
    ports:
      - "5432:5432"
    volumes:
      - pg_data:/var/lib/postgresql/data
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U postgres"]
      interval: 5s
      timeout: 5s
      retries: 5

  cache:
    image: redis:7-alpine
    ports:
      - "6379:6379"

volumes:
  pg_data:
```

Bring it up: `docker compose up -d`. Tear down: `docker compose down` (keeps volumes), `docker compose down -v` (also removes volumes).

**The startup-order detail**: `depends_on` only waits for the container to *start*, not for the service inside to be ready. The `condition: service_healthy` clause makes the API actually wait for Postgres to accept connections. Skipping this gives you the famous "connection refused on first boot" bug.

## Required reading

1. **Docker: Best practices for writing Dockerfiles** — https://docs.docker.com/build/building/best-practices/
2. **OneUptime: Containerize a FastAPI Application with Docker** — https://oneuptime.com/blog/post/2026-02-08-how-to-containerize-a-fastapi-application-with-docker/view
3. **Digon.io: Build Multistage Python Docker Images Using UV** — https://digon.io/en/blog/2025_07_28_python_docker_images_with_uv — the canonical reference for the uv pattern.
4. **Docker Compose reference** — https://docs.docker.com/compose/compose-file/

## Optional reading

- **`hadolint`** — https://github.com/hadolint/hadolint — Dockerfile linter. Run it in CI.
- **Snyk: 10 best practices to build a Java container with Docker** — concepts apply to any language. Search "container best practices."
- **Slimmer FastAPI Docker images** — https://davidmuraya.com/blog/slimmer-fastapi-docker-images-multistage-builds

## Exercises

1. **`.dockerignore`** — write the file. Pay attention to never shipping `.git`, `.env`, virtualenvs, or test artifacts.

2. **Dockerfile** — write the multi-stage Dockerfile above. Tweak as needed for your project. Build with:
   ```bash
   docker build -t intern-api:dev .
   ```
   Verify the image size is under 250 MB. Compare with `docker images`.

3. **Run the image standalone** — without compose, just:
   ```bash
   docker run --rm -p 8000:8000 \
     -e DATABASE_URL=postgresql+asyncpg://... \
     -e JWT_SECRET=test \
     intern-api:dev
   ```
   Confirm it boots and responds to `/health`.

4. **docker-compose.yml** — write the compose file with `api`, `db`, `cache`. Use the healthcheck on Postgres. Verify:
   ```bash
   docker compose up -d
   docker compose logs -f api    # follow logs
   curl http://localhost:8000/health
   docker compose down
   ```

5. **Run tests inside the container** — `docker compose run --rm api pytest`. Confirm the suite passes against the Postgres in compose.

6. **Migrations on startup** — make the `api` service's command run `alembic upgrade head` before starting Uvicorn. Verify a fresh `docker compose up` from an empty DB creates tables automatically.

7. **Image size diet** — find one thing in your image you can remove. Document the before/after size in your journal.

## Common pitfalls

- **`COPY . .` before `RUN pip install`** — every code change re-installs deps. Layer order matters.
- **Running as root** — convenient, dangerous. Set `USER` near the end.
- **`latest` tags in production** — non-reproducible builds. Pin versions.
- **Hardcoded ports in `CMD`** — better to read from env so the image is reusable.
- **No healthcheck** — orchestrators can't tell a wedged process from a healthy one.
- **Shipping `.env` files inside the image** — secrets in an image are secrets in your registry. Pass env vars at runtime.
- **`docker compose up` without waiting for the DB to be ready** — first request fails. Use `depends_on: condition: service_healthy`.

## Self-check

1. What's the practical difference between `python:3.12` and `python:3.12-slim`?
2. Why does Docker cache work better when you `COPY pyproject.toml` before `COPY app/`?
3. You change one line in `app/main.py`. How many layers get rebuilt?
4. The container starts but the API can't reach Postgres. Where do you look first?
5. What does `--mount=type=cache,target=/root/.cache/uv` do that copying the cache wouldn't?
6. Your image is 1.4 GB. Walk through three things you'd investigate to shrink it.

## Definition of done

- [ ] `.dockerignore` and multi-stage `Dockerfile` committed.
- [ ] Final image size under 250 MB.
- [ ] Image runs as non-root.
- [ ] `docker compose up -d` brings up api + db + cache.
- [ ] Healthcheck passes on the API container.
- [ ] `docker compose run --rm api pytest` passes.
- [ ] PR merged.
