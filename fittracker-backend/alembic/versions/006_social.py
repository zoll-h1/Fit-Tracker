"""social features

Revision ID: 006_social
Revises: 005_notifications
Create Date: 2026-04-19

"""
from alembic import op
import sqlalchemy as sa

revision: str = "006_social"
down_revision: str = "005_notifications"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "user_follows",
        sa.Column("id", sa.Integer, primary_key=True, index=True),
        sa.Column("follower_id", sa.Integer, sa.ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True),
        sa.Column("following_id", sa.Integer, sa.ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True),
        sa.Column("created_at", sa.TIMESTAMP(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.UniqueConstraint("follower_id", "following_id", name="uq_follow"),
    )

    op.create_table(
        "activity_feed",
        sa.Column("id", sa.Integer, primary_key=True, index=True),
        sa.Column("user_id", sa.Integer, sa.ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True),
        sa.Column("activity_type", sa.String(30), nullable=False, index=True),
        sa.Column("ref_id", sa.Integer, nullable=True),
        sa.Column("title", sa.String(200), nullable=False),
        sa.Column("body", sa.Text, nullable=True),
        sa.Column("is_public", sa.Boolean, nullable=False, server_default="true"),
        sa.Column("likes_count", sa.Integer, nullable=False, server_default="0"),
        sa.Column("comments_count", sa.Integer, nullable=False, server_default="0"),
        sa.Column("created_at", sa.TIMESTAMP(timezone=True), server_default=sa.text("now()"), nullable=False),
    )

    op.create_table(
        "feed_likes",
        sa.Column("id", sa.Integer, primary_key=True),
        sa.Column("feed_id", sa.Integer, sa.ForeignKey("activity_feed.id", ondelete="CASCADE"), nullable=False, index=True),
        sa.Column("user_id", sa.Integer, sa.ForeignKey("users.id", ondelete="CASCADE"), nullable=False),
        sa.Column("created_at", sa.TIMESTAMP(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.UniqueConstraint("feed_id", "user_id", name="uq_feed_like"),
    )

    op.create_table(
        "feed_comments",
        sa.Column("id", sa.Integer, primary_key=True, index=True),
        sa.Column("feed_id", sa.Integer, sa.ForeignKey("activity_feed.id", ondelete="CASCADE"), nullable=False, index=True),
        sa.Column("user_id", sa.Integer, sa.ForeignKey("users.id", ondelete="CASCADE"), nullable=False),
        sa.Column("content", sa.Text, nullable=False),
        sa.Column("created_at", sa.TIMESTAMP(timezone=True), server_default=sa.text("now()"), nullable=False),
    )


def downgrade() -> None:
    op.drop_table("feed_comments")
    op.drop_table("feed_likes")
    op.drop_table("activity_feed")
    op.drop_table("user_follows")
