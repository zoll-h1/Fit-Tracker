from datetime import datetime, timezone
from typing import Optional

from fastapi import APIRouter, Depends, Query
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.database import get_db
from app.dependencies import get_current_active_user
from app.models.exercise import ExerciseLibrary, PersonalRecord
from app.models.user import User
from app.models.workout import WorkoutExercise, WorkoutSession, WorkoutSet, WorkoutTemplate, TemplateExercise
from app.schemas.workout import (
    WorkoutExerciseCreate,
    WorkoutExerciseResponse,
    WorkoutFinishRequest,
    WorkoutHistoryResponse,
    WorkoutSessionListItem,
    WorkoutSessionResponse,
    WorkoutSetCreate,
    WorkoutSetResponse,
    WorkoutSetUpdate,
    WorkoutStartRequest,
)
from app.schemas.templates import TemplateSaveFromWorkout, TemplateOut
from app.services import gamification_service
from app.services.notification_service import create_notification

router = APIRouter(prefix="/api/workouts", tags=["workouts"])


# ─── helpers ────────────────────────────────────────────────────────────────

def _not_found(msg: str = "Not found"):
    from app.core.exceptions import NotFoundError
    raise NotFoundError(msg)


async def _get_session_for_user(
    session_id: int, user_id: int, db: AsyncSession, load_relations: bool = False
) -> WorkoutSession:
    q = select(WorkoutSession).where(
        WorkoutSession.id == session_id,
        WorkoutSession.user_id == user_id,
    )
    if load_relations:
        q = q.options(
            selectinload(WorkoutSession.exercises).selectinload(WorkoutExercise.sets)
        )
    result = await db.execute(q)
    session = result.scalar_one_or_none()
    if not session:
        _not_found("Workout session not found")
    return session  # type: ignore[return-value]


# ─── Sessions ─────────────────────────────────────────────────────────────────

@router.post("", response_model=WorkoutSessionResponse, status_code=201)
async def start_workout(
    body: WorkoutStartRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """Start a new workout session."""
    session = WorkoutSession(
        user_id=current_user.id,
        name=body.name,
        notes=body.notes,
        template_id=body.template_id,
        status="in_progress",
    )
    db.add(session)
    await db.commit()
    await db.refresh(session)

    # Load relations for response
    result = await db.execute(
        select(WorkoutSession)
        .where(WorkoutSession.id == session.id)
        .options(selectinload(WorkoutSession.exercises).selectinload(WorkoutExercise.sets))
    )
    session = result.scalar_one()
    return WorkoutSessionResponse.model_validate(session)


@router.get("", response_model=WorkoutHistoryResponse)
async def list_workouts(
    page: int = Query(1, ge=1),
    per_page: int = Query(10, ge=1, le=50),
    status: Optional[str] = Query(None),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """List all workout sessions for the current user."""
    q = select(WorkoutSession).where(WorkoutSession.user_id == current_user.id)
    if status:
        q = q.where(WorkoutSession.status == status)

    total_result = await db.execute(select(func.count()).select_from(q.subquery()))
    total = total_result.scalar() or 0

    q = q.order_by(WorkoutSession.started_at.desc()).offset((page - 1) * per_page).limit(per_page)
    result = await db.execute(q)
    items = result.scalars().all()

    return WorkoutHistoryResponse(
        total=total,
        page=page,
        per_page=per_page,
        items=[WorkoutSessionListItem.model_validate(s) for s in items],
    )


@router.get("/{session_id}", response_model=WorkoutSessionResponse)
async def get_workout(
    session_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    session = await _get_session_for_user(session_id, current_user.id, db, load_relations=True)
    return WorkoutSessionResponse.model_validate(session)


@router.post("/{session_id}/finish", response_model=WorkoutSessionResponse)
async def finish_workout(
    session_id: int,
    body: WorkoutFinishRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """Finish a workout — auto-calculates stats, detects PRs, burns calories."""
    result = await db.execute(
        select(WorkoutSession)
        .where(WorkoutSession.id == session_id, WorkoutSession.user_id == current_user.id)
        .options(
            selectinload(WorkoutSession.exercises).selectinload(WorkoutExercise.sets),
            selectinload(WorkoutSession.exercises).selectinload(WorkoutExercise.exercise),
        )
    )
    session = result.scalar_one_or_none()
    if not session:
        _not_found("Workout session not found")

    if body.notes:
        session.notes = body.notes  # type: ignore[union-attr]

    now = datetime.now(timezone.utc)
    session.finished_at = now  # type: ignore[union-attr]
    session.status = "finished"  # type: ignore[union-attr]

    started = session.started_at  # type: ignore[union-attr]
    if started.tzinfo is None:
        started = started.replace(tzinfo=timezone.utc)
    session.duration_seconds = int((now - started).total_seconds())  # type: ignore[union-attr]

    total_volume = 0.0
    total_sets = 0
    total_reps = 0

    user_weight_kg: float = float(current_user.weight_kg or 70)  # type: ignore[attr-defined]

    for we in session.exercises:  # type: ignore[union-attr]
        met = float(we.exercise.met_value if we.exercise else 5.0)
        hours = session.duration_seconds / 3600  # type: ignore[union-attr]
        for ws in we.sets:
            if not ws.completed:
                continue
            total_sets += 1
            if ws.reps:
                total_reps += ws.reps
            if ws.weight_kg and ws.reps:
                total_volume += float(ws.weight_kg) * ws.reps

    session.total_volume_kg = round(total_volume, 2)  # type: ignore[union-attr]
    session.total_sets = total_sets  # type: ignore[union-attr]
    session.total_reps = total_reps  # type: ignore[union-attr]

    # Estimate calories: MET * weight_kg * hours (simplified; use average MET 5)
    hours_worked = session.duration_seconds / 3600  # type: ignore[union-attr]
    session.calories_burned = int(5.0 * user_weight_kg * hours_worked)  # type: ignore[union-attr]

    # Detect PRs: for each exercise check if any set beats current record
    for we in session.exercises:  # type: ignore[union-attr]
        for ws in we.sets:
            if not ws.completed or not ws.weight_kg or not ws.reps:
                continue
            pr_result = await db.execute(
                select(PersonalRecord).where(
                    PersonalRecord.user_id == current_user.id,
                    PersonalRecord.exercise_id == we.exercise_library_id,
                )
            )
            existing_pr = pr_result.scalar_one_or_none()

            if existing_pr is None or float(ws.weight_kg) > float(existing_pr.weight_kg):
                if existing_pr:
                    existing_pr.weight_kg = ws.weight_kg
                    existing_pr.reps = ws.reps
                    existing_pr.achieved_at = now
                    existing_pr.workout_set_id = ws.id
                else:
                    new_pr = PersonalRecord(
                        user_id=current_user.id,
                        exercise_id=we.exercise_library_id,
                        weight_kg=ws.weight_kg,
                        reps=ws.reps,
                        achieved_at=now,
                        workout_set_id=ws.id,
                    )
                    db.add(new_pr)
                ws.is_pr = True

    await db.flush()

    # Gamification: award XP, update streak, check achievements
    await gamification_service.award_xp(db, current_user.id, gamification_service.XP_AWARDS["complete_workout"], "complete_workout")
    streak_result = await gamification_service.update_streak(db, current_user.id)

    # Extra XP for any new PRs this session
    pr_count_this_session = sum(
        1 for we in session.exercises  # type: ignore[union-attr]
        for ws in we.sets if ws.is_pr
    )
    if pr_count_this_session:
        await gamification_service.award_xp(
            db, current_user.id,
            gamification_service.XP_AWARDS["pr_achieved"] * pr_count_this_session,
            "pr_achieved"
        )

    new_achievements = await gamification_service.check_achievements(db, current_user.id, "workout_finish")

    # Notify for new achievements
    for ach in new_achievements:
        await create_notification(
            db, current_user.id, "achievement_earned",
            f"🏆 Achievement Unlocked!",
            f"{ach['name']} — {ach['description']} (+{ach['xp_reward']} XP)",
            action_url="/achievements",
        )

    # Update challenge progress
    from app.services.challenge_service import update_challenge_progress
    await update_challenge_progress(db, current_user.id)

    # Auto-post to activity feed
    from app.models.social import ActivityFeed as ActivityFeedModel
    feed_entry = ActivityFeedModel(
        user_id=current_user.id,
        activity_type="workout",
        ref_id=session.id,
        title=f"Completed workout: {session.name}",
        body=f"{session.total_sets} sets · {int(float(session.total_volume_kg or 0))} kg volume"
             + (f" · {session.duration_seconds // 60} min" if session.duration_seconds else ""),
    )
    db.add(feed_entry)
    await db.flush()

    await db.commit()

    result = await db.execute(
        select(WorkoutSession)
        .where(WorkoutSession.id == session_id)
        .options(selectinload(WorkoutSession.exercises).selectinload(WorkoutExercise.sets))
    )
    return WorkoutSessionResponse.model_validate(result.scalar_one())


@router.delete("/{session_id}", status_code=204)
async def cancel_workout(
    session_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    session = await _get_session_for_user(session_id, current_user.id, db)
    session.status = "cancelled"
    await db.commit()


# ─── Exercises within session ────────────────────────────────────────────────

@router.post("/{session_id}/exercises", response_model=WorkoutExerciseResponse, status_code=201)
async def add_exercise(
    session_id: int,
    body: WorkoutExerciseCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    session = await _get_session_for_user(session_id, current_user.id, db)

    # Validate exercise exists
    ex_result = await db.execute(select(ExerciseLibrary).where(ExerciseLibrary.id == body.exercise_library_id))
    if not ex_result.scalar_one_or_none():
        _not_found("Exercise not found in library")

    we = WorkoutExercise(
        session_id=session_id,
        exercise_library_id=body.exercise_library_id,
        exercise_order=body.exercise_order,
        notes=body.notes,
        rest_seconds=body.rest_seconds,
    )
    db.add(we)
    await db.commit()
    await db.refresh(we)

    result = await db.execute(
        select(WorkoutExercise)
        .where(WorkoutExercise.id == we.id)
        .options(selectinload(WorkoutExercise.sets))
    )
    return WorkoutExerciseResponse.model_validate(result.scalar_one())


@router.delete("/{session_id}/exercises/{exercise_id}", status_code=204)
async def remove_exercise(
    session_id: int,
    exercise_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    await _get_session_for_user(session_id, current_user.id, db)
    result = await db.execute(
        select(WorkoutExercise).where(
            WorkoutExercise.id == exercise_id,
            WorkoutExercise.session_id == session_id,
        )
    )
    we = result.scalar_one_or_none()
    if not we:
        _not_found("Exercise not found in this session")
    await db.delete(we)
    await db.commit()


# ─── Sets ────────────────────────────────────────────────────────────────────

@router.post(
    "/{session_id}/exercises/{exercise_id}/sets",
    response_model=WorkoutSetResponse,
    status_code=201,
)
async def add_set(
    session_id: int,
    exercise_id: int,
    body: WorkoutSetCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    await _get_session_for_user(session_id, current_user.id, db)

    result = await db.execute(
        select(WorkoutExercise).where(
            WorkoutExercise.id == exercise_id,
            WorkoutExercise.session_id == session_id,
        )
    )
    we = result.scalar_one_or_none()
    if not we:
        _not_found("Exercise not found in this session")

    # Fetch previous best for this exercise (hint)
    prev_result = await db.execute(
        select(PersonalRecord).where(
            PersonalRecord.user_id == current_user.id,
            PersonalRecord.exercise_id == we.exercise_library_id,  # type: ignore[union-attr]
        )
    )
    ws = WorkoutSet(
        workout_exercise_id=exercise_id,
        set_number=body.set_number,
        set_type=body.set_type,
        reps=body.reps,
        weight_kg=body.weight_kg,
        duration_seconds=body.duration_seconds,
        distance_km=body.distance_km,
        rpe=body.rpe,
    )
    db.add(ws)
    await db.commit()
    await db.refresh(ws)
    return WorkoutSetResponse.model_validate(ws)


@router.patch(
    "/{session_id}/exercises/{exercise_id}/sets/{set_id}",
    response_model=WorkoutSetResponse,
)
async def update_set(
    session_id: int,
    exercise_id: int,
    set_id: int,
    body: WorkoutSetUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    await _get_session_for_user(session_id, current_user.id, db)

    result = await db.execute(
        select(WorkoutSet).where(
            WorkoutSet.id == set_id,
            WorkoutSet.workout_exercise_id == exercise_id,
        )
    )
    ws = result.scalar_one_or_none()
    if not ws:
        _not_found("Set not found")

    for field, value in body.model_dump(exclude_none=True).items():
        setattr(ws, field, value)

    if body.completed and not ws.completed_at:
        ws.completed_at = datetime.now(timezone.utc)
        ws.completed = True

    await db.commit()
    await db.refresh(ws)
    return WorkoutSetResponse.model_validate(ws)


@router.delete(
    "/{session_id}/exercises/{exercise_id}/sets/{set_id}",
    status_code=204,
)
async def delete_set(
    session_id: int,
    exercise_id: int,
    set_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    await _get_session_for_user(session_id, current_user.id, db)
    result = await db.execute(
        select(WorkoutSet).where(
            WorkoutSet.id == set_id,
            WorkoutSet.workout_exercise_id == exercise_id,
        )
    )
    ws = result.scalar_one_or_none()
    if not ws:
        _not_found("Set not found")
    await db.delete(ws)
    await db.commit()


# ─── Save workout as template ────────────────────────────────────────────────

@router.post("/{workout_id}/save-as-template", response_model=TemplateOut, status_code=201)
async def save_as_template(
    workout_id: int,
    body: TemplateSaveFromWorkout,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """Save an existing workout session as a reusable template."""
    from app.core.exceptions import ForbiddenError

    session = await _get_session_for_user(
        workout_id, current_user.id, db, load_relations=True
    )

    template = WorkoutTemplate(
        user_id=current_user.id,
        name=body.name,
        description=body.description,
        is_public=body.is_public,
        estimated_duration_min=body.estimated_duration_min,
    )
    db.add(template)
    await db.flush()

    for order, we in enumerate(session.exercises, start=1):
        te = TemplateExercise(
            template_id=template.id,
            exercise_library_id=we.exercise_library_id,
            exercise_order=we.exercise_order or order,
            rest_seconds=we.rest_seconds,
            notes=we.notes,
        )
        db.add(te)

    await db.commit()

    result = await db.execute(
        select(WorkoutTemplate)
        .where(WorkoutTemplate.id == template.id)
        .options(selectinload(WorkoutTemplate.exercises))
    )
    t = result.scalar_one()
    return TemplateOut(
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
