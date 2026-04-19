from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from pathlib import Path

from app.config import settings
from app.routers import auth, users
from app.routers import exercise_library, workouts
from app.routers import body
from app.routers.nutrition import router as nutrition_router, foods_router
from app.routers import gamification, analytics, notifications
from app.routers import templates
from app.routers.social import router as social_router, users_router
from app.routers import challenges
from app.core.scheduler import start_scheduler, stop_scheduler

app = FastAPI(
    title="FitTracker API",
    version="1.0.0",
    description="FitTracker — Your AI-powered fitness companion",
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
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


@app.on_event("startup")
async def startup_event():
    start_scheduler()
    # Seed achievement definitions
    from app.database import AsyncSessionLocal
    from app.seeds.achievements import seed_achievements
    async with AsyncSessionLocal() as db:
        try:
            await seed_achievements(db)
        except Exception:
            pass  # Tables may not exist yet (before migration)


@app.on_event("shutdown")
async def shutdown_event():
    stop_scheduler()


@app.get("/health")
async def health_check():
    return {"status": "ok", "service": "fittracker-api"}
