# Day 6 — FastAPI Deep Dive

> **Week 2 · Day 6** · ~7 hours · [← Week overview](../week-2-backend-core.md)

## Objective

Move from "FastAPI works" to "I know *why* it works." Today you'll learn the patterns you'll use in every endpoint for the next three weeks: routers for organizing code, dependencies for cross-cutting concerns, Pydantic v2 in depth for validation, and a consistent global exception envelope.

## Why this matters

FastAPI looks small until you're three months into a project and your `main.py` has 800 lines. The framework gives you proper primitives — routers, dependencies, exception handlers — and the senior dev expects you to use them from day one. By the end of today, you should be able to add a new resource to the codebase in under 10 minutes because the layout makes it mechanical.

## Concepts

**Routers — splitting the app**

```python
# app/routes/users.py
from fastapi import APIRouter

router = APIRouter(prefix="/users", tags=["users"])

@router.get("/")
async def list_users(): ...

@router.get("/{user_id}")
async def get_user(user_id: int): ...
```

```python
# app/main.py
from app.routes import users, posts, auth

app = FastAPI()
app.include_router(users.router)
app.include_router(posts.router)
app.include_router(auth.router, prefix="/auth")  # nest prefixes
```

Tags become section headers in `/docs`. Use them.

**Dependencies — the most underused feature**

`Depends()` is FastAPI's dependency-injection mechanism. It's not just for DB sessions — it's for *any* logic you want to factor out of handlers.

```python
from fastapi import Depends, HTTPException, Header

async def get_api_key(x_api_key: str = Header()) -> str:
    if x_api_key != settings.api_key:
        raise HTTPException(401, "Invalid API key")
    return x_api_key

@router.get("/secure")
async def secure_route(api_key: str = Depends(get_api_key)):
    return {"ok": True}
```

Dependencies can be **chained** (dependencies of dependencies), **cached per request** (the same `Depends(fn)` returns the same value within one request), and **parameterized** with classes.

You'll see this pattern used for: DB sessions, current user resolution, pagination params, feature flags, request context.

**Pydantic v2 — what's worth knowing**

- **Model config**: `model_config = ConfigDict(from_attributes=True)` — needed to build response models from ORM objects (replaces v1's `orm_mode`).
- **Field validation**: `email: EmailStr`, `age: int = Field(ge=0, le=150)`, `tags: list[str] = Field(default_factory=list)`.
- **Custom validators**: `@field_validator("name")` for per-field, `@model_validator(mode="after")` for cross-field.
- **Separate request/response models**: `UserCreate` (what the client sends — no `id`), `UserOut` (what we return — has `id`, no password).
- **`model_dump(mode="json")`** — serializes datetimes etc. to JSON-friendly types.

```python
class UserCreate(BaseModel):
    email: EmailStr
    password: str = Field(min_length=12)

class UserOut(BaseModel):
    id: int
    email: EmailStr
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)
```

**Exception handling**

FastAPI's default behavior:
- `HTTPException(status, detail)` → `{"detail": "..."}` body, status set.
- Pydantic validation fail → 422 with a detailed `detail: [...]` array.

For consistency across services, replace these with one envelope:

```python
class ErrorEnvelope(BaseModel):
    error: dict[str, str]  # {"code": "USER_NOT_FOUND", "message": "..."}

@app.exception_handler(HTTPException)
async def http_exception_handler(request, exc):
    return JSONResponse(
        status_code=exc.status_code,
        content={"error": {"code": _code_for(exc.status_code), "message": exc.detail}},
    )

@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request, exc):
    return JSONResponse(
        status_code=422,
        content={"error": {"code": "VALIDATION_ERROR", "message": "Invalid request", "details": exc.errors()}},
    )
```

**Project layout (the one we'll keep using)**

```
app/
├── main.py               ← create_app(), middleware, exception handlers
├── config.py             ← Settings
├── deps.py               ← shared dependencies (auth, pagination, ...)
├── exceptions.py         ← custom domain exceptions
├── routes/
│   ├── users.py
│   ├── posts.py
│   └── auth.py
├── schemas/              ← Pydantic request/response models
│   ├── user.py
│   └── post.py
├── services/             ← business logic (no FastAPI imports here)
│   ├── user_service.py
│   └── post_service.py
└── models/               ← (Day 8) SQLAlchemy models
```

The rule that holds this together: **handlers thin, services fat**. Handlers parse requests, call services, format responses. Services contain the real logic and are unit-testable without FastAPI.

## Required reading

1. **FastAPI: Bigger Applications** — https://fastapi.tiangolo.com/tutorial/bigger-applications/
2. **FastAPI: Dependencies** — https://fastapi.tiangolo.com/tutorial/dependencies/ — read all five subsections.
3. **Pydantic v2: Models** — https://docs.pydantic.dev/latest/concepts/models/
4. **Pydantic v2: Fields** — https://docs.pydantic.dev/latest/concepts/fields/
5. **FastAPI: Handling Errors** — https://fastapi.tiangolo.com/tutorial/handling-errors/

## Optional reading

- **Auth0: FastAPI Best Practices** — https://auth0.com/blog/fastapi-best-practices — opinionated take on production patterns.
- **`zhanymkanov/fastapi-best-practices` (GitHub)** — https://github.com/zhanymkanov/fastapi-best-practices — community-curated list.

## Exercises

1. **Refactor Day 5's hello-api** — add the `services/` and `schemas/` directories. Move logic out of `routes/`. Confirm tests still pass.

2. **`/users` resource (in-memory)** — implement full CRUD against an in-memory `dict[int, User]`:
   - `POST /users` — create. Body: `UserCreate`. Returns: `UserOut`, 201.
   - `GET /users` — list with `?limit=20&offset=0` query params (default 20, max 100).
   - `GET /users/{user_id}` — return one. 404 if not found.
   - `PUT /users/{user_id}` — full replace.
   - `PATCH /users/{user_id}` — partial update. Use a `UserUpdate` model with all-optional fields.
   - `DELETE /users/{user_id}` — return 204 No Content.
   - Reject duplicate emails with 409.

3. **Pagination as a dependency** — implement
   ```python
   def pagination(limit: int = Query(20, ge=1, le=100), offset: int = Query(0, ge=0)) -> tuple[int, int]:
       return limit, offset
   ```
   Use it in `GET /users` via `Depends`.

4. **Global error envelope** — register the two exception handlers shown above. Confirm both `HTTPException` and validation failures return the new shape. Update tests to match.

## Common pitfalls

- **Business logic in route handlers** — fine for week-1 toy code, painful by week 4. Put it in `services/`.
- **Reusing one Pydantic model for input and output** — they're nearly always different (input lacks `id`, `created_at`; output lacks `password`). Be explicit.
- **`@app.get` instead of router `@router.get`** — once you've moved to routers, don't mix.
- **Catching exceptions inside handlers and returning custom dicts** — the global handler exists for this. Raise; let it format.
- **Forgetting `response_model=...`** on routes — without it FastAPI returns whatever your function does, including internal fields you didn't mean to expose.

## Self-check

1. What does `Depends` give you that just calling the function wouldn't?
2. Two routes both depend on `get_current_user`. The same request hits both via internal routing. How many times does `get_current_user` actually run? Why?
3. Why is `UserOut` typically a *different* class than `UserCreate`, not the same class with some fields nullable?
4. Show how to validate that `password_confirm` matches `password` on a `UserCreate` model.
5. Your `PATCH /users/{id}` accepts a `UserUpdate` with all optional fields. How do you tell "user explicitly set `email` to null" from "user didn't include `email`"?
6. The global exception handler swallows all exceptions and returns 500. What's wrong with that, and what should you do instead?

## Definition of done

- [ ] `/users` CRUD complete with all 6 endpoints + pagination.
- [ ] `services/` and `schemas/` directories used; routes are thin.
- [ ] Global error envelope live; tests assert on the new shape.
- [ ] Tests cover create-then-get, duplicate-email-409, update, delete, and not-found-404.
- [ ] `/docs` shows clean grouped tags (`users`, `health`, etc.).
- [ ] PR merged.
