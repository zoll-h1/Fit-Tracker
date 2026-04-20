from datetime import datetime, timezone
from typing import Optional
import sqlalchemy as sa
from sqlalchemy.orm import Mapped, mapped_column
from app.database import Base


class UserFollow(Base):
    __tablename__ = "user_follows"
    id: Mapped[int] = mapped_column(sa.Integer, primary_key=True, index=True)
    follower_id: Mapped[int] = mapped_column(sa.Integer, sa.ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    following_id: Mapped[int] = mapped_column(sa.Integer, sa.ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    created_at: Mapped[datetime] = mapped_column(sa.TIMESTAMP(timezone=True), default=lambda: datetime.now(timezone.utc), server_default=sa.func.now())
    __table_args__ = (sa.UniqueConstraint("follower_id", "following_id", name="uq_follow"),)


class ActivityFeed(Base):
    __tablename__ = "activity_feed"
    id: Mapped[int] = mapped_column(sa.Integer, primary_key=True, index=True)
    user_id: Mapped[int] = mapped_column(sa.Integer, sa.ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    activity_type: Mapped[str] = mapped_column(sa.String(30), nullable=False, index=True)
    ref_id: Mapped[Optional[int]] = mapped_column(sa.Integer)
    title: Mapped[str] = mapped_column(sa.String(200), nullable=False)
    body: Mapped[Optional[str]] = mapped_column(sa.Text)
    is_public: Mapped[bool] = mapped_column(sa.Boolean, default=True, server_default="1")
    likes_count: Mapped[int] = mapped_column(sa.Integer, default=0, server_default="0")
    comments_count: Mapped[int] = mapped_column(sa.Integer, default=0, server_default="0")
    created_at: Mapped[datetime] = mapped_column(sa.TIMESTAMP(timezone=True), default=lambda: datetime.now(timezone.utc), server_default=sa.func.now())


class FeedLike(Base):
    __tablename__ = "feed_likes"
    id: Mapped[int] = mapped_column(sa.Integer, primary_key=True)
    feed_id: Mapped[int] = mapped_column(sa.Integer, sa.ForeignKey("activity_feed.id", ondelete="CASCADE"), nullable=False, index=True)
    user_id: Mapped[int] = mapped_column(sa.Integer, sa.ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    created_at: Mapped[datetime] = mapped_column(sa.TIMESTAMP(timezone=True), default=lambda: datetime.now(timezone.utc), server_default=sa.func.now())
    __table_args__ = (sa.UniqueConstraint("feed_id", "user_id", name="uq_feed_like"),)


class FeedComment(Base):
    __tablename__ = "feed_comments"
    id: Mapped[int] = mapped_column(sa.Integer, primary_key=True, index=True)
    feed_id: Mapped[int] = mapped_column(sa.Integer, sa.ForeignKey("activity_feed.id", ondelete="CASCADE"), nullable=False, index=True)
    user_id: Mapped[int] = mapped_column(sa.Integer, sa.ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    content: Mapped[str] = mapped_column(sa.Text, nullable=False)
    created_at: Mapped[datetime] = mapped_column(sa.TIMESTAMP(timezone=True), default=lambda: datetime.now(timezone.utc), server_default=sa.func.now())
