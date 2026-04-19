"""Exercise library, workout sessions, sets, templates, PRs

Revision ID: 002_workouts
Revises: 001_initial
Create Date: 2026-04-19

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "002_workouts"
down_revision: Union[str, None] = "001_initial"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Exercise library
    op.create_table(
        "exercise_library",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("name", sa.String(200), nullable=False),
        sa.Column("slug", sa.String(200), nullable=False),
        sa.Column("muscle_primary", sa.Text(), nullable=True),
        sa.Column("muscle_secondary", sa.Text(), nullable=True),
        sa.Column("equipment", sa.Text(), nullable=True),
        sa.Column("force_type", sa.String(20), nullable=True),
        sa.Column("difficulty", sa.String(20), server_default="intermediate", nullable=False),
        sa.Column("category", sa.String(20), server_default="strength", nullable=False),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("instructions", sa.Text(), nullable=True),
        sa.Column("video_url", sa.String(500), nullable=True),
        sa.Column("image_url", sa.String(500), nullable=True),
        sa.Column("is_custom", sa.Boolean(), server_default=sa.false(), nullable=False),
        sa.Column("created_by", sa.Integer(), nullable=True),
        sa.Column("met_value", sa.Numeric(4, 1), server_default="5.0", nullable=False),
        sa.Column("created_at", sa.TIMESTAMP(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.ForeignKeyConstraint(["created_by"], ["users.id"], ondelete="SET NULL"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("slug"),
    )
    op.create_index("ix_exercise_library_id", "exercise_library", ["id"])
    op.create_index("ix_exercise_library_name", "exercise_library", ["name"])
    op.create_index("ix_exercise_library_category", "exercise_library", ["category"])

    # Workout templates (created before sessions so sessions can FK to it)
    op.create_table(
        "workout_templates",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("user_id", sa.Integer(), nullable=False),
        sa.Column("name", sa.String(200), nullable=False),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("is_public", sa.Boolean(), server_default=sa.false(), nullable=False),
        sa.Column("estimated_duration_min", sa.Integer(), nullable=True),
        sa.Column("times_used", sa.Integer(), server_default="0", nullable=False),
        sa.Column("last_used_at", sa.TIMESTAMP(timezone=True), nullable=True),
        sa.Column("created_at", sa.TIMESTAMP(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_workout_templates_user_id", "workout_templates", ["user_id"])

    # Workout sessions
    op.create_table(
        "workout_sessions",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("user_id", sa.Integer(), nullable=False),
        sa.Column("template_id", sa.Integer(), nullable=True),
        sa.Column("name", sa.String(200), server_default="Workout", nullable=False),
        sa.Column("notes", sa.Text(), nullable=True),
        sa.Column("started_at", sa.TIMESTAMP(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("finished_at", sa.TIMESTAMP(timezone=True), nullable=True),
        sa.Column("duration_seconds", sa.Integer(), nullable=True),
        sa.Column("total_volume_kg", sa.Numeric(10, 2), server_default="0", nullable=False),
        sa.Column("total_sets", sa.Integer(), server_default="0", nullable=False),
        sa.Column("total_reps", sa.Integer(), server_default="0", nullable=False),
        sa.Column("calories_burned", sa.Integer(), nullable=True),
        sa.Column("status", sa.String(20), server_default="in_progress", nullable=False),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["template_id"], ["workout_templates.id"], ondelete="SET NULL"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_workout_sessions_id", "workout_sessions", ["id"])
    op.create_index("ix_workout_sessions_user_id", "workout_sessions", ["user_id"])
    op.create_index("ix_workout_sessions_status", "workout_sessions", ["status"])

    # Workout exercises (exercises within a session)
    op.create_table(
        "workout_exercises",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("session_id", sa.Integer(), nullable=False),
        sa.Column("exercise_library_id", sa.Integer(), nullable=False),
        sa.Column("exercise_order", sa.Integer(), server_default="1", nullable=False),
        sa.Column("notes", sa.Text(), nullable=True),
        sa.Column("rest_seconds", sa.Integer(), server_default="60", nullable=False),
        sa.ForeignKeyConstraint(["session_id"], ["workout_sessions.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["exercise_library_id"], ["exercise_library.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_workout_exercises_id", "workout_exercises", ["id"])
    op.create_index("ix_workout_exercises_session_id", "workout_exercises", ["session_id"])

    # Workout sets
    op.create_table(
        "workout_sets",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("workout_exercise_id", sa.Integer(), nullable=False),
        sa.Column("set_number", sa.Integer(), nullable=False),
        sa.Column("set_type", sa.String(20), server_default="normal", nullable=False),
        sa.Column("reps", sa.Integer(), nullable=True),
        sa.Column("weight_kg", sa.Numeric(6, 2), nullable=True),
        sa.Column("duration_seconds", sa.Integer(), nullable=True),
        sa.Column("distance_km", sa.Numeric(6, 3), nullable=True),
        sa.Column("rpe", sa.Integer(), nullable=True),
        sa.Column("completed", sa.Boolean(), server_default=sa.false(), nullable=False),
        sa.Column("completed_at", sa.TIMESTAMP(timezone=True), nullable=True),
        sa.Column("is_pr", sa.Boolean(), server_default=sa.false(), nullable=False),
        sa.ForeignKeyConstraint(["workout_exercise_id"], ["workout_exercises.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_workout_sets_id", "workout_sets", ["id"])
    op.create_index("ix_workout_sets_workout_exercise_id", "workout_sets", ["workout_exercise_id"])

    # Template exercises
    op.create_table(
        "template_exercises",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("template_id", sa.Integer(), nullable=False),
        sa.Column("exercise_library_id", sa.Integer(), nullable=False),
        sa.Column("exercise_order", sa.Integer(), server_default="1", nullable=False),
        sa.Column("target_sets", sa.Integer(), nullable=True),
        sa.Column("target_reps", sa.Integer(), nullable=True),
        sa.Column("target_weight_kg", sa.Numeric(6, 2), nullable=True),
        sa.Column("rest_seconds", sa.Integer(), server_default="60", nullable=False),
        sa.Column("notes", sa.Text(), nullable=True),
        sa.ForeignKeyConstraint(["template_id"], ["workout_templates.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["exercise_library_id"], ["exercise_library.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )

    # Personal records
    op.create_table(
        "personal_records",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("user_id", sa.Integer(), nullable=False),
        sa.Column("exercise_id", sa.Integer(), nullable=False),
        sa.Column("weight_kg", sa.Numeric(6, 2), nullable=False),
        sa.Column("reps", sa.Integer(), nullable=False),
        sa.Column("achieved_at", sa.TIMESTAMP(timezone=True), nullable=False),
        sa.Column("workout_set_id", sa.Integer(), nullable=True),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["exercise_id"], ["exercise_library.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["workout_set_id"], ["workout_sets.id"], ondelete="SET NULL"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("user_id", "exercise_id", name="uq_pr_user_exercise"),
    )


def downgrade() -> None:
    op.drop_table("personal_records")
    op.drop_table("template_exercises")
    op.drop_index("ix_workout_sets_workout_exercise_id", "workout_sets")
    op.drop_index("ix_workout_sets_id", "workout_sets")
    op.drop_table("workout_sets")
    op.drop_index("ix_workout_exercises_session_id", "workout_exercises")
    op.drop_index("ix_workout_exercises_id", "workout_exercises")
    op.drop_table("workout_exercises")
    op.drop_index("ix_workout_sessions_status", "workout_sessions")
    op.drop_index("ix_workout_sessions_user_id", "workout_sessions")
    op.drop_index("ix_workout_sessions_id", "workout_sessions")
    op.drop_table("workout_sessions")
    op.drop_index("ix_workout_templates_user_id", "workout_templates")
    op.drop_table("workout_templates")
    op.drop_index("ix_exercise_library_category", "exercise_library")
    op.drop_index("ix_exercise_library_name", "exercise_library")
    op.drop_index("ix_exercise_library_id", "exercise_library")
    op.drop_table("exercise_library")
