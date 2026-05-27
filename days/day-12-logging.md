# Day 12 — Logging, Errors & Observability

> **Week 3 · Day 12** · ~6 hours · [← Week overview](../week-3-advanced.md)

## Objective

Replace ad-hoc `print()`s and basic loggers with structured JSON logging, request correlation IDs that tie multiple log lines from one request together, and a clear story for how exceptions and metrics fit in.

## Why this matters

When a production bug happens at 2 AM, "the logs" are the difference between a 30-minute fix and a 6-hour fishing expedition. `print("user_id:", user_id)` is great in development; in production it's noise. Structured logging is what lets you grep for `user_id=42 status=500` across millions of lines. Correlation IDs are what let you reconstruct a single user's journey across services. The three pillars — logs, metrics, traces — sit on top of these foundations.

## Concepts

**Structured logging (one paragraph)**

Each log line is a JSON object with key-value fields. Instead of `"User 42 failed login"`, you log `{"event": "login_failed", "user_id": 42, "reason": "wrong_password"}`. Aggregation tools (ELK, Datadog, Loki, CloudWatch Insights) can then filter, aggregate, and chart by those fields without regex gymnastics.

**`structlog` setup for FastAPI**

```python
# app/logging_setup.py
import logging
import structlog

def configure_logging(json_logs: bool = True, log_level: str = "INFO") -> None:
    logging.basicConfig(format="%(message)s", level=log_level, handlers=[logging.StreamHandler()])

    processors = [
        structlog.contextvars.merge_contextvars,
        structlog.processors.add_log_level,
        structlog.processors.TimeStamper(fmt="iso", utc=True),
        structlog.processors.StackInfoRenderer(),
        structlog.processors.format_exc_info,
    ]
    if json_logs:
        processors.append(structlog.processors.JSONRenderer())
    else:
        processors.append(structlog.dev.ConsoleRenderer())  # pretty, colored, dev-only

    structlog.configure(
        processors=processors,
        wrapper_class=structlog.make_filtering_bound_logger(getattr(logging, log_level)),
        logger_factory=structlog.PrintLoggerFactory(),
        cache_logger_on_first_use=True,
    )
```

Call `configure_logging(json_logs=settings.env != "dev")` in your `create_app()`.

**Correlation IDs — request tracing**

Each incoming request gets a unique ID. Either the client sends one in `X-Request-ID`, or you generate a UUID. Every log line in that request includes the ID. When a user reports a bug, they (or the frontend) can send you the ID and you can find every line.

```python
# app/middleware.py
import uuid, structlog
from starlette.middleware.base import BaseHTTPMiddleware

class CorrelationIdMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request, call_next):
        cid = request.headers.get("X-Request-ID") or str(uuid.uuid4())
        structlog.contextvars.clear_contextvars()
        structlog.contextvars.bind_contextvars(correlation_id=cid)
        response = await call_next(request)
        response.headers["X-Request-ID"] = cid
        return response
```

`bind_contextvars` puts the ID in a context variable. Any `structlog.get_logger().info("...")` *anywhere* in the request lifecycle now includes the ID automatically. No threading it through every function call.

**Log levels — what actually belongs where**

| Level | Use when | Examples |
|-------|----------|----------|
| `DEBUG` | Granular details for debugging. Off in prod. | Variable values, branch decisions |
| `INFO` | Normal operational events worth seeing. | User logged in, payment succeeded |
| `WARNING` | Unexpected but handled. Someone may want to investigate. | Retry succeeded, deprecated endpoint hit |
| `ERROR` | Something failed; user-facing impact. | Failed to send email, DB query timed out |
| `CRITICAL` | App can't continue. Page someone. | DB unreachable, out of memory |

**Two rules that prevent 90% of bad logging code:**
1. Never log with f-strings: `logger.info(f"user {user_id} logged in")` evaluates the f-string even when DEBUG is off. Use `logger.info("user_logged_in", user_id=user_id)`.
2. Never log secrets. Passwords, tokens, full credit cards, PII. Strip them at the boundary. Once a secret is in logs, it's leaked.

**Exception handling and logging**

The global FastAPI exception handlers should also log:

```python
@app.exception_handler(Exception)
async def unhandled(request, exc):
    log = structlog.get_logger()
    log.exception("unhandled_exception", path=request.url.path, method=request.method)
    return JSONResponse({"error": {"code": "INTERNAL_ERROR", "message": "Something went wrong"}}, status_code=500)
```

`log.exception(...)` captures the stack trace. Without it you just have "something broke."

**The three pillars (briefly)**

- **Logs**: discrete events. Structured logging is the unit of work.
- **Metrics**: numerical time-series. "How many login failures per minute?" — that's a counter. Backed by Prometheus, StatsD, etc.
- **Traces**: cross-service request flow. OpenTelemetry is the standard.

For this internship: get logs right. Touch metrics in the pet project if you take the observability stretch goal.

**Sentry (or any error tracker)**

A separate concern from logs: errors get reported to a dashboard with stack traces, breadcrumbs, and grouping. Sentry's FastAPI integration is one line. Worth knowing exists; not required for the pet project unless the mentor asks.

## Required reading

1. **structlog: Getting Started** — https://www.structlog.org/en/stable/getting-started.html
2. **OneUptime: Structured Logging in FastAPI** — https://oneuptime.com/blog/post/2026-02-02-fastapi-structured-logging/view — the full middleware + contextvars setup.
3. **Apitally: Complete guide to logging in FastAPI** — https://apitally.io/blog/fastapi-logging-guide — covers both stdlib and structlog, plus correlation IDs.

## Optional reading

- **OpenTelemetry: Python instrumentation for FastAPI** — https://opentelemetry-python-contrib.readthedocs.io/en/latest/instrumentation/fastapi/fastapi.html — when you're ready to add tracing.
- **Sentry: FastAPI integration** — https://docs.sentry.io/platforms/python/integrations/fastapi/
- **Honeycomb: What is observability?** — https://www.honeycomb.io/what-is-observability — broader context.

## Exercises

1. **Add `structlog`** as a dependency. Implement `configure_logging` and call it from `create_app()`. Use JSON in prod-ish envs, ConsoleRenderer in dev.

2. **Correlation ID middleware** — implement and register `CorrelationIdMiddleware` *before* the request-logger middleware. Confirm a request without a header gets a UUID, and one with `X-Request-ID: my-id-123` reuses that ID.

3. **Convert all logging** — replace every `print()` and `logger.info(f"...")` with structured `logger.info("event_name", key=value, ...)`. Pay attention to:
   - The login endpoint should log success and failure (without logging the password).
   - The exception handler should log with `log.exception`.
   - The request middleware should log method, path, status, duration_ms, correlation_id.

4. **Force an error** — trigger an unhandled exception in a test endpoint. Verify:
   - The response is a clean 500 with your error envelope.
   - The log line includes the full stack trace.
   - The correlation ID matches between the response header and the log line.

5. **Grep drill** — run the test suite. Pipe logs to a file. Demonstrate:
   - All log lines for one specific correlation ID.
   - All `WARNING` and above lines across all requests.
   - All login failures with their `reason` field.

6. **Metrics sketch** — write a paragraph in `journal/day-12.md` describing the 5 metrics you'd add if this were a production service. Be specific: counter/gauge/histogram, label dimensions, alert threshold.

## Common pitfalls

- **`print()` in production code** — find them with `ruff` rule `T20`. Enable it.
- **Logging secrets** — passwords, tokens, full PANs, JWT bodies. Strip at the boundary, never log the raw request body.
- **f-string log messages** — `logger.info(f"user {x}")` evaluates always; `logger.info("user_event", user_id=x)` doesn't unless the level is enabled.
- **Logging at the wrong level** — every error logged at INFO drowns the signal; every retry logged at ERROR pages someone at 2 AM.
- **Forgetting to clear contextvars between requests** — without `clear_contextvars()`, log fields from request N can leak into request N+1.
- **One huge log line per request** — useful for billing, terrible for debugging. Log discrete events as they happen.

## Self-check

1. What's the practical difference between a logger that writes JSON and one that writes plain text?
2. Walk through what happens when two concurrent requests use `bind_contextvars`. Why don't they overwrite each other?
3. You see a 500 error in production. What's the *minimum* you need in the log to reproduce and fix it?
4. When would `log.warning` be wrong, and `log.error` be right?
5. A request hits 5 internal services. What does a correlation ID give you that timestamps alone don't?
6. Your logs are 10× too big. How do you bring the volume down without losing signal?

## Definition of done

- [ ] `structlog` configured with JSON in non-dev environments.
- [ ] Correlation ID middleware live; ID appears in both response headers and every log line.
- [ ] Zero `print()` statements anywhere in `app/`.
- [ ] Exception handler logs with full stack trace.
- [ ] Test that triggers a 500 and asserts the log includes the correlation ID.
- [ ] Metrics sketch committed.
- [ ] PR merged.
