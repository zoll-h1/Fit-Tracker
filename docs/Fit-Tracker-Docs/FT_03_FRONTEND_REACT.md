# FT_03 — FRONTEND (REACT + VITE)
# FitTracker | React 18 + Vite + Tailwind CSS

---

## ⚙️ TECH STACK

| Layer          | Technology                              |
|----------------|-----------------------------------------|
| Framework      | React 18 + Vite 5                       |
| Language       | TypeScript                              |
| Styling        | Tailwind CSS + shadcn/ui components     |
| State          | Zustand (global) + React Query (server) |
| Routing        | React Router v6                         |
| Forms          | React Hook Form + Zod validation        |
| Charts         | Recharts                                |
| HTTP Client    | Axios + React Query                     |
| Icons          | Lucide React                            |
| Animations     | Framer Motion                           |
| Date Handling  | date-fns                                |
| i18n           | react-i18next (EN + RU)                 |

---

## 📁 PROJECT STRUCTURE

```
frontend/
├── src/
│   ├── main.tsx
│   ├── App.tsx                   # Routes + providers
│   │
│   ├── api/
│   │   ├── client.ts             # Axios instance + interceptors
│   │   ├── auth.ts
│   │   ├── workouts.ts
│   │   ├── exercises.ts
│   │   ├── body-metrics.ts
│   │   ├── nutrition.ts
│   │   ├── social.ts
│   │   ├── analytics.ts
│   │   └── gamification.ts
│   │
│   ├── hooks/
│   │   ├── useAuth.ts
│   │   ├── useWorkout.ts
│   │   ├── useAnalytics.ts
│   │   └── useNotifications.ts
│   │
│   ├── stores/
│   │   ├── authStore.ts          # Zustand auth state
│   │   ├── workoutStore.ts       # Active workout state
│   │   └── settingsStore.ts      # UI preferences
│   │
│   ├── pages/
│   │   ├── auth/
│   │   │   ├── LoginPage.tsx
│   │   │   ├── RegisterPage.tsx
│   │   │   └── ForgotPasswordPage.tsx
│   │   ├── dashboard/
│   │   │   └── DashboardPage.tsx
│   │   ├── workouts/
│   │   │   ├── WorkoutsPage.tsx
│   │   │   ├── WorkoutDetailPage.tsx
│   │   │   ├── ActiveWorkoutPage.tsx
│   │   │   └── TemplatesPage.tsx
│   │   ├── exercises/
│   │   │   ├── ExerciseLibraryPage.tsx
│   │   │   └── ExerciseDetailPage.tsx
│   │   ├── body-metrics/
│   │   │   └── BodyMetricsPage.tsx
│   │   ├── nutrition/
│   │   │   └── NutritionPage.tsx
│   │   ├── analytics/
│   │   │   └── AnalyticsPage.tsx
│   │   ├── social/
│   │   │   ├── FeedPage.tsx
│   │   │   ├── LeaderboardPage.tsx
│   │   │   └── ChallengesPage.tsx
│   │   ├── profile/
│   │   │   ├── ProfilePage.tsx
│   │   │   ├── PublicProfilePage.tsx
│   │   │   └── SettingsPage.tsx
│   │   └── gamification/
│   │       └── AchievementsPage.tsx
│   │
│   ├── components/
│   │   ├── layout/
│   │   │   ├── AppLayout.tsx     # Main layout with sidebar
│   │   │   ├── Sidebar.tsx
│   │   │   ├── TopBar.tsx
│   │   │   └── MobileNav.tsx
│   │   ├── workout/
│   │   │   ├── WorkoutCard.tsx
│   │   │   ├── ExerciseSetRow.tsx
│   │   │   ├── WorkoutTimer.tsx
│   │   │   └── SetLogger.tsx
│   │   ├── charts/
│   │   │   ├── StrengthProgressChart.tsx
│   │   │   ├── VolumeChart.tsx
│   │   │   ├── BodyWeightChart.tsx
│   │   │   ├── MuscleHeatmap.tsx
│   │   │   └── CalendarHeatmap.tsx
│   │   ├── gamification/
│   │   │   ├── XPBar.tsx
│   │   │   ├── LevelBadge.tsx
│   │   │   ├── AchievementCard.tsx
│   │   │   └── StreakBadge.tsx
│   │   ├── social/
│   │   │   ├── ActivityCard.tsx
│   │   │   ├── UserCard.tsx
│   │   │   └── ChallengeCard.tsx
│   │   └── ui/
│   │       ├── LoadingSpinner.tsx
│   │       ├── EmptyState.tsx
│   │       ├── ConfirmDialog.tsx
│   │       └── ImageUpload.tsx
│   │
│   ├── types/
│   │   ├── auth.ts
│   │   ├── workout.ts
│   │   ├── exercise.ts
│   │   ├── nutrition.ts
│   │   └── social.ts
│   │
│   ├── utils/
│   │   ├── formatters.ts         # Duration, weight, date formatters
│   │   ├── validators.ts
│   │   └── constants.ts
│   │
│   └── i18n/
│       ├── index.ts
│       ├── en.json
│       └── ru.json
│
├── public/
├── index.html
├── vite.config.ts
├── tailwind.config.ts
├── tsconfig.json
└── package.json
```

---

## 🎨 DESIGN SYSTEM

### Color Palette
```css
/* Primary — Energetic Blue */
--primary: #3B82F6;
--primary-dark: #2563EB;
--primary-light: #EFF6FF;

/* Accent — Fitness Orange */
--accent: #F97316;
--accent-dark: #EA580C;

/* Success — Green */
--success: #22C55E;

/* Warning — Yellow */
--warning: #EAB308;

/* Background */
--bg-primary: #0F172A;      /* Dark mode main */
--bg-secondary: #1E293B;    /* Dark mode card */
--bg-tertiary: #334155;     /* Dark mode input */

/* Text */
--text-primary: #F8FAFC;
--text-secondary: #94A3B8;
--text-muted: #64748B;
```

> Default to DARK MODE. Light mode optional.

### Typography
```
Headings: Inter Bold
Body: Inter Regular
Monospace (weights): JetBrains Mono (for numbers like 100kg, 15 reps)
```

---

## 🔐 PAGE 1 — AUTH SCREENS

### CODEX PROMPT — Auth Pages
```
Create React TypeScript auth pages for fitness app:

LoginPage:
- Logo + "FitTracker" heading
- Email input (with validation)
- Password input (show/hide toggle)
- "Remember me" checkbox
- Login button with loading state
- "Forgot password?" link
- "Don't have an account? Register" link
- Error message display (invalid credentials)
- On success: store token in Zustand + localStorage, redirect to /dashboard

RegisterPage:
- Full name, username, email, password, confirm password
- Date of birth (date picker)
- Gender selector (Male/Female/Other)
- Unit system toggle (Metric/Imperial)
- Height + Weight inputs (convert based on unit system)
- Terms acceptance checkbox
- Register button
- Success: auto-login, show "Welcome!" toast, redirect to /dashboard

Use React Hook Form + Zod for validation.
Use Zustand authStore for: { user, accessToken, setAuth, logout }
Axios interceptor: attach Bearer token to all requests.
On 401 response: try refresh token, if fail → logout.
Tailwind + shadcn/ui components. Dark background #0F172A.
```

---

## 🏠 PAGE 2 — DASHBOARD

### Layout
```
┌─────────────────────────────────────────────────────┐
│ TOP BAR: Logo | Search | 🔔 Notifications | Avatar  │
├──────────┬──────────────────────────────────────────┤
│ SIDEBAR  │  MAIN CONTENT                            │
│ • Home   │  ┌──────────────────────────────────────┐│
│ • Workout│  │ Greeting + XP Bar + Level             ││
│ • Body   │  ├──────────────────────────────────────┤│
│ • Food   │  │ Stats Row: Workouts | Volume | Streak ││
│ • Charts │  ├──────────────────────────────────────┤│
│ • Social │  │ Recent Workouts (last 5)              ││
│ • Trophy │  ├──────────────────────────────────────┤│
│ • Profile│  │ Progress Charts (weight + strength)   ││
│          │  ├──────────────────────────────────────┤│
│          │  │ Muscle Groups This Week (heatmap)     ││
│          │  ├──────────────────────────────────────┤│
│          │  │ Recent Achievements                  ││
│          │  └──────────────────────────────────────┘│
└──────────┴──────────────────────────────────────────┘
```

### CODEX PROMPT — Dashboard
```
Create React Dashboard page for fitness tracker:

Components:
1. WelcomeHeader: "Good morning, John! 💪" with current date
2. XPProgressBar: show current XP / XP needed for next level, animated fill
3. StatsRow: 4 cards: This Week Workouts | Total Volume kg | Current Streak | Goals Met %
4. RecentWorkouts: last 5 workout cards (name, date, duration, exercises count)
5. StrengthProgress: Recharts LineChart for top 3 lifts (bench/squat/deadlift) last 30d
6. WeeklyCalendar: 7-day strip showing which days had workouts (color dots)
7. MuscleHeatmap: simple body diagram with colored muscle groups (SVG, color intensity = frequency)
8. QuickLog button: floating "Start Workout" button → navigate to /workouts/active

Use React Query to fetch:
- GET /api/analytics/dashboard
- GET /api/workouts?limit=5
- GET /api/analytics/strength?period=30d
- GET /api/gamification/profile

Loading skeletons for all cards.
Responsive: sidebar collapses to bottom nav on mobile.
```

---

## 🏋️ PAGE 3 — ACTIVE WORKOUT (Most Critical)

### CODEX PROMPT — Active Workout
```
Create React Active Workout page (the core of the app):

This is the workout logging screen. User is actively doing a workout.

State (Zustand workoutStore):
- session: { id, name, started_at, exercises: [] }
- isActive: boolean
- elapsed: number (seconds, auto-increment timer)

Layout:
┌──────────────────────────────────┐
│ ← Back  "Chest Day"  ⏱ 00:23:15 │
│                    [Finish] btn  │
├──────────────────────────────────┤
│ + Add Exercise                   │
├──────────────────────────────────┤
│ Exercise 1: Bench Press          │
│ Set  Type  Weight  Reps  ✓       │
│  1   N     80kg    8    ✓ done   │
│  2   N     80kg    8    ○        │
│  3   N     85kg    6    ○        │
│ [+ Add Set]                      │
├──────────────────────────────────┤
│ Exercise 2: Push-up              │
│ ...                              │
└──────────────────────────────────┘

Features:
- Auto-save every set to API immediately (POST /api/workouts/{id}/exercises/{ex_id}/sets)
- Workout timer (counting up, show minutes:seconds)
- Rest timer: tap set done → start configurable rest countdown (60s default)
- Each set row: set number | dropdown (normal/warmup/dropset/failure) | weight input | reps input | checkmark
- Weight input: tap to edit, shows keyboard
- "Previous" hint: show last session's weight/reps for same exercise in gray
- Add Exercise: open modal to search exercise library
- Finish Workout: show summary (total volume, exercises, duration, PRs achieved), then navigate to /workouts/{id}
- Cancel: confirm dialog → delete session

API calls:
- POST /api/workouts (start session, get id)
- POST /api/workouts/{id}/exercises (add exercise)
- POST /api/workouts/{id}/exercises/{ex_id}/sets (log set immediately on checkmark tap)
- POST /api/workouts/{id}/finish
```

---

## 📊 PAGE 4 — ANALYTICS

### CODEX PROMPT — Analytics Page
```
Create comprehensive Analytics page with React + Recharts:

Tabs: Overview | Strength | Body | Nutrition | Muscles

Tab 1 — Overview:
- Period selector: 7d / 30d / 90d / 1y
- Line chart: workouts per week (bar chart better)
- Stats: total workouts, total hours, total volume, avg duration
- Streak calendar (GitHub-style heatmap, 365 days)

Tab 2 — Strength:
- Exercise selector dropdown
- Line chart: max weight over time for selected exercise
- Show PR annotation on chart
- Table: top PRs for all exercises

Tab 3 — Body:
- Multi-line chart: weight, body fat %, muscle mass over time
- Goal progress bars (current vs target)
- BMI trend + status label

Tab 4 — Nutrition:
- Bar chart: daily calories this week (vs target line)
- Macro breakdown: pie chart (protein/carbs/fat)
- Weekly adherence % (days hit calorie goal)

Tab 5 — Muscles:
- Last 7/30/90 days filter
- Bar chart: sets per muscle group
- "Muscle balance" indicator (push vs pull ratio)

Use React Query for all chart data.
Use Recharts: LineChart, BarChart, PieChart, AreaChart.
Loading skeleton for each chart.
Tooltips on hover with formatted values (e.g. "85.5 kg, Jan 15").
```

---

## 👤 PAGE 5 — PROFILE & SETTINGS

### CODEX PROMPT — Profile Pages
```
Create Profile and Settings pages:

ProfilePage (/profile):
- Avatar with upload button (ImageUpload component)
- Name, username, bio
- Stats summary: total workouts, followers, following
- Level badge + XP progress
- Achievement showcase (top 6 badges)
- Recent workout history (last 10)
- Edit profile button → opens edit form modal

PublicProfilePage (/profile/:userId):
- Same layout but readonly
- Follow/Unfollow button
- Only show public data

SettingsPage (/settings):
Tabs: Account | Preferences | Notifications | Privacy

Account tab:
- Change email (requires password confirm)
- Change password
- Delete account (requires typing "DELETE")

Preferences tab:
- Unit system toggle (Metric kg/cm vs Imperial lb/in)
- Language toggle (English/Russian)
- Default rest time (30s, 60s, 90s, 120s, custom)
- Dark/Light mode toggle

Notifications tab:
- Toggle each notification type on/off
- Email notifications toggle

Privacy tab:
- Profile visibility (Public/Followers only/Private)
- Allow workout feed posts (toggle)
```

---

## 🥗 PAGE 6 — NUTRITION TRACKER

### CODEX PROMPT — Nutrition Page
```
Create Nutrition tracking page:

Layout:
- Date picker (navigate days)
- Daily summary card: Calories eaten vs target (ring chart), Protein/Carbs/Fat bars
- Meal sections: Breakfast | Lunch | Dinner | Snacks
  Each section: list logged items, total calories, "+ Add food" button
- Water tracker: input + glass icons (8 glasses = target)

Add Food Modal:
- Search food (GET /api/nutrition/foods/search?q=)
- Show results: name, calories per 100g, macros
- Tap result → quantity input (in grams)
- Save → POST /api/nutrition/meals
- "+ Custom food" link at bottom of search

NutritionGoals:
- Side panel or separate tab
- Input: calorie target, protein/carbs/fat targets
- Save button

Use React Query for:
- GET /api/nutrition/meals/today
- GET /api/nutrition/goals
- GET /api/nutrition/summary?date=...
Optimistic updates when logging food.
```

---

## 🏆 PAGE 7 — GAMIFICATION

### CODEX PROMPT — Achievements Page
```
Create Gamification/Achievements page:

Layout:
Top section:
- Large level badge (e.g. "Level 7 — Iron Athlete")
- XP progress bar with sparkle animation at milestones
- Current streak with flame icon 🔥
- Total XP earned

Achievements section:
- Category filter tabs: All | Workout | Strength | Consistency | Social | Nutrition
- Grid of achievement cards:
  - Earned: full color, icon, name, description, date earned, XP badge
  - Locked: grayscale, lock icon, progress bar showing % to unlock
- Sort: Recent | XP value | Category

Leaderboard section:
- Toggle: Weekly | All-time
- Top 10 list with rank, avatar, name, level, XP/streak
- Highlight current user's position
- Show current user even if outside top 10

Recent XP activity:
- Timeline: "+50 XP — Completed Workout (2h ago)"
- Last 10 XP events

Animations:
- Achievement unlock: confetti + scale animation (Framer Motion)
- Level up: full screen overlay with level badge animation
```

---

## 👥 PAGE 8 — SOCIAL FEED

### CODEX PROMPT — Social Pages
```
Create Social Feed and Leaderboard pages:

FeedPage (/social):
- Activity cards from followed users:
  - Workout completed: avatar + "John completed Chest Day (1h 20m, 8 exercises)"
  - PR achieved: "John hit a new PR: 100kg Bench Press! 🏆"
  - Achievement earned: "John earned 'Iron Consistency' badge!"
  - Goal reached: "John reached their weight goal! 🎯"
- Like button + count, Comment button + count
- Comment section: collapsible, simple text input
- "Follow more people" prompt if < 3 following

Discover tab:
- Search users by username
- Suggested users to follow (top XP this week)

ChallengesPage (/challenges):
- Active challenges list:
  - Card: name, type, end date, participants, your rank/progress
  - Progress bar toward target
  - Join/Leave button
- Create Challenge button (modal):
  - Name, type (workouts/volume/streak), target, start/end date, public toggle

Use React Query + infinite scroll for feed.
```

---

## 🔌 API CLIENT SETUP

### CODEX PROMPT — API Layer
```
Create Axios API client with TypeScript for FitTracker:

api/client.ts:
- Base URL from env: VITE_API_URL
- Default headers: Content-Type: application/json
- Request interceptor: attach Authorization: Bearer <token> from Zustand authStore
- Response interceptor:
  - On 401: attempt token refresh (POST /api/auth/refresh with refresh_token)
  - If refresh succeeds: update store + retry original request
  - If refresh fails: logout user, redirect to /login
  - On 500: show toast "Server error, please try again"

authStore.ts (Zustand):
const useAuthStore = create<AuthState>()(persist(
  (set) => ({
    user: null,
    accessToken: null,
    refreshToken: null,
    setAuth: (user, accessToken, refreshToken) => set({user, accessToken, refreshToken}),
    logout: () => set({user: null, accessToken: null, refreshToken: null}),
  }),
  { name: 'fittracker-auth', storage: createJSONStorage(() => localStorage) }
))

workoutStore.ts (Zustand) — NOT persisted:
- activeSession: WorkoutSession | null
- startSession, addExercise, addSet, updateSet, endSession

React Query setup:
- queryClient with staleTime: 5 * 60 * 1000 (5 min)
- Auto refetch on window focus: false (saves API calls for workout screen)
- Retry: 1 (not 3, saves API calls)
```

---

## 📱 RESPONSIVE DESIGN RULES

```
Mobile (< 768px):
- Bottom navigation bar (5 icons): Home, Workout, Log, Social, Profile
- No sidebar
- Cards stack vertically
- Tables → cards

Tablet (768px - 1024px):
- Collapsible sidebar (icon only)
- 2-column grids

Desktop (> 1024px):
- Full sidebar with labels
- 3-column grids where appropriate
- Side panels for details

PRIORITY: Mobile-first. Most users will log workouts on their phone.
```

---

## 🌍 INTERNATIONALIZATION (i18n)

```json
// en.json (sample structure)
{
  "auth": {
    "login": "Login",
    "register": "Register",
    "email": "Email address",
    "password": "Password",
    "forgotPassword": "Forgot your password?"
  },
  "workout": {
    "startWorkout": "Start Workout",
    "finishWorkout": "Finish Workout",
    "addExercise": "Add Exercise",
    "restTimer": "Rest Timer",
    "sets": "Sets",
    "reps": "Reps",
    "weight": "Weight"
  },
  "analytics": {
    "strengthProgress": "Strength Progress",
    "bodyMetrics": "Body Metrics",
    "personalRecords": "Personal Records"
  }
}
```

---

## ⚠️ STRICT RULES FOR CODEX

1. TypeScript strict mode — no `any` types
2. All API calls via React Query (no raw useEffect for data fetching)
3. Loading + error + empty states for EVERY data display
4. No hardcoded colors — use Tailwind tokens only
5. No console.log in production code
6. Responsive by default (mobile-first)
7. Accessible: ARIA labels on icon buttons
8. Optimistic updates for fast feel (likes, set completion)
9. All forms validated with Zod before submit
10. Handle token refresh silently — user should never be randomly logged out
