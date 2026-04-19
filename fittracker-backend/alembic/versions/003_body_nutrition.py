"""Body metrics, goals, foods, meal logs, nutrition goals

Revision ID: 003_body_nutrition
Revises: 002_workouts
Create Date: 2026-04-19

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "003_body_nutrition"
down_revision: Union[str, None] = "002_workouts"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Body metrics
    op.create_table(
        "body_metrics",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("user_id", sa.Integer(), nullable=False),
        sa.Column("weight_kg", sa.Numeric(6, 2), nullable=True),
        sa.Column("body_fat_pct", sa.Numeric(5, 2), nullable=True),
        sa.Column("muscle_mass_kg", sa.Numeric(6, 2), nullable=True),
        sa.Column("bmi", sa.Numeric(5, 2), nullable=True),
        sa.Column("waist_cm", sa.Numeric(5, 1), nullable=True),
        sa.Column("chest_cm", sa.Numeric(5, 1), nullable=True),
        sa.Column("hip_cm", sa.Numeric(5, 1), nullable=True),
        sa.Column("notes", sa.Text(), nullable=True),
        sa.Column("recorded_at", sa.TIMESTAMP(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_body_metrics_id", "body_metrics", ["id"])
    op.create_index("ix_body_metrics_user_id", "body_metrics", ["user_id"])
    op.create_index("ix_body_metrics_recorded_at", "body_metrics", ["recorded_at"])

    # Body goals
    op.create_table(
        "body_goals",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("user_id", sa.Integer(), nullable=False),
        sa.Column("goal_type", sa.String(30), nullable=False),
        sa.Column("target_value", sa.Numeric(7, 2), nullable=False),
        sa.Column("start_value", sa.Numeric(7, 2), nullable=True),
        sa.Column("current_value", sa.Numeric(7, 2), nullable=True),
        sa.Column("unit", sa.String(10), server_default="kg", nullable=False),
        sa.Column("deadline", sa.TIMESTAMP(timezone=True), nullable=True),
        sa.Column("status", sa.String(20), server_default="active", nullable=False),
        sa.Column("completed_at", sa.TIMESTAMP(timezone=True), nullable=True),
        sa.Column("created_at", sa.TIMESTAMP(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_body_goals_id", "body_goals", ["id"])
    op.create_index("ix_body_goals_user_id", "body_goals", ["user_id"])

    # Foods
    op.create_table(
        "foods",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("name", sa.String(200), nullable=False),
        sa.Column("brand", sa.String(200), nullable=True),
        sa.Column("barcode", sa.String(50), nullable=True),
        sa.Column("calories_per_100g", sa.Numeric(7, 2), nullable=False),
        sa.Column("protein_g", sa.Numeric(6, 2), server_default="0", nullable=False),
        sa.Column("carbs_g", sa.Numeric(6, 2), server_default="0", nullable=False),
        sa.Column("fat_g", sa.Numeric(6, 2), server_default="0", nullable=False),
        sa.Column("fiber_g", sa.Numeric(6, 2), server_default="0", nullable=False),
        sa.Column("sugar_g", sa.Numeric(6, 2), server_default="0", nullable=False),
        sa.Column("sodium_mg", sa.Numeric(7, 1), server_default="0", nullable=False),
        sa.Column("is_custom", sa.Boolean(), server_default=sa.false(), nullable=False),
        sa.Column("created_by", sa.Integer(), nullable=True),
        sa.Column("created_at", sa.TIMESTAMP(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.ForeignKeyConstraint(["created_by"], ["users.id"], ondelete="SET NULL"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("barcode"),
    )
    op.create_index("ix_foods_id", "foods", ["id"])
    op.create_index("ix_foods_name", "foods", ["name"])

    # Meal logs
    op.create_table(
        "meal_logs",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("user_id", sa.Integer(), nullable=False),
        sa.Column("food_id", sa.Integer(), nullable=False),
        sa.Column("meal_type", sa.String(20), nullable=False),
        sa.Column("quantity_g", sa.Numeric(7, 1), nullable=False),
        sa.Column("logged_at", sa.TIMESTAMP(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("calories", sa.Numeric(8, 2), nullable=False),
        sa.Column("protein_g", sa.Numeric(6, 2), nullable=False),
        sa.Column("carbs_g", sa.Numeric(6, 2), nullable=False),
        sa.Column("fat_g", sa.Numeric(6, 2), nullable=False),
        sa.Column("fiber_g", sa.Numeric(6, 2), nullable=False),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["food_id"], ["foods.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_meal_logs_id", "meal_logs", ["id"])
    op.create_index("ix_meal_logs_user_id", "meal_logs", ["user_id"])
    op.create_index("ix_meal_logs_logged_at", "meal_logs", ["logged_at"])

    # Nutrition goals (one per user)
    op.create_table(
        "nutrition_goals",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("user_id", sa.Integer(), nullable=False),
        sa.Column("calories_target", sa.Integer(), server_default="2000", nullable=False),
        sa.Column("protein_g", sa.Integer(), server_default="150", nullable=False),
        sa.Column("carbs_g", sa.Integer(), server_default="200", nullable=False),
        sa.Column("fat_g", sa.Integer(), server_default="65", nullable=False),
        sa.Column("fiber_g", sa.Integer(), server_default="25", nullable=False),
        sa.Column("updated_at", sa.TIMESTAMP(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("user_id"),
    )
    op.create_index("ix_nutrition_goals_user_id", "nutrition_goals", ["user_id"])


def downgrade() -> None:
    op.drop_index("ix_nutrition_goals_user_id", "nutrition_goals")
    op.drop_table("nutrition_goals")
    op.drop_index("ix_meal_logs_logged_at", "meal_logs")
    op.drop_index("ix_meal_logs_user_id", "meal_logs")
    op.drop_index("ix_meal_logs_id", "meal_logs")
    op.drop_table("meal_logs")
    op.drop_index("ix_foods_name", "foods")
    op.drop_index("ix_foods_id", "foods")
    op.drop_table("foods")
    op.drop_index("ix_body_goals_user_id", "body_goals")
    op.drop_index("ix_body_goals_id", "body_goals")
    op.drop_table("body_goals")
    op.drop_index("ix_body_metrics_recorded_at", "body_metrics")
    op.drop_index("ix_body_metrics_user_id", "body_metrics")
    op.drop_index("ix_body_metrics_id", "body_metrics")
    op.drop_table("body_metrics")
