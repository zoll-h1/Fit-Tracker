"""APScheduler background jobs."""

from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger

scheduler = AsyncIOScheduler()


async def streak_warning_job() -> None:
    """Daily job: send streak warnings to users whose streak is about to break."""
    from datetime import date, timedelta
    from sqlalchemy import select
    from app.database import AsyncSessionLocal
    from app.models.gamification import UserXP
    from app.services.notification_service import create_notification

    today = date.today()
    yesterday = today - timedelta(days=1)

    async with AsyncSessionLocal() as db:
        # Users with streak ≥ 3 who haven't worked out today
        result = await db.execute(
            select(UserXP).where(
                UserXP.current_streak_days >= 3,
                UserXP.last_workout_date == yesterday,
            )
        )
        at_risk = result.scalars().all()

        for xp_row in at_risk:
            await create_notification(
                db=db,
                user_id=xp_row.user_id,
                notification_type="streak_warning",
                title="⚠️ Streak at Risk!",
                body=f"Your {xp_row.current_streak_days}-day streak ends tonight. Log a workout to keep it alive!",
                action_url="/workouts",
            )

        await db.commit()


async def challenge_completion_job():
    """Mark challenges as completed if end_date has passed."""
    from app.database import AsyncSessionLocal
    from app.models.challenges import Challenge, ChallengeParticipant
    from datetime import date
    from sqlalchemy import select
    async with AsyncSessionLocal() as db:
        today = date.today()
        result = await db.execute(
            select(Challenge).where(Challenge.status == "active", Challenge.end_date < today)
        )
        challenges = result.scalars().all()
        for challenge in challenges:
            challenge.status = "completed"
            winner_result = await db.execute(
                select(ChallengeParticipant).where(
                    ChallengeParticipant.challenge_id == challenge.id,
                    ChallengeParticipant.rank == 1
                )
            )
            winner = winner_result.scalar_one_or_none()
            if winner:
                challenge.winner_user_id = winner.user_id
        await db.commit()


def start_scheduler() -> None:
    scheduler.add_job(
        streak_warning_job,
        trigger=CronTrigger(hour=20, minute=0),  # 8 PM daily
        id="streak_warning",
        replace_existing=True,
    )
    scheduler.add_job(
        challenge_completion_job,
        "cron",
        hour=23,
        minute=59,
        id="challenge_completion",
        replace_existing=True,
    )
    scheduler.start()


def stop_scheduler() -> None:
    if scheduler.running:
        scheduler.shutdown(wait=False)
