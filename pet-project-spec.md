# Pet Project — Final Examination Spec

The pet project is the capstone of the internship. Pick **one** of the three options below, or propose your own (mentor must approve the proposal before any code is written).

Whichever option you pick, the project **must** demonstrate every required capability listed in [Required Capabilities](#required-capabilities).

---

## Option A — URL Shortener with Analytics

**Problem:** Build a tiny Bitly-like service. Users register, create short URLs, and see basic click analytics on their links.

**Core features**
- `POST /shorten` — given a long URL, return a short code.
- `GET /{code}` — 301 redirect to the original URL. Records the hit.
- `GET /links` — list the authenticated user's links with click counts.
- `GET /links/{id}/stats` — per-day hits for the last 30 days.
- Anonymous users can create up to 5 short URLs from one IP per day (rate limit).

**Why it's a good fit:** Touches DB design (URLs + hits), caching (the redirect lookup), background work (analytics rollup), and a real-world edge case (rate limiting).

---

## Option B — Task Manager with Teams

**Problem:** A small team task manager — think a minimal Trello.

**Core features**
- Auth: register, login, JWT.
- `Teams`: users can create a team and invite others by email.
- `Tasks`: belong to a team, have a title, description, status (`todo`/`doing`/`done`), assignee, due date.
- `GET /teams/{id}/tasks` with filters by status, assignee, and due date range.
- Authorization: only team members can see team tasks; only the task creator or an admin can delete a task.
- Webhook: optional outgoing webhook fired when a task is completed.

**Why it's a good fit:** Heavy on authorization rules, foreign keys, and query design.

---

## Option C — Personal Finance Tracker

**Problem:** Track income and expenses; produce monthly summaries.

**Core features**
- `Accounts`: cash, bank, credit card.
- `Transactions`: amount, category, date, account, notes.
- `Categories`: user-defined, with a parent for hierarchy (e.g. `Food > Groceries`).
- `GET /summary?month=YYYY-MM` — total in/out per category for a month.
- CSV import endpoint that bulk-creates transactions from a file.
- Idempotency on the CSV import (re-uploading the same file doesn't double-count).

**Why it's a good fit:** Exercises file handling, idempotency, aggregation queries, and money math (use `Decimal`, never `float`).

---

## Required Capabilities

Regardless of which option you pick, the project must include:

| # | Capability | How it's verified |
|---|-----------|-------------------|
| 1 | REST API with at least 8 endpoints | Routes file / OpenAPI |
| 2 | PostgreSQL with at least 4 related tables | Migration files |
| 3 | Migrations that can run forward from scratch | `alembic upgrade head` works on empty DB |
| 4 | JWT-based authentication | `/auth/register` + `/auth/login` |
| 5 | At least one non-trivial authorization rule | Demo'd live |
| 6 | Input validation with proper 4xx errors | Tests covering bad input |
| 7 | Structured logs with request correlation IDs | Show logs in demo |
| 8 | Redis cache used somewhere meaningful | Before/after measurement |
| 9 | Test suite ≥70% coverage on service-layer code | `pytest --cov` report |
| 10 | Dockerfile + docker-compose.yml | `docker compose up` brings full stack up |
| 11 | CI pipeline (lint + tests) on every push | GitHub Actions, green on main |
| 12 | Deployed to AWS EC2 via Terraform | `terraform apply` brings it up, mentor curls the public IP |
| 13 | Clear README with setup, run, and deploy instructions | Mentor follows it from scratch |

---

## Stretch Goals (Pick at Most One)

If you finish core early, **don't add more features**. Pick one of these to deepen the project instead:

- **Observability:** add Prometheus metrics + a basic Grafana dashboard.
- **Async work:** add a Celery worker for one of the slower operations (with Redis as the broker — already in your stack).
- **WebSocket / SSE:** push live updates for one resource type with FastAPI's WebSocket support.
- **Infrastructure depth:** extend the Terraform setup — move state to an S3 backend, add an Application Load Balancer with HTTPS via ACM, swap the in-instance Postgres for managed RDS (`db.t3.micro` is free-tier eligible for 12 months).

The grading rubric rewards depth over breadth. A small project done thoroughly beats a sprawling project done shallowly.

---

## Submission

When done, submit a single message to the mentor with:

1. Public repo URL.
2. Deployed service URL.
3. Demo time slot.
4. One paragraph: what you're proud of, and what you'd do differently with another week.
