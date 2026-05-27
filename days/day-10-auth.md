# Day 10 — Authentication & Authorization

> **Week 2 · Day 10** · ~7 hours · [← Week overview](../week-2-backend-core.md) · **Friday deliverable**

## Objective

Add real user accounts to the API: registration, login, JWT-based session, and a non-trivial authorization rule (admins can delete other users; regular users can't). Understand the failure modes well enough to spot them in code review.

## Why this matters

Auth is where the highest-impact security bugs live. Plaintext passwords, accepting `alg: none` JWTs, returning generic errors that confirm whether an email exists, timing attacks — these are CVE-grade mistakes that have shipped to production at large companies. The patterns below are battle-tested. The exercise is to apply them, then to explain *why* each piece is the way it is.

## Concepts

**Password hashing**

Never store plaintext. Hash with **bcrypt** or **argon2**. Both are slow on purpose — slowness is what makes a leaked password DB useless to attackers.

```python
from passlib.context import CryptContext

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def hash_password(password: str) -> str:
    return pwd_context.hash(password)

def verify_password(plain: str, hashed: str) -> bool:
    return pwd_context.verify(plain, hashed)
```

`passlib` handles the cost factor (12 by default for bcrypt — adequate as of 2026). The hash includes the salt, so don't store one separately.

**JWT — what it actually is**

A JWT is three base64url-encoded chunks separated by dots:
```
<header>.<payload>.<signature>
```
- **Header**: `{"alg": "HS256", "typ": "JWT"}`
- **Payload**: arbitrary JSON claims. Common ones: `sub` (subject), `exp` (expires-at, Unix timestamp), `iat` (issued-at), `role`.
- **Signature**: HMAC (or RSA) of `<header>.<payload>` using your secret key. This is what proves the token wasn't tampered with.

**Key fact**: the payload is **not encrypted**, only signed. Anyone can decode and read it. Don't put secrets in there.

**Issuing a token**

```python
from datetime import datetime, timedelta, UTC
import jwt  # PyJWT

def create_access_token(user_id: int, role: str, expires_in: timedelta = timedelta(hours=1)) -> str:
    payload = {
        "sub": str(user_id),
        "role": role,
        "iat": datetime.now(UTC),
        "exp": datetime.now(UTC) + expires_in,
    }
    return jwt.encode(payload, settings.jwt_secret, algorithm="HS256")
```

**Verifying a token**

```python
from fastapi import Depends, HTTPException
from fastapi.security import OAuth2PasswordBearer

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/login")

async def get_current_user(
    token: Annotated[str, Depends(oauth2_scheme)],
    db: SessionDep,
) -> User:
    creds_exc = HTTPException(status_code=401, detail="Could not validate credentials",
                              headers={"WWW-Authenticate": "Bearer"})
    try:
        payload = jwt.decode(token, settings.jwt_secret, algorithms=["HS256"])  # ← list, not "HS256"
        user_id = int(payload["sub"])
    except (jwt.InvalidTokenError, KeyError, ValueError):
        raise creds_exc
    user = await db.get(User, user_id)
    if not user:
        raise creds_exc
    return user
```

**The "list, not string" detail** above matters: if you pass `algorithms="HS256"` (a string), some libraries treat each character as a candidate algorithm and a forged `alg: none` token may slip through. Always a list.

**RBAC with a dependency**

```python
def require_role(*allowed_roles: str):
    async def checker(current_user: Annotated[User, Depends(get_current_user)]) -> User:
        if current_user.role not in allowed_roles:
            raise HTTPException(403, "Forbidden")
        return current_user
    return checker

require_admin = require_role("admin")

@router.delete("/users/{user_id}", status_code=204)
async def delete_user(user_id: int, _: Annotated[User, Depends(require_admin)], db: SessionDep):
    ...
```

Note **403 Forbidden** (authenticated but not allowed), not 401 (not authenticated).

**Login endpoint conventions**

```python
@router.post("/login")
async def login(form: Annotated[OAuth2PasswordRequestForm, Depends()], db: SessionDep):
    user = await db.scalar(select(User).where(User.email == form.username))
    if not user or not verify_password(form.password, user.password_hash):
        # Same error for "user not found" and "wrong password"
        # — otherwise you've built an email enumeration oracle.
        raise HTTPException(401, "Incorrect email or password")
    token = create_access_token(user.id, user.role)
    return {"access_token": token, "token_type": "bearer"}
```

`OAuth2PasswordRequestForm` lives at `fastapi.security`. It expects form-encoded `username` and `password` fields (the OAuth2 spec convention), not JSON.

**Refresh tokens — out of scope for week 2**

Long-lived refresh tokens stored server-side are the next step for production apps. For this internship, an access token with a 1-hour expiry is enough; we'll note where you'd add refresh tokens in the design doc later.

## Required reading

1. **FastAPI: OAuth2 with Password (and hashing), Bearer with JWT tokens** — https://fastapi.tiangolo.com/tutorial/security/oauth2-jwt/ — Tiangolo's tutorial is the canonical reference. Read every line.
2. **OWASP: Authentication Cheat Sheet** — https://cheatsheetseries.owasp.org/cheatsheets/Authentication_Cheat_Sheet.html — sections "Password Storage" and "Session Management."
3. **CrackStation: Salted Password Hashing** — https://crackstation.net/hashing-security.htm — explains *why* bcrypt/argon2, not SHA256.

## Optional reading

- **Opcito: FastAPI JWT authentication best setup** — https://www.opcito.com/blogs/flawless-authentication-with-fastapi-and-json-web-tokens — covers refresh tokens and revocation.
- **Stackademic: FastAPI RBAC with JWT** — https://stackademic.com/blog/fastapi-role-base-access-control-with-jwt-9fa2922a088c
- **jwt.io** — https://jwt.io — paste a token to decode and verify it. Useful for debugging.

## Exercises

1. **Schema migration** — add `password_hash` (string, not null) and `role` (string, not null, default `"member"`) to `User`. Generate and apply the migration.

2. **Register endpoint** — `POST /auth/register`
   - Body: `{email, password, name}`.
   - Hash the password before saving.
   - Reject duplicate emails with 409.
   - Returns the new `UserOut` (no password hash in the response, obviously).

3. **Login endpoint** — `POST /auth/login`
   - Accepts `OAuth2PasswordRequestForm`.
   - Returns `{"access_token": "...", "token_type": "bearer"}`.
   - Same generic error for missing user and wrong password.

4. **Current user endpoint** — `GET /users/me`
   - Protected by `get_current_user`.
   - Returns the logged-in user's details.

5. **Admin-only delete** — modify `DELETE /users/{user_id}` to require `role == "admin"`.

6. **Tests** — at minimum:
   - Register → login → call `/users/me` → success.
   - Login with wrong password → 401, generic message.
   - Hit `/users/me` with no token → 401.
   - Hit `/users/me` with an expired token → 401. (Build an expired token in the test using `create_access_token` with a negative expiry.)
   - Non-admin user tries `DELETE /users/{id}` → 403.

## Common pitfalls

- **Storing plaintext passwords** — once. Then you're a cautionary tale forever.
- **`algorithms="HS256"` as a string** — see above. Always a list.
- **Different error messages for "no such user" and "wrong password"** — leaks which emails are registered (account enumeration).
- **JWT secret in source code or git history** — load from env. If a secret is ever committed, it's leaked, even after a force-push.
- **Storing JWT in `localStorage` for frontends** — XSS-vulnerable. `httpOnly` cookies are safer; tradeoff is CSRF risk, which needs its own mitigation.
- **Long expiries** ("90 days" for an access token) — if it leaks, you can't revoke it short of rotating the signing secret (which kicks everyone out). Short expiries + refresh tokens are the pattern.
- **Skipping the `aud` and `iss` claims** when you have multiple services — eventually you'll regret it.

## Self-check

1. Why are bcrypt/argon2 slow on purpose? Why not just SHA-256?
2. Walk through what could go wrong if a JWT's payload could be modified by the client.
3. Why is `algorithms=` a list, not a string?
4. Login fails. Should the response say "user not found" or "incorrect password"? Why?
5. Your JWT secret leaks. What do you have to do? Who is affected?
6. A user logs out. They keep using their token. What happens, and how would a real system prevent that?

## Definition of done

- [ ] Migration adding `password_hash` and `role` columns is applied.
- [ ] Register, login, and `/users/me` endpoints work end-to-end.
- [ ] Tests cover happy path + 3+ failure modes.
- [ ] Admin-only delete enforced via dependency, not inline `if user.role`.
- [ ] No plaintext password ever stored, returned, or logged.
- [ ] JWT secret loaded from env, not hardcoded.
- [ ] PR merged.

## Week 2 review focus

Demo:
1. Register two users (one admin, one member) and log in as both.
2. Show the JWT decoded on `jwt.io`.
3. Show the admin-only delete working for admin, returning 403 for the member.
4. Walk through the auth flow on a whiteboard, sequence-diagram style.

One database design decision from the week you'd defend, and one you'd reconsider — talk it through with the mentor.
