from datetime import datetime, timezone
from typing import Optional

import sqlalchemy as sa
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


class WorkoutSession(Base):
    __tablename__ = "workout_sessions"

    id: Mapped[int] = mapped_column(sa.Integer, primary_key=True, index=True)
    user_id: Mapped[int] = mapped_column(sa.Integer, sa.ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    template_id: Mapped[Optional[int]] = mapped_column(sa.Integer, sa.ForeignKey("workout_templates.id", ondelete="SET NULL"))
    name: Mapped[str] = mapped_column(sa.String(200), nullable=False, default="Workout")
    notes: Mapped[Optional[str]] = mapped_column(sa.Text)

    started_at: Mapped[datetime] = mapped_column(
        sa.TIMESTAMP(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        server_default=sa.func.now(),
    )
    finished_at: Mapped[Optional[datetime]] = mapped_column(sa.TIMESTAMP(timezone=True))
    duration_seconds: Mapped[Optional[int]] = mapped_column(sa.Integer)

    # Auto-calculated stats
    total_volume_kg: Mapped[float] = mapped_column(sa.Numeric(10, 2), default=0, server_default="0")
    total_sets: Mapped[int] = mapped_column(sa.Integer, default=0, server_default="0")
    total_reps: Mapped[int] = mapped_column(sa.Integer, default=0, server_default="0")
    calories_burned: Mapped[Optional[int]] = mapped_column(sa.Integer)

    status: Mapped[str] = mapped_column(
        sa.String(20), default="in_progress", server_default="in_progress", index=True
    )  # in_progress / completed / cancelled

    # Relationships
    exercises: Mapped[list["WorkoutExercise"]] = relationship(
        "WorkoutExercise",
        back_populates="session",
        cascade="all, delete-orphan",
        order_by="WorkoutExercise.exercise_order",
    )


class WorkoutExercise(Base):
    __tablename__ = "workout_exercises"

    id: Mapped[int] = mapped_column(sa.Integer, primary_key=True, index=True)
    session_id: Mapped[int] = mapped_column(sa.Integer, sa.ForeignKey("workout_sessions.id", ondelete="CASCADE"), nullable=False, index=True)
    exercise_library_id: Mapped[int] = mapped_column(sa.Integer, sa.ForeignKey("exercise_library.id", ondelete="CASCADE"), nullable=False)
    exercise_order: Mapped[int] = mapped_column(sa.Integer, default=1)
    notes: Mapped[Optional[str]] = mapped_column(sa.Text)
    rest_seconds: Mapped[int] = mapped_column(sa.Integer, default=60, server_default="60")

    # Relationships
    session: Mapped["WorkoutSession"] = relationship("WorkoutSession", back_populates="exercises")
    exercise: Mapped["ExerciseLibrary"] = relationship("ExerciseLibrary", back_populates="workout_exercises")
    sets: Mapped[list["WorkoutSet"]] = relationship(
        "WorkoutSet",
        back_populates="workout_exercise",
        cascade="all, delete-orphan",
        order_by="WorkoutSet.set_number",
    )


class WorkoutSet(Base):
    __tablename__ = "workout_sets"

    id: Mapped[int] = mapped_column(sa.Integer, primary_key=True, index=True)
    workout_exercise_id: Mapped[int] = mapped_column(sa.Integer, sa.ForeignKey("workout_exercises.id", ondelete="CASCADE"), nullable=False, index=True)
    set_number: Mapped[int] = mapped_column(sa.Integer, nullable=False)
    set_type: Mapped[str] = mapped_column(sa.String(20), default="normal", server_default="normal")  # normal/warmup/dropset/failure
    reps: Mapped[Optional[int]] = mapped_column(sa.Integer)
    weight_kg: Mapped[Optional[float]] = mapped_column(sa.Numeric(6, 2))
    duration_seconds: Mapped[Optional[int]] = mapped_column(sa.Integer)
    distance_km: Mapped[Optional[float]] = mapped_column(sa.Numeric(6, 3))
    rpe: Mapped[Optional[int]] = mapped_column(sa.Integer)  # 1-10
    completed: Mapped[bool] = mapped_column(sa.Boolean, default=False, server_default=sa.false())
    completed_at: Mapped[Optional[datetime]] = mapped_column(sa.TIMESTAMP(timezone=True))
    is_pr: Mapped[bool] = mapped_column(sa.Boolean, default=False, server_default=sa.false())

    workout_exercise: Mapped["WorkoutExercise"] = relationship("WorkoutExercise", back_populates="sets")


class WorkoutTemplate(Base):
    __tablename__ = "workout_templates"

    id: Mapped[int] = mapped_column(sa.Integer, primary_key=True, index=True)
    user_id: Mapped[int] = mapped_column(sa.Integer, sa.ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    name: Mapped[str] = mapped_column(sa.String(200), nullable=False)
    description: Mapped[Optional[str]] = mapped_column(sa.Text)
    is_public: Mapped[bool] = mapped_column(sa.Boolean, default=False, server_default=sa.false())
    estimated_duration_min: Mapped[Optional[int]] = mapped_column(sa.Integer)
    times_used: Mapped[int] = mapped_column(sa.Integer, default=0, server_default="0")
    last_used_at: Mapped[Optional[datetime]] = mapped_column(sa.TIMESTAMP(timezone=True))
    created_at: Mapped[datetime] = mapped_column(
        sa.TIMESTAMP(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        server_default=sa.func.now(),
    )

    exercises: Mapped[list["TemplateExercise"]] = relationship(
        "TemplateExercise",
        back_populates="template",
        cascade="all, delete-orphan",
        order_by="TemplateExercise.exercise_order",
    )
    sessions: Mapped[list["WorkoutSession"]] = relationship("WorkoutSession", back_populates=None)


class TemplateExercise(Base):
    __tablename__ = "template_exercises"

    id: Mapped[int] = mapped_column(sa.Integer, primary_key=True)
    template_id: Mapped[int] = mapped_column(sa.Integer, sa.ForeignKey("workout_templates.id", ondelete="CASCADE"), nullable=False)
    exercise_library_id: Mapped[int] = mapped_column(sa.Integer, sa.ForeignKey("exercise_library.id", ondelete="CASCADE"), nullable=False)
    exercise_order: Mapped[int] = mapped_column(sa.Integer, default=1)
    target_sets: Mapped[Optional[int]] = mapped_column(sa.Integer)
    target_reps: Mapped[Optional[int]] = mapped_column(sa.Integer)
    target_weight_kg: Mapped[Optional[float]] = mapped_column(sa.Numeric(6, 2))
    rest_seconds: Mapped[int] = mapped_column(sa.Integer, default=60, server_default="60")
    notes: Mapped[Optional[str]] = mapped_column(sa.Text)

    template: Mapped["WorkoutTemplate"] = relationship("WorkoutTemplate", back_populates="exercises")
    exercise: Mapped["ExerciseLibrary"] = relationship("ExerciseLibrary")


# Fix circular import: import ExerciseLibrary here
from app.models.exercise import ExerciseLibrary  # noqa: E402, F401
