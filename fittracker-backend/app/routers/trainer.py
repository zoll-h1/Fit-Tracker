from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import selectinload
from sqlalchemy.ext.asyncio import AsyncSession
from pydantic import BaseModel
from typing import Optional
from datetime import datetime

from app.database import get_db
from app.dependencies import get_current_active_user
from app.models.user import User
from app.models.trainer import WorkoutProgram, ProgramDay, ProgramExercise, ProgramAssignment
from app.models.exercise import ExerciseLibrary
from app.models.workout import WorkoutSession
from app.models.gamification import UserXP

router = APIRouter(prefix="/api/trainer", tags=["trainer"])

# ── Helpers ───────────────────────────────────────────────────────────────────

def _require_trainer(user: User):
    if user.role not in ("trainer", "admin"):
        raise HTTPException(status_code=403, detail="Trainer role required")

# ── Schemas ───────────────────────────────────────────────────────────────────

class ProgramExerciseIn(BaseModel):
    exercise_id: int
    exercise_order: int = 1
    sets: int = 3
    reps: Optional[str] = None
    weight_note: Optional[str] = None
    rest_seconds: int = 90

class ProgramDayIn(BaseModel):
    week_number: int
    day_number: int
    name: Optional[str] = None
    exercises: list[ProgramExerciseIn] = []

class ProgramCreate(BaseModel):
    title: str
    description: Optional[str] = None
    duration_weeks: int = 4
    difficulty: str = "intermediate"
    is_public: bool = False
    days: list[ProgramDayIn] = []

class ProgramExerciseOut(BaseModel):
    id: int
    exercise_id: int
    exercise_name: str
    exercise_order: int
    sets: int
    reps: Optional[str]
    weight_note: Optional[str]
    rest_seconds: int
    model_config = {"from_attributes": True}

class ProgramDayOut(BaseModel):
    id: int
    week_number: int
    day_number: int
    name: Optional[str]
    exercises: list[ProgramExerciseOut]
    model_config = {"from_attributes": True}

class ProgramOut(BaseModel):
    id: int
    trainer_id: int
    title: str
    description: Optional[str]
    duration_weeks: int
    difficulty: str
    is_public: bool
    created_at: datetime
    days_count: int
    assignment_count: int
    model_config = {"from_attributes": True}

class ProgramDetailOut(BaseModel):
    id: int
    trainer_id: int
    title: str
    description: Optional[str]
    duration_weeks: int
    difficulty: str
    is_public: bool
    created_at: datetime
    days: list[ProgramDayOut]
    model_config = {"from_attributes": True}

class AssignmentCreate(BaseModel):
    client_username: str
    start_date: Optional[datetime] = None

class AssignmentOut(BaseModel):
    id: int
    program_id: int
    client_id: int
    client_username: str
    trainer_id: int
    assigned_at: datetime
    status: str
    model_config = {"from_attributes": True}

class ClientStats(BaseModel):
    user_id: int
    username: str
    total_workouts: int
    this_week_workouts: int
    current_streak: int
    level: int
    assigned_programs: list[str]

# ── Trainer upgrade ───────────────────────────────────────────────────────────

@router.post("/become-trainer", status_code=200)
async def become_trainer(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """Upgrade current user to trainer role."""
    if current_user.role == "admin":
        raise HTTPException(400, "Admin already has elevated privileges")
    current_user.role = "trainer"
    await db.commit()
    return {"message": "You are now a trainer", "role": "trainer"}

# ── Program CRUD ──────────────────────────────────────────────────────────────

@router.post("/programs", status_code=201, response_model=ProgramDetailOut)
async def create_program(
    body: ProgramCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    _require_trainer(current_user)
    program = WorkoutProgram(
        trainer_id=current_user.id,
        title=body.title,
        description=body.description,
        duration_weeks=body.duration_weeks,
        difficulty=body.difficulty,
        is_public=body.is_public,
    )
    db.add(program)
    await db.flush()
    for day_in in body.days:
        day = ProgramDay(
            program_id=program.id,
            week_number=day_in.week_number,
            day_number=day_in.day_number,
            name=day_in.name,
        )
        db.add(day)
        await db.flush()
        for ex_in in day_in.exercises:
            ex = ProgramExercise(
                day_id=day.id,
                exercise_id=ex_in.exercise_id,
                exercise_order=ex_in.exercise_order,
                sets=ex_in.sets,
                reps=ex_in.reps,
                weight_note=ex_in.weight_note,
                rest_seconds=ex_in.rest_seconds,
            )
            db.add(ex)
    await db.commit()
    result = await db.execute(
        select(WorkoutProgram)
        .where(WorkoutProgram.id == program.id)
        .options(
            selectinload(WorkoutProgram.days).selectinload(ProgramDay.exercises).selectinload(ProgramExercise.exercise)
        )
    )
    prog = result.scalar_one()
    days_out = []
    for d in prog.days:
        exs_out = [ProgramExerciseOut(
            id=e.id, exercise_id=e.exercise_id, exercise_name=e.exercise.name,
            exercise_order=e.exercise_order, sets=e.sets, reps=e.reps,
            weight_note=e.weight_note, rest_seconds=e.rest_seconds
        ) for e in d.exercises]
        days_out.append(ProgramDayOut(id=d.id, week_number=d.week_number, day_number=d.day_number, name=d.name, exercises=exs_out))
    return ProgramDetailOut(
        id=prog.id, trainer_id=prog.trainer_id, title=prog.title,
        description=prog.description, duration_weeks=prog.duration_weeks,
        difficulty=prog.difficulty, is_public=prog.is_public,
        created_at=prog.created_at, days=days_out
    )

@router.get("/programs/public", response_model=list[ProgramOut])
async def list_public_programs(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    result = await db.execute(
        select(WorkoutProgram)
        .where(WorkoutProgram.is_public == True)
        .options(selectinload(WorkoutProgram.days), selectinload(WorkoutProgram.assignments))
        .order_by(WorkoutProgram.created_at.desc())
        .limit(50)
    )
    programs = result.scalars().all()
    return [ProgramOut(
        id=p.id, trainer_id=p.trainer_id, title=p.title, description=p.description,
        duration_weeks=p.duration_weeks, difficulty=p.difficulty, is_public=p.is_public,
        created_at=p.created_at, days_count=len(p.days),
        assignment_count=len(p.assignments)
    ) for p in programs]

@router.get("/programs", response_model=list[ProgramOut])
async def list_my_programs(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    _require_trainer(current_user)
    result = await db.execute(
        select(WorkoutProgram)
        .where(WorkoutProgram.trainer_id == current_user.id)
        .options(selectinload(WorkoutProgram.days), selectinload(WorkoutProgram.assignments))
        .order_by(WorkoutProgram.created_at.desc())
    )
    programs = result.scalars().all()
    return [ProgramOut(
        id=p.id, trainer_id=p.trainer_id, title=p.title, description=p.description,
        duration_weeks=p.duration_weeks, difficulty=p.difficulty, is_public=p.is_public,
        created_at=p.created_at, days_count=len(p.days),
        assignment_count=len(p.assignments)
    ) for p in programs]

@router.get("/programs/{program_id}", response_model=ProgramDetailOut)
async def get_program(
    program_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    result = await db.execute(
        select(WorkoutProgram)
        .where(WorkoutProgram.id == program_id)
        .options(
            selectinload(WorkoutProgram.days).selectinload(ProgramDay.exercises).selectinload(ProgramExercise.exercise)
        )
    )
    prog = result.scalar_one_or_none()
    if not prog:
        raise HTTPException(404, "Program not found")
    if prog.trainer_id != current_user.id and not prog.is_public and current_user.role != "admin":
        raise HTTPException(403, "Access denied")
    days_out = []
    for d in prog.days:
        exs_out = [ProgramExerciseOut(
            id=e.id, exercise_id=e.exercise_id, exercise_name=e.exercise.name,
            exercise_order=e.exercise_order, sets=e.sets, reps=e.reps,
            weight_note=e.weight_note, rest_seconds=e.rest_seconds
        ) for e in d.exercises]
        days_out.append(ProgramDayOut(id=d.id, week_number=d.week_number, day_number=d.day_number, name=d.name, exercises=exs_out))
    return ProgramDetailOut(
        id=prog.id, trainer_id=prog.trainer_id, title=prog.title,
        description=prog.description, duration_weeks=prog.duration_weeks,
        difficulty=prog.difficulty, is_public=prog.is_public,
        created_at=prog.created_at, days=days_out
    )

@router.delete("/programs/{program_id}", status_code=204)
async def delete_program(
    program_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    _require_trainer(current_user)
    result = await db.execute(select(WorkoutProgram).where(WorkoutProgram.id == program_id))
    prog = result.scalar_one_or_none()
    if not prog:
        raise HTTPException(404)
    if prog.trainer_id != current_user.id and current_user.role != "admin":
        raise HTTPException(403)
    await db.delete(prog)
    await db.commit()

# ── Assignments ───────────────────────────────────────────────────────────────

@router.post("/programs/{program_id}/assign", status_code=201, response_model=AssignmentOut)
async def assign_program(
    program_id: int,
    body: AssignmentCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    _require_trainer(current_user)
    prog_result = await db.execute(select(WorkoutProgram).where(WorkoutProgram.id == program_id))
    prog = prog_result.scalar_one_or_none()
    if not prog:
        raise HTTPException(404, "Program not found")
    if prog.trainer_id != current_user.id and current_user.role != "admin":
        raise HTTPException(403)
    client_result = await db.execute(select(User).where(User.username == body.client_username))
    client = client_result.scalar_one_or_none()
    if not client:
        raise HTTPException(404, "Client user not found")
    assignment = ProgramAssignment(
        program_id=program_id,
        client_id=client.id,
        trainer_id=current_user.id,
        start_date=body.start_date,
    )
    db.add(assignment)
    await db.commit()
    await db.refresh(assignment)
    return AssignmentOut(
        id=assignment.id, program_id=assignment.program_id,
        client_id=assignment.client_id, client_username=client.username,
        trainer_id=assignment.trainer_id, assigned_at=assignment.assigned_at,
        status=assignment.status
    )

@router.get("/clients", response_model=list[ClientStats])
async def get_my_clients(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """Returns stats for all clients with active assignments from this trainer."""
    _require_trainer(current_user)
    from datetime import timedelta
    from sqlalchemy import func

    assignments_result = await db.execute(
        select(ProgramAssignment)
        .where(ProgramAssignment.trainer_id == current_user.id, ProgramAssignment.status == "active")
        .options(selectinload(ProgramAssignment.client), selectinload(ProgramAssignment.program))
    )
    assignments = assignments_result.scalars().all()

    client_programs: dict[int, list[str]] = {}
    client_users: dict[int, User] = {}
    for a in assignments:
        client_programs.setdefault(a.client_id, []).append(a.program.title)
        client_users[a.client_id] = a.client

    stats = []
    week_ago = datetime.utcnow() - timedelta(days=7)
    for client_id, client in client_users.items():
        total_result = await db.execute(
            select(func.count(WorkoutSession.id))
            .where(WorkoutSession.user_id == client_id, WorkoutSession.status == "finished")
        )
        total_workouts = total_result.scalar() or 0
        week_result = await db.execute(
            select(func.count(WorkoutSession.id))
            .where(WorkoutSession.user_id == client_id, WorkoutSession.status == "finished",
                   WorkoutSession.started_at >= week_ago)
        )
        this_week = week_result.scalar() or 0
        xp_result = await db.execute(select(UserXP).where(UserXP.user_id == client_id))
        xp = xp_result.scalar_one_or_none()
        stats.append(ClientStats(
            user_id=client_id, username=client.username,
            total_workouts=total_workouts, this_week_workouts=this_week,
            current_streak=xp.current_streak_days if xp else 0,
            level=xp.current_level if xp else 1,
            assigned_programs=client_programs.get(client_id, [])
        ))
    return stats

@router.get("/my-assignments", response_model=list[AssignmentOut])
async def get_my_program_assignments(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """For a regular user — see programs assigned to them."""
    result = await db.execute(
        select(ProgramAssignment)
        .where(ProgramAssignment.client_id == current_user.id, ProgramAssignment.status == "active")
        .options(selectinload(ProgramAssignment.program), selectinload(ProgramAssignment.trainer))
    )
    assignments = result.scalars().all()
    return [AssignmentOut(
        id=a.id, program_id=a.program_id, client_id=a.client_id,
        client_username=current_user.username, trainer_id=a.trainer_id,
        assigned_at=a.assigned_at, status=a.status
    ) for a in assignments]
