# FT_06 — AI GENERATION PROMPTS
# FitTracker | Templates for Codex CLI, Gemini CLI, Anthropic

---

## 📋 HOW TO USE THIS FILE

- **Codex CLI**: Code generation (new modules, components, schemas)
- **Gemini CLI**: Debugging errors, complex SQL, optimization
- **Claude (me)**: Architecture decisions, security review, weekly planning
- **Ollama (qwen3:8b)**: Quick syntax questions, small concepts

---

## 🔧 CODEX CLI PROMPTS

### Rule: Always give Codex context

Every Codex prompt should start with:
```
Context: FastAPI + SQLAlchemy (async) + PostgreSQL + Pydantic v2.
Auth: JWT with get_current_user dependency.
Error format: {"detail": "...", "code": "ERROR_CODE"}
Follow existing patterns from [reference file].
```

---

### PROMPT SET A — Backend Setup

#### A1. Project initialization
```
Create FastAPI project structure for FitTracker:

Tech: FastAPI 0.110+, SQLAlchemy 2.0 async, Alembic, PostgreSQL
Structure:
- app/main.py: FastAPI app, CORS, router inclusion, static files, scheduler startup
- app/database.py: async engine, SessionLocal, Base, get_db dependency
- app/config.py: Settings class from .env (DATABASE_URL, JWT_SECRET, etc.)
- app/dependencies.py: get_current_user dependency
- app/core/security.py: hash_password, verify_password, create_token, decode_token
- app/core/exceptions.py: custom HTTPExceptions with code fields
- alembic.ini + alembic/env.py configured for async PostgreSQL
- requirements.txt with all dependencies
- .env.example
- Dockerfile
Include comments explaining each section.
```

#### A2. Async SQLAlchemy pattern
```
Show correct pattern for async SQLAlchemy 2.0 with FastAPI:
- async engine creation
- AsyncSession with context manager
- get_db as async generator dependency
- Correct way to query: select(Model).where(Model.id == id)
- Correct way to add: db.add(obj), await db.commit(), await db.refresh(obj)
- Correct way to delete: await db.delete(obj), await db.commit()
Include example CRUD for a User model.
```

---

### PROMPT SET B — Authentication

#### B1. Full auth module
```
Create complete FastAPI authentication module.
Context: async SQLAlchemy, PostgreSQL.

User model (app/models/user.py):
id, username (unique), email (unique), password_hash, full_name, 
date_of_birth, gender (enum: male/female/other), unit_system (enum: metric/imperial),
timezone, bio, avatar_url, height_cm, weight_kg,
role (enum: user/premium/trainer/admin, default: user),
is_active (default True), is_email_verified (default False),
created_at, updated_at, last_active_at

Schemas (app/schemas/auth.py):
- RegisterRequest: username, email, password (min 8, has uppercase+number), full_name, 
  date_of_birth, gender, unit_system
- LoginRequest: email, password
- TokenResponse: access_token, refresh_token, token_type, user (UserBasicResponse)
- UserBasicResponse: id, username, full_name, avatar_url, role, unit_system

RefreshToken model: id, user_id, token_hash, expires_at, created_at, is_revoked

Routes (app/routers/auth.py):
- POST /api/auth/register → hash password, create user, create refresh token, return tokens
- POST /api/auth/login → verify credentials, return tokens
- POST /api/auth/refresh → validate refresh token, issue new access token
- POST /api/auth/logout → revoke refresh token
- GET /api/auth/me → return current user profile

Security:
- bcrypt 12 rounds
- access token: 30 min expiry
- refresh token: 7 days, stored as hash (not plaintext) in DB
- Rate limit login: 5/minute per IP (use slowapi)
- Same error message for wrong email and wrong password (prevent enumeration)
```

---

### PROMPT SET C — Core Features

#### C1. Workout session with real-time logging
```
Create FastAPI workout session module.
Context: async SQLAlchemy, JWT auth.

Refer to models in FT_01_DATABASE_SCHEMA.md:
WorkoutSession, WorkoutExercise, WorkoutSet, WorkoutTemplate, TemplateExercise

Service (app/services/workout_service.py):
- calculate_volume(session_id) → sum(weight_kg * reps) for all completed sets
- estimate_calories(session: WorkoutSession, user: User) → MET * weight * hours
- check_personal_records(user_id, exercise_id, weight, reps) → returns PR data if new record
- finish_session(session_id, user_id) → update duration, volume, calories, trigger gamification

Routes:
POST /api/workouts → create session {name, notes?, template_id?}, return session with empty exercises
GET /api/workouts → list user's sessions, paginated, filter by date range
GET /api/workouts/{id} → full detail with exercises and sets
PUT /api/workouts/{id} → update name/notes only
DELETE /api/workouts/{id} → only if status=in_progress or cancelled
POST /api/workouts/{id}/finish → call finish_session service, return summary
POST /api/workouts/{id}/exercises → add exercise {exercise_library_id, exercise_order, rest_seconds}
PUT /api/workouts/{id}/exercises/{ex_id} → update notes/rest_seconds/order
DELETE /api/workouts/{id}/exercises/{ex_id} → remove (cascades sets)
POST /api/workouts/{id}/exercises/{ex_id}/sets → log set {set_number, set_type, reps, weight_kg, rpe, completed}
PUT /api/workouts/sets/{set_id} → update any set field
DELETE /api/workouts/sets/{set_id} → delete set

All endpoints: ownership check required.
Include "previous_performance" in exercise response: last session's sets for same exercise.
```

#### C2. Gamification service
```
Create gamification service for FitTracker.
Context: async SQLAlchemy. Called internally after user actions, NOT directly from routes.

Models: UserXP, AchievementDefinition, UserAchievement (from schema)

Service (app/services/gamification_service.py):

async def award_xp(db, user_id: int, amount: int, reason: str) -> dict:
  - Add XP to user's total
  - Check if level increased (use level thresholds)
  - Return {"xp_awarded": 50, "new_total": 1250, "leveled_up": True, "new_level": 4}

XP Awards:
- "workout_completed": 50 XP
- "pr_achieved": 100 XP
- "streak_7": 200 XP
- "streak_30": 500 XP
- "goal_reached": 150 XP
- "meal_logged": 10 XP
- "body_metric_logged": 20 XP
- "first_follow": 5 XP

Level thresholds: [0, 500, 1200, 2500, 5000, 9000, 15000, 25000, 40000, 60000]
Level names: ["Newcomer","Beginner","Amateur","Intermediate","Advanced","Expert","Elite","Master","Champion","Legend"]

async def update_streak(db, user_id: int) -> dict:
  - Check last_workout_date on UserXP
  - If yesterday: increment streak, update last_workout_date
  - If today: streak unchanged (already counted)
  - If more than yesterday: reset streak to 1
  - Check streak milestones (3,7,14,30,60,90,180,365) → call check_achievements
  - Return {"current_streak": 8, "milestone_reached": 7}

async def check_achievements(db, user_id: int, event_type: str, value: float = None):
  - Query all unearned achievements matching event_type
  - For each: check if user meets requirement
  - Award any qualifying ones
  - Create notifications for awarded achievements
  - Return list of newly earned achievements

Seed 40 achievements across: workout_count, streak, pr_count, body_goal, social, nutrition
```

#### C3. Analytics queries
```
Create FastAPI analytics module.
Context: async SQLAlchemy, PostgreSQL. All endpoints require auth.

Routes (app/routers/analytics.py):

GET /api/analytics/dashboard
Query: aggregate stats for current_user
Return:
{
  this_week_workouts: int,
  this_month_workouts: int,
  total_workouts: int,
  total_volume_kg: float,
  avg_duration_minutes: float,
  current_streak: int,
  longest_streak: int,
  recent_prs: [{exercise_name, weight_kg, reps, achieved_at}] (last 5),
  this_week_calories_burned: float
}

GET /api/analytics/strength?exercise_id=1&period=90d
Return: [{date, max_weight_kg, total_volume_kg, total_sets}] sorted by date
Also include: all_time_pr: {weight_kg, reps, date}

GET /api/analytics/muscles?period=30d
Return: [{muscle_group, sets_count, percentage}] sorted by sets_count desc

GET /api/analytics/personal-records
Return: one record per exercise (the best set), sorted by most recent
[{exercise_id, exercise_name, weight_kg, reps, achieved_at, workout_id}]

GET /api/analytics/streak
Return: {
  current_streak, longest_streak,
  calendar: [{date: "2025-01-01", has_workout: true}] for last 365 days
}

Use SQLAlchemy func.sum, func.count, func.max, func.date for aggregations.
All queries scoped to current_user.id.
Support period: "7d", "30d", "90d", "1y", "all"
```

---

### PROMPT SET D — Frontend Components

#### D1. React API client setup
```
Create TypeScript API client setup for FitTracker React app.

File: src/api/client.ts
- Axios instance with baseURL from import.meta.env.VITE_API_URL
- Request interceptor: add "Authorization: Bearer {token}" from localStorage
- Response interceptor:
  - 401: attempt refresh (POST /api/auth/refresh), retry once, on second 401 → clear auth + redirect to /login
  - 500: dispatch toast "Server error"
- Export typed functions for common patterns

File: src/stores/authStore.ts (Zustand)
interface AuthState {
  user: User | null
  accessToken: string | null
  refreshToken: string | null
  isAuthenticated: boolean
  setAuth: (user: User, accessToken: string, refreshToken: string) => void
  logout: () => void
  updateUser: (user: Partial<User>) => void
}
Persist to localStorage with key "ft-auth".

File: src/api/workouts.ts
TypeScript functions wrapping axios:
- getWorkouts(params): Promise<WorkoutListResponse>
- createWorkout(data): Promise<WorkoutSession>
- finishWorkout(id): Promise<WorkoutSummary>
- addSet(workoutId, exerciseId, setData): Promise<WorkoutSet>
All with proper TypeScript types.

File: src/types/workout.ts
Full TypeScript interfaces for all workout-related types.
```

#### D2. Active Workout component
```
Create React Active Workout page — the core feature.
TypeScript, Tailwind CSS, Zustand.

Features:
1. Workout timer (counting up from 0, format mm:ss)
2. List of exercises with sets
3. Each set row: set number | type dropdown | weight input | reps input | done checkbox
4. Inline editing: tap weight/reps → number input field
5. Checkmark on set → mark completed, auto-start rest timer if configured
6. Rest timer: countdown modal overlay (shows 60s counting down, skip button)
7. "+ Add Set" button at bottom of each exercise
8. "+ Add Exercise" → opens ExerciseSearchModal
9. "Finish Workout" → shows summary modal → POST /api/workouts/{id}/finish
10. Previous performance: show last session's values as gray placeholder text

ExerciseSearchModal:
- Search input
- GET /api/exercise-library?search=...
- Debounced search (300ms)
- Results list with muscle badges
- Tap to add to workout

State management: Zustand workoutStore
- Auto-save each set to API immediately on checkmark
- If offline/error: show retry button

Use Framer Motion for set completion animation.
```

#### D3. Charts components
```
Create Recharts-based chart components for FitTracker analytics.
TypeScript, Tailwind CSS.

1. StrengthProgressChart:
Props: { data: [{date: string, max_weight_kg: number}], exerciseName: string }
Recharts LineChart with:
- Smooth curve (type="monotone")
- Custom tooltip showing "85kg — Jan 15, 2025"
- PR marker (star icon on highest point)
- Responsive container

2. VolumeBarChart:
Props: { data: [{date: string, volume_kg: number}] }
BarChart with gradient fill, responsive.

3. CalendarHeatmap:
Props: { calendar: [{date: string, has_workout: boolean}] }
365-day grid (like GitHub contributions)
Green for workout days, dark gray for rest
Month labels on top
Tooltip on hover

4. MuscleGroupChart:
Props: { data: [{muscle_group: string, sets_count: number, percentage: number}] }
Horizontal bar chart with muscle group labels
Color coded by muscle group

5. BodyWeightChart:
Props: { data: [{date: string, weight_kg: number}] }
AreaChart with gradient fill
Optional goal line (target_weight_kg prop)
Responsive

All charts: dark background, use FitTracker color palette (#3B82F6 primary, #F97316 accent).
```

---

### PROMPT SET E — Admin Panel

#### E1. Admin base setup
```
Create FastAPI admin panel with Jinja2 templates + Bootstrap 5.

Setup:
- Mount templates folder: templates/admin/
- Admin router prefix: /admin
- Session-based auth (not JWT): use itsdangerous for secure cookie signing
  SESSION_SECRET in .env
- Middleware: check admin session on all /admin/* routes (except /admin/login)
- If not authenticated: redirect to /admin/login

Session data: { admin_id: int, admin_email: str, logged_in_at: str }
Session expiry: 4 hours (check on each request)

base.html template:
- Bootstrap 5 dark theme (bg-dark text-light)
- Sidebar: Logo | Dashboard | Users | Exercises | Reports (badge) | Analytics | Logs | Logout
- Flash messages block (success/error/warning)
- {% block content %}{% endblock %}

Routes:
- GET /admin/login → render login form
- POST /admin/login → verify email+password, check role==admin, set session, redirect to dashboard
- GET /admin/logout → clear session, redirect to login
- GET /admin/dashboard → show stats (use admin analytics query)
```

---

## 🐛 GEMINI CLI PROMPTS

### For debugging errors
```
I'm getting this error in my FastAPI/SQLAlchemy project:

Error: [PASTE EXACT ERROR AND STACK TRACE]

Code file: [PASTE RELEVANT CODE]

Database model: [PASTE MODEL IF RELEVANT]

Questions:
1. What exactly causes this error?
2. How do I fix it?
3. How do I prevent this in future code?
```

### For complex SQL queries
```
I need an efficient PostgreSQL query for FitTracker.

Database tables: [describe relevant tables]

Goal: [explain what data you need]

Current attempt (if any): [paste your SQLAlchemy code]

Requirements:
- Must be performant (< 100ms for 10k users)
- Use SQLAlchemy 2.0 async syntax
- Handle edge cases (empty data, user with no workouts)
```

### For performance issues
```
FitTracker endpoint is slow: [endpoint name]

Current response time: [Xms]
Database size: [approx records]

Query being executed: [EXPLAIN ANALYZE output if available]

How to optimize this? Options I'm considering:
1. Add index on [column]
2. Use cache
3. Denormalize data
Which is best and why?
```

---

## 💬 OLLAMA PROMPTS (Quick Questions)

Use qwen3:8b for:
```
# Understanding a concept
"Explain SQLAlchemy relationship lazy loading vs eager loading with simple example"

# Quick syntax
"How do I write async for loop in Python for SQLAlchemy results?"

# React hooks
"When should I use useMemo vs useCallback in React?"

# Tailwind
"What Tailwind classes give a glassmorphism card effect?"

# PostgreSQL
"What's the difference between INNER JOIN and LEFT JOIN? Simple example."
```

---

## 📞 WHEN TO COME TO CLAUDE (ME)

Come to me when:
```
1. BEFORE starting a new major module:
   "I'm about to build [module]. Here's my plan: [describe approach].
   Is this the right approach? Any security concerns?"

2. AFTER building a module for security review:
   "Finished [module]. Here's the key code: [paste].
   Check against FT_05_SECURITY_RULES.md."

3. Architecture decision:
   "Should I [option A] or [option B]? 
   Context: [explain your situation]"

4. Stuck after trying Gemini + Ollama for 30+ min:
   "Spent 30 min on this. Codex gave me [solution], 
   Gemini said [solution], still broken. Here's full code: [paste]"

5. Weekly review (Friday):
   "Week X done. Here's what I built: [list].
   Here's what I'm unsure about: [questions].
   Plan for next week: [your plan].
   Is this correct?"
```

---

## ⚡ EFFICIENCY RULES FOR AI USAGE

1. **Paste context first** — always paste the relevant existing code when asking for new code that should follow patterns
2. **One prompt = one module** — don't ask for everything at once
3. **Review before running** — read generated code before copy-pasting, look for obvious issues
4. **Reference the schema** — paste table definitions when asking for queries
5. **Specify the pattern** — "follow the same pattern as WorkoutSession model"
6. **Ask for explanation** — end prompts with "Explain the key decisions you made"
7. **Test immediately** — run the generated code before moving to next module
8. **Save working prompts** — if a prompt generated great code, save it for reuse
