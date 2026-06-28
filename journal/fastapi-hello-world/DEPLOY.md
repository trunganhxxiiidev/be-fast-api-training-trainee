# Deploy Day 15

This guide deploys the FastAPI training API to one EC2 instance with Terraform.
The instance runs three Docker containers: API, Postgres, and Redis.

## Prerequisites

- AWS CLI v2 installed.
- Terraform installed.
- Docker installed locally.
- AWS CLI profile configured:
  ```bash
  aws configure --profile intern-deploy
  aws --profile intern-deploy sts get-caller-identity
  ```
- EC2 key pair exists in `ap-southeast-2`:
  ```bash
  aws --profile intern-deploy ec2 describe-key-pairs \
    --region ap-southeast-2 \
    --key-names intern-day15
  ```
- Current public IPv4 address:
  ```bash
  curl -4 -s https://ifconfig.me
  ```

## Build And Push The Image

Use Docker Hub or another public registry that EC2 can pull without extra auth.

```bash
docker build -t YOUR_DOCKERHUB_USER/intern-api:day15 .
docker push YOUR_DOCKERHUB_USER/intern-api:day15
```

## Configure Terraform

```bash
cd terraform
cp terraform.tfvars.example terraform.tfvars
```

Edit `terraform.tfvars`:

```hcl
aws_profile      = "intern-deploy"
region           = "ap-southeast-2"
project_name     = "intern-api"
owner            = "austin-nguyen"
instance_type    = "t3.micro"
key_name         = "intern-day15"
allowed_ssh_cidr = "YOUR_PUBLIC_IPV4/32"
image_uri        = "docker.io/YOUR_DOCKERHUB_USER/intern-api:day15"
jwt_secret       = "replace-with-a-training-secret-at-least-32-bytes"
```

Do not commit `terraform.tfvars`, `.terraform/`, or `terraform.tfstate*`.

## Deploy

```bash
terraform init
terraform plan
terraform apply
```

Read the plan before typing `yes`.

## Verify

```bash
terraform output
curl "$(terraform output -raw api_url)/health"
curl "$(terraform output -raw api_url)/ready"
```

SSH into the host:

```bash
$(terraform output -raw ssh_command)
docker ps
docker logs api --tail 100
```

Expected containers:

- `api`
- `pg`
- `cache`

## Tear Down

Destroy the EC2 instance and security group at the end of the day:

```bash
terraform destroy
```

Then verify in the AWS Console that the EC2 instance is terminated and no extra
Elastic IP, load balancer, or NAT gateway was created.

## Safety Notes

- Keep SSH restricted to your current `/32` IP.
- Do not create a NAT gateway or load balancer for this lab.
- Do not commit AWS access keys, `.pem` files, `terraform.tfvars`, or state files.
- If the AWS access key is exposed, ask the lead to deactivate it and create a new one.
