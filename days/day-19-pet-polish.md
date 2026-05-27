# Day 19 — Pet Project: Secondary Features + Polish

> **Week 4 · Day 19** · ~8 hours · [← Week overview](../week-4-pet-project.md)

## Objective

Land the secondary features called out in your design doc, add the cache, fill in observability, round out test coverage to 70% on services, and tidy everything for the Day 20 demo. Today is the difference between "it works" and "it's reviewable."

## Why this matters

A senior dev reviewing your project notices polish: clear logs, a useful README, helpful error messages, sensible defaults, no debug prints left in. None of these change what the app *does*, but they change how it's *received*. The rubric weights this heavily (see [`evaluation-rubric.md`](../evaluation-rubric.md)).

## Order of operations

Strict priority. Stop when you run out of time — don't push to Day 20.

1. **Secondary features** from your design (the long tail of CRUD endpoints, filtering, pagination, etc.).
2. **Cache** — at least one cached read with TTL and write-through invalidation.
3. **Tests** — push services-layer coverage to ≥70%.
4. **Structured logging + correlation ID** — every request logs one structured line, errors include stack traces.
5. **Pre-demo dry run** with the mentor (4 PM cutoff — book the slot).
6. **README polish** — install, env vars table, example curl commands, deploy guide.
7. **Stretch goal** — only if everything above is done and time remains.

## Secondary feature implementation tips

**Pagination as a dependency** (already shipped on Day 6, just reuse):
```python
def pagination(limit: int = Query(20, ge=1, le=100), offset: int = Query(0, ge=0)) -> tuple[int, int]:
    return limit, offset
```
Apply it consistently. Don't paginate one endpoint with `?page=` and another with `?offset=`.

**Filtering and sorting**

Add `?status=...`, `?created_after=...` etc. *only* where the design doc lists them. Don't invent filters — scope creep loses you time you need for polish.

**Cache wiring** (from [Day 14](./day-14-caching.md))

```python
async def get_resource_cached(rid: int, db: SessionDep, redis: RedisDep) -> Resource:
    key = f"v1:resource:{rid}"
    if cached := await redis.get(key):
        return ResourceOut.model_validate_json(cached)
    resource = await db.get(Resource, rid)
    if not resource:
        raise HTTPException(404)
    out = ResourceOut.model_validate(resource)
    await redis.set(key, out.model_dump_json(), ex=300)
    return out
```

On any write to that resource, `await redis.delete(f"v1:resource:{rid}")`. Add a test that confirms the invalidation works.

**Measure the cache** — even a small `time` measurement comparing before/after, captured in `journal/day-19.md`, makes the demo more credible.

## Test coverage push

Run `uv run pytest --cov=app/services --cov-report=term-missing`. Look at the report. For each uncovered line in `app/services/`, decide:
- Worth testing → write the test now.
- Glue/logging → skip; possibly add `# pragma: no cover`.
- Dead code → delete it.

You're aiming for **≥70%** on `app/services`. Routes and adapters can be lower — they're already covered by integration tests.

## Observability checklist

Walk through these in order:

- [ ] `print()` count in `app/` is zero (`grep -r "print(" app/`).
- [ ] All `logger.info(...)` calls use `event_name + kwargs`, not f-strings.
- [ ] `CorrelationIdMiddleware` registered.
- [ ] Response includes `X-Request-ID` header.
- [ ] Exception handler logs with full stack trace.
- [ ] One log line per request (method, path, status, duration_ms, correlation_id).
- [ ] No password, no JWT, no PII appears in logs.

## README polish

Treat the README as the demo's silent supporting cast. Sections to fill in:

```markdown
# <Project Name>

One-sentence description.

## Quickstart
```bash
cp .env.example .env  # then edit
docker compose up -d
docker compose exec api alembic upgrade head
curl http://localhost:8000/health
```

## Environment variables
| Var | Default | Notes |
|-----|---------|-------|
| DATABASE_URL | — | required, asyncpg form |
| JWT_SECRET | — | required, 32+ bytes |
| REDIS_URL | redis://cache:6379/0 | |
| LOG_LEVEL | INFO | |
| APP_ENV | dev | "prod" enables JSON logs |

## Running tests
`docker compose run --rm api pytest -v --cov=app`

## Example API flow
Five `curl` commands that exercise register → login → main feature → cleanup.

## Deployment
See [DEPLOY.md](./DEPLOY.md). TL;DR: `terraform apply` from `terraform/`.

## Architecture
A single Mermaid diagram showing api, db, cache, and how a request flows.
```

## Day plan (suggested)

**Morning (4 hours)**
1. Stand-up with mentor — share priority list.
2. Implement remaining endpoints from DESIGN.md.
3. Wire cache + invalidation. Write tests.
4. Test coverage push.

**Afternoon (4 hours)**
5. Observability checklist.
6. **4 PM: dry-run demo with mentor.** Apply their feedback before close of day.
7. README polish.
8. Commit, push, ensure CI green on `main`.

## Common pitfalls

- **Starting a stretch goal at 2 PM** — you won't finish. Polish what you have.
- **One giant final commit** — splits poorly and makes review hard. Keep small commits flowing through the day.
- **README written at 5:30 PM** — rushed, vague, missing env vars. Block 60 minutes for it earlier.
- **Cache invalidation forgotten on PATCH** — only DELETE invalidates. Test the PATCH path explicitly.
- **Test coverage at 65% because two big functions are uncovered** — write the tests; don't shrink the target.
- **No correlation ID showing up in logs** — middleware order matters. `CorrelationIdMiddleware` must run before `RequestLoggerMiddleware`.

## Self-check

1. Walk through the request path through your cache wrapper. What happens on hit vs miss?
2. You added five new endpoints today. Did each get at least one test?
3. The mentor asks you to demo a failing request. Show the log line that proves you can debug it.
4. Where does your README say to find the Terraform config? Has someone besides you ever followed your README?
5. What part of the project are you proudest of? Be specific. What part are you least happy with?
6. What's the *one* thing you'd build differently if you had another week?

## Definition of done

- [ ] All endpoints from DESIGN.md implemented and tested.
- [ ] Cache wired on at least one read path, with invalidation on writes.
- [ ] Services-layer coverage ≥70%.
- [ ] Observability checklist 100%.
- [ ] Pre-demo dry run completed with mentor.
- [ ] README, DEPLOY.md, and DESIGN.md all current.
- [ ] CI green on `main`.
- [ ] PR(s) merged so `main` is the demo source.
