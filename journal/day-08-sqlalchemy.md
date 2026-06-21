# Day 8 SQLAlchemy Notes

## ER Model In Code

Day 8 chuyển schema blog thành ORM models:

```text
users 1 -- many posts
users 1 -- many comments
posts 1 -- many comments
```

Trong code:

- `User.posts` nối tới `Post.author`.
- `User.comments` nối tới `Comment.author`.
- `Post.comments` nối tới `Comment.post`.
- `Post.user_id` là foreign key tới `users.id`.
- `Comment.post_id` là foreign key tới `posts.id`.
- `Comment.user_id` nullable vì có thể giữ comment nếu author bị xóa.

## N+1 Query

Endpoint cần chú ý:

```text
GET /users/{user_id}/posts
```

Service dùng:

```python
select(User).options(selectinload(User.posts)).where(User.id == user_id)
```

Lý do:

- Nếu chỉ load user rồi lazy-load `user.posts`, ORM có thể query thêm lúc đọc relationship.
- `selectinload(User.posts)` preload posts bằng query phụ dạng `WHERE posts.user_id IN (...)`.
- Với một user cụ thể, log SQL nên chỉ có khoảng 2 query chính: một query lấy user, một query lấy posts.

## Important SQLAlchemy Calls

```python
db.add(user)
await db.flush()
```

- `db.add(user)`: đưa object vào session, chưa chắc đã gửi SQL ngay.
- `flush()`: gửi `INSERT` xuống DB để lấy `id`, nhưng transaction vẫn chưa commit.
- `get_session()` commit ở cuối request nếu không có lỗi.

```python
result = await db.execute(select(User).where(User.email == email))
user = result.scalar_one_or_none()
```

- `execute()`: chạy SQL.
- `scalar_one_or_none()`: lấy 0 hoặc 1 ORM object.
- Với email unique, đây là kiểu đọc phù hợp.

## Verification

```bash
cd journal/fastapi-hello-world
DATABASE_URL=sqlite+aiosqlite:////tmp/day08_verify.db DATABASE_ECHO=false uv run python scripts/create_tables.py
uv run pytest
uv run ruff check .
```

Kết quả:

- `scripts/create_tables.py`: tạo được SQLite DB tạm `/tmp/day08_verify.db`.
- `pytest`: `20 passed`, có 1 warning từ dependency `fastapi.testclient`/Starlette.
- `ruff`: `All checks passed!`
