# FITTRACKER_QUICKSTART.md
# Complete Documentation Index

---

## 📚 ALL DOCUMENTATION FILES

| File | Contents | When to Read |
|------|----------|-------------|
| FT_00_MAIN_README.md | Vision, architecture, tech stack, feature list | First time, for overview |
| FT_01_DATABASE_SCHEMA.md | All 28 tables, relationships, indexes, seed data | Before writing any models |
| FT_02_BACKEND_API.md | All 10 API modules, endpoints, Codex prompts | Building backend |
| FT_03_FRONTEND_REACT.md | Pages, components, store setup, Codex prompts | Building frontend |
| FT_04_ADMIN_PANEL.md | Jinja2 admin panel, all pages, Codex prompts | Building admin |
| FT_05_SECURITY_RULES.md | Non-negotiable security rules + checklist | Read BEFORE writing code |
| FT_06_AI_PROMPTS.md | Codex, Gemini, Ollama prompt templates | Daily use |
| FT_07_TESTING_GUIDE.md | Manual tests for every module | After each module |
| FT_08_DEPLOYMENT.md | Docker, Railway, Render, VPS setup | Weeks 4 and 12 |
| FT_09_FEATURES_ROADMAP.md | Build order, priorities, effort matrix | Weekly planning |
| FT_PROJECT_TRACKER.md | Progress tracker, weekly reviews | Daily + Friday reviews |

---

## 🚀 START HERE (Day 1)

### Step 1 — Read in this order (30 min)
```
1. FT_00_MAIN_README.md         → understand what you're building
2. FT_05_SECURITY_RULES.md      → memorize before writing code
3. FT_01_DATABASE_SCHEMA.md     → understand the data model
4. FT_09_FEATURES_ROADMAP.md    → know the build order
```

### Step 2 — Set up tracker
```
Open FT_PROJECT_TRACKER.md
→ Fill in project start date
→ Write your personal goals (why are you building this?)
→ Bookmark for daily updates
```

### Step 3 — Generate the project structure
```
Use FT_06_AI_PROMPTS.md → Prompt Set A1
→ Paste into Codex CLI
→ Get project skeleton
```

### Step 4 — Create database
```
Use FT_01_DATABASE_SCHEMA.md → Alembic migration prompts
→ Generate models
→ Run: alembic upgrade head
```

### Step 5 — Build Week 1 (auth)
```
Use FT_02_BACKEND_API.md → MODULE 1 CODEX PROMPT
→ Generate auth module
→ Test with FT_07_TESTING_GUIDE.md → MODULE 1 AUTH TESTING
```

---

## 🤖 WHICH AI FOR WHAT

| Task | Use |
|------|-----|
| Generate new module from scratch | Codex CLI (Prompt Set in FT_06) |
| Debug error + stack trace | Gemini CLI (FT_06 debug prompts) |
| Quick syntax question | Ollama qwen3:8b |
| Architecture review | Claude (me) |
| Security review | Claude (me) — compare to FT_05 |
| Weekly planning/review | Claude (me) — Mondays + Fridays |
| Complex SQL optimization | Gemini CLI |

---

## 🏗️ TECH STACK SUMMARY

```
Backend:    Python 3.11 + FastAPI + SQLAlchemy 2.0 (async) + Alembic
Database:   PostgreSQL 15
Admin:      FastAPI + Jinja2 + Bootstrap 5 (server-rendered)
Frontend:   React 18 + TypeScript + Vite + Tailwind CSS + shadcn/ui
State:      Zustand (auth/workout) + React Query (server data)
Auth:       JWT (access 30min + refresh 7d)
Charts:     Recharts
Files:      Local filesystem → S3 later
Deploy:     Docker + Railway (free) or Render (free)
```

---

## ⚡ WEEKLY SCHEDULE

```
MONDAY:   Plan week + start backend module (1-2h)
TUESDAY:  Backend development + testing (2-3h)
WEDNESDAY: Backend done + frontend start (2-3h)
THURSDAY: Frontend + integration (2-3h)
FRIDAY:   Testing + fixes + review with Claude (1-2h)
SATURDAY: Experiments + refactoring (optional)
SUNDAY:   Rest
```

---

## 📞 HOW TO TALK TO CLAUDE (ME)

### Monday planning:
```
"Starting Week [X]. Phase [1/2/3].
This week I need to build: [list from roadmap].
I have questions: [questions].
Is my plan correct?"
```

### Friday review:
```
"Week [X] done.
Built: [what you finished]
Blocked by: [what's unfinished + why]
Key code (security review): [paste critical code]
Questions: [list]
Plan for next week: [your plan]"
```

### Emergency (stuck):
```
"Stuck on [specific problem].
Tried: Codex (result), Gemini (result), Ollama (result).
Error: [exact error]
Code: [paste relevant code]
Help."
```
