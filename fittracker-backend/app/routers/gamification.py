from fastapi import APIRouter, Depends
from sqlalchemy import select, func, desc
from sqlalchemy.ext.asyncio import AsyncSession
from pydantic import BaseModel

from app.database import get_db
from app.dependencies import get_current_active_user
from app.models.gamification import UserXP, AchievementDefinition, UserAchievement
from app.models.user import User
from app.services.gamification_service import (
    _get_or_create_xp, LEVEL_THRESHOLDS, LEVEL_NAMES, xp_to_level
)

router = APIRouter(prefix="/api/gamification", tags=["gamification"])


# ── Schemas ───────────────────────────────────────────────────────────────────
class LevelInfo(BaseModel):
    level: int
    name: str
    xp_required: int
    next_level_xp: int | None


class GamificationProfile(BaseModel):
    total_xp: int
    current_level: int
    level_name: str
    xp_in_level: int
    xp_for_next: int | None
    xp_pct: float
    current_streak_days: int
    longest_streak_days: int
    weekly_xp: int
    monthly_xp: int


class AchievementOut(BaseModel):
    id: int
    key: str
    name: str
    description: str
    icon_name: str | None
    category: str
    xp_reward: int
    requirement_type: str
    requirement_value: float
    rarity: str
    earned: bool
    earned_at: str | None = None


class LeaderboardEntry(BaseModel):
    rank: int
    user_id: int
    username: str
    total_xp: int
    current_level: int
    level_name: str


class StreakInfo(BaseModel):
    current_streak: int
    longest_streak: int
    last_workout_date: str | None


# ── Endpoints ─────────────────────────────────────────────────────────────────

@router.get("/profile", response_model=GamificationProfile)
async def get_profile(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    xp = await _get_or_create_xp(db, current_user.id)
    await db.commit()

    level = xp.current_level
    level_xp = LEVEL_THRESHOLDS.get(level, 0)
    next_level = level + 1 if level < 10 else None
    next_xp = LEVEL_THRESHOLDS.get(next_level) if next_level else None

    xp_in_level = xp.total_xp - level_xp
    xp_for_next_span = (next_xp - level_xp) if next_xp else None
    pct = round((xp_in_level / xp_for_next_span) * 100, 1) if xp_for_next_span else 100.0

    return GamificationProfile(
        total_xp=xp.total_xp,
        current_level=level,
        level_name=LEVEL_NAMES.get(level, "Beginner"),
        xp_in_level=xp_in_level,
        xp_for_next=xp_for_next_span,
        xp_pct=min(pct, 100.0),
        current_streak_days=xp.current_streak_days,
        longest_streak_days=xp.longest_streak_days,
        weekly_xp=xp.weekly_xp,
        monthly_xp=xp.monthly_xp,
    )


@router.get("/achievements", response_model=list[AchievementOut])
async def list_all_achievements(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    defs_result = await db.execute(select(AchievementDefinition).order_by(AchievementDefinition.category, AchievementDefinition.xp_reward))
    all_defs = defs_result.scalars().all()

    earned_result = await db.execute(
        select(UserAchievement).where(UserAchievement.user_id == current_user.id)
    )
    earned_map = {ua.achievement_id: ua.earned_at for ua in earned_result.scalars().all()}

    return [
        AchievementOut(
            id=d.id,
            key=d.key,
            name=d.name,
            description=d.description,
            icon_name=d.icon_name,
            category=d.category,
            xp_reward=d.xp_reward,
            requirement_type=d.requirement_type,
            requirement_value=float(d.requirement_value),
            rarity=d.rarity,
            earned=d.id in earned_map,
            earned_at=str(earned_map[d.id]) if d.id in earned_map else None,
        )
        for d in all_defs
    ]


@router.get("/achievements/my", response_model=list[AchievementOut])
async def my_achievements(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    result = await db.execute(
        select(UserAchievement, AchievementDefinition)
        .join(AchievementDefinition, UserAchievement.achievement_id == AchievementDefinition.id)
        .where(UserAchievement.user_id == current_user.id)
        .order_by(UserAchievement.earned_at.desc())
    )
    rows = result.all()
    return [
        AchievementOut(
            id=defn.id,
            key=defn.key,
            name=defn.name,
            description=defn.description,
            icon_name=defn.icon_name,
            category=defn.category,
            xp_reward=defn.xp_reward,
            requirement_type=defn.requirement_type,
            requirement_value=float(defn.requirement_value),
            rarity=defn.rarity,
            earned=True,
            earned_at=str(ua.earned_at),
        )
        for ua, defn in rows
    ]


@router.get("/leaderboard", response_model=list[LeaderboardEntry])
async def leaderboard(
    limit: int = 20,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    result = await db.execute(
        select(UserXP, User.username)
        .join(User, UserXP.user_id == User.id)
        .order_by(desc(UserXP.total_xp))
        .limit(limit)
    )
    rows = result.all()
    return [
        LeaderboardEntry(
            rank=i + 1,
            user_id=xp.user_id,
            username=username,
            total_xp=xp.total_xp,
            current_level=xp.current_level,
            level_name=LEVEL_NAMES.get(xp.current_level, "Beginner"),
        )
        for i, (xp, username) in enumerate(rows)
    ]


@router.get("/streaks", response_model=StreakInfo)
async def get_streaks(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    xp = await _get_or_create_xp(db, current_user.id)
    await db.commit()
    return StreakInfo(
        current_streak=xp.current_streak_days,
        longest_streak=xp.longest_streak_days,
        last_workout_date=str(xp.last_workout_date) if xp.last_workout_date else None,
    )
