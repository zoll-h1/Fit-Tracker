from datetime import date
from sqlalchemy import Integer, String, Boolean, Text, ForeignKey, Numeric, UniqueConstraint, Date
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.database import Base


class UserXP(Base):
    __tablename__ = "user_xp"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    user_id: Mapped[int] = mapped_column(Integer, ForeignKey("users.id", ondelete="CASCADE"), unique=True, nullable=False)

    total_xp: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    current_level: Mapped[int] = mapped_column(Integer, default=1, nullable=False)

    current_streak_days: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    longest_streak_days: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    last_workout_date: Mapped[date | None] = mapped_column(Date, nullable=True)

    weekly_xp: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    monthly_xp: Mapped[int] = mapped_column(Integer, default=0, nullable=False)

    user = relationship("User", back_populates="xp_record", foreign_keys=[user_id])


class AchievementDefinition(Base):
    __tablename__ = "achievement_definitions"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    key: Mapped[str] = mapped_column(String(100), unique=True, nullable=False)
    name: Mapped[str] = mapped_column(String(200), nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=False)
    icon_name: Mapped[str | None] = mapped_column(String(50), nullable=True)

    category: Mapped[str] = mapped_column(String(30), nullable=False)
    # 'workout', 'strength', 'consistency', 'social', 'nutrition', 'body'

    xp_reward: Mapped[int] = mapped_column(Integer, default=50, nullable=False)

    requirement_type: Mapped[str] = mapped_column(String(50), nullable=False)
    # 'workout_count', 'streak_days', 'total_volume_kg', 'pr_count',
    # 'meal_count', 'body_metric_count', 'level'
    requirement_value: Mapped[float] = mapped_column(Numeric(12, 2), nullable=False)

    rarity: Mapped[str] = mapped_column(String(20), default="common", nullable=False)
    # 'common', 'rare', 'epic', 'legendary'

    earned_by = relationship("UserAchievement", back_populates="definition")


class UserAchievement(Base):
    __tablename__ = "user_achievements"
    __table_args__ = (UniqueConstraint("user_id", "achievement_id"),)

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    user_id: Mapped[int] = mapped_column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    achievement_id: Mapped[int] = mapped_column(Integer, ForeignKey("achievement_definitions.id"), nullable=False)
    earned_at: Mapped[str] = mapped_column(String, server_default="now()", nullable=False)
    notified: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)

    user = relationship("User", foreign_keys=[user_id])
    definition = relationship("AchievementDefinition", back_populates="earned_by")
