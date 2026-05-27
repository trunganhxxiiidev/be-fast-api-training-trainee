# Day 18 — Pet Project: Core CRUD + Auth

> **Week 4 · Day 18** · ~8 hours · [← Week overview](../week-4-pet-project.md)

## Objective

Implement the auth flow (register, login, JWT, RBAC dependency) and the primary CRUD resource end-to-end with tests. By end of day, a user should be able to sign up, log in, and exercise the main resource through real HTTP requests.

## Why this matters

This is where the project becomes real. Today's work proves that all the scaffolding from Day 17 actually holds together: routes → services → DB → migrations → tests. If something is wrong with the architecture, you find out *now* — Day 19 is too late.

## Strategy

Pick the **two highest-value paths** through your app and implement them properly with tests. For the three pet project options:

- **URL Shortener** — auth flow + `POST /shorten` + `GET /{code}` (the redirect). Get the lookup cached on Day 19.
- **Task Manager** — auth flow + team creation + task creation under a team. Authorization rule for who can create tasks.
- **Finance Tracker** — auth flow + transaction CRUD. The CSV import comes later.

Whatever you pick: the smallest end-to-end slice that proves the app works. Resist the urge to implement the long tail of endpoints today.

## The auth flow (copy from Day 10)

1. `password_hash` (bcrypt via `passlib`) and `role` columns on the `User` model. Migration applied.
2. `POST /auth/register` — body has `email`, `password`, `name`. Returns 201 with `UserOut`.
3. `POST /auth/login` — `OAuth2PasswordRequestForm`. Returns `{access_token, token_type}`.
4. `get_current_user` dependency — decodes JWT, returns the `User`. Raises 401 on failure.
5. `require_role(*allowed_roles)` dependency factory — raises 403 if the user's role isn't in the list.
6. `GET /users/me` — protected by `get_current_user`. Returns the logged-in user.

This is essentially the same code from Day 10 with the model and schemas adjusted for your project. Don't reinvent.

## The primary resource

Implement the full CRUD with tests:

| Verb | Path | Auth | Status codes |
|------|------|------|--------------|
| POST | `/<resource>/` | logged-in | 201 created, 400/422 bad request, 409 conflict |
| GET | `/<resource>/` | logged-in | 200 with pagination |
| GET | `/<resource>/{id}` | logged-in | 200, 404 |
| PUT | `/<resource>/{id}` | owner or admin | 200, 403, 404 |
| PATCH | `/<resource>/{id}` | owner or admin | 200, 403, 404 |
| DELETE | `/<resource>/{id}` | owner or admin | 204, 403, 404 |

**The non-trivial authorization rule** — required by the spec. Whatever your DESIGN.md says, implement it now via a `Depends`-friendly check, not inline in the handler. Common patterns:

```python
async def require_owner_or_admin(
    resource_id: int,
    current_user: Annotated[User, Depends(get_current_user)],
    db: SessionDep,
) -> Resource:
    resource = await db.get(Resource, resource_id)
    if not resource:
        raise HTTPException(404)
    if resource.owner_id != current_user.id and current_user.role != "admin":
        raise HTTPException(403)
    return resource

@router.delete("/resources/{resource_id}", status_code=204)
async def delete_resource(
    resource: Annotated[Resource, Depends(require_owner_or_admin)],
    db: SessionDep,
):
    await db.delete(resource)
```

## Required reading (skim)

- [Day 06 — FastAPI Deep Dive](./day-06-fastapi-deep-dive.md) — routes thin, services fat. Apply it.
- [Day 10 — Authentication & Authorization](./day-10-auth.md) — auth recipes.
- [Day 11 — Automated Testing](./day-11-testing.md) — the rollback-fixture pattern. Use it.

## Day plan (suggested)

**Morning — Auth (3 hours)**

1. Add `password_hash` and `role` to `User`. Generate + apply migration.
2. Implement `app/services/auth_service.py` with `register_user`, `authenticate_user`, `create_access_token`, `decode_token`.
3. Implement `app/routes/auth.py` — thin, calls into the service.
4. `get_current_user` and `require_role` in `app/deps.py`.
5. Tests for: register success, register duplicate-email-409, login success, login wrong-password-401, `/users/me` with valid/invalid/expired tokens.

**Afternoon — Primary resource (5 hours)**

6. Implement service module for the primary resource.
7. Implement route module (thin handlers).
8. Schemas: separate `<Resource>Create`, `<Resource>Update`, `<Resource>Out`.
9. Authorization rule as a dependency.
10. Tests for: full CRUD happy paths, the authorization rule (allowed user works, disallowed user gets 403), 404 on missing resource.
11. Open the WIP PR; tag the mentor for end-of-day review.

## End-of-day mentor checkpoint

The mentor will look at:
- Route handlers are short (5–15 lines each typically). Logic lives in services.
- Tests cover auth flow + CRUD + the authz rule.
- No plaintext passwords in DB, logs, or responses.
- Migrations apply cleanly from empty DB.
- `docker compose up && pytest` works.

Be ready to demo the auth flow live. Have a `curl` script or Postman collection handy.

## Common pitfalls

- **Implementing all routes shallowly instead of two routes properly** — you'll regret this on Day 19. Depth > breadth.
- **Putting authz logic inline in every handler** — `if user.role != "admin": raise ...` repeated 15 times. Use a dependency.
- **Same Pydantic model for input + output** — leaks fields. Different models for `Create`, `Update`, `Out`.
- **Forgetting to convert SQLAlchemy → Pydantic** — your response model probably needs `model_config = ConfigDict(from_attributes=True)`.
- **Slow tests** — if your test suite is over a few seconds, check whether each test is creating a new engine. Reuse fixtures.
- **`expire_on_commit=True`** — causes `DetachedInstanceError` after returning from the session context.

## Self-check

1. Walk through the request path from `POST /auth/login` to the JSON response. Every layer.
2. Your authz dependency raises 403. Where does that 403 get formatted into the response envelope?
3. A test logs in then calls `/users/me`. It works. Now you add a second test that does the same thing. It fails. Why might that be? (Hint: cleanup.)
4. The mentor asks you to add a second authorization rule. How many places do you change?
5. A user changes their role from `member` to `admin`. Do their existing JWTs reflect the new role? Why or why not?
6. What's the *one* test that, if it broke, would tell you something critical is wrong?

## Definition of done

- [ ] Auth flow works end-to-end: register → login → call protected endpoint.
- [ ] JWT secret in env, not in source.
- [ ] At least 10 tests passing across auth + primary CRUD.
- [ ] Authorization rule implemented as a dependency (not inline).
- [ ] PR up to date, mentor review requested.
- [ ] All migrations apply on a fresh DB.
- [ ] `docker compose run --rm api pytest` passes.
