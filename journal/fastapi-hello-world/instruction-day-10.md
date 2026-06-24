# Instruction: Day 10 Authentication & Authorization

Day 10 thêm auth thật cho API: register, login, JWT bearer token, current user và admin-only delete. Trọng tâm không phải chỉ chạy được endpoint, mà là hiểu vì sao không lưu plaintext password, vì sao JWT payload không được chứa secret, và vì sao authorization nên đặt thành dependency.

## 1. Mục tiêu bài học

Sau bài này bạn cần hiểu:

- Password phải hash bằng bcrypt/argon2, không lưu plaintext.
- JWT có 3 phần: header, payload, signature.
- JWT payload chỉ được signed, không được encrypted; ai có token cũng decode đọc được payload.
- `algorithms=["HS256"]` phải là list khi decode token.
- Login phải dùng cùng một lỗi generic cho email không tồn tại và sai password.
- `401 Unauthorized` dùng cho chưa login/token sai; `403 Forbidden` dùng cho đã login nhưng không đủ quyền.
- Admin-only delete nên enforce bằng dependency, không nhét inline logic vào route.

## 2. File chính trong bài

```text
app/
├── security.py
├── routes/
│   ├── auth.py
│   └── users.py
├── schemas/
│   ├── auth.py
│   └── user.py
├── services/
│   ├── auth_service.py
│   └── user_service.py
└── models/
    └── user.py
```

Ý nghĩa:

- `security.py`: hash password, verify password, create JWT, verify JWT, dependency `get_current_user`, dependency `require_admin`.
- `routes/auth.py`: `POST /auth/register`, `POST /auth/login`.
- `routes/users.py`: thêm `GET /users/me`, sửa `DELETE /users/{user_id}` thành admin-only.
- `services/auth_service.py`: register/login business logic.
- `services/user_service.py`: tạo/sửa user bằng `password_hash`, không lưu plaintext.
- `models/user.py`: dùng `password_hash` thay cho `password`.

## 3. Password hashing

```python
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def hash_password(password: str) -> str:
    return pwd_context.hash(password)


def verify_password(plain_password: str, password_hash: str) -> bool:
    return pwd_context.verify(plain_password, password_hash)
```

Lý do:

- Nếu database leak, attacker không có plaintext password.
- bcrypt chậm có chủ đích để brute-force khó hơn.
- bcrypt hash đã chứa salt, không cần lưu salt riêng.

## 4. JWT

Tạo token:

```python
payload = {
    "sub": str(user_id),
    "role": role,
    "iat": now,
    "exp": expire,
}
jwt.encode(payload, settings.jwt_secret, algorithm="HS256")
```

Verify token:

```python
jwt.decode(token, settings.jwt_secret, algorithms=["HS256"])
```

Lưu ý:

- `sub` là subject, ở đây là user id.
- `exp` là thời điểm hết hạn.
- `role` dùng cho authorization.
- Payload không encrypted, không bỏ password/secret vào JWT.

## 5. Auth endpoints

### Register

```text
POST /auth/register
```

Body:

```json
{
  "email": "ada@example.com",
  "name": "Ada Lovelace",
  "password": "correct-horse-battery"
}
```

Luồng:

```text
RegisterRequest
-> auth_service.register_user()
-> user_service.create_user()
-> hash_password()
-> save User.password_hash
-> return UserOut
```

### Login

```text
POST /auth/login
```

Form fields:

```text
username=ada@example.com
password=correct-horse-battery
```

Lý do dùng `username`: `OAuth2PasswordRequestForm` theo convention OAuth2 dùng field `username`, dù mình truyền email.

Response:

```json
{
  "access_token": "...",
  "token_type": "bearer"
}
```

## 6. Protected endpoint

```text
GET /users/me
```

Header:

```text
Authorization: Bearer <token>
```

Route dùng:

```python
current_user: Annotated[User, Depends(get_current_user)]
```

Nếu token thiếu/sai/hết hạn, response là `401`.

## 7. Admin-only delete

```python
@router.delete("/{user_id}", status_code=204)
async def delete_user(
    user_id: int,
    db: SessionDep,
    _admin: Annotated[User, Depends(require_admin)],
) -> None:
    await user_service.delete_user(db, user_id)
```

Lý do dùng dependency:

- Route vẫn mỏng.
- Có thể tái sử dụng `require_admin` cho endpoint khác.
- Authorization logic tập trung ở `security.py`.

## 8. Migration

Migration:

```text
ffb29e3dd7c8_add_password_hash_for_auth.py
```

Làm:

- Add `users.password_hash`.
- Backfill existing rows bằng một bcrypt hash placeholder.
- Alter `password_hash` thành `NOT NULL`.
- Drop plaintext `users.password`.

Vì sao không add `NOT NULL` ngay?

- DB cũ có row cũ.
- Row cũ chưa có `password_hash`.
- Cần add nullable, backfill, rồi mới not null.

## 9. Verification

```bash
cd journal/fastapi-hello-world
rm -f /tmp/day10_verify.db
DATABASE_URL=sqlite+aiosqlite:////tmp/day10_verify.db DATABASE_ECHO=false uv run alembic upgrade head
DATABASE_URL=sqlite+aiosqlite:////tmp/day10_verify.db DATABASE_ECHO=false uv run alembic current
DATABASE_URL=sqlite+aiosqlite:////tmp/day10_verify.db DATABASE_ECHO=false uv run alembic downgrade -1
DATABASE_URL=sqlite+aiosqlite:////tmp/day10_verify.db DATABASE_ECHO=false uv run alembic upgrade head
DATABASE_URL=sqlite+aiosqlite:////tmp/day10_verify.db DATABASE_ECHO=false uv run alembic check
uv run pytest
uv run ruff check .
```

## 10. Checklist hoàn thành

- [ ] Password hash được lưu trong `password_hash`, không lưu plaintext.
- [ ] `POST /auth/register` hoạt động.
- [ ] `POST /auth/login` trả bearer token.
- [ ] `GET /users/me` cần token.
- [ ] Expired token trả `401`.
- [ ] Wrong password trả generic `401`.
- [ ] Member delete user trả `403`.
- [ ] Admin delete user trả `204`.
- [ ] Migration auth chạy được từ DB rỗng.
- [ ] `pytest` và `ruff` pass.

## 11. Self-check

1. Vì sao không dùng SHA-256 để lưu password?
2. JWT payload có encrypted không?
3. Vì sao login không nói rõ "email không tồn tại" hay "sai password"?
4. `401` khác `403` thế nào?
5. Vì sao `algorithms` khi decode JWT phải là list?
6. Nếu `JWT_SECRET` bị leak thì phải làm gì?
7. Vì sao logout với access-token-only JWT là vấn đề khó?
