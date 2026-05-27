# Day 15 — Deploying with Terraform + AWS EC2 (Free Tier)

> **Week 3 · Day 15** · ~8 hours · [← Week overview](../week-3-advanced.md) · **Friday deliverable**

## Objective

Provision a real Linux server in AWS using Terraform, deploy the Dockerized FastAPI stack to it, and hit it from the public internet. Stay entirely within the free tier. Be able to `terraform destroy` and rebuild from scratch.

## Why this matters

There's a giant gap between "I built an API" and "people on the internet can use it." Closing that gap means: provisioning compute, configuring networking, securing the surface, and shipping the artifact onto the host. Terraform makes all of this *code* — version-controlled, reviewable, reproducible. Doing it once by hand is a rite of passage; doing it with Terraform is what the job actually looks like.

⚠ **Read the [Cost & safety](#cost--safety) section before running any command. AWS will bill you if you leave things running.**

## Concepts

**Terraform — the model**

You write `.tf` files describing the *desired state* of your infrastructure. Terraform reads them, compares against the current state (stored in a state file), and figures out the plan to converge.

```
terraform init       # download provider, set up backend
terraform plan       # show what would change
terraform apply      # apply changes (you'll be prompted to confirm)
terraform destroy    # tear it all down
```

**State**

`terraform.tfstate` is the source of truth for what Terraform thinks exists. Local state is fine for solo learning. In a team, you move it to a remote backend (S3 + DynamoDB lock) so multiple people can't apply simultaneously and corrupt each other's state. We'll keep state local for the internship.

**AWS account setup (the parts you can't skip)**

1. **Create an AWS account.** Use a real email; you can close it cleanly later if needed.
2. **Set a billing alarm at $1.** Console → Billing → Budgets. This is non-optional. Anything above free tier triggers it.
3. **Never use the root account for daily work.** Create an IAM user.
4. **IAM user setup**
   - Console → IAM → Users → Add user
   - Name: `intern-deploy`
   - Attach policies: `AmazonEC2FullAccess` + `IAMReadOnlyAccess` (and add more later only as needed)
   - Create access keys → save them to `~/.aws/credentials` under a named profile:
     ```ini
     [intern-deploy]
     aws_access_key_id = ...
     aws_secret_access_key = ...
     ```
5. **Install AWS CLI** (`brew install awscli`) and Terraform (`brew install terraform`). Verify:
   ```bash
   aws --profile intern-deploy sts get-caller-identity
   terraform version
   ```

**Free tier — what's actually free**

For the first 12 months of a new account:
- **750 hours/month** of `t2.micro` *or* `t3.micro` (one running 24/7 fits).
- **30 GB** of EBS storage (the volume attached to your EC2).
- Some data transfer (read the page below).

Things that aren't free and will surprise you:
- Elastic IPs that are *not* attached to a running instance ($0.005/hour ≈ $3.65/month — annoying small bills).
- NAT gateways (~$32/month — don't add one).
- Application Load Balancers (~$16/month — skip for now; access via public IP).
- Anything in regions other than the one you created the alarm in.

> **AWS Free Tier overview:** https://aws.amazon.com/free/

**The Terraform layout we'll use**

```
terraform/
├── main.tf            ← provider + EC2 + security group
├── variables.tf       ← inputs (region, instance_type, etc.)
├── outputs.tf         ← public_ip, ssh_command
├── user_data.sh       ← runs on first boot: install Docker, run the app
├── terraform.tfvars   ← actual values (gitignored)
└── terraform.tfvars.example
```

**`variables.tf`**
```hcl
variable "region"          { type = string; default = "us-east-1" }
variable "instance_type"   { type = string; default = "t3.micro" }
variable "key_name"        { type = string; description = "Name of the EC2 key pair you uploaded" }
variable "allowed_ssh_cidr" { type = string; description = "Your IP/32 — get from https://ifconfig.me" }
variable "image_uri"       { type = string; description = "Docker image to run, e.g. docker.io/youruser/app:latest" }
```

**`main.tf`**
```hcl
terraform {
  required_version = ">= 1.5"
  required_providers {
    aws = { source = "hashicorp/aws", version = "~> 5.0" }
  }
}

provider "aws" {
  region  = var.region
  profile = "intern-deploy"
}

# Latest Amazon Linux 2023 AMI for x86_64
data "aws_ami" "al2023" {
  most_recent = true
  owners      = ["amazon"]
  filter {
    name   = "name"
    values = ["al2023-ami-*-x86_64"]
  }
}

resource "aws_security_group" "api" {
  name        = "intern-api-sg"
  description = "Allow SSH from my IP, HTTP from world"

  ingress {
    description = "SSH from me"
    from_port   = 22
    to_port     = 22
    protocol    = "tcp"
    cidr_blocks = [var.allowed_ssh_cidr]
  }
  ingress {
    description = "HTTP"
    from_port   = 80
    to_port     = 80
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }
  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }
}

resource "aws_instance" "api" {
  ami                    = data.aws_ami.al2023.id
  instance_type          = var.instance_type
  key_name               = var.key_name
  vpc_security_group_ids = [aws_security_group.api.id]
  user_data              = templatefile("${path.module}/user_data.sh", { image_uri = var.image_uri })

  tags = {
    Name  = "intern-api"
    Owner = "nathan-intern"
  }
}
```

**`user_data.sh`** (runs once on first boot, as root)
```bash
#!/bin/bash
set -eux

dnf update -y
dnf install -y docker
systemctl enable --now docker

# Run the API on port 80 so we don't need a load balancer.
# Postgres runs on the same box for the internship; production would use RDS.
docker run -d \
  --name pg \
  --restart unless-stopped \
  -e POSTGRES_PASSWORD=apppass \
  -e POSTGRES_DB=app \
  -v pg_data:/var/lib/postgresql/data \
  postgres:16

# Wait for Postgres to accept connections.
until docker exec pg pg_isready -U postgres; do sleep 1; done

docker run -d \
  --name api \
  --restart unless-stopped \
  --link pg:db \
  -e DATABASE_URL=postgresql+asyncpg://postgres:apppass@db:5432/app \
  -e JWT_SECRET="$(openssl rand -hex 32)" \
  -p 80:8000 \
  ${image_uri}
```

**`outputs.tf`**
```hcl
output "public_ip"  { value = aws_instance.api.public_ip }
output "ssh_command" {
  value = "ssh -i ~/.ssh/${var.key_name}.pem ec2-user@${aws_instance.api.public_ip}"
}
output "api_url" { value = "http://${aws_instance.api.public_ip}" }
```

**The pre-flight checklist before `terraform apply`**

1. Push your Docker image to a registry the EC2 can pull from. Docker Hub free account is easy:
   ```bash
   docker tag intern-api:dev youruser/intern-api:latest
   docker push youruser/intern-api:latest
   ```
2. Create an EC2 key pair (Console → EC2 → Key Pairs → Create). Download the `.pem`. `chmod 400 ~/.ssh/whatever.pem`.
3. Get your IP: `curl ifconfig.me`. Use `1.2.3.4/32` as `allowed_ssh_cidr`.
4. Fill in `terraform.tfvars` with these values. Confirm it's gitignored.
5. `terraform init && terraform plan` — read the plan. There should be ~3 resources to create.
6. `terraform apply` — type `yes`.

**Cost & safety**

- **Always run `terraform destroy` at the end of every working day.** The free tier doesn't protect against forgetfulness — leaving things running 24/7 burns the 750 hours, and then you're billed.
- Check the AWS Billing dashboard daily. The dollar amount, not "free tier usage."
- Never commit: `*.tfvars` (your IP, image names), `*.pem` files, `.aws/credentials`, `.terraform/`, `terraform.tfstate*`.
  `.gitignore`:
  ```
  *.tfvars
  *.tfvars.json
  *.pem
  .terraform/
  terraform.tfstate
  terraform.tfstate.*
  .terraform.lock.hcl
  ```
  (`.terraform.lock.hcl` is sometimes committed in real projects — for solo work it's fine to ignore.)

## Required reading

1. **Terraform: AWS Get Started tutorial** — https://developer.hashicorp.com/terraform/tutorials/aws-get-started — do the entire tutorial path. Plan for ~30 min.
2. **Terraform AWS Provider docs** — https://registry.terraform.io/providers/hashicorp/aws/latest/docs — bookmark; you'll search it constantly.
3. **AWS Free Tier overview** — https://aws.amazon.com/free/ — read what's covered and the time limits.
4. **AWS IAM best practices** — https://docs.aws.amazon.com/IAM/latest/UserGuide/best-practices.html — sections 1–4 minimum.

## Optional reading

- **terraform-aws-modules** — https://github.com/terraform-aws-modules — for when you start using community modules instead of writing everything from scratch.
- **Spacelift: Terraform best practices** — https://spacelift.io/blog/terraform-best-practices
- **AWS: EC2 user data** — https://docs.aws.amazon.com/AWSEC2/latest/UserGuide/user-data.html

## Exercises

1. **Account setup** (do this before lunch):
   - AWS account created, MFA on root account.
   - Billing alarm at $1 configured.
   - IAM user `intern-deploy` created with access keys.
   - AWS CLI + Terraform installed and `sts get-caller-identity` succeeds.

2. **CI workflow** — add `.github/workflows/ci.yml` to your repo running `ruff check`, `pytest`, and `docker build` on every push. Document the badge in your README.

3. **Push the image** — to Docker Hub or GitHub Container Registry. Make it public for simplicity; secured registries are a Week 4 stretch goal.

4. **Terraform** — write all four files (`main.tf`, `variables.tf`, `outputs.tf`, `user_data.sh`). `terraform init && plan && apply`. Capture the output URL.

5. **Verify**
   - `curl http://<public-ip>/health` returns `{"status":"ok"}`.
   - `curl -X POST http://<public-ip>/auth/register -d '{...}'` works end-to-end.
   - SSH in (`terraform output ssh_command`). Run `docker ps` to see both containers running.

6. **`/ready` endpoint** — if you haven't already, add an endpoint that returns 503 if the DB is unreachable. Verify it during deployment.

7. **DEPLOY.md** — write a one-page deploy guide covering: prerequisites, env setup, the four Terraform commands, how to verify, and how to tear down. The mentor will follow this from scratch on Monday.

8. **`terraform destroy`** — actually destroy at end of day. Verify the EC2 instance shows "terminated" in the console. Check the security group is gone too.

## Common pitfalls

- **Leaving the instance running over the weekend** — burns free-tier hours. Destroy.
- **Forgetting to attach the IAM policy correctly** — `terraform apply` fails with `UnauthorizedOperation`. Read the error and add the missing permission to your IAM user.
- **Security group too open** — `0.0.0.0/0` on port 22 is a fast way to get scanned and brute-forced. Lock SSH to your IP.
- **Hardcoded passwords in `user_data.sh`** — visible in the EC2 instance metadata. For real deploys, use AWS Secrets Manager or Parameter Store.
- **No `--restart unless-stopped` on Docker containers** — if the EC2 reboots, your app doesn't come back.
- **Committing `.pem` files or `*.tfvars`** — credentials in git history are credentials leaked, period. Even a force-push doesn't help if anyone cloned in between.
- **Using `terraform destroy -auto-approve` when you don't mean to** — and finding out you destroyed prod.

## Self-check

1. What does `terraform plan` show you that `terraform apply` doesn't?
2. Your `aws_instance` resource's `ami` field is set to a hardcoded AMI ID. What's wrong with that, and how does the `data "aws_ami" "al2023"` block fix it?
3. You apply, then change `instance_type` from `t3.micro` to `t3.small` and apply again. What does Terraform do? Why might that matter?
4. Where is the database persisted? What happens when you `terraform destroy`?
5. Your `terraform.tfstate` was accidentally committed. What do you do?
6. What's the next infrastructure step you'd take if this were headed to actual production?

## Definition of done

- [ ] AWS account + IAM user + billing alarm configured.
- [ ] CI pipeline green on `main`.
- [ ] Docker image pushed to a registry.
- [ ] `terraform/` directory committed (with `*.tfvars` ignored).
- [ ] `terraform apply` succeeds; outputs include a working public URL.
- [ ] `curl http://<public-ip>/health` returns 200.
- [ ] End-to-end flow (register → login → fetch /me) works against the deployed service.
- [ ] `DEPLOY.md` committed.
- [ ] `terraform destroy` executed; AWS console shows no running resources.
- [ ] PR merged.

## Week 3 review focus

Live demo:
1. `terraform apply` from clean slate to public URL — narrate what Terraform is doing.
2. Hit the deployed service with `curl`.
3. SSH in. `docker logs api`. Show structured logs.
4. `terraform destroy`.
5. Show the CI pipeline going green on a PR.

Discuss: what's missing before this is production-ready? (Some good answers: HTTPS, managed RDS, ALB + auto-scaling, secrets manager, structured backup, monitoring/alerts.)
