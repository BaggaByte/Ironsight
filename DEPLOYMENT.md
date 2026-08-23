# Ironsight Deployment Guide

This guide covers deploying the Ironsight stack using Docker Compose.

## Prerequisites
- Docker Engine & Docker Compose
- Node.js (for local frontend development)
- Python 3.10+ (for local backend development)

## 1. Secrets and Environment Variables

Before starting the stack, you **must** configure a `.env` file at the root of the repository. Do not use default or hardcoded secrets in production.

Generate a secure `SECRET_KEY`:
```bash
openssl rand -hex 32
```

Create `.env` based on the provided template:
```env
# Required core secrets
SECRET_KEY=your_secure_hex_string
DATABASE_URL=postgresql://postgres:postgres@postgres:5432/ironsight_db
REDIS_URL=redis://redis:6379/0

# Optional integrations
GROQ_API_KEY=your_groq_key
NVD_API_KEY=your_nvd_key

# Admin configuration
CREATE_DEFAULT_ADMIN=true
DEFAULT_ADMIN_PASSWORD=your_secure_admin_password
```

## 2. Running the Stack

To spin up the entire unified Ironsight platform (Postgres, Redis, Neo4j, MinIO, API, Worker, Next.js):
```bash
docker-compose up -d
```

### Accessing Services
- **Next.js Dashboard**: `http://localhost:3000`
- **FastAPI Swagger Docs**: `http://localhost:8000/docs`
- **MinIO Console**: `http://localhost:9001` (Creds: `minioadmin`/`minioadmin`)

## 3. Production Hardening Notes

- **CORS**: By default, `backend/main.py` restricts CORS to specific frontend origins (e.g., `localhost:3000`). If deploying to a remote server, update `allow_origins` to match your domain.
- **Resource Limits**: Memory (1GB) and CPU limits (1 core) are applied to the `ironsight-frontend` by default to prevent runaway Next.js dev server builds.
- **Observability Stack**: `grafana`, `pgadmin`, and `opensearch-dashboards` have been secured with generic credentials in `docker-compose.yml`. In a real production scenario, these should be moved to `.env` variables or hidden behind a proxy (like Nginx) entirely.

## 4. Git History 
This repository underwent a major history rewrite to purge accidentally committed `.db` files and old `.env` files. If you find legacy artifacts, please use `git filter-repo` to invert them locally.
