# Instruction: Day 5 Hello API

Day 5 là bài chuyển từ "FastAPI hello world" sang một service backend nhỏ nhưng có cấu trúc giống dự án thật.

## Bài Này Học Gì

Mục tiêu là build một API tên `hello-api` có:

| Method | Path | Kết quả |
| --- | --- | --- |
| `GET` | `/health` | `{"status": "ok"}` |
| `POST` | `/echo` | Nhận `{"message": "..."}` và trả lại `{"echo": "...", "received_at": "..."}` |
| `GET` | `/version` | `{"version": "..."}` đọc từ config |

Phần quan trọng không chỉ là 3 endpoint. Phần quan trọng là học cách tổ chức backend:

```text
app/
├── main.py          # tạo FastAPI app
├── config.py        # đọc env vars
├── logging_setup.py # cấu hình logging
├── middleware.py    # log mọi request
├── schemas.py       # định nghĩa request/response models
└── routes/          # tách endpoint theo module
```

Tư duy chính: backend thật không nên nhét hết vào một file. Một file `main.py` có thể ổn khi mới học, nhưng khi có 20 endpoint, config, auth, database, logging, testing thì nó rất nhanh thành khó đọc.

## 1. App Factory Là Gì

Trong `app/main.py`, phần quan trọng nhất là:

```python
def create_app(settings: Settings | None = None) -> FastAPI:
    app_settings = settings or get_settings()
    setup_logging(app_settings.log_level)

    app = FastAPI(
        title="Hello API",
        version=app_settings.app_version,
        description="A small structured FastAPI service for Week 1 review.",
    )

    app.state.settings = app_settings

    app.add_middleware(RequestLoggerMiddleware)
    app.include_router(health.router)
    app.include_router(echo.router)
    app.include_router(version.router)

    return app
```

Đây gọi là `create_app()` factory.

Thay vì chỉ viết:

```python
app = FastAPI()
```

ta viết một function chuyên tạo app.

Lợi ích:

- Test dễ hơn.
- Có thể truyền config riêng khi test.
- Setup middleware/router nằm một chỗ.
- Sau này thêm database/auth/cache dễ hơn.

Cuối file vẫn có:

```python
app = create_app()
```

Dòng này để Uvicorn import được app khi chạy:

```bash
uv run uvicorn app.main:app --reload
```

`app.main:app` nghĩa là:

```text
module: app/main.py
biến: app
```

## 2. Config Bằng Env Vars

Trong `app/config.py`:

```python
class Settings(BaseSettings):
    port: int = 8000
    app_version: str = "0.1.0"
    log_level: str = "INFO"
```

Backend thật không nên hard-code mọi thứ. Ví dụ version, port, log level thường lấy từ môi trường.

Ví dụ:

```bash
APP_VERSION=2.0.0 uv run uvicorn app.main:app --reload
```

Khi gọi:

```bash
curl http://127.0.0.1:8000/version
```

sẽ ra:

```json
{"version":"2.0.0"}
```

Pydantic Settings tự map:

```text
APP_VERSION -> app_version
LOG_LEVEL   -> log_level
PORT        -> port
```

## 3. Schemas Là Gì

Trong `app/schemas.py`:

```python
class EchoRequest(BaseModel):
    message: str = Field(min_length=1, examples=["hello FastAPI"])
```

Đây là model request body cho `/echo`.

Khi client gửi:

```json
{"message":"hello"}
```

FastAPI kiểm tra body này có đúng schema không.

Nếu client gửi sai:

```json
{}
```

FastAPI tự trả:

```json
{
  "detail": [
    {
      "type": "missing",
      "loc": ["body", "message"],
      "msg": "Field required",
      "input": {}
    }
  ]
}
```

Status là `422`.

Điểm quan trọng: không cần tự viết `if` để kiểm tra `message` tồn tại. FastAPI và Pydantic làm giúp.

## 4. Route Tách Riêng

Ví dụ `app/routes/echo.py`:

```python
@router.post("/echo", response_model=EchoResponse)
def echo(payload: EchoRequest) -> EchoResponse:
    return EchoResponse(
        echo=payload.message,
        received_at=datetime.now(UTC).isoformat(),
    )
```

Luồng xử lý:

1. Client gửi `POST /echo`.
2. FastAPI đọc JSON body.
3. FastAPI validate body thành `EchoRequest`.
4. Function `echo()` chạy.
5. Function trả `EchoResponse`.
6. FastAPI convert thành JSON response.

`response_model=EchoResponse` giúp docs đẹp hơn và đảm bảo response trả ra đúng shape.

## 5. Middleware Là Gì

Middleware là lớp nằm giữa request và endpoint.

Trong `app/middleware.py`:

```python
start = time.perf_counter()
response = await call_next(request)
duration_ms = (time.perf_counter() - start) * 1000
```

Nó đo request mất bao lâu.

Sau đó log:

```python
logger.info(
    "request_handled",
    extra={
        "method": request.method,
        "path": request.url.path,
        "status": status_code,
        "duration_ms": round(duration_ms, 2),
    },
)
```

Ví dụ log:

```json
{"level":"INFO","logger":"request","event":"request_handled","method":"GET","path":"/health","status":200,"duration_ms":1.23}
```

Middleware này chạy với mọi endpoint, nên không phải viết log riêng trong từng route.

## 6. Logging Setup

Trong `app/logging_setup.py`, logging được cấu hình để log ra stdout dạng JSON.

Backend service thật thường log ra stdout để Docker, Kubernetes, hoặc server collect log dễ hơn.

Không nên dùng:

```python
print("request done")
```

Nên dùng:

```python
logger.info("request_handled", extra={...})
```

Vì logging có level, format, logger name, và dễ cấu hình hơn.

## Step By Step Dựng Project Từ Đầu

### Bước 1: Tạo Project

```bash
mkdir fastapi-hello-world
cd fastapi-hello-world
uv init
```

### Bước 2: Cài Dependencies

```bash
uv add "fastapi[standard]" pydantic-settings
uv add --dev pytest httpx ruff pre-commit
```

### Bước 3: Tạo Cấu Trúc Thư Mục

```bash
mkdir -p app/routes tests
touch app/__init__.py app/routes/__init__.py tests/__init__.py
```

### Bước 4: Tạo `app/config.py`

Mục đích: gom toàn bộ env vars vào một chỗ.

```python
from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    port: int = 8000
    app_version: str = "0.1.0"
    log_level: str = "INFO"

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )


@lru_cache
def get_settings() -> Settings:
    return Settings()
```

### Bước 5: Tạo `app/schemas.py`

Mục đích: định nghĩa input/output của API.

```python
from pydantic import BaseModel, Field


class HealthResponse(BaseModel):
    status: str = Field(examples=["ok"])


class EchoRequest(BaseModel):
    message: str = Field(min_length=1, examples=["hello FastAPI"])


class EchoResponse(BaseModel):
    echo: str = Field(examples=["hello FastAPI"])
    received_at: str = Field(examples=["2026-06-09T10:30:00.000000+00:00"])


class VersionResponse(BaseModel):
    version: str = Field(examples=["0.1.0"])
```

### Bước 6: Tạo Routes

`app/routes/health.py`:

```python
from fastapi import APIRouter

from app.schemas import HealthResponse

router = APIRouter(tags=["health"])


@router.get("/health", response_model=HealthResponse)
def health_check() -> HealthResponse:
    return HealthResponse(status="ok")
```

`app/routes/echo.py`:

```python
from datetime import UTC, datetime

from fastapi import APIRouter

from app.schemas import EchoRequest, EchoResponse

router = APIRouter(tags=["echo"])


@router.post("/echo", response_model=EchoResponse)
def echo(payload: EchoRequest) -> EchoResponse:
    return EchoResponse(
        echo=payload.message,
        received_at=datetime.now(UTC).isoformat(),
    )
```

`app/routes/version.py`:

```python
from fastapi import APIRouter, Request

from app.schemas import VersionResponse

router = APIRouter(tags=["version"])


@router.get("/version", response_model=VersionResponse)
def version(request: Request) -> VersionResponse:
    return VersionResponse(version=request.app.state.settings.app_version)
```

### Bước 7: Tạo Logging Và Middleware

`app/logging_setup.py`:

```python
import json
import logging
import sys
from typing import Any


class JsonFormatter(logging.Formatter):
    def format(self, record: logging.LogRecord) -> str:
        payload: dict[str, Any] = {
            "level": record.levelname,
            "logger": record.name,
            "event": record.getMessage(),
        }

        for key in ("method", "path", "status", "duration_ms"):
            value = getattr(record, key, None)
            if value is not None:
                payload[key] = value

        return json.dumps(payload, separators=(",", ":"))


def setup_logging(log_level: str) -> None:
    handler = logging.StreamHandler(sys.stdout)
    handler.setFormatter(JsonFormatter())

    root_logger = logging.getLogger()
    root_logger.handlers.clear()
    root_logger.addHandler(handler)
    root_logger.setLevel(log_level.upper())
```

`app/middleware.py`:

```python
import logging
import time
from collections.abc import Callable

from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import Response

logger = logging.getLogger("request")


class RequestLoggerMiddleware(BaseHTTPMiddleware):
    async def dispatch(
        self,
        request: Request,
        call_next: Callable[[Request], Response],
    ) -> Response:
        start = time.perf_counter()
        status_code = 500

        try:
            response = await call_next(request)
            status_code = response.status_code
            return response
        finally:
            duration_ms = (time.perf_counter() - start) * 1000
            logger.info(
                "request_handled",
                extra={
                    "method": request.method,
                    "path": request.url.path,
                    "status": status_code,
                    "duration_ms": round(duration_ms, 2),
                },
            )
```

### Bước 8: Tạo `app/main.py`

Mục đích: nối tất cả thành app chạy được.

```python
import uvicorn
from fastapi import FastAPI

from app.config import Settings, get_settings
from app.logging_setup import setup_logging
from app.middleware import RequestLoggerMiddleware
from app.routes import echo, health, version


def create_app(settings: Settings | None = None) -> FastAPI:
    app_settings = settings or get_settings()
    setup_logging(app_settings.log_level)

    app = FastAPI(
        title="Hello API",
        version=app_settings.app_version,
        description="A small structured FastAPI service for Week 1 review.",
    )
    app.state.settings = app_settings

    app.add_middleware(RequestLoggerMiddleware)
    app.include_router(health.router)
    app.include_router(echo.router)
    app.include_router(version.router)

    return app


app = create_app()


if __name__ == "__main__":
    uvicorn.run("app.main:app", host="0.0.0.0", port=get_settings().port, reload=True)
```

### Bước 9: Chạy App

```bash
uv run uvicorn app.main:app --reload
```

Test nhanh:

```bash
curl http://127.0.0.1:8000/health
curl http://127.0.0.1:8000/version
curl -X POST http://127.0.0.1:8000/echo \
  -H "Content-Type: application/json" \
  -d '{"message":"hello"}'
```

### Bước 10: Viết Test

`tests/conftest.py` tạo client dùng chung:

```python
import pytest
from fastapi.testclient import TestClient

from app.config import Settings
from app.main import create_app


@pytest.fixture
def client() -> TestClient:
    app = create_app(Settings(app_version="9.9.9", log_level="INFO"))
    return TestClient(app)
```

Điểm hay: test truyền `app_version="9.9.9"` nên không phụ thuộc env thật của máy.

Ví dụ test `/health`:

```python
from fastapi.testclient import TestClient


def test_health_returns_ok(client: TestClient) -> None:
    response = client.get("/health")

    assert response.status_code == 200
    assert response.json() == {"status": "ok"}
```

Ví dụ test `/echo` body sai:

```python
from fastapi.testclient import TestClient


def test_echo_rejects_missing_message(client: TestClient) -> None:
    response = client.post("/echo", json={})

    assert response.status_code == 422
    body = response.json()
    assert "detail" in body
    assert body["detail"][0]["loc"] == ["body", "message"]
```

Chạy test và lint:

```bash
uv run pytest -v
uv run ruff check .
```

## Cách Nghĩ Khi Thêm Endpoint Mới

Ví dụ sau này muốn thêm:

```text
GET /users
```

Làm theo pattern:

1. Thêm schema trong `app/schemas.py` nếu cần.
2. Tạo file `app/routes/users.py`.
3. Tạo `router = APIRouter(tags=["users"])`.
4. Viết `@router.get("/users")`.
5. Quay lại `app/main.py` include `users.router`.
6. Viết test trong `tests/test_users.py`.

## Cốt Lõi Cần Nhớ

```text
main.py       nối app lại
config.py     đọc cấu hình
schemas.py    định nghĩa dữ liệu vào/ra
routes/        chứa endpoint
middleware.py  xử lý request chung
tests/         chứng minh API chạy đúng
```

Đừng học từ code trước. Hãy học theo luồng request:

```text
curl
-> uvicorn
-> FastAPI app
-> middleware
-> router
-> schema validation
-> route function
-> response model
-> middleware log
-> client
```

## Có Cần Tạo Project Mới Không?

Không cần tạo project mới để làm bài Day 5 này.

Project hiện tại `fastapi-hello-world` đã được nâng cấp thành đúng artifact của bài:

- Có cấu trúc `app/`.
- Có cấu trúc `tests/`.
- Có 3 endpoint bắt buộc.
- Có config từ env vars.
- Có middleware log request.
- Có test happy path và edge case.
- Có README và instruction để học lại.

Nếu tạo project mới ngay bây giờ, mày sẽ có hai project gần giống nhau và dễ bị rối:

```text
fastapi-hello-world/   # project đang học
hello-api/             # project mới giống y chang
```

Cách hợp lý hơn:

1. Dùng project hiện tại để hiểu bài và nộp bài.
2. Nếu muốn luyện lại từ đầu, tạo một thư mục practice riêng sau khi đã hiểu flow.
3. Khi luyện lại, không copy code ngay; tự dựng theo checklist bên dưới.

Nếu muốn tạo bản luyện tay, đặt tên rõ:

```bash
cd ..
mkdir hello-api-practice
cd hello-api-practice
uv init
```

Nhưng bài chính thì cứ dùng `fastapi-hello-world`.

## Required Reading

Trước hoặc sau khi code xong, đọc lướt các phần này để hiểu tại sao bài bắt làm như vậy:

| Chủ đề | Link | Đọc để hiểu gì |
| --- | --- | --- |
| FastAPI Bigger Applications | `https://fastapi.tiangolo.com/tutorial/bigger-applications/` | Vì sao phải tách routes thay vì nhét hết vào `main.py` |
| FastAPI Middleware | `https://fastapi.tiangolo.com/tutorial/middleware/` | Middleware nằm ở đâu trong luồng request |
| Pydantic Settings | `https://docs.pydantic.dev/latest/concepts/pydantic_settings/` | Cách đọc env vars bằng `BaseSettings` |
| httpx docs | `https://www.python-httpx.org` | Nền tảng của HTTP client dùng trong test |

Không cần đọc thuộc lòng. Mục tiêu là biết tài liệu chính thức nằm ở đâu và phần code của mình đang áp dụng concept nào.

## Exercises / Deliverable

Đây là checklist bài tập chính. Với project hiện tại, mày dùng checklist này để tự kiểm tra.

### Bài 1: Scaffold Project

Mục tiêu: project có cấu trúc chuẩn.

Checklist:

- Có `pyproject.toml`.
- Có `uv.lock`.
- Có `app/`.
- Có `tests/`.
- Có `.env.example`.
- Có `.gitignore`.
- Có `.pre-commit-config.yaml`.

Lệnh kiểm tra:

```bash
find . -maxdepth 3 -type f | sort
```

### Bài 2: Cài Dependency

Mục tiêu: dependency chính và dev dependency nằm trong `pyproject.toml`.

Dependency chính:

- `fastapi[standard]`
- `pydantic-settings`

Dev dependency:

- `pytest`
- `httpx`
- `ruff`
- `pre-commit`

Lệnh kiểm tra:

```bash
uv sync
```

### Bài 3: Implement 3 Routes

Mục tiêu: mỗi route nằm trong module riêng.

Checklist:

- `GET /health` nằm trong `app/routes/health.py`.
- `POST /echo` nằm trong `app/routes/echo.py`.
- `GET /version` nằm trong `app/routes/version.py`.
- `app/main.py` include cả 3 router.

Lệnh chạy app:

```bash
uv run uvicorn app.main:app --reload
```

Lệnh test thủ công:

```bash
curl http://127.0.0.1:8000/health
curl http://127.0.0.1:8000/version
curl -X POST http://127.0.0.1:8000/echo \
  -H "Content-Type: application/json" \
  -d '{"message":"hello"}'
```

### Bài 4: Verify 422

Mục tiêu: request body sai phải trả `422` bằng default Pydantic error envelope.

Gọi:

```bash
curl -i -X POST http://127.0.0.1:8000/echo \
  -H "Content-Type: application/json" \
  -d '{}'
```

Kết quả cần thấy:

```text
HTTP/1.1 422 Unprocessable Entity
```

Body có key:

```json
{
  "detail": [...]
}
```

### Bài 5: Verify Middleware Log

Mục tiêu: mỗi request tạo một dòng log có đủ:

- `method`
- `path`
- `status`
- `duration_ms`

Khi gọi:

```bash
curl http://127.0.0.1:8000/health
```

Terminal chạy server cần thấy log dạng:

```json
{"level":"INFO","logger":"request","event":"request_handled","method":"GET","path":"/health","status":200,"duration_ms":1.23}
```

### Bài 6: Viết Tests

Mục tiêu: ít nhất 6 tests, mỗi route có 2 test.

Checklist:

- `/health` happy path.
- `/health` edge case, ví dụ sai method.
- `/echo` happy path.
- `/echo` body sai trả `422`.
- `/version` happy path.
- `/version` edge case, ví dụ sai method.

Lệnh kiểm tra:

```bash
uv run pytest -v
```

### Bài 7: Verify Swagger UI

Mục tiêu: docs tự động hiển thị sạch.

Chạy app rồi mở:

```text
http://127.0.0.1:8000/docs
```

Checklist:

- Thấy endpoint `/health`.
- Thấy endpoint `/echo`.
- Thấy endpoint `/version`.
- Thấy model `EchoRequest`.
- Thấy model `EchoResponse`.

### Bài 8: README / Instruction

Mục tiêu: người khác clone project về có thể chạy được.

README hoặc instruction cần có:

- Mô tả project.
- Cách install bằng `uv sync`.
- Cách run bằng `uv run uvicorn app.main:app --reload`.
- Cách test bằng `uv run pytest`.
- Bảng env vars.
- Cách mở `/docs`.

## Common Pitfalls

Các lỗi hay gặp trong bài này:

1. Nhét mọi thứ vào `main.py`.

   Làm vậy chạy được, nhưng sai mục tiêu bài học. Bài này đang luyện project layout.

2. Dùng `os.getenv()` rải rác.

   Config nên nằm ở `app/config.py`, không nên mỗi file tự đọc env.

3. Import app global trong test rồi phụ thuộc env thật.

   Nên dùng `create_app()` và truyền `Settings` riêng cho test.

4. Dùng `print()` để log request.

   Service thật nên dùng `logging`, vì có level và format rõ ràng.

5. Logging bằng f-string trong `logger.info()`.

   Không nên:

   ```python
   logger.info(f"handled {request.method} {request.url.path}")
   ```

   Nên:

   ```python
   logger.info("request_handled", extra={"method": request.method})
   ```

6. Quên ignore file local.

   `.gitignore` nên có:

   ```gitignore
   .env
   .venv/
   __pycache__/
   *.py[cod]
   .pytest_cache/
   .ruff_cache/
   ```

7. Quên test case `422`.

   API không chỉ cần chạy đúng khi input đúng. Nó còn phải xử lý input sai đúng cách.

## Self-Check

Tự trả lời mấy câu này. Nếu trả lời được bằng lời của mình, coi như hiểu bài.

1. Vì sao dùng `create_app()` thay vì chỉ viết `app = FastAPI()` ở top-level?
2. `APP_VERSION=2.0.0` đi qua những bước nào để cuối cùng `/version` trả `2.0.0`?
3. Middleware bắt đầu bấm giờ ở đâu và dừng ở đâu?
4. Khi `/echo` thiếu `message`, vì sao FastAPI trả `422` mà mình không cần tự viết `if`?
5. Response lỗi mặc định của FastAPI có key chính nào?
6. Vì sao dùng `TestClient` trong test dù endpoint có thể là async?
7. Nếu thêm `GET /users`, cần tạo file nào và sửa file nào?
8. Vì sao `.env.example` được commit nhưng `.env` thì không?
9. Vì sao `uv.lock` nên được commit?
10. Một request `curl /echo` đi qua những lớp nào trước khi trả response?

## Definition Of Done

Bài này hoàn thành khi:

- Project structure có `app/` và `tests/`.
- 3 endpoint hoạt động.
- `/docs` hiển thị đủ endpoint và models.
- `uv run pytest -v` pass ít nhất 6 tests.
- `uv run ruff check .` clean.
- Middleware log hiện trong terminal khi hit endpoint.
- `.env.example` có trong project.
- `.env` nằm trong `.gitignore`.
- README/instruction đủ để mentor hoặc người khác chạy từ đầu.

Lệnh kiểm tra cuối:

```bash
uv sync
uv run pytest -v
uv run ruff check .
uv run uvicorn app.main:app --reload
```

Sau đó mở:

```text
http://127.0.0.1:8000/docs
```

## Week 1 Review Focus

Khi demo với mentor, đừng chỉ nói "em làm xong API". Hãy demo theo thứ tự này:

1. Mở Swagger UI ở `/docs`.
2. Gọi `GET /health` và cho thấy response `{"status":"ok"}`.
3. Gọi `POST /echo` với body đúng và cho thấy response có `received_at`.
4. Gọi `POST /echo` với `{}` và cho thấy response `422`.
5. Nhìn terminal và chỉ ra middleware log có `method`, `path`, `status`, `duration_ms`.
6. Mở `app/main.py` và chỉ nơi include router.
7. Mở `app/routes/echo.py` để chỉ nơi thêm logic endpoint.
8. Mở `tests/test_echo.py` để chỉ test happy path và edge case.
9. Nói một concept chưa chắc, ví dụ middleware hoặc app factory, để mentor giải thích thêm.

## Nếu Muốn Tự Luyện Lại Từ Đầu

Sau khi hiểu project hiện tại, có thể tự luyện bằng project mới. Khi đó không nhìn code cũ ngay.

Tạo project practice:

```bash
cd /home/home-austin/Training/D1/be-fast-api-training-trainee/journal
mkdir hello-api-practice
cd hello-api-practice
uv init
```

Luật luyện:

1. Chỉ nhìn checklist trong file này.
2. Tự tạo từng file.
3. Chạy test sau mỗi endpoint.
4. Khi bí quá mới mở project `fastapi-hello-world` để so sánh.

Nhưng đây là phần luyện thêm, không phải bắt buộc để hoàn thành bài Day 5.
