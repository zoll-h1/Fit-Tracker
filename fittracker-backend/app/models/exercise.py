from datetime import datetime, timezone
from typing import Optional

import sqlalchemy as sa
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


class ExerciseLibrary(Base):
    __tablename__ = "exercise_library"

    id: Mapped[int] = mapped_column(sa.Integer, primary_key=True, index=True)
    name: Mapped[str] = mapped_column(sa.String(200), nullable=False, index=True)
    slug: Mapped[str] = mapped_column(sa.String(200), unique=True, nullable=False)

    # Muscle groups stored as comma-separated strings (compatible without Postgres array extension)
    muscle_primary: Mapped[Optional[str]] = mapped_column(sa.Text)   # e.g. "chest,triceps"
    muscle_secondary: Mapped[Optional[str]] = mapped_column(sa.Text) # e.g. "shoulders"

    equipment: Mapped[Optional[str]] = mapped_column(sa.Text)        # e.g. "barbell,bench"
    force_type: Mapped[Optional[str]] = mapped_column(sa.String(20)) # push/pull/static
    difficulty: Mapped[str] = mapped_column(sa.String(20), default="intermediate", server_default="intermediate")
    category: Mapped[str] = mapped_column(sa.String(20), default="strength", server_default="strength", index=True)

    description: Mapped[Optional[str]] = mapped_column(sa.Text)
    instructions: Mapped[Optional[str]] = mapped_column(sa.Text)
    video_url: Mapped[Optional[str]] = mapped_column(sa.String(500))
    image_url: Mapped[Optional[str]] = mapped_column(sa.String(500))

    is_custom: Mapped[bool] = mapped_column(sa.Boolean, default=False, server_default=sa.false())
    created_by: Mapped[Optional[int]] = mapped_column(sa.Integer, sa.ForeignKey("users.id", ondelete="SET NULL"))
    created_by_user_id: Mapped[Optional[int]] = mapped_column(sa.Integer, sa.ForeignKey("users.id", ondelete="SET NULL"))
    met_value: Mapped[float] = mapped_column(sa.Numeric(4, 1), default=5.0, server_default="5.0")

    created_at: Mapped[datetime] = mapped_column(
        sa.TIMESTAMP(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        server_default=sa.func.now(),
    )

    # Relationships
    workout_exercises: Mapped[list["WorkoutExercise"]] = relationship(
        "WorkoutExercise", back_populates="exercise"
    )


class PersonalRecord(Base):
    __tablename__ = "personal_records"

    id: Mapped[int] = mapped_column(sa.Integer, primary_key=True)
    user_id: Mapped[int] = mapped_column(sa.Integer, sa.ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    exercise_id: Mapped[int] = mapped_column(sa.Integer, sa.ForeignKey("exercise_library.id", ondelete="CASCADE"), nullable=False)
    weight_kg: Mapped[float] = mapped_column(sa.Numeric(6, 2), nullable=False)
    reps: Mapped[int] = mapped_column(sa.Integer, nullable=False)
    achieved_at: Mapped[datetime] = mapped_column(sa.TIMESTAMP(timezone=True), nullable=False)
    workout_set_id: Mapped[Optional[int]] = mapped_column(sa.Integer, sa.ForeignKey("workout_sets.id", ondelete="SET NULL"))

    __table_args__ = (
        sa.UniqueConstraint("user_id", "exercise_id", name="uq_pr_user_exercise"),
    )
