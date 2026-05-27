# Week 1 — Foundations

**Goal:** Get fluent with the tools, language, and protocols every Python backend dev uses daily.

By Friday, the intern should be able to: clone a repo, branch and PR cleanly, write a small FastAPI service with tests, and explain what happens between `curl` and the route handler.

> **Detailed daily lessons** with required reading, exercises, pitfalls, and self-check:
> - [Day 1 — Environment, Shell & Git](./days/day-01-environment-git.md)
> - [Day 2 — Python Refresher](./days/day-02-python-refresher.md)
> - [Day 3 — HTTP & REST](./days/day-03-http-rest.md)
> - [Day 4 — Async Python & FastAPI Fundamentals](./days/day-04-async-fastapi.md)
> - [Day 5 — Hello API (deliverable)](./days/day-05-hello-api.md)

This page is the **week-at-a-glance**. Click into each day for the full lesson.

---

## Day 1 — Environment, Shell & Git

**Topics**
- macOS/Linux shell basics: `cd`, `ls`, `grep`, `find`, `xargs`, pipes, redirection.
- Editor setup: VS Code + extensions (Python, Pylance, Ruff, even Better TOML).
- Git mental model: working tree, index, HEAD, remote. **Not** memorized commands — the model.
- Branching strategy: `main` is protected, work happens on `feature/<topic>` branches, merged via PR.
- `.gitignore`, conventional commit messages, rebase vs. merge.

**Exercises**
1. Install Python 3.12 (via `pyenv`). Document the steps in `journal/day-01.md`.
2. Clone the training repo, create a `feature/intern-setup` branch, add a file with your name, open a PR.
3. Read [Pro Git ch. 2 & 3](https://git-scm.com/book/en/v2). Summarize the difference between `merge` and `rebase` in your own words.

**Checkpoint**
- Mentor reviews the PR. Common feedback: commit message style, branch naming.

---

## Day 2 — Python Refresher

**Topics**
- Virtual environments — pick **one** of `venv`, `uv`, or `poetry` and stick with it for the program. Recommend `uv` for speed.
- Type hints, `dataclasses`, `Optional`, `Union`, `TypedDict`, `Protocol`.
- Standard library highlights: `pathlib`, `json`, `dataclasses`, `enum`, `logging`, `datetime`.
- `pytest` basics: fixtures, `parametrize`, assertions, `-k` and `-x` flags.

**Exercises**
1. Write a CLI script `wordcount.py` that counts words in a file with `argparse` + full type hints.
2. Write 5 pytest tests for it including edge cases (empty file, missing file, unicode).
3. Configure `ruff` + `black` and add a pre-commit hook that runs them.

---

## Day 3 — HTTP & REST

**Topics**
- HTTP/1.1 request anatomy: method, path, headers, body. Status code categories.
- Idempotency, safety, caching headers (`ETag`, `Cache-Control`, `Last-Modified`).
- REST conventions: resource naming, verb mapping, status codes for common scenarios.
- Why `POST /users/login` is fine but `GET /users/delete?id=5` is not.
- Content negotiation, `Accept`, `Content-Type`, CORS at a high level.

**Exercises**
1. Use `curl -v` against a public API (e.g. `api.github.com`) and trace one request end-to-end. Save the output and annotate every line.
2. Read [MDN HTTP overview](https://developer.mozilla.org/en-US/docs/Web/HTTP/Overview) and answer in `journal/day-03.md`:
   - What's the difference between 401 and 403?
   - When would you use 409 vs 422?
   - What does `ETag` actually solve?
3. Set up Postman/Bruno/Insomnia (pick one) and save a collection for the GitHub API calls you traced.

---

## Day 4 — Async Python & FastAPI Fundamentals

**Topics**
- The event loop in 5 minutes: `async def`, `await`, why blocking calls in async handlers are a disaster.
- When async actually helps vs. when sync is fine.
- FastAPI hello-world: `app`, route decorators, path/query params, request bodies.
- Pydantic v2 — request/response models, automatic validation, automatic OpenAPI docs at `/docs`.

**Exercises**
1. Build a minimal FastAPI app with `GET /` returning a JSON greeting.
2. Add `GET /items/{item_id}` with a Pydantic response model.
3. Add `POST /items` accepting a Pydantic request body; return 422 if invalid (FastAPI does this for free — verify).
4. Open `/docs` and explore the auto-generated Swagger UI.

---

## Day 5 — Hello API (Week 1 Deliverable)

**Spec — a small but proper FastAPI service**

- `POST /echo` accepts JSON `{"message": "<string>"}` and returns `{"echo": "<string>", "received_at": "<ISO8601>"}`.
- `GET /health` returns `{"status": "ok"}`.
- Returns 422 with a clear error body if the request shape is wrong (FastAPI default is fine; understand it).
- Logs every request with method, path, status, and duration (write a simple middleware).
- Reads port from `PORT` env var, defaults to 8000.

**Project structure**
```
hello-api/
├── pyproject.toml
├── README.md
├── .env.example
├── app/
│   ├── __init__.py
│   ├── main.py          ← app factory, middleware
│   ├── routes/
│   │   ├── __init__.py
│   │   ├── echo.py
│   │   └── health.py
│   └── schemas.py       ← Pydantic models
└── tests/
    ├── test_echo.py
    └── test_health.py
```

**PR checklist**
- [ ] `README.md` explains how to install, run, and test in three commands.
- [ ] At least one happy-path + one validation-error test per route, using `httpx.AsyncClient` or FastAPI's `TestClient`.
- [ ] `ruff` clean, `black` formatted.
- [ ] No hardcoded port; read from env.
- [ ] No print statements — use `logging`.

**Weekly review focus**
- Walk through the project layout. Why split routes into their own modules?
- Show the OpenAPI docs at `/docs`. Find one thing you'd improve.
- One concept from this week that didn't click — talk it through with the mentor.
