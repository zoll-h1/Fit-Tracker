# FT_10_FUTURE_MODIFICATIONS.md
# FitTracker | Future Features & Modifications Roadmap

> This document covers EVERY planned feature not yet in the core documentation.
> Each feature has: purpose, database schema additions, API design, frontend design,
> implementation complexity, and Codex prompts.
> Read this BEFORE starting any new feature. Plan first, build second.

---

## 📋 WHAT'S ALREADY IN CORE DOCS (Skip These)

These are fully documented in FT_00 through FT_09:
- ✅ Workout logging (sets, reps, weight, timer)
- ✅ Body metrics tracking (weight, BF%, measurements)
- ✅ Nutrition / meal logging
- ✅ Exercise library
- ✅ Gamification (XP, levels, achievements, streaks)
- ✅ Social feed, follows, challenges
- ✅ Analytics & charts
- ✅ Admin panel
- ✅ Notifications
- ✅ Workout templates

---

## 📑 TABLE OF CONTENTS

1. [Notes System](#1-notes-system)
2. [Training Time Tracker](#2-training-time-tracker)
3. [Gym To-Do System](#3-gym-to-do-system)
4. [Rewards System](#4-rewards-system)
5. [Boostings System](#5-boostings-system)
6. [AI Coach & Recommendations](#6-ai-coach--recommendations)
7. [Recovery Tracker](#7-recovery-tracker)
8. [1RM Calculator & Strength Standards](#8-1rm-calculator--strength-standards)
9. [Periodization Planner](#9-periodization-planner)
10. [Habit Tracker](#10-habit-tracker)
11. [Injury Log & Prevention](#11-injury-log--prevention)
12. [Body Photo Comparison](#12-body-photo-comparison)
13. [Barcode Food Scanner](#13-barcode-food-scanner)
14. [Sleep Tracker](#14-sleep-tracker)
15. [PR Celebration System](#15-pr-celebration-system)
16. [Workout Music Integration](#16-workout-music-integration)
17. [Accountability Partner System](#17-accountability-partner-system)
18. [Custom Program Builder](#18-custom-program-builder)
19. [Export & Reports](#19-export--reports)
20. [Calendar Integration](#20-calendar-integration)
21. [Streak Shield (Spend XP)](#21-streak-shield-spend-xp)
22. [Water Tracker](#22-water-tracker)
23. [Voice Logging](#23-voice-logging)
24. [Wearable Integration](#24-wearable-integration)
25. [Implementation Priority Matrix](#25-implementation-priority-matrix)

---

## 1. NOTES SYSTEM

### Purpose
A standalone note-taking system for gym-related thoughts. Different from workout notes (those are attached to sessions). This is a personal knowledge base: form cues, program ideas, things to try, motivational notes, research snippets.

### Database Additions
```sql
CREATE TABLE notes (
    id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    
    title VARCHAR(200),
    content TEXT NOT NULL,
    
    -- Organization
    category VARCHAR(50),        -- "form_tips", "program_ideas", "motivation", "research", "custom"
    tags TEXT[],                 -- e.g. ["bench press", "technique", "competition"]
    color VARCHAR(20),           -- UI highlight color: "blue", "yellow", "red", "green"
    is_pinned BOOLEAN DEFAULT FALSE,
    is_archived BOOLEAN DEFAULT FALSE,
    
    -- Links (optional context)
    linked_exercise_id INTEGER REFERENCES exercise_library(id),
    linked_workout_id INTEGER REFERENCES workout_sessions(id),
    
    -- Timestamps
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX idx_notes_user ON notes(user_id);
CREATE INDEX idx_notes_tags ON notes USING GIN(tags);
CREATE INDEX idx_notes_search ON notes USING GIN(to_tsvector('english', title || ' ' || content));
```

### API Endpoints
```
POST   /api/notes                    → Create note
GET    /api/notes                    → List (filter: category, tags, pinned, archived)
GET    /api/notes/{id}               → Note detail
PUT    /api/notes/{id}               → Update note
DELETE /api/notes/{id}               → Delete (soft delete → trash)
GET    /api/notes/search?q=          → Full-text search
POST   /api/notes/{id}/pin           → Toggle pin
POST   /api/notes/{id}/archive       → Archive note
```

### Frontend Design
```
Layout: Masonry card grid (like Google Keep)
Each card: title + content preview + tags + color accent + pin icon
Top: search bar + category filter pills + "New Note" button
New note: expandable card with rich text (markdown support)
Pinned notes: shown at top in a separate row
Tags: clickable chips that filter the view
Colors: 6 color options for card background tint

Keyboard shortcut: Ctrl+N → create new note
```

### Codex Prompt
```
Create a Notes module for FitTracker. Google Keep-style.

Backend:
- Note model with: title, content (text), category, tags (array), color, is_pinned, is_archived
- Full-text search using PostgreSQL tsvector (index on title + content)
- Tag filtering using PostgreSQL array operators (ANY)
- GET /api/notes: filter by category, tags, is_pinned, is_archived, paginate
- GET /api/notes/search?q=: full-text search
- All routes scoped to current_user.id

Frontend (React):
- Masonry grid layout (CSS columns: 3 on desktop, 2 on tablet, 1 on mobile)
- NoteCard component: shows title, content preview (max 5 lines), tags, color tint
- CreateNoteInput: expandable textarea at top (like Google Keep)
- Tag chips: click to filter, different color per tag
- Color picker: 6 colors for card highlight
- Pin toggle: pushes card to top section
- Debounced search (400ms delay)
- Optimistic updates (note appears instantly)
```

---

## 2. TRAINING TIME TRACKER

### Purpose
Beyond the workout timer (which tracks active gym time), this tracks HOW you spend your gym time. Rest periods, warm-up time, actual working time. Also includes a Pomodoro-style focus timer for study/training sessions outside the gym.

Also covers: total time spent training per day/week/month for analytics.

### Database Additions
```sql
CREATE TABLE training_time_logs (
    id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    
    -- What was tracked
    session_type VARCHAR(30) NOT NULL,
    -- "gym_workout" (linked to workout_session)
    -- "cardio" (running, cycling — standalone)
    -- "mobility" (stretching, yoga)
    -- "skill_practice" (calisthenics skills, technique)
    -- "study" (watching tutorials, reading about training)
    
    -- Times
    started_at TIMESTAMPTZ NOT NULL,
    ended_at TIMESTAMPTZ,
    duration_seconds INTEGER,         -- auto-calculated when ended
    
    -- Optional context
    workout_session_id INTEGER REFERENCES workout_sessions(id),
    notes TEXT,
    location VARCHAR(100),            -- "Home", "Gym XYZ", "Park"
    
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- For detailed breakdown within a session
CREATE TABLE time_segments (
    id SERIAL PRIMARY KEY,
    time_log_id INTEGER NOT NULL REFERENCES training_time_logs(id) ON DELETE CASCADE,
    segment_type VARCHAR(30),         -- "warmup", "working", "rest", "cooldown"
    duration_seconds INTEGER NOT NULL,
    notes TEXT
);

CREATE INDEX idx_time_logs_user_date ON training_time_logs(user_id, started_at);
```

### API Endpoints
```
POST   /api/time-tracker/start           → Start a timer session
POST   /api/time-tracker/{id}/stop       → Stop + auto-calculate duration
POST   /api/time-tracker/{id}/pause      → Pause timer
POST   /api/time-tracker/{id}/resume     → Resume timer
GET    /api/time-tracker/logs            → History (filter by date, type)
GET    /api/time-tracker/summary         → Total time per type per period
GET    /api/time-tracker/active          → Currently running timer (if any)
DELETE /api/time-tracker/{id}            → Delete log
```

### Frontend Design
```
Dashboard widget: "Time This Week" — pie chart: gym / cardio / mobility / study
Timer screen: Large countdown/count-up display, session type selector
Start: tap session type → timer starts
Visual: animated ring around time display

Analytics tab addition: "Time Distribution" chart
- Hours per week per session type
- Average session duration trend
- Best time of day for workouts (histogram)

Quick timer: Accessible from anywhere in the app (floating button)
Pomodoro mode: 25min work / 5min rest cycles for study sessions
```

### Codex Prompt
```
Create a Training Time Tracker module for FitTracker.

Backend:
- TrainingTimeLog model: user_id, session_type (enum), started_at, ended_at, duration_seconds, notes, location
- POST /api/time-tracker/start {session_type, notes?, location?} → create log with started_at=now
- POST /api/time-tracker/{id}/stop → set ended_at=now, calc duration_seconds, return log
- GET /api/time-tracker/active → return running log (ended_at IS NULL) for current user
- GET /api/time-tracker/summary?period=7d → aggregate by session_type, return total seconds per type
- Prevent starting 2 concurrent sessions (check for active session)
- Auto-stop orphaned sessions (cron: sessions running > 4 hours → auto-stop)

Frontend:
- TimerWidget component: shows session type, elapsed time (count-up), stop button
- Persists timer state in Zustand (not React Query — needs real-time update)
- Large digital clock display (font: JetBrains Mono)
- setInterval every second to update display
- On stop: show session summary card
- TimeDistributionChart: donut chart of hours per type (last 7/30d)
```

---

## 3. GYM TO-DO SYSTEM

### Purpose
A task manager specifically built for gym/training context. Not a generic to-do app — every task is connected to fitness: things to learn, movements to try, goals to hit, equipment to buy, things to ask a trainer.

### Database Additions
```sql
CREATE TABLE training_todos (
    id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    
    title VARCHAR(300) NOT NULL,
    description TEXT,
    
    -- Context
    category VARCHAR(50),
    -- "learn" (new exercise/technique to learn)
    -- "try" (movement/variation to try)
    -- "improve" (something to work on)
    -- "buy" (equipment, supplements)
    -- "research" (look up, watch video)
    -- "goal" (performance target)
    -- "ask" (ask trainer, ask in community)
    -- "custom"
    
    -- Priority & Status
    priority INTEGER DEFAULT 2,       -- 1=low, 2=medium, 3=high
    status VARCHAR(20) DEFAULT 'todo',-- todo, in_progress, done, cancelled
    
    -- Optional links
    linked_exercise_id INTEGER REFERENCES exercise_library(id),
    
    -- Scheduling
    due_date DATE,
    reminder_at TIMESTAMPTZ,
    completed_at TIMESTAMPTZ,
    
    -- Order (manual drag-n-drop reorder)
    display_order INTEGER DEFAULT 0,
    
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX idx_todos_user_status ON training_todos(user_id, status);
```

### API Endpoints
```
POST   /api/todos                        → Create todo
GET    /api/todos                        → List (filter: status, category, priority)
PUT    /api/todos/{id}                   → Update (title, status, priority, etc.)
DELETE /api/todos/{id}                   → Delete
POST   /api/todos/{id}/complete          → Mark as done + set completed_at
POST   /api/todos/reorder                → Update display_order for drag-n-drop
GET    /api/todos/stats                  → Completion rate, count by category
```

### Frontend Design
```
Layout: Kanban board (3 columns: To-Do | In Progress | Done)
OR: Simple list view with category tabs

Each todo card:
- Checkbox (check = complete, animation)
- Title
- Category badge (color-coded)
- Priority indicator (red/orange/green dot)
- Due date (red if overdue)
- Linked exercise chip (if linked)

Create todo: quick-add bar at top (just type + enter)
Full form: expand for category, priority, due date, description, exercise link

Swipe left on mobile: delete/archive
Swipe right: mark done

Dashboard widget: "Training To-Dos" — shows 3 pending todos, "View all" link

Special feature: "Add to Todo from Exercise Library" — 
browse exercises → tap "Add to Learn List" → auto-creates todo
```

### Codex Prompt
```
Create a Training Todo module for FitTracker.

Backend:
- TrainingTodo model: user_id, title, description, category (enum), priority (1-3), 
  status (todo/in_progress/done/cancelled), linked_exercise_id, due_date, 
  completed_at, display_order
- POST /api/todos: create, default status=todo, auto-set display_order to max+1
- GET /api/todos: filter by status, category, priority; sort by display_order
- POST /api/todos/{id}/complete: set status=done, completed_at=now
- POST /api/todos/reorder: accept {ordered_ids: [1,3,2,5]} → update display_order for each
- GET /api/todos/stats: {total, completed_this_week, completion_rate, by_category: {...}}
- Award 15 XP when todo marked complete (call gamification service)

Frontend:
- Kanban columns using CSS grid (3 cols desktop, tabs on mobile)
- DraggableCard: use @dnd-kit/core for drag-n-drop between columns + reorder
- QuickAddBar: input + enter to create todo in "To-Do" column
- CategoryBadge: colored pill component
- PriorityDot: colored circle based on priority level
- Completion animation: checkbox → checkmark with confetti burst (Framer Motion)
- Overdue indicator: due_date in red if past
```

---

## 4. REWARDS SYSTEM

### Purpose
Beyond XP and levels (which are abstract), the Rewards system gives users tangible, meaningful unlocks when they hit milestones. Think: unlocking new app themes, special dashboard widgets, custom achievement frames, exclusive workout templates, profile badge frames.

This makes progression feel REAL and valuable.

### Database Additions
```sql
CREATE TABLE reward_definitions (
    id SERIAL PRIMARY KEY,
    key VARCHAR(100) UNIQUE NOT NULL,           -- "theme_dark_fire", "frame_gold"
    name VARCHAR(200) NOT NULL,
    description TEXT,
    reward_type VARCHAR(50) NOT NULL,
    -- "theme" (app color theme)
    -- "badge_frame" (profile picture frame)
    -- "dashboard_widget" (exclusive stats widget)
    -- "workout_template" (exclusive pre-built program)
    -- "title" (displayed under username)
    -- "avatar_flair" (animated overlay on avatar)
    
    -- How to unlock
    unlock_type VARCHAR(50) NOT NULL,
    -- "level" (reach certain level)
    -- "achievement" (earn specific achievement)
    -- "streak" (hit streak milestone)
    -- "workout_count" (log N workouts)
    -- "pr_count" (hit N PRs)
    -- "challenge_win" (win a challenge)
    
    unlock_requirement JSONB NOT NULL,
    -- {"type": "level", "value": 5}
    -- {"type": "streak", "value": 30}
    -- {"type": "achievement", "key": "iron_consistency"}
    
    -- The actual reward data
    reward_data JSONB,
    -- {"theme": {"primary": "#FF5500", "accent": "#FF8C00", "name": "Fire"}}
    -- {"frame_url": "/static/frames/gold_frame.png"}
    -- {"title_text": "Iron Athlete", "color": "#C0C0C0"}
    
    rarity VARCHAR(20) DEFAULT 'common',        -- common, rare, epic, legendary
    preview_url VARCHAR(500),
    
    created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE TABLE user_rewards (
    id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    reward_id INTEGER NOT NULL REFERENCES reward_definitions(id),
    earned_at TIMESTAMPTZ DEFAULT NOW(),
    is_equipped BOOLEAN DEFAULT FALSE,
    UNIQUE(user_id, reward_id)
);

-- Track which reward is active per slot
CREATE TABLE user_equipped_rewards (
    user_id INTEGER PRIMARY KEY REFERENCES users(id) ON DELETE CASCADE,
    active_theme_id INTEGER REFERENCES reward_definitions(id),
    active_frame_id INTEGER REFERENCES reward_definitions(id),
    active_title_id INTEGER REFERENCES reward_definitions(id),
    active_flair_id INTEGER REFERENCES reward_definitions(id),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX idx_user_rewards_user ON user_rewards(user_id);
```

### API Endpoints
```
GET    /api/rewards                      → All reward definitions + unlock status
GET    /api/rewards/my                   → User's earned rewards
POST   /api/rewards/{id}/equip           → Set as active reward in its slot
GET    /api/rewards/equipped             → Currently equipped rewards (for UI rendering)
```

### Reward Ideas (Seed Data)
```
Themes:
- "Default Blue" → unlocked by default
- "Fire Orange" → reach Level 5
- "Ice Blue" → 30-day streak
- "Night Gold" → reach Level 10
- "Matrix Green" → log 200 workouts
- "Blood Iron" → achieve 10 PRs in one month

Profile Frames:
- "Bronze Lifter" → Level 3
- "Silver Athlete" → Level 6
- "Gold Champion" → Level 9
- "Legendary" → Level 10
- "Streak Master" → 100-day streak
- "Iron Consistency" → earn Iron Consistency achievement

User Titles:
- "Beginner" → default
- "Dedicated" → 50 workouts
- "Iron Athlete" → 100 workouts
- "Volume King" → 10,000kg total volume
- "Streak Warrior" → 60-day streak
- "Challenge Champion" → win 5 challenges
- "The Grinder" → 365 workouts total
```

### Frontend Design
```
Rewards Gallery page:
- Grid of reward cards
- Each card: reward name, type badge, rarity glow (common=gray, rare=blue, epic=purple, legendary=gold)
- Locked rewards: grayed out with lock icon + "unlock requirement" shown
- Earned rewards: full color + "Equip" button

Equip modal: 
- Shows preview of how it looks
- Confirm equip button

Profile page changes:
- Shows active frame around avatar
- Shows active title below username
- Theme changes are app-wide (saved in Zustand settingsStore, persisted)

Reward earned moment:
- Full-screen overlay: reward appears with animation
- Rarity-appropriate effects (legendary = gold particle rain)
```

---

## 5. BOOSTINGS SYSTEM

### Purpose
Spend XP (earned through activity) to activate temporary boosts that enhance the tracking experience. NOT pay-to-win — just a fun XP sink that makes progression feel strategic.

### Boost Types
```
XP BOOSTS:
- "Double XP" → next workout gives 2x XP (costs 200 XP)
- "Triple XP Weekend" → all XP doubled for 48h (costs 500 XP)
- "Streak Multiplier" → streak XP awards doubled for 7 days (costs 300 XP)

STREAK PROTECTION:
- "Streak Shield" → protects streak for 1 missed day (costs 150 XP)
  → If you miss a day, shield auto-activates, streak preserved
  → Can hold max 3 shields at once
- "Streak Freeze" → manually freeze streak for a planned rest week (costs 400 XP)

CHALLENGE BOOSTS:
- "Challenge Head Start" → start challenge with +10% progress (costs 250 XP, one per challenge)
- "Challenge Insight" → see competitors' strategies in a challenge (costs 100 XP)

ANALYTICS BOOSTS:
- "Deep Analysis" → unlock advanced analytics for 30 days (costs 350 XP)
  → Shows: predicted 1RM, recovery rate, performance optimization tips

SOCIAL BOOSTS:
- "Spotlight" → your activity appears at top of followers' feed for 24h (costs 200 XP)
```

### Database Additions
```sql
CREATE TABLE boost_definitions (
    id SERIAL PRIMARY KEY,
    key VARCHAR(100) UNIQUE NOT NULL,
    name VARCHAR(200) NOT NULL,
    description TEXT NOT NULL,
    boost_type VARCHAR(50) NOT NULL,       -- "xp_multiplier", "streak_shield", "streak_freeze", "analytics", "social"
    cost_xp INTEGER NOT NULL,
    duration_hours INTEGER,                -- null = instant/permanent effect
    effect_data JSONB NOT NULL,            -- {"multiplier": 2.0} or {"shields": 1}
    max_stack INTEGER DEFAULT 1,           -- how many you can hold at once
    cooldown_hours INTEGER DEFAULT 0,      -- prevent buying same boost too frequently
    is_active BOOLEAN DEFAULT TRUE
);

CREATE TABLE user_boosts (
    id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    boost_id INTEGER NOT NULL REFERENCES boost_definitions(id),
    
    purchased_at TIMESTAMPTZ DEFAULT NOW(),
    activated_at TIMESTAMPTZ,
    expires_at TIMESTAMPTZ,
    is_active BOOLEAN DEFAULT FALSE,
    is_used BOOLEAN DEFAULT FALSE,
    
    -- For streak shields: how many remaining
    uses_remaining INTEGER DEFAULT 1
);

CREATE INDEX idx_user_boosts_active ON user_boosts(user_id, is_active, expires_at);
```

### API Endpoints
```
GET    /api/boosts                       → List all available boosts + user's current
POST   /api/boosts/{id}/purchase         → Deduct XP, add boost to inventory
POST   /api/boosts/{id}/activate         → Activate a purchased boost
GET    /api/boosts/active                → Currently active boosts (for XP calculation)
GET    /api/boosts/inventory             → Purchased but not yet activated
```

### Frontend Design
```
Boosts Shop page:
- Grid of boost cards
- Each card: name, description, cost (XP icon + amount), duration, rarity color
- Current XP balance shown at top
- "Purchase" button → confirm modal showing XP deduction
- Inventory section: purchased, not yet activated boosts
- "Activate" button on inventory items

Dashboard widget: "Active Boosts" — shows active boost icons with countdown timers
During workout: "2x XP Active" badge shown in workout header
On XP award: show multiplied amount ("You earned 100 XP! (2x boost)")

Visual design: Boost cards look like item cards in a game store
```

---

## 6. AI COACH & RECOMMENDATIONS

### Purpose
Use the Anthropic API (since you already have it) to power a personal AI fitness coach. Analyzes user's history and gives personalized recommendations, answers fitness questions, suggests workout adjustments.

### Implementation
```python
# This is "Claude in Claude" — use the Anthropic API from within the app

# Backend service: app/services/ai_coach_service.py

async def get_ai_recommendation(user_id: int, db) -> str:
    # 1. Gather user context
    recent_workouts = await get_recent_workouts(user_id, limit=10, db=db)
    body_metrics = await get_latest_metrics(user_id, db=db)
    goals = await get_user_goals(user_id, db=db)
    prs = await get_personal_records(user_id, db=db)
    streak = await get_streak_info(user_id, db=db)
    
    # 2. Build context string
    context = f"""
    User fitness data:
    - Streak: {streak.current} days
    - Recent workouts: {format_workouts(recent_workouts)}
    - Current weight: {body_metrics.weight_kg}kg
    - PRs: {format_prs(prs)}
    - Goals: {format_goals(goals)}
    """
    
    # 3. Call Anthropic API
    response = await anthropic.messages.create(
        model="claude-sonnet-4-20250514",
        max_tokens=500,
        system="You are a personal fitness coach. Be direct, practical, and motivating. Base advice on the data provided. Max 3 bullet points.",
        messages=[{"role": "user", "content": f"Based on this data, what should I focus on this week?\n{context}"}]
    )
    
    return response.content[0].text
```

### Database Additions
```sql
CREATE TABLE ai_coach_conversations (
    id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    
    -- Message exchange
    user_message TEXT NOT NULL,
    ai_response TEXT NOT NULL,
    
    -- Context snapshot (what data was used to answer)
    context_snapshot JSONB,
    
    -- Typing (what kind of conversation)
    message_type VARCHAR(50) DEFAULT 'general',
    -- "general", "workout_advice", "nutrition_advice", "motivation", "analysis"
    
    tokens_used INTEGER,
    
    created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE TABLE ai_weekly_insights (
    id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    week_start DATE NOT NULL,
    insight_text TEXT NOT NULL,
    insight_type VARCHAR(50),        -- "performance", "recovery", "nutrition", "motivation"
    generated_at TIMESTAMPTZ DEFAULT NOW(),
    UNIQUE(user_id, week_start, insight_type)
);

CREATE INDEX idx_ai_conversations_user ON ai_coach_conversations(user_id, created_at DESC);
```

### API Endpoints
```
POST   /api/ai-coach/chat            → Send message, get AI response
GET    /api/ai-coach/history         → Conversation history
GET    /api/ai-coach/weekly-insight  → This week's personalized insight
POST   /api/ai-coach/analyze-workout → AI analysis of a specific workout
```

### Frontend Design
```
AI Coach screen:
- Chat bubble interface (like a messaging app)
- User messages on right (blue bubbles)
- AI responses on left (dark bubbles with brain icon)
- Suggested prompts: "How am I progressing?", "What should I focus on?", 
  "Analyze my recent workouts", "Suggest a deload week?", "Am I overtraining?"
- Typing indicator while AI responds
- Weekly insight card on dashboard (collapsed, tap to expand)

Context-aware prompts:
- After finishing workout: "Ask AI to analyze this workout"
- After PR: "What does this mean for my training?"
- After body metric log: "Am I on track for my goals?"
```

---

## 7. RECOVERY TRACKER

### Purpose
Track how well you recover between workouts. Muscle soreness, sleep quality, energy levels, stress. Helps identify overtraining patterns and guides rest day decisions.

### Database Additions
```sql
CREATE TABLE recovery_logs (
    id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    logged_at DATE NOT NULL DEFAULT CURRENT_DATE,
    
    -- Subjective ratings (1-10)
    energy_level INTEGER CHECK (energy_level BETWEEN 1 AND 10),
    sleep_quality INTEGER CHECK (sleep_quality BETWEEN 1 AND 10),
    mood INTEGER CHECK (mood BETWEEN 1 AND 10),
    stress_level INTEGER CHECK (stress_level BETWEEN 1 AND 10),
    
    -- Sleep data
    sleep_hours NUMERIC(4,1),         -- e.g. 7.5
    sleep_bedtime TIME,
    sleep_wakeup TIME,
    
    -- Physical indicators
    resting_heart_rate INTEGER,       -- bpm
    hrv_score INTEGER,                -- Heart Rate Variability (if tracked)
    
    -- Muscle soreness per area (1-5 scale)
    soreness JSONB DEFAULT '{}',
    -- {"chest": 3, "back": 2, "legs": 4, "shoulders": 1}
    
    -- Readiness (auto-calculated score 1-10)
    readiness_score NUMERIC(4,1),
    
    notes TEXT,
    
    UNIQUE(user_id, logged_at)
);

CREATE INDEX idx_recovery_user_date ON recovery_logs(user_id, logged_at DESC);
```

### API Endpoints
```
POST   /api/recovery                  → Log today's recovery
GET    /api/recovery                  → History (paginated)
GET    /api/recovery/today            → Today's log (or null)
GET    /api/recovery/summary          → Trends over time
GET    /api/recovery/readiness        → Today's readiness score + recommendation
```

### Readiness Score Algorithm
```python
def calculate_readiness(log: RecoveryLog) -> float:
    score = 0
    
    # Sleep quality is most important (30%)
    score += (log.sleep_quality / 10) * 30
    
    # Energy level (25%)  
    score += (log.energy_level / 10) * 25
    
    # Low stress is good (20%)
    stress_score = (10 - log.stress_level) / 10
    score += stress_score * 20
    
    # Sleep hours (15%)
    ideal_sleep = min(log.sleep_hours, 9) / 9
    score += ideal_sleep * 15
    
    # Mood (10%)
    score += (log.mood / 10) * 10
    
    return round(score, 1)

def get_recommendation(score: float) -> str:
    if score >= 8: return "High readiness — push hard today! 🔥"
    if score >= 6: return "Good readiness — train normally 💪"
    if score >= 4: return "Moderate — consider lighter intensity today 🟡"
    return "Low readiness — rest day or light mobility recommended 🛌"
```

---

## 8. 1RM CALCULATOR & STRENGTH STANDARDS

### Purpose
Estimate max strength from training data. Compare your lifts to global standards by bodyweight and gender. Shows where you stand (beginner → elite) for each major lift.

### API Endpoints
```
GET    /api/strength/one-rm/{exercise_id}    → Estimated 1RM history
GET    /api/strength/standards/{exercise_id} → Comparison to strength standards
GET    /api/strength/profile                 → Full strength profile across all lifts
```

### Implementation
```python
# 1RM formulas (use average of multiple for accuracy)
def brzycki(weight: float, reps: int) -> float:
    return weight * (36 / (37 - reps))

def epley(weight: float, reps: int) -> float:
    return weight * (1 + reps / 30)

def estimate_1rm(weight: float, reps: int) -> float:
    if reps == 1:
        return weight
    if reps > 10:
        return None  # Too many reps, too inaccurate
    return (brzycki(weight, reps) + epley(weight, reps)) / 2

# Strength standards by bodyweight (kg) — male
STRENGTH_STANDARDS = {
    "bench_press": {
        "beginner": 0.5,      # ratio to bodyweight
        "novice": 0.75,
        "intermediate": 1.0,
        "advanced": 1.25,
        "elite": 1.5
    },
    "squat": {
        "beginner": 0.75,
        "novice": 1.0,
        "intermediate": 1.25,
        "advanced": 1.5,
        "elite": 1.75
    },
    "deadlift": {
        "beginner": 1.0,
        "novice": 1.25,
        "intermediate": 1.5,
        "advanced": 1.75,
        "elite": 2.25
    }
}
```

---

## 9. PERIODIZATION PLANNER

### Purpose
Build multi-week structured training programs (not just single workouts). Supports linear, wave, and block periodization. User can schedule which days train what, and see the full program calendar.

### Database Additions
```sql
CREATE TABLE training_programs (
    id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    name VARCHAR(200) NOT NULL,
    description TEXT,
    periodization_type VARCHAR(30),   -- "linear", "undulating", "block", "custom"
    duration_weeks INTEGER NOT NULL,
    difficulty VARCHAR(20),
    goal VARCHAR(30),                  -- "strength", "hypertrophy", "endurance", "power"
    is_public BOOLEAN DEFAULT FALSE,
    is_active BOOLEAN DEFAULT FALSE,   -- only one can be active at a time
    started_at DATE,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE TABLE program_weeks (
    id SERIAL PRIMARY KEY,
    program_id INTEGER NOT NULL REFERENCES training_programs(id) ON DELETE CASCADE,
    week_number INTEGER NOT NULL,
    theme VARCHAR(100),                -- "Intensity Week", "Volume Week", "Deload"
    intensity_modifier NUMERIC(4,2) DEFAULT 1.0  -- 0.7 = deload at 70%
);

CREATE TABLE program_days (
    id SERIAL PRIMARY KEY,
    week_id INTEGER NOT NULL REFERENCES program_weeks(id) ON DELETE CASCADE,
    day_of_week INTEGER NOT NULL,      -- 0=Mon, 6=Sun
    workout_template_id INTEGER REFERENCES workout_templates(id),
    is_rest_day BOOLEAN DEFAULT FALSE,
    notes TEXT
);
```

---

## 10. HABIT TRACKER

### Purpose
Track daily health habits beyond just workouts. Water, sleep, protein goal, stretching, no junk food, meditation. Small habits compound into transformation.

### Database Additions
```sql
CREATE TABLE habit_definitions (
    id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    name VARCHAR(200) NOT NULL,
    icon_name VARCHAR(50),             -- lucide icon name
    color VARCHAR(20),
    target_frequency VARCHAR(20),      -- "daily", "weekdays", "weekends", "custom"
    target_days INTEGER[],             -- [0,1,2,3,4] for weekdays
    reminder_time TIME,
    xp_reward INTEGER DEFAULT 10,
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE TABLE habit_logs (
    id SERIAL PRIMARY KEY,
    habit_id INTEGER NOT NULL REFERENCES habit_definitions(id) ON DELETE CASCADE,
    user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    logged_date DATE NOT NULL DEFAULT CURRENT_DATE,
    completed BOOLEAN DEFAULT TRUE,
    notes TEXT,
    UNIQUE(habit_id, logged_date)
);

CREATE INDEX idx_habit_logs_user_date ON habit_logs(user_id, logged_date DESC);
```

---

## 11. INJURY LOG & PREVENTION

### Purpose
Track injuries, pain, and discomfort. App warns you when you're training an injured area. Tracks recovery timeline. Auto-suggests exercise modifications.

### Database Additions
```sql
CREATE TABLE injury_logs (
    id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    
    body_area VARCHAR(50) NOT NULL,    -- "left_shoulder", "lower_back", "right_knee"
    injury_type VARCHAR(100),          -- "strain", "tendinitis", "soreness", "pain"
    severity INTEGER CHECK (severity BETWEEN 1 AND 5),  -- 1=minor, 5=serious
    
    started_date DATE NOT NULL,
    resolved_date DATE,               -- null = still ongoing
    is_resolved BOOLEAN DEFAULT FALSE,
    
    notes TEXT,
    
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- When adding exercise to workout, check if any active injury affects that muscle
-- Warn: "You have an active left shoulder injury. Bench press affects this area. Continue?"
```

---

## 12. BODY PHOTO COMPARISON

### Purpose
Upload progress photos and compare them side-by-side. Timeline of visual progress. One of the most powerful motivators.

### Database Additions
```sql
CREATE TABLE progress_photos (
    id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    
    photo_url VARCHAR(500) NOT NULL,
    thumbnail_url VARCHAR(500),
    
    taken_date DATE NOT NULL DEFAULT CURRENT_DATE,
    pose_type VARCHAR(30),             -- "front", "back", "side_left", "side_right"
    
    -- Optional body metric snapshot at time of photo
    body_metric_id INTEGER REFERENCES body_metrics(id),
    weight_kg NUMERIC(6,2),
    
    notes TEXT,
    is_private BOOLEAN DEFAULT TRUE,   -- private by default!
    
    created_at TIMESTAMPTZ DEFAULT NOW()
);
```

### Frontend
```
Photo Comparison screen:
- Upload photo: choose pose type
- Timeline slider: scrub through dates
- Side-by-side comparison: pick "before" and "after" date
- Grid view: all photos by pose type
- Photo is PRIVATE by default (never shown to others)

Privacy: progress photos NEVER shown in social feed unless user explicitly shares
```

---

## 13. BARCODE FOOD SCANNER

### Purpose
Scan food product barcodes to instantly add nutritional info. Uses Open Food Facts API (free, no key required).

### Implementation
```python
# Backend: app/routers/nutrition.py

@router.get("/api/nutrition/foods/scan/{barcode}")
async def scan_barcode(barcode: str, db: AsyncSession = Depends(get_db)):
    # 1. Check local DB first
    local = await db.scalar(select(FoodItem).where(FoodItem.barcode == barcode))
    if local:
        return local
    
    # 2. Query Open Food Facts API
    async with httpx.AsyncClient() as client:
        response = await client.get(
            f"https://world.openfoodfacts.org/api/v0/product/{barcode}.json",
            timeout=5.0
        )
    
    data = response.json()
    if data.get("status") != 1:
        raise HTTPException(404, "Product not found")
    
    product = data["product"]
    nutrients = product.get("nutriments", {})
    
    # 3. Save to local DB for future use
    food = FoodItem(
        name=product.get("product_name", "Unknown"),
        brand=product.get("brands"),
        barcode=barcode,
        calories_per_100g=nutrients.get("energy-kcal_100g", 0),
        protein_per_100g=nutrients.get("proteins_100g", 0),
        carbs_per_100g=nutrients.get("carbohydrates_100g", 0),
        fat_per_100g=nutrients.get("fat_100g", 0),
        is_custom=False
    )
    db.add(food)
    await db.commit()
    
    return food
```

### Frontend
```
In nutrition food search:
- Camera icon button → opens barcode scanner
- Uses html5-qrcode library (works in browser)
- On scan: calls /api/nutrition/foods/scan/{barcode}
- Auto-populates food + opens quantity input
```

---

## 14. SLEEP TRACKER

### Purpose
Track sleep duration and quality. Correlate sleep data with workout performance. Good sleep = better gains — show users the data to prove it.

Already partially in Recovery Tracker (sleep_quality, sleep_hours). This expands it with dedicated tracking and correlation analysis.

### Additional API
```
GET    /api/sleep/correlation         → Chart: sleep quality vs next-day workout performance
GET    /api/sleep/average             → Average sleep per period
GET    /api/sleep/recommendation      → AI-powered sleep advice based on patterns
```

---

## 15. PR CELEBRATION SYSTEM

### Purpose
When a Personal Record is broken, make it a moment. Animated celebration, shareable card, automatic social post option.

### Implementation
```python
# In workout service, after logging a set:
async def check_and_celebrate_pr(user_id, exercise_id, weight_kg, reps, db):
    previous_best = await get_pr(user_id, exercise_id, db)
    estimated_1rm = estimate_1rm(weight_kg, reps)
    
    if not previous_best or estimated_1rm > previous_best.estimated_1rm:
        # New PR!
        await save_pr(user_id, exercise_id, weight_kg, reps, estimated_1rm, db)
        await award_xp(user_id, 100, "pr_achieved", db)
        
        return {
            "is_pr": True,
            "exercise_name": exercise.name,
            "new_weight": weight_kg,
            "previous_best": previous_best.weight_kg if previous_best else None,
            "improvement_kg": weight_kg - (previous_best.weight_kg if previous_best else 0),
            "share_card_url": f"/api/share/pr/{new_pr_id}"
        }
```

### Frontend
```
PR celebration overlay:
- Full-screen animation (confetti + trophy icon + pulsing glow)
- "NEW PR! 🏆 Bench Press — 85kg" in massive text
- Previous vs New comparison: "Previous: 80kg → New: 85kg (+5kg)"
- "Share" button → generates shareable image card
- "Nice!" dismiss button

Shareable PR card (generated server-side as PNG):
- FitTracker logo
- Exercise name + weight
- Date
- User's level + username
- Suitable for Instagram stories
```

---

## 16. WORKOUT MUSIC INTEGRATION

### Purpose
Control Spotify playback from within the workout screen. See what's playing, skip tracks, change playlist — without leaving the workout.

### Implementation
```python
# OAuth2 with Spotify
# Scopes needed: user-read-playback-state, user-modify-playback-state

# Backend routes:
GET  /api/integrations/spotify/connect  → Spotify OAuth redirect
GET  /api/integrations/spotify/callback → Handle OAuth callback, save tokens
GET  /api/integrations/spotify/now-playing → Current track
POST /api/integrations/spotify/next     → Skip track
POST /api/integrations/spotify/previous → Previous track
POST /api/integrations/spotify/pause    → Pause/play toggle
GET  /api/integrations/spotify/playlists → User's playlists
POST /api/integrations/spotify/play-playlist/{id} → Play a playlist
```

---

## 17. ACCOUNTABILITY PARTNER SYSTEM

### Purpose
Connect with one specific person as your accountability partner. See each other's workout streaks, get notified when they train, leave each other voice notes or messages.

### Database Additions
```sql
CREATE TABLE accountability_pairs (
    id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL REFERENCES users(id),
    partner_id INTEGER NOT NULL REFERENCES users(id),
    status VARCHAR(20) DEFAULT 'pending',  -- pending, accepted, declined
    requested_at TIMESTAMPTZ DEFAULT NOW(),
    accepted_at TIMESTAMPTZ,
    UNIQUE(user_id, partner_id)
);
```

---

## 18. CUSTOM PROGRAM BUILDER

### Purpose
A visual drag-and-drop program builder. Design week-by-week training blocks, assign different templates to each day, add intensity modifiers per week.

### Frontend: Drag-and-drop weekly calendar
```
Week view: 7 columns (Mon–Sun)
Each cell: assign workout template or "Rest Day"
Week rows: 4–12 weeks
Click any template: opens preview
Drag template from library to day cell
Copy week: duplicate entire week structure
```

---

## 19. EXPORT & REPORTS

### Purpose
Export all your data. PDF progress reports. CSV data export for analysis in Excel/Sheets.

### API Endpoints
```
GET    /api/export/workouts.csv       → All workouts + sets as CSV
GET    /api/export/body-metrics.csv   → Body measurement history as CSV
GET    /api/export/nutrition.csv      → Meal log as CSV
GET    /api/export/full-backup.json   → Complete data export as JSON
GET    /api/reports/monthly-pdf       → Monthly progress report as PDF
```

### Monthly PDF Report Contents
```
Page 1: Summary (workouts, volume, streak, PRs this month)
Page 2: Workout frequency calendar
Page 3: Top lifts progress charts
Page 4: Body metrics chart
Page 5: Nutrition adherence summary
Page 6: Achievements earned this month
```

---

## 20. CALENDAR INTEGRATION

### Purpose
Sync workout schedule to Google Calendar. See planned workouts in your calendar app.

### Implementation
```
OAuth2 with Google Calendar
When user activates program: auto-create calendar events for each workout day
When workout completed: update event with actual stats
```

---

## 21. STREAK SHIELD (SPEND XP)

*Already detailed in Boostings System (#5) — see streak protection boosts.*

---

## 22. WATER TRACKER

### Purpose
Simple but powerful. Track daily water intake. Part of the Recovery Tracker but deserves its own widget.

### Database: Add to recovery_logs
```sql
ALTER TABLE recovery_logs ADD COLUMN water_ml INTEGER DEFAULT 0;
-- Or standalone:
CREATE TABLE water_logs (
    id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES users(id) ON DELETE CASCADE,
    logged_at TIMESTAMPTZ DEFAULT NOW(),
    amount_ml INTEGER NOT NULL
);
```

### Frontend: Dashboard widget
```
Water widget: 8 glass icons, tap each to fill (250ml per glass)
Shows: X / 2000ml today
Streak: days in a row hitting goal
Quick-add buttons: +250ml, +500ml, +1000ml
```

---

## 23. VOICE LOGGING

### Purpose
"Hey FitTracker, log 3 reps at 80 kilos" — hands-free set logging during workout.

### Implementation
```javascript
// Frontend: Web Speech API (browser built-in, no API key needed)
const recognition = new webkitSpeechRecognition();
recognition.onresult = (event) => {
    const transcript = event.results[0][0].transcript;
    // Parse: "3 reps 80 kilos" → {reps: 3, weight_kg: 80}
    // Or: "log 5 sets 100 kilos" → {reps: 5, weight_kg: 100}
    parseVoiceCommand(transcript);
};

function parseVoiceCommand(text: string) {
    // Regex patterns for common phrases
    const repsWeight = text.match(/(\d+)\s+reps?\s+(\d+)\s*(kg|kilos?|kg)/i);
    if (repsWeight) {
        logSet({ reps: parseInt(repsWeight[1]), weight_kg: parseInt(repsWeight[2]) });
    }
}
```

---

## 24. WEARABLE INTEGRATION

### Purpose
Import data from fitness trackers: Garmin, Fitbit, Apple Health (via health export).

### Phase 1: Apple Health (CSV export import)
```
User exports Apple Health data → uploads XML to FitTracker
App parses: workouts, steps, heart rate, sleep
Auto-imports to recovery logs and cardio tracking
```

### Phase 2: Garmin Connect
```
Garmin has a free OAuth API
Import: workouts, heart rate, VO2 max, sleep stages, HRV
```

---

## 25. IMPLEMENTATION PRIORITY MATRIX

| Feature | Value (1-10) | Effort (1-10) | Score | Start Phase |
|---------|-------------|----------------|-------|-------------|
| Notes System | 8 | 3 | **9** | Phase 2 |
| Gym To-Do | 8 | 3 | **9** | Phase 2 |
| Water Tracker | 7 | 2 | **9** | Phase 2 |
| Recovery Tracker | 9 | 4 | **8.5** | Phase 2 |
| Boostings (XP spend) | 9 | 4 | **8.5** | Phase 2 |
| Rewards System | 9 | 5 | **8** | Phase 2 |
| PR Celebration | 8 | 4 | **8** | Phase 2 |
| Training Time Tracker | 7 | 4 | **7.5** | Phase 2 |
| Barcode Scanner | 8 | 3 | **7.5** | Phase 3 |
| 1RM Calculator | 7 | 3 | **7.5** | Phase 3 |
| Habit Tracker | 7 | 4 | **7** | Phase 3 |
| AI Coach | 10 | 6 | **7** | Phase 3 |
| Body Photo Compare | 8 | 5 | **7** | Phase 3 |
| Voice Logging | 8 | 4 | **7** | Phase 3 |
| Periodization Planner | 7 | 6 | **6** | Phase 3 |
| Custom Program Builder | 7 | 7 | **5.5** | Phase 4 |
| Sleep Integration | 6 | 5 | **5.5** | Phase 4 |
| Spotify Integration | 6 | 5 | **5.5** | Phase 4 |
| Injury Log | 6 | 5 | **5.5** | Phase 4 |
| Export & Reports | 5 | 5 | **5** | Phase 4 |
| Calendar Integration | 5 | 6 | **4.5** | Phase 4 |
| Accountability Partner | 6 | 7 | **4.5** | Phase 4 |
| Wearable Integration | 7 | 9 | **4** | Phase 5 |
| Trainer Marketplace | 8 | 10 | **4** | Phase 5 |

### Recommended Phase 2 Add-ons (build these alongside Phase 2):
1. **Notes** (Week 5 — low effort, high value)
2. **Water Tracker** (Week 5 — 1 day of work)
3. **Gym To-Do** (Week 6 — 2 days of work)
4. **Recovery Tracker** (Week 7 — connects to analytics)
5. **Boostings + Rewards** (Week 8 — fun, increases retention)

---

## 📝 NOTES FOR IMPLEMENTATION

### Schema Changes Rule
When adding any new feature from this document:
1. Create a new Alembic migration — NEVER edit existing migrations
2. Add new tables — never delete old ones (backward compatibility)
3. Add new columns as NULLABLE with default value — never break existing rows
4. Update FT_01_DATABASE_SCHEMA.md with new tables
5. Update FT_PROJECT_TRACKER.md to track the feature

### AI Coach Warning
The Anthropic API calls cost money. Implement:
- Rate limit: max 20 AI messages per day per user
- Cache weekly insights (generate once, serve for 7 days)
- Only call API if user has enough data (min 5 workouts)
