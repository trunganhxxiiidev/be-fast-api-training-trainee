# Day 1 — Environment, Shell & Git

> **Week 1 · Day 1** · ~5 hours · [← Week overview](../week-1-fundamentals.md)

## Objective

Set up a working Python development environment, learn the shell tools you'll use daily, and develop a working mental model of Git that's deeper than memorized commands.

## Why this matters

Every hour you save by being fluent with Git and the shell is an hour you spend on real engineering. Conversely, every hour you spend fighting your environment, mis-merging branches, or grepping for the right command is dead weight. Backend engineers live in the terminal — there is no escaping it.

## Concepts

**Shell fundamentals**
- File navigation: `cd`, `ls -lah`, `pwd`, `tree`.
- Text manipulation: `grep -rni`, `find . -name`, `sed`, `awk` (basic only), `head`, `tail`, `wc`, `cut`, `sort -u`.
- Process inspection: `ps`, `kill`, `lsof -i :8000` (find what's using a port).
- Redirection and pipes: `>`, `>>`, `2>&1`, `|`, `xargs`.

**Editor**
- VS Code + the Python, Pylance, Ruff, and Even Better TOML extensions.
- Learn the command palette (`Cmd+Shift+P`) and basic key bindings — multi-cursor, go-to-definition, find-in-files.

**Git mental model — what a senior dev expects you to know**
- A commit is a *snapshot*, not a diff. Branches are *pointers* to commits.
- The three areas: working tree (your files), index (the staging area), and `HEAD` (the last commit on the current branch).
- `git status` is your eyes. Run it constantly. It tells you exactly which area is in which state.
- `git log --oneline --graph --all` shows you the topology — get used to reading it.
- `merge` preserves history (creates a merge commit). `rebase` rewrites history (linear). Use `rebase` to clean up *your own* feature branches before review, `merge` to integrate into shared branches.

**Branching workflow on this team**
- `main` is protected. Direct pushes are disabled.
- Create `feature/<short-description>` branches from up-to-date `main`.
- Open a PR. Keep it small. Get one approval. Merge with squash-merge.
- Commit messages follow [Conventional Commits](https://www.conventionalcommits.org/): `feat:`, `fix:`, `refactor:`, `docs:`, `chore:`, `test:`.

## Required reading

1. **Pro Git, Ch. 1–3** — https://git-scm.com/book/en/v2 — skim Ch. 1 (concepts), read Ch. 2 (basics), read Ch. 3 (branching) carefully.
2. **Atlassian: Merging vs. Rebasing** — https://www.atlassian.com/git/tutorials/merging-vs-rebasing — short and clear.
3. **Conventional Commits spec** — https://www.conventionalcommits.org/en/v1.0.0/ — 5-minute read.

## Optional reading

- **The Missing Semester (MIT)** — https://missing.csail.mit.edu/2020/shell-tools/ — the closest thing to a shell crash course you'll find.
- **Oh My Zsh** — https://ohmyz.sh — if you're on zsh and want a nicer prompt; not required.

## Exercises

1. **Environment**
   - Install `pyenv` and use it to install Python 3.12: `pyenv install 3.12 && pyenv global 3.12`.
   - Install `uv` (fast Python package manager): `curl -LsSf https://astral.sh/uv/install.sh | sh`.
   - Verify: `python --version`, `uv --version`.
2. **Shell drills** — answer these by running commands, then write the command you used in `journal/day-01.md`:
   - How many `.py` files are in your home directory tree?
   - What process is using port 8000 (if any)?
   - Show the last 20 lines of any log file on your system.
3. **Git PR flow**
   - Create a `feature/<your-name>-setup` branch.
   - Add `journal/day-01.md` with your environment details, shell-drill answers, and a 3-sentence explanation of merge vs. rebase in your own words.
   - Commit with a Conventional Commit message.
   - Open a PR. Tag the mentor for review.

## Common pitfalls

- **Forgetting to pull `main` before branching** → causes painful rebases later. Always `git checkout main && git pull && git checkout -b feature/...`.
- **Committing virtualenvs, `__pycache__`, `.env` files** → add them to `.gitignore` on day one.
- **Writing "fix" or "update" as a commit message** → useless six months from now. Be specific.
- **Pushing with `--force` on shared branches** → never do this without explicit approval. On *your own* feature branch, `--force-with-lease` is safer than `--force`.
- **Running random scripts from the internet without reading them** — `curl ... | sh` is convenient but be sure you trust the source.

## Self-check (you should be able to answer all of these)

1. What's the difference between `git fetch` and `git pull`?
2. You're on a feature branch and want to incorporate the latest `main` changes. Do you `merge` or `rebase`? Why?
3. You accidentally committed to `main` locally. How do you move that commit onto a new branch and reset `main`?
4. What does `git stash` do? When is it useful?
5. What's the difference between `~/.gitignore` and a repo's `.gitignore`?
6. How do you find which line of which file introduced a specific string?

## Definition of done

- [ ] PR opened with `journal/day-01.md`.
- [ ] Commit message follows Conventional Commits.
- [ ] `python --version` shows 3.12.x.
- [ ] `uv --version` succeeds.
- [ ] You can answer the self-check questions out loud.
