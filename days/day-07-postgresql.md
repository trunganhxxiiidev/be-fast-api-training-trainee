# Day 7 — PostgreSQL Fundamentals

> **Week 2 · Day 7** · ~7 hours · [← Week overview](../week-2-backend-core.md)

## Objective

Get comfortable thinking in tables, keys, and constraints. By the end of the day you should be able to design a small relational schema from first principles, write queries by hand, read an `EXPLAIN ANALYZE` output, and know when adding an index will help vs. hurt.

## Why this matters

The ORM (you'll meet SQLAlchemy tomorrow) doesn't save you from understanding the database. It just changes which mistakes you make. The most expensive production bugs come from people who never learned what a foreign key actually does or what makes a query slow. Today is your chance to learn that without the ORM in the way.

## Concepts

**Install + connect**

```bash
# Easiest: Docker
docker run --name pg -e POSTGRES_PASSWORD=dev -p 5432:5432 -d postgres:16

# Connect
psql postgres://postgres:dev@localhost:5432/postgres
```

`psql` is the official CLI. You'll use it constantly. Survival kit:
- `\l` — list databases.
- `\c dbname` — connect to a database.
- `\dt` — list tables.
- `\d users` — describe the `users` table (columns, types, indexes, FKs).
- `\df` — list functions.
- `\timing` — show query duration. Toggle on.
- `\?` — help.

**Schema design — the building blocks**

```sql
CREATE TABLE users (
    id          BIGSERIAL PRIMARY KEY,
    email       TEXT NOT NULL UNIQUE,
    name        TEXT NOT NULL,
    role        TEXT NOT NULL DEFAULT 'member' CHECK (role IN ('member', 'admin')),
    created_at  TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE TABLE posts (
    id          BIGSERIAL PRIMARY KEY,
    user_id     BIGINT NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    title       TEXT NOT NULL,
    body        TEXT NOT NULL,
    published   BOOLEAN NOT NULL DEFAULT FALSE,
    created_at  TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX idx_posts_user_id ON posts(user_id);
CREATE INDEX idx_posts_published_created ON posts(published, created_at DESC) WHERE published = TRUE;
```

Things to notice:
- **`BIGSERIAL`** auto-increments and uses 64 bits. `SERIAL` runs out after 2 billion — don't.
- **`TEXT`** in Postgres has no performance penalty vs. `VARCHAR(n)`. Just use `TEXT`.
- **`TIMESTAMPTZ`** stores UTC with timezone awareness. *Always* prefer it over `TIMESTAMP`.
- **`NOT NULL DEFAULT ...`** is your friend. Forgetting `NOT NULL` is the single most common schema mistake.
- **`REFERENCES ... ON DELETE CASCADE`** declares the relationship *and* the cleanup rule. Other options: `RESTRICT`, `SET NULL`, `SET DEFAULT`.
- **`CHECK`** constraints enforce invariants at the DB level. Use them for finite enums and simple ranges.
- **Partial indexes** (the `WHERE` clause above) are tiny and fast for "only published posts" queries.

**Normalization in plain English**

- **1NF**: no repeating groups in a column. One value per cell. (Don't put `"tag1,tag2,tag3"` in a column.)
- **2NF**: no partial dependencies on a composite key. Rarely matters in practice.
- **3NF**: non-key columns depend on the key, the whole key, and nothing but the key. Translation: don't store `user_email` in `posts` just because you have it handy — `posts.user_id` already gives you that, and now `user_email` will drift out of sync.

When to *denormalize*: read-heavy hot paths where the join cost dominates. Be deliberate. Add tests.

**Transactions**

```sql
BEGIN;
UPDATE accounts SET balance = balance - 100 WHERE id = 1;
UPDATE accounts SET balance = balance + 100 WHERE id = 2;
COMMIT;
```

ACID — Atomicity, Consistency, Isolation, Durability. The two you'll care about daily:
- **Atomicity**: both updates happen or neither. `ROLLBACK` undoes.
- **Isolation**: concurrent transactions don't see each other's half-finished state. Postgres default is `READ COMMITTED`. You'll occasionally need `SERIALIZABLE` (rare) or `REPEATABLE READ` (also rare).

`SELECT ... FOR UPDATE` locks rows for the rest of the transaction. Use it when you read-then-write the same row and must avoid races.

**Indexes — the 80/20**

- Postgres uses B-tree indexes by default. Great for equality and range queries.
- An index on `(a, b, c)` can serve queries filtering on `a`, on `(a, b)`, on `(a, b, c)`, but **not** on `b` alone. Column order matters.
- Every index makes writes slower. Don't index "just in case."
- The query planner decides whether to use an index. Sometimes it picks a sequential scan because the table is tiny — that's fine.

**`EXPLAIN` and `EXPLAIN ANALYZE`**

```sql
EXPLAIN ANALYZE
SELECT p.* FROM posts p
JOIN users u ON p.user_id = u.id
WHERE u.email = 'alice@example.com'
ORDER BY p.created_at DESC
LIMIT 10;
```

`EXPLAIN` shows the planned query plan. `EXPLAIN ANALYZE` *actually runs* it and shows real timing. Read it as a tree (bottom up):
- **Seq Scan** = full table read. Bad on large tables for selective queries.
- **Index Scan** / **Bitmap Index Scan** = using an index.
- **Hash Join** / **Nested Loop** = how tables get combined.

Paste the output into **https://explain.dalibo.com** for a visual tree.

## Required reading

1. **PostgreSQL Tutorial — Constraints** — https://www.postgresqltutorial.com/postgresql-tutorial/postgresql-primary-key/ — primary keys, foreign keys, check, unique, not null.
2. **Use The Index, Luke!** — https://use-the-index-luke.com — the *only* SQL indexing tutorial you need. Read at least Ch. 1–3.
3. **Postgres docs: `EXPLAIN`** — https://www.postgresql.org/docs/current/using-explain.html — sections 14.1 and 14.2.
4. **Postgres docs: Transaction Isolation** — https://www.postgresql.org/docs/current/transaction-iso.html — short, important.

## Optional reading

- **PostgreSQL Exercises** — https://pgexercises.com — free interactive SQL drills.
- **Postgres docs: Index types** — https://www.postgresql.org/docs/current/indexes-types.html — B-tree, hash, GIN, GiST. Skim.

## Exercises

1. **Design a blog schema** — on paper or in a markdown ER diagram, design tables for: `users`, `posts`, `comments`, `tags`, `post_tags` (the join table). Decide on PKs, FKs, NOT NULLs, defaults, and ON DELETE behaviors. Commit the diagram to `journal/day-07-er-diagram.md`.

2. **Implement it** — write a single `schema.sql` file with `CREATE TABLE` statements. Apply it: `psql ... -f schema.sql`. Then `\dt` to verify.

3. **Seed data** — write `seed.sql` that inserts:
   - 3 users
   - 10 posts across them
   - 25 comments across the posts
   - 5 tags, with each post having 1–3 tags

4. **Query drills** — write SQL by hand (no AI assist) and put the queries + outputs in `journal/day-07-queries.md`:
   - All posts by a specific user, newest first.
   - Top 5 most-commented posts in the last 7 days.
   - Average number of comments per post.
   - All tags a given user has used.
   - Posts that have *no* comments.

5. **Indexing exercise**
   - Run `EXPLAIN ANALYZE` on the "top 5 most-commented posts" query. Note the cost and scan type.
   - Add an appropriate index.
   - Re-run. Paste the before/after into your journal.

## Common pitfalls

- **`VARCHAR(255)` everywhere** — meaningless in Postgres. Use `TEXT`.
- **Storing timestamps without timezone** (`TIMESTAMP` instead of `TIMESTAMPTZ`) — eventually causes data loss across deploys in different timezones.
- **Forgetting `ON DELETE`** — when you delete a user, what happens to their posts? Decide explicitly.
- **Indexing tiny tables** — Postgres will sequential-scan them anyway, and you've just added write overhead.
- **Implicit casts in `WHERE`** — `WHERE created_at::date = '2026-01-01'` defeats the index on `created_at`. Use a range: `WHERE created_at >= '2026-01-01' AND created_at < '2026-01-02'`.
- **Using `SELECT *` in production code** — fine in `psql`. In code, name the columns; otherwise schema changes break callers silently.

## Self-check

1. What's the difference between `UNIQUE` and `PRIMARY KEY`?
2. You add `CREATE INDEX ON posts(created_at);`. Why might a query with `WHERE created_at > '2026-01-01'` still do a sequential scan?
3. Walk through what `ON DELETE CASCADE` vs `ON DELETE SET NULL` do, and when you'd pick each.
4. What is the N+1 query problem? (Preview — you'll see it tomorrow with SQLAlchemy.)
5. Two transactions both run `UPDATE counters SET n = n + 1 WHERE id = 1`. Will the result always be `n + 2`? Why?
6. When would you choose to denormalize?

## Definition of done

- [ ] ER diagram committed.
- [ ] `schema.sql` applied successfully; `\dt` shows your tables.
- [ ] `seed.sql` populates non-trivial data.
- [ ] Query drill answers in your journal — SQL + actual output.
- [ ] At least one `EXPLAIN ANALYZE` before/after showing an index helped.
- [ ] PR merged.
