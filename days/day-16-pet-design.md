# Day 16 — Pet Project: Design

> **Week 4 · Day 16** · ~6 hours · [← Week overview](../week-4-pet-project.md)

## Objective

Pick one of the pet project options (or propose your own), then write a 1-page design doc that the mentor reviews and approves before you write a single line of project code.

## Why this matters

Writing code is fast. Writing the *wrong* code is faster. Every senior engineer has built something for two weeks before realizing the schema or the API shape was wrong, and that's expensive. The design doc is the cheapest possible artifact for getting feedback — you can rewrite it in 30 minutes. You cannot rewrite a wired-up codebase in 30 minutes.

For this project specifically, the design doc is your contract: it locks down the scope so the mentor can give an honest "passes / doesn't pass" judgment on Day 20.

## Concepts

**What a senior dev looks for in a design doc**

1. **A clear problem statement** — one paragraph, no jargon. "I'm building X because Y."
2. **Explicit non-goals** — the things you're *not* building. The mentor will hold you to this.
3. **The data model** — entities, relationships, and the columns that matter. Decisions made: PK type, soft-delete vs hard, what's indexed.
4. **The API surface** — every endpoint, every method, every status code. If it's not in the doc, it's not in the project.
5. **The auth model** — who can do what. RBAC roles named.
6. **Open questions** — things you genuinely don't know yet. Better to flag them than to silently guess.
7. **Risks** — what could turn into a Day-19 emergency.

Length: aim for one to two pages. Three is too long; half a page is too short.

**The pet project options (recap)**

From [`pet-project-spec.md`](../pet-project-spec.md):
- **Option A: URL Shortener with Analytics** — DB design + caching + analytics rollup + rate limiting.
- **Option B: Team Task Manager** — heavy authorization rules, foreign keys, query design.
- **Option C: Personal Finance Tracker** — file handling, idempotency, aggregation, money math.

You can also **propose your own** if it covers all 13 required capabilities. The mentor must approve before Day 17.

**Mandatory items every design doc must address** (from [pet-project-spec.md](../pet-project-spec.md)):
- At least 8 endpoints.
- At least 4 related tables.
- JWT auth + at least one non-trivial authorization rule.
- Redis cache used somewhere meaningful.
- Migrations, Docker, CI, Terraform deploy, tests ≥70% coverage on services.

## Required reading

1. **Google's design doc template** — https://www.industrialempathy.com/posts/design-docs-at-google/ — the canonical "what goes in a design doc" article. Lift the structure.
2. **The Anti-Plan** — https://lethain.com/anti-plan/ — when *not* to over-design.
3. **DBML or Mermaid ER syntax** — pick one for the ER diagram. Mermaid renders in GitHub: https://mermaid.js.org/syntax/entityRelationshipDiagram.html

## Optional reading

- **API design checklist** — https://github.com/stoplightio/spectral — formal API linting. Overkill for the pet project, useful to know exists.
- **Choosing a database key strategy** — https://shopify.engineering/building-resilient-payment-systems — Shopify's take on UUID vs serial vs ULID. Light read.

## Design-doc template

Save this as `pet-project/DESIGN.md` and fill it in:

```markdown
# <Project Name> — Design Doc

**Author:** <your name>
**Mentor:** Nathan Pham
**Status:** Draft → In Review → Approved
**Last updated:** YYYY-MM-DD

## 1. Problem
One paragraph. What does this service do, and for whom?

## 2. Goals
- Bullet list of measurable goals.

## 3. Non-goals
- Things you are explicitly *not* building.
- Be aggressive here. Cutting scope is the most useful thing you'll do today.

## 4. Data model
Mermaid ER diagram, then 1-line descriptions of each table and the rationale for the non-obvious columns.

```mermaid
erDiagram
    users ||--o{ posts : "writes"
    posts ||--o{ comments : "has"
    ...
```

## 5. API surface
A table covering every endpoint:

| Method | Path | Auth | Request | Response | Status |
|--------|------|------|---------|----------|--------|
| POST   | /auth/register | – | `{email, password, name}` | `UserOut` | 201, 409 |
| ...    | ...  | ... | ...     | ...      | ...    |

## 6. Auth & authorization
- Token type (JWT), expiry.
- Roles and what each can do.
- At least one non-trivial rule, called out (e.g. "only the team's admin can delete a task created by another team member").

## 7. Caching
- Which endpoint is cached, with what TTL, invalidated on what events.
- One sentence on why caching helps this endpoint specifically.

## 8. Background work (if any)
- What runs in the background, on what schedule, in what failure mode.

## 9. Deployment
- Single EC2 + Docker Compose, same pattern as Day 15. Note anything different.

## 10. Open questions
- Things you don't know yet. Resolve them before Day 17 if possible.

## 11. Risks
- Things that could blow up the schedule. One sentence each.
```

## Exercises

1. **Pick** one of the three options (or propose your own). Write it in your `journal/day-16.md` with a one-sentence justification.

2. **Draft `pet-project/DESIGN.md`** following the template. Take your time — aim for 90 minutes of focused writing.

3. **Self-review** before sending to the mentor. Check:
   - Could a stranger build this from the doc alone?
   - Did you name every status code for every endpoint?
   - Is the ER diagram complete (all FKs, all NOT NULLs)?
   - Did you explicitly cover all 13 required capabilities (see [pet-project-spec.md](../pet-project-spec.md))?
   - Did you list at least 3 non-goals?

4. **Get feedback** — submit to the mentor by 3 PM. Iterate. The doc needs **Approved** status before you leave today.

5. **Repo setup** — once approved, initialize the repo:
   ```bash
   gh repo create intern-pet-project --public
   cd intern-pet-project
   git init -b main
   uv init && uv add fastapi 'sqlalchemy[asyncio]' asyncpg alembic pydantic-settings python-jose passlib redis structlog
   uv add --dev pytest pytest-asyncio httpx ruff pre-commit
   cp /path/to/DESIGN.md ./DESIGN.md
   # ... copy your week-3 Dockerfile, docker-compose.yml, terraform/ as starting points
   git add . && git commit -m "feat: scaffold project + design doc"
   git push -u origin main
   ```

## Common pitfalls

- **Over-scoping** — you have 4 days. If your design has 25 endpoints, cut it now. The grading rewards depth, not breadth.
- **Skipping non-goals** — without them, scope creep starts on Day 17.
- **Glossing over the auth rule** — "users can edit their own resources" isn't non-trivial. "Only the original creator OR an admin OR a team member with the editor role can edit, but only during the first 24 hours" is.
- **Writing the doc *after* coding** — the doc loses its purpose. Write it first.
- **No mentor review before coding** — you'll spend Day 17 building the wrong thing.
- **Pretending you have no open questions** — every project has them. Listing them is a sign of seniority, not weakness.

## Self-check

1. If a different engineer picked up your design doc tomorrow, what one thing would they ask first?
2. Which capability from the [13 required](../pet-project-spec.md#required-capabilities) is least obvious from your design? Could you defend it?
3. What's the riskiest assumption in your design? What's your fallback if it turns out to be wrong?
4. Why is the auth rule you picked "non-trivial"? Defend it in one sentence.
5. What changes about your design if your test coverage target dropped from 70% to 50%? If it rose to 95%?
6. What did you cut from the original idea, and why?

## Definition of done

- [ ] Option chosen and justified.
- [ ] `DESIGN.md` complete with ER diagram + API table.
- [ ] All 13 required capabilities explicitly covered.
- [ ] At least 3 non-goals listed.
- [ ] Mentor has marked the doc **Approved**.
- [ ] Repo initialized, initial commit pushed.
