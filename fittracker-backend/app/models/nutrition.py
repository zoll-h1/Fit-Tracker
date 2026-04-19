from datetime import datetime, timezone
from typing import Optional

import sqlalchemy as sa
from sqlalchemy.orm import Mapped, mapped_column

from app.database import Base


class Food(Base):
    __tablename__ = "foods"

    id: Mapped[int] = mapped_column(sa.Integer, primary_key=True, index=True)
    name: Mapped[str] = mapped_column(sa.String(200), nullable=False, index=True)
    brand: Mapped[Optional[str]] = mapped_column(sa.String(200))
    barcode: Mapped[Optional[str]] = mapped_column(sa.String(50), unique=True)

    # Per 100g
    calories_per_100g: Mapped[float] = mapped_column(sa.Numeric(7, 2), nullable=False)
    protein_g: Mapped[float] = mapped_column(sa.Numeric(6, 2), default=0, server_default="0")
    carbs_g: Mapped[float] = mapped_column(sa.Numeric(6, 2), default=0, server_default="0")
    fat_g: Mapped[float] = mapped_column(sa.Numeric(6, 2), default=0, server_default="0")
    fiber_g: Mapped[float] = mapped_column(sa.Numeric(6, 2), default=0, server_default="0")
    sugar_g: Mapped[float] = mapped_column(sa.Numeric(6, 2), default=0, server_default="0")
    sodium_mg: Mapped[float] = mapped_column(sa.Numeric(7, 1), default=0, server_default="0")

    is_custom: Mapped[bool] = mapped_column(sa.Boolean, default=False, server_default=sa.false())
    created_by: Mapped[Optional[int]] = mapped_column(
        sa.Integer, sa.ForeignKey("users.id", ondelete="SET NULL")
    )
    created_at: Mapped[datetime] = mapped_column(
        sa.TIMESTAMP(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        server_default=sa.func.now(),
    )


class MealLog(Base):
    __tablename__ = "meal_logs"

    id: Mapped[int] = mapped_column(sa.Integer, primary_key=True, index=True)
    user_id: Mapped[int] = mapped_column(
        sa.Integer, sa.ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True
    )
    food_id: Mapped[int] = mapped_column(
        sa.Integer, sa.ForeignKey("foods.id", ondelete="CASCADE"), nullable=False
    )
    meal_type: Mapped[str] = mapped_column(
        sa.String(20), nullable=False
    )  # breakfast / lunch / dinner / snack
    quantity_g: Mapped[float] = mapped_column(sa.Numeric(7, 1), nullable=False)
    logged_at: Mapped[datetime] = mapped_column(
        sa.TIMESTAMP(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        server_default=sa.func.now(),
        index=True,
    )

    # Computed at log time (so food edits don't retroactively change logs)
    calories: Mapped[float] = mapped_column(sa.Numeric(8, 2), nullable=False)
    protein_g: Mapped[float] = mapped_column(sa.Numeric(6, 2), nullable=False)
    carbs_g: Mapped[float] = mapped_column(sa.Numeric(6, 2), nullable=False)
    fat_g: Mapped[float] = mapped_column(sa.Numeric(6, 2), nullable=False)
    fiber_g: Mapped[float] = mapped_column(sa.Numeric(6, 2), nullable=False)


class NutritionGoal(Base):
    __tablename__ = "nutrition_goals"

    id: Mapped[int] = mapped_column(sa.Integer, primary_key=True)
    user_id: Mapped[int] = mapped_column(
        sa.Integer,
        sa.ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        unique=True,
        index=True,
    )
    calories_target: Mapped[int] = mapped_column(sa.Integer, default=2000, server_default="2000")
    protein_g: Mapped[int] = mapped_column(sa.Integer, default=150, server_default="150")
    carbs_g: Mapped[int] = mapped_column(sa.Integer, default=200, server_default="200")
    fat_g: Mapped[int] = mapped_column(sa.Integer, default=65, server_default="65")
    fiber_g: Mapped[int] = mapped_column(sa.Integer, default=25, server_default="25")
    updated_at: Mapped[datetime] = mapped_column(
        sa.TIMESTAMP(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        server_default=sa.func.now(),
        onupdate=lambda: datetime.now(timezone.utc),
    )
