# Week 4 — Pet Project

**Goal:** Apply everything from weeks 1–3 to build a single, end-to-end project from scratch. No more guided exercises — this is solo work with mentor check-ins.

Full spec lives in [`pet-project-spec.md`](./pet-project-spec.md).

---

## Day-by-day plan (suggested — adjust as needed)

### Day 16 — Design

- Pick one of the three options in [`pet-project-spec.md`](./pet-project-spec.md) (or propose your own — mentor must approve).
- Write a 1-page design doc covering:
  - **Problem statement** — one paragraph.
  - **API surface** — list of endpoints with method, path, request, response, status codes.
  - **Data model** — ER diagram.
  - **Auth model** — who can do what.
  - **Non-goals** — what you're explicitly *not* building.
- Mentor reviews before code is written. Iterate until approved.

### Day 17 — Scaffold + Database

- Set up the repo: project structure, linter, formatter, `.env.example`, `README.md`.
- Write the initial migration. Get the schema into Postgres.
- Stub out routers/controllers — they can return 501 for now.
- Set up Docker Compose locally.

### Day 18 — Core CRUD + Auth

- Implement auth flow: register, login, JWT issuance, middleware.
- Implement the primary resource CRUD.
- Write tests as you go — don't leave them for the end.

### Day 19 — Secondary Features + Polish

- Implement the secondary feature(s) from your spec.
- Add caching where it makes sense.
- Add structured logging and request IDs.
- Round out test coverage.
- Tidy up the README — install steps, env vars table, example curl commands.

### Day 20 — Deploy + Demo

- Deploy to a free-tier host. Public URL working.
- CI passing on `main`.
- Prepare a 20-minute demo:
  - 5 min: problem + design tradeoffs.
  - 10 min: live walkthrough — hit the API with `curl`/Postman, show logs flowing.
  - 5 min: what you'd do differently next time + Q&A.

---

## Mentor Check-ins

| When | What |
|------|------|
| End of Day 16 | Design doc review. Approved or revised. |
| End of Day 18 | Code review of WIP PR. Focus on structure, naming, test coverage. |
| End of Day 19 | Pre-demo dry run. Catch obvious gaps before the real review. |
| End of Day 20 | Final demo + program retro. |

---

## What "Done" Looks Like

The pet project is considered complete when:

- [ ] Code is in a public GitHub repo with a clear README.
- [ ] `docker compose up` brings the entire stack up locally with one command.
- [ ] CI (GitHub Actions) runs lint + tests on every push, green on `main`.
- [ ] Deployed to a publicly accessible URL.
- [ ] At least 70% test coverage on service-layer code.
- [ ] Auth works end-to-end with a non-trivial authorization rule.
- [ ] Logs are structured and include a per-request correlation ID.
- [ ] You can answer "why did you build it this way?" for every major decision.

---

## What Makes a Great Demo

- **Show, don't tell.** Hit endpoints live. Show the logs streaming. Trigger an error and show how it's handled.
- **Be honest about gaps.** "I ran out of time to add rate limiting — here's where I'd put it" is a better answer than pretending it's done.
- **Have one slide of architecture.** A simple boxes-and-arrows diagram of the components.
- **Don't read code line by line.** Talk about why, not what.
