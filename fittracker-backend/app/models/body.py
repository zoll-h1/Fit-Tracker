from datetime import datetime, timezone
from typing import Optional

import sqlalchemy as sa
from sqlalchemy.orm import Mapped, mapped_column

from app.database import Base


class BodyMetric(Base):
    __tablename__ = "body_metrics"

    id: Mapped[int] = mapped_column(sa.Integer, primary_key=True, index=True)
    user_id: Mapped[int] = mapped_column(
        sa.Integer, sa.ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True
    )
    weight_kg: Mapped[Optional[float]] = mapped_column(sa.Numeric(6, 2))
    body_fat_pct: Mapped[Optional[float]] = mapped_column(sa.Numeric(5, 2))
    muscle_mass_kg: Mapped[Optional[float]] = mapped_column(sa.Numeric(6, 2))
    bmi: Mapped[Optional[float]] = mapped_column(sa.Numeric(5, 2))
    waist_cm: Mapped[Optional[float]] = mapped_column(sa.Numeric(5, 1))
    chest_cm: Mapped[Optional[float]] = mapped_column(sa.Numeric(5, 1))
    hip_cm: Mapped[Optional[float]] = mapped_column(sa.Numeric(5, 1))
    notes: Mapped[Optional[str]] = mapped_column(sa.Text)
    recorded_at: Mapped[datetime] = mapped_column(
        sa.TIMESTAMP(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        server_default=sa.func.now(),
        index=True,
    )


class BodyGoal(Base):
    __tablename__ = "body_goals"

    id: Mapped[int] = mapped_column(sa.Integer, primary_key=True, index=True)
    user_id: Mapped[int] = mapped_column(
        sa.Integer, sa.ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True
    )
    goal_type: Mapped[str] = mapped_column(sa.String(30), nullable=False)
    # e.g. weight_loss / weight_gain / body_fat / muscle_mass / waist / custom
    target_value: Mapped[float] = mapped_column(sa.Numeric(7, 2), nullable=False)
    start_value: Mapped[Optional[float]] = mapped_column(sa.Numeric(7, 2))
    current_value: Mapped[Optional[float]] = mapped_column(sa.Numeric(7, 2))
    unit: Mapped[str] = mapped_column(sa.String(10), default="kg", server_default="kg")
    deadline: Mapped[Optional[datetime]] = mapped_column(sa.TIMESTAMP(timezone=True))
    status: Mapped[str] = mapped_column(
        sa.String(20), default="active", server_default="active"
    )  # active / completed / cancelled
    completed_at: Mapped[Optional[datetime]] = mapped_column(sa.TIMESTAMP(timezone=True))
    created_at: Mapped[datetime] = mapped_column(
        sa.TIMESTAMP(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        server_default=sa.func.now(),
    )
