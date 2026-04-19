# FT_PROJECT_TRACKER.md
# FitTracker | Weekly Progress Tracker

---

## 📌 PROJECT INFO

| Field            | Value                          |
|------------------|--------------------------------|
| Start Date       | _______________                |
| Target Phase 1   | _______________  (4 weeks)     |
| Target Phase 2   | _______________  (8 weeks)     |
| Target Phase 3   | _______________  (12 weeks)    |
| GitHub Repo      | _______________                |
| Backend URL      | _______________                |
| Frontend URL     | _______________                |

---

## 🔢 CURRENT STATUS

```
Phase: [1 / 2 / 3]
Current Week: [___]
Current Module: [_______________]
Blocker (if any): [_______________]
```

---

## ✅ PHASE 1 PROGRESS (Weeks 1-4)

### WEEK 1 — Foundation
```
[ ] Backend project setup (FastAPI + Docker + PostgreSQL)
[ ] Alembic configured + initial migration
[ ] User model + registration endpoint
[ ] Login endpoint + JWT tokens
[ ] Token refresh + logout
[ ] GET /api/auth/me
[ ] User profile update (PUT /api/users/profile)
[ ] Avatar upload
[ ] Frontend setup (React + Vite + TypeScript + Tailwind)
[ ] Zustand auth store + localStorage persistence
[ ] Axios client with interceptors + auto token refresh
[ ] Login page (with validation)
[ ] Register page (with validation)
[ ] Dashboard shell (layout only)
[ ] Sidebar + TopBar layout
[ ] Protected routes (redirect to login if not auth)

Week 1 notes:
_______________________________________________
_______________________________________________

Week 1 blockers resolved:
_______________________________________________
```

### WEEK 2 — Workout Logging
```
[ ] Exercise library model + seed (50 exercises)
[ ] Exercise library endpoints (list, search, detail)
[ ] Workout session model
[ ] POST /api/workouts (start session)
[ ] POST /api/workouts/{id}/exercises (add exercise)
[ ] POST /api/workouts/{id}/exercises/{ex_id}/sets (log set)
[ ] PUT /api/workouts/sets/{set_id} (update set)
[ ] DELETE /api/workouts/sets/{set_id}
[ ] POST /api/workouts/{id}/finish (calculate stats)
[ ] GET /api/workouts (history)
[ ] GET /api/workouts/{id} (detail with exercises+sets)
[ ] Previous performance hint (last session's sets for same exercise)
[ ] Personal records detection

[ ] Exercise library page (frontend)
[ ] Active workout page (frontend) — MOST IMPORTANT
[ ] Workout timer component
[ ] Set logger row (weight, reps, checkmark)
[ ] Rest timer (countdown modal)
[ ] Add exercise modal (search + add)
[ ] Finish workout flow (summary modal)
[ ] Workout history page
[ ] Workout detail page

Week 2 notes:
_______________________________________________
_______________________________________________
```

### WEEK 3 — Body Metrics + Nutrition
```
[ ] Body metrics model + endpoints
[ ] BMI auto-calculation
[ ] Body goals model + endpoints
[ ] Goal auto-completion detection
[ ] Food database model + seed (200 foods)
[ ] Food search endpoint
[ ] Meal logging endpoints
[ ] Daily nutrition summary query
[ ] Nutrition goals

[ ] Body metrics page (log + history)
[ ] Body metrics chart (weight over time)
[ ] Goals progress section
[ ] Nutrition page (daily view by meal type)
[ ] Food search UI (modal)
[ ] Daily macro ring chart
[ ] Weekly adherence display

Week 3 notes:
_______________________________________________
_______________________________________________
```

### WEEK 4 — Gamification + Analytics
```
[ ] UserXP model + table
[ ] Achievement definitions (40) seeded
[ ] XP award service
[ ] Level system (10 levels + names)
[ ] Streak tracking logic
[ ] Achievement checker service
[ ] Gamification triggered after workout finish
[ ] Gamification triggered after PR
[ ] Gamification triggered after goal reached
[ ] APScheduler setup (streak warning job)
[ ] Analytics dashboard query
[ ] Strength progress query
[ ] Muscle distribution query
[ ] PR query
[ ] Streak calendar query

[ ] XP bar in header/sidebar
[ ] Level badge component
[ ] Achievements page (grid)
[ ] Achievement unlock animation
[ ] Analytics page (5 tabs)
[ ] Strength chart (Recharts LineChart)
[ ] Volume chart (BarChart)
[ ] Calendar heatmap (365 days)
[ ] PR table

PHASE 1 COMPLETE? [ ] Yes / [ ] Not yet
Phase 1 completion date: _______________
```

---

## ✅ PHASE 2 PROGRESS (Weeks 5-8)

### WEEK 5 — Workout Templates
```
[ ] WorkoutTemplate model
[ ] TemplateExercise model
[ ] Save workout as template endpoint
[ ] List templates endpoint
[ ] Start workout from template
[ ] Public templates browsing

[ ] Templates page
[ ] Save as template UI
[ ] Template detail + start button
```

### WEEK 6 — Social Features
```
[ ] Follow/unfollow endpoints
[ ] ActivityFeed model + auto-post triggers
[ ] Feed likes + comments endpoints
[ ] Public profile endpoint
[ ] User search endpoint

[ ] Social feed page
[ ] Activity cards (3 types)
[ ] Like/comment interactions
[ ] Public profile page
[ ] Follow/unfollow button
[ ] Followers list page
```

### WEEK 7 — Challenges
```
[ ] Challenge model
[ ] ChallengeParticipant model
[ ] Challenge CRUD
[ ] Challenge progress update job
[ ] Challenge result logic

[ ] Challenges page
[ ] Create challenge modal
[ ] Challenge card with progress
[ ] Leaderboard view
```

### WEEK 8 — Admin + Notifications
```
[ ] Admin auth (session-based)
[ ] Admin dashboard page + stats
[ ] Admin user management
[ ] Admin exercise library management
[ ] Admin reports queue
[ ] Admin logs

[ ] Notification model + all trigger points
[ ] Notification settings model
[ ] Streak warning daily job
[ ] GET/PUT notification endpoints

[ ] Notifications bell + dropdown (frontend)
[ ] Notifications page
[ ] Notification settings in profile
```

---

## ✅ PHASE 3 PROGRESS (Weeks 9-12)

### WEEK 9 — Advanced Analytics
```
[ ] Volume progression
[ ] Muscle balance (push/pull)
[ ] Nutrition adherence heatmap
[ ] CSV export
[ ] Advanced body composition chart
```

### WEEK 10 — Trainer Features
```
[ ] Trainer role
[ ] Workout programs (multi-week)
[ ] Program assignment
[ ] Client tracking
```

### WEEK 11 — Advanced Workout
```
[ ] Cardio tracking
[ ] Supersets
[ ] Custom exercises
[ ] Workout photos
```

### WEEK 12 — Polish
```
[ ] PWA setup
[ ] Dark/light mode
[ ] RU/EN language toggle
[ ] Performance optimization
[ ] Sentry error monitoring
[ ] Final deployment
[ ] Landing page
```

---

## 📓 WEEKLY REVIEW LOG

### Week 1 Review (Friday)
```
Built this week:
_______________________________________________

Learned this week:
_______________________________________________

Struggled with:
_______________________________________________

Questions for Claude:
1. _______________________________________________
2. _______________________________________________
3. _______________________________________________

Plan for next week:
_______________________________________________

Overall feeling: [😤 Stuck / 😐 OK / 💪 Good / 🔥 Crushing it]
```

### Week 2 Review (Friday)
```
Built this week:
_______________________________________________

Learned this week:
_______________________________________________

Struggled with:
_______________________________________________

Questions for Claude:
1. _______________________________________________
2. _______________________________________________
3. _______________________________________________

Plan for next week:
_______________________________________________

Overall feeling: [😤 Stuck / 😐 OK / 💪 Good / 🔥 Crushing it]
```

### Week 3 Review
```
(copy format from Week 1)
```

### Week 4 Review
```
(copy format from Week 1)
```

---

## 🐛 BUG LOG

| Date | Bug Description | Module | Status | Fixed How |
|------|----------------|--------|--------|-----------|
|      |                |        | Open   |           |
|      |                |        | Fixed  |           |

---

## 💡 IDEAS TO IMPLEMENT LATER

*(Write down ideas here instead of interrupting current work)*

1. _______________________________________________
2. _______________________________________________
3. _______________________________________________
4. _______________________________________________
5. _______________________________________________

---

## 📚 RESOURCES USED

| Resource | What For | URL |
|----------|---------|-----|
| FastAPI docs | Async SQLAlchemy | https://fastapi.tiangolo.com |
| Recharts | Chart components | https://recharts.org |
| shadcn/ui | React UI components | https://ui.shadcn.com |
| Tailwind CSS | Styling | https://tailwindcss.com |
| SQLAlchemy | ORM docs | https://docs.sqlalchemy.org |

---

## ⏰ TIME TRACKING (Optional)

| Week | Hours Spent | Modules Completed | Notes |
|------|-------------|-------------------|-------|
| 1    |             |                   |       |
| 2    |             |                   |       |
| 3    |             |                   |       |
| 4    |             |                   |       |
| 5    |             |                   |       |
| 6    |             |                   |       |
| 7    |             |                   |       |
| 8    |             |                   |       |
| 9    |             |                   |       |
| 10   |             |                   |       |
| 11   |             |                   |       |
| 12   |             |                   |       |

---

## 🎯 PERSONAL GOALS FOR THIS PROJECT

*(Write why you're building FitTracker — reference when motivation drops)*

_______________________________________________
_______________________________________________
_______________________________________________
_______________________________________________

---

## 🏆 MILESTONES

```
[ ] First workout logged in the app (personal milestone)
    Date: _______________

[ ] App running in Docker
    Date: _______________

[ ] First week of real personal use
    Date: _______________

[ ] Phase 1 complete
    Date: _______________

[ ] First other person uses the app
    Date: _______________

[ ] Phase 2 complete
    Date: _______________

[ ] App deployed publicly
    Date: _______________

[ ] Phase 3 complete
    Date: _______________

[ ] 100 workouts logged (using FitTracker personally)
    Date: _______________
```
