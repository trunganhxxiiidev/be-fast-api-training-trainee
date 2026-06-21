# Instruction: Day 7 PostgreSQL Fundamentals

Day 7 là bài học về PostgreSQL thuần. Mục tiêu không phải là nối database vào FastAPI ngay, mà là hiểu cách nghĩ bằng bảng, khóa, constraint, query, transaction và index trước khi dùng SQLAlchemy ở Day 8.

Day 6 dùng `/users` in-memory. Day 7 tạm rời code FastAPI để luyện database bằng tay với `psql`, `schema.sql`, `seed.sql` và các query SQL.

Nếu cần bài giải mẫu có SQL đầy đủ, xem `solution-day-07.md`. Khi học thật, hãy tự chạy từng câu lệnh và tự giải thích được schema/query trước khi nộp bài.

## 1. Mục tiêu bài học

Sau bài này bạn cần hiểu:

- PostgreSQL lưu dữ liệu bằng table, row, column.
- Primary key dùng để định danh một row.
- Foreign key dùng để mô tả quan hệ giữa các bảng.
- `NOT NULL`, `UNIQUE`, `CHECK`, `DEFAULT` giúp database tự bảo vệ dữ liệu.
- Normalization giúp tránh dữ liệu bị lặp và lệch nhau.
- Transaction giúp nhiều thao tác SQL thành một đơn vị an toàn.
- Index giúp query nhanh hơn, nhưng làm write chậm hơn.
- `EXPLAIN ANALYZE` cho biết query thật sự chạy như thế nào.

## 2. Branch làm bài

Từ root repo:

```bash
cd ~/Training/D1/be-fast-api-training-trainee
git status --short --branch
git switch -c feature/day-07-postgresql
```

Nếu đang còn ở branch Day 6 và chưa merge PR, không tự ý reset hoặc xóa branch. Có thể tạo branch Day 7 từ branch hiện tại nếu mentor cho phép, hoặc đợi Day 6 merge rồi tạo từ `main`.

## 3. Project và file cần tạo

Day 7 vẫn đặt bài làm trong project training hiện tại:

```bash
cd journal/fastapi-hello-world
```

Tạo các file:

```text
journal/
├── day-07-er-diagram.md
└── day-07-queries.md

journal/fastapi-hello-world/
├── schema.sql
├── seed.sql
├── index-lab.sql
└── instruction-day-07.md
```

Ý nghĩa:

- `schema.sql`: định nghĩa bảng, khóa, constraint, index.
- `seed.sql`: dữ liệu mẫu để query.
- `index-lab.sql`: dữ liệu test lớn bằng `generate_series()` để luyện `EXPLAIN ANALYZE` và thấy index hoạt động rõ hơn.
- `journal/day-07-er-diagram.md`: mô tả ER diagram và quyết định thiết kế.
- `journal/day-07-queries.md`: lưu query, output và `EXPLAIN ANALYZE` trước/sau index.

## 4. Cài và chạy PostgreSQL

Cách dễ nhất là dùng Docker:

```bash
docker run --name pg-day-07 \
  -e POSTGRES_PASSWORD=dev \
  -e POSTGRES_DB=day07_blog \
  -p 5432:5432 \
  -d postgres:16
```

Kiểm tra container:

```bash
docker ps
```

Kết nối bằng `psql`:

```bash
psql postgres://postgres:dev@localhost:5432/day07_blog
```

Nếu máy chưa có `psql`, cài client:

```bash
sudo apt update
sudo apt install -y postgresql-client
```

Các lệnh `psql` cần nhớ:

```text
\l          list databases
\c dbname   connect database
\dt         list tables
\d users    describe table users
\timing     bật/tắt đo thời gian query
\q          thoát psql
```

## 5. Nội dung chính cần học

### Table

Table giống một bảng dữ liệu có cột và dòng. Ví dụ `users` lưu người dùng, `posts` lưu bài viết.

### Primary key

Primary key là định danh duy nhất của một row. Trong bài này ưu tiên:

```sql
id BIGSERIAL PRIMARY KEY
```

`BIGSERIAL` tự tăng và có range lớn hơn `SERIAL`.

### Foreign key

Foreign key nối bảng con tới bảng cha:

```sql
user_id BIGINT NOT NULL REFERENCES users(id) ON DELETE CASCADE
```

Nghĩa là mỗi post thuộc về một user. Nếu user bị xóa, post của user đó cũng bị xóa theo.

### Constraint

Constraint là luật dữ liệu ở tầng database:

```sql
email TEXT NOT NULL UNIQUE
role TEXT NOT NULL DEFAULT 'member' CHECK (role IN ('member', 'admin'))
```

Không nên chỉ validate ở API. Database cũng phải chặn dữ liệu sai.

### Normalization

Không lưu `"python,fastapi,sql"` trong một cột `tags`. Tách thành bảng:

```text
tags
post_tags
```

Vì một post có nhiều tag và một tag có thể thuộc nhiều post, đây là quan hệ many-to-many.

### Transaction

Transaction gom nhiều câu SQL thành một khối:

```sql
BEGIN;
UPDATE posts SET published = TRUE WHERE id = 1;
INSERT INTO comments (post_id, user_id, body) VALUES (1, 2, 'Nice post');
COMMIT;
```

Nếu có lỗi giữa chừng:

```sql
ROLLBACK;
```

### Index

Index giúp query tìm dữ liệu nhanh hơn. Nhưng mỗi index làm `INSERT`, `UPDATE`, `DELETE` tốn thêm chi phí. Vì vậy chỉ tạo index cho query thật sự cần.

Ví dụ query hay lọc post theo user:

```sql
CREATE INDEX idx_posts_user_id ON posts(user_id);
```

## 6. Thiết kế blog schema

Bài yêu cầu 5 bảng:

```text
users
posts
comments
tags
post_tags
```

Gợi ý quan hệ:

```text
users 1 -- many posts
users 1 -- many comments
posts 1 -- many comments
posts many -- many tags, thông qua post_tags
```

Quyết định thiết kế cần ghi vào `journal/day-07-er-diagram.md`:

- Vì sao `posts.user_id` dùng `ON DELETE CASCADE`.
- Vì sao `comments.post_id` nên dùng `ON DELETE CASCADE`.
- Vì sao `comments.user_id` có thể dùng `ON DELETE SET NULL` hoặc `RESTRICT`, tùy quyết định của bạn.
- Vì sao tag cần bảng riêng, không lưu list tag trong `posts`.

Ví dụ ER diagram bằng Mermaid:

````markdown
```mermaid
erDiagram
    users ||--o{ posts : writes
    users ||--o{ comments : writes
    posts ||--o{ comments : has
    posts ||--o{ post_tags : has
    tags ||--o{ post_tags : labels
```
````

## 7. Viết `schema.sql`

File `schema.sql` nên có thứ tự:

1. Drop table cũ nếu cần reset local.
2. Tạo `users`.
3. Tạo `posts`.
4. Tạo `comments`.
5. Tạo `tags`.
6. Tạo `post_tags`.
7. Tạo index cần thiết.

Gợi ý skeleton:

```sql
DROP TABLE IF EXISTS post_tags;
DROP TABLE IF EXISTS comments;
DROP TABLE IF EXISTS posts;
DROP TABLE IF EXISTS tags;
DROP TABLE IF EXISTS users;

CREATE TABLE users (
    id BIGSERIAL PRIMARY KEY,
    email TEXT NOT NULL UNIQUE,
    name TEXT NOT NULL,
    role TEXT NOT NULL DEFAULT 'member' CHECK (role IN ('member', 'admin')),
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE TABLE posts (
    id BIGSERIAL PRIMARY KEY,
    user_id BIGINT NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    title TEXT NOT NULL,
    body TEXT NOT NULL,
    published BOOLEAN NOT NULL DEFAULT FALSE,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- TODO: comments
-- TODO: tags
-- TODO: post_tags
-- TODO: indexes
```

Chạy schema:

```bash
psql postgres://postgres:dev@localhost:5432/day07_blog -f schema.sql
```

Kiểm tra:

```bash
psql postgres://postgres:dev@localhost:5432/day07_blog
\dt
\d users
\d posts
```

## 8. Viết `seed.sql`

File `seed.sql` cần insert:

- 3 users
- 10 posts
- 25 comments
- 5 tags
- mỗi post có 1 đến 3 tags

Gợi ý:

```sql
INSERT INTO users (email, name, role) VALUES
    ('ada@example.com', 'Ada Lovelace', 'admin'),
    ('linus@example.com', 'Linus Torvalds', 'member'),
    ('grace@example.com', 'Grace Hopper', 'member');

INSERT INTO tags (name) VALUES
    ('python'),
    ('fastapi'),
    ('postgresql'),
    ('sql'),
    ('backend');
```

Chạy seed:

```bash
psql postgres://postgres:dev@localhost:5432/day07_blog -f seed.sql
```

Kiểm tra số lượng:

```sql
SELECT COUNT(*) FROM users;
SELECT COUNT(*) FROM posts;
SELECT COUNT(*) FROM comments;
SELECT COUNT(*) FROM tags;
SELECT COUNT(*) FROM post_tags;
```

## 9. Query drills

Ghi SQL và output thật vào `journal/day-07-queries.md`.

### 1. All posts by a specific user, newest first

Cần dùng `JOIN` hoặc filter bằng `user_id`.

Gợi ý hướng nghĩ:

```sql
SELECT p.id, p.title, p.created_at
FROM posts p
JOIN users u ON u.id = p.user_id
WHERE u.email = 'ada@example.com'
ORDER BY p.created_at DESC;
```

### 2. Top 5 most-commented posts in the last 7 days

Cần:

- `LEFT JOIN comments`
- filter comment theo thời gian
- `GROUP BY`
- `COUNT`
- `ORDER BY`
- `LIMIT 5`

### 3. Average number of comments per post

Cần tính comment count theo từng post trước, rồi lấy average.

### 4. All tags a given user has used

Đường join:

```text
users -> posts -> post_tags -> tags
```

Dùng `DISTINCT` để không lặp tag.

### 5. Posts that have no comments

Cách phổ biến:

```sql
SELECT p.id, p.title
FROM posts p
LEFT JOIN comments c ON c.post_id = p.id
WHERE c.id IS NULL;
```

## 10. Indexing exercise

Bật timing:

```sql
\timing
```

Chạy explain trước khi thêm index:

```sql
EXPLAIN ANALYZE
-- paste query top 5 most-commented posts here
;
```

Ghi output vào `journal/day-07-queries.md` dưới mục `Before index`.

Sau đó thêm index phù hợp. Ví dụ nếu query lọc comment theo `created_at` và join theo `post_id`, có thể cân nhắc:

```sql
CREATE INDEX idx_comments_created_at ON comments(created_at);
CREATE INDEX idx_comments_post_id ON comments(post_id);
```

Chạy lại:

```sql
EXPLAIN ANALYZE
-- same query
;
```

Ghi output vào mục `After index`.

Lưu ý: với dataset nhỏ, Postgres có thể vẫn dùng `Seq Scan`. Điều đó không sai. Nếu muốn thấy index rõ hơn, bạn cần seed nhiều data hơn hoặc giải thích trong journal rằng table quá nhỏ nên planner chọn sequential scan.

Để luyện index rõ hơn, chạy lab riêng:

```bash
psql postgres://postgres:dev@localhost:5432/day07_blog -f index-lab.sql
```

File này tự tạo bảng `index_lab_*`, seed nhiều dữ liệu bằng `generate_series()`, rồi chạy các ví dụ:

- query trước/sau composite index `(user_id, created_at DESC)`;
- query chỉ filter `created_at` để thấy column order quan trọng;
- partial index cho `published = TRUE`;
- ví dụ predicate xấu `created_at::date = CURRENT_DATE`;
- ví dụ predicate tốt dùng range theo timestamp;
- comment-count query trước/sau index `(created_at, post_id)`.

## 11. Verification

Chạy từ `journal/fastapi-hello-world`:

```bash
psql postgres://postgres:dev@localhost:5432/day07_blog -f schema.sql
psql postgres://postgres:dev@localhost:5432/day07_blog -f seed.sql
psql postgres://postgres:dev@localhost:5432/day07_blog -f index-lab.sql
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

Nếu có SQL format/lint tool thì chạy thêm. Nếu không có, ít nhất phải chạy được toàn bộ SQL từ database trống.

## 12. Journal cần cập nhật

Tạo hoặc cập nhật:

```text
journal/YYYY-MM-DD.md
```

Nội dung nên có:

- `What I Learned`: PK, FK, constraint, transaction, index, explain.
- `What I Built`: blog schema, seed data, query drills.
- `Verification`: lệnh `psql -f schema.sql`, `psql -f seed.sql`, query count.
- `Blockers`: lỗi SQL hoặc Docker/psql nếu có.
- `Question`: một câu hỏi hỏi mentor.

Ví dụ question tốt:

```text
Khi nào nên dùng ON DELETE CASCADE và khi nào nên giữ data bằng SET NULL hoặc RESTRICT?
```

## 13. Git commit và push

Từ root repo:

```bash
cd ~/Training/D1/be-fast-api-training-trainee
git status --short
git add journal/fastapi-hello-world/instruction-day-07.md \
        journal/fastapi-hello-world/schema.sql \
        journal/fastapi-hello-world/seed.sql \
        journal/fastapi-hello-world/index-lab.sql \
        journal/fastapi-hello-world/solution-day-07.md \
        journal/day-07-er-diagram.md \
        journal/day-07-queries.md \
        journal/2026-06-14.md
git diff --cached --stat
git diff --cached --name-only
git commit -m "docs: add day 7 postgresql practice"
git push -u origin feature/day-07-postgresql
```

Chỉ stage file thật sự liên quan Day 7. Không stage `.venv/`, cache, `.env`, `.pytest_cache/`, `.ruff_cache/`.

## 14. Checklist hoàn thành Day 7

- [ ] Chạy được Postgres local bằng Docker hoặc service local.
- [ ] Kết nối được bằng `psql`.
- [ ] Có ER diagram trong `journal/day-07-er-diagram.md`.
- [ ] Có `schema.sql` tạo đủ 5 bảng.
- [ ] Có PK, FK, `NOT NULL`, `UNIQUE`, `CHECK`, `DEFAULT` hợp lý.
- [ ] Có `seed.sql` tạo đủ data mẫu.
- [ ] Có query drills và output trong `journal/day-07-queries.md`.
- [ ] Có `EXPLAIN ANALYZE` trước/sau index.
- [ ] Có chạy `index-lab.sql` và hiểu ít nhất 3 ví dụ index: composite, partial, range predicate.
- [ ] Journal ngày hiện tại đã cập nhật.
- [ ] Branch/commit sạch, chỉ chứa file Day 7.

## 15. Self-check

Tự trả lời trước khi nộp bài:

1. `PRIMARY KEY` khác `UNIQUE` ở điểm nào?
2. Vì sao không nên lưu tags dưới dạng text `"python,sql"` trong bảng `posts`?
3. Nếu xóa user, comments của user đó nên bị xóa, set null, hay bị chặn? Vì sao?
4. Vì sao query có index rồi nhưng `EXPLAIN ANALYZE` vẫn có thể hiện `Seq Scan`?
5. Index trên `(user_id, created_at)` giúp query nào? Có giúp query chỉ filter theo `created_at` không?
6. Transaction giúp gì khi có nhiều câu SQL liên quan nhau?
