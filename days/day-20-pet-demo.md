# Day 20 — Pet Project: Deploy & Demo

> **Week 4 · Day 20** · ~6 hours · [← Week overview](../week-4-pet-project.md) · **Final examination**

## Objective

Ship the pet project to AWS, demo it live to the mentor, sit a 30-minute Q&A, and finish the internship having shown — not just claimed — that the curriculum landed.

## Why this matters

Today is the only day where what you *did* gets compared with what the curriculum *asked you to do*. Be honest about both. The mentor isn't grading a flawless project — they're grading whether you understand what you built and what you'd do differently.

## Morning — Deploy (3 hours)

This is the same flow as [Day 15](./day-15-terraform-ec2.md), now applied to the pet project repo.

1. **Push the image** to your registry.
   ```bash
   docker build -t youruser/intern-pet:1.0.0 .
   docker push youruser/intern-pet:1.0.0
   ```
   Use a real semver tag, not `latest`. The mentor will want to reproduce.

2. **Fill in `terraform.tfvars`** for the pet project.
   - `image_uri = "docker.io/youruser/intern-pet:1.0.0"`
   - `allowed_ssh_cidr = "$(curl -s ifconfig.me)/32"`
   - `key_name = "<your EC2 key pair>"`

3. **`terraform init && terraform plan && terraform apply`**. Watch the output. Capture the `api_url`.

4. **Smoke test** the deployed service with `curl`:
   - `GET /health` → 200
   - `POST /auth/register` with a real-looking body → 201
   - `POST /auth/login` → 200 with a token
   - One request that exercises the main feature
   - One request that exercises the authorization rule (expect 403 with the wrong user)
   - One deliberate bad request (expect 422 with the error envelope)

5. **SSH in and verify**
   - `docker ps` shows api + pg containers running.
   - `docker logs --tail 50 api` shows structured logs with correlation IDs.
   - `docker logs --tail 5 pg` shows Postgres healthy.

6. **Confirm CI green on `main`**. The mentor will look.

## Demo (60 min slot, 20 min talking)

Structure your demo. Don't wing it.

**0:00–5:00 — Problem & design**
- One slide / one paragraph: "I built X. Here's why, and what I chose not to build."
- Show the architecture diagram from your README.
- Call out one specific tradeoff you made and why.

**5:00–15:00 — Live walkthrough**
- Walk through the deployed service with `curl` or Postman.
- Hit the main happy path.
- Trigger an error. Show the structured log line with the correlation ID. Find the same correlation ID in the response header.
- Show one query in the DB via `psql` over SSH (or via a query endpoint), demonstrating the data shape.
- Show one cache hit/miss timing if you wired caching.

**15:00–20:00 — Retro**
- What you're proudest of (be specific — not "the auth flow" but "the dependency-based authz rule that lives in one place").
- What you'd do differently with another week.
- One thing the curriculum could improve.

## Q&A (30 min)

Topics the mentor may ask across the program — be ready for any of these:

**Foundations**
- Why is `await asyncio.sleep(5)` different from `time.sleep(5)` in an async handler?
- What's the difference between 401 and 403? When do you use each in your project?

**FastAPI & Pydantic**
- Walk through a `Depends` chain in your code.
- Why are `UserCreate` and `UserOut` different classes?

**Database**
- Walk through one query in your code and the SQL it generates.
- How does your schema handle deletes? Cascade or restrict?
- Show one query you'd want an index on, and explain why.

**Auth**
- Walk through what happens when a JWT expires.
- Could the JWT secret leak? What would the blast radius be?

**Testing**
- How are your tests isolated?
- What's not tested, and why?

**Ops**
- Walk through the deploy: from `git push` to a public URL.
- What's missing for a real production deploy? List five things.

**Observability**
- Show me a log line. Walk me through every field.
- How would you debug a 500 from a real user report?

## Wrap-up tasks

- [ ] **`terraform destroy`** — *before* you leave. Confirm the EC2 instance and SG are gone in the AWS console.
- [ ] Mark the PR as merged. Tag the final commit: `git tag -a v1.0.0 -m "internship final submission" && git push --tags`.
- [ ] Move the AWS billing alarm to $1 (or keep it). Don't delete the account today — the mentor may want to redeploy to verify.
- [ ] Submit the one-paragraph reflection to the mentor (see [pet-project-spec.md](../pet-project-spec.md#submission)).
- [ ] Write your own retro in `journal/day-20.md` — what you'd tell your Day 1 self.

## Self-check (before the demo starts)

1. Can you `terraform apply` from a clean machine in under 10 minutes following only your `DEPLOY.md`?
2. Can you reproduce the most interesting bug you fixed during the program, on demand?
3. Can you point to exactly one line of code you're proudest of and exactly one you'd refactor?
4. If the mentor asks you to add a 9th endpoint live, how long would it take you?
5. Did you actually run `terraform destroy` yet?
6. What's one thing you learned that wasn't in the curriculum?

## Common pitfalls (on demo day specifically)

- **Demo runs out of free-tier budget mid-presentation** — verify last night that the budget alert hasn't fired and that the instance is up.
- **Live deploy from scratch during demo** — fast Wi-Fi, slow apt cache, mysterious AWS failure. Deploy *before* the demo and verify; have the URL warm.
- **Pretending an unfinished feature is done** — easier to say "I didn't get to it; here's where I'd put it" than to be caught later.
- **Reading code line by line** — the worst kind of demo. Talk about *why*, not *what*.
- **Forgetting to `terraform destroy`** — the bill comes home regardless.
- **No `journal/day-20.md` retro** — the curriculum can't improve without it. Write it.

## Definition of done — the whole internship

- [ ] Pet project deployed and reachable at a public URL.
- [ ] Code in a public GitHub repo, tagged `v1.0.0`.
- [ ] `docker compose up` works on a fresh clone.
- [ ] CI green on `main`.
- [ ] All 13 [required capabilities](../pet-project-spec.md#required-capabilities) demonstrably met.
- [ ] Demo and Q&A complete.
- [ ] `terraform destroy` executed; AWS console clean.
- [ ] Final reflection submitted.
- [ ] Mentor recommendation in hand.

That's it. Whatever the grade, you wrote, deployed, and defended a real backend service from scratch in four weeks. Go celebrate.
