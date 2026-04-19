from datetime import datetime
from typing import Optional
import sqlalchemy as sa
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.database import Base
from app.models.user import User  # noqa: F401
from app.models.exercise import ExerciseLibrary  # noqa: F401


class WorkoutProgram(Base):
    __tablename__ = "workout_programs"
    id: Mapped[int] = mapped_column(sa.Integer, primary_key=True, index=True)
    trainer_id: Mapped[int] = mapped_column(sa.Integer, sa.ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    title: Mapped[str] = mapped_column(sa.String(200), nullable=False)
    description: Mapped[Optional[str]] = mapped_column(sa.Text)
    duration_weeks: Mapped[int] = mapped_column(sa.Integer, default=4)
    difficulty: Mapped[str] = mapped_column(sa.String(20), default="intermediate")  # beginner/intermediate/advanced
    is_public: Mapped[bool] = mapped_column(sa.Boolean, default=False, server_default="0")
    created_at: Mapped[datetime] = mapped_column(sa.TIMESTAMP(timezone=True), server_default=sa.func.now())

    trainer: Mapped["User"] = relationship("User", foreign_keys=[trainer_id])
    days: Mapped[list["ProgramDay"]] = relationship("ProgramDay", back_populates="program", cascade="all, delete-orphan", order_by="ProgramDay.week_number, ProgramDay.day_number")
    assignments: Mapped[list["ProgramAssignment"]] = relationship("ProgramAssignment", back_populates="program", cascade="all, delete-orphan")


class ProgramDay(Base):
    __tablename__ = "program_days"
    id: Mapped[int] = mapped_column(sa.Integer, primary_key=True, index=True)
    program_id: Mapped[int] = mapped_column(sa.Integer, sa.ForeignKey("workout_programs.id", ondelete="CASCADE"), nullable=False, index=True)
    week_number: Mapped[int] = mapped_column(sa.Integer, nullable=False)  # 1-based
    day_number: Mapped[int] = mapped_column(sa.Integer, nullable=False)   # 1 = Monday, 7 = Sunday
    name: Mapped[Optional[str]] = mapped_column(sa.String(200))
    exercises: Mapped[list["ProgramExercise"]] = relationship("ProgramExercise", back_populates="day", cascade="all, delete-orphan", order_by="ProgramExercise.exercise_order")
    program: Mapped["WorkoutProgram"] = relationship("WorkoutProgram", back_populates="days")


class ProgramExercise(Base):
    __tablename__ = "program_exercises"
    id: Mapped[int] = mapped_column(sa.Integer, primary_key=True, index=True)
    day_id: Mapped[int] = mapped_column(sa.Integer, sa.ForeignKey("program_days.id", ondelete="CASCADE"), nullable=False)
    exercise_id: Mapped[int] = mapped_column(sa.Integer, sa.ForeignKey("exercise_library.id", ondelete="CASCADE"), nullable=False)
    exercise_order: Mapped[int] = mapped_column(sa.Integer, default=1)
    sets: Mapped[int] = mapped_column(sa.Integer, default=3)
    reps: Mapped[Optional[str]] = mapped_column(sa.String(50))  # "8-12" or "10"
    weight_note: Mapped[Optional[str]] = mapped_column(sa.String(100))  # "RPE 7" or "70% 1RM"
    rest_seconds: Mapped[int] = mapped_column(sa.Integer, default=90)
    exercise: Mapped["ExerciseLibrary"] = relationship("ExerciseLibrary")
    day: Mapped["ProgramDay"] = relationship("ProgramDay", back_populates="exercises")


class ProgramAssignment(Base):
    __tablename__ = "program_assignments"
    id: Mapped[int] = mapped_column(sa.Integer, primary_key=True, index=True)
    program_id: Mapped[int] = mapped_column(sa.Integer, sa.ForeignKey("workout_programs.id", ondelete="CASCADE"), nullable=False)
    client_id: Mapped[int] = mapped_column(sa.Integer, sa.ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    trainer_id: Mapped[int] = mapped_column(sa.Integer, sa.ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    assigned_at: Mapped[datetime] = mapped_column(sa.TIMESTAMP(timezone=True), server_default=sa.func.now())
    start_date: Mapped[Optional[datetime]] = mapped_column(sa.TIMESTAMP(timezone=True))
    status: Mapped[str] = mapped_column(sa.String(20), default="active")  # active/completed/cancelled
    program: Mapped["WorkoutProgram"] = relationship("WorkoutProgram", back_populates="assignments")
    client: Mapped["User"] = relationship("User", foreign_keys=[client_id])
    trainer: Mapped["User"] = relationship("User", foreign_keys=[trainer_id])
