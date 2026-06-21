# Instruction: Day 8 SQLAlchemy 2.0

Day 8 chuyển project từ `/users` in-memory sang database thật bằng SQLAlchemy ORM 2.0. Bài này có thể học như điểm bắt đầu FastAPI luôn: không cần giả lập dict trong memory, học thẳng luồng API thật với request, schema, service, ORM model, session và database.

## 1. Mục tiêu bài học

Sau bài này bạn cần hiểu:

- SQLAlchemy model là class Python map với table trong database.
- Pydantic schema khác SQLAlchemy model ở trách nhiệm nào.
- `AsyncSession` là một phiên làm việc với database trong mỗi request.
- `async def`, `await`, `async with` dùng khi code phải chờ I/O như database query.
- `Mapped[int]` mô tả type của ORM attribute, còn `mapped_column(...)` mô tả column thật trong database.
- `db.add()` đưa object vào session, `db.flush()` gửi SQL xuống DB nhưng chưa commit, `commit()` mới chốt transaction.
- `relationship()` mô tả quan hệ giữa bảng ở tầng Python.
- N+1 query là gì và vì sao dùng `selectinload()`.

## 2. File chính trong bài

```text
app/
├── db.py
├── models/
│   ├── base.py
│   ├── user.py
│   ├── post.py
│   └── comment.py
├── routes/
│   ├── users.py
│   └── posts.py
├── schemas/
│   ├── user.py
│   └── post.py
└── services/
    ├── user_service.py
    └── post_service.py
```

Ý nghĩa:

- `app/db.py`: tạo engine, session factory và FastAPI dependency `SessionDep`.
- `app/models/`: SQLAlchemy ORM models, đại diện cho table.
- `app/schemas/`: Pydantic schemas, validate request và shape response.
- `app/routes/`: endpoint HTTP.
- `app/services/`: business logic và SQLAlchemy queries.

## 3. Luồng request

Ví dụ `POST /users`:

```text
JSON request
-> UserCreate validate body
-> users.py route nhận payload + db session
-> user_service.create_user()
-> SQLAlchemy tạo User model
-> db.add(user)
-> await db.flush()
-> get_session() commit cuối request
-> UserOut serialize response
-> JSON response
```

## 4. Database dependency

```python
engine = create_async_engine(
    settings.database_url,
    echo=settings.database_echo,
)
SessionLocal = async_sessionmaker(engine, expire_on_commit=False)
```

Giải thích:

- `engine`: quản lý kết nối tới database.
- `echo=True`: in SQL thật ra terminal để học.
- `async_sessionmaker`: tạo session mới cho mỗi request.
- `expire_on_commit=False`: sau commit object vẫn đọc được field trong FastAPI response.

```python
async def get_session() -> AsyncGenerator[AsyncSession, None]:
    async with SessionLocal() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
```

Giải thích:

- `async with`: mở/đóng session theo kiểu async.
- `yield session`: đưa session cho route dùng.
- code sau `yield` chạy sau khi route xử lý xong.
- thành công thì `commit()`.
- lỗi thì `rollback()`.

## 5. Model typed style

```python
id: Mapped[int] = mapped_column(primary_key=True)
```

Tách nghĩa:

- `id`: tên attribute trong Python.
- `Mapped[int]`: ORM attribute này có kiểu Python là `int`.
- `mapped_column(primary_key=True)`: column thật trong DB là primary key.

```python
email: Mapped[str] = mapped_column(String(255), unique=True, index=True)
```

Nghĩa là:

- Python đọc `user.email` như string.
- Database tạo column string.
- `unique=True` chặn email trùng.
- `index=True` giúp tìm theo email nhanh hơn.

## 6. Relationship

```python
class User(Base):
    posts: Mapped[list["Post"]] = relationship(back_populates="author")


class Post(Base):
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"))
    author: Mapped["User"] = relationship(back_populates="posts")
```

Ý nghĩa:

- `Post.user_id` là foreign key thật trong database.
- `User.posts` là shortcut Python để lấy posts của user.
- `Post.author` là shortcut Python để lấy user viết post.
- `back_populates` nối hai chiều relationship.

## 7. N+1 query

Ví dụ xấu:

```python
result = await db.execute(select(User))
users = result.scalars().all()

for user in users:
    print(user.posts)
```

Nếu có 100 users, ORM có thể chạy:

```text
1 query lấy users
100 query lấy posts từng user
```

Đây là N+1.

Cách fix trong bài:

```python
result = await db.execute(
    select(User).options(selectinload(User.posts)).where(User.id == user_id)
)
```

`selectinload(User.posts)` thường chạy thêm một query dạng:

```sql
SELECT posts.*
FROM posts
WHERE posts.user_id IN (...)
```

Như vậy list relationship không bị query từng row.

## 8. Bài tập đã làm

- Thêm SQLAlchemy async dependencies: `sqlalchemy[asyncio]`, `asyncpg`, `aiosqlite`.
- Thêm `app/db.py`.
- Thêm models `User`, `Post`, `Comment`.
- Chuyển `/users` CRUD sang database.
- Thêm `/posts` CRUD.
- Thêm `GET /users/{user_id}/posts` dùng relationship path.
- Day 8 ban đầu dùng script tạo table tạm; sang Day 9 script này được thay bằng Alembic migrations.
- Thêm tests dùng SQLite async in-memory.

## 9. Verification

```bash
cd journal/fastapi-hello-world
DATABASE_URL=sqlite+aiosqlite:////tmp/day08_verify.db DATABASE_ECHO=false uv run alembic upgrade head
uv run pytest
uv run ruff check .
```

## 10. Checklist tự học

- [ ] Giải thích được `async def` và `await` trong route/service.
- [ ] Giải thích được `SessionDep` đến từ đâu.
- [ ] Giải thích được SQLAlchemy model khác Pydantic schema thế nào.
- [ ] Giải thích được `Mapped[int]` và `mapped_column(...)`.
- [ ] Giải thích được `db.add()`, `db.flush()`, `commit()`, `rollback()`.
- [ ] Giải thích được `ForeignKey` và `relationship`.
- [ ] Giải thích được N+1 query và vì sao `selectinload` giúp.
- [ ] Chạy được tests và ruff.

## 11. Self-check

1. Vì sao mỗi request nên có một DB session riêng?
2. Nếu route gọi `db.add(user)` nhưng không `flush()` hoặc `commit()`, chuyện gì xảy ra?
3. Vì sao response schema không trả `password`?
4. `Post.user_id` khác `Post.author` ở điểm nào?
5. `User.posts` có phải column trong database không?
6. N+1 query xuất hiện khi nào?
7. Vì sao Day 8 dùng `create_all`, nhưng Day 9 sẽ chuyển sang Alembic?
