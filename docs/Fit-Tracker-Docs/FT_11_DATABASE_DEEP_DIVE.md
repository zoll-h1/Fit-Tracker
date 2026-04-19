# FT_11_DATABASE_DEEP_DIVE.md
# FitTracker | Complete Database Architecture

> This is the definitive answer to "what database and why".
> Covers: choice rationale, full schema, scaling strategy,
> indexing, migrations, backups, and future-proofing.

---

## 🎯 THE ANSWER: WHY POSTGRESQL

FitTracker uses **PostgreSQL 15** as its primary database. Here's exactly why:

### Why NOT MySQL
```
MySQL was considered. Rejected because:

❌ Array columns: MySQL doesn't support native arrays
   (muscle_primary TEXT[] — PostgreSQL feature, critical for exercise library)

❌ JSONB: MySQL has JSON but NO GIN indexing on it
   (We use JSONB + GIN index for tags, boost effects, achievement requirements)

❌ Full-text search: MySQL FTS is inferior
   (Exercise search, food search, notes search all benefit from PostgreSQL tsvector)

❌ Window functions: MySQL support is weaker
   (Analytics queries use RANK(), LAG(), PARTITION BY — PostgreSQL is best at these)

❌ Extensions: PostgreSQL has pg_stat_statements, pg_trgm, uuid-ossp
   (Trigram search, UUID generation, query analysis — all PostgreSQL advantages)

✅ MySQL would work. But PostgreSQL makes 30% of queries simpler.
```

### Why NOT MongoDB/NoSQL
```
❌ FitTracker data is highly relational:
   User → Workouts → Exercises → Sets → PRs
   Relationships are complex and need JOIN efficiency

❌ ACID transactions are critical:
   "Log set + check PR + award XP + create notification" must be atomic
   MongoDB multi-document transactions exist but add complexity

❌ Analytics would be painful:
   "Sum of volume per muscle group per week" = simple SQL
   Same in MongoDB = MapReduce or complex aggregation pipelines

✅ MongoDB would work for simple CRUD. FitTracker is NOT simple CRUD.
```

### Why NOT SQLite
```
❌ SQLite is single-writer — concurrent users would block each other
❌ No connection pooling
❌ Missing array, JSONB, advanced FTS
✅ SQLite is fine for mobile local storage (e.g. Flutter app offline cache)
```

### Why PostgreSQL Wins
```
✅ Native arrays → exercise muscles stored cleanly
✅ JSONB with GIN index → flexible config without schema changes
✅ Full-text search → exercise/food/notes search built-in
✅ Window functions → clean analytics queries
✅ pg_trgm → fuzzy search ("bech press" finds "bench press")
✅ UUID support → future-proof IDs if you need distributed system
✅ Row Level Security → if you ever go multi-tenant
✅ Logical replication → read replicas when you scale
✅ PostGIS extension → if you add gym location features
✅ Best cloud support → Railway, Render, Supabase, RDS all support it
✅ Used by: Instagram, Spotify, GitLab, Twitch, Shopify
```

---

## 🗄️ COMPLETE SCHEMA (All Tables)

### USERS & AUTH

```sql
-- Core user table
CREATE TABLE users (
    id SERIAL PRIMARY KEY,
    username VARCHAR(50) UNIQUE NOT NULL,
    email VARCHAR(255) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    full_name VARCHAR(200),
    
    -- Profile
    date_of_birth DATE,
    gender VARCHAR(10),                     -- 'male', 'female', 'other'
    bio TEXT,
    avatar_url VARCHAR(500),
    
    -- Physical
    height_cm NUMERIC(5,1),
    weight_kg NUMERIC(6,2),                 -- starting weight (not tracked here, use body_metrics)
    
    -- Preferences
    unit_system VARCHAR(10) DEFAULT 'metric',  -- 'metric', 'imperial'
    timezone VARCHAR(50) DEFAULT 'UTC',
    language VARCHAR(10) DEFAULT 'en',
    
    -- Access
    role VARCHAR(20) DEFAULT 'user',        -- 'user', 'premium', 'trainer', 'admin'
    is_active BOOLEAN DEFAULT TRUE,
    is_email_verified BOOLEAN DEFAULT FALSE,
    
    -- Timestamps
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW(),
    last_active_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX idx_users_email ON users(email);
CREATE INDEX idx_users_username ON users(username);
CREATE INDEX idx_users_role ON users(role);

-- JWT refresh tokens (stored hashed, not plaintext)
CREATE TABLE refresh_tokens (
    id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    token_hash VARCHAR(255) NOT NULL,       -- bcrypt hash of the token
    expires_at TIMESTAMPTZ NOT NULL,
    is_revoked BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    device_info TEXT                        -- optional: "iPhone 15, iOS 17"
);

CREATE INDEX idx_refresh_tokens_user ON refresh_tokens(user_id);
CREATE INDEX idx_refresh_tokens_hash ON refresh_tokens(token_hash);

-- Email verification and password reset
CREATE TABLE user_tokens (
    id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    token_type VARCHAR(30) NOT NULL,        -- 'email_verify', 'password_reset'
    token_hash VARCHAR(255) NOT NULL,
    expires_at TIMESTAMPTZ NOT NULL,
    is_used BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMPTZ DEFAULT NOW()
);
```

---

### EXERCISE LIBRARY

```sql
-- Global exercise database (seeded + user-created custom)
CREATE TABLE exercise_library (
    id SERIAL PRIMARY KEY,
    name VARCHAR(200) NOT NULL,
    slug VARCHAR(200) UNIQUE,               -- URL-friendly: "barbell-bench-press"
    
    -- Classification
    category VARCHAR(30) NOT NULL,          -- 'strength', 'cardio', 'flexibility', 'balance', 'sport'
    force_type VARCHAR(20),                 -- 'push', 'pull', 'static', 'hinge', 'squat', 'carry'
    difficulty VARCHAR(20),                 -- 'beginner', 'intermediate', 'advanced'
    
    -- Muscles (PostgreSQL arrays)
    muscle_primary TEXT[] NOT NULL DEFAULT '{}',
    -- ["chest", "triceps"] — primary movers
    muscle_secondary TEXT[] DEFAULT '{}',
    -- ["shoulders", "core"] — stabilizers
    
    -- Equipment needed
    equipment TEXT[] DEFAULT '{}',
    -- ["barbell", "bench"] or [] for bodyweight
    
    -- Metabolic equivalent (for calorie calculation)
    met_value NUMERIC(4,2) DEFAULT 5.0,
    
    -- Content
    description TEXT,
    instructions TEXT,                      -- step-by-step text
    tips TEXT,                              -- form cues, common mistakes
    video_url VARCHAR(500),
    image_url VARCHAR(500),
    
    -- Custom exercise support
    is_custom BOOLEAN DEFAULT FALSE,
    created_by INTEGER REFERENCES users(id) ON DELETE SET NULL,
    
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX idx_exercise_category ON exercise_library(category);
CREATE INDEX idx_exercise_muscles ON exercise_library USING GIN(muscle_primary);
CREATE INDEX idx_exercise_equipment ON exercise_library USING GIN(equipment);
CREATE INDEX idx_exercise_search ON exercise_library 
    USING GIN(to_tsvector('english', name || ' ' || COALESCE(description, '')));
CREATE INDEX idx_exercise_custom ON exercise_library(created_by) WHERE is_custom = TRUE;

-- Trigram index for fuzzy search ("bech press" finds "bench press")
CREATE EXTENSION IF NOT EXISTS pg_trgm;
CREATE INDEX idx_exercise_trgm ON exercise_library USING GIN(name gin_trgm_ops);
```

---

### WORKOUTS

```sql
-- A single workout session
CREATE TABLE workout_sessions (
    id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    template_id INTEGER REFERENCES workout_templates(id) ON DELETE SET NULL,
    
    name VARCHAR(200) NOT NULL DEFAULT 'Workout',
    notes TEXT,
    
    -- Timing
    started_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    finished_at TIMESTAMPTZ,
    duration_seconds INTEGER,              -- auto-calculated when finished
    
    -- Calculated stats (denormalized for fast read)
    total_volume_kg NUMERIC(10,2) DEFAULT 0,   -- sum(weight*reps) all sets
    total_sets INTEGER DEFAULT 0,
    total_reps INTEGER DEFAULT 0,
    calories_burned NUMERIC(8,2),
    
    -- Status
    status VARCHAR(20) DEFAULT 'in_progress',  -- 'in_progress', 'completed', 'cancelled'
    
    created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX idx_sessions_user ON workout_sessions(user_id);
CREATE INDEX idx_sessions_user_date ON workout_sessions(user_id, started_at DESC);
CREATE INDEX idx_sessions_status ON workout_sessions(user_id, status);

-- Exercises within a session (ordered list)
CREATE TABLE workout_exercises (
    id SERIAL PRIMARY KEY,
    session_id INTEGER NOT NULL REFERENCES workout_sessions(id) ON DELETE CASCADE,
    exercise_library_id INTEGER NOT NULL REFERENCES exercise_library(id),
    
    exercise_order INTEGER NOT NULL DEFAULT 0,
    rest_seconds INTEGER DEFAULT 90,
    notes TEXT,
    
    created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX idx_wex_session ON workout_exercises(session_id, exercise_order);

-- Individual sets within an exercise
CREATE TABLE workout_sets (
    id SERIAL PRIMARY KEY,
    workout_exercise_id INTEGER NOT NULL REFERENCES workout_exercises(id) ON DELETE CASCADE,
    
    set_number INTEGER NOT NULL,
    set_type VARCHAR(20) DEFAULT 'normal',  -- 'normal', 'warmup', 'dropset', 'failure', 'amrap'
    
    -- Strength tracking
    weight_kg NUMERIC(7,2),
    reps INTEGER,
    
    -- Cardio/timed tracking
    duration_seconds INTEGER,
    distance_km NUMERIC(7,3),
    
    -- Quality
    rpe INTEGER CHECK (rpe BETWEEN 1 AND 10),  -- Rate of Perceived Exertion
    
    -- State
    completed BOOLEAN DEFAULT FALSE,
    completed_at TIMESTAMPTZ,
    
    -- Estimated 1RM for this set (auto-calculated)
    estimated_1rm NUMERIC(7,2),
    
    created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX idx_sets_exercise ON workout_sets(workout_exercise_id);

-- Workout templates (saved workouts for reuse)
CREATE TABLE workout_templates (
    id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    
    name VARCHAR(200) NOT NULL,
    description TEXT,
    is_public BOOLEAN DEFAULT FALSE,
    estimated_duration_min INTEGER,
    difficulty VARCHAR(20),
    
    times_used INTEGER DEFAULT 0,
    last_used_at TIMESTAMPTZ,
    
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX idx_templates_user ON workout_templates(user_id);
CREATE INDEX idx_templates_public ON workout_templates(is_public) WHERE is_public = TRUE;

-- Exercises within a template
CREATE TABLE template_exercises (
    id SERIAL PRIMARY KEY,
    template_id INTEGER NOT NULL REFERENCES workout_templates(id) ON DELETE CASCADE,
    exercise_library_id INTEGER NOT NULL REFERENCES exercise_library(id),
    exercise_order INTEGER NOT NULL,
    target_sets INTEGER,
    target_reps INTEGER,
    target_weight_kg NUMERIC(7,2),
    rest_seconds INTEGER DEFAULT 90,
    notes TEXT
);

-- Personal records (best set for each exercise per user)
CREATE TABLE personal_records (
    id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    exercise_id INTEGER NOT NULL REFERENCES exercise_library(id),
    
    weight_kg NUMERIC(7,2),
    reps INTEGER,
    estimated_1rm NUMERIC(7,2),
    
    achieved_at TIMESTAMPTZ NOT NULL,
    workout_session_id INTEGER REFERENCES workout_sessions(id) ON DELETE SET NULL,
    
    UNIQUE(user_id, exercise_id)            -- one PR per exercise (auto-updated)
);

CREATE INDEX idx_prs_user ON personal_records(user_id);
CREATE INDEX idx_prs_user_exercise ON personal_records(user_id, exercise_id);
```

---

### BODY METRICS

```sql
CREATE TABLE body_metrics (
    id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    
    logged_at DATE NOT NULL DEFAULT CURRENT_DATE,
    
    -- Core measurements
    weight_kg NUMERIC(6,2),
    body_fat_percentage NUMERIC(5,2),
    muscle_mass_kg NUMERIC(6,2),
    bmi NUMERIC(5,2),                       -- auto-calculated from weight + user.height_cm
    
    -- Body measurements (cm)
    waist_cm NUMERIC(5,1),
    chest_cm NUMERIC(5,1),
    hips_cm NUMERIC(5,1),
    bicep_left_cm NUMERIC(5,1),
    bicep_right_cm NUMERIC(5,1),
    thigh_left_cm NUMERIC(5,1),
    thigh_right_cm NUMERIC(5,1),
    calf_left_cm NUMERIC(5,1),
    calf_right_cm NUMERIC(5,1),
    neck_cm NUMERIC(5,1),
    
    notes TEXT,
    photo_url VARCHAR(500),
    
    created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX idx_body_metrics_user_date ON body_metrics(user_id, logged_at DESC);

-- Goals for body metrics
CREATE TABLE body_goals (
    id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    metric_type VARCHAR(30) NOT NULL,       -- 'weight', 'body_fat', 'muscle_mass', 'waist', etc.
    target_value NUMERIC(8,2) NOT NULL,
    target_date DATE,
    is_achieved BOOLEAN DEFAULT FALSE,
    achieved_at TIMESTAMPTZ,
    created_at TIMESTAMPTZ DEFAULT NOW()
);
```

---

### NUTRITION

```sql
-- Global food database (seeded + user custom)
CREATE TABLE food_items (
    id SERIAL PRIMARY KEY,
    name VARCHAR(300) NOT NULL,
    brand VARCHAR(200),
    barcode VARCHAR(50) UNIQUE,             -- for barcode scanner feature
    
    -- Macros per 100g
    calories_per_100g NUMERIC(8,2) NOT NULL DEFAULT 0,
    protein_per_100g NUMERIC(7,2) DEFAULT 0,
    carbs_per_100g NUMERIC(7,2) DEFAULT 0,
    fat_per_100g NUMERIC(7,2) DEFAULT 0,
    fiber_per_100g NUMERIC(7,2) DEFAULT 0,
    sugar_per_100g NUMERIC(7,2) DEFAULT 0,
    
    is_custom BOOLEAN DEFAULT FALSE,
    created_by INTEGER REFERENCES users(id) ON DELETE SET NULL,
    
    created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX idx_food_search ON food_items 
    USING GIN(to_tsvector('english', name || ' ' || COALESCE(brand, '')));
CREATE INDEX idx_food_barcode ON food_items(barcode) WHERE barcode IS NOT NULL;
CREATE INDEX idx_food_trgm ON food_items USING GIN(name gin_trgm_ops);

-- Meal logs
CREATE TABLE meal_logs (
    id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    food_item_id INTEGER NOT NULL REFERENCES food_items(id),
    
    logged_at TIMESTAMPTZ DEFAULT NOW(),
    meal_type VARCHAR(20) NOT NULL,         -- 'breakfast', 'lunch', 'dinner', 'snack', 'pre_workout', 'post_workout'
    
    quantity_g NUMERIC(8,2) NOT NULL,
    
    -- Calculated (stored for fast retrieval)
    calories NUMERIC(8,2),
    protein_g NUMERIC(7,2),
    carbs_g NUMERIC(7,2),
    fat_g NUMERIC(7,2),
    
    notes TEXT
);

CREATE INDEX idx_meal_logs_user_date ON meal_logs(user_id, logged_at DESC);
CREATE INDEX idx_meal_logs_user_today ON meal_logs(user_id, (logged_at::date));

-- Nutrition goals
CREATE TABLE nutrition_goals (
    id SERIAL PRIMARY KEY,
    user_id INTEGER UNIQUE NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    calories_target INTEGER DEFAULT 2000,
    protein_target_g NUMERIC(7,2) DEFAULT 150,
    carbs_target_g NUMERIC(7,2) DEFAULT 250,
    fat_target_g NUMERIC(7,2) DEFAULT 65,
    water_target_ml INTEGER DEFAULT 2000,
    updated_at TIMESTAMPTZ DEFAULT NOW()
);
```

---

### GAMIFICATION

```sql
-- User XP and streak state
CREATE TABLE user_xp (
    id SERIAL PRIMARY KEY,
    user_id INTEGER UNIQUE NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    
    total_xp INTEGER DEFAULT 0,
    current_level INTEGER DEFAULT 1,
    
    -- Streak
    current_streak_days INTEGER DEFAULT 0,
    longest_streak_days INTEGER DEFAULT 0,
    last_workout_date DATE,
    streak_frozen_until DATE,              -- for streak freeze boost
    streak_shields INTEGER DEFAULT 0,      -- for streak shield boost
    
    -- Time-scoped XP (for leaderboards)
    weekly_xp INTEGER DEFAULT 0,
    monthly_xp INTEGER DEFAULT 0,
    
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- Achievement definitions (seeded)
CREATE TABLE achievement_definitions (
    id SERIAL PRIMARY KEY,
    key VARCHAR(100) UNIQUE NOT NULL,
    name VARCHAR(200) NOT NULL,
    description TEXT NOT NULL,
    icon_name VARCHAR(50),                 -- lucide-react icon name
    
    category VARCHAR(30) NOT NULL,
    -- 'workout', 'strength', 'consistency', 'social', 'nutrition', 'body', 'challenge'
    
    xp_reward INTEGER DEFAULT 50,
    
    -- How to earn it
    requirement_type VARCHAR(50) NOT NULL,
    -- 'workout_count', 'streak_days', 'total_volume_kg', 'pr_count',
    -- 'follower_count', 'challenge_wins', 'level'
    
    requirement_value NUMERIC NOT NULL,
    
    rarity VARCHAR(20) DEFAULT 'common'    -- 'common', 'rare', 'epic', 'legendary'
);

-- User's earned achievements
CREATE TABLE user_achievements (
    id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    achievement_id INTEGER NOT NULL REFERENCES achievement_definitions(id),
    earned_at TIMESTAMPTZ DEFAULT NOW(),
    notified BOOLEAN DEFAULT FALSE,
    UNIQUE(user_id, achievement_id)
);

CREATE INDEX idx_user_achievements_user ON user_achievements(user_id);
```

---

### SOCIAL

```sql
-- Follow relationships
CREATE TABLE follows (
    id SERIAL PRIMARY KEY,
    follower_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    following_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    UNIQUE(follower_id, following_id),
    CHECK (follower_id != following_id)    -- can't follow yourself
);

CREATE INDEX idx_follows_follower ON follows(follower_id);
CREATE INDEX idx_follows_following ON follows(following_id);

-- Activity feed
CREATE TABLE activity_feed (
    id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    
    activity_type VARCHAR(50) NOT NULL,
    -- 'workout_completed', 'pr_achieved', 'goal_reached', 
    -- 'achievement_earned', 'challenge_won', 'streak_milestone'
    
    -- Context (nullable depending on type)
    workout_id INTEGER REFERENCES workout_sessions(id) ON DELETE SET NULL,
    achievement_id INTEGER REFERENCES achievement_definitions(id) ON DELETE SET NULL,
    
    description TEXT NOT NULL,
    is_public BOOLEAN DEFAULT TRUE,
    
    likes_count INTEGER DEFAULT 0,         -- denormalized for performance
    comments_count INTEGER DEFAULT 0,
    
    created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX idx_feed_user ON activity_feed(user_id, created_at DESC);
CREATE INDEX idx_feed_public ON activity_feed(is_public, created_at DESC);

-- Likes and comments
CREATE TABLE feed_likes (
    id SERIAL PRIMARY KEY,
    activity_id INTEGER NOT NULL REFERENCES activity_feed(id) ON DELETE CASCADE,
    user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    UNIQUE(activity_id, user_id)
);

CREATE TABLE feed_comments (
    id SERIAL PRIMARY KEY,
    activity_id INTEGER NOT NULL REFERENCES activity_feed(id) ON DELETE CASCADE,
    user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    text VARCHAR(1000) NOT NULL,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Challenges
CREATE TABLE challenges (
    id SERIAL PRIMARY KEY,
    creator_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    
    name VARCHAR(200) NOT NULL,
    description TEXT,
    
    challenge_type VARCHAR(30) NOT NULL,
    -- 'total_workouts', 'total_volume_kg', 'streak_days', 'specific_exercise'
    
    target_value NUMERIC NOT NULL,
    exercise_id INTEGER REFERENCES exercise_library(id),  -- for specific_exercise type
    
    start_date DATE NOT NULL,
    end_date DATE NOT NULL,
    
    is_public BOOLEAN DEFAULT TRUE,
    max_participants INTEGER DEFAULT 50,
    
    status VARCHAR(20) DEFAULT 'upcoming',  -- 'upcoming', 'active', 'completed'
    
    created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE TABLE challenge_participants (
    id SERIAL PRIMARY KEY,
    challenge_id INTEGER NOT NULL REFERENCES challenges(id) ON DELETE CASCADE,
    user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    
    current_value NUMERIC DEFAULT 0,
    rank INTEGER,
    
    joined_at TIMESTAMPTZ DEFAULT NOW(),
    completed_at TIMESTAMPTZ,
    
    UNIQUE(challenge_id, user_id)
);
```

---

### NOTIFICATIONS

```sql
CREATE TABLE notifications (
    id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    
    notification_type VARCHAR(50) NOT NULL,
    title VARCHAR(200) NOT NULL,
    body TEXT NOT NULL,
    
    is_read BOOLEAN DEFAULT FALSE,
    
    -- Deep link back to relevant content
    action_url VARCHAR(200),
    
    -- Context
    related_type VARCHAR(30),              -- 'workout', 'achievement', 'challenge', 'user'
    related_id INTEGER,
    
    created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX idx_notifications_user ON notifications(user_id, is_read, created_at DESC);
CREATE INDEX idx_notifications_unread ON notifications(user_id, is_read) WHERE is_read = FALSE;

-- Per-user notification preferences
CREATE TABLE notification_settings (
    user_id INTEGER PRIMARY KEY REFERENCES users(id) ON DELETE CASCADE,
    
    workout_reminders BOOLEAN DEFAULT TRUE,
    streak_alerts BOOLEAN DEFAULT TRUE,
    achievement_alerts BOOLEAN DEFAULT TRUE,
    social_alerts BOOLEAN DEFAULT TRUE,
    challenge_alerts BOOLEAN DEFAULT TRUE,
    nutrition_reminders BOOLEAN DEFAULT FALSE,
    
    email_notifications BOOLEAN DEFAULT FALSE,
    
    -- Custom reminder time (for workout reminders)
    reminder_time TIME DEFAULT '18:00:00',
    reminder_days INTEGER[] DEFAULT '{1,2,3,4,5}'   -- Mon-Fri
);
```

---

### ADMIN

```sql
-- Audit log of all admin actions
CREATE TABLE admin_logs (
    id SERIAL PRIMARY KEY,
    admin_id INTEGER NOT NULL REFERENCES users(id),
    
    action VARCHAR(100) NOT NULL,
    -- 'user_suspended', 'user_activated', 'user_role_changed',
    -- 'exercise_created', 'exercise_updated', 'report_resolved'
    
    target_type VARCHAR(30),               -- 'user', 'exercise', 'report'
    target_id INTEGER,
    
    details JSONB,                         -- {"previous_role": "user", "new_role": "admin"}
    ip_address INET,
    
    created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX idx_admin_logs_admin ON admin_logs(admin_id, created_at DESC);
CREATE INDEX idx_admin_logs_target ON admin_logs(target_type, target_id);

-- User reports
CREATE TABLE reports (
    id SERIAL PRIMARY KEY,
    reporter_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    
    target_type VARCHAR(20) NOT NULL,      -- 'user', 'workout', 'comment'
    target_id INTEGER NOT NULL,
    
    reason VARCHAR(50) NOT NULL,
    -- 'spam', 'harassment', 'fake', 'offensive', 'other'
    
    description TEXT,
    
    status VARCHAR(20) DEFAULT 'pending',  -- 'pending', 'resolved', 'dismissed'
    resolved_by INTEGER REFERENCES users(id),
    resolved_at TIMESTAMPTZ,
    resolution_notes TEXT,
    
    created_at TIMESTAMPTZ DEFAULT NOW()
);
```

---

## 📊 SCALING STRATEGY

### Phase 1: Single Instance (0–1,000 users)
```
Current setup: one PostgreSQL instance
Action needed: NOTHING. PostgreSQL handles 1k users easily.
Monitoring: Add pg_stat_statements to track slow queries
```

### Phase 2: Read Replicas (1,000–10,000 users)
```
Problem: Analytics queries are heavy reads
Solution: Add 1 read replica

Analytics queries → replica (read)
Write operations → primary (write)

SQLAlchemy config:
engines = {
    "write": create_async_engine(PRIMARY_DB_URL),
    "read": create_async_engine(REPLICA_DB_URL),
}
# Route SELECT queries to read engine
# Route INSERT/UPDATE/DELETE to write engine
```

### Phase 3: Connection Pooling (10,000–100,000 users)
```
Problem: Too many connections overwhelming PostgreSQL
Solution: Add PgBouncer connection pooler

Users → FastAPI → PgBouncer → PostgreSQL
                (pools 10,000 app connections → 100 DB connections)

Docker service:
  pgbouncer:
    image: pgbouncer/pgbouncer
    environment:
      DATABASES_HOST: postgres
      POOL_MODE: transaction
      MAX_CLIENT_CONN: 10000
      DEFAULT_POOL_SIZE: 100
```

### Phase 4: Table Partitioning (100,000+ users)
```
Problem: workout_sets, meal_logs, notifications tables become huge

Solution: Range partitioning by date

CREATE TABLE workout_sets (
    -- same schema
) PARTITION BY RANGE (created_at);

CREATE TABLE workout_sets_2025 PARTITION OF workout_sets
    FOR VALUES FROM ('2025-01-01') TO ('2026-01-01');

CREATE TABLE workout_sets_2026 PARTITION OF workout_sets
    FOR VALUES FROM ('2026-01-01') TO ('2027-01-01');

Benefit: Queries for "last 30 days" only scan 1-2 partitions, not entire table
```

### Phase 5: Horizontal Scaling (1M+ users)
```
This is future territory — far away.
Options:
- Citus (distributed PostgreSQL — shard by user_id)
- Migrate analytics to ClickHouse (columnar, OLAP)
- Cache leaderboards in Redis
- Full-text search in Elasticsearch

You will NOT need this for a personal app.
Document it here for completeness.
```

---

## 📈 CRITICAL INDEXES

These indexes are the difference between 2ms and 2000ms queries:

```sql
-- Most critical: all queries that filter by user_id AND date
CREATE INDEX idx_sessions_user_date ON workout_sessions(user_id, started_at DESC);
CREATE INDEX idx_meal_logs_user_date ON meal_logs(user_id, logged_at DESC);
CREATE INDEX idx_body_metrics_user_date ON body_metrics(user_id, logged_at DESC);
CREATE INDEX idx_notifications_unread ON notifications(user_id) WHERE is_read = FALSE;

-- Social: feed generation
-- "Get workouts by everyone I follow, sorted by date"
CREATE INDEX idx_feed_user_public ON activity_feed(user_id, created_at DESC) WHERE is_public = TRUE;
CREATE INDEX idx_follows_follower ON follows(follower_id);

-- Search
CREATE INDEX idx_exercise_trgm ON exercise_library USING GIN(name gin_trgm_ops);
CREATE INDEX idx_food_trgm ON food_items USING GIN(name gin_trgm_ops);

-- Gamification
CREATE INDEX idx_user_xp_leaderboard ON user_xp(weekly_xp DESC, monthly_xp DESC);
```

---

## 🔄 MIGRATION STRATEGY

### Rules (NON-NEGOTIABLE)
```python
# 1. ALWAYS create new migration for schema changes
alembic revision --autogenerate -m "add_notes_table"

# 2. NEVER edit existing migration files after they've been run

# 3. New columns must be nullable OR have a default:
# WRONG:
op.add_column('users', sa.Column('new_col', sa.String(), nullable=False))
# This breaks if table has existing rows!

# RIGHT:
op.add_column('users', sa.Column('new_col', sa.String(), nullable=True))
# OR:
op.add_column('users', sa.Column('new_col', sa.Integer(), server_default='0'))

# 4. Never drop columns — just stop using them (backward compat)
# 5. Index creation: use CONCURRENTLY in production (doesn't lock table)
op.create_index('idx_name', 'table', ['col'], postgresql_concurrently=True)
```

---

## 💾 BACKUP STRATEGY

### Development
```bash
# Manual backup
pg_dump fittracker > backup_$(date +%Y%m%d).sql

# Restore
psql fittracker < backup_20250101.sql
```

### Production (Railway/Render)
```
Railway: automatic daily backups, 7-day retention
Render: automatic daily backups on paid plans

Manual backup via GitHub Actions (weekly):
- pg_dump → compress → upload to S3/Cloudflare R2
- Retention: 90 days
- Test restore: quarterly
```

### What to backup
```
CRITICAL (daily): PostgreSQL data dump
IMPORTANT (weekly): uploads/ folder (avatars, photos)
NICE (daily): application logs
```

---

## 🔍 USEFUL QUERIES REFERENCE

```sql
-- Dashboard stats for one user
SELECT
    COUNT(*) FILTER (WHERE started_at > NOW() - INTERVAL '7 days') as this_week,
    COUNT(*) FILTER (WHERE started_at > NOW() - INTERVAL '30 days') as this_month,
    COUNT(*) as total,
    SUM(total_volume_kg) as all_time_volume
FROM workout_sessions
WHERE user_id = $1 AND status = 'completed';

-- Strength progress for a specific exercise
SELECT
    DATE(ws.started_at) as date,
    MAX(wse.weight_kg) as max_weight,
    SUM(wse.weight_kg * wse.reps) as volume
FROM workout_sets wse
JOIN workout_exercises we ON wse.workout_exercise_id = we.id
JOIN workout_sessions ws ON we.session_id = ws.id
WHERE ws.user_id = $1
  AND we.exercise_library_id = $2
  AND wse.completed = TRUE
  AND ws.started_at > NOW() - INTERVAL '90 days'
GROUP BY DATE(ws.started_at)
ORDER BY date;

-- Muscle group distribution
SELECT
    unnest(el.muscle_primary) as muscle_group,
    COUNT(wse.id) as sets_count,
    ROUND(COUNT(wse.id) * 100.0 / SUM(COUNT(wse.id)) OVER (), 1) as percentage
FROM workout_sets wse
JOIN workout_exercises we ON wse.workout_exercise_id = we.id
JOIN workout_sessions ws ON we.session_id = ws.id
JOIN exercise_library el ON we.exercise_library_id = el.id
WHERE ws.user_id = $1
  AND ws.started_at > NOW() - INTERVAL '30 days'
  AND wse.completed = TRUE
GROUP BY muscle_group
ORDER BY sets_count DESC;

-- Leaderboard (weekly XP)
SELECT
    u.username, u.avatar_url,
    ux.current_level, ux.weekly_xp,
    RANK() OVER (ORDER BY ux.weekly_xp DESC) as rank
FROM user_xp ux
JOIN users u ON ux.user_id = u.id
WHERE u.is_active = TRUE
ORDER BY ux.weekly_xp DESC
LIMIT 50;
```
