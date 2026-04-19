from datetime import datetime, timezone, date, timedelta
from typing import Optional

from fastapi import APIRouter, Depends, Query
from sqlalchemy import func, or_, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.dependencies import get_current_active_user
from app.models.nutrition import Food, MealLog, NutritionGoal
from app.models.user import User
from app.schemas.nutrition import (
    DailySummaryResponse,
    FoodListResponse,
    FoodResponse,
    MealLogCreate,
    MealLogResponse,
    MealTypeGroup,
    NutritionGoalResponse,
    NutritionGoalUpsert,
    WeeklyAdherenceResponse,
    WeeklyDayAdherence,
)

router = APIRouter(prefix="/api/nutrition", tags=["nutrition"])
foods_router = APIRouter(prefix="/api/foods", tags=["foods"])


# ── Foods ─────────────────────────────────────────────────────────────────────

@foods_router.get("", response_model=FoodListResponse)
async def list_foods(
    page: int = Query(1, ge=1),
    per_page: int = Query(20, ge=1, le=100),
    search: Optional[str] = Query(None),
    db: AsyncSession = Depends(get_db),
    _: User = Depends(get_current_active_user),
):
    q = select(Food)
    if search:
        term = f"%{search.lower()}%"
        q = q.where(
            or_(
                func.lower(Food.name).like(term),
                func.lower(Food.brand).like(term),
            )
        )

    total_result = await db.execute(select(func.count()).select_from(q.subquery()))
    total = total_result.scalar() or 0

    q = q.order_by(Food.name).offset((page - 1) * per_page).limit(per_page)
    result = await db.execute(q)
    items = result.scalars().all()

    return FoodListResponse(
        total=total,
        page=page,
        per_page=per_page,
        items=[FoodResponse.model_validate(f) for f in items],
    )


@foods_router.get("/{food_id}", response_model=FoodResponse)
async def get_food(
    food_id: int,
    db: AsyncSession = Depends(get_db),
    _: User = Depends(get_current_active_user),
):
    result = await db.execute(select(Food).where(Food.id == food_id))
    food = result.scalar_one_or_none()
    if not food:
        from app.core.exceptions import NotFoundError
        raise NotFoundError("Food not found")
    return FoodResponse.model_validate(food)


# ── Meal Logs ─────────────────────────────────────────────────────────────────

@router.post("/log", response_model=MealLogResponse, status_code=201)
async def log_meal(
    body: MealLogCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    food_result = await db.execute(select(Food).where(Food.id == body.food_id))
    food = food_result.scalar_one_or_none()
    if not food:
        from app.core.exceptions import NotFoundError
        raise NotFoundError("Food not found")

    factor = body.quantity_g / 100
    log = MealLog(
        user_id=current_user.id,
        food_id=body.food_id,
        meal_type=body.meal_type,
        quantity_g=body.quantity_g,
        logged_at=body.logged_at or datetime.now(timezone.utc),
        calories=round(float(food.calories_per_100g) * factor, 2),
        protein_g=round(float(food.protein_g) * factor, 2),
        carbs_g=round(float(food.carbs_g) * factor, 2),
        fat_g=round(float(food.fat_g) * factor, 2),
        fiber_g=round(float(food.fiber_g) * factor, 2),
    )
    db.add(log)
    await db.commit()
    await db.refresh(log)
    return MealLogResponse.model_validate(log)


@router.delete("/log/{log_id}", status_code=204)
async def delete_log(
    log_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    result = await db.execute(
        select(MealLog).where(MealLog.id == log_id, MealLog.user_id == current_user.id)
    )
    log = result.scalar_one_or_none()
    if not log:
        from app.core.exceptions import NotFoundError
        raise NotFoundError("Log entry not found")
    await db.delete(log)
    await db.commit()


# ── Daily Summary ─────────────────────────────────────────────────────────────

@router.get("/daily", response_model=DailySummaryResponse)
async def daily_summary(
    date_str: Optional[str] = Query(None, alias="date"),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    target_date = date.fromisoformat(date_str) if date_str else date.today()
    day_start = datetime(target_date.year, target_date.month, target_date.day, tzinfo=timezone.utc)
    day_end = day_start + timedelta(days=1)

    result = await db.execute(
        select(MealLog).where(
            MealLog.user_id == current_user.id,
            MealLog.logged_at >= day_start,
            MealLog.logged_at < day_end,
        ).order_by(MealLog.logged_at)
    )
    logs = result.scalars().all()

    # Group by meal type
    groups: dict[str, list[MealLog]] = {}
    for log in logs:
        groups.setdefault(log.meal_type, []).append(log)

    meal_groups = []
    total_cal = total_prot = total_carbs = total_fat = total_fiber = 0.0

    for meal_type, items in groups.items():
        sub_cal = sum(float(i.calories) for i in items)
        sub_prot = sum(float(i.protein_g) for i in items)
        sub_carbs = sum(float(i.carbs_g) for i in items)
        sub_fat = sum(float(i.fat_g) for i in items)
        total_cal += sub_cal
        total_prot += sub_prot
        total_carbs += sub_carbs
        total_fat += sub_fat
        total_fiber += sum(float(i.fiber_g) for i in items)
        meal_groups.append(
            MealTypeGroup(
                meal_type=meal_type,
                items=[MealLogResponse.model_validate(i) for i in items],
                subtotal_calories=round(sub_cal, 1),
                subtotal_protein_g=round(sub_prot, 1),
                subtotal_carbs_g=round(sub_carbs, 1),
                subtotal_fat_g=round(sub_fat, 1),
            )
        )

    return DailySummaryResponse(
        date=target_date.isoformat(),
        total_calories=round(total_cal, 1),
        total_protein_g=round(total_prot, 1),
        total_carbs_g=round(total_carbs, 1),
        total_fat_g=round(total_fat, 1),
        total_fiber_g=round(total_fiber, 1),
        meals=meal_groups,
    )


# ── Weekly Adherence ──────────────────────────────────────────────────────────

@router.get("/weekly", response_model=WeeklyAdherenceResponse)
async def weekly_adherence(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    goal_result = await db.execute(
        select(NutritionGoal).where(NutritionGoal.user_id == current_user.id)
    )
    goal = goal_result.scalar_one_or_none()
    target = goal.calories_target if goal else 2000

    days = []
    total_adherence = 0.0
    today = date.today()

    for offset in range(6, -1, -1):
        d = today - timedelta(days=offset)
        day_start = datetime(d.year, d.month, d.day, tzinfo=timezone.utc)
        day_end = day_start + timedelta(days=1)

        cal_result = await db.execute(
            select(func.coalesce(func.sum(MealLog.calories), 0)).where(
                MealLog.user_id == current_user.id,
                MealLog.logged_at >= day_start,
                MealLog.logged_at < day_end,
            )
        )
        calories = float(cal_result.scalar() or 0)
        adherence = min(round(calories / target * 100, 1), 100.0) if target > 0 else 0.0
        total_adherence += adherence
        days.append(
            WeeklyDayAdherence(
                date=d.isoformat(),
                calories=round(calories, 1),
                target=target,
                adherence_pct=adherence,
            )
        )

    return WeeklyAdherenceResponse(
        days=days,
        avg_adherence_pct=round(total_adherence / 7, 1),
    )


# ── Nutrition Goals ───────────────────────────────────────────────────────────

@router.get("/goals", response_model=NutritionGoalResponse)
async def get_nutrition_goals(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    result = await db.execute(
        select(NutritionGoal).where(NutritionGoal.user_id == current_user.id)
    )
    goal = result.scalar_one_or_none()
    if not goal:
        # Return defaults
        return NutritionGoalResponse(
            calories_target=2000,
            protein_g=150,
            carbs_g=200,
            fat_g=65,
            fiber_g=25,
            updated_at=datetime.now(timezone.utc),
        )
    return NutritionGoalResponse.model_validate(goal)


@router.put("/goals", response_model=NutritionGoalResponse)
async def upsert_nutrition_goals(
    body: NutritionGoalUpsert,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    result = await db.execute(
        select(NutritionGoal).where(NutritionGoal.user_id == current_user.id)
    )
    goal = result.scalar_one_or_none()
    now = datetime.now(timezone.utc)

    if goal:
        goal.calories_target = body.calories_target
        goal.protein_g = body.protein_g
        goal.carbs_g = body.carbs_g
        goal.fat_g = body.fat_g
        goal.fiber_g = body.fiber_g
        goal.updated_at = now
    else:
        goal = NutritionGoal(
            user_id=current_user.id,
            calories_target=body.calories_target,
            protein_g=body.protein_g,
            carbs_g=body.carbs_g,
            fat_g=body.fat_g,
            fiber_g=body.fiber_g,
            updated_at=now,
        )
        db.add(goal)

    await db.commit()
    await db.refresh(goal)
    return NutritionGoalResponse.model_validate(goal)
