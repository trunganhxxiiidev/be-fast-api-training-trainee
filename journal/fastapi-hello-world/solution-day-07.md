# Solution: Day 7 PostgreSQL Fundamentals

File này là bài giải mẫu cho Day 7. Đừng chỉ copy-paste: hãy chạy từng bước, đọc lỗi nếu có, và tự giải thích được vì sao mỗi table/index tồn tại.

## 1. Start PostgreSQL

Chạy PostgreSQL bằng Docker:

```bash
docker run --name pg-day-07 \
  -e POSTGRES_PASSWORD=dev \
  -e POSTGRES_DB=day07_blog \
  -p 5432:5432 \
  -d postgres:16
```

Nếu container đã tồn tại:

```bash
docker start pg-day-07
```

Kết nối:

```bash
psql postgres://postgres:dev@localhost:5432/day07_blog
```

Thoát `psql`:

```text
\q
```

## 2. ER Design

Schema blog có 5 table:

```text
users
posts
comments
tags
post_tags
```

Quan hệ:

```mermaid
erDiagram
    users ||--o{ posts : writes
    users ||--o{ comments : writes
    posts ||--o{ comments : has
    posts ||--o{ post_tags : has
    tags ||--o{ post_tags : labels
```

Giải thích quyết định:

- `posts.user_id ON DELETE CASCADE`: nếu user bị xóa, post của user đó không còn owner hợp lệ.
- `comments.post_id ON DELETE CASCADE`: nếu post bị xóa, comment trong post đó cũng nên bị xóa.
- `comments.user_id ON DELETE SET NULL`: nếu user bị xóa, có thể giữ comment như nội dung lịch sử, nhưng mất author.
- `tags.name UNIQUE`: không nên có hai tag `python`.
- `post_tags PRIMARY KEY (post_id, tag_id)`: chặn gắn cùng một tag vào cùng một post hai lần.

## 3. Apply Schema

Từ thư mục project:

```bash
cd ~/Training/D1/be-fast-api-training-trainee/journal/fastapi-hello-world
psql postgres://postgres:dev@localhost:5432/day07_blog -f schema.sql
```

Verify:

```bash
psql postgres://postgres:dev@localhost:5432/day07_blog
```

Trong `psql`:

```sql
\dt
\d users
\d posts
\d comments
\d tags
\d post_tags
```

Kỳ vọng có 5 table.

## 4. Schema SQL

File runnable đã được tạo ở `schema.sql`.

Điểm cần hiểu:

- `BIGSERIAL PRIMARY KEY`: id tự tăng, dùng integer 64-bit.
- `TEXT`: đủ tốt cho text trong Postgres, không cần `VARCHAR(255)` nếu không có rule nghiệp vụ.
- `TIMESTAMPTZ`: timestamp có timezone, an toàn hơn `TIMESTAMP`.
- `CHECK (role IN (...))`: database tự chặn role sai.
- `ON DELETE CASCADE`: xóa parent thì child liên quan bị xóa theo.
- `ON DELETE SET NULL`: xóa user nhưng giữ comment, author thành `NULL`.

## 4.1 Normalization: Vì Sao Phải Chuẩn Hóa?

Chuẩn hóa là cách tách dữ liệu thành các bảng đúng trách nhiệm để tránh lặp dữ liệu, dữ liệu lệch nhau và update khó kiểm soát.

Ví dụ thiết kế xấu:

```sql
CREATE TABLE bad_posts (
    id BIGSERIAL PRIMARY KEY,
    user_email TEXT NOT NULL,
    user_name TEXT NOT NULL,
    title TEXT NOT NULL,
    tags TEXT NOT NULL,
    comment_1 TEXT,
    comment_2 TEXT,
    comment_3 TEXT
);
```

Vấn đề:

- `user_email`, `user_name` bị lặp ở mọi post. User đổi tên thì phải update nhiều row.
- `tags` dạng `"python,sql"` vi phạm 1NF vì một cột chứa nhiều giá trị.
- `comment_1`, `comment_2`, `comment_3` là repeating groups. Nếu post có 4 comments thì schema gãy.
- Không có foreign key nên database không biết post/comment thuộc về user nào hợp lệ.

Thiết kế chuẩn hơn:

```text
users(id, email, name)
posts(id, user_id, title, body)
comments(id, post_id, user_id, body)
tags(id, name)
post_tags(post_id, tag_id)
```

Mapping theo normal forms:

- 1NF: mỗi cell chỉ có một giá trị. Tags không nằm trong một string, mà tách sang `tags` và `post_tags`.
- 2NF: bảng join `post_tags` chỉ có dữ liệu phụ thuộc vào toàn bộ khóa `(post_id, tag_id)`.
- 3NF: `posts` không lưu `user_email` hay `user_name`; các field đó phụ thuộc vào `users.id`, không phụ thuộc trực tiếp vào `posts.id`.

Test nhanh để thấy constraint bảo vệ dữ liệu:

```sql
-- Fail vì duplicate email, nhờ UNIQUE.
INSERT INTO users (email, name) VALUES ('ada@example.com', 'Another Ada');

-- Fail vì role không nằm trong CHECK.
INSERT INTO users (email, name, role) VALUES ('bad@example.com', 'Bad Role', 'owner');

-- Fail vì post trỏ tới user không tồn tại, nhờ FOREIGN KEY.
INSERT INTO posts (user_id, title, body) VALUES (9999, 'Broken post', 'No owner');

-- Fail vì post_tags duplicate, nhờ PRIMARY KEY (post_id, tag_id).
INSERT INTO post_tags (post_id, tag_id) VALUES (1, 1);
```

Khi test trong `psql`, một số câu sẽ báo lỗi. Đó là kết quả đúng: database đang chặn data sai.

## 5. Apply Seed Data

Chạy:

```bash
psql postgres://postgres:dev@localhost:5432/day07_blog -f seed.sql
```

Verify counts:

```sql
SELECT COUNT(*) FROM users;
SELECT COUNT(*) FROM posts;
SELECT COUNT(*) FROM comments;
SELECT COUNT(*) FROM tags;
SELECT COUNT(*) FROM post_tags;
```

Kết quả mong đợi:

```text
users      3
posts      10
comments   25
tags       5
post_tags  21
```

## 6. Query 1: All Posts By A Specific User

Mục tiêu: lấy toàn bộ posts của `ada@example.com`, mới nhất trước.

```sql
SELECT p.id, p.title, p.published, p.created_at
FROM posts p
JOIN users u ON u.id = p.user_id
WHERE u.email = 'ada@example.com'
ORDER BY p.created_at DESC;
```

Kết quả mong đợi: 4 posts của Ada, gồm post id `10`, `1`, `2`, `3`.

Vì sao dùng `JOIN`: đề bài filter theo email, mà email nằm ở bảng `users`; post chỉ giữ `user_id`.

## 7. Query 2: Top 5 Most-Commented Posts In The Last 7 Days

Với seed này, dùng mốc bài học:

```sql
WITH recent_comments AS (
    SELECT id, post_id
    FROM comments
    WHERE created_at >= TIMESTAMPTZ '2026-06-07 00:00:00+00'
)
SELECT
    p.id,
    p.title,
    COUNT(rc.id) AS comment_count
FROM posts p
LEFT JOIN recent_comments rc ON rc.post_id = p.id
GROUP BY p.id, p.title
ORDER BY comment_count DESC, p.id
LIMIT 5;
```

Kết quả mong đợi:

```text
1  FastAPI routers in practice  5
2  Pydantic response models     4
3  Service layer notes          3
4  PostgreSQL constraints       3
5  Index basics                 2
```

Nếu muốn đúng nghĩa “7 ngày tính từ lúc chạy query”, đổi điều kiện thành:

```sql
WHERE created_at >= NOW() - INTERVAL '7 days'
```

Nhược điểm: kết quả phụ thuộc ngày hiện tại.

## 8. Query 3: Average Comments Per Post

```sql
WITH comment_counts AS (
    SELECT
        p.id,
        COUNT(c.id) AS comment_count
    FROM posts p
    LEFT JOIN comments c ON c.post_id = p.id
    GROUP BY p.id
)
SELECT ROUND(AVG(comment_count)::numeric, 2) AS avg_comments_per_post
FROM comment_counts;
```

Kết quả mong đợi:

```text
2.50
```

Vì có 25 comments / 10 posts.

## 9. Query 4: All Tags A Given User Has Used

Ví dụ lấy tag mà `ada@example.com` đã dùng trong posts của mình:

```sql
SELECT DISTINCT t.name
FROM users u
JOIN posts p ON p.user_id = u.id
JOIN post_tags pt ON pt.post_id = p.id
JOIN tags t ON t.id = pt.tag_id
WHERE u.email = 'ada@example.com'
ORDER BY t.name;
```

Kết quả mong đợi:

```text
backend
fastapi
python
```

`DISTINCT` cần thiết vì nhiều posts của cùng user có thể dùng cùng một tag.

## 10. Query 5: Posts That Have No Comments

```sql
SELECT p.id, p.title
FROM posts p
LEFT JOIN comments c ON c.post_id = p.id
WHERE c.id IS NULL
ORDER BY p.id;
```

Kết quả mong đợi:

```text
10  Draft API checklist
```

Vì post id `10` trong seed không có comment nào.

## 11. EXPLAIN ANALYZE Before And After Index

Để nhìn rõ tác dụng index trên dataset nhỏ, tạm drop index liên quan:

```sql
DROP INDEX IF EXISTS idx_comments_created_at;
DROP INDEX IF EXISTS idx_comments_post_id_created_at;
```

Chạy explain:

```sql
EXPLAIN ANALYZE
WITH recent_comments AS (
    SELECT id, post_id
    FROM comments
    WHERE created_at >= TIMESTAMPTZ '2026-06-07 00:00:00+00'
)
SELECT
    p.id,
    p.title,
    COUNT(rc.id) AS comment_count
FROM posts p
LEFT JOIN recent_comments rc ON rc.post_id = p.id
GROUP BY p.id, p.title
ORDER BY comment_count DESC, p.id
LIMIT 5;
```

Ghi output vào `journal/day-07-queries.md` dưới mục `Before index`.

Tạo lại index:

```sql
CREATE INDEX idx_comments_created_at ON comments(created_at);
CREATE INDEX idx_comments_post_id_created_at ON comments(post_id, created_at DESC);
```

Chạy lại cùng câu `EXPLAIN ANALYZE`, ghi output vào mục `After index`.

Lưu ý quan trọng: với 25 comments, Postgres rất có thể vẫn chọn `Seq Scan` vì table quá nhỏ. Đây là hành vi đúng. Trong journal, giải thích:

```text
Dataset nhỏ nên planner chọn Seq Scan dù có index. Index sẽ hữu ích hơn khi comments lớn và query lọc một phần nhỏ dữ liệu.
```

Muốn ép nhìn thấy index trong lúc học, có thể chạy trong session test:

```sql
SET enable_seqscan = off;
```

Không dùng setting này trong production.

## 11.1 Index Lab Với Dữ Liệu Lớn

Dataset chính chỉ có 25 comments nên không đủ lớn để thấy index rõ. Vì vậy có thêm file `index-lab.sql`. File này tạo bảng riêng:

```text
index_lab_users
index_lab_posts
index_lab_comments
```

và seed bằng `generate_series()`:

```sql
INSERT INTO index_lab_posts (user_id, title, published, created_at)
SELECT
    ((n - 1) % 1000) + 1,
    'Post ' || n,
    n % 3 <> 0,
    NOW() - (n || ' minutes')::interval
FROM generate_series(1, 50000) AS n;
```

Chạy lab:

```bash
psql postgres://postgres:dev@localhost:5432/day07_blog -f index-lab.sql
```

Các ví dụ quan trọng trong lab:

### Composite index

Query:

```sql
SELECT id, title, created_at
FROM index_lab_posts
WHERE user_id = 42
ORDER BY created_at DESC
LIMIT 20;
```

Index phù hợp:

```sql
CREATE INDEX idx_lab_posts_user_created
ON index_lab_posts(user_id, created_at DESC);
```

Vì sao hợp: query filter theo `user_id`, rồi sort theo `created_at DESC`. Index cùng thứ tự giúp Postgres tìm đúng user và đọc theo thứ tự mới nhất.

### Column order trong composite index

Index `(user_id, created_at)` giúp:

```sql
WHERE user_id = 42
WHERE user_id = 42 AND created_at >= ...
```

Nhưng không giúp tốt cho:

```sql
WHERE created_at >= NOW() - INTERVAL '7 days'
```

Vì `created_at` không phải cột đầu của index. Muốn query này nhanh, cần index riêng:

```sql
CREATE INDEX idx_lab_posts_created ON index_lab_posts(created_at DESC);
```

### Partial index

Nếu app hay query published posts:

```sql
SELECT id, title, created_at
FROM index_lab_posts
WHERE published = TRUE
ORDER BY created_at DESC
LIMIT 20;
```

Index tốt hơn index full:

```sql
CREATE INDEX idx_lab_posts_published_created
ON index_lab_posts(created_at DESC)
WHERE published = TRUE;
```

Vì index chỉ chứa row published, nhỏ hơn và đọc nhanh hơn.

### Predicate xấu làm index khó dùng

Không nên:

```sql
WHERE created_at::date = CURRENT_DATE
```

Vì cast function lên column có thể làm planner khó dùng b-tree index thường.

Nên viết range:

```sql
WHERE created_at >= CURRENT_DATE
  AND created_at < CURRENT_DATE + INTERVAL '1 day'
```

### Index cho join/filter comments

Query comment-count lọc comments gần đây:

```sql
SELECT p.id, p.title, COUNT(c.id) AS comment_count
FROM index_lab_posts p
LEFT JOIN index_lab_comments c
  ON c.post_id = p.id
 AND c.created_at >= NOW() - INTERVAL '1 day'
GROUP BY p.id, p.title
ORDER BY comment_count DESC, p.id
LIMIT 10;
```

Index dùng trong lab:

```sql
CREATE INDEX idx_lab_comments_created_post
ON index_lab_comments(created_at, post_id);
```

Vì điều kiện lọc chính là `created_at >= ...`, đặt `created_at` trước giúp Postgres thu hẹp comments gần đây trước, rồi dùng `post_id` cho join/group.

Khi đọc `EXPLAIN ANALYZE`, tập trung vào:

- scan type: `Seq Scan`, `Index Scan`, `Bitmap Index Scan`;
- row estimate vs actual rows;
- `Execution Time`;
- có sort riêng không, hay index đã trả dữ liệu đúng thứ tự.

## 12. Transaction Practice

Thử transaction và rollback:

```sql
BEGIN;

INSERT INTO posts (user_id, title, body, published)
VALUES (1, 'Temporary transaction post', 'This should be rolled back.', FALSE);

SELECT COUNT(*) FROM posts;

ROLLBACK;

SELECT COUNT(*) FROM posts;
```

Kỳ vọng:

- Trong transaction, count tăng lên 11.
- Sau `ROLLBACK`, count quay lại 10.

Thử commit:

```sql
BEGIN;

UPDATE posts
SET published = TRUE
WHERE id = 10;

COMMIT;

SELECT id, title, published FROM posts WHERE id = 10;
```

## 13. Journal Output Template

Tạo `journal/day-07-er-diagram.md`:

````markdown
# Day 7 ER Diagram

```mermaid
erDiagram
    users ||--o{ posts : writes
    users ||--o{ comments : writes
    posts ||--o{ comments : has
    posts ||--o{ post_tags : has
    tags ||--o{ post_tags : labels
```

## Decisions

- `posts.user_id`: `ON DELETE CASCADE` because posts should not outlive their owner in this exercise.
- `comments.post_id`: `ON DELETE CASCADE` because comments belong to a post.
- `comments.user_id`: `ON DELETE SET NULL` because we can keep comment history if an author is deleted.
- `post_tags`: join table for many-to-many relationship between posts and tags.
````

Tạo `journal/day-07-queries.md` và paste từng query + output thật từ máy của bạn.

## 14. Full Verification

Từ `journal/fastapi-hello-world`:

```bash
psql postgres://postgres:dev@localhost:5432/day07_blog -f schema.sql
psql postgres://postgres:dev@localhost:5432/day07_blog -f seed.sql
psql postgres://postgres:dev@localhost:5432/day07_blog
```

Trong `psql`:

```sql
\dt
SELECT COUNT(*) FROM users;
SELECT COUNT(*) FROM posts;
SELECT COUNT(*) FROM comments;
SELECT COUNT(*) FROM tags;
SELECT COUNT(*) FROM post_tags;
```

## 15. What To Explain To Mentor

Bạn cần nói được:

- Vì sao Day 7 chưa cần SQLAlchemy và Alembic.
- Vì sao cần `post_tags` thay vì lưu tag list trong `posts`.
- Vì sao constraint nên nằm ở database, không chỉ ở FastAPI.
- Vì sao index không phải lúc nào cũng được dùng.
- Vì sao `EXPLAIN ANALYZE` chạy query thật, không chỉ plan.
