# FT_08 — DEPLOYMENT GUIDE
# FitTracker | Docker + Cloud Deployment

---

## 🐳 LOCAL DEVELOPMENT (Docker)

### docker-compose.yml

```yaml
version: "3.9"

services:
  postgres:
    image: postgres:15-alpine
    container_name: fittracker-db
    environment:
      POSTGRES_DB: fittracker
      POSTGRES_USER: fittracker_user
      POSTGRES_PASSWORD: ${DB_PASSWORD}
    volumes:
      - postgres_data:/var/lib/postgresql/data
    ports:
      - "5432:5432"
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U fittracker_user -d fittracker"]
      interval: 10s
      timeout: 5s
      retries: 5

  redis:
    image: redis:7-alpine
    container_name: fittracker-redis
    ports:
      - "6379:6379"
    volumes:
      - redis_data:/data

  backend:
    build:
      context: ./backend
      dockerfile: Dockerfile
    container_name: fittracker-backend
    depends_on:
      postgres:
        condition: service_healthy
    environment:
      DATABASE_URL: postgresql+asyncpg://fittracker_user:${DB_PASSWORD}@postgres:5432/fittracker
      JWT_SECRET: ${JWT_SECRET}
      JWT_ALGORITHM: HS256
      ACCESS_TOKEN_EXPIRE_MINUTES: 30
      REFRESH_TOKEN_EXPIRE_DAYS: 7
      REDIS_URL: redis://redis:6379
      UPLOAD_DIR: /app/uploads
      CORS_ORIGINS: ${CORS_ORIGINS}
      DEBUG: ${DEBUG:-false}
      SESSION_SECRET: ${SESSION_SECRET}
    volumes:
      - ./backend/uploads:/app/uploads
    ports:
      - "8000:8000"
    command: >
      sh -c "alembic upgrade head &&
             python -m app.seed &&
             uvicorn app.main:app --host 0.0.0.0 --port 8000"

  frontend:
    build:
      context: ./frontend
      dockerfile: Dockerfile
      args:
        VITE_API_URL: http://localhost:8000
    container_name: fittracker-frontend
    ports:
      - "3000:80"
    depends_on:
      - backend

volumes:
  postgres_data:
  redis_data:
```

### .env (local)
```bash
# Database
DB_PASSWORD=your_strong_db_password_here

# JWT (generate: python -c "import secrets; print(secrets.token_hex(32))")
JWT_SECRET=your_64_char_random_secret_here

# Session (for admin panel)
SESSION_SECRET=another_64_char_random_secret

# CORS
CORS_ORIGINS=http://localhost:3000,http://localhost:5173

# Debug
DEBUG=true
```

---

## 📦 DOCKERFILES

### Backend Dockerfile
```dockerfile
FROM python:3.11-slim

WORKDIR /app

# Install system deps (for python-magic, Pillow)
RUN apt-get update && apt-get install -y \
    libmagic1 \
    libjpeg-dev \
    libpng-dev \
    && rm -rf /var/lib/apt/lists/*

# Install Python deps
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy app
COPY . .

# Create uploads directory
RUN mkdir -p uploads/avatars uploads/workouts uploads/meals

# Run as non-root user (security)
RUN useradd -m appuser && chown -R appuser /app
USER appuser

EXPOSE 8000
```

### Frontend Dockerfile
```dockerfile
# Build stage
FROM node:20-alpine AS builder

WORKDIR /app

ARG VITE_API_URL
ENV VITE_API_URL=$VITE_API_URL

COPY package*.json .
RUN npm ci

COPY . .
RUN npm run build

# Production stage
FROM nginx:alpine

COPY --from=builder /app/dist /usr/share/nginx/html
COPY nginx.conf /etc/nginx/conf.d/default.conf

EXPOSE 80
```

### frontend/nginx.conf
```nginx
server {
    listen 80;
    root /usr/share/nginx/html;
    index index.html;

    # Handle React Router (all paths → index.html)
    location / {
        try_files $uri $uri/ /index.html;
    }

    # Cache static assets
    location ~* \.(js|css|png|jpg|svg|ico)$ {
        expires 1y;
        add_header Cache-Control "public, immutable";
    }

    # Gzip
    gzip on;
    gzip_types text/plain application/javascript text/css application/json;
}
```

---

## 🚀 CLOUD DEPLOYMENT (Free Tier)

### Option A: Railway (Recommended — Easiest)

```bash
# 1. Install Railway CLI
npm install -g @railway/cli

# 2. Login
railway login

# 3. Init project
railway init

# 4. Add PostgreSQL
railway add postgresql

# 5. Deploy backend
cd backend
railway up

# 6. Set environment variables in Railway dashboard:
# JWT_SECRET, SESSION_SECRET, CORS_ORIGINS

# 7. Get backend URL from Railway
# Update frontend VITE_API_URL

# 8. Deploy frontend
cd ../frontend
railway up
```

**Railway Free Tier**: $5/month credit = runs small app for free.
**PostgreSQL**: Included.
**Auto-deploy**: Push to GitHub → auto deploy.

---

### Option B: Render.com (Also Free)

```yaml
# render.yaml (put in project root)
services:
  - type: web
    name: fittracker-backend
    env: python
    buildCommand: pip install -r requirements.txt
    startCommand: alembic upgrade head && uvicorn app.main:app --host 0.0.0.0 --port $PORT
    envVars:
      - key: DATABASE_URL
        fromDatabase:
          name: fittracker-db
          property: connectionString
      - key: JWT_SECRET
        generateValue: true
      - key: SESSION_SECRET
        generateValue: true

  - type: web
    name: fittracker-frontend
    env: static
    buildCommand: npm run build
    staticPublishPath: ./dist
    envVars:
      - key: VITE_API_URL
        value: https://fittracker-backend.onrender.com

databases:
  - name: fittracker-db
    plan: free
    databaseName: fittracker
    user: fittracker_user
```

**Render Free Tier Notes**:
- Free services spin down after 15min inactivity (cold start ~30s)
- Free PostgreSQL: 1GB storage, expires after 90 days
- For personal use: acceptable. For demo: wake it up before showing.

---

### Option C: VPS (Cheapest Long-term)

**DigitalOcean Droplet $6/month** — full control:

```bash
# 1. Create Ubuntu 22.04 droplet ($6/mo)
# 2. SSH in

# 3. Install Docker
curl -fsSL https://get.docker.com | sh
sudo usermod -aG docker $USER

# 4. Clone repo
git clone https://github.com/yourname/fittracker.git
cd fittracker

# 5. Create .env with production values
cp .env.example .env
nano .env  # Set strong values

# 6. Run
docker-compose up -d

# 7. Setup Nginx reverse proxy
sudo apt install nginx certbot python3-certbot-nginx

# 8. Get SSL cert (requires domain)
sudo certbot --nginx -d fittracker.yourdomain.com
```

---

## 🔄 CI/CD (GitHub Actions)

```yaml
# .github/workflows/deploy.yml
name: Deploy FitTracker

on:
  push:
    branches: [main]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - uses: actions/setup-python@v4
        with:
          python-version: '3.11'
      - run: pip install -r backend/requirements.txt
      - run: cd backend && pytest tests/ -v

  deploy:
    needs: test
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      # Railway auto-deploys on push if connected to GitHub
      # Or add deploy step for your chosen platform
```

---

## 🌱 SEED DATA SCRIPT

```python
# backend/app/seed.py
# Run once on first deploy

async def seed_database():
    async with SessionLocal() as db:
        # 1. Create admin user
        admin_exists = await db.scalar(select(User).where(User.email == "admin@fittracker.com"))
        if not admin_exists:
            admin = User(
                username="admin",
                email="admin@fittracker.com",
                password_hash=hash_password("Admin123!"),
                full_name="FitTracker Admin",
                role="admin",
                is_active=True,
                is_email_verified=True
            )
            db.add(admin)

        # 2. Seed muscle groups
        # 3. Seed equipment types  
        # 4. Seed exercise library (50 exercises)
        # 5. Seed achievement definitions (40 achievements)
        # 6. Seed food database (200 foods)
        # 7. Seed promotion packages
        
        await db.commit()
        print("✅ Seed data created successfully")

if __name__ == "__main__":
    import asyncio
    asyncio.run(seed_database())
```

---

## 📋 PRODUCTION CHECKLIST

Before going live:

```
SECURITY:
[ ] JWT_SECRET is 64+ chars random (not "secret" or "password")
[ ] SESSION_SECRET is 64+ chars random
[ ] DB_PASSWORD is strong (generated, not guessable)
[ ] CORS_ORIGINS set to actual frontend URL only
[ ] DEBUG=false in production
[ ] .env not committed to git
[ ] HTTPS enabled (SSL cert)

DATABASE:
[ ] Alembic migrations run
[ ] Seed data created
[ ] Admin user created with strong password
[ ] Database backups configured (Railway/Render do this automatically)

PERFORMANCE:
[ ] uvicorn with multiple workers: --workers 2
[ ] Database connection pool configured
[ ] Static files served by Nginx (not FastAPI)

MONITORING:
[ ] Health check endpoint: GET /health → {"status": "ok"}
[ ] Error logging configured (logs to stdout for Docker)
[ ] Uptime monitoring (UptimeRobot free tier)
```

---

## 🆘 COMMON DEPLOYMENT ISSUES

### Database connection fails
```bash
# Check DATABASE_URL format for asyncpg:
# postgresql+asyncpg://user:password@host:5432/dbname
# NOT postgresql:// (that's for sync SQLAlchemy)
```

### Alembic migration fails
```bash
# Run manually to see error:
docker exec -it fittracker-backend alembic upgrade head

# Common fix: check models imported in alembic/env.py
from app.models import *  # Add this line
```

### CORS errors in browser
```bash
# Check CORS_ORIGINS includes exact frontend URL
# Including protocol (https://) and no trailing slash
CORS_ORIGINS=https://fittracker-frontend.railway.app
```

### Upload files not persisting (Railway/Render)
```bash
# Ephemeral filesystem = uploads lost on restart
# Quick fix: mount a volume in Railway/Render
# Long-term fix: use S3/Cloudflare R2 for file storage
```
