from datetime import datetime, timezone, date
from typing import Optional
import sqlalchemy as sa
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.database import Base


class Challenge(Base):
    __tablename__ = "challenges"
    id: Mapped[int] = mapped_column(sa.Integer, primary_key=True, index=True)
    creator_id: Mapped[int] = mapped_column(sa.Integer, sa.ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    title: Mapped[str] = mapped_column(sa.String(200), nullable=False)
    description: Mapped[Optional[str]] = mapped_column(sa.Text)
    challenge_type: Mapped[str] = mapped_column(sa.String(30), nullable=False)  # total_workouts / total_volume / streak
    target_value: Mapped[float] = mapped_column(sa.Numeric(10, 2), nullable=False)
    start_date: Mapped[date] = mapped_column(sa.Date, nullable=False)
    end_date: Mapped[date] = mapped_column(sa.Date, nullable=False)
    is_public: Mapped[bool] = mapped_column(sa.Boolean, default=True, server_default="1")
    status: Mapped[str] = mapped_column(sa.String(20), default="active", server_default="active", index=True)  # active/completed/cancelled
    winner_user_id: Mapped[Optional[int]] = mapped_column(sa.Integer, sa.ForeignKey("users.id", ondelete="SET NULL"))
    created_at: Mapped[datetime] = mapped_column(sa.TIMESTAMP(timezone=True), default=lambda: datetime.now(timezone.utc), server_default=sa.func.now())

    participants: Mapped[list["ChallengeParticipant"]] = relationship(
        "ChallengeParticipant", back_populates="challenge", cascade="all, delete-orphan"
    )


class ChallengeParticipant(Base):
    __tablename__ = "challenge_participants"
    id: Mapped[int] = mapped_column(sa.Integer, primary_key=True)
    challenge_id: Mapped[int] = mapped_column(sa.Integer, sa.ForeignKey("challenges.id", ondelete="CASCADE"), nullable=False, index=True)
    user_id: Mapped[int] = mapped_column(sa.Integer, sa.ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    current_progress: Mapped[float] = mapped_column(sa.Numeric(10, 2), default=0, server_default="0")
    rank: Mapped[Optional[int]] = mapped_column(sa.Integer)
    joined_at: Mapped[datetime] = mapped_column(sa.TIMESTAMP(timezone=True), default=lambda: datetime.now(timezone.utc), server_default=sa.func.now())
    __table_args__ = (sa.UniqueConstraint("challenge_id", "user_id", name="uq_challenge_participant"),)

    challenge: Mapped["Challenge"] = relationship("Challenge", back_populates="participants")
