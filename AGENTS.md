# AGENTS.md

File này là luật làm việc cho Codex/ChatGPT và các coding agent khi làm trong repo training này.

Mục tiêu: mỗi lần agent code, làm bài tập, viết journal, commit hoặc push thì phải tuân thủ workflow của khóa học trong `README.md`.

## Source Of Truth

Trước khi làm bài mới, đọc các file liên quan theo thứ tự:

1. `README.md` để nắm rule chung của khóa học.
2. File lesson tương ứng trong `days/day-XX-*.md`.
3. File week overview tương ứng nếu cần, ví dụ `week-1-fundamentals.md`.
4. Các file hiện có trong `journal/` để không làm lệch lịch sử học tập.
5. README/instruction của project con nếu đang làm trong một project cụ thể.

Nếu user đưa pasted text hoặc file bài học mới, đọc file đó trước rồi mới code.

## Course Ground Rules

Agent phải tuân thủ các rule từ khóa học:

- Commit nhỏ, tập trung vào một mục tiêu rõ ràng.
- Nếu bị kẹt, đọc lỗi trước và giải thích đã thử gì.
- Không copy-paste code từ AI mà không giải thích được.
- Viết test cho phần không tầm thường.
- Giữ journal hằng ngày.
- Nộp bài bằng branch/PR sạch, có test/lint pass khi có thể.

## Daily Journal Rule

Mỗi ngày làm bài training, tạo hoặc cập nhật:

```text
journal/YYYY-MM-DD.md
```

Journal nên có:

- `What I Learned`: học được gì.
- `What I Built`: đã build gì.
- `Verification`: đã chạy lệnh nào, kết quả gì.
- `Blockers`: bị kẹt gì.
- `Question`: một câu hỏi để hỏi mentor.

Không cần viết dài cho có. Viết thật, ngắn, rõ.

## Coding Rules

Khi code trong repo này:

- Ưu tiên pattern có sẵn trong project.
- Không nhét mọi thứ vào một file nếu lesson yêu cầu project structure.
- Với FastAPI, ưu tiên:
  - `create_app()` factory khi phù hợp.
  - routes tách trong `app/routes/`.
  - schemas Pydantic trong module riêng.
  - config/env vars gom vào module config.
  - logging thay vì `print()`.
  - tests cho happy path và edge/error case.
- Không tạo abstraction mới nếu chưa cần.
- Không sửa file ngoài phạm vi bài học nếu không có lý do rõ.
- Không xóa hoặc revert thay đổi của user nếu user không yêu cầu.

## Verification Rules

Trước khi commit/push code Python, chạy lệnh phù hợp với project.

Với project dùng `uv`, thường chạy:

```bash
uv run pytest
uv run ruff check .
```

Nếu project nằm trong thư mục con, chạy các lệnh trên ở đúng thư mục project con.

Nếu test/lint fail:

- Không che giấu lỗi.
- Giải thích lỗi fail là gì.
- Chỉ commit/push code fail nếu user yêu cầu push WIP hoặc có lý do rõ.

## Git Rules

Trước khi sửa hoặc commit:

```bash
git status --short --branch
```

Trước khi commit:

```bash
git diff --cached --stat
git diff --cached --name-only
```

Luật Git:

- Làm trên feature branch, không làm trực tiếp trên `main` trừ khi user yêu cầu rõ.
- Commit message ngắn, scoped, có ý nghĩa.
- Chỉ stage file liên quan đến task hiện tại.
- Không commit `.venv/`, cache, `.env`, `__pycache__/`, `.pytest_cache/`, `.ruff_cache/`.
- Không dùng lệnh phá hủy như `git reset --hard`, `git checkout --`, `git clean -fd` nếu user không yêu cầu rõ.
- Khi push, push branch hiện tại hoặc branch user chỉ định.

## Push / PR Rules

Trước khi push:

1. Kiểm tra branch hiện tại.
2. Kiểm tra working tree.
3. Chạy verification phù hợp.
4. Đảm bảo journal ngày hiện tại đã được cập nhật nếu đây là bài training.

Sau khi push, báo cho user:

- Branch đã push.
- Commit hash.
- Các lệnh verification đã chạy.
- Kết quả pass/fail.

## Learning / Teaching Rules

Vì repo này là training repo, agent không chỉ code xong rồi thôi.

Khi user yêu cầu học bài hoặc làm bài tập:

- Giải thích mục tiêu bài học.
- Nêu concept chính.
- Nêu step-by-step cách dựng.
- Chỉ ra file nào chịu trách nhiệm phần nào.
- Thêm checklist bài tập nếu bài có deliverable.
- Thêm self-check questions nếu phù hợp.

Nếu tạo tài liệu tiếng Việt, viết tiếng Việt có dấu.

## File Placement Rules

- Course journal nằm trong `journal/`.
- Project bài tập có thể nằm trong `journal/<project-name>/` nếu đang theo pattern hiện tại.
- Rule cho agent nằm ở root repo: `AGENTS.md`.
- Nếu cần hỗ trợ Claude, có thể tạo `CLAUDE.md` trỏ về `AGENTS.md`.

## Current Repo Notes

Repo remote hiện tại là trainee repo:

```text
git@github.com:trunganhxxiiidev/be-fast-api-training-trainee.git
```

Repo course gốc trong README là nguồn bài học, không phải nơi push bài trainee.

GitHub Actions `pages build and deployment` trong repo course gốc là GitHub Pages workflow tự động, không phải CI của trainee repo.

