# FitTracker

A full-stack fitness tracking application built with FastAPI + React.

## Features

- 💪 Workout logging with exercise library (50+ exercises)
- 🥗 Nutrition tracking with food database (200+ foods)
- 🏆 Gamification (XP, levels, 40 achievements, streaks)
- 📊 Advanced analytics with charts
- 👥 Social features (feed, follows, challenges)
- 🎯 Trainer features (programs, client tracking)
- 🏃 Cardio & strength workout tracking

## Quick Start

### With Docker (recommended)

```bash
cp fittracker-backend/.env.example fittracker-backend/.env
docker compose up
```

- App: http://localhost:5173
- API docs: http://localhost:8000/docs
- Admin panel: http://localhost:8000/admin (password: admin123)

### Manual Setup

**Backend:**

```bash
cd fittracker-backend
python -m venv venv && source venv/bin/activate
pip install -r requirements.txt
export DATABASE_URL=postgresql+asyncpg://user:pass@localhost/fittracker
alembic upgrade head
uvicorn app.main:app --reload
```

**Frontend:**

```bash
cd fittracker-frontend
npm install && npm run dev
```

## Tech Stack

- **Backend**: FastAPI, SQLAlchemy 2.0 (async), PostgreSQL, Alembic, JWT auth
- **Frontend**: React 18, TypeScript, Vite, Tailwind CSS, React Query, Recharts
- **Infrastructure**: Docker Compose, Nginx (production)

## Testing

```bash
cd fittracker-backend
venv/bin/python -m pytest tests/ -q
```

140+ tests across 12 test files.
