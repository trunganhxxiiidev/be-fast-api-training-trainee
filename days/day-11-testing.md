# Day 11 — Automated Testing

> **Week 3 · Day 11** · ~7 hours · [← Week overview](../week-3-advanced.md)

## Objective

Move from "I wrote a few tests on Day 5" to a real test suite that covers the FastAPI + SQLAlchemy app: unit tests for service-layer logic, integration tests against a real Postgres, and at least one end-to-end test that exercises auth + DB + HTTP in one flow.

## Why this matters

Tests aren't about coverage percentages — they're about being able to change code without fear. The senior dev's actual heuristic: "can a junior refactor this module on a Friday afternoon and know if they broke anything?" If the answer is no, the tests aren't doing their job. Today you build that safety net for the codebase you've been growing all week.

## Concepts

**The test pyramid (in two sentences)**

Many fast unit tests at the base. Fewer integration tests in the middle. A handful of slow end-to-end tests at the top. The pyramid shape is a *consequence* of: cheap, isolated tests catch most bugs; expensive, broad tests catch the rest.

**Unit vs integration vs end-to-end**

| Type | What it tests | Speed | Dependencies | Example |
|------|---------------|-------|--------------|---------|
| Unit | Pure logic in one function/class | ms | None | `compute_total(items)` |
| Integration | One slice through ≥2 layers | tens of ms | Real DB (often) | "create user via service, query DB" |
| End-to-end | Full request → response | hundreds of ms | Full stack | "register → login → fetch /me" |

**Test doubles — vocabulary**

- **Stub**: returns a canned value when called.
- **Mock**: a stub that also records calls so you can assert on them.
- **Fake**: a real working implementation that takes shortcuts (e.g. an in-memory dict for a database). Often the best choice.

**When NOT to mock**: when mocking the DB would let bugs through that production would catch. For a Postgres-specific feature (JSONB, transactions, FK cascades), test against real Postgres.

**The transactional rollback pattern (test DB isolation)**

The trick: each test runs in a transaction that gets rolled back at the end. Tests can call `db.commit()` and still see clean DB state next time. This is the modern best practice for async SQLAlchemy with pytest.

```python
# tests/conftest.py
import pytest
import pytest_asyncio
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from httpx import AsyncClient, ASGITransport

from app.main import create_app
from app.db import get_session
from app.models import Base

TEST_DB_URL = "postgresql+asyncpg://postgres:dev@localhost:5432/app_test"

@pytest_asyncio.fixture(scope="session")
async def engine():
    eng = create_async_engine(TEST_DB_URL)
    async with eng.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)
    yield eng
    await eng.dispose()

@pytest_asyncio.fixture
async def db_session(engine):
    async with engine.connect() as conn:
        trans = await conn.begin()
        async_session = AsyncSession(bind=conn, join_transaction_mode="create_savepoint")
        yield async_session
        await async_session.close()
        await trans.rollback()

@pytest_asyncio.fixture
async def client(db_session):
    app = create_app()
    async def override_get_session():
        yield db_session
    app.dependency_overrides[get_session] = override_get_session
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as c:
        yield c
```

The key bit: `join_transaction_mode="create_savepoint"`. Even if your code calls `session.commit()`, the outer transaction is still open and gets rolled back. Tests stay isolated.

**A test that uses both fixtures**

```python
# tests/test_users.py
import pytest

@pytest.mark.asyncio
async def test_register_then_login(client):
    r = await client.post("/auth/register", json={
        "email": "a@b.com", "password": "supersecret-123", "name": "Alice"
    })
    assert r.status_code == 201

    r = await client.post("/auth/login", data={
        "username": "a@b.com", "password": "supersecret-123"
    })
    assert r.status_code == 200
    token = r.json()["access_token"]

    r = await client.get("/users/me", headers={"Authorization": f"Bearer {token}"})
    assert r.status_code == 200
    assert r.json()["email"] == "a@b.com"
```

**Parametrize for table-driven tests**

```python
@pytest.mark.parametrize("password,expected_status", [
    ("short", 422),               # too short — Pydantic rejects
    ("nouppercase123", 201),      # currently passes
    ("a" * 200, 201),             # very long — accept
])
@pytest.mark.asyncio
async def test_password_validation(client, password, expected_status):
    r = await client.post("/auth/register", json={"email": f"{password[:5]}@x.com", "password": password, "name": "X"})
    assert r.status_code == expected_status
```

**Coverage**

```bash
uv add --dev pytest-cov
uv run pytest --cov=app --cov-report=term-missing
```

Aim for ~70–80% on `app/services/` (real logic). Don't obsess about 100% — covered code isn't necessarily *tested* code, and some lines (logging, glue) genuinely don't need tests.

## Required reading

1. **pytest docs — How to write and report assertions** — https://docs.pytest.org/en/stable/how-to/assert.html
2. **pytest docs — Fixtures** — https://docs.pytest.org/en/stable/explanation/fixtures.html
3. **Praciano: FastAPI + async SQLAlchemy 2.0 with pytest done right** — https://praciano.com.br/fastapi-and-async-sqlalchemy-20-with-pytest-done-right.html — the rollback pattern.
4. **Martin Fowler: The Practical Test Pyramid** — https://martinfowler.com/articles/practical-test-pyramid.html

## Optional reading

- **pytest-asyncio docs** — https://pytest-asyncio.readthedocs.io/en/latest/
- **Weird Sheep Labs: async testing with FastAPI and pytest** — https://weirdsheeplabs.com/blog/fast-and-furious-async-testing-with-fastapi-and-pytest
- **FastAPI: Testing** — https://fastapi.tiangolo.com/tutorial/testing/

## Exercises

1. **Test DB setup**
   - Add a `postgres-test` service to `docker-compose.yml` (or use a separate database in the same Postgres instance).
   - Create the test database manually: `createdb app_test`.
   - Implement the `conftest.py` fixtures shown above. Verify a trivial test runs end-to-end.

2. **Unit tests** — write tests for at least one service module without touching the DB or HTTP. Use a fake repository (in-memory dict).

3. **Integration tests** — for the user and post services, write 5+ tests each that hit the real DB through the session fixture. Cover:
   - Happy path
   - Constraint violations (duplicate email, missing FK)
   - Update behavior
   - Cascade delete (deleting a user removes their posts)

4. **End-to-end auth flow test** — the example above is a starting point. Extend it to also create a post after login, fetch it back, and delete it.

5. **Coverage report**
   - Add `pytest-cov`.
   - Configure `[tool.pytest.ini_options]` and `[tool.coverage.run]` in `pyproject.toml`.
   - Run with `--cov=app --cov-report=term-missing`.
   - Look at the uncovered lines. For each, decide: worth testing, or genuinely uninteresting? Write that decision in your journal.

6. **Find a real bug with a test** — go through your codebase and find one edge case that nothing tests for. Write the test. If it passes, good — you found a quietly-correct line. If it fails, even better — you found a real bug. Either way, commit the test.

## Common pitfalls

- **Tests that depend on each other** — `test_b` only works if `test_a` ran first. The rollback fixture above prevents this; never store cross-test state in module-level variables.
- **Mocking what you don't own** — mocking `psycopg2.connect` means your tests will keep passing if a real DB change breaks production. Use real DBs for integration tests.
- **Reading from real data sources** in tests (S3, external APIs) — flaky, slow. Stub at the boundary; integration-test in CI against test fixtures.
- **One mega-test that asserts 20 things** — when it fails you don't know which assertion. Split into smaller tests.
- **Forgetting that `expire_on_commit=False` matters in tests too** — without it, the session expires attributes after each commit and you get `DetachedInstanceError`.
- **Coverage as a target** — "we need 90% coverage" leads to gaming. Use it as a guide; trust your judgment about what to test.

## Self-check

1. Why use a real Postgres for integration tests, not SQLite?
2. The rollback fixture uses `join_transaction_mode="create_savepoint"`. Why is that detail load-bearing?
3. You wrote 50 tests. They all pass. What's still wrong if they all use the same fixture data?
4. When would you mock instead of using a real dependency?
5. Coverage shows a 100% covered line that has a bug. How is that possible?
6. Your tests pass locally but fail in CI. What are the most common reasons?

## Definition of done

- [ ] `tests/conftest.py` with engine, session, and client fixtures using the rollback pattern.
- [ ] ≥10 tests total covering unit, integration, and end-to-end levels.
- [ ] At least one test added because you found a real bug or edge case.
- [ ] Coverage on `app/services` ≥ 70%.
- [ ] `uv run pytest -v` passes in under 30 seconds.
- [ ] PR merged.
