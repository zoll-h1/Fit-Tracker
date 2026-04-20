import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from pathlib import Path

import sentry_sdk
from sentry_sdk.integrations.fastapi import FastApiIntegration
from sentry_sdk.integrations.sqlalchemy import SqlalchemyIntegration

from app.config import settings
from app.routers import auth, users
from app.routers import exercise_library, workouts
from app.routers import body
from app.routers.nutrition import router as nutrition_router, foods_router
from app.routers import gamification, analytics, notifications
from app.routers import templates
from app.routers.social import router as social_router, users_router
from app.routers import challenges
from app.routers.trainer import router as trainer_router
from app.models import trainer as trainer_models  # noqa: F401
from app.admin.router import router as admin_router
from app.core.scheduler import start_scheduler, stop_scheduler

app = FastAPI(
    title="FitTracker API",
    version="1.0.0",
    description="FitTracker — Your AI-powered fitness companion",
)

# Sentry (only if DSN is configured)
SENTRY_DSN = os.getenv("SENTRY_DSN", "")
if SENTRY_DSN:
    sentry_sdk.init(
        dsn=SENTRY_DSN,
        integrations=[FastApiIntegration(), SqlalchemyIntegration()],
        traces_sample_rate=0.1,
        environment=os.getenv("ENVIRONMENT", "development"),
    )

# CORS — if origins list contains "*", allow all origins (useful for Vercel preview URLs)
_cors_origins = settings.cors_origins
_allow_all = "*" in _cors_origins
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"] if _allow_all else _cors_origins,
    allow_credentials=False if _allow_all else True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Static file serving for uploads
uploads_path = Path(settings.UPLOAD_DIR)
uploads_path.mkdir(parents=True, exist_ok=True)
app.mount("/uploads", StaticFiles(directory=str(uploads_path)), name="uploads")

# Routers
app.include_router(auth.router)
app.include_router(users.router)
app.include_router(exercise_library.router)
app.include_router(workouts.router)
app.include_router(body.router)
app.include_router(nutrition_router)
app.include_router(foods_router)
app.include_router(gamification.router)
app.include_router(analytics.router)
app.include_router(notifications.router)
app.include_router(templates.router)
app.include_router(social_router)
app.include_router(users_router)
app.include_router(challenges.router)
app.include_router(trainer_router)
app.include_router(admin_router)


@app.on_event("startup")
async def startup_event():
    start_scheduler()
    from app.database import AsyncSessionLocal
    from app.seeds.achievements import seed_achievements
    from app.seeds.exercises import seed as seed_exercises
    from app.seeds.foods import seed as seed_foods
    async with AsyncSessionLocal() as db:
        try:
            await seed_achievements(db)
        except Exception:
            pass
        try:
            await seed_exercises()
        except Exception:
            pass
        try:
            await seed_foods()
        except Exception:
            pass


@app.on_event("shutdown")
async def shutdown_event():
    stop_scheduler()


@app.get("/health")
async def health_check():
    return {"status": "ok", "version": "1.0.0"}
