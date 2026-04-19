from datetime import datetime, timezone
from typing import Optional

from fastapi import APIRouter, Depends, Query
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.dependencies import get_current_active_user
from app.models.body import BodyGoal, BodyMetric
from app.models.user import User
from app.schemas.body import (
    BodyGoalCreate,
    BodyGoalResponse,
    BodyGoalUpdate,
    BodyMetricCreate,
    BodyMetricHistoryResponse,
    BodyMetricResponse,
)

router = APIRouter(prefix="/api/body", tags=["body"])


# ── Helpers ───────────────────────────────────────────────────────────────────

def _calc_bmi(weight_kg: float, height_cm: Optional[float]) -> Optional[float]:
    if not height_cm or height_cm <= 0:
        return None
    height_m = height_cm / 100
    return round(weight_kg / (height_m ** 2), 1)


def _progress_pct(goal: BodyGoal) -> Optional[float]:
    if goal.start_value is None or goal.target_value == goal.start_value:
        return None
    current = float(goal.current_value or goal.start_value)
    start = float(goal.start_value)
    target = float(goal.target_value)
    pct = abs(current - start) / abs(target - start) * 100
    return round(min(pct, 100), 1)


# ── Body Metrics ──────────────────────────────────────────────────────────────

@router.post("/metrics", response_model=BodyMetricResponse, status_code=201)
async def log_metric(
    body: BodyMetricCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    bmi = None
    if body.weight_kg and getattr(current_user, "height_cm", None):
        bmi = _calc_bmi(body.weight_kg, current_user.height_cm)  # type: ignore[attr-defined]

    metric = BodyMetric(
        user_id=current_user.id,
        weight_kg=body.weight_kg,
        body_fat_pct=body.body_fat_pct,
        muscle_mass_kg=body.muscle_mass_kg,
        waist_cm=body.waist_cm,
        chest_cm=body.chest_cm,
        hip_cm=body.hip_cm,
        notes=body.notes,
        bmi=bmi,
        recorded_at=body.recorded_at or datetime.now(timezone.utc),
    )
    db.add(metric)

    # Update user's current weight
    if body.weight_kg:
        current_user.weight_kg = body.weight_kg  # type: ignore[attr-defined]

    # Auto-update body goals current_value and check completion
    if body.weight_kg:
        goals_result = await db.execute(
            select(BodyGoal).where(
                BodyGoal.user_id == current_user.id,
                BodyGoal.status == "active",
                BodyGoal.goal_type.in_(["weight_loss", "weight_gain"]),
            )
        )
        for goal in goals_result.scalars().all():
            goal.current_value = body.weight_kg
            target = float(goal.target_value)
            if (goal.goal_type == "weight_loss" and body.weight_kg <= target) or (
                goal.goal_type == "weight_gain" and body.weight_kg >= target
            ):
                goal.status = "completed"
                goal.completed_at = datetime.now(timezone.utc)

    await db.commit()
    await db.refresh(metric)
    return BodyMetricResponse.model_validate(metric)


@router.get("/metrics", response_model=BodyMetricHistoryResponse)
async def list_metrics(
    page: int = Query(1, ge=1),
    per_page: int = Query(20, ge=1, le=100),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    q = select(BodyMetric).where(BodyMetric.user_id == current_user.id)
    total_result = await db.execute(select(func.count()).select_from(q.subquery()))
    total = total_result.scalar() or 0

    q = q.order_by(BodyMetric.recorded_at.desc()).offset((page - 1) * per_page).limit(per_page)
    result = await db.execute(q)
    items = result.scalars().all()

    return BodyMetricHistoryResponse(
        total=total,
        page=page,
        per_page=per_page,
        items=[BodyMetricResponse.model_validate(m) for m in items],
    )


@router.get("/metrics/latest", response_model=BodyMetricResponse)
async def latest_metric(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    result = await db.execute(
        select(BodyMetric)
        .where(BodyMetric.user_id == current_user.id)
        .order_by(BodyMetric.recorded_at.desc())
        .limit(1)
    )
    metric = result.scalar_one_or_none()
    if not metric:
        from app.core.exceptions import NotFoundError
        raise NotFoundError("No body metrics logged yet")
    return BodyMetricResponse.model_validate(metric)


@router.delete("/metrics/{metric_id}", status_code=204)
async def delete_metric(
    metric_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    result = await db.execute(
        select(BodyMetric).where(
            BodyMetric.id == metric_id, BodyMetric.user_id == current_user.id
        )
    )
    metric = result.scalar_one_or_none()
    if not metric:
        from app.core.exceptions import NotFoundError
        raise NotFoundError("Metric not found")
    await db.delete(metric)
    await db.commit()


# ── Body Goals ────────────────────────────────────────────────────────────────

@router.post("/goals", response_model=BodyGoalResponse, status_code=201)
async def create_goal(
    body: BodyGoalCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    goal = BodyGoal(
        user_id=current_user.id,
        goal_type=body.goal_type,
        target_value=body.target_value,
        start_value=body.start_value,
        current_value=body.start_value,
        unit=body.unit,
        deadline=body.deadline,
    )
    db.add(goal)
    await db.commit()
    await db.refresh(goal)
    resp = BodyGoalResponse.model_validate(goal)
    resp.progress_pct = _progress_pct(goal)
    return resp


@router.get("/goals", response_model=list[BodyGoalResponse])
async def list_goals(
    status: Optional[str] = Query(None),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    q = select(BodyGoal).where(BodyGoal.user_id == current_user.id)
    if status:
        q = q.where(BodyGoal.status == status)
    q = q.order_by(BodyGoal.created_at.desc())
    result = await db.execute(q)
    goals = result.scalars().all()
    responses = []
    for g in goals:
        r = BodyGoalResponse.model_validate(g)
        r.progress_pct = _progress_pct(g)
        responses.append(r)
    return responses


@router.patch("/goals/{goal_id}", response_model=BodyGoalResponse)
async def update_goal(
    goal_id: int,
    body: BodyGoalUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    result = await db.execute(
        select(BodyGoal).where(
            BodyGoal.id == goal_id, BodyGoal.user_id == current_user.id
        )
    )
    goal = result.scalar_one_or_none()
    if not goal:
        from app.core.exceptions import NotFoundError
        raise NotFoundError("Goal not found")

    for field, value in body.model_dump(exclude_none=True).items():
        setattr(goal, field, value)

    if body.status == "completed" and not goal.completed_at:
        goal.completed_at = datetime.now(timezone.utc)

    await db.commit()
    await db.refresh(goal)
    resp = BodyGoalResponse.model_validate(goal)
    resp.progress_pct = _progress_pct(goal)
    return resp


@router.delete("/goals/{goal_id}", status_code=204)
async def delete_goal(
    goal_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    result = await db.execute(
        select(BodyGoal).where(
            BodyGoal.id == goal_id, BodyGoal.user_id == current_user.id
        )
    )
    goal = result.scalar_one_or_none()
    if not goal:
        from app.core.exceptions import NotFoundError
        raise NotFoundError("Goal not found")
    await db.delete(goal)
    await db.commit()
