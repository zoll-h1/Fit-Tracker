# FT_02 — BACKEND API SPECIFICATION
# FitTracker | FastAPI + PostgreSQL

---

## ⚙️ TECH STACK

| Layer        | Technology                          |
|--------------|-------------------------------------|
| Framework    | FastAPI 0.110+                      |
| ORM          | SQLAlchemy 2.0 (async)              |
| Migrations   | Alembic                             |
| Database     | PostgreSQL 15                       |
| Auth         | JWT (access 30min + refresh 7d)     |
| Validation   | Pydantic v2                         |
| Files        | Local filesystem + optional S3      |
| Task Queue   | APScheduler (background jobs)       |
| Cache        | Redis (optional, for leaderboards)  |
| Docs         | Auto Swagger at /docs               |

---

## 📁 PROJECT STRUCTURE

```
backend/
├── app/
│   ├── main.py                    # App entry point, CORS, routers
│   ├── database.py                # Async SQLAlchemy engine
│   ├── dependencies.py            # Shared deps (get_db, get_current_user)
│   ├── config.py                  # Settings from .env
│   │
│   ├── models/
│   │   ├── __init__.py
│   │   ├── user.py
│   │   ├── workout.py
│   │   ├── exercise.py
│   │   ├── body_metrics.py
│   │   ├── nutrition.py
│   │   ├── social.py
│   │   ├── gamification.py
│   │   └── notification.py
│   │
│   ├── schemas/
│   │   ├── __init__.py
│   │   ├── auth.py
│   │   ├── user.py
│   │   ├── workout.py
│   │   ├── exercise.py
│   │   ├── body_metrics.py
│   │   ├── nutrition.py
│   │   ├── social.py
│   │   └── analytics.py
│   │
│   ├── routers/
│   │   ├── auth.py
│   │   ├── users.py
│   │   ├── workouts.py
│   │   ├── exercises.py
│   │   ├── exercise_library.py
│   │   ├── body_metrics.py
│   │   ├── nutrition.py
│   │   ├── social.py
│   │   ├── analytics.py
│   │   ├── gamification.py
│   │   ├── notifications.py
│   │   └── admin.py
│   │
│   ├── services/
│   │   ├── auth_service.py
│   │   ├── workout_service.py
│   │   ├── analytics_service.py
│   │   ├── gamification_service.py
│   │   ├── notification_service.py
│   │   └── file_service.py
│   │
│   ├── core/
│   │   ├── security.py            # JWT, password hashing
│   │   ├── exceptions.py          # Custom HTTP exceptions
│   │   └── scheduler.py           # APScheduler jobs
│   │
│   └── utils/
│       ├── validators.py
│       └── helpers.py
│
├── alembic/
│   ├── versions/
│   └── env.py
├── uploads/
│   ├── avatars/
│   ├── workouts/
│   └── meals/
├── tests/
├── .env
├── .env.example
├── requirements.txt
├── Dockerfile
└── alembic.ini
```

---

## 🔐 MODULE 1 — AUTHENTICATION

### Endpoints

| Method | Path                        | Auth | Description              |
|--------|-----------------------------|------|--------------------------|
| POST   | /api/auth/register          | No   | Register new user        |
| POST   | /api/auth/login             | No   | Login, get tokens        |
| POST   | /api/auth/refresh           | No   | Refresh access token     |
| POST   | /api/auth/logout            | Yes  | Invalidate refresh token |
| POST   | /api/auth/forgot-password   | No   | Send reset email         |
| POST   | /api/auth/reset-password    | No   | Reset with token         |
| POST   | /api/auth/verify-email      | No   | Verify email address     |
| GET    | /api/auth/me                | Yes  | Get current user info    |

### Request/Response Examples

```python
# Register
POST /api/auth/register
{
  "username": "strongjohn",
  "email": "john@example.com",
  "password": "SecurePass123!",
  "full_name": "John Doe",
  "date_of_birth": "2000-05-15",
  "gender": "male",
  "unit_system": "metric"
}

# Response
{
  "access_token": "eyJ...",
  "refresh_token": "eyJ...",
  "token_type": "bearer",
  "user": { "id": 1, "username": "strongjohn", "email": "john@example.com" }
}

# Login
POST /api/auth/login
{ "email": "john@example.com", "password": "SecurePass123!" }
```

### CODEX PROMPT — Auth Module
```
Create FastAPI authentication module with PostgreSQL/SQLAlchemy:

User model fields:
- id, username (unique), email (unique), password_hash
- full_name, date_of_birth, gender (male/female/other)
- unit_system (metric/imperial), timezone
- bio, avatar_url, height_cm, weight_kg
- role (user/premium/trainer/admin)
- is_active, is_email_verified
- created_at, last_active_at

Auth logic:
- bcrypt password hashing (12 rounds)
- JWT access token (30 min expiry)
- JWT refresh token (7 days expiry, stored in DB)
- POST /api/auth/register (validate unique email+username, hash pw, create user)
- POST /api/auth/login (verify credentials, return both tokens)
- POST /api/auth/refresh (validate refresh token, issue new access)
- POST /api/auth/logout (delete refresh token from DB)
- GET /api/auth/me (return current user, requires valid access token)
- Dependency: get_current_user(token: str = Depends(oauth2_scheme))
- Custom exception handlers: 401 Unauthorized, 403 Forbidden
Include Pydantic schemas for all requests and responses.
```

---

## 💪 MODULE 2 — EXERCISE LIBRARY

### Endpoints

| Method | Path                              | Auth  | Description                  |
|--------|-----------------------------------|-------|------------------------------|
| GET    | /api/exercise-library             | No    | List exercises (filter/search)|
| GET    | /api/exercise-library/{id}        | No    | Exercise detail              |
| GET    | /api/exercise-library/categories  | No    | List muscle group categories |
| POST   | /api/exercise-library             | Admin | Create exercise              |
| PUT    | /api/exercise-library/{id}        | Admin | Update exercise              |
| GET    | /api/exercise-library/search      | No    | Full-text search             |
| POST   | /api/exercises/custom             | Yes   | Create user custom exercise  |
| GET    | /api/exercises/custom             | Yes   | List user's custom exercises |

### CODEX PROMPT — Exercise Library
```
Create FastAPI exercise library module:

ExerciseLibrary model:
- id, name, slug (unique)
- muscle_primary (array), muscle_secondary (array)
- equipment (array), force_type (push/pull/static)
- difficulty (beginner/intermediate/advanced)
- category (strength/cardio/flexibility/balance)
- description, instructions (step-by-step text)
- video_url, image_url
- is_custom (false = seeded, true = user created)
- created_by (user_id, null for global)
- met_value (metabolic equivalent for calorie calc)

Endpoints:
- GET /api/exercise-library (pagination, filter by muscle/equipment/category/difficulty)
- GET /api/exercise-library/search?q=push+up (full-text search on name+description)
- GET /api/exercise-library/{id}
- POST /api/exercises/custom (auth, user's own custom exercise)
- GET /api/exercises/custom (auth, user's custom exercises)
Include seed data for 50 common exercises.
```

---

## 🏋️ MODULE 3 — WORKOUTS

### Endpoints

| Method | Path                                     | Auth | Description                     |
|--------|------------------------------------------|------|---------------------------------|
| POST   | /api/workouts                            | Yes  | Create/start workout session    |
| GET    | /api/workouts                            | Yes  | List user's workouts (history)  |
| GET    | /api/workouts/{id}                       | Yes  | Workout detail with exercises   |
| PUT    | /api/workouts/{id}                       | Yes  | Update workout (add notes etc.) |
| DELETE | /api/workouts/{id}                       | Yes  | Delete workout                  |
| POST   | /api/workouts/{id}/finish                | Yes  | Mark workout as complete        |
| POST   | /api/workouts/{id}/exercises             | Yes  | Add exercise to workout         |
| PUT    | /api/workouts/{id}/exercises/{ex_id}     | Yes  | Update exercise in workout      |
| DELETE | /api/workouts/{id}/exercises/{ex_id}     | Yes  | Remove exercise from workout    |
| POST   | /api/workouts/{id}/exercises/{ex_id}/sets| Yes  | Log a set                       |
| PUT    | /api/workouts/sets/{set_id}              | Yes  | Update a set                    |
| DELETE | /api/workouts/sets/{set_id}              | Yes  | Delete a set                    |
| GET    | /api/workouts/templates                  | Yes  | List user's workout templates   |
| POST   | /api/workouts/templates                  | Yes  | Save workout as template        |
| POST   | /api/workouts/from-template/{tpl_id}     | Yes  | Start workout from template     |

### CODEX PROMPT — Workouts Module
```
Create FastAPI workouts module with full session tracking:

Models:
WorkoutSession: id, user_id, template_id (nullable), name, notes,
  started_at, finished_at, duration_seconds, total_volume_kg,
  total_sets, total_reps, calories_burned, status (in_progress/completed/cancelled)

WorkoutExercise: id, session_id, exercise_library_id, exercise_order,
  notes, rest_seconds

WorkoutSet: id, workout_exercise_id, set_number, set_type (normal/warmup/dropset/failure),
  reps, weight_kg, duration_seconds (for timed), distance_km (for cardio),
  rpe (1-10), completed, completed_at

WorkoutTemplate: id, user_id, name, description, is_public,
  estimated_duration_min, times_used, last_used_at

TemplateExercise: id, template_id, exercise_library_id, exercise_order,
  target_sets, target_reps, target_weight_kg, rest_seconds, notes

Business logic:
- Auto-calculate total_volume_kg (sum of weight*reps across all sets)
- Auto-calculate duration_seconds when workout finished
- Estimate calories_burned using MET value * weight_kg * hours
- Personal records: detect if any set is a PR for that exercise
- Update user XP when workout completed (services/gamification_service.py)
- All endpoints require ownership checks
Include full CRUD for sessions, exercises within session, and sets.
```

---

## 📏 MODULE 4 — BODY METRICS

### Endpoints

| Method | Path                           | Auth | Description                |
|--------|--------------------------------|------|----------------------------|
| POST   | /api/body-metrics              | Yes  | Log body measurement       |
| GET    | /api/body-metrics              | Yes  | History (paginated)        |
| GET    | /api/body-metrics/latest       | Yes  | Most recent entry          |
| DELETE | /api/body-metrics/{id}         | Yes  | Delete entry               |
| GET    | /api/body-metrics/progress     | Yes  | Progress chart data        |
| POST   | /api/body-metrics/goals        | Yes  | Set body goals             |
| GET    | /api/body-metrics/goals        | Yes  | Get current goals          |

### CODEX PROMPT — Body Metrics
```
Create FastAPI body metrics module:

BodyMetric model:
- id, user_id, logged_at
- weight_kg, body_fat_percentage, muscle_mass_kg
- bmi (auto-calculated from weight + user height)
- waist_cm, chest_cm, hips_cm, bicep_cm, thigh_cm
- notes, photo_url (optional progress photo)

BodyGoal model:
- id, user_id, metric_type (weight/body_fat/muscle_mass)
- target_value, target_date, created_at, is_achieved, achieved_at

Endpoints:
- POST /api/body-metrics (auto-calc BMI, auto-check if goal achieved)
- GET /api/body-metrics (paginated, date range filter)
- GET /api/body-metrics/latest (most recent single entry)
- GET /api/body-metrics/progress (return array for chart: {date, value} for each metric)
- POST /api/body-metrics/goals (set or update goal)
- GET /api/body-metrics/goals (all active goals with progress %)
Progress endpoint supports: ?metric=weight&from=2025-01-01&to=2025-12-31
```

---

## 🥗 MODULE 5 — NUTRITION

### Endpoints

| Method | Path                              | Auth | Description              |
|--------|-----------------------------------|------|--------------------------|
| POST   | /api/nutrition/meals              | Yes  | Log a meal               |
| GET    | /api/nutrition/meals              | Yes  | Meal history             |
| GET    | /api/nutrition/meals/today        | Yes  | Today's meals            |
| DELETE | /api/nutrition/meals/{id}         | Yes  | Delete meal              |
| GET    | /api/nutrition/summary            | Yes  | Daily summary            |
| POST   | /api/nutrition/goals              | Yes  | Set nutrition goals      |
| GET    | /api/nutrition/goals              | Yes  | Get nutrition goals      |
| GET    | /api/nutrition/foods/search       | No   | Search food database     |
| GET    | /api/nutrition/foods/{id}         | No   | Food detail              |
| POST   | /api/nutrition/foods/custom       | Yes  | Add custom food          |

### CODEX PROMPT — Nutrition Module
```
Create FastAPI nutrition tracking module:

FoodItem model (global database):
- id, name, brand (nullable)
- calories_per_100g, protein_per_100g, carbs_per_100g
- fat_per_100g, fiber_per_100g, sugar_per_100g
- is_custom (false=seeded), created_by (user_id, null if global)
- barcode (optional, for scanner feature)

MealLog model:
- id, user_id, logged_at, meal_type (breakfast/lunch/dinner/snack)
- food_item_id, quantity_g
- calories (auto-calc), protein_g, carbs_g, fat_g
- notes

NutritionGoal model:
- id, user_id
- calories_target, protein_target_g, carbs_target_g, fat_target_g
- water_target_ml

Endpoints:
- POST /api/nutrition/meals (auto-calculate macros from quantity_g)
- GET /api/nutrition/meals/today (all today's meals, sum of calories/macros)
- GET /api/nutrition/summary?date=2025-01-01 (daily totals vs goals)
- GET /api/nutrition/foods/search?q=chicken+breast (search by name)
- POST /api/nutrition/foods/custom (user creates their own food item)
Seed 200 common foods.
```

---

## 👥 MODULE 6 — SOCIAL

### Endpoints

| Method | Path                              | Auth | Description                    |
|--------|-----------------------------------|------|--------------------------------|
| POST   | /api/social/follow/{user_id}      | Yes  | Follow a user                  |
| DELETE | /api/social/follow/{user_id}      | Yes  | Unfollow a user                |
| GET    | /api/social/followers             | Yes  | Get my followers               |
| GET    | /api/social/following             | Yes  | Get who I'm following          |
| GET    | /api/users/{id}/profile           | No   | Public profile                 |
| GET    | /api/social/feed                  | Yes  | Activity feed                  |
| POST   | /api/social/feed/{activity_id}/like | Yes | Like an activity             |
| POST   | /api/social/feed/{activity_id}/comment | Yes | Comment on activity      |
| GET    | /api/social/challenges            | Yes  | List challenges                |
| POST   | /api/social/challenges            | Yes  | Create challenge               |
| POST   | /api/social/challenges/{id}/join  | Yes  | Join challenge                 |
| GET    | /api/social/leaderboard           | Yes  | Global leaderboard             |

### CODEX PROMPT — Social Module
```
Create FastAPI social module for fitness app:

Models:
Follow: id, follower_id, following_id, created_at (UNIQUE follower+following)

ActivityFeed: id, user_id, type (workout_completed/pr_achieved/goal_reached/challenge_won),
  workout_id (nullable), body_metric_id (nullable), achievement_id (nullable),
  description, is_public, created_at

FeedLike: id, activity_id, user_id, created_at (UNIQUE)
FeedComment: id, activity_id, user_id, text, created_at

Challenge: id, creator_id, name, description, challenge_type (total_workouts/total_volume/streak),
  target_value, start_date, end_date, is_public, max_participants, status

ChallengeParticipant: id, challenge_id, user_id, current_value, rank, joined_at

Endpoints:
- POST /api/social/follow/{user_id} (cannot follow self)
- DELETE /api/social/follow/{user_id}
- GET /api/social/feed (paginated, show followed users' activities, newest first)
- POST /api/social/feed/{id}/like (toggle like)
- GET /api/social/leaderboard?type=weekly_workouts&limit=50 (top users)
- GET /api/social/challenges (active challenges, filter joinable)
- POST /api/social/challenges/{id}/join
Auto-post to ActivityFeed when: workout completed, PR achieved, goal reached.
```

---

## 🏆 MODULE 7 — GAMIFICATION

### Endpoints

| Method | Path                               | Auth | Description              |
|--------|------------------------------------|------|--------------------------|
| GET    | /api/gamification/profile          | Yes  | XP, level, badges        |
| GET    | /api/gamification/achievements     | Yes  | All achievements          |
| GET    | /api/gamification/achievements/my  | Yes  | User's earned ones       |
| GET    | /api/gamification/leaderboard      | Yes  | XP-based leaderboard     |
| GET    | /api/gamification/streaks          | Yes  | Current & best streaks   |

### CODEX PROMPT — Gamification
```
Create FastAPI gamification module:

Models:
UserXP: id, user_id (unique), total_xp, current_level, current_streak_days,
  longest_streak_days, last_workout_date, weekly_xp, monthly_xp

AchievementDefinition: id, key (unique), name, description, icon_name,
  category (workout/strength/consistency/social/nutrition/body),
  xp_reward, requirement_type, requirement_value

UserAchievement: id, user_id, achievement_id, earned_at, notified

XP Awards:
- Complete workout: +50 XP
- PR achieved: +100 XP
- 7-day streak: +200 XP
- 30-day streak: +500 XP
- Goal reached: +150 XP
- Log meal: +10 XP
- Log body metric: +20 XP
- Follow someone: +5 XP

Levels:
1: 0 XP, 2: 500, 3: 1200, 4: 2500, 5: 5000, 6: 9000, 7: 15000, 8: 25000, 9: 40000, 10: 60000

Service: gamification_service.py
- award_xp(user_id, amount, reason) → check level up, return event
- check_achievements(user_id, event_type) → loop definitions, award if qualified
- update_streak(user_id) → update streak, award streak achievements

Seed 40 achievements covering all categories.
```

---

## 📊 MODULE 8 — ANALYTICS

### Endpoints

| Method | Path                               | Auth | Description                    |
|--------|------------------------------------|------|--------------------------------|
| GET    | /api/analytics/workouts            | Yes  | Workout frequency charts       |
| GET    | /api/analytics/strength            | Yes  | Strength progress per exercise |
| GET    | /api/analytics/volume              | Yes  | Volume over time               |
| GET    | /api/analytics/muscles             | Yes  | Muscle group distribution      |
| GET    | /api/analytics/body                | Yes  | Body metric trends             |
| GET    | /api/analytics/nutrition           | Yes  | Nutrition adherence            |
| GET    | /api/analytics/personal-records    | Yes  | All-time PRs                   |
| GET    | /api/analytics/streak              | Yes  | Streak calendar data           |
| GET    | /api/analytics/dashboard           | Yes  | Dashboard summary stats        |

### CODEX PROMPT — Analytics
```
Create FastAPI analytics module:

All endpoints require auth (user_id from token).
All support ?period=7d|30d|90d|1y|all and ?from=&to= date range.

Endpoints:
GET /api/analytics/dashboard → {
  this_week_workouts, this_month_workouts, current_streak,
  total_workouts, total_volume_kg, avg_workout_duration_min,
  recent_prs: [{exercise, weight, date}],
  this_week_calories, goal_adherence_pct
}

GET /api/analytics/strength?exercise_id=1&period=90d → {
  chart: [{date, max_weight_kg, total_volume}],
  pr_weight: 100, pr_date: "2025-01-01"
}

GET /api/analytics/muscles?period=30d → {
  distribution: [{muscle_group, sets_count, percentage}]
}

GET /api/analytics/personal-records → {
  records: [{exercise_id, exercise_name, weight_kg, reps, achieved_at}]
}

GET /api/analytics/streak → {
  current_streak: 12, longest_streak: 30,
  calendar: [{date, has_workout, is_rest_day}] for last 365 days
}

Use SQLAlchemy aggregate queries (func.sum, func.count, func.max).
```

---

## 🔔 MODULE 9 — NOTIFICATIONS

### Endpoints

| Method | Path                                | Auth | Description           |
|--------|-------------------------------------|------|-----------------------|
| GET    | /api/notifications                  | Yes  | List notifications    |
| GET    | /api/notifications/unread-count     | Yes  | Unread count          |
| PUT    | /api/notifications/{id}/read        | Yes  | Mark one as read      |
| PUT    | /api/notifications/read-all         | Yes  | Mark all read         |
| DELETE | /api/notifications/{id}             | Yes  | Delete notification   |
| GET    | /api/notifications/settings         | Yes  | Notification settings |
| PUT    | /api/notifications/settings         | Yes  | Update settings       |

### CODEX PROMPT — Notifications
```
Create FastAPI notifications module:

Notification model:
- id, user_id, type, title, body, is_read, created_at
- action_url (nullable, deep link)
- related_id, related_type

Types:
- workout_reminder, streak_warning (streak about to break!)
- achievement_earned, level_up
- pr_achieved, goal_reached
- new_follower, feed_like, feed_comment
- challenge_joined, challenge_completed, challenge_result

NotificationSettings model (1-per-user):
- user_id, workout_reminders, streak_alerts, achievement_alerts
- social_alerts, challenge_alerts, email_notifications

Endpoints:
- GET /api/notifications (paginated, filter unread)
- PUT /api/notifications/read-all (mark all as read)
- GET /api/notifications/unread-count (quick count for badge)
- GET/PUT /api/notifications/settings

Service: notification_service.py
- create_notification(user_id, type, title, body, action_url=None) 
  → check user settings before creating
- streak_warning_job() → APScheduler, runs daily at 8PM
  → find users with streak ≥ 3 but no workout today, send warning
```

---

## 🛡️ MODULE 10 — ADMIN API

> Full admin panel is documented in FT_04_ADMIN_PANEL.md
> This covers the API endpoints only.

### Endpoints

| Method | Path                               | Auth  | Description               |
|--------|------------------------------------|-------|---------------------------|
| GET    | /api/admin/dashboard               | Admin | Platform statistics       |
| GET    | /api/admin/users                   | Admin | List all users            |
| GET    | /api/admin/users/{id}              | Admin | User detail               |
| PUT    | /api/admin/users/{id}/role         | Admin | Change user role          |
| POST   | /api/admin/users/{id}/suspend      | Admin | Suspend user              |
| POST   | /api/admin/users/{id}/activate     | Admin | Reactivate user           |
| GET    | /api/admin/reports                 | Admin | Pending reports           |
| POST   | /api/admin/reports/{id}/resolve    | Admin | Resolve report            |
| GET    | /api/admin/exercises               | Admin | Manage exercise library   |
| POST   | /api/admin/exercises               | Admin | Add exercise              |
| PUT    | /api/admin/exercises/{id}          | Admin | Edit exercise             |
| GET    | /api/admin/analytics               | Admin | Platform-wide analytics   |
| GET    | /api/admin/logs                    | Admin | Admin action logs         |

---

## 📤 FILE UPLOAD SERVICE

### Rules (NON-NEGOTIABLE)
```python
ALLOWED_TYPES = ["image/jpeg", "image/png", "image/webp"]
MAX_FILE_SIZE_MB = 5
MAX_AVATAR_SIZE_MB = 2
AVATAR_PATH = "uploads/avatars/"
WORKOUT_PHOTO_PATH = "uploads/workouts/"
MEAL_PHOTO_PATH = "uploads/meals/"

# Always validate MIME type (not just extension!)
# Resize images on upload (max 1200px)
# Generate thumbnail (300px) for listing views
# Use UUID for filenames (never user-provided names)
```

### CODEX PROMPT — File Service
```
Create file upload service in FastAPI:

- POST /api/users/avatar (upload profile picture)
  → validate image type + size
  → resize to max 800x800px using Pillow
  → generate 150x150 thumbnail
  → save both to uploads/avatars/{uuid}_full.jpg and {uuid}_thumb.jpg
  → update user.avatar_url in DB
  → delete old avatar files

- POST /api/workouts/{id}/photo (attach photo to workout)
  → validate, resize to 1200px max
  → save to uploads/workouts/
  → return public URL

File serving:
- Mount /uploads as static files in FastAPI main.py
- URL format: http://host/uploads/avatars/uuid_full.jpg

Security:
- Never trust Content-Type header alone
- Use python-magic for real MIME detection
- Strip EXIF metadata from photos (using Pillow)
```

---

## 🔧 BACKGROUND JOBS (APScheduler)

```python
# scheduler.py — runs on app startup

from apscheduler.schedulers.asyncio import AsyncIOScheduler

scheduler = AsyncIOScheduler()

# Daily at 8 PM — streak warning
@scheduler.scheduled_job("cron", hour=20)
async def streak_warning_job():
    # Find users: streak >= 3, no workout today
    # Send streak_warning notification

# Daily at midnight — reset daily counters
@scheduler.scheduled_job("cron", hour=0, minute=0)
async def daily_reset_job():
    # Update weekly/monthly XP if needed
    # Archive old notifications (older than 60 days)

# Weekly — leaderboard calculation
@scheduler.scheduled_job("cron", day_of_week="mon", hour=0)
async def weekly_leaderboard_job():
    # Calculate weekly XP ranking
    # Award weekly challenge results
    # Reset weekly_xp counter
```

---

## 🌱 SEED DATA REQUIRED

Run `python seed.py` to populate:
- 50+ exercises (exercise library)
- 8 muscle groups
- 10 equipment types
- 200+ food items (nutrition)
- 40 achievement definitions
- 5 default workout templates
- 1 admin user (admin@fittracker.com / Admin123!)
- 3 demo users with workout history

---

## ⚠️ STRICT RULES FOR CODEX

1. Every endpoint that touches user data MUST verify ownership
2. Never return password_hash in any response
3. Use async def for all endpoints and DB calls
4. Always use Pydantic schemas — never return raw SQLAlchemy objects
5. Paginate ALL list endpoints (default page_size=20, max=100)
6. Log all admin actions to admin_logs table
7. Return consistent error format: `{"detail": "message", "code": "ERROR_CODE"}`
8. Use database transactions for multi-step operations
9. Input validation on ALL fields — no trusting user input
10. Rate limiting on auth endpoints (5 attempts per minute)
