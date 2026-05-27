# Backend Intern Training Program — 1 Month

**Mentor:** Nathan Pham (Senior Backend Developer)
**Duration:** 4 weeks (20 working days)
**Stack:** Python · FastAPI · SQLAlchemy · PostgreSQL · Docker · Terraform · AWS EC2 (free tier)
**Format:** Self-paced learning + daily 30-min sync + weekly review

---

## Goals

By the end of this program, the intern should be able to:

1. Build a production-style REST API from scratch with **FastAPI + SQLAlchemy + PostgreSQL**.
2. Design a normalized relational schema, write Alembic migrations, and query it through SQLAlchemy 2.0.
3. Write and run automated tests (unit + integration) with reasonable coverage.
4. Containerize an application with Docker and run it with `docker compose`.
5. Provision a real cloud server with **Terraform** and deploy to an **AWS EC2 free-tier** instance.
6. Follow a professional Git workflow (feature branches, PRs, code review).
7. Understand and explain core backend concepts: HTTP, REST, auth, caching, async I/O, logging.

The final examination is a **pet project** (see [`pet-project-spec.md`](./pet-project-spec.md)) that exercises every topic from the course.

---

## Curriculum Overview

| Week | Theme | Deliverable |
|------|-------|-------------|
| [Week 1](./week-1-fundamentals.md) | Foundations: Python, Git, HTTP, FastAPI basics | "Hello API" — a tested FastAPI echo service |
| [Week 2](./week-2-backend-core.md) | FastAPI + SQLAlchemy + Postgres + auth | CRUD service backed by PostgreSQL with JWT auth |
| [Week 3](./week-3-advanced.md) | Testing, Docker, caching, Terraform + EC2 | Containerized service deployed to AWS EC2 via Terraform |
| [Week 4](./week-4-pet-project.md) | Pet project + final review | Pet project demo + code walkthrough |

---

## Daily Rhythm

| Time | Activity |
|------|----------|
| 09:00 – 09:15 | Daily standup (yesterday / today / blockers) |
| 09:15 – 12:00 | Reading + exercises |
| 13:00 – 17:00 | Hands-on coding |
| 17:00 – 17:30 | Push WIP branch, write a short log entry in `/journal/YYYY-MM-DD.md` |
| Friday 16:00 | Weekly review with mentor — demo + retro |

---

## Ground Rules

- **Commit often.** Small, focused commits beat one giant commit at end of day.
- **Ask after 30 minutes of being stuck.** Don't burn a whole afternoon silent — ask in chat with what you tried.
- **Read the error before Googling it.** Stack traces usually point at the answer.
- **No copy-paste from AI without understanding.** If you can't explain it line by line in standup, you can't use it.
- **Write tests for anything non-trivial.** "It worked on my machine" is not a deliverable.
- **Keep a journal.** One markdown file per day under `journal/` with what you learned, what blocked you, and one question.

---

## Repository Layout

```
intern-training/
├── README.md                  ← this file
├── course-mindmap.md          ← mermaid mindmap + clickable nav graph
├── course-map.html            ← interactive mindmap (open in browser)
├── week-1-fundamentals.md     ← week-at-a-glance pages
├── week-2-backend-core.md
├── week-3-advanced.md
├── week-4-pet-project.md
├── days/                      ← detailed daily lesson files
│   ├── day-01-environment-git.md
│   ├── day-02-python-refresher.md
│   ├── ...
│   └── day-20-pet-demo.md
├── pet-project-spec.md        ← final examination spec
├── resources.md               ← curated reading/video list
├── evaluation-rubric.md       ← how the mentor scores the program
└── journal/                   ← intern's daily log entries (created day 1)
```

> **Tip:** open [`course-map.html`](./course-map.html) in a browser for an interactive mindmap where every day-node links straight to its detailed lesson.

## Daily index

| Week | Day | Topic |
|------|-----|-------|
| 1 | [Day 1](./days/day-01-environment-git.md) | Environment, Shell & Git |
| 1 | [Day 2](./days/day-02-python-refresher.md) | Python Refresher |
| 1 | [Day 3](./days/day-03-http-rest.md) | HTTP & REST |
| 1 | [Day 4](./days/day-04-async-fastapi.md) | Async Python & FastAPI Fundamentals |
| 1 | [Day 5](./days/day-05-hello-api.md) | Hello API *(deliverable)* |
| 2 | [Day 6](./days/day-06-fastapi-deep-dive.md) | FastAPI Deep Dive |
| 2 | [Day 7](./days/day-07-postgresql.md) | PostgreSQL Fundamentals |
| 2 | [Day 8](./days/day-08-sqlalchemy.md) | SQLAlchemy 2.0 |
| 2 | [Day 9](./days/day-09-alembic.md) | Alembic Migrations |
| 2 | [Day 10](./days/day-10-auth.md) | Authentication & Authorization *(deliverable)* |
| 3 | [Day 11](./days/day-11-testing.md) | Automated Testing |
| 3 | [Day 12](./days/day-12-logging.md) | Logging, Errors & Observability |
| 3 | [Day 13](./days/day-13-docker.md) | Docker & docker compose |
| 3 | [Day 14](./days/day-14-caching.md) | Caching & Async Work |
| 3 | [Day 15](./days/day-15-terraform-ec2.md) | Terraform + AWS EC2 *(deliverable)* |
| 4 | [Day 16](./days/day-16-pet-design.md) | Pet Project: Design |
| 4 | [Day 17](./days/day-17-pet-scaffold.md) | Pet Project: Scaffold & Database |
| 4 | [Day 18](./days/day-18-pet-crud-auth.md) | Pet Project: CRUD + Auth |
| 4 | [Day 19](./days/day-19-pet-polish.md) | Pet Project: Polish |
| 4 | [Day 20](./days/day-20-pet-demo.md) | Pet Project: Deploy & Demo *(final)* |

---

## Success Criteria

The internship is considered successful if, at the end of week 4, the intern can:

- Demo a working pet project hosted in a container.
- Walk through the code unprompted and explain every design decision.
- Pass a 30-minute Q&A on the curriculum topics (see [`evaluation-rubric.md`](./evaluation-rubric.md)).
- Submit a clean PR — clear title, scoped commits, passing CI, useful description.

Anything less than that is fine — the goal is honest learning, not theatrical output. We adjust the next iteration of this curriculum based on what landed and what didn't.
