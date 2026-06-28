# Day 9 Alembic Notes

## Migration Chain

```text
base
  -> 5c061848ffac initial schema
  -> 060fbf88ad71 add post summary
  -> 41aed7e2fffc backfill post published at
```

## Key Concepts

- `upgrade()` đưa DB lên revision mới.
- `downgrade()` quay DB về revision trước.
- Chỉ chạy một chiều tùy command: `alembic upgrade ...` hoặc `alembic downgrade ...`.
- Autogenerate chỉ tạo bản nháp; data migration phải tự viết.
- Migration đã merge thì không sửa trực tiếp.

## Data Migration

Migration `41aed7e2fffc` thêm `posts.published_at`.

Pattern:

1. Add column nullable.
2. Backfill `published_at = created_at`.
3. Alter column thành `NOT NULL`.

Lý do: nếu bảng đã có data, thêm `NOT NULL` ngay có thể fail vì row cũ chưa có giá trị.

## Docker Note

Deploy bình thường:

```bash
uv run alembic upgrade head
```

Rollback có chủ đích:

```bash
uv run alembic downgrade -1
```

Trong Docker Compose, migration chạy từ app/backend image vì Alembic code nằm cùng backend code. DB container chỉ giữ dữ liệu.

## Verification

```bash
cd journal/fastapi-hello-world
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

Kết quả:

- `alembic upgrade head`: apply đủ 3 migrations từ DB rỗng.
- `alembic current`: `41aed7e2fffc (head)`.
- `alembic downgrade -1 && alembic upgrade head`: pass.
- `alembic check`: `No new upgrade operations detected.`
- `pytest`: `20 passed`, có 1 warning từ dependency `fastapi.testclient`/Starlette.
- `ruff`: `All checks passed!`
