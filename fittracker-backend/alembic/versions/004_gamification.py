"""Gamification: user_xp, achievement_definitions, user_achievements

Revision ID: 004_gamification
Revises: 003_body_nutrition
Create Date: 2026-04-19

"""
from alembic import op
import sqlalchemy as sa

revision: str = "004_gamification"
down_revision: str = "003_body_nutrition"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "user_xp",
        sa.Column("id", sa.Integer, primary_key=True),
        sa.Column("user_id", sa.Integer, sa.ForeignKey("users.id", ondelete="CASCADE"), unique=True, nullable=False),
        sa.Column("total_xp", sa.Integer, nullable=False, server_default="0"),
        sa.Column("current_level", sa.Integer, nullable=False, server_default="1"),
        sa.Column("current_streak_days", sa.Integer, nullable=False, server_default="0"),
        sa.Column("longest_streak_days", sa.Integer, nullable=False, server_default="0"),
        sa.Column("last_workout_date", sa.Date, nullable=True),
        sa.Column("weekly_xp", sa.Integer, nullable=False, server_default="0"),
        sa.Column("monthly_xp", sa.Integer, nullable=False, server_default="0"),
        sa.Column("updated_at", sa.TIMESTAMP(timezone=True), server_default=sa.text("now()"), nullable=False),
    )

    op.create_table(
        "achievement_definitions",
        sa.Column("id", sa.Integer, primary_key=True),
        sa.Column("key", sa.String(100), unique=True, nullable=False),
        sa.Column("name", sa.String(200), nullable=False),
        sa.Column("description", sa.Text, nullable=False),
        sa.Column("icon_name", sa.String(50), nullable=True),
        sa.Column("category", sa.String(30), nullable=False),
        sa.Column("xp_reward", sa.Integer, nullable=False, server_default="50"),
        sa.Column("requirement_type", sa.String(50), nullable=False),
        sa.Column("requirement_value", sa.Numeric(12, 2), nullable=False),
        sa.Column("rarity", sa.String(20), nullable=False, server_default="common"),
    )

    op.create_table(
        "user_achievements",
        sa.Column("id", sa.Integer, primary_key=True),
        sa.Column("user_id", sa.Integer, sa.ForeignKey("users.id", ondelete="CASCADE"), nullable=False),
        sa.Column("achievement_id", sa.Integer, sa.ForeignKey("achievement_definitions.id"), nullable=False),
        sa.Column("earned_at", sa.TIMESTAMP(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("notified", sa.Boolean, nullable=False, server_default="false"),
        sa.UniqueConstraint("user_id", "achievement_id", name="uq_user_achievement"),
    )
    op.create_index("idx_user_achievements_user", "user_achievements", ["user_id"])


def downgrade() -> None:
    op.drop_table("user_achievements")
    op.drop_table("achievement_definitions")
    op.drop_table("user_xp")
