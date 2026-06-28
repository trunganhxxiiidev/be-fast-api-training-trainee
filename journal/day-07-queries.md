# Day 7 Queries

## Verification Counts

```sql
SELECT 'users' AS table_name, COUNT(*) FROM users
UNION ALL SELECT 'posts', COUNT(*) FROM posts
UNION ALL SELECT 'comments', COUNT(*) FROM comments
UNION ALL SELECT 'tags', COUNT(*) FROM tags
UNION ALL SELECT 'post_tags', COUNT(*) FROM post_tags
ORDER BY table_name;
```

```text
 table_name | count
------------+-------
 comments   |    25
 posts      |    10
 post_tags  |    21
 tags       |     5
 users      |     3
```

## 1. All Posts By A Specific User

```sql
SELECT p.id, p.title, p.published, p.created_at
FROM posts p
JOIN users u ON u.id = p.user_id
WHERE u.email = 'ada@example.com'
ORDER BY p.created_at DESC;
```

```text
 id |            title            | published |       created_at
----+-----------------------------+-----------+------------------------
 10 | Draft API checklist         | f         | 2026-06-14 12:00:00+00
  1 | FastAPI routers in practice | t         | 2026-06-14 09:00:00+00
  2 | Pydantic response models    | t         | 2026-06-13 09:00:00+00
  3 | Service layer notes         | t         | 2026-06-12 09:00:00+00
```

## 2. Top 5 Most-Commented Posts In The Last 7 Days

```sql
WITH recent_comments AS (
    SELECT id, post_id
    FROM comments
    WHERE created_at >= TIMESTAMPTZ '2026-06-07 00:00:00+00'
)
SELECT p.id, p.title, COUNT(rc.id) AS comment_count
FROM posts p
LEFT JOIN recent_comments rc ON rc.post_id = p.id
GROUP BY p.id, p.title
ORDER BY comment_count DESC, p.id
LIMIT 5;
```

```text
 id |            title            | comment_count
----+-----------------------------+---------------
  1 | FastAPI routers in practice |             5
  2 | Pydantic response models    |             4
  3 | Service layer notes         |             3
  4 | PostgreSQL constraints      |             3
  5 | Index basics                |             2
```

## 3. Average Number Of Comments Per Post

```sql
WITH comment_counts AS (
    SELECT p.id, COUNT(c.id) AS comment_count
    FROM posts p
    LEFT JOIN comments c ON c.post_id = p.id
    GROUP BY p.id
)
SELECT ROUND(AVG(comment_count)::numeric, 2) AS avg_comments_per_post
FROM comment_counts;
```

```text
 avg_comments_per_post
-----------------------
                  2.50
```

## 4. All Tags A Given User Has Used

```sql
SELECT DISTINCT t.name
FROM users u
JOIN posts p ON p.user_id = u.id
JOIN post_tags pt ON pt.post_id = p.id
JOIN tags t ON t.id = pt.tag_id
WHERE u.email = 'ada@example.com'
ORDER BY t.name;
```

```text
  name
---------
 backend
 fastapi
 python
```

## 5. Posts That Have No Comments

```sql
SELECT p.id, p.title
FROM posts p
LEFT JOIN comments c ON c.post_id = p.id
WHERE c.id IS NULL
ORDER BY p.id;
```

```text
 id |        title
----+---------------------
 10 | Draft API checklist
```

## EXPLAIN ANALYZE Notes

Dataset chính chỉ có 25 comments, nên Postgres có thể vẫn chọn `Seq Scan` dù có index. Điều đó đúng vì table quá nhỏ.

Với `index-lab.sql`, dữ liệu lớn hơn nên thấy index rõ hơn:

- Query `WHERE user_id = 42 ORDER BY created_at DESC LIMIT 20` trước index dùng `Seq Scan` trên `index_lab_posts`, execution time khoảng `3.729 ms`.
- Sau `CREATE INDEX idx_lab_posts_user_created ON index_lab_posts(user_id, created_at DESC)`, cùng query dùng `Index Scan`, execution time khoảng `0.195 ms`.
- Query chỉ filter `created_at` không dùng tốt composite index `(user_id, created_at)` vì `created_at` không phải cột đầu.
- Sau `CREATE INDEX idx_lab_posts_created ON index_lab_posts(created_at DESC)`, query `created_at >= ... ORDER BY created_at DESC` dùng `Index Scan`, execution time khoảng `0.291 ms`.
- Predicate xấu `created_at::date = CURRENT_DATE` dùng `Seq Scan`; predicate range `created_at >= CURRENT_DATE AND created_at < CURRENT_DATE + INTERVAL '1 day'` dùng `Index Only Scan`.
