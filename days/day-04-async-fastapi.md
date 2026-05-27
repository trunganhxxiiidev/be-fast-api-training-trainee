# Day 4 — Async Python & FastAPI Fundamentals

> **Week 1 · Day 4** · ~6 hours · [← Week overview](../week-1-fundamentals.md)

## Objective

Build a working mental model of Python's async/await before writing FastAPI code, then write your first FastAPI service with Pydantic-validated request/response models. By end of day, you should be able to explain *when* async helps and *when* it actively hurts you.

## Why this matters

FastAPI is async-first. Used correctly, it's one of the fastest Python web frameworks. Used incorrectly — i.e. blocking the event loop with synchronous I/O inside an async handler — it's slower and more confusing than Flask. The difference between these two outcomes is understanding the event loop. Spend the morning on the model, the afternoon on the framework.

## Concepts

**The event loop in 5 minutes**

Python's `asyncio` has a single-threaded *event loop*. When you `await` an I/O operation, your coroutine yields control back to the loop, which can run other coroutines while the I/O is pending. When the I/O completes, the loop resumes your coroutine.

This is great for I/O-bound workloads (DB queries, HTTP calls, file reads on SSDs). It's pointless for CPU-bound work (image processing, large JSON parsing) — those block the loop just as badly as synchronous code does.

**The cardinal rule**: never call a *synchronous, blocking* function inside an `async def` handler. If you do, every other request waits for it to finish. Examples of accidental blocking:
- `time.sleep(5)` — use `await asyncio.sleep(5)`.
- `requests.get(...)` — use `httpx.AsyncClient().get(...)` with `await`.
- `psycopg2.connect(...)` — use `asyncpg` or SQLAlchemy's async engine.
- Heavy CPU work — offload to a thread pool with `await asyncio.to_thread(fn, *args)` or a process pool.

**When sync is fine**

FastAPI lets you mix `def` and `async def` handlers. A `def` handler runs in a thread pool — it doesn't block the event loop. For endpoints that only do CPU work or call sync-only libraries, `def` can actually be the right choice. Don't reach for `async def` reflexively.

**FastAPI hello world**

```python
from fastapi import FastAPI
from pydantic import BaseModel

app = FastAPI(title="My First API", version="0.1.0")

class Item(BaseModel):
    name: str
    price: float
    in_stock: bool = True

@app.get("/")
async def root() -> dict[str, str]:
    return {"message": "hello"}

@app.get("/items/{item_id}")
async def get_item(item_id: int, q: str | None = None) -> Item:
    return Item(name=f"Item {item_id}", price=9.99)

@app.post("/items", status_code=201)
async def create_item(item: Item) -> Item:
    return item
```

Run it: `uv run uvicorn main:app --reload`. Visit `http://localhost:8000/docs` for the auto-generated Swagger UI.

**What FastAPI gives you for free**
- Path/query/body parameter parsing with type coercion.
- Pydantic validation on the request body — returns `422` with a clear error envelope.
- OpenAPI 3 schema generation, served at `/docs` (Swagger UI) and `/redoc`.
- Async support — but only useful if your handler logic is actually async.

**Pydantic v2 essentials (preview — deeper on Day 6)**
- `BaseModel` subclasses are your request/response schemas.
- Fields can have defaults, validation (`Field(min_length=1, gt=0)`), and aliases.
- `model_dump()` (not `.dict()`) converts to a plain dict.
- `model_validate()` parses from a dict.
- Pydantic v2 is *much* faster than v1 — written in Rust under the hood.

## Required reading

1. **Real Python: Async IO in Python** — https://realpython.com/async-io-python/ — read the first half carefully. Skim the rest.
2. **FastAPI Tutorial: First Steps → Path Parameters → Query Parameters → Request Body** — https://fastapi.tiangolo.com/tutorial/first-steps/ — go through these four pages in order.
3. **FastAPI: Concurrency and async / await** — https://fastapi.tiangolo.com/async/ — Tiangolo's own explanation is excellent.

## Optional reading

- **Pydantic v2 migration guide** — https://docs.pydantic.dev/latest/migration/ — only if you find old `dict()` / `parse_obj()` code online.
- **`asyncio` docs** — https://docs.python.org/3/library/asyncio.html — reference, not a tutorial.

## Exercises

1. **`async` mental model drill** — write `journal/day-04.md` with your own one-paragraph explanation of:
   - Why `time.sleep(5)` in an async handler hurts every other request.
   - When you would deliberately use `def` instead of `async def` in FastAPI.
   - What `await asyncio.gather(call_a(), call_b())` does that sequential `await` doesn't.

2. **FastAPI starter**
   - `uv init hello-api && cd hello-api && uv add fastapi uvicorn[standard]`
   - Create `main.py` with:
     - `GET /` returning a hello message.
     - `GET /items/{item_id}` accepting a path param + optional `q` query param, returning a Pydantic `Item` response.
     - `POST /items` accepting a Pydantic `Item` body, returning the same item with a generated UUID.
   - Run `uv run uvicorn main:app --reload` and verify everything in the browser at `/docs`.

3. **Force a 422** — hit `POST /items` with a deliberately-bad payload (missing field, wrong type). Read the response body. In your journal, note three things the response tells the client.

## Common pitfalls

- **`async def` with sync libraries** — `requests`, `psycopg2`, `time.sleep`. Use the async equivalents (`httpx.AsyncClient`, `asyncpg`/SQLAlchemy async, `asyncio.sleep`).
- **Forgetting to `await`** — `result = some_async_func()` gives you a coroutine object, not the result. Linters and type checkers will warn — listen to them.
- **Heavy CPU work in an async handler** — JSON parsing of huge payloads, image encoding, hashing. Offload to a thread or process pool.
- **Mixing Pydantic v1 and v2 patterns** — if a tutorial uses `.dict()` or `parse_obj_as`, it's v1. The current docs are v2.
- **Using `app.on_event("startup")`** — deprecated. Use lifespan context managers.

## Self-check

1. Why is FastAPI typically faster than Flask for I/O-bound endpoints?
2. What happens if a `def` handler does a 5-second `time.sleep` in FastAPI?
3. You have an endpoint that calls three independent external APIs. How do you fetch them in parallel?
4. What status code does FastAPI return when a request body fails Pydantic validation? Why that specific code?
5. Where does the OpenAPI schema live by default, and how do you customize the title and version?
6. When would you use `BackgroundTasks` instead of returning the result synchronously?

## Definition of done

- [ ] Hello API repo committed, three endpoints working.
- [ ] Swagger UI at `/docs` shows correct request/response schemas.
- [ ] Async/sync explanation in `journal/day-04.md`.
- [ ] You can demo the 422-on-bad-payload behavior live to the mentor.
- [ ] PR opened and reviewed.
