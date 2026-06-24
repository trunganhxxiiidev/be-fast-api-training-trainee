# Day 10 Auth Notes

## Auth Flow

```text
POST /auth/register
  -> hash password with bcrypt
  -> save users.password_hash
  -> return UserOut without password_hash

POST /auth/login
  -> OAuth2PasswordRequestForm(username, password)
  -> generic 401 for missing user or wrong password
  -> create JWT with sub, role, iat, exp

GET /users/me
  -> Authorization: Bearer <token>
  -> decode JWT with algorithms=["HS256"]
  -> load current user from DB
```

## Authorization

Admin-only delete uses dependency:

```python
_admin: Annotated[User, Depends(require_admin)]
```

Meaning:

- No token or invalid token: `401`.
- Valid token but role is not `admin`: `403`.
- Valid admin token: route body runs.

## Migration

Migration `ffb29e3dd7c8` replaces plaintext `users.password` with `users.password_hash`.

Safe pattern:

1. Add nullable `password_hash`.
2. Backfill existing rows with bcrypt placeholder hash.
3. Alter `password_hash` to `NOT NULL`.
4. Drop plaintext `password`.

## Verification

```bash
cd journal/fastapi-hello-world
rm -f /tmp/day10_verify.db
DATABASE_URL=sqlite+aiosqlite:////tmp/day10_verify.db DATABASE_ECHO=false uv run alembic upgrade head
DATABASE_URL=sqlite+aiosqlite:////tmp/day10_verify.db DATABASE_ECHO=false uv run alembic current
DATABASE_URL=sqlite+aiosqlite:////tmp/day10_verify.db DATABASE_ECHO=false uv run alembic downgrade -1
DATABASE_URL=sqlite+aiosqlite:////tmp/day10_verify.db DATABASE_ECHO=false uv run alembic upgrade head
DATABASE_URL=sqlite+aiosqlite:////tmp/day10_verify.db DATABASE_ECHO=false uv run alembic check
uv run pytest
uv run ruff check .
```

Kết quả:

- `alembic current`: `ffb29e3dd7c8 (head)`.
- `alembic check`: `No new upgrade operations detected.`
- `pytest`: `25 passed`, có 2 warnings từ dependencies.
- `ruff`: `All checks passed!`
