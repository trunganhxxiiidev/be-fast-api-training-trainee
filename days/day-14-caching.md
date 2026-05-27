# Day 14 — Caching & Async Work

> **Week 3 · Day 14** · ~6 hours · [← Week overview](../week-3-advanced.md)

## Objective

Add a Redis-backed cache to the API for a read-heavy endpoint, prove the speedup with a measurement, and learn the invalidation patterns and failure modes that determine whether a cache helps or hurts. Touch background jobs with Celery so you know what shape they take.

## Why this matters

Caching is a force multiplier when used right and a footgun when used wrong. The performance gains are visible — a hot endpoint can go from 200ms to 5ms. The bugs are *invisible* until production: stale data, cache stampedes, cache-DB inconsistency. Today is about the discipline as much as the technique.

## Concepts

**What Redis is**

A single-threaded, in-memory key-value store with very fast (sub-millisecond) reads and writes. Common uses:
- **Cache** — store the result of expensive queries.
- **Session store** — server-side session data.
- **Rate limiter** — atomic counters with TTL.
- **Message broker** — for Celery, RQ.
- **Pub/sub** — light real-time fanout.

Single-threaded means individual commands are atomic. `INCR`, `SETNX`, and `EXPIRE` give you most of what you need for coordination.

**Cache-aside (the only pattern you need on day one)**

```python
async def get_post_cached(post_id: int, db: AsyncSession, redis: Redis) -> Post:
    key = f"post:{post_id}"
    cached = await redis.get(key)
    if cached:
        return Post.model_validate_json(cached)   # hit
    post = await db.get(Post, post_id)             # miss
    if post is None:
        raise HTTPException(404)
    await redis.set(key, post.model_dump_json(), ex=300)   # 5-min TTL
    return post
```

The flow: check cache → on miss, read from DB → populate cache → return. Other patterns (write-through, write-behind) exist but cache-aside is the simplest and rarely wrong.

**Invalidation — the only hard problem in caching**

Three strategies, ordered by simplicity:

1. **TTL-only** — set an expiry, accept staleness for up to that long. Best for read-heavy data where eventual consistency is fine (top-N lists, popular-posts).
2. **TTL + write-through bust** — on update, also delete the cache key. Better consistency, more code.
3. **Manual invalidation everywhere** — every write path knows which cache keys it invalidates. Hardest to maintain.

Pick TTL-only as your default. Add write-through busting only where staleness has bitten you.

**Failure modes you must know**

- **Stale data** — TTL too high or invalidation missed. Symptom: "I updated my profile but it didn't change."
- **Cache stampede** — TTL expires on a hot key; 1000 requests all miss simultaneously and pile on the DB. Fix: use a "lock + recompute" pattern, or add jitter to the TTL.
- **Cache-DB inconsistency on partial failures** — DB update succeeds, cache delete fails (or vice versa). Real systems eventually need a way to reconcile.
- **Memory exhaustion** — without an eviction policy, Redis fills up and refuses writes. Configure `maxmemory-policy allkeys-lru` for cache use cases.
- **Treating cache as truth** — every cache must be safe to wipe. If wiping causes data loss, you're using cache as a primary store.

**Key naming conventions**

- Use colons as separators: `user:42`, `post:142:comments`, `rate:login:ip:1.2.3.4`.
- Include the schema version when keys store serialized data: `v2:post:42`. Bumping `v2` to `v3` invalidates the whole namespace atomically.
- Avoid keys without TTL unless they're meant to be persistent.

**Redis with FastAPI — `redis.asyncio`**

```python
# app/redis.py
from redis.asyncio import Redis, from_url

_redis: Redis | None = None

async def get_redis() -> Redis:
    global _redis
    if _redis is None:
        _redis = from_url(settings.redis_url, decode_responses=True)
    return _redis
```

Wire as a dependency: `RedisDep = Annotated[Redis, Depends(get_redis)]`.

**Background jobs — when to reach for them**

If a request must wait for a slow operation (sending an email, processing an upload, computing a report) and the user doesn't need the result inline, run it in the background. Two options:

1. **FastAPI `BackgroundTasks`** — runs after the response is sent, in the same process. Fine for fire-and-forget like "send a welcome email" with low SLA.
2. **Celery (or RQ, Dramatiq, Arq)** — a worker process consumes jobs from Redis. Survives app restarts. Right for anything that *must* complete, takes seconds-to-minutes, or runs on a schedule.

For this internship: know what they are. Use Celery only in the pet project if you take the async-work stretch goal.

## Required reading

1. **Redis docs: Introduction** — https://redis.io/docs/latest/develop/get-started/data-store/
2. **`redis-py` async docs** — https://redis.readthedocs.io/en/stable/examples/asyncio_examples.html
3. **Cache aside pattern (Microsoft Azure docs)** — https://learn.microsoft.com/en-us/azure/architecture/patterns/cache-aside — concise.
4. **Martin Fowler: TwoHardThings** — https://martinfowler.com/bliki/TwoHardThings.html — "naming things and cache invalidation."

## Optional reading

- **Redis: Cache eviction policies** — https://redis.io/docs/latest/develop/reference/eviction/
- **Celery: First steps with Celery** — https://docs.celeryq.dev/en/stable/getting-started/first-steps-with-celery.html
- **The thundering herd problem** — https://en.wikipedia.org/wiki/Thundering_herd_problem — the formal name for cache stampedes.

## Exercises

1. **Add Redis to compose** — already in your `docker-compose.yml` from Day 13. Verify it's reachable: `docker compose exec cache redis-cli PING` returns `PONG`.

2. **Cache `GET /posts/{id}`** — implement the cache-aside pattern from above. Choose a 5-minute TTL.

3. **Prove the speedup**
   - Hit the endpoint 100 times via `ab` or `wrk` with the cache cold.
   - Measure p50 and p99 latency.
   - Repeat with cache warm.
   - Commit the numbers to `journal/day-14.md`.

4. **Invalidation** — on `PUT /posts/{id}`, `PATCH /posts/{id}`, and `DELETE /posts/{id}`, delete the cache key. Add tests that confirm:
   - Updating a post invalidates the cache (subsequent GET returns the new data).
   - The cache repopulates with the new value on the next read.

5. **Cache key versioning** — change your serialization format (e.g. add a field). Bump the cache version prefix. Confirm old cache entries are ignored (effectively orphaned, will TTL out).

6. **Stretch (optional): rate limiter** — add a simple per-IP rate limit on `/auth/login`: 5 attempts per minute. Implement with `INCR` + `EXPIRE` on a key like `rate:login:ip:{ip}`. Return 429 if exceeded.

7. **Failure-modes journal** — pick 3 of the failure modes listed above and write one paragraph each on how you'd notice, diagnose, and mitigate them.

## Common pitfalls

- **Forgetting the TTL** — `redis.set(k, v)` with no `ex=` leaves it forever. Always pass `ex` for cache entries.
- **Caching errors** — if the underlying DB call fails, don't cache "404 Not Found" for 5 minutes. Only cache successful responses (and very intentionally cache 404s if you want, with a short TTL).
- **Caching user-specific data under a global key** — `posts:popular` cached per-user-with-a-shared-key is a data leak. Include user identity in the key when needed.
- **Long TTLs on data that changes often** — the speedup isn't worth the staleness.
- **Treating Redis as durable** — it isn't (by default). Don't put data you can't regenerate.
- **Synchronous Redis client in an async app** — same lesson as Day 4. Use `redis.asyncio.Redis`.

## Self-check

1. You set a 5-minute TTL on `post:42`. The post is updated 1 minute in. How long can stale data be served? How would you reduce that?
2. A hot key is requested 1000×/sec. Its TTL expires. What happens? How do you prevent it?
3. Why is "delete on write" easier to get right than "update on write"?
4. Your cache hit rate is 5%. Is that good or bad? What questions would you ask?
5. You add Redis caching but latency *increases*. Plausible causes?
6. The DB has been updated by an admin in `psql` directly (bypassing the API). Your cache still serves the old value. What's the systemic fix?

## Definition of done

- [ ] `GET /posts/{id}` uses cache-aside with a 5-minute TTL.
- [ ] Write paths (PUT/PATCH/DELETE) invalidate the cache.
- [ ] Latency measurement (cold vs warm) committed.
- [ ] Tests cover both cache miss and cache hit paths.
- [ ] Cache version prefix in key naming.
- [ ] PR merged.
