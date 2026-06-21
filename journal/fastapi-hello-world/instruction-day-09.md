# Instruction: Day 9 Alembic Migrations

Day 9 thay `Base.metadata.create_all()` bằng Alembic migrations. Mục tiêu không chỉ là tạo table, mà là học cách quản lý lịch sử thay đổi database: đi tới bằng `upgrade()`, quay lui bằng `downgrade()`, đọc migration trước khi apply, và viết data migration an toàn.

## 1. Mục tiêu bài học

Sau bài này bạn cần hiểu:

- Alembic quản lý schema bằng các revision file trong `migrations/versions/`.
- Mỗi migration mô tả một bước đổi DB, gồm `upgrade()` và `downgrade()`.
- Deploy bình thường chạy `alembic upgrade head`.
- Rollback có chủ đích mới chạy `alembic downgrade -1` hoặc downgrade tới revision cụ thể.
- `alembic revision --autogenerate` chỉ tạo bản nháp, luôn phải đọc lại.
- Data migration là phần tự viết, autogenerate không thể đoán.
- Không sửa migration đã merge vào `main`; nếu cần sửa thì tạo migration mới.

## 2. File chính trong bài

```text
alembic.ini
migrations/
├── env.py
├── script.py.mako
└── versions/
    ├── 5c061848ffac_initial_schema.py
    ├── 060fbf88ad71_add_post_summary.py
    └── 41aed7e2fffc_backfill_post_published_at.py
```

Ý nghĩa:

- `alembic.ini`: config chung của Alembic.
- `migrations/env.py`: nối Alembic với `Settings.database_url` và `Base.metadata`.
- `migrations/versions/`: mỗi file là một version schema.

## 3. Wire Alembic với app

Trong `migrations/env.py`:

```python
from app.config import get_settings
from app.models import Base

settings = get_settings()
config.set_main_option("sqlalchemy.url", settings.database_url)
target_metadata = Base.metadata
```

Giải thích:

- `get_settings()` đọc `DATABASE_URL`.
- `Base.metadata` chứa schema từ SQLAlchemy models.
- `app.models.__init__` phải import đủ `User`, `Post`, `Comment`; nếu thiếu model, Alembic không thấy table đó.

## 4. Ba migrations trong bài

### 1. Initial schema

Revision:

```text
5c061848ffac_initial_schema.py
```

Tạo:

- `users`
- `posts`
- `comments`
- indexes cho email/user_id/post_id
- foreign keys giữa bảng

### 2. Schema migration

Revision:

```text
060fbf88ad71_add_post_summary.py
```

Thêm column:

```text
posts.summary
```

Đây là ví dụ schema migration đơn giản: đổi cấu trúc bảng.

### 3. Data migration

Revision:

```text
41aed7e2fffc_backfill_post_published_at.py
```

Thêm column:

```text
posts.published_at
```

Pattern an toàn:

```python
with op.batch_alter_table("posts") as batch_op:
    batch_op.add_column(... nullable=True)

op.execute("""
    UPDATE posts
    SET published_at = created_at
    WHERE published_at IS NULL
""")

with op.batch_alter_table("posts") as batch_op:
    batch_op.alter_column("published_at", nullable=False)
```

Vì sao không add `NOT NULL` ngay?

- Nếu bảng đã có data, column mới chưa có giá trị.
- Add `NOT NULL` ngay có thể fail.
- Phải add nullable trước, backfill data cũ, rồi mới chuyển sang not null.

## 5. Upgrade và downgrade

Một migration có cả hai hàm:

```python
def upgrade() -> None:
    ...


def downgrade() -> None:
    ...
```

Nhưng Alembic không chạy cả hai cùng lúc.

```bash
uv run alembic upgrade head
```

Chạy `upgrade()`.

```bash
uv run alembic downgrade -1
```

Chạy `downgrade()`.

Tư duy đúng:

```text
upgrade = đi tới revision mới
downgrade = quay lui revision cũ
```

Không phải:

```text
upgrade chỉ add
downgrade chỉ delete
```

Nếu thay đổi mới là xóa column, thì `upgrade()` có thể là `drop_column`.

## 6. Docker/deploy mental model

Khi deploy bằng Docker Compose:

```yaml
migrate:
  build: .
  environment:
    DATABASE_URL: postgresql+asyncpg://postgres:dev@db:5432/app
  depends_on:
    - db
  command: uv run alembic upgrade head
```

Service `migrate` chỉ chạy command được đưa vào. Nếu command là `upgrade head`, nó chỉ chạy `upgrade()`.

Rollback có chủ đích:

```bash
docker compose run --rm migrate uv run alembic downgrade -1
```

Production thường không để downgrade tự động. Rollback DB phải có chủ đích vì có thể mất data.

## 7. Verification

Chạy từ `journal/fastapi-hello-world`:

```bash
rm -f /tmp/day09_verify.db
DATABASE_URL=sqlite+aiosqlite:////tmp/day09_verify.db DATABASE_ECHO=false uv run alembic upgrade head
DATABASE_URL=sqlite+aiosqlite:////tmp/day09_verify.db DATABASE_ECHO=false uv run alembic current
DATABASE_URL=sqlite+aiosqlite:////tmp/day09_verify.db DATABASE_ECHO=false uv run alembic history --verbose
DATABASE_URL=sqlite+aiosqlite:////tmp/day09_verify.db DATABASE_ECHO=false uv run alembic downgrade -1
DATABASE_URL=sqlite+aiosqlite:////tmp/day09_verify.db DATABASE_ECHO=false uv run alembic upgrade head
DATABASE_URL=sqlite+aiosqlite:////tmp/day09_verify.db DATABASE_ECHO=false uv run alembic check
uv run pytest
uv run ruff check .
```

## 8. Checklist hoàn thành

- [ ] Có `alembic.ini`.
- [ ] Có `migrations/env.py` nối với `Base.metadata`.
- [ ] Có ít nhất 3 migrations.
- [ ] `alembic upgrade head` chạy được từ DB rỗng.
- [ ] Có ít nhất một data migration.
- [ ] `alembic downgrade -1 && alembic upgrade head` chạy được.
- [ ] `alembic check` pass.
- [ ] `pytest` pass.
- [ ] `ruff` pass.

## 9. Self-check

1. Vì sao production không dùng `Base.metadata.create_all()`?
2. `upgrade()` và `downgrade()` có chạy cùng lúc không?
3. Nếu migration mới là xóa column, `upgrade()` làm gì?
4. Vì sao autogenerate không được tin tuyệt đối?
5. Vì sao rename column nguy hiểm?
6. Vì sao thêm `NOT NULL` column vào bảng có data phải làm nhiều bước?
7. Vì sao không sửa migration đã merge vào `main`?
8. Khi deploy Docker, migration chạy từ app image hay DB image?
