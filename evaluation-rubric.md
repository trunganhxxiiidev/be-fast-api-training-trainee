# Evaluation Rubric

How the mentor scores the program at the end of week 4. Shared with the intern on day 1 — no surprises.

The rubric is **not** about whether every feature is shipped. It's about whether the intern can think like a backend engineer.

---

## Scoring Bands

| Band | What it means |
|------|---------------|
| **Exceeds** | Independent, makes good tradeoff calls without being prompted, code is one I'd merge with light review. |
| **Meets** | Did the work, understood it, needed reasonable amount of guidance. Ready for a junior IC role. |
| **Approaches** | Got it done with heavy guidance; some concepts haven't clicked yet. Worth a second iteration. |
| **Not yet** | Significant gaps. Honest conversation about whether this path is the right fit. |

---

## Categories

### 1. Code Quality (25%)

- Naming: do variables and functions tell you what they are?
- Structure: is the project laid out sensibly? Can I find the auth code without grep?
- No dead code, no commented-out blocks, no `TODO: fix later` from week 1.
- Errors handled, not swallowed.
- Comments where the *why* is non-obvious, never the *what*.

### 2. Engineering Judgment (25%)

- Can the intern explain *why* they chose this DB schema over alternatives?
- Did they push back on parts of the spec that didn't make sense?
- Did they pick a stretch goal that actually deepened understanding (vs. adding surface area)?
- When they got stuck, did they debug it methodically or thrash?

### 3. Testing & Verification (15%)

- Tests run, pass, and cover the meaningful paths.
- Tests are readable — I can tell what's being verified without reading the implementation.
- They caught at least one bug *because* of a test (and they noticed).

### 4. Tooling & Process (15%)

- Git history is clean: branches, focused commits, clear messages.
- CI is green on `main`.
- README lets me run the project in under 5 minutes from a fresh clone.
- `docker compose up` works.

### 5. Communication (20%)

- Standups: clear, honest, no padding.
- Journal entries: actually written, show learning over the month.
- Demo: organized, honest about gaps, can answer questions without panicking.
- PR descriptions: useful — they tell me what changed and why.

---

## Pass/Fail Knockouts

Some things are non-negotiable regardless of total score:

- **Pet project must run.** A non-running project from a graduating intern is the one outcome we can't ship around.
- **No plagiarized code.** AI-generated code is fine *only* if the intern can fully explain and defend it line by line on demand.
- **No catastrophic security mistakes shipped.** Plaintext passwords stored, secrets in git history, SQL injection — these are show-stoppers. We catch them in review or revert.

---

## End-of-Program Conversation

The final conversation is 60 minutes:

- 20 min: Demo (intern drives).
- 20 min: Live Q&A — mentor asks technical questions across the curriculum.
- 10 min: Intern's retro — what worked, what didn't, what they wish they'd done differently.
- 10 min: Mentor's feedback — strengths, growth areas, suggested next steps.

The goal of the conversation is not a verdict — it's a useful next-step recommendation. Pass/fail is a side effect.
