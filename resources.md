# Resources

Curated, not exhaustive. Pick what you need — don't try to read everything.

---

## Books (free or available online)

- **Pro Git** — Scott Chacon. https://git-scm.com/book/en/v2 — skim ch. 1–3, deep read ch. 7 (rebasing, reset).
- **Designing Data-Intensive Applications** — Martin Kleppmann. Heavy but the chapters on replication and transactions are worth it eventually. Not a week-one read.
- **The Twelve-Factor App** — https://12factor.net — read it twice during the program.

---

## Python

- **FastAPI docs** — https://fastapi.tiangolo.com — the tutorial alone covers 80% of what you need.
- **Pydantic v2 docs** — https://docs.pydantic.dev/latest/
- **SQLAlchemy 2.0 tutorial** — https://docs.sqlalchemy.org/en/20/tutorial/ — the only ORM doc you need.
- **Alembic docs** — https://alembic.sqlalchemy.org/en/latest/ — short, read end-to-end.
- **uv** — https://docs.astral.sh/uv/ — fast Python package manager. Recommended.
- **Real Python** — https://realpython.com — good for filling specific gaps.

---

## Databases

- **Use the Index, Luke!** — https://use-the-index-luke.com — the only SQL indexing tutorial you actually need.
- **PostgreSQL EXPLAIN visualizer** — https://explain.dalibo.com — paste an `EXPLAIN ANALYZE` output and see it as a tree.
- **PostgreSQL official docs** — https://www.postgresql.org/docs/current/ — reach for it when you hit a real question, not as a tutorial.

---

## HTTP / REST

- **MDN HTTP docs** — https://developer.mozilla.org/en-US/docs/Web/HTTP — the authoritative reference.
- **RESTful Web APIs** — Leonard Richardson. Older but the model still holds up.
- **httpstat.us** — https://httpstat.us — return any status code for testing.

---

## Testing

- **Practical Test Pyramid** — Ham Vocke. https://martinfowler.com/articles/practical-test-pyramid.html
- **pytest docs** — https://docs.pytest.org/en/stable/
- **`pytest-asyncio`** — https://pytest-asyncio.readthedocs.io/ — for testing FastAPI async routes.

---

## Docker

- **Docker docs — get started** — https://docs.docker.com/get-started/
- **Play with Docker** — https://labs.play-with-docker.com — free sandbox.

---

## Terraform & AWS

- **Terraform tutorials — AWS Get Started** — https://developer.hashicorp.com/terraform/tutorials/aws-get-started — official, 30 min total, do it once.
- **Terraform AWS Provider docs** — https://registry.terraform.io/providers/hashicorp/aws/latest/docs — reach for it constantly.
- **AWS Free Tier overview** — https://aws.amazon.com/free/ — bookmark this; check what counts.
- **AWS EC2 user guide** — https://docs.aws.amazon.com/ec2/ — skim the "instance lifecycle" and "security groups" sections.
- **`terraform fmt` / `terraform validate`** — run them like you run a linter.

---

## Security (don't skip)

- **OWASP Top 10** — https://owasp.org/www-project-top-ten/ — read each item once.
- **Have I Been Pwned: Password Hashing** — https://crackstation.net/hashing-security.htm
- **JWT pitfalls** — https://blog.codinghorror.com/why-jwts-are-bad-for-authentication/ — read the counter-arguments too.

---

## Newsletters / staying current (optional)

- **Pointer** — weekly engineering newsletter, mostly senior-level reading.
- **Bytebytego** — diagrams + explainers for distributed-systems-y topics.

---

## What *not* to do

- Don't watch 10-hour "complete Python course" YouTube videos. Read docs, then build.
- Don't subscribe to 30 newsletters. One is enough.
- Don't copy-paste from ChatGPT/Claude without reading the output line by line and being able to explain it.
- Don't read books cover to cover. Read the chapter that solves your current problem.
