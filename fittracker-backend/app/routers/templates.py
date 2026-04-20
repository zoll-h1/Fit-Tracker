from datetime import datetime, timezone

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import selectinload

from app.database import get_db
from app.dependencies import get_current_active_user
from app.models.workout import WorkoutTemplate, TemplateExercise, WorkoutSession, WorkoutExercise
from app.models.user import User
from app.schemas.templates import (
    TemplateCreate, TemplateUpdate, TemplateOut, TemplateDetailOut,
    TemplateSaveFromWorkout, TemplateExerciseOut,
)
from app.schemas.workout import WorkoutSessionResponse
from app.core.exceptions import NotFoundError, ForbiddenError

router = APIRouter(prefix="/api/templates", tags=["templates"])


# ─── helpers ────────────────────────────────────────────────────────────────

def _template_detail(t: WorkoutTemplate, user: User) -> TemplateDetailOut:
    exercises = [
        TemplateExerciseOut(
            id=e.id,
            exercise_library_id=e.exercise_library_id,
            exercise_order=e.exercise_order,
            target_sets=e.target_sets,
            target_reps=e.target_reps,
            target_weight_kg=float(e.target_weight_kg) if e.target_weight_kg else None,
            rest_seconds=e.rest_seconds,
            notes=e.notes,
            exercise_name=e.exercise.name if e.exercise else None,
        )
        for e in sorted(t.exercises, key=lambda x: x.exercise_order)
    ]
    return TemplateDetailOut(
        id=t.id,
        user_id=t.user_id,
        name=t.name,
        description=t.description,
        is_public=t.is_public,
        estimated_duration_min=t.estimated_duration_min,
        times_used=t.times_used,
        created_at=t.created_at,
        exercise_count=len(t.exercises),
        exercises=exercises,
        creator_username=user.username,
    )


async def _load_template(template_id: int, db: AsyncSession) -> WorkoutTemplate:
    result = await db.execute(
        select(WorkoutTemplate)
        .where(WorkoutTemplate.id == template_id)
        .options(
            selectinload(WorkoutTemplate.exercises).selectinload(TemplateExercise.exercise)
        )
    )
    t = result.scalar_one_or_none()
    if not t:
        raise NotFoundError("Template not found")
    return t


# ─── Endpoints ───────────────────────────────────────────────────────────────

@router.post("", response_model=TemplateDetailOut, status_code=201)
async def create_template(
    body: TemplateCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    template = WorkoutTemplate(
        user_id=current_user.id,
        name=body.name,
        description=body.description,
        is_public=body.is_public,
        estimated_duration_min=body.estimated_duration_min,
    )
    db.add(template)
    await db.flush()

    for ex in body.exercises:
        te = TemplateExercise(
            template_id=template.id,
            exercise_library_id=ex.exercise_library_id,
            exercise_order=ex.exercise_order,
            target_sets=ex.target_sets,
            target_reps=ex.target_reps,
            target_weight_kg=ex.target_weight_kg,
            rest_seconds=ex.rest_seconds,
            notes=ex.notes,
        )
        db.add(te)

    await db.commit()

    t = await _load_template(template.id, db)
    return _template_detail(t, current_user)


@router.get("", response_model=list[TemplateOut])
async def list_templates(
    mine: bool = True,
    public: bool = False,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    results: list[WorkoutTemplate] = []

    if mine:
        q = (
            select(WorkoutTemplate)
            .where(WorkoutTemplate.user_id == current_user.id)
            .options(selectinload(WorkoutTemplate.exercises))
            .order_by(WorkoutTemplate.created_at.desc())
        )
        r = await db.execute(q)
        results.extend(r.scalars().all())

    if public:
        q = (
            select(WorkoutTemplate)
            .where(
                WorkoutTemplate.is_public == True,
                WorkoutTemplate.user_id != current_user.id,
            )
            .options(selectinload(WorkoutTemplate.exercises))
            .order_by(WorkoutTemplate.times_used.desc())
        )
        r = await db.execute(q)
        public_templates = r.scalars().all()
        # Avoid duplicates if user asked for both mine+public
        existing_ids = {t.id for t in results}
        results.extend(t for t in public_templates if t.id not in existing_ids)

    return [
        TemplateOut(
            id=t.id,
            user_id=t.user_id,
            name=t.name,
            description=t.description,
            is_public=t.is_public,
            estimated_duration_min=t.estimated_duration_min,
            times_used=t.times_used,
            created_at=t.created_at,
            exercise_count=len(t.exercises),
        )
        for t in results
    ]


@router.get("/{template_id}", response_model=TemplateDetailOut)
async def get_template(
    template_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    t = await _load_template(template_id, db)

    # Only owner or public templates visible to others
    if t.user_id != current_user.id and not t.is_public:
        raise ForbiddenError("Access denied")

    # Fetch creator
    user_result = await db.execute(select(User).where(User.id == t.user_id))
    creator = user_result.scalar_one_or_none() or current_user

    return _template_detail(t, creator)


@router.put("/{template_id}", response_model=TemplateDetailOut)
async def update_template(
    template_id: int,
    body: TemplateUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    t = await _load_template(template_id, db)

    if t.user_id != current_user.id:
        raise ForbiddenError("Not the owner")

    if body.name is not None:
        t.name = body.name
    if body.description is not None:
        t.description = body.description
    if body.is_public is not None:
        t.is_public = body.is_public
    if body.estimated_duration_min is not None:
        t.estimated_duration_min = body.estimated_duration_min

    await db.commit()

    t = await _load_template(template_id, db)
    return _template_detail(t, current_user)


@router.delete("/{template_id}", status_code=204)
async def delete_template(
    template_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    t = await _load_template(template_id, db)

    if t.user_id != current_user.id:
        raise ForbiddenError("Not the owner")

    await db.delete(t)
    await db.commit()


@router.post("/{template_id}/start", response_model=WorkoutSessionResponse, status_code=201)
async def start_from_template(
    template_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    t = await _load_template(template_id, db)

    # Anyone can start a public template; only owner can start private
    if t.user_id != current_user.id and not t.is_public:
        raise ForbiddenError("Access denied")

    session = WorkoutSession(
        user_id=current_user.id,
        name=t.name,
        template_id=t.id,
        status="in_progress",
    )
    db.add(session)
    await db.flush()

    for te in sorted(t.exercises, key=lambda x: x.exercise_order):
        we = WorkoutExercise(
            session_id=session.id,
            exercise_library_id=te.exercise_library_id,
            exercise_order=te.exercise_order,
            rest_seconds=te.rest_seconds,
            notes=te.notes,
        )
        db.add(we)

    # Increment times_used
    t.times_used = (t.times_used or 0) + 1
    t.last_used_at = datetime.now(timezone.utc)

    await db.commit()

    result = await db.execute(
        select(WorkoutSession)
        .where(WorkoutSession.id == session.id)
        .options(
            selectinload(WorkoutSession.exercises).selectinload(WorkoutExercise.sets)
        )
    )
    return WorkoutSessionResponse.model_validate(result.scalar_one())
