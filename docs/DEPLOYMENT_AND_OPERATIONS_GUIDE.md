# MASTERY — Deployment & Operations Guide
## Architecture Deployment States, Containerization, Cloud Infrastructure & Operational Runbooks

**Platform:** MASTERY — Beyond Marks. Towards Mastery.  
**Team:** VARY — SRUJAN 2026  
**Problem Statement:** AI-03 — Student Performance Prediction  
**Track:** AI, CyberSecurity and Digital Trust  
**Phase:** 11/11 — Final Platform Hardening & Release Preparation  
**Target Environment:** Local Workstations, Dockerized Staging, and Supabase Cloud Production  

---

## 1. Deployment Readiness Status Matrix

To avoid misrepresenting development prototypes as production-hardened deployments, this section explicitly classifies every subsystem according to its verified operational readiness:

```
+---------------------------------------------------------------------------------------------------------+
|                                    MASTERY DEPLOYMENT MATURITY MATRIX                                   |
+------------------------------------+--------------------------+-----------------------+-----------------+
| Subsystem / Layer                  | Target Environment       | Verified Status       | Classification  |
+------------------------------------+--------------------------+-----------------------+-----------------+
| FastAPI Core REST Service          | Localhost / Uvicorn      | 100% Tests Passing    | LOCALLY VERIFIED|
| React 18 TypeScript Frontend       | Vite Development Server  | 100% Functional       | LOCALLY VERIFIED|
| Frontend Production Build Bundle   | Static Web Server (Nginx)| Built to `dist/`      | STAGING READY   |
| Supabase PostgreSQL Database       | Supabase Cloud Project   | 58 Tables / Alembic   | PRODUCTION LIVE |
| Supabase Auth & JWT Verification   | GoTrue JWKS / HS256      | Cryptographically OK  | PRODUCTION LIVE |
| Docker Containerization            | Dockerfile / Compose     | Multi-Stage Recipes   | STAGING READY   |
| CI/CD Pipeline Automation          | GitHub Actions Workflows | Local Pre-Commit Runs | NOT CONFIGURED  |
| Horizontal Auto-Scaling / K8s     | Cloud Kubernetes Cluster | Single Instance Pool  | FUTURE SCOPE    |
+------------------------------------+--------------------------+-----------------------+-----------------+
```

---

## 2. Containerized Deployment Strategy (Docker)

### 2.1 Backend Dockerfile (`backend/Dockerfile`)
A production-ready multi-stage Docker build recipe:
```dockerfile
# Stage 1: Build & Dependency Wheel Cache
FROM python:3.11-slim as builder
WORKDIR /app
RUN apt-get update && apt-get install -y --no-install-recommends gcc libpq-dev && rm -rf /var/lib/apt/lists/*
COPY requirements.txt .
RUN pip wheel --no-cache-dir --no-deps --wheel-dir /app/wheels -r requirements.txt

# Stage 2: Minimal Runtime Container
FROM python:3.11-slim
WORKDIR /app
RUN apt-get update && apt-get install -y --no-install-recommends libpq5 && rm -rf /var/lib/apt/lists/*
COPY --from=builder /app/wheels /wheels
RUN pip install --no-cache /wheels/*
COPY . .
EXPOSE 8000
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000", "--workers", "4"]
```

### 2.2 Frontend Dockerfile (`frontend/Dockerfile`)
```dockerfile
# Stage 1: Compile React Production Bundle
FROM node:20-alpine as build
WORKDIR /app
COPY package.json pnpm-lock.yaml ./
RUN corepack enable && pnpm install --frozen-lockfile
COPY . .
RUN npm run build

# Stage 2: High-Performance Nginx Web Server
FROM nginx:alpine
COPY --from=build /app/dist /usr/share/nginx/html
COPY nginx.conf /etc/nginx/conf.d/default.conf
EXPOSE 80
CMD ["nginx", "-g", "daemon off;"]
```

### 2.3 Docker Compose Staging Configuration (`docker-compose.yml`)
```yaml
version: "3.8"

services:
  backend:
    build: ./backend
    ports:
      - "8000:8000"
    environment:
      - APP_ENV=production
      - DATABASE_URL=${DATABASE_URL}
      - SUPABASE_URL=${SUPABASE_URL}
      - SUPABASE_SECRET_KEY=${SUPABASE_SECRET_KEY}
    restart: unless-stopped

  frontend:
    build: ./frontend
    ports:
      - "80:80"
    depends_on:
      - backend
    restart: unless-stopped
```

---

## 3. Operational Runbooks & Health Monitoring

### 3.1 Health Check Endpoints
MASTERY provides standardized health check probes for container orchestrators (Kubernetes `livenessProbe` and `readinessProbe`):
1. **Liveness Probe:** `GET /api/v1/health`
   - Returns service uptime, service name, and version without checking external dependencies.
   - Response: `{"status": "healthy", "service": "MASTERY", "version": "0.1.0"}`
2. **Readiness Probe:** `GET /api/v1/health/database`
   - Tests active PostgreSQL connection pool latency and query execution.
   - Response: `{"status": "healthy", "database_connected": true, "latency_ms": 1.25}`

### 3.2 Database Backup & Disaster Recovery
- **Continuous Backups:** Supabase Cloud provides Point-in-Time Recovery (PITR) for PostgreSQL transactions.
- **Logical Schema Dumps:** To create an offline snapshot of the schema and seed state:
  ```bash
  pg_dump -h <SUPABASE_DB_HOST> -U postgres -d postgres --schema=public -F p -f mastery_backup.sql
  ```
- **Migration Rollbacks:** Migrations are governed by Alembic. In the event of schema rollback:
  ```bash
  cd backend
  alembic downgrade -1
  ```

---

## 4. Operational Troubleshooting Guide

| Symptom | Root Cause | Remediation Procedure |
|---|---|---|
| **`Database connection operational: False`** | Unpopulated `[YOUR-PASSWORD]` placeholder or IP allowlist block in Supabase. | Update `DATABASE_URL` in `backend/.env` with actual DB credentials and ensure connection string uses `postgresql+psycopg://`. |
| **`401 Missing access token` on frontend** | Expired session or missing Bearer token in Axios/Fetch header. | Trigger re-login at `/login` or verify `VITE_SUPABASE_URL` matches backend configuration. |
| **`403 Access Forbidden` on Dashboard** | Authenticated user lacks authorized role or attempted cross-institution lookup. | Verify user's assigned role in `profiles` and check that `institution_id` matches target query parameters. |
| **`CORS Request Blocked`** | Frontend origin port mismatch. | Add client origin (e.g., `http://localhost:5173`) to `CORS_ORIGINS` in `backend/app/core/config.py`. |
