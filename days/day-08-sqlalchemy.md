# Day 8 — SQLAlchemy 2.0

> **Week 2 · Day 8** · ~7 hours · [← Week overview](../week-2-backend-core.md)

## Objective

Convert yesterday's hand-written SQL into SQLAlchemy 2.0 models with the typed `Mapped` style, run them with async sessions in FastAPI, and learn to *see* the SQL the ORM is generating so you can spot N+1 queries before they ship.

## Why this matters

SQLAlchemy is the most popular Python ORM. The 2.0 release in 2023 was a major rewrite — many tutorials online still show the old 1.x style. Knowing which is which saves hours of confusion. The typed style we'll use gives you IDE autocomplete, mypy support, and clearer code. The async session integration with FastAPI is what makes this stack hold up under load.

## Concepts

**The 2.0 typed declarative style**

```python
# app/models/__init__.py
from datetime import datetime
from sqlalchemy import String, ForeignKey, func
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship

class Base(DeclarativeBase):
    pass

class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True)
    email: Mapped[str] = mapped_column(String(255), unique=True, index=True)
    name: Mapped[str] = mapped_column(String(120))
    created_at: Mapped[datetime] = mapped_column(server_default=func.now())

    posts: Mapped[list["Post"]] = relationship(back_populates="author", cascade="all, delete-orphan")

class Post(Base):
    __tablename__ = "posts"

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), index=True)
    title: Mapped[str] = mapped_column(String(200))
    body: Mapped[str]
    created_at: Mapped[datetime] = mapped_column(server_default=func.now())

    author: Mapped["User"] = relationship(back_populates="posts")
```

What's different from 1.x:
- `Column("name", String(120))` → `Mapped[str] = mapped_column(String(120))`.
- Type comes from the annotation, not the column.
- Nullable: `Mapped[str | None]`.
- Relationships use the same `Mapped[...]` style and benefit from forward-reference strings.

**Async engine and session — the FastAPI pattern**

```python
# app/db.py
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from typing import AsyncGenerator

engine = create_async_engine(settings.database_url, echo=False, pool_size=10)
SessionLocal = async_sessionmaker(engine, expire_on_commit=False)

async def get_session() -> AsyncGenerator[AsyncSession, None]:
    async with SessionLocal() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
```

Wire it as a FastAPI dependency:

```python
from typing import Annotated
SessionDep = Annotated[AsyncSession, Depends(get_session)]

@router.get("/users/{user_id}")
async def get_user(user_id: int, db: SessionDep) -> UserOut:
    user = await db.get(User, user_id)
    if not user:
        raise HTTPException(404, "User not found")
    return user
```

`Annotated[..., Depends(...)]` lets you give the dependency a name (`SessionDep`) you can reuse across routes without repeating `Depends(get_session)` everywhere.

**Connection string**

```
postgresql+asyncpg://user:password@localhost:5432/dbname
```

The driver is `asyncpg`, the fastest async Postgres driver. `pip`/`uv add asyncpg sqlalchemy[asyncio]`.

**Querying — the four patterns you'll use 95% of the time**

```python
from sqlalchemy import select

# 1. Get by primary key
user = await db.get(User, user_id)

# 2. Filter
result = await db.execute(select(User).where(User.email == email))
user = result.scalar_one_or_none()

# 3. List with pagination
result = await db.execute(select(User).order_by(User.id).limit(20).offset(0))
users = result.scalars().all()

# 4. Insert
user = User(email=email, name=name)
db.add(user)
await db.flush()  # populates user.id without committing
```

**The N+1 problem — and how to fix it**

The trap:

```python
# Bad — one query for users, then one query per user for posts
result = await db.execute(select(User))
users = result.scalars().all()
for user in users:
    print(user.posts)  # ← triggers a query EACH ITERATION
```

The fix — eager-load the relationship in a single query:

```python
from sqlalchemy.orm import selectinload

result = await db.execute(select(User).options(selectinload(User.posts)))
users = result.scalars().all()
for user in users:
    print(user.posts)  # ← already loaded, no extra query
```

`selectinload` issues one extra query that pulls all related posts in one batch (using `WHERE user_id IN (...)`).
`joinedload` does a SQL `JOIN`. Use `selectinload` for one-to-many, `joinedload` for many-to-one or one-to-one.

**Turn on SQL logging while learning**

```python
engine = create_async_engine(url, echo=True)
```

This prints every SQL statement to stdout. Leave it on for the first few weeks. You will be horrified by how chatty the ORM is until you internalize the patterns.

## Required reading

1. **SQLAlchemy 2.0 Tutorial** — https://docs.sqlalchemy.org/en/20/tutorial/ — start at "Establishing Connectivity," read through "Working with ORM-Related Objects."
2. **SQLAlchemy: Asynchronous I/O (asyncio)** — https://docs.sqlalchemy.org/en/20/orm/extensions/asyncio.html — the patterns you need for FastAPI.
3. **OneUptime: SQLAlchemy with FastAPI** — https://oneuptime.com/blog/post/2026-01-27-sqlalchemy-fastapi/view — a practical walkthrough of session management.
4. **Async SQLAlchemy 2 step-by-step** — https://dev.to/amverum/asynchronous-sqlalchemy-2-a-simple-step-by-step-guide-to-configuration-models-relationships-and-3ob3

## Optional reading

- **SQLAlchemy: Relationship Loading Techniques** — https://docs.sqlalchemy.org/en/20/orm/queryguide/relationships.html — for when `selectinload` vs `joinedload` isn't obvious.
- **Building Production APIs (Towards AI)** — https://pub.towardsai.net/building-production-ready-apis-with-fastapi-sqlalchemy-and-alembic-a-complete-guide-a4656b7e700c — end-to-end project tour.

## Exercises

1. **Models** — write `app/models/__init__.py` with `User`, `Post`, `Comment` matching yesterday's schema. Use the typed `Mapped` style. Add proper relationships and `cascade` rules.

2. **DB module + dependency** — create `app/db.py` with the engine, `SessionLocal`, and `get_session`. Set up `SessionDep` as shown above.

3. **Wire it up**
   - Add `asyncpg` and `sqlalchemy[asyncio]` deps.
   - Replace your Day 6 in-memory `/users` storage with the database.
   - Add a tiny script `scripts/create_tables.py` that runs `Base.metadata.create_all(engine.sync_engine)` — you'll replace this with Alembic tomorrow, but for now you need *something* to create tables.

4. **Add `/posts` resource** — full CRUD against the DB. Posts belong to users.
   - `POST /posts` — body includes `user_id`, `title`, `body`. Reject with 404 if user doesn't exist.
   - `GET /users/{user_id}/posts` — list a user's posts. **Use `selectinload` so this is one query, not N+1.**

5. **Prove no N+1** — with `echo=True`, hit `GET /users/{id}/posts` and copy the SQL to your journal. There must be exactly 1 or 2 queries (one for the user, one for the posts) — not one per post.

## Common pitfalls

- **Synchronous calls inside async sessions** — `session.query(...)` is the v1 API and won't work on async sessions. Use `await session.execute(select(...))`.
- **`expire_on_commit=True` (default)** — re-reads attributes from the DB after commit, which crashes if the session is closed. Set `expire_on_commit=False` for FastAPI.
- **Accessing relationships outside the session** — once the session is closed, lazy-loaded relationships raise. Either pre-load with `selectinload` or convert to Pydantic models before exiting the request scope.
- **Forgetting to commit** — `db.add(x)` stages but doesn't write. The `get_session` dependency commits at the end; if you bypass it, you must commit yourself.
- **Sharing a session across requests** — sessions are per-request. Never store one as a module global.

## Self-check

1. What's the difference between `db.flush()` and `db.commit()`?
2. You see two queries in the logs when you hit one endpoint: `SELECT users` and `SELECT posts WHERE user_id IN (1, 2, 3)`. Is this an N+1? Why or why not?
3. When would you use `joinedload` instead of `selectinload`?
4. The same session is used by two concurrent requests by mistake. What's the symptom?
5. Why does `expire_on_commit=False` matter in async FastAPI apps?
6. How do you convert a SQLAlchemy `User` model into a Pydantic `UserOut` response?

## Definition of done

- [ ] Models defined with the 2.0 typed style.
- [ ] `/users` CRUD running on the real DB (no in-memory dict).
- [ ] `/posts` CRUD working, including the nested `/users/{id}/posts` listing.
- [ ] SQL logging proves no N+1 on the nested listing.
- [ ] All tests still pass (you may need a test DB — we'll formalize that on Day 11).
- [ ] PR merged.
