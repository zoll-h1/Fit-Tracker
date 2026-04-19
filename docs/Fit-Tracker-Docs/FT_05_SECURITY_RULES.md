# FT_05 — SECURITY RULES
# FitTracker | NON-NEGOTIABLE REQUIREMENTS

> ⛔ These rules CANNOT be skipped, simplified, or "added later".
> They must be implemented FROM THE START.
> Violating these rules = vulnerable to real attacks.

---

## 🔐 1. AUTHENTICATION SECURITY

### Passwords
```python
# ALWAYS use bcrypt with min 12 rounds
# NEVER MD5, SHA1, plain text, or weak hashing
from passlib.context import CryptContext
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto", bcrypt__rounds=12)

# Minimum password requirements (enforce in Pydantic schema):
# - At least 8 characters
# - At least 1 uppercase letter
# - At least 1 number
# - No password = username rule

# NEVER return password_hash in any API response
# NEVER log passwords anywhere
```

### JWT Tokens
```python
# Access token: 30 minutes expiry
# Refresh token: 7 days expiry, stored in DB

ACCESS_TOKEN_EXPIRE_MINUTES = 30
REFRESH_TOKEN_EXPIRE_DAYS = 7

# JWT secret: minimum 32 characters, random
# NEVER hardcode JWT secret in code (use .env)
# NEVER use "secret", "mysecret", "password" as JWT secret

# Always verify:
# 1. Signature valid
# 2. Not expired
# 3. Token type correct (access vs refresh)
# 4. User still exists and is_active=True

# On logout: invalidate refresh token in DB
# On password change: invalidate ALL refresh tokens for that user
# On account suspend: immediately invalidate all tokens
```

### Rate Limiting (CRITICAL)
```python
# AUTH ENDPOINTS — STRICTLY RATE LIMITED:
# POST /api/auth/login: 5 attempts per IP per minute
# POST /api/auth/register: 10 per IP per hour
# POST /api/auth/forgot-password: 3 per IP per hour
# POST /api/auth/reset-password: 5 per IP per hour

# Implementation using slowapi:
from slowapi import Limiter
from slowapi.util import get_remote_address

limiter = Limiter(key_func=get_remote_address)

@router.post("/login")
@limiter.limit("5/minute")
async def login(request: Request, ...):
    ...

# On too many attempts: return 429 with Retry-After header
# Do NOT reveal whether email exists (same error for wrong email vs wrong password)
```

---

## 🛡️ 2. AUTHORIZATION (OWNERSHIP CHECKS)

### The Golden Rule
```python
# EVERY endpoint that reads, modifies, or deletes data
# MUST verify the requesting user owns that data.
# This is the most common vulnerability — always check!

# WRONG (VULNERABLE):
@router.get("/workouts/{workout_id}")
async def get_workout(workout_id: int, db: Session = Depends(get_db)):
    return db.query(WorkoutSession).filter_by(id=workout_id).first()
    # BUG: Any authenticated user can read any workout!

# CORRECT:
@router.get("/workouts/{workout_id}")
async def get_workout(
    workout_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    workout = db.query(WorkoutSession).filter_by(id=workout_id).first()
    if not workout:
        raise HTTPException(404, "Not found")
    if workout.user_id != current_user.id:
        raise HTTPException(403, "Not authorized")
    return workout
```

### Admin Role Check
```python
# Separate dependency for admin-only endpoints:
async def require_admin(current_user: User = Depends(get_current_user)):
    if current_user.role != "admin":
        raise HTTPException(403, "Admin access required")
    return current_user

# Use on ALL admin routes:
@router.post("/admin/users/{id}/suspend")
async def suspend_user(id: int, admin: User = Depends(require_admin), ...):
    ...
```

### Objects That Need Ownership Checks
- WorkoutSession → user_id
- WorkoutExercise → via session → user_id
- WorkoutSet → via exercise → session → user_id
- BodyMetric → user_id
- MealLog → user_id
- NutritionGoal → user_id
- WorkoutTemplate → user_id (unless is_public=True for read)
- Notification → user_id
- Conversation → user_a_id OR user_b_id

---

## 💉 3. INPUT VALIDATION

### Pydantic Schemas (ALWAYS USE THESE)
```python
# NEVER accept raw dict from requests
# ALWAYS define Pydantic schemas with strict validation

class WorkoutCreateSchema(BaseModel):
    name: str = Field(..., min_length=1, max_length=100)
    notes: Optional[str] = Field(None, max_length=1000)
    template_id: Optional[int] = Field(None, gt=0)

    @validator('name')
    def sanitize_name(cls, v):
        # Strip leading/trailing whitespace
        return v.strip()

# NEVER trust user IDs from request body when auth is available
# Get user_id from JWT token, NOT from request body
# WRONG: { "user_id": 5, "exercise": "bench" }  ← user can forge user_id
# RIGHT: get user_id from Depends(get_current_user).id
```

### Numeric Bounds
```python
class WorkoutSetSchema(BaseModel):
    weight_kg: Optional[float] = Field(None, ge=0, le=2000)    # Max 2000kg
    reps: Optional[int] = Field(None, ge=0, le=9999)            # Max 9999 reps
    rpe: Optional[int] = Field(None, ge=1, le=10)               # RPE 1-10
    duration_seconds: Optional[int] = Field(None, ge=0, le=86400)  # Max 24h

class BodyMetricSchema(BaseModel):
    weight_kg: Optional[float] = Field(None, ge=1, le=700)
    height_cm: Optional[float] = Field(None, ge=50, le=300)
    body_fat_percentage: Optional[float] = Field(None, ge=1, le=70)
```

### SQL Injection Prevention
```python
# SQLAlchemy ORM prevents SQL injection automatically
# NEVER use raw string formatting in queries!

# WRONG (SQL INJECTION VULNERABLE):
db.execute(f"SELECT * FROM users WHERE email = '{email}'")

# CORRECT:
db.query(User).filter(User.email == email).first()
# OR with raw SQL:
db.execute(text("SELECT * FROM users WHERE email = :email"), {"email": email})
```

---

## 📁 4. FILE UPLOAD SECURITY

```python
# FILE UPLOAD RULES (CRITICAL):

ALLOWED_MIME_TYPES = {"image/jpeg", "image/png", "image/webp"}
MAX_FILE_SIZE = 5 * 1024 * 1024  # 5MB

async def validate_upload(file: UploadFile):
    # 1. Check file size
    content = await file.read()
    if len(content) > MAX_FILE_SIZE:
        raise HTTPException(400, "File too large (max 5MB)")
    
    # 2. Check REAL MIME type (not just the header!)
    import magic
    real_mime = magic.from_buffer(content, mime=True)
    if real_mime not in ALLOWED_MIME_TYPES:
        raise HTTPException(400, "Invalid file type")
    
    # 3. Generate safe filename (NEVER use user-provided filename)
    import uuid
    safe_filename = f"{uuid.uuid4()}.jpg"
    
    # 4. Strip EXIF metadata (prevents GPS location leaks!)
    from PIL import Image
    import io
    img = Image.open(io.BytesIO(content))
    # Re-save without EXIF
    output = io.BytesIO()
    img.save(output, format="JPEG", quality=85)
    
    return safe_filename, output.getvalue()

# NEVER serve uploads through FastAPI without access control check
# Use /uploads as static only for PUBLIC images (avatars)
# For workout photos: check user owns workout before serving
```

---

## 🌐 5. CORS & HEADERS

```python
# main.py
from fastapi.middleware.cors import CORSMiddleware

ALLOWED_ORIGINS = [
    "http://localhost:5173",     # Vite dev
    "https://fittracker.app",    # Production frontend URL
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE"],
    allow_headers=["Authorization", "Content-Type"],
)

# Security headers middleware:
@app.middleware("http")
async def add_security_headers(request: Request, call_next):
    response = await call_next(request)
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["X-Frame-Options"] = "DENY"
    response.headers["X-XSS-Protection"] = "1; mode=block"
    response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
    return response

# NEVER use allow_origins=["*"] in production!
```

---

## 🗄️ 6. DATABASE SECURITY

```python
# Environment variables (NEVER hardcode):
DATABASE_URL = os.getenv("DATABASE_URL")  # from .env

# .env (NEVER commit to git):
DATABASE_URL=postgresql://user:strongpassword@localhost:5432/fittracker
JWT_SECRET=your-64-char-random-string-here
JWT_ALGORITHM=HS256

# Connection pool limits:
engine = create_async_engine(
    DATABASE_URL,
    pool_size=10,
    max_overflow=20,
    pool_timeout=30,
    pool_recycle=1800,
)

# Always use transactions for multi-step operations:
async with db.begin():
    workout = WorkoutSession(user_id=user.id, ...)
    db.add(workout)
    # If anything fails here, both operations are rolled back
    xp_event = XPEvent(user_id=user.id, ...)
    db.add(xp_event)
```

---

## 🔒 7. SENSITIVE DATA HANDLING

```python
# Fields to NEVER return in API responses:
EXCLUDED_FIELDS = [
    "password_hash",
    "refresh_token",
    "reset_token",
    "email_verify_token",
]

# Create separate response schemas that DON'T include sensitive fields:
class UserPublicSchema(BaseModel):
    id: int
    username: str
    full_name: str
    avatar_url: Optional[str]
    # NO email, NO password_hash

class UserPrivateSchema(UserPublicSchema):
    email: str          # Only shown to the user themselves
    # Still NO password_hash

# Logging: NEVER log:
# - Passwords (even failed attempts)
# - JWT tokens
# - Credit card info (not applicable here)
# - Full email addresses (use john@***.com format if needed)
```

---

## 🚨 8. ERROR HANDLING

```python
# NEVER expose internal errors to users in production:

# WRONG:
raise HTTPException(500, detail=str(e))  # Leaks stack trace, DB structure!

# CORRECT:
# In development:
if settings.DEBUG:
    raise HTTPException(500, detail=str(e))
# In production:
else:
    logger.error(f"Internal error: {e}")  # Log for developers
    raise HTTPException(500, detail="Internal server error")  # Generic for users

# Consistent error format:
{
    "detail": "Human-readable message",
    "code": "MACHINE_READABLE_CODE"
}

# Error codes to use:
# AUTH_INVALID_CREDENTIALS, AUTH_TOKEN_EXPIRED, AUTH_TOKEN_INVALID
# NOT_FOUND, FORBIDDEN, VALIDATION_ERROR
# RATE_LIMIT_EXCEEDED, SERVER_ERROR
```

---

## 📋 9. .GITIGNORE (NON-NEGOTIABLE)

```
# .gitignore — MUST include these
.env
.env.local
.env.production
*.env
__pycache__/
uploads/
*.pyc
.venv/
venv/
node_modules/
dist/
.DS_Store
*.log
```

---

## ✅ SECURITY CHECKLIST (Run Before Every PR)

### Authentication
- [ ] All auth endpoints rate-limited?
- [ ] JWT secret in .env (not in code)?
- [ ] Password min requirements enforced?
- [ ] password_hash never in response?
- [ ] Token expiry set correctly?

### Authorization
- [ ] Every data endpoint checks ownership?
- [ ] Admin-only endpoints use require_admin?
- [ ] Can I access another user's data? (Test manually)

### Input
- [ ] All inputs have Pydantic schemas with constraints?
- [ ] File uploads validated for MIME type AND size?
- [ ] Numeric fields bounded (no negative weight_kg)?

### Infrastructure
- [ ] CORS not set to wildcard?
- [ ] .env not committed to git?
- [ ] Database URL not hardcoded?
- [ ] No raw SQL string formatting?

### Data
- [ ] Sensitive fields excluded from responses?
- [ ] No secrets in log output?

> If ANY checkbox is unchecked → DO NOT DEPLOY
