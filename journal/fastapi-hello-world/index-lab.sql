DROP TABLE IF EXISTS index_lab_comments;
DROP TABLE IF EXISTS index_lab_posts;
DROP TABLE IF EXISTS index_lab_users;

CREATE TABLE index_lab_users (
    id BIGSERIAL PRIMARY KEY,
    email TEXT NOT NULL UNIQUE,
    name TEXT NOT NULL,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE TABLE index_lab_posts (
    id BIGSERIAL PRIMARY KEY,
    user_id BIGINT NOT NULL REFERENCES index_lab_users(id) ON DELETE CASCADE,
    title TEXT NOT NULL,
    published BOOLEAN NOT NULL DEFAULT FALSE,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE TABLE index_lab_comments (
    id BIGSERIAL PRIMARY KEY,
    post_id BIGINT NOT NULL REFERENCES index_lab_posts(id) ON DELETE CASCADE,
    body TEXT NOT NULL,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

INSERT INTO index_lab_users (email, name, created_at)
SELECT
    'user' || n || '@example.com',
    'User ' || n,
    NOW() - (n || ' hours')::interval
FROM generate_series(1, 1000) AS n;

INSERT INTO index_lab_posts (user_id, title, published, created_at)
SELECT
    ((n - 1) % 1000) + 1,
    'Post ' || n,
    n % 3 <> 0,
    NOW() - (n || ' minutes')::interval
FROM generate_series(1, 50000) AS n;

INSERT INTO index_lab_comments (post_id, body, created_at)
SELECT
    ((n - 1) % 50000) + 1,
    'Comment ' || n,
    NOW() - (n || ' seconds')::interval
FROM generate_series(1, 300000) AS n;

ANALYZE index_lab_users;
ANALYZE index_lab_posts;
ANALYZE index_lab_comments;

-- 1. Before index: user feed query.
EXPLAIN ANALYZE
SELECT id, title, created_at
FROM index_lab_posts
WHERE user_id = 42
ORDER BY created_at DESC
LIMIT 20;

CREATE INDEX idx_lab_posts_user_created ON index_lab_posts(user_id, created_at DESC);
ANALYZE index_lab_posts;

-- 2. After composite index: should use idx_lab_posts_user_created.
EXPLAIN ANALYZE
SELECT id, title, created_at
FROM index_lab_posts
WHERE user_id = 42
ORDER BY created_at DESC
LIMIT 20;

-- 3. Composite index column order: this can use the index because user_id is first.
EXPLAIN ANALYZE
SELECT id, title, created_at
FROM index_lab_posts
WHERE user_id = 42
  AND created_at >= NOW() - INTERVAL '7 days'
ORDER BY created_at DESC
LIMIT 20;

-- 4. This usually cannot use idx_lab_posts_user_created efficiently because it filters only on created_at.
EXPLAIN ANALYZE
SELECT id, title, created_at
FROM index_lab_posts
WHERE created_at >= NOW() - INTERVAL '7 days'
ORDER BY created_at DESC
LIMIT 20;

CREATE INDEX idx_lab_posts_created ON index_lab_posts(created_at DESC);
ANALYZE index_lab_posts;

-- 5. After a created_at-only index, the created_at-only query has a suitable index.
EXPLAIN ANALYZE
SELECT id, title, created_at
FROM index_lab_posts
WHERE created_at >= NOW() - INTERVAL '7 days'
ORDER BY created_at DESC
LIMIT 20;

-- 6. Partial index: useful when most queries only care about published posts.
CREATE INDEX idx_lab_posts_published_created
ON index_lab_posts(created_at DESC)
WHERE published = TRUE;
ANALYZE index_lab_posts;

EXPLAIN ANALYZE
SELECT id, title, created_at
FROM index_lab_posts
WHERE published = TRUE
ORDER BY created_at DESC
LIMIT 20;

-- 7. Bad predicate: casting the indexed column can block normal index usage.
EXPLAIN ANALYZE
SELECT COUNT(*)
FROM index_lab_posts
WHERE created_at::date = CURRENT_DATE;

-- 8. Better predicate: use a range so the b-tree index can be used.
EXPLAIN ANALYZE
SELECT COUNT(*)
FROM index_lab_posts
WHERE created_at >= CURRENT_DATE
  AND created_at < CURRENT_DATE + INTERVAL '1 day';

-- 9. Comment-count query before and after a join/filter index.
DROP INDEX IF EXISTS idx_lab_comments_created_post;
ANALYZE index_lab_comments;

EXPLAIN ANALYZE
SELECT p.id, p.title, COUNT(c.id) AS comment_count
FROM index_lab_posts p
LEFT JOIN index_lab_comments c
  ON c.post_id = p.id
 AND c.created_at >= NOW() - INTERVAL '1 day'
GROUP BY p.id, p.title
ORDER BY comment_count DESC, p.id
LIMIT 10;

CREATE INDEX idx_lab_comments_created_post ON index_lab_comments(created_at, post_id);
ANALYZE index_lab_comments;

EXPLAIN ANALYZE
SELECT p.id, p.title, COUNT(c.id) AS comment_count
FROM index_lab_posts p
LEFT JOIN index_lab_comments c
  ON c.post_id = p.id
 AND c.created_at >= NOW() - INTERVAL '1 day'
GROUP BY p.id, p.title
ORDER BY comment_count DESC, p.id
LIMIT 10;
