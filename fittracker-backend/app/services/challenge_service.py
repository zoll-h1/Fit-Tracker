from datetime import date, timezone, datetime
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from app.models.challenges import Challenge, ChallengeParticipant
from app.models.workout import WorkoutSession


async def update_challenge_progress(db: AsyncSession, user_id: int) -> None:
    """Recalculate challenge progress for a user across all active challenges they participate in."""
    today = date.today()

    result = await db.execute(
        select(ChallengeParticipant)
        .join(Challenge, Challenge.id == ChallengeParticipant.challenge_id)
        .where(
            ChallengeParticipant.user_id == user_id,
            Challenge.status == "active",
            Challenge.start_date <= today,
            Challenge.end_date >= today,
        )
    )
    participations = result.scalars().all()

    for part in participations:
        challenge = await db.get(Challenge, part.challenge_id)
        if not challenge:
            continue

        progress = 0.0
        start_dt = datetime.combine(challenge.start_date, datetime.min.time()).replace(tzinfo=timezone.utc)

        if challenge.challenge_type == "total_workouts":
            count_result = await db.execute(
                select(func.count(WorkoutSession.id)).where(
                    WorkoutSession.user_id == user_id,
                    WorkoutSession.status == "finished",
                    WorkoutSession.finished_at >= start_dt,
                )
            )
            progress = float(count_result.scalar() or 0)

        elif challenge.challenge_type == "total_volume":
            vol_result = await db.execute(
                select(func.sum(WorkoutSession.total_volume_kg)).where(
                    WorkoutSession.user_id == user_id,
                    WorkoutSession.status == "finished",
                    WorkoutSession.finished_at >= start_dt,
                )
            )
            progress = float(vol_result.scalar() or 0)

        elif challenge.challenge_type == "streak":
            count_result = await db.execute(
                select(func.count(WorkoutSession.id)).where(
                    WorkoutSession.user_id == user_id,
                    WorkoutSession.status == "finished",
                    WorkoutSession.finished_at >= start_dt,
                )
            )
            progress = float(count_result.scalar() or 0)

        part.current_progress = progress

    await db.flush()


async def update_leaderboard_ranks(db: AsyncSession, challenge_id: int) -> None:
    """Update ranks for all participants of a challenge based on current_progress."""
    result = await db.execute(
        select(ChallengeParticipant)
        .where(ChallengeParticipant.challenge_id == challenge_id)
        .order_by(ChallengeParticipant.current_progress.desc())
    )
    participants = result.scalars().all()
    for rank, part in enumerate(participants, start=1):
        part.rank = rank
    await db.flush()
