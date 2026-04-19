# FT_09 — FEATURES ROADMAP
# FitTracker | Priority Guide & Build Order

---

## 🎯 BUILD ORDER PHILOSOPHY

Build in this order: **Core → Valuable → Nice-to-have**

Never start a "nice-to-have" when a "core" feature isn't done.
A workout tracker that doesn't track workouts perfectly is useless.

---

## 🔴 PHASE 1 — CORE (Weeks 1-4)
*Must work perfectly. This IS the app.*

### Week 1: Foundation
```
Priority: CRITICAL
Risk if skipped: App doesn't function at all

Backend:
[ ] Project setup (FastAPI + PostgreSQL + Docker)
[ ] Database migrations (Alembic)
[ ] User registration & login
[ ] JWT auth + token refresh
[ ] User profile (view + edit)
[ ] Avatar upload

Frontend:
[ ] Project setup (React + Vite + TypeScript + Tailwind)
[ ] API client with token management
[ ] Login page
[ ] Register page
[ ] Basic dashboard shell

Test after: Full auth flow works end-to-end
```

### Week 2: Workout Logging
```
Priority: CRITICAL
Risk if skipped: Core value proposition missing

Backend:
[ ] Exercise library (50 exercises seeded)
[ ] Start workout session
[ ] Add exercises to session
[ ] Log sets (weight, reps, type)
[ ] Finish workout (auto-calc volume, duration, calories)
[ ] Workout history (list + detail)
[ ] Personal records detection

Frontend:
[ ] Exercise library page (search + filter)
[ ] Active workout page (the timer, set logging)
[ ] Set row component (weight, reps, checkmark, rest timer)
[ ] Workout history page
[ ] Workout detail page

Test after: Log full workout from start to finish in the app
```

### Week 3: Body Metrics + Nutrition
```
Priority: HIGH
Risk if skipped: App is just a workout log

Backend:
[ ] Body metrics CRUD (weight, BF%, measurements)
[ ] BMI auto-calculation
[ ] Body goals (set + auto-detect when achieved)
[ ] Food database (200 items seeded)
[ ] Meal logging (with auto-macro calculation)
[ ] Daily nutrition summary
[ ] Nutrition goals

Frontend:
[ ] Body metrics page (log + chart)
[ ] Goal progress display
[ ] Nutrition page (daily view)
[ ] Food search + log meal
[ ] Daily summary ring/chart

Test after: Log a full day (workout + meals + body weight)
```

### Week 4: Gamification + Analytics
```
Priority: HIGH
Reason: Retention hook — users come back for streaks and achievements

Backend:
[ ] XP system (award on actions)
[ ] Level system (10 levels)
[ ] Streak tracking + daily job
[ ] 40 achievement definitions + seeded
[ ] Achievement checker (triggered after actions)
[ ] Basic analytics queries (dashboard stats)
[ ] Streak calendar data

Frontend:
[ ] XP bar + level badge (in header/sidebar)
[ ] Achievements page (grid with locked/unlocked)
[ ] Achievement unlock animation (Framer Motion)
[ ] Analytics dashboard page
[ ] Strength progress charts (Recharts)
[ ] Calendar heatmap (365 days)
[ ] PR table

Test after: Complete 3 workouts, see XP/streak update, earn 2+ achievements
```

---

## 🟡 PHASE 2 — VALUABLE (Weeks 5-8)
*Significantly improves the experience. Build these next.*

### Week 5: Workout Templates
```
Priority: HIGH
Reason: Power user feature — users want to repeat their routines

Backend:
[ ] Save workout as template
[ ] List/manage templates
[ ] Start workout from template (pre-loads exercises)
[ ] Public templates (browse others')

Frontend:
[ ] Templates page
[ ] "Save as template" button on workout detail
[ ] Template detail + start workout button
[ ] "My Templates" section
```

### Week 6: Social Features
```
Priority: MEDIUM-HIGH
Reason: Retention booster — accountability + community

Backend:
[ ] Follow/unfollow users
[ ] Activity feed posts (auto-created on workout/PR/achievement)
[ ] Feed likes + comments
[ ] Public profile pages

Frontend:
[ ] Social feed page
[ ] Activity cards (workout, PR, achievement types)
[ ] Like + comment interactions
[ ] Public profile page
[ ] Follow/unfollow button
[ ] Followers/following lists
```

### Week 7: Challenges
```
Priority: MEDIUM
Reason: Engagement feature — drives weekly app opens

Backend:
[ ] Challenge CRUD (create, join, leave)
[ ] Challenge types: total_workouts, total_volume, streak
[ ] Challenge progress auto-update (background job)
[ ] Challenge leaderboard
[ ] Challenge result/winner logic

Frontend:
[ ] Challenges page (active, upcoming, past)
[ ] Challenge card (progress bar, rank, time left)
[ ] Create challenge modal
[ ] Challenge leaderboard view
```

### Week 8: Admin Panel + Notifications
```
Priority: HIGH (for a real app)
Reason: You need visibility + control over the platform

Backend:
[ ] Admin panel (FastAPI + Jinja2)
[ ] User management (list, suspend, activate, role)
[ ] Exercise library management (add/edit)
[ ] Platform analytics dashboard
[ ] Admin logs (all actions tracked)
[ ] Notification system (all types)
[ ] Notification settings per user
[ ] Streak warning job (daily 8PM)

Frontend:
[ ] Notifications bell + dropdown
[ ] Notifications page
[ ] Notification settings in profile settings
```

---

## 🟢 PHASE 3 — NICE-TO-HAVE (Weeks 9-12)
*Polish and advanced features. Only after Phase 1+2 are solid.*

### Week 9: Advanced Analytics
```
[ ] Volume progression chart
[ ] Muscle balance analysis (push/pull ratio)
[ ] Body composition trend
[ ] Nutrition adherence heatmap
[ ] Workout frequency patterns
[ ] Export data (CSV download)
```

### Week 10: Trainer Features
```
[ ] Trainer role (upgrade from user)
[ ] Trainer creates workout plans (multi-week programs)
[ ] Assign plan to follower
[ ] Client progress tracking (trainer views client data)
[ ] Trainer public profile (with bio + credentials)
```

### Week 11: Advanced Workout Features
```
[ ] Cardio tracking (distance, pace, heart rate)
[ ] Supersets (link exercises together)
[ ] Drop sets (auto-decrease weight)
[ ] Video guide for exercises (YouTube embed)
[ ] Custom exercises (per-user)
[ ] Workout notes photos (attach progress photo to workout)
```

### Week 12: Polish & Performance
```
[ ] Progressive Web App (PWA — installable on phone)
[ ] Offline workout logging (sync when back online)
[ ] Push notifications (browser)
[ ] Dark/light mode toggle
[ ] Language toggle (RU/EN)
[ ] Performance optimization (lazy loading, caching)
[ ] Comprehensive error monitoring (Sentry free tier)
[ ] App landing page (marketing page)
```

---

## 📊 FEATURE EFFORT MATRIX

| Feature              | Effort | Value | Build? |
|----------------------|--------|-------|--------|
| Auth + User profile  | Medium | High  | ✅ Week 1 |
| Workout logging      | High   | High  | ✅ Week 2 |
| Body metrics         | Low    | High  | ✅ Week 3 |
| Nutrition tracking   | Medium | High  | ✅ Week 3 |
| Gamification         | Medium | High  | ✅ Week 4 |
| Analytics charts     | Medium | High  | ✅ Week 4 |
| Templates            | Low    | High  | ✅ Week 5 |
| Social feed          | Medium | Medium| ✅ Week 6 |
| Challenges           | Medium | Medium| ✅ Week 7 |
| Admin panel          | Medium | High  | ✅ Week 8 |
| Notifications        | Medium | High  | ✅ Week 8 |
| Trainer features     | High   | Medium| ⏳ Week 10 |
| Cardio tracking      | Medium | Medium| ⏳ Week 11 |
| PWA + offline        | High   | Medium| ⏳ Week 12 |
| Video integration    | Low    | Low   | ⏳ Later |

---

## ⚠️ COMMON MISTAKES TO AVOID

```
❌ Building beautiful UI before the core feature works
✅ Make workout logging flawless first, pretty second

❌ Adding features while existing ones have bugs
✅ Fix bugs before building new features

❌ Building social before you use the app yourself
✅ Use the app daily for 2 weeks before social features

❌ Premature optimization (caching, indexing too early)
✅ Make it work first, then make it fast

❌ Skipping tests to "save time"
✅ Tests save time — they prevent debugging 3x longer later

❌ Building everything, finishing nothing
✅ Ship Phase 1 perfectly. Then ship Phase 2.
```

---

## 🏁 DEFINITION OF "DONE" FOR EACH PHASE

### Phase 1 is "done" when:
- You personally use it for 1 week straight to track real workouts
- All Phase 1 checklist items in FT_07_TESTING_GUIDE.md pass
- No 500 errors in normal usage
- Runs in Docker with one command

### Phase 2 is "done" when:
- 3 friends/people can register and use it independently
- Social features work across multiple accounts
- Admin can manage users and content

### Phase 3 is "done" when:
- You'd be comfortable showing it in a job interview
- It's deployed publicly and stable
- It works on mobile browser

---

## 📅 WEEKLY SCHEDULE (Sustainable Pace)

```
Monday:    Plan week, review docs, start new module (backend)
Tuesday:   Backend development + testing
Wednesday: Backend completion + frontend start
Thursday:  Frontend development + integration
Friday:    Integration testing + bug fixes + weekly review with Claude
Saturday:  Experiments, refactoring, learning
Sunday:    Rest (seriously, rest makes you more productive)

Daily routine:
- 1-2 hours min on project
- Start with: what did I do yesterday? what's today's goal?
- End with: update MASTER_PROJECT_TRACKER, note questions for Friday
```
