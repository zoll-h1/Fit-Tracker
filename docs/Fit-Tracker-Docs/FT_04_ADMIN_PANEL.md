# FT_04 — ADMIN PANEL
# FitTracker | FastAPI + Jinja2 + Bootstrap 5

---

## 🎯 OVERVIEW

The admin panel is a **server-rendered web app** using FastAPI + Jinja2 templates.
No separate React app. Runs at `/admin` on the same FastAPI backend.

Why server-rendered:
- Simpler to build (no API integration)
- Faster to implement (less code)
- Secure by default (server-side session)
- No CORS issues

---

## 📁 STRUCTURE

```
app/
├── templates/
│   ├── admin/
│   │   ├── base.html               # Layout with sidebar + navbar
│   │   ├── login.html
│   │   ├── dashboard.html
│   │   ├── users/
│   │   │   ├── list.html
│   │   │   └── detail.html
│   │   ├── exercises/
│   │   │   ├── list.html
│   │   │   └── form.html
│   │   ├── reports/
│   │   │   └── list.html
│   │   ├── analytics/
│   │   │   └── index.html
│   │   └── logs/
│   │       └── list.html
│   └── admin_errors/
│       ├── 403.html
│       └── 404.html
├── routers/
│   └── admin.py                    # All admin routes
└── static/
    └── admin/
        ├── css/custom.css
        └── js/charts.js
```

---

## 🔐 AUTH

Admin panel uses **HTTP-only session cookies** (NOT JWT).

```python
# Session-based auth (more secure for browser-based admin)
# Session data: { admin_id, admin_role, expires_at }

# Login: POST /admin/login
# Verify role == "admin"
# Set session cookie (http-only, secure, samesite=lax)

# Middleware: check session on every /admin/* request
# Invalid session → redirect to /admin/login
```

---

## 🖥️ PAGES

### 1. Login (`/admin/login`)

```html
Clean centered form:
- FitTracker Admin logo
- Email + Password inputs
- Login button
- Error message display
- Dark theme (matches main app)
```

### 2. Dashboard (`/admin/dashboard`)

```
Stats Cards (top row):
┌───────────┐ ┌───────────┐ ┌───────────┐ ┌───────────┐
│ Total     │ │ Active    │ │ Workouts  │ │ Reports   │
│ Users     │ │ Today     │ │ This Week │ │ Pending   │
│   1,234   │ │    87     │ │   3,451   │ │     5     │
└───────────┘ └───────────┘ └───────────┘ └───────────┘

Charts Row:
┌──────────────────────────┐ ┌──────────────────────────┐
│ New Users (last 30 days) │ │ Workouts per Day (30d)   │
│ Line chart               │ │ Bar chart                │
└──────────────────────────┘ └──────────────────────────┘

Bottom Row:
┌─────────────────────────────┐ ┌────────────────────────────┐
│ Recent Reports (5)          │ │ Top Active Users (10)      │
│ link to resolve each        │ │ username | workouts | XP   │
└─────────────────────────────┘ └────────────────────────────┘
```

### CODEX PROMPT — Admin Dashboard
```
Create FastAPI admin dashboard route with Jinja2 template:

Route: GET /admin/dashboard
Context variables to pass to template:
{
  total_users, new_users_today, new_users_week,
  active_users_today (logged workout today),
  total_workouts, workouts_today, workouts_week,
  pending_reports,
  new_users_chart: [{"date": "2025-01-01", "count": 5}, ...] (last 30 days),
  workouts_chart: [{"date": "2025-01-01", "count": 12}, ...],
  recent_reports: [...],
  top_users: [{"username": "...", "workouts": 45, "xp": 3400}, ...] (top 10 this month)
}

Template: admin/dashboard.html using Bootstrap 5 cards + Chart.js for charts.
Sidebar navigation with links to all admin sections.
```

---

### 3. Users (`/admin/users`)

```
Features:
- Sortable table: ID | Avatar | Username | Email | Role | Status | Joined | Last Active | Actions
- Search: by email or username (query param ?search=)
- Filter: by role (user/premium/trainer/admin), by status (active/suspended)
- Pagination (50 per page)
- Per-user actions: View | Suspend | Activate | Change Role
```

### CODEX PROMPT — Users Management
```
Create admin users management with FastAPI + Jinja2:

GET /admin/users
- Query params: search, role_filter, status_filter, page
- Return paginated users with total count
- Template: table with sortable columns, Bootstrap badges for role/status

GET /admin/users/{id}
- Full user detail: profile, stats (total workouts, XP, streak), account info
- Action buttons: Suspend, Activate, Change Role, View Workouts
- Recent activity log (last 10 actions from admin_logs)

POST /admin/users/{id}/suspend
- Body: { reason: "spam" }
- Set user.is_active = False
- Log action to admin_logs
- Redirect back with success flash message

POST /admin/users/{id}/activate
- Set user.is_active = True
- Log action

POST /admin/users/{id}/role
- Body: { new_role: "premium" }
- Validate role is valid enum
- Update role, log action

Use Bootstrap modal for confirmation before suspend/activate.
Flash messages for success/error feedback.
```

---

### 4. Exercise Library (`/admin/exercises`)

```
Most used admin feature — maintain the global exercise database.

Table: Name | Category | Difficulty | Equipment | Muscles | Custom? | Actions
Filter: category, difficulty, equipment
Search: exercise name

Actions:
- Add Exercise (form)
- Edit Exercise (same form pre-filled)
- Delete Exercise (with confirmation)
- Approve custom exercises submitted by users
```

### CODEX PROMPT — Exercise Library Admin
```
Create admin exercise library management:

GET /admin/exercises
- Table with all exercises
- Filter by category/difficulty/is_custom
- Search by name
- "Add Exercise" button

GET /admin/exercises/create → form
POST /admin/exercises/create → save + redirect

GET /admin/exercises/{id}/edit → form pre-filled
POST /admin/exercises/{id}/edit → update + redirect

POST /admin/exercises/{id}/delete → soft delete (set is_active=False)

Exercise form fields:
- Name (required)
- Category (select: strength/cardio/flexibility/balance)
- Difficulty (select: beginner/intermediate/advanced)
- Primary muscles (multi-select checkboxes)
- Secondary muscles (multi-select checkboxes)
- Equipment (multi-select checkboxes)
- Force type (select: push/pull/static/none)
- Instructions (textarea)
- Video URL (optional)
- MET value (number input, for calorie calculation)

Use Bootstrap forms + validation.
```

---

### 5. Reports (`/admin/reports`)

```
Queue of user reports to review.

Table: ID | Reporter | Target | Type | Reason | Date | Status | Actions
Filter: status (pending/resolved), target_type (user/workout)

Actions per report:
- Dismiss (mark resolved, no action)
- Warn User (send notification to reported user)
- Suspend User (if target is user)
- View Target (link to user or workout)
```

### CODEX PROMPT — Reports Management
```
Create admin reports queue:

GET /admin/reports
- Show pending reports first
- Filter by status, target_type
- Show: reporter username, target info, reason, description, date

POST /admin/reports/{id}/dismiss
- Set status = "dismissed", resolved_by = admin_id, resolved_at = now
- Log action

POST /admin/reports/{id}/warn
- Set report status = "resolved_warned"
- Create notification for reported user: "Your content was reported and reviewed"
- Log action

POST /admin/reports/{id}/suspend-user
- Suspend the reported user
- Resolve the report
- Log action
- Show confirmation modal before suspending

Use color badges: pending=yellow, resolved=green, dismissed=gray
```

---

### 6. Platform Analytics (`/admin/analytics`)

```
Platform-wide metrics for admin insights.

Section 1: User Growth
- New registrations per day (last 90 days) — Line chart
- Total users by role breakdown — Pie chart
- Retention rate (users who logged workout in last 7 days)

Section 2: Engagement
- Daily active users (last 30 days)
- Average workouts per user per week
- Most popular exercises (top 10 bar chart)
- Most popular muscle groups

Section 3: Content
- Total workouts logged per day (last 30 days)
- Top workout templates by usage
- Leaderboard: top 20 users by XP this month

Section 4: Feature Usage
- Nutrition feature adoption %
- Body metrics feature adoption %
- Social feature adoption %
```

### CODEX PROMPT — Admin Analytics
```
Create admin analytics page:

GET /admin/analytics
SQL aggregation queries:

1. New users per day: 
   SELECT DATE(created_at), COUNT(*) FROM users GROUP BY DATE(created_at) ORDER BY 1 DESC LIMIT 90

2. Active users today:
   SELECT COUNT(DISTINCT user_id) FROM workout_sessions WHERE DATE(started_at) = TODAY

3. Most popular exercises:
   SELECT e.name, COUNT(*) as usage FROM workout_exercises we 
   JOIN exercise_library e ON we.exercise_library_id = e.id 
   GROUP BY e.name ORDER BY usage DESC LIMIT 10

4. Role breakdown:
   SELECT role, COUNT(*) FROM users GROUP BY role

5. Feature adoption (last 30 days):
   - % users who logged nutrition
   - % users who logged body metrics
   - % users who followed someone

Template uses Chart.js for all charts.
Data passed as JSON to template for Chart.js.
```

---

### 7. Admin Logs (`/admin/logs`)

```
Audit trail of all admin actions.

Table: Timestamp | Admin | Action | Target | Details
Filter: by admin, by action type, by date range
Search: by target username

NOT editable. Read-only audit trail.
```

---

## 📐 BASE TEMPLATE LAYOUT

```html
<!-- base.html structure -->
<html>
<head>Bootstrap 5 CDN, Chart.js CDN, Custom CSS</head>
<body class="bg-dark text-light">
  <!-- Sidebar -->
  <nav class="sidebar">
    Logo: FitTracker Admin
    Links:
    - 📊 Dashboard
    - 👥 Users
    - 💪 Exercises
    - 🚩 Reports (badge with count)
    - 📈 Analytics
    - 📋 Logs
    - 🚪 Logout
  </nav>

  <!-- Main Content -->
  <main class="main-content">
    <!-- Flash messages -->
    {% for msg in messages %}
    <div class="alert alert-{{ msg.type }}">{{ msg.text }}</div>
    {% endfor %}
    
    <!-- Page content -->
    {% block content %}{% endblock %}
  </main>
</body>
</html>
```

---

## ⚠️ STRICT ADMIN RULES

1. All admin routes MUST verify `user.role == "admin"` via session
2. ALL actions must be logged to `admin_logs` table with admin_id, action, target, timestamp
3. Destructive actions (suspend, delete) MUST have confirmation modal
4. No admin can delete themselves or demote themselves
5. Flash messages for every action (success/error)
6. Rate limiting: max 100 admin actions per hour per admin
7. Admin session expires after 4 hours of inactivity
8. Log admin login/logout events
