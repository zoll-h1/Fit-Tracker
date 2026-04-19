# FT_07 — TESTING GUIDE
# FitTracker | Test Every Feature Before Moving On

---

## 📋 PHILOSOPHY

**Test as you build. Never skip testing.**

Rule: After every module → run its test checklist before starting the next one.
This prevents "I'll test it all at the end" → finding 20 broken things at once.

---

## 🔧 TEST TOOLS

| Tool              | Use Case                           | Install         |
|-------------------|------------------------------------|-----------------|
| pytest + httpx    | FastAPI endpoint testing           | pip install     |
| Swagger UI        | Manual API testing (/docs)         | Built-in        |
| Postman/Insomnia  | Manual API testing (alternative)   | Download        |
| React DevTools    | Component state inspection         | Browser ext     |
| React Query Devtools | Query cache inspection          | npm install     |

---

## 🔐 MODULE 1 — AUTH TESTING

### Manual Tests (Swagger UI at localhost:8000/docs)

#### Registration
```
Test 1 — Happy path:
POST /api/auth/register
{
  "username": "testuser1",
  "email": "test1@example.com",
  "password": "TestPass123!",
  "full_name": "Test User",
  "date_of_birth": "2000-01-01",
  "gender": "male",
  "unit_system": "metric"
}
Expected: 200, tokens returned, user in response

Test 2 — Duplicate email:
Same body again
Expected: 400, "Email already registered"

Test 3 — Duplicate username:
Different email, same username
Expected: 400, "Username already taken"

Test 4 — Weak password:
password: "abc"
Expected: 422, validation error

Test 5 — Missing required field:
No email field
Expected: 422, validation error
```

#### Login
```
Test 6 — Happy path:
POST /api/auth/login { email, password }
Expected: 200, access_token and refresh_token returned

Test 7 — Wrong password:
Correct email, wrong password
Expected: 401, "Invalid credentials"
(NOT "wrong password" — don't reveal which field is wrong)

Test 8 — Wrong email:
Non-existent email
Expected: 401, "Invalid credentials"
(Same error as wrong password!)

Test 9 — Suspended user:
Suspend user via admin, try to login
Expected: 401, "Account suspended"
```

#### Token & Protected Routes
```
Test 10 — Valid token:
GET /api/auth/me with Authorization: Bearer <valid_token>
Expected: 200, user data (NO password_hash!)

Test 11 — No token:
GET /api/auth/me (no auth header)
Expected: 401

Test 12 — Invalid token:
Authorization: Bearer invalid.token.here
Expected: 401

Test 13 — Expired token:
Wait 30 minutes or manually create expired token
Expected: 401

Test 14 — Refresh token:
POST /api/auth/refresh { refresh_token: "valid_refresh" }
Expected: 200, new access_token

Test 15 — Use old refresh token after refresh:
Refresh once, try using same refresh token again
Expected: 401, "Token already used"
```

#### Rate Limiting
```
Test 16 — Rate limit:
POST /api/auth/login 6 times in under a minute with wrong password
Expected: 429 on 6th attempt with Retry-After header
```

---

## 🏋️ MODULE 2 — WORKOUT TESTING

```
Setup: Have valid JWT token from auth tests.

Test 1 — Start workout:
POST /api/workouts { "name": "Chest Day", "notes": "Feeling strong" }
Expected: 201, workout with id, status=in_progress, empty exercises

Test 2 — Add exercise to workout:
POST /api/workouts/{id}/exercises
{ "exercise_library_id": 1, "exercise_order": 1, "rest_seconds": 90 }
Expected: 201, exercise added

Test 3 — Log a set:
POST /api/workouts/{id}/exercises/{ex_id}/sets
{ "set_number": 1, "set_type": "normal", "weight_kg": 80, "reps": 8, "completed": true }
Expected: 201, set created

Test 4 — Log multiple sets:
Add 3 more sets
Expected: All saved, set numbers increment

Test 5 — Finish workout:
POST /api/workouts/{id}/finish
Expected: 200, workout with:
- status = "completed"
- duration_seconds calculated
- total_volume_kg = sum(weight*reps)
- finished_at set

Test 6 — View history:
GET /api/workouts
Expected: List with finished workout, shows exercises+sets count

Test 7 — Ownership check:
Login as different user (user2)
GET /api/workouts/{id} (from user1's workout)
Expected: 403 Forbidden

Test 8 — Delete another user's workout:
DELETE /api/workouts/{id} as user2
Expected: 403

Test 9 — Can't edit finished workout name:
PUT /api/workouts/{id} on completed workout
Expected: 400, "Cannot edit completed workout"
```

---

## 📏 MODULE 3 — BODY METRICS TESTING

```
Test 1 — Log metrics:
POST /api/body-metrics
{ "weight_kg": 75.5, "body_fat_percentage": 15.2, "waist_cm": 82 }
Expected: 201, entry created, BMI auto-calculated

Test 2 — Get latest:
GET /api/body-metrics/latest
Expected: Most recent entry

Test 3 — Progress data:
GET /api/body-metrics/progress?metric=weight&period=90d
Expected: Array of {date, value} objects

Test 4 — Set goal:
POST /api/body-metrics/goals
{ "metric_type": "weight", "target_value": 70.0, "target_date": "2025-12-31" }
Expected: 201, goal created

Test 5 — Goal auto-completed:
Log weight_kg: 70.0
GET /api/body-metrics/goals
Expected: Goal shows is_achieved: true, achievement notification created
```

---

## 🥗 MODULE 4 — NUTRITION TESTING

```
Test 1 — Search food:
GET /api/nutrition/foods/search?q=chicken
Expected: List of food items with macros

Test 2 — Log meal:
POST /api/nutrition/meals
{ "food_item_id": 1, "quantity_g": 200, "meal_type": "lunch" }
Expected: 201, macros auto-calculated from quantity_g

Test 3 — Today's meals:
GET /api/nutrition/meals/today
Expected: All today's meals, sum of calories/macros

Test 4 — Daily summary:
GET /api/nutrition/summary?date=2025-01-15
Expected: { eaten_calories, goal_calories, protein_g, carbs_g, fat_g, adherence_pct }

Test 5 — Custom food:
POST /api/nutrition/foods/custom
{ "name": "My Protein Shake", "calories_per_100g": 380, "protein_per_100g": 75 }
Expected: Food created, only visible to this user
```

---

## 🏆 MODULE 5 — GAMIFICATION TESTING

```
Setup: Complete a workout to trigger XP

Test 1 — XP awarded after workout:
Complete workout → GET /api/gamification/profile
Expected: total_xp increased by 50

Test 2 — PR gives bonus XP:
Log a weight that is new PR for exercise
Expected: +100 XP, notification created

Test 3 — Streak tracking:
Log workout today → GET /api/gamification/streaks
Expected: current_streak = 1 (or +1 if had streak)

Test 4 — Achievement earned:
Complete 1 workout (should earn "First Workout" achievement)
GET /api/gamification/achievements/my
Expected: "First Workout" achievement in list with earned_at

Test 5 — Level up:
Award enough XP to hit level 2 threshold (500 XP)
Expected: current_level updated to 2, level_up notification created

Test 6 — Duplicate achievement not awarded:
Complete second workout
GET /api/gamification/achievements/my
Expected: "First Workout" still only appears once
```

---

## 👥 MODULE 6 — SOCIAL TESTING

```
Setup: Two users (user1, user2)

Test 1 — Follow user:
user1 → POST /api/social/follow/{user2_id}
Expected: 200, following created

Test 2 — Can't follow self:
user1 → POST /api/social/follow/{user1_id}
Expected: 400, "Cannot follow yourself"

Test 3 — Duplicate follow:
user1 follows user2 again
Expected: 400, "Already following"

Test 4 — Feed shows followed user's workouts:
user2 completes workout
user1 → GET /api/social/feed
Expected: user2's workout in feed

Test 5 — Unfollow:
user1 → DELETE /api/social/follow/{user2_id}
Expected: 200, following removed
user1 → GET /api/social/feed
Expected: user2's workout no longer in feed

Test 6 — Public profile:
GET /api/users/{user2_id}/profile (no auth)
Expected: Public info only (no email!)

Test 7 — Like activity:
POST /api/social/feed/{activity_id}/like
Expected: like count increases
POST again (toggle)
Expected: like count decreases
```

---

## 🔔 MODULE 7 — NOTIFICATIONS TESTING

```
Test 1 — Notification created on workout complete:
Complete workout → GET /api/notifications
Expected: "workout_completed" notification present

Test 2 — Achievement notification:
Earn achievement → GET /api/notifications
Expected: "achievement_earned" notification present

Test 3 — Unread count:
GET /api/notifications/unread-count
Expected: count > 0

Test 4 — Mark as read:
PUT /api/notifications/{id}/read
GET /api/notifications/unread-count
Expected: count decreased by 1

Test 5 — Mark all read:
PUT /api/notifications/read-all
GET /api/notifications/unread-count
Expected: count = 0

Test 6 — Notification settings respected:
PUT /api/notifications/settings { "social_alerts": false }
Someone follows you → GET /api/notifications
Expected: no "new_follower" notification created
```

---

## 🛡️ SECURITY TESTS (Run on EVERY module)

```
For each protected endpoint:

TEST: No auth → 401
Trigger: Request without Authorization header
Expected: 401 Unauthorized

TEST: Invalid token → 401
Trigger: Authorization: Bearer garbage_token
Expected: 401

TEST: Access other user's data → 403
Setup: Create resource as user1, request as user2
Expected: 403 Forbidden (NOT 404 or 200)

TEST: SQL injection attempt
Trigger: email = "admin@test.com'; DROP TABLE users; --"
Expected: 422 validation error (Pydantic catches this)
OR: 200 but returns empty result (parameterized query works)

TEST: Oversized input
Trigger: name = "a" * 10000
Expected: 422 validation error (Pydantic max_length catches this)

TEST: Negative numeric values
Trigger: weight_kg = -50
Expected: 422 validation error

TEST: Password not in response
Register and login, check ALL responses
Expected: password_hash field NEVER appears in any response
```

---

## 🖥️ FRONTEND TESTING CHECKLIST

### Auth Flow
```
[ ] Register with valid data → land on dashboard
[ ] Register with duplicate email → show error message
[ ] Login → land on dashboard
[ ] Wrong password → show "Invalid credentials" (NOT which field is wrong)
[ ] Token auto-refresh: wait 30min or manually expire → next action should work silently
[ ] Logout → redirect to login, token cleared
[ ] Protected page without login → redirect to login
```

### Active Workout Flow (Most Critical)
```
[ ] Start workout → see timer counting up
[ ] Add exercise → search works, exercise added to list
[ ] Log set → checkmark marks complete, rest timer starts
[ ] Rest timer → countdown shows, skip button works
[ ] Previous performance hints show in gray
[ ] Finish workout → summary modal shows correct stats
[ ] Workout appears in history
[ ] PR achieved → badge shows on that set
```

### Analytics
```
[ ] Dashboard loads with real data (not placeholder)
[ ] Charts render correctly with real data
[ ] Period filter changes chart data
[ ] Heatmap shows correct days with workouts
[ ] PR table shows correct bests
```

### Responsiveness
```
[ ] Works on mobile (375px width)
[ ] Bottom nav appears on mobile
[ ] Charts resize correctly on mobile
[ ] No horizontal scroll on any page
[ ] Touch targets are large enough (44px minimum)
```

---

## 🚀 PRE-LAUNCH CHECKLIST

Before calling the app "done":

```
SECURITY:
[ ] All endpoints tested for auth/authorization
[ ] SQL injection tests passed
[ ] File upload type validation works
[ ] Rate limiting on auth endpoints works
[ ] .env not in git
[ ] password_hash never in any response

FUNCTIONALITY:
[ ] Complete user journey works end-to-end
[ ] All CRUD operations work for all resources
[ ] Error messages are user-friendly (not "Internal Server Error")
[ ] Empty states show correctly (no workouts yet, etc.)

PERFORMANCE:
[ ] Dashboard loads in < 2 seconds
[ ] Workout screen responds instantly to set logging
[ ] Pagination works (test with large dataset)

RELIABILITY:
[ ] App doesn't crash on refresh (React Query cache)
[ ] Token refresh works silently
[ ] Offline action shows proper error (not white screen)

ADMIN:
[ ] Admin login works
[ ] Can suspend/activate users
[ ] Reports queue works
[ ] Exercise library management works
[ ] Dashboard shows real data
```
