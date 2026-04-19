from typing import Optional

from fastapi import APIRouter, Depends, Query
from sqlalchemy import func, or_, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.dependencies import get_current_active_user
from app.models.exercise import ExerciseLibrary
from app.models.user import User
from app.schemas.exercise import ExerciseListResponse, ExerciseResponse

router = APIRouter(prefix="/api/exercises", tags=["exercises"])


@router.get("", response_model=ExerciseListResponse)
async def list_exercises(
    page: int = Query(1, ge=1),
    per_page: int = Query(20, ge=1, le=100),
    search: Optional[str] = Query(None),
    category: Optional[str] = Query(None),
    muscle: Optional[str] = Query(None),
    equipment: Optional[str] = Query(None),
    difficulty: Optional[str] = Query(None),
    db: AsyncSession = Depends(get_db),
    _: User = Depends(get_current_active_user),
):
    q = select(ExerciseLibrary)

    if search:
        term = f"%{search.lower()}%"
        q = q.where(
            or_(
                func.lower(ExerciseLibrary.name).like(term),
                func.lower(ExerciseLibrary.muscle_primary).like(term),
            )
        )
    if category:
        q = q.where(ExerciseLibrary.category == category)
    if muscle:
        term = f"%{muscle.lower()}%"
        q = q.where(
            or_(
                func.lower(ExerciseLibrary.muscle_primary).like(term),
                func.lower(ExerciseLibrary.muscle_secondary).like(term),
            )
        )
    if equipment:
        q = q.where(func.lower(ExerciseLibrary.equipment).like(f"%{equipment.lower()}%"))
    if difficulty:
        q = q.where(ExerciseLibrary.difficulty == difficulty)

    total_result = await db.execute(select(func.count()).select_from(q.subquery()))
    total = total_result.scalar() or 0

    q = q.order_by(ExerciseLibrary.name).offset((page - 1) * per_page).limit(per_page)
    result = await db.execute(q)
    items = result.scalars().all()

    return ExerciseListResponse(
        total=total,
        page=page,
        per_page=per_page,
        items=[ExerciseResponse.model_validate(ex) for ex in items],
    )


@router.get("/{exercise_id}", response_model=ExerciseResponse)
async def get_exercise(
    exercise_id: int,
    db: AsyncSession = Depends(get_db),
    _: User = Depends(get_current_active_user),
):
    result = await db.execute(select(ExerciseLibrary).where(ExerciseLibrary.id == exercise_id))
    exercise = result.scalar_one_or_none()
    if not exercise:
        from app.core.exceptions import NotFoundError
        raise NotFoundError("Exercise not found")
    return ExerciseResponse.model_validate(exercise)
