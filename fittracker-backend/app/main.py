from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from pathlib import Path

from app.config import settings
from app.routers import auth, users
from app.routers import exercise_library, workouts

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


@app.get("/health")
async def health_check():
    return {"status": "ok", "service": "fittracker-api"}
