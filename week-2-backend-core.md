# Week 2 — Backend Core (FastAPI + SQLAlchemy + PostgreSQL)

**Goal:** Build a real REST API with a relational database, migrations, and auth. By Friday the intern should have a CRUD service that a frontend could plausibly hit.

Stack lock-in: **FastAPI** for the web layer, **SQLAlchemy 2.0** for the ORM, **PostgreSQL** for storage, **Alembic** for migrations.

> **Detailed daily lessons** with required reading, exercises, pitfalls, and self-check:
> - [Day 6 — FastAPI Deep Dive](./days/day-06-fastapi-deep-dive.md)
> - [Day 7 — PostgreSQL Fundamentals](./days/day-07-postgresql.md)
> - [Day 8 — SQLAlchemy 2.0](./days/day-08-sqlalchemy.md)
> - [Day 9 — Alembic Migrations](./days/day-09-alembic.md)
> - [Day 10 — Authentication & Authorization (deliverable)](./days/day-10-auth.md)

This page is the **week-at-a-glance**. Click into each day for the full lesson.

---

## Day 6 — FastAPI Deep Dive

**Topics**
- Routers, prefixes, tags — splitting a large app cleanly.
- Pydantic v2 in depth: field validation, model config, custom validators, `model_dump` vs. `dict()`.
- Dependencies (`Depends`) — what they enable beyond just DI (auth, pagination, DB sessions).
- Global exception handlers and a consistent error envelope.
- Project layout — what goes in `app/api`, `app/core`, `app/models`, `app/services`, `app/db`.

**Exercises**
1. Extend last week's Hello API with a `/users` resource: full CRUD against an **in-memory** list (DB comes Day 8).
2. Use Pydantic models for every request/response — no raw dicts in handlers.
3. Add a global exception handler that returns `{"error": {"code": "...", "message": "..."}}` for all 4xx/5xx.
4. Refactor into the recommended project layout.

---

## Day 7 — PostgreSQL Fundamentals

**Topics**
- Installing Postgres locally (Docker is fine; we'll go full Docker next week).
- Tables, primary/foreign keys, indexes, constraints, `NOT NULL`, `UNIQUE`.
- Normalization (1NF → 3NF) at a practical level — not memorized rules.
- Transactions, isolation levels, why `SELECT ... FOR UPDATE` exists.
- `EXPLAIN ANALYZE` — what an index actually does to a query plan.
- `psql` survival: `\dt`, `\d table`, `\df`, `\timing`.

**Exercises**
1. Spin up Postgres (Docker or local). Connect with `psql`.
2. Design a schema for a blog: `users`, `posts`, `comments`, `tags`, `post_tags`. Draw the ER diagram first, then write the `CREATE TABLE` statements by hand.
3. Insert sample data with `INSERT`. Write SQL by hand for: top 5 most-commented posts in the last 7 days.
4. Add an index that improves the query and prove it with `EXPLAIN ANALYZE` (before vs. after).

---

## Day 8 — SQLAlchemy 2.0

**Topics**
- ORM vs. Core — when to use which.
- Declarative models with the 2.0 typed style (`Mapped[...]`, `mapped_column`).
- Sessions and the unit-of-work pattern.
- Relationships: `relationship()`, lazy/eager loading, `selectinload` vs `joinedload`.
- The N+1 problem — how to spot it (turn on SQL logging) and how to fix it.

**Exercises**
1. Convert the Day 6 in-memory `/users` CRUD to SQLAlchemy-backed.
2. Add SQLAlchemy models for `posts` and `comments` with proper relationships.
3. Add `GET /users/{id}/posts` — verify in the SQL log that you're issuing one query, not N+1.
4. Implement a paginated `GET /posts?limit=20&offset=0`.

---

## Day 9 — Alembic Migrations

**Topics**
- Why migrations exist; why you never edit a committed migration.
- `alembic init`, `alembic revision --autogenerate`, `alembic upgrade head`, `alembic downgrade -1`.
- Autogenerate's blind spots — when you must edit by hand (enum changes, constraint renames, data migrations).
- Migration ordering, multi-head warnings, and how to resolve them.
- Seeding test data — keep it out of migrations; use a fixtures script.

**Exercises**
1. Initialize Alembic in the project. Make `alembic upgrade head` recreate the schema on an empty DB.
2. Generate a migration that adds a `published_at` column to `posts`.
3. Write a **data migration** that backfills `published_at` from `created_at` for existing rows.
4. Run `downgrade -1` and confirm the schema reverts cleanly.

---

## Day 10 — Authentication & Authorization

**Topics**
- Password hashing: `bcrypt` / `argon2` (use `passlib`). Why never store plaintext.
- JWT structure (header, payload, signature) — and its real limitations (revocation, size).
- Session-based vs. token-based auth — when to pick which.
- Authorization: role-based (RBAC) vs. attribute-based (ABAC).
- Common pitfalls: timing attacks on login, accepting `alg: none`, storing JWT in `localStorage` for XSS-prone frontends.

**Exercises**
1. Add `POST /auth/register` and `POST /auth/login` to the service.
2. Issue a JWT on login (use `python-jose` or `pyjwt`). Protect `/users/me` with a `Depends(get_current_user)` dependency.
3. Add a `role` enum column to `users` (`member`, `admin`). Make `DELETE /users/{id}` admin-only via a dependency.
4. Write tests covering: wrong password, expired token, missing token, insufficient role.

**Weekly review focus**
- Database design choices for the blog schema — defend the normalization decisions.
- Walkthrough of the auth flow with a sequence diagram drawn live on a whiteboard.
- One SQL query you optimized with an index — show the `EXPLAIN ANALYZE` before/after.
- One security pitfall you almost shipped and how you caught it.
