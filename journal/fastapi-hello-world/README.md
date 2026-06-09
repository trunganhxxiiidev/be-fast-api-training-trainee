# Hello API

Day 5 bien project FastAPI hello world thanh mot service nho nhung co cau truc gan voi cach lam that: tach route, tach schema, config doc tu bien moi truong, middleware log request, va test bang HTTP client.

Service nay co 3 endpoint:

| Method | Path | Ket qua |
| --- | --- | --- |
| `GET` | `/health` | Tra ve `{"status": "ok"}` |
| `POST` | `/echo` | Nhan `{"message": str}` va tra ve message kem timestamp |
| `GET` | `/version` | Tra ve version doc tu config |

## Muc Tieu Bai Hoc

Sau bai nay ban can nam duoc:

- Vi sao project backend khong nen de tat ca code trong mot file `main.py`.
- Cach dung `create_app()` factory de tao FastAPI app ro rang va de test.
- Cach tach request/response model bang Pydantic.
- Cach doc config tu env var bang `pydantic-settings`.
- Cach viet middleware do thoi gian request va log ra stdout.
- Cach viet test cho endpoint thanh cong va request sai body.

## Cau Truc Project

```text
fastapi-hello-world/
├── app/
│   ├── __init__.py
│   ├── main.py
│   ├── config.py
│   ├── logging_setup.py
│   ├── middleware.py
│   ├── schemas.py
│   └── routes/
│       ├── __init__.py
│       ├── health.py
│       ├── echo.py
│       └── version.py
├── tests/
│   ├── __init__.py
│   ├── conftest.py
│   ├── test_health.py
│   ├── test_echo.py
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
- `app/config.py`: noi doc `PORT`, `APP_VERSION`, `LOG_LEVEL`.
- `app/logging_setup.py`: cau hinh log JSON ra stdout.
- `app/middleware.py`: do moi request mat bao lau va log mot dong.
- `app/schemas.py`: dinh nghia shape request/response.
- `app/routes/`: moi file la mot nhom endpoint rieng.
- `tests/`: test endpoint bang `TestClient`.
- `main.py`: shim de command cu `main:app` van import duoc.

## Cai Dat

Can co `uv` tren may. Tu thu muc project:

```bash
cd fastapi-hello-world
uv sync
```

Lenh `uv sync` doc `pyproject.toml` va `uv.lock`, sau do tao/cap nhat `.venv` dung version dependency cua project.

## Chay App

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

Swagger UI o `/docs` se hien 3 endpoint va schema `EchoRequest`, `EchoResponse`, `HealthResponse`, `VersionResponse`.

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
    app.include_router(health.router)
    app.include_router(echo.router)
    app.include_router(version.router)
    return app
```

`create_app()` tot hon viec chi viet `app = FastAPI()` vi:

- Test co the tao app moi cho tung fixture.
- Co the truyen settings rieng khi test.
- Setup app nam mot cho, de them middleware/router sau nay.

### `app/schemas.py`

Schema tach khoi route de code doc de hon:

- `EchoRequest`: body client gui len.
- `EchoResponse`: body server tra ve.
- `HealthResponse`: response cua `/health`.
- `VersionResponse`: response cua `/version`.

Khi body `/echo` thieu `message`, FastAPI va Pydantic tu dong tra ve HTTP `422` voi envelope mac dinh co key `detail`.

### `app/routes/echo.py`

```python
@router.post("/echo", response_model=EchoResponse)
def echo(payload: EchoRequest) -> EchoResponse:
    return EchoResponse(
        echo=payload.message,
        received_at=datetime.now(UTC).isoformat(),
    )
```

FastAPI lam cac buoc:

1. Doc JSON body.
2. Validate body theo `EchoRequest`.
3. Neu hop le, goi function `echo`.
4. Validate response theo `EchoResponse`.
5. Convert response thanh JSON.

## Test

Chay test:

```bash
uv run pytest -v
```

Project hien co 6 test:

- `/health` happy path.
- `/health` reject sai method.
- `/echo` happy path.
- `/echo` body thieu `message` tra ve `422`.
- `/version` doc version tu settings.
- `/version` reject sai method.

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
