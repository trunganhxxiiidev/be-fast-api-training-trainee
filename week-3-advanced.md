# Week 3 — Production-Adjacent Concerns

**Goal:** Move from "it works on my laptop" to "it's testable, observable, and deployable." Everything this week is about making code survive contact with reality.

> **Detailed daily lessons** with required reading, exercises, pitfalls, and self-check:
> - [Day 11 — Automated Testing](./days/day-11-testing.md)
> - [Day 12 — Logging, Errors & Observability](./days/day-12-logging.md)
> - [Day 13 — Docker & docker compose](./days/day-13-docker.md)
> - [Day 14 — Caching & Async Work](./days/day-14-caching.md)
> - [Day 15 — Deploying with Terraform + AWS EC2 (deliverable)](./days/day-15-terraform-ec2.md)

This page is the **week-at-a-glance**. Click into each day for the full lesson.

---

## Day 11 — Automated Testing

**Topics**
- Test pyramid: unit, integration, end-to-end — when to use which.
- Test doubles: stubs, mocks, fakes — and why mocks become a smell when overused.
- Database tests: throwaway database per test run vs. transactional rollback.
- Coverage as a guide, not a target. 100% coverage is suspicious.

**Exercises**
1. Add unit tests for service-layer logic in the week-2 API. Aim for ~80% coverage on `app/services`.
2. Add integration tests that hit a real PostgreSQL test database.
3. Write one end-to-end test that registers, logs in, creates a post, and reads it back.
4. Set up `pytest-cov` and review the uncovered lines — are they worth testing or genuinely uninteresting?

**Reading**
- ["The Practical Test Pyramid" — Ham Vocke](https://martinfowler.com/articles/practical-test-pyramid.html)

---

## Day 12 — Logging, Errors, Observability

**Topics**
- Structured logging (JSON) vs. printf. Why grepping prod logs only works at small scale.
- Log levels — what actually belongs at DEBUG vs INFO vs WARNING vs ERROR.
- Correlation IDs: tying logs from one request together across services.
- Sentry/error tracking — what gets reported and what gets swallowed.
- Metrics vs. logs vs. traces — the three pillars.

**Exercises**
1. Replace any `print()` calls with `structlog` configured for JSON output.
2. Add a middleware that generates a request ID and includes it in every log line for that request.
3. Make sure exceptions get logged with their stack trace, not just the message.
4. Sketch the metrics you'd add if this were a production service: which counters/gauges/histograms and why?

---

## Day 13 — Docker & docker compose

**Topics**
- Image vs. container. Layers and the build cache.
- Multi-stage builds — why your prod image shouldn't ship `node_modules` with dev deps.
- `docker compose` for local stacks: app + postgres + redis.
- Volumes, networks, environment variables, secrets (and what *not* to bake into images).

**Exercises**
1. Write a `Dockerfile` for the Python API. Multi-stage. Final image under 200MB.
2. Write a `docker-compose.yml` that spins up: API, Postgres, Redis. Health checks on all services.
3. Bring it up with `docker compose up -d` and run the integration tests against it.
4. Read up on `.dockerignore` and apply it (do you really want `node_modules` in the build context?).

---

## Day 14 — Caching & Async Work

**Topics**
- When caching helps (read-heavy, slow-to-compute) and when it bites (stale data, cache stampedes).
- Redis as a cache: TTL, eviction policies, key naming.
- Cache invalidation strategies: write-through, write-behind, TTL-only, manual bust.
- Background jobs: `celery` (broker = Redis) — and when a simple cron is enough.

**Exercises**
1. Add a Redis-backed cache for `GET /posts/{id}`. Invalidate on update.
2. Measure the difference: hit `GET /posts/1` 100 times with and without the cache.
3. Add a background job that recomputes a "popular posts" list every 5 minutes.
4. Discuss: what could go wrong with this cache? List 3 failure modes.

---

## Day 15 — Deploying to AWS EC2 with Terraform

**Goal:** Provision a real Linux server in the cloud with Terraform, deploy the Docker stack to it, and access it from the public internet. Free-tier only — no surprise bills.

**Topics**
- 12-factor app principles — at least skim the list and pick three to apply.
- Health checks, readiness vs. liveness.
- Environment-based config (`.env` files for local, env vars + AWS Parameter Store for prod).
- CI basics: lint + test on every PR with GitHub Actions.
- **Infrastructure as Code with Terraform**
  - Providers, resources, variables, outputs, state files.
  - `terraform init` → `plan` → `apply` → `destroy` — the four commands you'll run all day.
  - Why state matters (and why you'd eventually move it to S3 with locking).
- **AWS free-tier essentials**
  - IAM user with programmatic access (never the root account).
  - EC2 `t2.micro` or `t3.micro` — the only free-tier instance types.
  - Security groups: open SSH (22) from your IP only, open HTTP (80) to the world.
  - Key pairs for SSH access.
  - AMIs — pick the latest Amazon Linux 2023 or Ubuntu 22.04 LTS.
- **Deploying via Docker on EC2**
  - `user_data` script to install Docker + docker-compose on first boot.
  - Pulling the image from a registry (Docker Hub or GitHub Container Registry).
  - `docker compose up -d` to run the stack on the instance.

**Pre-flight (do this before Day 15)**
- Create an AWS account. Set a billing alarm at $1. Treat anything outside free tier as a fire alarm.
- Install AWS CLI and `terraform` locally.
- Create an IAM user named `intern-deploy` with the minimum policies for EC2 + VPC. Save the access keys to `~/.aws/credentials` under a named profile, **never** in the repo.

**Exercises**
1. Add a GitHub Actions workflow that runs `ruff`, `pytest`, and `docker build` on every push.
2. Add a `/health` (always-200) and `/ready` (DB-checked) endpoint to the API.
3. Write a `terraform/` directory in your project:
   ```
   terraform/
   ├── main.tf          ← provider + EC2 instance + security group + key pair
   ├── variables.tf     ← region, instance_type, allowed_ssh_cidr, key_name
   ├── outputs.tf       ← public_ip, ssh_command
   ├── user_data.sh     ← installs Docker, pulls image, runs docker compose
   └── terraform.tfvars.example
   ```
4. Run `terraform init && terraform plan && terraform apply`. SSH in. Verify the container is running. Curl the public IP from your laptop.
5. Document everything in `DEPLOY.md` — including the **mandatory** `terraform destroy` step when you're done for the day.

**Reference `main.tf` skeleton (intern fills in the gaps)**
```hcl
terraform {
  required_providers {
    aws = { source = "hashicorp/aws", version = "~> 5.0" }
  }
}

provider "aws" {
  region  = var.region
  profile = "intern-deploy"
}

resource "aws_security_group" "api" {
  name        = "intern-api-sg"
  description = "API server SG"
  # TODO: ingress for 22 (your IP only) and 80 (0.0.0.0/0)
  # TODO: egress all
}

resource "aws_instance" "api" {
  ami                    = var.ami_id            # TODO: pick a free-tier AMI
  instance_type          = "t3.micro"            # free tier eligible
  key_name               = var.key_name
  vpc_security_group_ids = [aws_security_group.api.id]
  user_data              = file("${path.module}/user_data.sh")

  tags = { Name = "intern-api", Owner = "nathan-intern" }
}

output "public_ip"  { value = aws_instance.api.public_ip }
output "ssh_command" {
  value = "ssh -i ~/.ssh/${var.key_name}.pem ec2-user@${aws_instance.api.public_ip}"
}
```

**Cost & safety**
- `terraform destroy` at end of every working day. The free tier gives 750 hours/month of `t2.micro`/`t3.micro`, but a forgotten Elastic IP or EBS volume *will* bill you.
- Never commit `.tfstate`, `*.tfvars` (with secrets), or PEM keys. Add them to `.gitignore` on day one.
- The billing alarm is your safety net. Trust it; check it weekly.

**Weekly review focus**
- Live demo: `terraform apply` from a clean slate to a public URL.
- Walk through `main.tf` and explain each resource.
- Show CI green on a real PR.
- What's missing before this is "production-ready"? (HTTPS, persistent EBS for Postgres, load balancer, managed RDS, secrets out of `.tfvars`...)
