"""challenges

Revision ID: 007_challenges
Revises: 006_social
Create Date: 2026-04-26

"""
from alembic import op
import sqlalchemy as sa

revision: str = "007_challenges"
down_revision: str = "006_social"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "challenges",
        sa.Column("id", sa.Integer, primary_key=True, index=True),
        sa.Column("creator_id", sa.Integer, sa.ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True),
        sa.Column("title", sa.String(200), nullable=False),
        sa.Column("description", sa.Text, nullable=True),
        sa.Column("challenge_type", sa.String(30), nullable=False),
        sa.Column("target_value", sa.Numeric(10, 2), nullable=False),
        sa.Column("start_date", sa.Date, nullable=False),
        sa.Column("end_date", sa.Date, nullable=False),
        sa.Column("is_public", sa.Boolean, nullable=False, server_default="1"),
        sa.Column("status", sa.String(20), nullable=False, server_default="active", index=True),
        sa.Column("winner_user_id", sa.Integer, sa.ForeignKey("users.id", ondelete="SET NULL"), nullable=True),
        sa.Column("created_at", sa.TIMESTAMP(timezone=True), server_default=sa.text("now()"), nullable=False),
    )

    op.create_table(
        "challenge_participants",
        sa.Column("id", sa.Integer, primary_key=True),
        sa.Column("challenge_id", sa.Integer, sa.ForeignKey("challenges.id", ondelete="CASCADE"), nullable=False, index=True),
        sa.Column("user_id", sa.Integer, sa.ForeignKey("users.id", ondelete="CASCADE"), nullable=False),
        sa.Column("current_progress", sa.Numeric(10, 2), nullable=False, server_default="0"),
        sa.Column("rank", sa.Integer, nullable=True),
        sa.Column("joined_at", sa.TIMESTAMP(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.UniqueConstraint("challenge_id", "user_id", name="uq_challenge_participant"),
    )


def downgrade() -> None:
    op.drop_table("challenge_participants")
    op.drop_table("challenges")
