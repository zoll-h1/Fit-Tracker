# 🏋️ FitTracker

**Your complete personal fitness operating system.**  
Track everything. Analyze everything. Become everything.

---

## 🧠 What is FitTracker?

FitTracker is not just a workout logger. It's a **full fitness management platform** — the kind of tool a serious athlete actually needs. Every set you log, every meal you track, every gram of progress on the scale feeds into a unified system that learns your patterns, rewards your consistency, and shows you exactly where you're winning and where you're falling short.

Built with production-level architecture from day one — secure, scalable, and designed for real long-term use.

```
You finish a workout →
  ✓ Sets, reps, volume calculated
  ✓ Personal records auto-detected
  ✓ XP awarded, streak updated
  ✓ Muscle groups logged to heatmap
  ✓ Analytics updated
  ✓ Achievements checked
  ✓ Activity posted to feed
  — all automatically, in one action.
```

---

## ✨ Features

### 💪 Training Core
- **Real-time workout logging** — timer, sets, reps, weight, RPE all in one screen
- **Rest timer** — configurable countdown between sets with audio cue
- **Personal Records** — auto-detected and celebrated with full-screen animation
- **Workout history** — full session replay with volume, duration, and exercise breakdown
- **Exercise library** — 50+ seeded exercises with muscles, equipment, difficulty, instructions
- **Custom exercises** — add your own movements to the library
- **Workout templates** — save and reuse your favorite routines instantly

### 📊 Analytics
- **Strength progress** — per-exercise line charts with PR markers
- **Volume tracking** — weekly/monthly training load over time
- **Muscle heatmap** — see which muscle groups you've trained and how often
- **Workout calendar** — GitHub-style 365-day activity heatmap
- **Body composition trends** — weight, body fat %, muscle mass over time
- **PR board** — all-time personal bests across every exercise

### 🏆 Gamification
- **XP system** — earn points for every fitness action
- **10 levels** — from Newcomer to Legend, each with a title
- **Streaks** — consecutive training days tracked and protected
- **40 achievements** — across workout, strength, consistency, social, nutrition, and body categories
- **Boosts** — spend XP on Double XP, Streak Shield, Streak Freeze, and more
- **Rewards** — unlock app themes, profile frames, and exclusive titles by hitting milestones

### 🥗 Nutrition
- **Meal logging** — breakfast, lunch, dinner, snacks, pre/post workout
- **Macro calculator** — auto-calculates protein, carbs, fat from portion size
- **Food database** — 200+ seeded items + custom food creation
- **Barcode scanner** — scan packaged food to auto-fill nutritional info
- **Daily summary** — calories + macros vs your personal targets
- **Nutrition goals** — set calorie and macro targets, track weekly adherence

### 📏 Body Tracking
- **Full metrics** — weight, body fat %, muscle mass, 10 body measurements
- **BMI auto-calculation** from logged weight and profile height
- **Goal system** — set target values with deadlines, auto-marks when achieved
- **Progress photos** — private photo timeline with side-by-side comparison
- **Trend charts** — multiple metrics on one chart, date-range filterable

### 👥 Social
- **Activity feed** — see workouts, PRs, and achievements from people you follow
- **Challenges** — create or join timed fitness challenges with leaderboards
- **Follows** — follow other users, build accountability
- **Public profiles** — showcase your stats, level, and achievements
- **Likes & comments** — engage with the community's wins

### 🤖 AI Coach
- **Personalized insights** — powered by Claude AI, analyzes YOUR training history
- **Weekly reports** — auto-generated performance summary every Monday
- **Chat interface** — ask fitness questions in context of your actual data
- **Context-aware** — knows your streak, recent workouts, PRs, and goals

### 🔧 Power Tools
- **Notes** — Google Keep-style training notebook (form cues, ideas, research)
- **Gym To-Do** — Kanban board for training tasks with XP rewards
- **Recovery tracker** — daily readiness score from sleep, energy, soreness
- **Time tracker** — log gym time, cardio, mobility, study separately
- **Habit tracker** — daily habits with streaks and XP rewards
- **1RM calculator** — estimated max from any set, compared to strength standards
- **Voice logging** — hands-free set logging during workout (Web Speech API)
- **Export** — full data export as CSV or PDF monthly reports

### 🛡️ Admin Panel
- **User management** — suspend, activate, change roles
- **Exercise library** — add, edit, manage the global exercise database
- **Reports queue** — review and resolve user reports
- **Platform analytics** — registrations, active users, workouts, retention
- **Audit logs** — every admin action recorded

---

## 🛠 Tech Stack

| Layer | Technology | Why |
|-------|-----------|-----|
| **Frontend** | React 18 + TypeScript + Vite | Fast, type-safe, modern |
| **Styling** | Tailwind CSS + shadcn/ui | Dark-first, consistent design |
| **State** | Zustand + React Query | Global state + server cache |
| **Charts** | Recharts | Flexible, responsive data viz |
| **Animations** | Framer Motion | Smooth, physics-based |
| **Backend** | Python 3.11 + FastAPI | Async, auto-documented API |
| **ORM** | SQLAlchemy 2.0 (async) | Type-safe DB access |
| **Migrations** | Alembic | Version-controlled schema |
| **Database** | PostgreSQL 15 | Arrays, JSONB, full-text search |
| **Auth** | JWT (access 30min + refresh 7d) | Secure, stateless |
| **Admin** | FastAPI + Jinja2 + Bootstrap 5 | Server-rendered, fast to build |
| **Jobs** | APScheduler | Streak warnings, weekly resets |
| **Files** | Local filesystem → S3 | Avatars, progress photos |
| **Deploy** | Docker + Docker Compose | One-command setup |
| **CI/CD** | GitHub Actions | Auto-deploy on push |

---

## 🚀 Getting Started

### Prerequisites

- Docker + Docker Compose
- Git

### 1. Clone the repo

```bash
git clone https://github.com/yourusername/fittracker.git
cd fittracker
```

### 2. Set up environment

```bash
cp .env.example .env
```

Open `.env` and set your values:

```env
DB_PASSWORD=your_strong_password_here
JWT_SECRET=your_64_char_random_secret_here
SESSION_SECRET=another_64_char_random_secret
CORS_ORIGINS=http://localhost:3000
```

> **Generate secrets:** `python -c "import secrets; print(secrets.token_hex(32))"`

### 3. Run

```bash
docker-compose up --build
```

That's it. Services start, migrations run, seed data loads automatically.

| Service | URL |
|---------|-----|
| 🖥 Frontend | http://localhost:3000 |
| ⚡ Backend API | http://localhost:8000 |
| 📖 API Docs (Swagger) | http://localhost:8000/docs |
| 🛡 Admin Panel | http://localhost:8000/admin |


---

## 🗄️ Database

PostgreSQL was chosen deliberately over MySQL and NoSQL options. Key reasons:

- **Native arrays** — muscle groups stored as `TEXT[]`, queryable with GIN indexes
- **JSONB** — boost effects, achievement configs, reward data stored flexibly without sacrificing query performance  
- **Full-text search** — exercise and food search using `tsvector` + `pg_trgm` (fuzzy matching)
- **Window functions** — analytics queries use `RANK()`, `LAG()`, `PARTITION BY` natively
- **ACID transactions** — "log set + check PR + award XP + notify" is one atomic operation

**Schema:** 30+ tables, fully normalized, with strategic denormalization only where query speed demands it (likes count, comments count on feed items).

**Scaling path:** single instance → read replica → PgBouncer pooling → table partitioning — all documented without requiring a rewrite.

---

## 📁 Project Structure

```
fittracker/
├── backend/
│   ├── app/
│   │   ├── main.py              # FastAPI app, CORS, routers
│   │   ├── models/              # SQLAlchemy models (10 files)
│   │   ├── schemas/             # Pydantic schemas
│   │   ├── routers/             # API routes (11 modules)
│   │   ├── services/            # Business logic
│   │   └── core/                # Security, config, scheduler
│   ├── alembic/                 # Database migrations
│   ├── uploads/                 # User files
│   └── tests/
│
├── frontend/
│   └── src/
│       ├── api/                 # Typed API client (Axios)
│       ├── pages/               # Route-level components
│       ├── components/          # Reusable UI components
│       ├── stores/              # Zustand state
│       ├── hooks/               # Custom React hooks
│       └── types/               # TypeScript interfaces
│
├── docs/                        # Full project documentation (13 files)
├── docker-compose.yml
└── .env.example
```

---

## 📖 Documentation

The project ships with complete production documentation across 13 files:

| File | Contents |
|------|----------|
| `FT_00_MAIN_README.md` | Project vision, architecture, feature map |
| `FT_01_DATABASE_SCHEMA.md` | Full SQL schema for all 30+ tables |
| `FT_02_BACKEND_API.md` | All API modules, endpoints, and Codex prompts |
| `FT_03_FRONTEND_REACT.md` | Pages, components, state setup |
| `FT_04_ADMIN_PANEL.md` | Admin panel — all pages and routes |
| `FT_05_SECURITY_RULES.md` | Non-negotiable security requirements |
| `FT_06_AI_PROMPTS.md` | Codex/Gemini/Claude prompt templates |
| `FT_07_TESTING_GUIDE.md` | Manual test cases for every module |
| `FT_08_DEPLOYMENT.md` | Docker, Railway, Render, VPS setup |
| `FT_09_FEATURES_ROADMAP.md` | 12-week build order and priority matrix |
| `FT_10_FUTURE_MODIFICATIONS.md` | 24 planned future features with full specs |
| `FT_11_DATABASE_DEEP_DIVE.md` | Database rationale, scaling, indexing strategy |
| `FT_PROJECT_TRACKER.md` | Week-by-week progress tracker |

---

## 🗺 Roadmap

### ✅ Phase 1 — Core (Weeks 1–4)
- [ ] Authentication + user profiles
- [ ] Real-time workout logging
- [ ] Body metrics tracking
- [ ] Nutrition logging
- [ ] Gamification (XP, levels, streaks, achievements)
- [ ] Analytics dashboard

### 🔄 Phase 2 — Valuable (Weeks 5–8)
- [ ] Workout templates
- [ ] Social feed + follows
- [ ] Challenges + leaderboards
- [ ] Admin panel
- [ ] Notifications system
- [ ] Notes + Gym To-Do
- [ ] Recovery tracker
- [ ] Boosts + Rewards

### 📋 Phase 3 — Power Features (Weeks 9–12)
- [ ] AI Coach (Anthropic API)
- [ ] Barcode food scanner
- [ ] Progress photo comparison
- [ ] Voice logging
- [ ] 1RM calculator + strength standards
- [ ] Habit tracker
- [ ] Export + PDF reports
- [ ] PWA (installable on phone)

### 🔭 Phase 4 — Advanced
- [ ] Periodization planner + program builder
- [ ] Spotify integration
- [ ] Calendar sync (Google)
- [ ] Wearable import (Garmin, Apple Health)
- [ ] Injury tracker + prevention warnings
- [ ] Trainer features + client management

---

## 🔐 Security

Security is treated as a first-class concern, not an afterthought.

- Passwords hashed with **bcrypt** (12 rounds)
- **JWT** with short-lived access tokens (30 min) + rotating refresh tokens (7 days)
- **Rate limiting** on all auth endpoints (5 attempts/min)
- **Ownership checks** on every data endpoint — you cannot access another user's data
- **File uploads** validated by real MIME type (not just extension), EXIF stripped
- **SQL injection** prevented by ORM + parameterized queries only
- **CORS** locked to specific origins, never wildcard in production
- **Security headers** — X-Frame-Options, X-Content-Type-Options, Referrer-Policy
- All secrets in environment variables, never in code

---

## 🤝 Contributing

This is a personal project, but PRs and issues are welcome.

```bash
# Fork → clone → create branch
git checkout -b feature/your-feature-name

# Make changes, test them
# See FT_07_TESTING_GUIDE.md for test procedures

# Commit with clear message
git commit -m "feat: add barcode scanner to nutrition module"

# Push + open PR
```

**Commit convention:** `feat:` / `fix:` / `docs:` / `refactor:` / `test:`

---

## 📄 License

MIT — do whatever you want with it.

---




