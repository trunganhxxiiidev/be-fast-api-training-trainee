# Day 2 — Python Refresher

> **Week 1 · Day 2** · ~6 hours · [← Week overview](../week-1-fundamentals.md)

## Objective

Get fluent enough with modern Python (3.12+) that the language stays out of your way for the rest of the program. You should be comfortable with type hints, virtual environments, the most-used standard library modules, and writing a small set of pytest tests.

## Why this matters

Python is your primary tool for the next four weeks. Every day you'll be reading and writing Python code that depends on confident use of types, packages, and the standard library. Spending today on fluency pays back compounding interest tomorrow.

## Concepts

**Project management with `uv`**

`uv` is a modern Python project tool from Astral (same makers as `ruff`). It replaces `pip`, `virtualenv`, and `pip-tools` with one fast binary.

```bash
uv init my-project        # scaffolds pyproject.toml, README, src/
cd my-project
uv add fastapi pydantic   # adds deps to pyproject.toml + uv.lock
uv add --dev pytest ruff  # dev deps
uv run pytest             # runs in the project's virtualenv
uv sync                   # restore env from lockfile (use this on a fresh clone)
```

Alternatives: `poetry`, `pdm`, or plain `venv` + `pip`. We use `uv` because it's the fastest and least painful. **Pick one and use it for the whole program** — don't mix.

**Type hints (modern style)**
- Basic: `def add(a: int, b: int) -> int:`.
- Union with `|` (PEP 604): `def find(name: str) -> User | None:` — preferred over `Optional[User]`.
- Built-in generics (PEP 585): `list[int]`, `dict[str, int]` — no more `from typing import List, Dict`.
- `TypedDict` for dict shapes, `Protocol` for structural typing, `Annotated` for adding metadata.
- Use `from __future__ import annotations` at the top of files if you want forward references to "just work" without quoting.

**Dataclasses**
- `@dataclass(frozen=True, slots=True)` for value objects.
- `field(default_factory=list)` — never use mutable defaults directly.
- Modern alternative: Pydantic models (you'll meet these on Day 4).

**Standard library you'll actually use**
- `pathlib.Path` instead of `os.path` — much cleaner: `Path("a") / "b" / "c.txt"`.
- `json` for serialization, `datetime` for time (use `datetime.now(tz=UTC)` — naive datetimes will bite you).
- `enum.StrEnum` (3.11+) — `class Role(StrEnum): ADMIN = "admin"; MEMBER = "member"`.
- `logging` — never `print()` in real code.
- `decimal.Decimal` for money — never `float`.

**Testing with pytest**
- File names: `test_*.py`. Function names: `def test_*():`. Convention.
- `assert x == y` — pytest gives you rich diff output for free.
- Fixtures: `@pytest.fixture` for shared setup. Function-scoped by default; use `scope="module"` or `"session"` for expensive setup.
- Parametrize: `@pytest.mark.parametrize("a,b,expected", [(1, 2, 3), (0, 0, 0)])` runs one test function with multiple inputs.
- Useful flags: `-v` (verbose), `-x` (stop on first failure), `-k "name"` (filter by name).

**Linting and formatting**
- `ruff check .` — fast linter (replaces flake8 + pylint + isort).
- `ruff format .` — formatter (replaces black; they're now essentially the same).
- Configure in `pyproject.toml` under `[tool.ruff]`.
- Add a `pre-commit` hook so this runs before every commit.

## Required reading

1. **`uv` docs — Getting started** — https://docs.astral.sh/uv/getting-started/ — read end to end (~15 min).
2. **PEP 8** — https://peps.python.org/pep-0008/ — skim once. Knowing the rules makes `ruff` decisions less surprising.
3. **mypy cheat sheet** — https://mypy.readthedocs.io/en/stable/cheat_sheet_py3.html — use as reference, don't memorize.
4. **pytest — Get Started** — https://docs.pytest.org/en/stable/getting-started.html — 10 min.

## Optional reading

- **Real Python: Modern Python Features** — https://realpython.com/python312-new-features/ — what's actually new in 3.12.
- **`ruff` rules reference** — https://docs.astral.sh/ruff/rules/ — search when a rule flags something you don't recognize.

## Exercises

1. **`wordcount.py`** — a small CLI:
   - Accepts `--file PATH` (required) and `--top N` (default 10).
   - Counts word occurrences (case-insensitive, strip punctuation).
   - Prints the top N words and their counts.
   - Full type hints. Uses `argparse` and `pathlib.Path`.
2. **Tests** — write at least 5 pytest tests covering:
   - Happy path (a small fixture file).
   - Empty file returns nothing.
   - Missing file raises `FileNotFoundError` (or your custom error) cleanly.
   - Unicode content (e.g. "café" appearing 3 times).
   - The `--top` flag respects its argument.
3. **Tooling** — set up `ruff` and pre-commit:
   - Add `[tool.ruff]` config in `pyproject.toml`.
   - Install `pre-commit`, create `.pre-commit-config.yaml`, register `ruff` and `ruff-format` hooks.
   - Run `pre-commit run --all-files` and fix anything it flags.

## Common pitfalls

- **Mutable default arguments**: `def f(items: list = []):` — the same list is reused across calls. Use `items: list | None = None` and set inside.
- **Forgetting to activate the venv** — symptoms: `command not found: pytest`. With `uv run pytest` this goes away.
- **`datetime.now()` without a timezone** — produces naive datetimes that compare incorrectly with aware ones. Always pass `tz=`.
- **Catching `Exception` broadly** — hides real bugs. Catch the specific exception you expect.
- **`print()` debugging that ships to production** — use `logging` from day one.

## Self-check

1. What's the difference between `list` and `list[int]` in a type hint?
2. Why is `def f(x=[]):` dangerous?
3. When would you use a `Protocol` instead of an abstract base class?
4. What does `@pytest.fixture(scope="session")` change?
5. Why is `from __future__ import annotations` useful?
6. Show two ways to skip a test, and explain when each is appropriate.

## Definition of done

- [ ] `wordcount.py` committed with full type hints.
- [ ] 5+ pytest tests pass with `uv run pytest -v`.
- [ ] `ruff check .` returns zero issues.
- [ ] `pre-commit run --all-files` passes.
- [ ] PR opened and reviewed.
