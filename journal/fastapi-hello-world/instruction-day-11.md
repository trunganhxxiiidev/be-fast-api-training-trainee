# Instruction: Day 11 Automated Testing

Day 11 biến test suite từ vài API tests thành safety net có đủ 3 tầng: unit, integration và end-to-end. Mục tiêu là có thể sửa service layer hoặc auth flow mà biết nhanh mình có làm vỡ behavior quan trọng không.

## 1. Mục tiêu bài học

Sau bài này bạn cần hiểu:

- Unit test kiểm tra logic nhỏ, nhanh, không phụ thuộc DB/HTTP.
- Integration test kiểm tra nhiều layer làm việc với nhau, ở bài này là service + SQLAlchemy session.
- End-to-end test đi qua HTTP flow thật: register, login, current user, post CRUD.
- Transaction rollback fixture giúp mỗi test có DB sạch dù code trong route có `commit()`.
- Coverage là công cụ soi vùng mù, không phải điểm số để “cày” 100%.

## 2. File chính trong bài

```text
tests/
├── conftest.py
├── test_auth_service_unit.py
├── test_user_service_integration.py
├── test_post_service_integration.py
└── test_auth_e2e.py
pyproject.toml
docker-compose.yml
```

Ý nghĩa:

- `tests/conftest.py`: thêm async engine/session/client fixtures, dùng `join_transaction_mode="create_savepoint"`.
- `test_auth_service_unit.py`: unit tests cho auth service bằng fake session, không gọi HTTP/DB thật.
- `test_user_service_integration.py`: service tests cho user với session thật.
- `test_post_service_integration.py`: service tests cho post với session thật.
- `test_auth_e2e.py`: flow đầy đủ qua HTTP.
- `pyproject.toml`: cấu hình `pytest-asyncio` và `pytest-cov`.
- `docker-compose.yml`: service `postgres-test` cho hướng chạy integration với Postgres thật.

## 3. Bài tập đã làm

- Thêm rollback fixture cho async SQLAlchemy session.
- Thêm unit tests không đi qua HTTP.
- Thêm integration tests cho user service và post service.
- Thêm E2E test register -> login -> get me -> create post -> get post -> delete post.
- Thêm `pytest-cov` và coverage config.
- Thêm test edge case: xóa user phải cascade xóa posts.

## 4. Lệnh chạy

```bash
cd journal/fastapi-hello-world
uv run pytest -v
uv run pytest --cov=app --cov-report=term-missing
uv run ruff check .
```

Nếu muốn chuẩn bị Postgres test DB theo đúng bài học:

```bash
docker compose up -d postgres-test
DATABASE_URL=postgresql+asyncpg://postgres:dev@localhost:5433/app_test uv run pytest -v
```

Hiện test suite vẫn dùng SQLite in-memory để chạy nhanh trong local training. `postgres-test` đã có sẵn để chuyển integration suite sang Postgres thật khi cần CI/local Docker ổn định.

## 5. Checklist hoàn thành

- [x] Có rollback fixture trong `tests/conftest.py`.
- [x] Có unit tests cho service logic.
- [x] Có integration tests cho user/post service.
- [x] Có E2E auth flow.
- [x] Có coverage config.
- [x] Có journal ngày học.
