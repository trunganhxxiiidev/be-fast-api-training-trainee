# Instruction: Day 6 FastAPI Deep Dive

Day 6 là bài chuyển project Day 5 từ service nhỏ sang cấu trúc backend dễ mở rộng hơn. Mục tiêu không chỉ là có thêm `/users`, mà là học cách chia trách nhiệm giữa route, schema, service, dependency và error handler.

## 1. Mục tiêu bài học

Sau bài này bạn cần hiểu:

- `APIRouter` giúp chia endpoint theo nhóm.
- `Depends()` giúp gom logic dùng chung, ví dụ pagination.
- Pydantic model nên tách request và response.
- Route handler nên mỏng: nhận request, gọi service, trả response.
- Business logic nên nằm trong `services/`.
- Error response nên thống nhất một format.

## 2. Branch làm bài

Từ root repo:

```bash
cd ~/Training/D1/be-fast-api-training-trainee
git status --short --branch
git pull --ff-only origin main
git switch -c feature/day-06-fastapi-deep-dive
```

Không làm trực tiếp trên `main` vì rule của khóa học yêu cầu feature branch.

## 3. Project cần sửa

Day 6 tiếp tục từ project Day 5:

```bash
cd journal/fastapi-hello-world
```

Chạy test nền trước khi sửa:

```bash
uv run pytest
uv run ruff check .
```

## 4. Refactor schema

Day 5 có một file:

```text
app/schemas.py
```

Day 6 đổi thành package:

```text
app/schemas/
├── __init__.py
├── echo.py
├── error.py
├── health.py
├── user.py
└── version.py
```

Lý do: khi app lớn lên, gom mọi model vào một file sẽ khó đọc. Mỗi domain nên có schema riêng.

## 5. Thêm service layer

Tạo:

```text
app/services/
├── __init__.py
├── echo_service.py
└── user_service.py
```

`echo_service.py` giữ logic tạo response echo.

`user_service.py` giữ business logic của users:

- lưu user trong `dict[int, UserRecord]`;
- tạo id tự tăng;
- kiểm tra email duplicate;
- get/list/replace/patch/delete user;
- raise domain exception khi lỗi.

Điểm quan trọng: service không import FastAPI. Nhờ vậy logic dễ test và sau này dễ thay in-memory bằng database.

## 6. Thêm dependency pagination

Tạo `app/deps.py`:

```python
def pagination(
    limit: Annotated[int, Query(ge=1, le=100)] = 20,
    offset: Annotated[int, Query(ge=0)] = 0,
) -> tuple[int, int]:
    return limit, offset
```

Trong route dùng:

```python
page: Annotated[tuple[int, int], Depends(pagination)]
```

FastAPI sẽ tự đọc `?limit=20&offset=0`, validate giới hạn, rồi inject vào function.

## 7. Thêm route `/users`

Tạo `app/routes/users.py` với 6 endpoint:

```text
POST   /users
GET    /users?limit=20&offset=0
GET    /users/{user_id}
PUT    /users/{user_id}
PATCH  /users/{user_id}
DELETE /users/{user_id}
```

Route chỉ nên làm 3 việc:

1. nhận payload/path/query;
2. gọi `user_service`;
3. convert kết quả sang `UserOut`.

Không nhét duplicate-email logic hoặc list slicing trực tiếp trong route.

## 8. Global error envelope

Tạo:

```text
app/exceptions.py
app/error_handlers.py
```

`exceptions.py` chứa lỗi domain:

```text
UserNotFoundError -> 404 USER_NOT_FOUND
DuplicateEmailError -> 409 DUPLICATE_EMAIL
```

`error_handlers.py` đổi lỗi thành format:

```json
{
  "error": {
    "code": "USER_NOT_FOUND",
    "message": "User not found"
  }
}
```

Validation error cũng dùng format này:

```json
{
  "error": {
    "code": "VALIDATION_ERROR",
    "message": "Invalid request",
    "details": []
  }
}
```

## 9. Nối vào `app/main.py`

Trong `create_app()`:

```python
register_exception_handlers(app)
app.include_router(users.router)
```

Thứ tự setup app nên rõ ràng:

1. load settings;
2. setup logging;
3. tạo `FastAPI`;
4. add middleware;
5. register exception handlers;
6. include routers.

## 10. Tests cần có

Day 6 cần test:

- create rồi get user;
- duplicate email trả `409`;
- list user với pagination;
- `PUT` replace user;
- `PATCH` update user;
- delete user trả `204`;
- get missing user trả `404`;
- validation error trả `422` theo error envelope.

Chạy:

```bash
uv run pytest
uv run ruff check .
```

## 11. Git commit và push

Từ root repo:

```bash
cd ~/Training/D1/be-fast-api-training-trainee
git status --short
git add journal/fastapi-hello-world journal/2026-06-14.md
git diff --cached --stat
git diff --cached --name-only
git commit -m "feat: add day 6 users crud"
git push -u origin feature/day-06-fastapi-deep-dive
```

Sau khi push, mở GitHub và tạo pull request từ:

```text
feature/day-06-fastapi-deep-dive -> main
```

## 12. Cách tự kiểm tra bằng curl

Chạy app:

```bash
uv run uvicorn app.main:app --reload
```

Tạo user:

```bash
curl -X POST http://127.0.0.1:8000/users \
  -H "Content-Type: application/json" \
  -d '{"email":"ada@example.com","name":"Ada Lovelace","password":"correct-horse-battery","is_active":true}'
```

List user:

```bash
curl 'http://127.0.0.1:8000/users?limit=20&offset=0'
```

Get user:

```bash
curl http://127.0.0.1:8000/users/1
```

Patch user:

```bash
curl -X PATCH http://127.0.0.1:8000/users/1 \
  -H "Content-Type: application/json" \
  -d '{"name":"Countess Ada"}'
```

Delete user:

```bash
curl -X DELETE http://127.0.0.1:8000/users/1 -i
```

## 13. Self-check

- Vì sao `UserCreate` và `UserOut` không nên là cùng một class?
- Vì sao service không nên import FastAPI?
- `Depends(pagination)` khác gì so với tự gọi `pagination()` trong route?
- Khi `PATCH` dùng `model_dump(exclude_unset=True)`, nó giúp phân biệt điều gì?
- Vì sao duplicate email nên trả `409` thay vì `400`?
