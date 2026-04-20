from fastapi import APIRouter, Request, Form, Depends
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from pathlib import Path
from datetime import datetime, timedelta, timezone

from app.database import get_db
from app.models.user import User
from app.models.workout import WorkoutSession
from app.models.exercise import ExerciseLibrary
from app.models.nutrition import Food
from app.models.challenges import Challenge
from app.admin.auth import get_admin_session, ADMIN_SESSION_TOKEN, ADMIN_COOKIE_NAME, ADMIN_PASSWORD

router = APIRouter(prefix="/admin", tags=["admin"])
templates = Jinja2Templates(directory=str(Path(__file__).parent / "templates"))


def _require_auth(request: Request):
    """Returns redirect to login if not authenticated."""
    if not get_admin_session(request):
        return RedirectResponse(url="/admin/login", status_code=302)
    return None


@router.get("/login", response_class=HTMLResponse)
async def admin_login_page(request: Request):
    return templates.TemplateResponse(request, "login.html", {"error": None})


@router.post("/login")
async def admin_login(request: Request, password: str = Form(...)):
    if password == ADMIN_PASSWORD:
        response = RedirectResponse(url="/admin", status_code=302)
        response.set_cookie(ADMIN_COOKIE_NAME, ADMIN_SESSION_TOKEN, httponly=True, max_age=86400)
        return response
    return templates.TemplateResponse(request, "login.html", {"error": "Invalid password"})


@router.get("/logout")
async def admin_logout():
    response = RedirectResponse(url="/admin/login", status_code=302)
    response.delete_cookie(ADMIN_COOKIE_NAME)
    return response


@router.get("", response_class=HTMLResponse)
async def admin_dashboard(request: Request, db: AsyncSession = Depends(get_db)):
    redirect = _require_auth(request)
    if redirect:
        return redirect

    now = datetime.now(timezone.utc)
    seven_days_ago = now - timedelta(days=7)
    today_start = now.replace(hour=0, minute=0, second=0, microsecond=0)

    total_users = (await db.execute(select(func.count(User.id)))).scalar()
    active_users_7d = (await db.execute(
        select(func.count(User.id)).where(User.last_active_at >= seven_days_ago)
    )).scalar()
    total_workouts = (await db.execute(select(func.count(WorkoutSession.id)))).scalar()
    workouts_today = (await db.execute(
        select(func.count(WorkoutSession.id)).where(WorkoutSession.started_at >= today_start)
    )).scalar()
    total_foods = (await db.execute(select(func.count(Food.id)))).scalar()
    total_challenges = (await db.execute(select(func.count(Challenge.id)))).scalar()

    stats = dict(
        total_users=total_users or 0,
        active_users_7d=active_users_7d or 0,
        total_workouts=total_workouts or 0,
        workouts_today=workouts_today or 0,
        total_foods=total_foods or 0,
        total_challenges=total_challenges or 0,
    )
    return templates.TemplateResponse(request, "dashboard.html", {"stats": stats, "active": "dashboard"})


@router.get("/users", response_class=HTMLResponse)
async def admin_users(request: Request, search: str = "", db: AsyncSession = Depends(get_db)):
    redirect = _require_auth(request)
    if redirect:
        return redirect

    q = select(User).order_by(User.created_at.desc())
    if search:
        q = q.where(User.username.ilike(f"%{search}%"))
    result = await db.execute(q)
    users = result.scalars().all()

    return templates.TemplateResponse(request, "users.html", {
        "users": users, "total": len(users),
        "search": search, "message": request.query_params.get("message"), "active": "users"
    })


@router.post("/users/{user_id}/toggle")
async def toggle_user_status(user_id: int, request: Request, db: AsyncSession = Depends(get_db)):
    redirect = _require_auth(request)
    if redirect:
        return redirect
    user = await db.get(User, user_id)
    if user:
        user.is_active = not user.is_active
        await db.commit()
    return RedirectResponse(url="/admin/users?message=User+status+updated", status_code=302)


@router.post("/users/{user_id}/make-admin")
async def make_admin(user_id: int, request: Request, db: AsyncSession = Depends(get_db)):
    redirect = _require_auth(request)
    if redirect:
        return redirect
    user = await db.get(User, user_id)
    if user:
        user.role = "admin"
        await db.commit()
    return RedirectResponse(url="/admin/users?message=User+role+updated", status_code=302)


@router.get("/exercises", response_class=HTMLResponse)
async def admin_exercises(request: Request, db: AsyncSession = Depends(get_db)):
    redirect = _require_auth(request)
    if redirect:
        return redirect
    result = await db.execute(select(ExerciseLibrary).order_by(ExerciseLibrary.id))
    exercises = result.scalars().all()
    return templates.TemplateResponse(request, "exercises.html", {
        "exercises": exercises, "total": len(exercises),
        "message": request.query_params.get("message"), "active": "exercises"
    })


@router.post("/exercises")
async def add_exercise(
    request: Request,
    name: str = Form(...),
    muscle_primary: str = Form(""),
    category: str = Form("strength"),
    difficulty: str = Form("intermediate"),
    db: AsyncSession = Depends(get_db),
):
    redirect = _require_auth(request)
    if redirect:
        return redirect

    slug = name.lower().replace(" ", "-").replace("/", "-")
    exercise = ExerciseLibrary(
        name=name,
        slug=slug,
        category=category,
        difficulty=difficulty,
        muscle_primary=muscle_primary or None,
        is_custom=False,
        met_value=4.0,
    )
    db.add(exercise)
    await db.commit()
    return RedirectResponse(url="/admin/exercises?message=Exercise+added", status_code=302)


@router.get("/foods", response_class=HTMLResponse)
async def admin_foods(request: Request, search: str = "", db: AsyncSession = Depends(get_db)):
    redirect = _require_auth(request)
    if redirect:
        return redirect
    q = select(Food).order_by(Food.id.desc())
    if search:
        q = q.where(Food.name.ilike(f"%{search}%"))
    result = await db.execute(q.limit(100))
    foods = result.scalars().all()
    return templates.TemplateResponse(request, "foods.html", {
        "foods": foods, "total": len(foods),
        "search": search, "message": request.query_params.get("message"), "active": "foods"
    })


@router.post("/foods")
async def add_food(
    request: Request,
    name: str = Form(...),
    brand: str = Form(""),
    calories_per_100g: float = Form(...),
    protein_g: float = Form(0),
    carbs_g: float = Form(0),
    fat_g: float = Form(0),
    fiber_g: float = Form(0),
    sugar_g: float = Form(0),
    sodium_mg: float = Form(0),
    db: AsyncSession = Depends(get_db),
):
    redirect = _require_auth(request)
    if redirect:
        return redirect
    food = Food(
        name=name,
        brand=brand or None,
        calories_per_100g=calories_per_100g,
        protein_g=protein_g,
        carbs_g=carbs_g,
        fat_g=fat_g,
        fiber_g=fiber_g,
        sugar_g=sugar_g,
        sodium_mg=sodium_mg,
        is_custom=False,
    )
    db.add(food)
    await db.commit()
    return RedirectResponse(url="/admin/foods?message=Food+added+successfully", status_code=302)


@router.post("/foods/{food_id}/delete")
async def delete_food(food_id: int, request: Request, db: AsyncSession = Depends(get_db)):
    redirect = _require_auth(request)
    if redirect:
        return redirect
    food = await db.get(Food, food_id)
    if food:
        await db.delete(food)
        await db.commit()
    return RedirectResponse(url="/admin/foods?message=Food+deleted", status_code=302)


@router.get("/logs", response_class=HTMLResponse)
async def admin_logs(request: Request, db: AsyncSession = Depends(get_db)):
    redirect = _require_auth(request)
    if redirect:
        return redirect

    result = await db.execute(
        select(WorkoutSession, User.username)
        .join(User, User.id == WorkoutSession.user_id)
        .order_by(WorkoutSession.started_at.desc())
        .limit(20)
    )
    rows = result.all()

    class WorkoutRow:
        def __init__(self, ws, username):
            self.id = ws.id
            self.username = username
            self.name = ws.name
            self.total_sets = ws.total_sets
            self.total_volume_kg = ws.total_volume_kg
            self.status = ws.status
            self.started_at = ws.started_at

    recent_workouts = [WorkoutRow(ws, username) for ws, username in rows]
    return templates.TemplateResponse(request, "logs.html", {
        "recent_workouts": recent_workouts, "active": "logs"
    })
