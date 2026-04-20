"""Gamification service: XP awards, level-ups, streak tracking, achievement checks."""

from datetime import date, timedelta
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func

from app.models.gamification import UserXP, AchievementDefinition, UserAchievement
from app.models.workout import WorkoutSession
from app.models.exercise import PersonalRecord
from app.models.nutrition import MealLog
from app.models.body import BodyMetric, BodyGoal

# XP award amounts
XP_AWARDS = {
    "complete_workout": 50,
    "pr_achieved": 100,
    "streak_7": 200,
    "streak_30": 500,
    "goal_reached": 150,
    "log_meal": 10,
    "log_body_metric": 20,
}

# Level thresholds: level → min XP required
LEVEL_THRESHOLDS = {
    1: 0,
    2: 500,
    3: 1200,
    4: 2500,
    5: 5000,
    6: 9000,
    7: 15000,
    8: 25000,
    9: 40000,
    10: 60000,
}

LEVEL_NAMES = {
    1: "Beginner",
    2: "Rookie",
    3: "Amateur",
    4: "Intermediate",
    5: "Advanced",
    6: "Expert",
    7: "Elite",
    8: "Master",
    9: "Champion",
    10: "Legend",
}


def xp_to_level(total_xp: int) -> int:
    level = 1
    for lvl, threshold in sorted(LEVEL_THRESHOLDS.items()):
        if total_xp >= threshold:
            level = lvl
    return level


async def _get_or_create_xp(db: AsyncSession, user_id: int) -> UserXP:
    result = await db.execute(select(UserXP).where(UserXP.user_id == user_id))
    xp = result.scalar_one_or_none()
    if not xp:
        xp = UserXP(user_id=user_id, total_xp=0, current_level=1)
        db.add(xp)
        await db.flush()
    return xp


async def award_xp(
    db: AsyncSession, user_id: int, amount: int, reason: str
) -> dict:
    """Award XP to a user. Returns {leveled_up, new_level, total_xp}."""
    xp = await _get_or_create_xp(db, user_id)

    old_level = xp.current_level
    xp.total_xp += amount
    xp.weekly_xp += amount
    xp.monthly_xp += amount

    new_level = xp_to_level(xp.total_xp)
    xp.current_level = new_level

    await db.flush()

    return {
        "leveled_up": new_level > old_level,
        "old_level": old_level,
        "new_level": new_level,
        "total_xp": xp.total_xp,
        "xp_awarded": amount,
        "reason": reason,
    }


async def update_streak(db: AsyncSession, user_id: int) -> dict:
    """Update workout streak. Call after a workout is completed."""
    xp = await _get_or_create_xp(db, user_id)
    today = date.today()

    if xp.last_workout_date == today:
        return {"streak": xp.current_streak_days, "extended": False}

    yesterday = today - timedelta(days=1)
    if xp.last_workout_date == yesterday:
        xp.current_streak_days += 1
    else:
        xp.current_streak_days = 1

    if xp.current_streak_days > xp.longest_streak_days:
        xp.longest_streak_days = xp.current_streak_days

    xp.last_workout_date = today
    await db.flush()

    # Award streak milestone XP
    streak_rewards = []
    if xp.current_streak_days == 7:
        result = await award_xp(db, user_id, XP_AWARDS["streak_7"], "7-day streak")
        streak_rewards.append(result)
    elif xp.current_streak_days == 30:
        result = await award_xp(db, user_id, XP_AWARDS["streak_30"], "30-day streak")
        streak_rewards.append(result)

    return {
        "streak": xp.current_streak_days,
        "extended": True,
        "streak_rewards": streak_rewards,
    }


async def check_achievements(
    db: AsyncSession, user_id: int, event_type: str
) -> list[dict]:
    """Check and award any newly earned achievements after an event."""
    # Load all achievement definitions
    defs_result = await db.execute(select(AchievementDefinition))
    all_defs = defs_result.scalars().all()

    # Load already-earned achievement IDs
    earned_result = await db.execute(
        select(UserAchievement.achievement_id).where(UserAchievement.user_id == user_id)
    )
    earned_ids = set(earned_result.scalars().all())

    xp = await _get_or_create_xp(db, user_id)

    newly_earned = []

    for defn in all_defs:
        if defn.id in earned_ids:
            continue

        qualified = await _check_single_achievement(db, user_id, xp, defn)
        if qualified:
            ua = UserAchievement(user_id=user_id, achievement_id=defn.id, notified=False)
            db.add(ua)
            earned_ids.add(defn.id)

            # Award XP for this achievement
            await award_xp(db, user_id, defn.xp_reward, f"achievement:{defn.key}")

            # Post to activity feed
            from app.models.social import ActivityFeed as ActivityFeedModel
            feed_entry = ActivityFeedModel(
                user_id=user_id,
                activity_type="achievement",
                ref_id=defn.id,
                title=f"Earned achievement: {defn.name}",
                body=defn.description,
            )
            db.add(feed_entry)

            newly_earned.append({
                "key": defn.key,
                "name": defn.name,
                "description": defn.description,
                "xp_reward": defn.xp_reward,
                "rarity": defn.rarity,
                "icon_name": defn.icon_name,
            })

    if newly_earned:
        await db.flush()

    return newly_earned


async def _check_single_achievement(
    db: AsyncSession, user_id: int, xp: UserXP, defn: AchievementDefinition
) -> bool:
    req = float(defn.requirement_value)
    rtype = defn.requirement_type

    if rtype == "workout_count":
        result = await db.execute(
            select(func.count(WorkoutSession.id)).where(
                WorkoutSession.user_id == user_id,
                WorkoutSession.status == "finished",
            )
        )
        count = result.scalar() or 0
        return count >= req

    elif rtype == "pr_count":
        result = await db.execute(
            select(func.count(PersonalRecord.id)).where(PersonalRecord.user_id == user_id)
        )
        count = result.scalar() or 0
        return count >= req

    elif rtype == "total_volume_kg":
        result = await db.execute(
            select(func.coalesce(func.sum(WorkoutSession.total_volume_kg), 0)).where(
                WorkoutSession.user_id == user_id,
                WorkoutSession.status == "finished",
            )
        )
        total = float(result.scalar() or 0)
        return total >= req

    elif rtype == "streak_days":
        return xp.current_streak_days >= req or xp.longest_streak_days >= req

    elif rtype == "meal_count":
        result = await db.execute(
            select(func.count(MealLog.id)).where(MealLog.user_id == user_id)
        )
        count = result.scalar() or 0
        return count >= req

    elif rtype == "body_metric_count":
        result = await db.execute(
            select(func.count(BodyMetric.id)).where(BodyMetric.user_id == user_id)
        )
        count = result.scalar() or 0
        return count >= req

    elif rtype == "goals_reached":
        result = await db.execute(
            select(func.count(BodyGoal.id)).where(
                BodyGoal.user_id == user_id,
                BodyGoal.status == "completed",
            )
        )
        count = result.scalar() or 0
        return count >= req

    elif rtype == "level":
        return xp.current_level >= req

    # For types we can't yet check dynamically, skip
    return False
