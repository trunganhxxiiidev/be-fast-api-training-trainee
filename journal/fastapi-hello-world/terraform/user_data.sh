#!/bin/bash
set -euxo pipefail

dnf update -y
dnf install -y docker
systemctl enable --now docker

docker network create intern-api || true

docker volume create pg_data

docker rm -f pg cache api || true

docker run -d \
  --name pg \
  --network intern-api \
  --restart unless-stopped \
  -e POSTGRES_PASSWORD=apppass \
  -e POSTGRES_DB=app \
  -v pg_data:/var/lib/postgresql/data \
  postgres:16-alpine

until docker exec pg pg_isready -U postgres -d app; do
  sleep 2
done

docker run -d \
  --name cache \
  --network intern-api \
  --restart unless-stopped \
  redis:7-alpine

docker run -d \
  --name api \
  --network intern-api \
  --restart unless-stopped \
  -e ENVIRONMENT=prod \
  -e LOG_LEVEL=INFO \
  -e DATABASE_URL=postgresql+asyncpg://postgres:apppass@pg:5432/app \
  -e DATABASE_ECHO=false \
  -e REDIS_URL=redis://cache:6379/0 \
  -e JWT_SECRET="${jwt_secret}" \
  -p 80:8000 \
  ${image_uri}
