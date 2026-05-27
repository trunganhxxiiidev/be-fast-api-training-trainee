# Day 9 — Alembic Migrations

> **Week 2 · Day 9** · ~6 hours · [← Week overview](../week-2-backend-core.md)

## Objective

Replace yesterday's `metadata.create_all()` with real migrations. Learn how Alembic compares model state to DB state, what autogenerate gets right and wrong, and how to write a data migration (not just a schema migration) without breaking production.

## Why this matters

Once your service is deployed, you can't `DROP TABLE` and start over. Every schema change has to go through a migration that can be safely applied, rolled back, and re-applied. This is also where most production incidents happen — bad migrations can lock tables for hours, lose data, or fail mid-apply. Today is about respecting the discipline.

## Concepts

**What Alembic is**

Alembic is a migration tool by the SQLAlchemy author. It generates Python scripts that contain `upgrade()` (apply the change) and `downgrade()` (revert it). These scripts live in version control alongside your code.

**Setup**

```bash
uv add alembic
alembic init -t async migrations   # `-t async` uses an async-compatible env.py template
```

This creates:
```
migrations/
├── env.py                ← reads your models + DB config
├── script.py.mako        ← template for new migrations
└── versions/             ← one .py file per migration
alembic.ini               ← config file
```

**Wire it to your models and env**

In `migrations/env.py`, replace the default `target_metadata = None` with:

```python
from app.config import settings
from app.models import Base  # imports Base AND all models

config.set_main_option("sqlalchemy.url", settings.database_url)
target_metadata = Base.metadata
```

Critically, **import every model module** in `app/models/__init__.py` so that they're all registered with `Base.metadata`. Alembic won't auto-discover them.

**The daily commands**

```bash
alembic revision --autogenerate -m "create users and posts"   # writes a new file under versions/
alembic upgrade head                                          # apply all pending migrations
alembic downgrade -1                                          # revert last migration
alembic history --verbose                                     # show all revisions
alembic current                                               # show current applied revision
alembic check                                                 # CI guardrail (1.10+): fails if models drift from migrations
```

**What autogenerate gets right**
- New tables, columns, indexes, foreign keys, unique constraints.
- Type changes (with caveats).
- Column adds/removes.

**What autogenerate gets wrong (and you must fix by hand)**
- **Column renames** — Alembic sees a drop + add. It will literally drop the column and recreate it, losing data. Edit the migration to use `op.alter_column(..., new_column_name=...)`.
- **Enum changes** — `CHECK` constraints often don't autogenerate cleanly.
- **Server-side defaults** — sometimes detected, sometimes not. Verify.
- **Data migrations** — autogenerate never writes data. You write that part.
- **Index renames** — same problem as column renames.

The rule: **always read the generated migration before applying it.** Treat it like AI-generated code.

**The rule you never break**

> Once a migration is committed to `main`, never edit it.

If you need to change it, write a *new* migration that applies the correction. Past collaborators may already have applied the old one.

**Data migrations — when schema and data both change**

Adding a `published_at` column where existing rows should get backfilled from `created_at`:

```python
def upgrade() -> None:
    op.add_column("posts", sa.Column("published_at", sa.DateTime(timezone=True), nullable=True))
    # data migration
    op.execute("UPDATE posts SET published_at = created_at WHERE published_at IS NULL")
    # now safely make it NOT NULL
    op.alter_column("posts", "published_at", nullable=False)

def downgrade() -> None:
    op.drop_column("posts", "published_at")
```

Three steps, one migration. The same pattern works for renames-with-data-copy.

**Migration ordering and multi-head trouble**

Each migration has a `revision` and `down_revision`. They form a DAG. If two devs both branch from the same migration and add new ones, you get "multiple heads":

```bash
alembic merge -m "merge heads" head1 head2   # creates a no-op merge migration
```

In a small team, just talk to each other and avoid this. If it happens, the merge migration above is the standard fix.

**Migrations in deployment**

Two strategies:
1. **Run before app starts** (most common). The deploy script does `alembic upgrade head && uvicorn ...`. Simple, works for small services. Risk: a slow migration delays startup.
2. **Run as a separate step** before traffic is shifted. Required for zero-downtime deploys. We'll touch this on Day 15.

## Required reading

1. **Alembic Tutorial** — https://alembic.sqlalchemy.org/en/latest/tutorial.html — read top to bottom; it's not long.
2. **Alembic: Auto Generating Migrations** — https://alembic.sqlalchemy.org/en/latest/autogenerate.html — read the "What does Autogenerate Detect (and what does it not detect?)" section twice.
3. **Towards AI: Building Production APIs (Alembic section)** — https://pub.towardsai.net/building-production-ready-apis-with-fastapi-sqlalchemy-and-alembic-a-complete-guide-a4656b7e700c — end-to-end walkthrough.

## Optional reading

- **Alembic: Operation Reference** — https://alembic.sqlalchemy.org/en/latest/ops.html — the `op.*` API. Reference, not tutorial.
- **GitHub Discussion: Best practices for large migration sets** — https://github.com/sqlalchemy/alembic/discussions/1259 — for when you eventually have 100+ migrations.

## Exercises

1. **Initialize Alembic** with the async template. Wire `env.py` to use your `Settings` and `Base.metadata`.

2. **First migration**
   - Delete the `create_tables.py` script from Day 8.
   - Drop the existing DB and recreate it empty: `docker exec -i pg psql -U postgres -c "DROP DATABASE app; CREATE DATABASE app;"`.
   - Run `alembic revision --autogenerate -m "initial schema"`.
   - Open the file. Read every line. Confirm it matches your models.
   - `alembic upgrade head`. Confirm tables exist with `\dt` in `psql`.

3. **Schema migration: add a column**
   - Add `published: bool = mapped_column(default=False, server_default="false")` to `Post`.
   - Generate a migration: `alembic revision --autogenerate -m "add published flag to posts"`.
   - Read it. Apply it. Verify with `\d posts`.

4. **Data migration: backfill `published_at`**
   - Add `published_at: Mapped[datetime | None]` to `Post`.
   - Generate the migration. **Edit it** to backfill `published_at = created_at` for all existing rows before making the column `NOT NULL`. Three-step pattern shown above.
   - Apply. Spot-check with a `SELECT`.

5. **Downgrade drill**
   - `alembic downgrade -1`. Verify the column is gone and data is intact for other columns.
   - `alembic upgrade head`. Back to current state.

6. **CI guardrail** — add `alembic check` to your CI workflow (you'll set up CI fully on Day 15). It will fail any PR where the models have changed without a matching migration.

## Common pitfalls

- **Not importing models in `migrations/env.py`** — autogenerate sees an empty `Base.metadata` and proposes dropping every table. Always import them.
- **Editing an applied migration in place** — anyone who's run the old one is now in an inconsistent state. Write a new migration.
- **`UPDATE` in a data migration without a transaction** — Alembic wraps each migration in a transaction by default (good), but make sure your `op.execute` is inside `upgrade()`, not at module scope.
- **Autogenerated migrations that drop a column you renamed** — read every migration before applying. Autogenerate can't read your mind.
- **Forgetting `server_default` on a new `NOT NULL` column on a populated table** — the migration will fail. Add a default, or do the three-step pattern (add nullable → backfill → make NOT NULL).

## Self-check

1. What's the difference between `Base.metadata.create_all()` and `alembic upgrade head`? Why prefer the latter in production?
2. You renamed `user_name` to `name` on the `users` model. Autogenerate produced `drop_column + add_column`. What do you do?
3. You need to make a non-null column on an existing table that has data. Walk through the safe sequence.
4. What does `alembic check` do, and why is it useful in CI?
5. Multiple devs merged migrations to `main` and now `alembic upgrade head` reports "multiple heads." How do you resolve it?
6. Should `downgrade()` always perfectly reverse `upgrade()`? When is it acceptable to leave it as a no-op?

## Definition of done

- [ ] `migrations/` directory committed with at least 3 migrations.
- [ ] `alembic upgrade head` from an empty DB recreates the full schema.
- [ ] At least one data migration shipped (and you can explain it).
- [ ] `alembic downgrade -1 && alembic upgrade head` round-trips cleanly.
- [ ] `alembic check` passes locally.
- [ ] PR merged.
