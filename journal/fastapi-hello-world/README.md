# Hello API

Day 5 biến project FastAPI hello world thành một service nhỏ có cấu trúc gần với dự án thật. Day 6 tiếp tục refactor project này theo hướng backend core: tách `schemas/`, thêm `services/`, dùng `Depends()` cho pagination, thêm CRUD `/users`, và chuẩn hóa error response. Day 8 chuyển `/users` sang SQLAlchemy ORM async, thêm models quan hệ `User`/`Post`/`Comment`, và thêm CRUD `/posts`. Day 10 thêm register/login bằng JWT, password hashing và admin-only delete. Day 11 mở rộng test suite theo test pyramid: unit, integration, end-to-end, rollback fixture và coverage report.

Service này có các endpoint chính:

| Method | Path | Ket qua |
| --- | --- | --- |
| `GET` | `/health` | Tra ve `{"status": "ok"}` |
| `POST` | `/echo` | Nhan `{"message": str}` va tra ve message kem timestamp |
| `GET` | `/version` | Tra ve version doc tu config |
| `POST` | `/auth/register` | Đăng ký user, hash password |
| `POST` | `/auth/login` | Đăng nhập OAuth2 form, trả JWT bearer token |
| `POST` | `/users` | Tạo user trong database |
| `GET` | `/users?limit=20&offset=0` | List user có pagination |
| `GET` | `/users/me` | Lấy current user từ JWT |
| `GET` | `/users/{user_id}` | Lấy một user |
| `GET` | `/users/{user_id}/posts` | List posts của user bằng relationship |
| `PUT` | `/users/{user_id}` | Replace user |
| `PATCH` | `/users/{user_id}` | Update một phần user |
| `DELETE` | `/users/{user_id}` | Admin-only delete, trả `204` |
| `POST` | `/posts` | Tạo post thuộc về user |
| `GET` | `/posts?limit=20&offset=0` | List posts có pagination |
| `GET` | `/posts/{post_id}` | Lấy một post |
| `PUT` | `/posts/{post_id}` | Replace post |
| `PATCH` | `/posts/{post_id}` | Update một phần post |
| `DELETE` | `/posts/{post_id}` | Xóa post, trả `204` |

## Muc Tieu Bai Hoc

Sau bai nay ban can nam duoc:

- Vi sao project backend khong nen de tat ca code trong mot file `main.py`.
- Cach dung `create_app()` factory de tao FastAPI app ro rang va de test.
- Cach tach request/response model bang Pydantic.
- Cach doc config tu env var bang `pydantic-settings`.
- Cach viet middleware do thoi gian request va log ra stdout.
- Cach viet test cho endpoint thanh cong va request sai body.
- Cách dùng `APIRouter` để nhóm endpoint theo tag.
- Cách dùng `Depends()` cho query params dùng lại được.
- Cách giữ route mỏng và đưa business logic vào `services/`.
- Cách dùng global exception handlers để error có shape thống nhất.
- Cách dùng SQLAlchemy 2.0 typed ORM với `Mapped[...]` và `mapped_column(...)`.
- Cách dùng `AsyncSession` làm FastAPI dependency.
- Cách khai báo relationship giữa `User`, `Post`, `Comment`.
- Cách tránh N+1 query bằng `selectinload`.
- Cách hash password bằng bcrypt/passlib, không lưu plaintext password.
- Cách issue/verify JWT bằng secret từ config.
- Cách dùng dependency cho current user và role-based authorization.
- Cách tổ chức test pyramid cho FastAPI + SQLAlchemy.
- Cách dùng async pytest fixtures với transaction rollback.
- Cách dùng coverage report để tìm vùng logic đáng test tiếp.

## Cau Truc Project

```text
fastapi-hello-world/
├── app/
│   ├── __init__.py
│   ├── main.py
│   ├── config.py
│   ├── db.py
│   ├── deps.py
│   ├── error_handlers.py
│   ├── exceptions.py
│   ├── logging_setup.py
│   ├── middleware.py
│   ├── security.py
│   ├── schemas/
│   │   ├── __init__.py
│   │   ├── auth.py
│   │   ├── echo.py
│   │   ├── error.py
│   │   ├── health.py
│   │   ├── post.py
│   │   ├── user.py
│   │   └── version.py
│   ├── models/
│   │   ├── __init__.py
│   │   ├── base.py
│   │   ├── user.py
│   │   ├── post.py
│   │   └── comment.py
│   ├── services/
│   │   ├── __init__.py
│   │   ├── auth_service.py
│   │   ├── echo_service.py
│   │   ├── post_service.py
│   │   └── user_service.py
│   └── routes/
│       ├── __init__.py
│       ├── auth.py
│       ├── health.py
│       ├── echo.py
│       ├── posts.py
│       ├── users.py
│       └── version.py
├── migrations/
│   ├── env.py
│   └── versions/
├── tests/
│   ├── __init__.py
│   ├── conftest.py
│   ├── test_auth_e2e.py
│   ├── test_auth_service_unit.py
│   ├── test_health.py
│   ├── test_auth.py
│   ├── test_echo.py
│   ├── test_post_service_integration.py
│   ├── test_posts.py
│   ├── test_user_service_integration.py
│   ├── test_users.py
│   └── test_version.py
├── main.py
├── pyproject.toml
├── uv.lock
├── README.md
├── .env.example
├── .gitignore
└── .pre-commit-config.yaml
```

Y nghia nhanh:

- `app/main.py`: tao app, gan middleware, include router.
- `app/config.py`: noi doc `PORT`, `APP_VERSION`, `LOG_LEVEL`, `DATABASE_URL`, `DATABASE_ECHO`, `JWT_SECRET`.
- `app/db.py`: tạo async engine, session factory và dependency `SessionDep`.
- `app/security.py`: password hashing, JWT issue/verify, current-user dependency, RBAC dependency.
- `app/deps.py`: dependency dùng chung, hiện có `pagination`.
- `app/error_handlers.py`: đăng ký global error envelope.
- `app/exceptions.py`: domain exceptions như duplicate email, user not found.
- `app/logging_setup.py`: cau hinh log JSON ra stdout.
- `app/middleware.py`: do moi request mat bao lau va log mot dong.
- `app/schemas/`: định nghĩa shape request/response bằng Pydantic.
- `app/models/`: định nghĩa SQLAlchemy ORM models map với database tables.
- `app/services/`: chứa business logic, không import FastAPI.
- `app/routes/`: moi file la mot nhom endpoint rieng.
- `migrations/`: Alembic migrations quản lý schema database theo version.
- `tests/`: test endpoint bang `TestClient`.
- `tests/test_*_service_integration.py`: test service layer với async DB session fixture.
- `tests/test_auth_service_unit.py`: unit test auth service bằng fake session.
- `tests/test_auth_e2e.py`: E2E auth + post flow qua HTTP.
- `main.py`: shim de command cu `main:app` van import duoc.

## Cai Dat

Can co `uv` tren may. Tu thu muc project:

```bash
cd fastapi-hello-world
uv sync
```

Lenh `uv sync` doc `pyproject.toml` va `uv.lock`, sau do tao/cap nhat `.venv` dung version dependency cua project.

## Chay App

Day 8 cần database. Ví dụ `.env` local:

```text
DATABASE_URL=postgresql+asyncpg://postgres:dev@localhost:5432/day08_api
DATABASE_ECHO=true
JWT_SECRET=change-this-in-real-environments-32-bytes-minimum
ACCESS_TOKEN_EXPIRE_MINUTES=60
```

Tạo hoặc cập nhật schema bằng Alembic:

```bash
uv run alembic upgrade head
```

Chay theo dung layout moi:

```bash
uv run uvicorn app.main:app --reload
```

Neu muon dung port trong env var:

```bash
PORT=9000 uv run python -m app.main
```

Mo browser:

```text
http://127.0.0.1:8000/docs
```

Swagger UI o `/docs` sẽ hiện endpoint theo tag: `health`, `echo`, `version`, `auth`, `users`, `posts`.

## Goi Thu API

Health check:

```bash
curl http://127.0.0.1:8000/health
```

Ket qua:

```json
{"status":"ok"}
```

Echo:

```bash
curl -X POST http://127.0.0.1:8000/echo \
  -H "Content-Type: application/json" \
  -d '{"message":"hello FastAPI"}'
```

Ket qua co dang:

```json
{
  "echo": "hello FastAPI",
  "received_at": "2026-06-09T10:30:00.000000+00:00"
}
```

Version:

```bash
APP_VERSION=2.0.0 uv run uvicorn app.main:app --reload
curl http://127.0.0.1:8000/version
```

Ket qua:

```json
{"version":"2.0.0"}
```

Users:

```bash
curl -X POST http://127.0.0.1:8000/users \
  -H "Content-Type: application/json" \
  -d '{"email":"ada@example.com","name":"Ada Lovelace","password":"correct-horse-battery","is_active":true}'
```

Kết quả:

```json
{
  "id": 1,
  "email": "ada@example.com",
  "name": "Ada Lovelace",
  "is_active": true,
  "created_at": "2026-06-14T10:00:00.000000Z",
  "updated_at": null
}
```

List user có pagination:

```bash
curl 'http://127.0.0.1:8000/users?limit=20&offset=0'
```

Nếu lỗi, API trả envelope thống nhất:

```json
{
  "error": {
    "code": "USER_NOT_FOUND",
    "message": "User not found"
  }
}
```

## Env Vars

| Bien | Mac dinh | Y nghia |
| --- | --- | --- |
| `PORT` | `8000` | Port khi chay bang `python -m app.main` |
| `APP_VERSION` | `0.1.0` | Version tra ve tu `GET /version` |
| `LOG_LEVEL` | `INFO` | Muc log cua app |

File `.env.example` duoc commit de lam mau. File `.env` that bi ignore vi no la config local.

Vi du tao `.env`:

```bash
cp .env.example .env
```

Sau do sua:

```env
PORT=8000
APP_VERSION=2.0.0
LOG_LEVEL=INFO
```

## Middleware Log

Moi request di qua `RequestLoggerMiddleware`. Middleware lam 4 viec:

1. Ghi lai thoi diem bat dau bang `time.perf_counter()`.
2. Goi endpoint that bang `call_next(request)`.
3. Lay `response.status_code`.
4. Tinh `duration_ms` va log mot dong JSON ra stdout.

Log co dang:

```json
{"level":"INFO","logger":"request","event":"request_handled","method":"GET","path":"/health","status":200,"duration_ms":1.23}
```

Khong dung `print()` trong backend service vi `logging` cho phep dieu khien log level, format, va output tot hon.

## Giai Thich Code Chinh

### `app/config.py`

```python
class Settings(BaseSettings):
    port: int = 8000
    app_version: str = "0.1.0"
    log_level: str = "INFO"
```

`BaseSettings` tu `pydantic-settings` tu dong map env var vao field:

- `PORT` -> `port`
- `APP_VERSION` -> `app_version`
- `LOG_LEVEL` -> `log_level`

`get_settings()` co `@lru_cache` de app khong tao lai settings nhieu lan trong mot process.

### `app/main.py`

```python
def create_app(settings: Settings | None = None) -> FastAPI:
    app_settings = settings or get_settings()
    setup_logging(app_settings.log_level)
    app = FastAPI(...)
    app.state.settings = app_settings
    app.add_middleware(RequestLoggerMiddleware)
    register_exception_handlers(app)
    app.include_router(health.router)
    app.include_router(echo.router)
    app.include_router(version.router)
    app.include_router(users.router)
    return app
```

`create_app()` tot hon viec chi viet `app = FastAPI()` vi:

- Test co the tao app moi cho tung fixture.
- Co the truyen settings rieng khi test.
- Setup app nam mot cho, de them middleware/router sau nay.

### `app/schemas/`

Schema tach khoi route de code doc de hon:

- `EchoRequest`: body client gui len.
- `EchoResponse`: body server tra ve.
- `HealthResponse`: response cua `/health`.
- `VersionResponse`: response cua `/version`.
- `UserCreate`: body tạo user, không có `id`.
- `UserUpdate`: body patch user, field optional.
- `UserOut`: response user, có `id`, không trả `password`.
- `ErrorEnvelope`: shape lỗi thống nhất.

Khi body `/echo` thieu `message`, FastAPI và Pydantic trả HTTP `422`, sau đó global handler đổi response thành `{"error": ...}`.

### `app/routes/echo.py`

```python
@router.post("/echo", response_model=EchoResponse)
def echo(payload: EchoRequest) -> EchoResponse:
    return build_echo_response(payload.message)
```

FastAPI lam cac buoc:

1. Doc JSON body.
2. Validate body theo `EchoRequest`.
3. Neu hop le, goi function `echo`.
4. Validate response theo `EchoResponse`.
5. Convert response thanh JSON.

### `app/routes/users.py` và `app/services/user_service.py`

`routes/users.py` chỉ nhận request, validate bằng schema, gọi service, rồi trả `UserOut`.

`services/user_service.py` giữ in-memory `dict[int, UserRecord]` và xử lý:

- tạo id tự tăng;
- reject duplicate email bằng `DuplicateEmailError`;
- trả `UserNotFoundError` khi không thấy user;
- list theo `limit` và `offset`;
- replace, patch, delete user.

### `app/deps.py`

```python
def pagination(limit: int = Query(20, ge=1, le=100), offset: int = Query(0, ge=0)):
    return limit, offset
```

Dependency này được dùng trong `GET /users`, giúp route không phải tự parse query params.

### `app/error_handlers.py`

File này đổi lỗi mặc định của FastAPI từ:

```json
{"detail": "..."}
```

thành:

```json
{"error": {"code": "...", "message": "..."}}
```

## Test

Chay test:

```bash
uv run pytest -v
```

Chay test kem coverage:

```bash
uv run pytest --cov=app --cov-report=term-missing
```

Chạy lint:

```bash
uv run ruff check .
```

Day 11 test suite hiện có unit, integration và E2E tests cho health, echo, version, auth, users, posts và service layer.

Test DB Postgres cho bài Day 11 có thể bật bằng:

```bash
docker compose up -d postgres-test
```

Chay lint:

```bash
uv run ruff check .
```

## Luong Mot Request `/echo`

Khi goi:

```bash
curl -X POST http://127.0.0.1:8000/echo \
  -H "Content-Type: application/json" \
  -d '{"message":"hello"}'
```

Request di qua cac lop:

1. Uvicorn nhan HTTP request.
2. FastAPI app trong `app.main:app` nhan request.
3. `RequestLoggerMiddleware` bat dau bam gio.
4. Router tim thay route `POST /echo`.
5. FastAPI validate body theo `EchoRequest`.
6. Function `echo()` tao `EchoResponse`.
7. FastAPI serialize response thanh JSON.
8. Middleware lay status, tinh `duration_ms`, log mot dong.
9. Uvicorn gui response ve client.

## Loi Thuong Gap

- De tat ca route trong `main.py`: sau nay them endpoint se kho doc va kho test.
- Dung `os.getenv()` rai rac: config bi phan tan, kho biet app can nhung bien nao.
- Dung `print()` de debug request: khong phu hop service that.
- Quen test `422`: API khong chi can test case dung, ma con can test input sai.
- Quen commit `.env.example`: nguoi khac khong biet can env var nao.

## Self-Check

Tu tra loi cac cau nay de chac da hieu:

1. Vi sao test dung `create_app()` thay vi import thang app global?
2. `APP_VERSION=2.0.0` duoc map vao field nao trong `Settings`?
3. Timer trong middleware bat dau va ket thuc o dau?
4. Khi `/echo` thieu `message`, response `422` co key chinh nao?
5. Neu muon them endpoint `GET /users`, ban se tao file o dau va include router o dau?
6. Vi sao `uv.lock` nen duoc commit?

## Definition Of Done

Da hoan thanh khi:

- Cau truc project co `app/` va `tests/`.
- 3 endpoint hoat dong va hien trong `/docs`.
- `uv run pytest -v` pass it nhat 6 tests.
- `uv run ruff check .` clean.
- Middleware log hien ra terminal khi hit endpoint.
- Co `.env.example`, va `.env` nam trong `.gitignore`.
