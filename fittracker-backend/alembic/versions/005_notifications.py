"""Notifications: notifications, notification_settings

Revision ID: 005_notifications
Revises: 004_gamification
Create Date: 2026-04-19

"""
from alembic import op
import sqlalchemy as sa

revision: str = "005_notifications"
down_revision: str = "004_gamification"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "notifications",
        sa.Column("id", sa.Integer, primary_key=True),
        sa.Column("user_id", sa.Integer, sa.ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True),
        sa.Column("notification_type", sa.String(50), nullable=False),
        sa.Column("title", sa.String(200), nullable=False),
        sa.Column("body", sa.Text, nullable=False),
        sa.Column("is_read", sa.Boolean, nullable=False, server_default="false"),
        sa.Column("action_url", sa.String(200), nullable=True),
        sa.Column("related_type", sa.String(30), nullable=True),
        sa.Column("related_id", sa.Integer, nullable=True),
        sa.Column("created_at", sa.TIMESTAMP(timezone=True), server_default=sa.text("now()"), nullable=False),
    )
    op.create_index("idx_notifications_user", "notifications", ["user_id", "is_read"])

    op.create_table(
        "notification_settings",
        sa.Column("user_id", sa.Integer, sa.ForeignKey("users.id", ondelete="CASCADE"), primary_key=True),
        sa.Column("workout_reminders", sa.Boolean, nullable=False, server_default="true"),
        sa.Column("streak_alerts", sa.Boolean, nullable=False, server_default="true"),
        sa.Column("achievement_alerts", sa.Boolean, nullable=False, server_default="true"),
        sa.Column("social_alerts", sa.Boolean, nullable=False, server_default="true"),
        sa.Column("challenge_alerts", sa.Boolean, nullable=False, server_default="true"),
        sa.Column("email_notifications", sa.Boolean, nullable=False, server_default="false"),
    )


def downgrade() -> None:
    op.drop_table("notification_settings")
    op.drop_table("notifications")
