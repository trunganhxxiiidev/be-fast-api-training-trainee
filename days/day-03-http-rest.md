# Day 3 — HTTP & REST

> **Week 1 · Day 3** · ~5 hours · [← Week overview](../week-1-fundamentals.md)

## Objective

Understand HTTP as a protocol, not as "the thing the framework hides from me." By the end of the day you should be able to read a raw HTTP request/response, name status codes from memory for common scenarios, and explain idempotency, safety, and caching headers.

## Why this matters

Every API you build, every bug you debug at the request layer, every authentication flow — all of it sits on top of HTTP. Frameworks abstract it, but they don't replace it. When a request behaves strangely, the answer is almost always in the headers, the status code, or the method semantics. You can't debug what you don't understand.

## Concepts

**Anatomy of an HTTP request**
```
POST /api/v1/users HTTP/1.1
Host: api.example.com
Content-Type: application/json
Authorization: Bearer eyJ...
Content-Length: 47

{"email": "alice@example.com", "name": "Alice"}
```
- **Request line:** method, path (+ query string), protocol version.
- **Headers:** metadata about the request — content type, auth, caching hints, host.
- **Body:** the payload. Empty for `GET`, typically present for `POST`/`PUT`/`PATCH`.

**Anatomy of an HTTP response**
```
HTTP/1.1 201 Created
Content-Type: application/json
Location: /api/v1/users/42
Date: Tue, 27 May 2026 12:00:00 GMT

{"id": 42, "email": "alice@example.com", "name": "Alice"}
```

**Methods and their semantics**

| Method | Safe? | Idempotent? | Typical use |
|--------|-------|-------------|-------------|
| `GET` | ✅ | ✅ | Read |
| `HEAD` | ✅ | ✅ | Metadata only |
| `OPTIONS` | ✅ | ✅ | Capability discovery (CORS) |
| `POST` | ❌ | ❌ | Create / non-idempotent action |
| `PUT` | ❌ | ✅ | Full replace |
| `PATCH` | ❌ | ❌ (typically) | Partial update |
| `DELETE` | ❌ | ✅ | Remove |

- **Safe** = no server state change. **Idempotent** = repeated calls have the same effect as one call.
- `GET /users/5/delete` is a sin — it's a side-effecting action behind a "safe" method.

**Status code categories**

| Range | Meaning | Common ones |
|-------|---------|-------------|
| 1xx | Informational | rare |
| 2xx | Success | 200 OK, 201 Created, 204 No Content |
| 3xx | Redirection | 301 Moved Permanently, 302 Found, 304 Not Modified |
| 4xx | Client error | 400, 401, 403, 404, 409, 422, 429 |
| 5xx | Server error | 500, 502, 503, 504 |

**The codes you'll use a lot** — internalize these:
- **200 OK** — successful response with a body.
- **201 Created** — successful POST that created a resource. Include `Location` header.
- **204 No Content** — successful, no body (often DELETE).
- **400 Bad Request** — malformed request (syntactically).
- **401 Unauthorized** — *not authenticated*. (Misnamed historically — it means "no valid credentials.")
- **403 Forbidden** — authenticated but not allowed.
- **404 Not Found** — resource doesn't exist.
- **409 Conflict** — request can't be applied to current state (e.g. duplicate email on register).
- **422 Unprocessable Entity** — request is syntactically valid but semantically wrong (e.g. negative age). FastAPI uses this for Pydantic validation errors.
- **429 Too Many Requests** — rate limited.
- **500 Internal Server Error** — your bug.
- **502/503/504** — gateway / unavailable / timeout. Usually upstream issues.

**Caching headers (one-pager)**
- `Cache-Control: max-age=3600` — cache for 1 hour.
- `ETag: "abc123"` — opaque version identifier. Client can send `If-None-Match: "abc123"` on a follow-up; server replies `304 Not Modified` if unchanged.
- `Last-Modified` / `If-Modified-Since` — older mechanism, same idea.

**CORS in one paragraph**
- Browsers enforce same-origin policy on JS fetches.
- Your API can opt-in by returning `Access-Control-Allow-Origin` and friends.
- "Preflight" requests are `OPTIONS` requests browsers send before non-simple requests.
- It's a *browser* concern. `curl` and server-to-server calls ignore it.

## Required reading

1. **MDN: An overview of HTTP** — https://developer.mozilla.org/en-US/docs/Web/HTTP/Overview
2. **MDN: HTTP request methods** — https://developer.mozilla.org/en-US/docs/Web/HTTP/Methods
3. **MDN: HTTP response status codes** — https://developer.mozilla.org/en-US/docs/Web/HTTP/Status — skim the full list; bookmark it.
4. **REST API Tutorial: HTTP Status Codes** — https://restfulapi.net/http-status-codes/ — short, opinionated, useful.

## Optional reading

- **MDN: HTTP caching** — https://developer.mozilla.org/en-US/docs/Web/HTTP/Caching — deeper than what we covered.
- **Mozilla: CORS** — https://developer.mozilla.org/en-US/docs/Web/HTTP/CORS — only when CORS bites you.
- **httpstat.us** — https://httpstat.us — returns any status code you ask for, useful for testing.

## Exercises

1. **Trace a real request** — Pick one endpoint from `api.github.com` (e.g. `GET /repos/torvalds/linux`). Run `curl -v` against it. In `journal/day-03.md`:
   - Paste the full output.
   - Annotate every header.
   - Identify which headers tell the client about caching.
2. **Status code drills** — for each scenario, write what status code your API should return and why:
   - A user submits a sign-up form with a missing email field.
   - A user submits valid JSON but the email is already registered.
   - An unauthenticated user requests `/users/me`.
   - A normal user tries to delete another user.
   - A user requests `/users/99999` which doesn't exist.
   - Your code calls a downstream service and times out.
3. **Postman / Bruno collection** — Save a 4-request collection against `api.github.com`: get a user, get their repos, search for issues, get rate-limit info. Export and commit the collection.

## Common pitfalls

- **Returning 200 for an error** with `{"success": false}` in the body. Don't. Use the right status code.
- **Confusing 401 and 403** — 401 = "who are you?", 403 = "I know who you are but no."
- **Putting state-changing actions behind `GET`** — caches, link previewers, and search bots will trigger them.
- **Sending JSON without `Content-Type: application/json`** — some clients will treat it as text and break.
- **Forgetting that `PUT` is a full replace, not a partial update** — use `PATCH` for partials.

## Self-check

1. A `POST` returns 201. Where should the client look to find the URL of the newly-created resource?
2. You have an endpoint that creates an order. The client retries on network failure. How do you make this safe?
3. Why does FastAPI return 422 on bad request bodies, while many frameworks return 400?
4. What's the difference between a 502 and a 503?
5. The same `GET` request returns different responses to different users. Should it be cached? What header expresses that?
6. A frontend complains your API returns CORS errors. Where do you look first?

## Definition of done

- [ ] `journal/day-03.md` committed with the annotated `curl -v` trace.
- [ ] Status-code drill answers in your journal.
- [ ] Postman/Bruno collection committed under `tools/api-collections/`.
- [ ] PR opened and reviewed.
