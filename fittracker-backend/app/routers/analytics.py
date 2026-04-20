import csv
import io
from datetime import date, timedelta
from typing import Optional

from fastapi import APIRouter, Depends, Query
from fastapi.responses import StreamingResponse
from sqlalchemy import func, select, desc
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload
from pydantic import BaseModel

from app.database import get_db
from app.dependencies import get_current_active_user
from app.models.exercise import ExerciseLibrary, PersonalRecord
from app.models.gamification import UserXP
from app.models.nutrition import MealLog, NutritionGoal
from app.models.body import BodyMetric
from app.models.workout import WorkoutExercise, WorkoutSession, WorkoutSet
from app.models.user import User

router = APIRouter(prefix="/api/analytics", tags=["analytics"])


# ── Schemas ───────────────────────────────────────────────────────────────────
class DashboardStats(BaseModel):
    this_week_workouts: int
    this_month_workouts: int
    total_workouts: int
    total_volume_kg: float
    avg_workout_duration_min: float
    current_streak: int
    this_week_calories: float
    recent_prs: list[dict]


class StrengthPoint(BaseModel):
    date: str
    max_weight_kg: float
    total_volume: float


class StrengthData(BaseModel):
    chart: list[StrengthPoint]
    pr_weight: float | None
    pr_date: str | None


class MuscleGroup(BaseModel):
    muscle_group: str
    sets_count: int
    percentage: float


class PRRecord(BaseModel):
    exercise_id: int
    exercise_name: str
    weight_kg: float
    reps: int | None
    achieved_at: str


class CalendarDay(BaseModel):
    date: str
    has_workout: bool


class StreakCalendar(BaseModel):
    current_streak: int
    longest_streak: int
    calendar: list[CalendarDay]


class VolumePoint(BaseModel):
    date: str
    volume_kg: float
    workout_count: int


class WorkoutFreqPoint(BaseModel):
    date: str
    count: int


# ── Helpers ───────────────────────────────────────────────────────────────────
def _period_start(period: str) -> date:
    today = date.today()
    if period == "7d":
        return today - timedelta(days=7)
    elif period == "30d":
        return today - timedelta(days=30)
    elif period == "90d":
        return today - timedelta(days=90)
    elif period == "1y":
        return today - timedelta(days=365)
    return date(2000, 1, 1)  # 'all'


# ── Endpoints ─────────────────────────────────────────────────────────────────

@router.get("/dashboard", response_model=DashboardStats)
async def dashboard(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    today = date.today()
    week_start = today - timedelta(days=today.weekday())
    month_start = today.replace(day=1)

    # Workout counts
    def wcount(since: date):
        return select(func.count(WorkoutSession.id)).where(
            WorkoutSession.user_id == current_user.id,
            WorkoutSession.status == "finished",
            func.date(WorkoutSession.started_at) >= since,
        )

    this_week_wc = (await db.execute(wcount(week_start))).scalar() or 0
    this_month_wc = (await db.execute(wcount(month_start))).scalar() or 0

    total_r = await db.execute(
        select(
            func.count(WorkoutSession.id),
            func.coalesce(func.sum(WorkoutSession.total_volume_kg), 0),
            func.coalesce(func.avg(WorkoutSession.duration_seconds), 0),
        ).where(
            WorkoutSession.user_id == current_user.id,
            WorkoutSession.status == "finished",
        )
    )
    total_count, total_vol, avg_dur = total_r.one()

    # Streak
    xp_r = await db.execute(select(UserXP).where(UserXP.user_id == current_user.id))
    xp = xp_r.scalar_one_or_none()
    streak = xp.current_streak_days if xp else 0

    # This week calories from nutrition
    cal_r = await db.execute(
        select(func.coalesce(func.sum(MealLog.calories), 0)).where(
            MealLog.user_id == current_user.id,
            func.date(MealLog.logged_at) >= week_start,
        )
    )
    week_cal = float(cal_r.scalar() or 0)

    # Recent PRs
    pr_r = await db.execute(
        select(PersonalRecord, ExerciseLibrary.name)
        .join(ExerciseLibrary, PersonalRecord.exercise_id == ExerciseLibrary.id)
        .where(PersonalRecord.user_id == current_user.id)
        .order_by(desc(PersonalRecord.achieved_at))
        .limit(5)
    )
    recent_prs = [
        {"exercise": name, "weight_kg": float(pr.weight_kg), "date": str(pr.achieved_at)[:10]}
        for pr, name in pr_r.all()
    ]

    return DashboardStats(
        this_week_workouts=this_week_wc,
        this_month_workouts=this_month_wc,
        total_workouts=total_count,
        total_volume_kg=round(float(total_vol), 1),
        avg_workout_duration_min=round(float(avg_dur) / 60, 1),
        current_streak=streak,
        this_week_calories=round(week_cal, 0),
        recent_prs=recent_prs,
    )


@router.get("/strength", response_model=StrengthData)
async def strength_progress(
    exercise_id: int = Query(...),
    period: str = Query("90d"),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    since = _period_start(period)

    result = await db.execute(
        select(
            func.date(WorkoutSession.started_at).label("d"),
            func.max(WorkoutSet.weight_kg).label("max_w"),
            func.sum(WorkoutSet.weight_kg * WorkoutSet.reps).label("vol"),
        )
        .join(WorkoutExercise, WorkoutSet.workout_exercise_id == WorkoutExercise.id)
        .join(WorkoutSession, WorkoutExercise.workout_session_id == WorkoutSession.id)
        .where(
            WorkoutSession.user_id == current_user.id,
            WorkoutSession.status == "finished",
            WorkoutExercise.exercise_library_id == exercise_id,
            WorkoutSet.completed == True,
            func.date(WorkoutSession.started_at) >= since,
        )
        .group_by(func.date(WorkoutSession.started_at))
        .order_by(func.date(WorkoutSession.started_at))
    )
    rows = result.all()

    pr_r = await db.execute(
        select(PersonalRecord).where(
            PersonalRecord.user_id == current_user.id,
            PersonalRecord.exercise_id == exercise_id,
        )
    )
    pr = pr_r.scalar_one_or_none()

    return StrengthData(
        chart=[StrengthPoint(date=str(r.d), max_weight_kg=float(r.max_w or 0), total_volume=float(r.vol or 0)) for r in rows],
        pr_weight=float(pr.weight_kg) if pr else None,
        pr_date=str(pr.achieved_at)[:10] if pr else None,
    )


@router.get("/volume", response_model=list[VolumePoint])
async def volume_over_time(
    period: str = Query("30d"),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    since = _period_start(period)
    result = await db.execute(
        select(
            func.date(WorkoutSession.started_at).label("d"),
            func.coalesce(func.sum(WorkoutSession.total_volume_kg), 0).label("vol"),
            func.count(WorkoutSession.id).label("cnt"),
        )
        .where(
            WorkoutSession.user_id == current_user.id,
            WorkoutSession.status == "finished",
            func.date(WorkoutSession.started_at) >= since,
        )
        .group_by(func.date(WorkoutSession.started_at))
        .order_by(func.date(WorkoutSession.started_at))
    )
    return [VolumePoint(date=str(r.d), volume_kg=round(float(r.vol), 1), workout_count=r.cnt) for r in result.all()]


@router.get("/muscles", response_model=list[MuscleGroup])
async def muscle_distribution(
    period: str = Query("30d"),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    since = _period_start(period)
    result = await db.execute(
        select(
            ExerciseLibrary.primary_muscle,
            func.count(WorkoutSet.id).label("sets"),
        )
        .join(WorkoutExercise, WorkoutSet.workout_exercise_id == WorkoutExercise.id)
        .join(WorkoutSession, WorkoutExercise.workout_session_id == WorkoutSession.id)
        .join(ExerciseLibrary, WorkoutExercise.exercise_library_id == ExerciseLibrary.id)
        .where(
            WorkoutSession.user_id == current_user.id,
            WorkoutSession.status == "finished",
            WorkoutSet.completed == True,
            func.date(WorkoutSession.started_at) >= since,
        )
        .group_by(ExerciseLibrary.primary_muscle)
        .order_by(desc(func.count(WorkoutSet.id)))
    )
    rows = result.all()
    total = sum(r.sets for r in rows) or 1
    return [
        MuscleGroup(muscle_group=r.primary_muscle or "Other", sets_count=r.sets, percentage=round(r.sets / total * 100, 1))
        for r in rows
    ]


@router.get("/personal-records", response_model=list[PRRecord])
async def personal_records(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    result = await db.execute(
        select(PersonalRecord, ExerciseLibrary.name)
        .join(ExerciseLibrary, PersonalRecord.exercise_id == ExerciseLibrary.id)
        .where(PersonalRecord.user_id == current_user.id)
        .order_by(desc(PersonalRecord.achieved_at))
    )
    return [
        PRRecord(
            exercise_id=pr.exercise_id,
            exercise_name=name,
            weight_kg=float(pr.weight_kg),
            reps=pr.reps,
            achieved_at=str(pr.achieved_at)[:10],
        )
        for pr, name in result.all()
    ]


@router.get("/streak", response_model=StreakCalendar)
async def streak_calendar(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    today = date.today()
    since = today - timedelta(days=364)

    result = await db.execute(
        select(func.date(WorkoutSession.started_at).label("d"))
        .where(
            WorkoutSession.user_id == current_user.id,
            WorkoutSession.status == "finished",
            func.date(WorkoutSession.started_at) >= since,
        )
        .distinct()
    )
    workout_dates = {r.d for r in result.all()}

    calendar = []
    for i in range(365):
        d = since + timedelta(days=i)
        calendar.append(CalendarDay(date=str(d), has_workout=d in workout_dates))

    xp_r = await db.execute(select(UserXP).where(UserXP.user_id == current_user.id))
    xp = xp_r.scalar_one_or_none()

    return StreakCalendar(
        current_streak=xp.current_streak_days if xp else 0,
        longest_streak=xp.longest_streak_days if xp else 0,
        calendar=calendar,
    )


@router.get("/workouts", response_model=list[WorkoutFreqPoint])
async def workout_frequency(
    period: str = Query("30d"),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    since = _period_start(period)
    result = await db.execute(
        select(
            func.date(WorkoutSession.started_at).label("d"),
            func.count(WorkoutSession.id).label("cnt"),
        )
        .where(
            WorkoutSession.user_id == current_user.id,
            WorkoutSession.status == "finished",
            func.date(WorkoutSession.started_at) >= since,
        )
        .group_by(func.date(WorkoutSession.started_at))
        .order_by(func.date(WorkoutSession.started_at))
    )
    return [WorkoutFreqPoint(date=str(r.d), count=r.cnt) for r in result.all()]


# ── Week 9: Advanced Analytics ────────────────────────────────────────────────

class VolumeProgressionPoint(BaseModel):
    week: str
    total_volume: float
    workout_count: int
    rolling_avg: float


class MuscleBalance(BaseModel):
    category: str
    sets_count: int
    percentage: float
    exercises: list[str]


class BodyCompositionPoint(BaseModel):
    date: str
    weight_kg: float | None
    body_fat_pct: float | None
    bmi: float | None


class NutritionHeatmapDay(BaseModel):
    date: str
    calories_logged: float
    goal_calories: float | None
    adherence_pct: float | None


_PUSH_MUSCLES = {"chest", "shoulders", "triceps"}
_PULL_MUSCLES = {"back", "biceps"}
_LEG_MUSCLES = {"quadriceps", "hamstrings", "glutes", "calves"}
_CORE_MUSCLES = {"abs", "core"}


def _muscle_category(muscle_primary: str | None) -> str:
    if not muscle_primary:
        return "other"
    muscles = {m.strip().lower() for m in muscle_primary.split(",")}
    if muscles & _PUSH_MUSCLES:
        return "push"
    if muscles & _PULL_MUSCLES:
        return "pull"
    if muscles & _LEG_MUSCLES:
        return "legs"
    if muscles & _CORE_MUSCLES:
        return "core"
    return "other"


@router.get("/volume-progression", response_model=list[VolumeProgressionPoint])
async def volume_progression(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    since = date.today() - timedelta(weeks=16)
    result = await db.execute(
        select(
            func.strftime("%Y-W%W", WorkoutSession.started_at).label("week"),
            func.coalesce(func.sum(WorkoutSession.total_volume_kg), 0).label("vol"),
            func.count(WorkoutSession.id).label("cnt"),
        )
        .where(
            WorkoutSession.user_id == current_user.id,
            WorkoutSession.status == "finished",
            func.date(WorkoutSession.started_at) >= since,
        )
        .group_by(func.strftime("%Y-W%W", WorkoutSession.started_at))
        .order_by(func.strftime("%Y-W%W", WorkoutSession.started_at))
    )
    rows = result.all()

    points = []
    vols = [float(r.vol) for r in rows]
    for i, r in enumerate(rows):
        window = vols[max(0, i - 3) : i + 1]
        rolling_avg = sum(window) / len(window)
        points.append(
            VolumeProgressionPoint(
                week=r.week,
                total_volume=round(float(r.vol), 1),
                workout_count=r.cnt,
                rolling_avg=round(rolling_avg, 1),
            )
        )
    return points


@router.get("/muscle-balance", response_model=list[MuscleBalance])
async def muscle_balance(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    since = date.today() - timedelta(days=30)
    result = await db.execute(
        select(
            ExerciseLibrary.name,
            ExerciseLibrary.muscle_primary,
            func.count(WorkoutSet.id).label("sets"),
        )
        .join(WorkoutExercise, WorkoutSet.workout_exercise_id == WorkoutExercise.id)
        .join(WorkoutSession, WorkoutExercise.session_id == WorkoutSession.id)
        .join(ExerciseLibrary, WorkoutExercise.exercise_library_id == ExerciseLibrary.id)
        .where(
            WorkoutSession.user_id == current_user.id,
            WorkoutSession.status == "finished",
            WorkoutSet.completed == True,
            func.date(WorkoutSession.started_at) >= since,
        )
        .group_by(ExerciseLibrary.id, ExerciseLibrary.name, ExerciseLibrary.muscle_primary)
        .order_by(desc(func.count(WorkoutSet.id)))
    )
    rows = result.all()

    cats: dict[str, dict] = {
        "push": {"sets": 0, "exercises": []},
        "pull": {"sets": 0, "exercises": []},
        "legs": {"sets": 0, "exercises": []},
        "core": {"sets": 0, "exercises": []},
        "other": {"sets": 0, "exercises": []},
    }
    for r in rows:
        cat = _muscle_category(r.muscle_primary)
        cats[cat]["sets"] += r.sets
        cats[cat]["exercises"].append((r.name, r.sets))

    total = sum(c["sets"] for c in cats.values())
    output = []
    for cat_name, data in cats.items():
        top3 = [e[0] for e in sorted(data["exercises"], key=lambda x: x[1], reverse=True)[:3]]
        pct = round(data["sets"] / total * 100, 1) if total > 0 else 0.0
        output.append(
            MuscleBalance(category=cat_name, sets_count=data["sets"], percentage=pct, exercises=top3)
        )
    return output


@router.get("/body-composition", response_model=list[BodyCompositionPoint])
async def body_composition(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    since = date.today() - timedelta(days=90)
    result = await db.execute(
        select(BodyMetric)
        .where(
            BodyMetric.user_id == current_user.id,
            func.date(BodyMetric.recorded_at) >= since,
        )
        .order_by(BodyMetric.recorded_at)
    )
    metrics = result.scalars().all()
    return [
        BodyCompositionPoint(
            date=str(m.recorded_at)[:10],
            weight_kg=float(m.weight_kg) if m.weight_kg is not None else None,
            body_fat_pct=float(m.body_fat_pct) if m.body_fat_pct is not None else None,
            bmi=float(m.bmi) if m.bmi is not None else None,
        )
        for m in metrics
    ]


@router.get("/nutrition-heatmap", response_model=list[NutritionHeatmapDay])
async def nutrition_heatmap(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    today = date.today()
    since = today - timedelta(days=89)  # 90 days inclusive

    goal_r = await db.execute(
        select(NutritionGoal).where(NutritionGoal.user_id == current_user.id)
    )
    goal = goal_r.scalar_one_or_none()
    goal_calories = float(goal.calories_target) if goal else None

    cal_r = await db.execute(
        select(
            func.date(MealLog.logged_at).label("d"),
            func.sum(MealLog.calories).label("total"),
        )
        .where(
            MealLog.user_id == current_user.id,
            func.date(MealLog.logged_at) >= since,
        )
        .group_by(func.date(MealLog.logged_at))
    )
    daily_map = {str(r.d): float(r.total) for r in cal_r.all()}

    days = []
    for i in range(90):
        d = since + timedelta(days=i)
        d_str = str(d)
        cal = daily_map.get(d_str, 0.0)
        adherence = round(cal / goal_calories * 100, 1) if goal_calories else None
        days.append(
            NutritionHeatmapDay(
                date=d_str,
                calories_logged=cal,
                goal_calories=goal_calories,
                adherence_pct=adherence,
            )
        )
    return days


@router.get("/export/csv")
async def export_workouts_csv(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    result = await db.execute(
        select(WorkoutSession)
        .where(
            WorkoutSession.user_id == current_user.id,
            WorkoutSession.status == "finished",
        )
        .options(
            selectinload(WorkoutSession.exercises).selectinload(WorkoutExercise.exercise),
            selectinload(WorkoutSession.exercises).selectinload(WorkoutExercise.sets),
        )
        .order_by(WorkoutSession.started_at)
    )
    sessions = result.scalars().all()

    output = io.StringIO()
    fieldnames = ["date", "workout_name", "duration_min", "total_volume_kg", "exercises"]
    writer = csv.DictWriter(output, fieldnames=fieldnames)
    writer.writeheader()
    for session in sessions:
        exercises_str = "; ".join(
            f"{we.exercise.name}:{len(we.sets)}sets"
            for we in session.exercises
            if we.exercise
        )
        writer.writerow(
            {
                "date": str(session.started_at)[:10],
                "workout_name": session.name,
                "duration_min": (
                    round(session.duration_seconds / 60, 1) if session.duration_seconds else 0
                ),
                "total_volume_kg": float(session.total_volume_kg),
                "exercises": exercises_str,
            }
        )
    output.seek(0)
    return StreamingResponse(
        iter([output.getvalue()]),
        media_type="text/csv",
        headers={
            "Content-Disposition": f'attachment; filename="workouts_{current_user.username}.csv"'
        },
    )
