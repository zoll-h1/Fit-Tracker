from datetime import datetime, timezone
from typing import Optional

import sqlalchemy as sa
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(sa.Integer, primary_key=True, index=True)
    username: Mapped[str] = mapped_column(sa.String(50), unique=True, nullable=False, index=True)
    email: Mapped[str] = mapped_column(sa.String(255), unique=True, nullable=False, index=True)
    password_hash: Mapped[str] = mapped_column(sa.String(255), nullable=False)
    full_name: Mapped[Optional[str]] = mapped_column(sa.String(200))

    # Profile
    date_of_birth: Mapped[Optional[datetime]] = mapped_column(sa.Date)
    gender: Mapped[Optional[str]] = mapped_column(sa.String(10))
    bio: Mapped[Optional[str]] = mapped_column(sa.Text)
    avatar_url: Mapped[Optional[str]] = mapped_column(sa.String(500))

    # Physical
    height_cm: Mapped[Optional[float]] = mapped_column(sa.Numeric(5, 1))
    weight_kg: Mapped[Optional[float]] = mapped_column(sa.Numeric(6, 2))

    # Preferences
    unit_system: Mapped[str] = mapped_column(sa.String(10), default="metric", server_default="metric")
    timezone: Mapped[str] = mapped_column(sa.String(50), default="UTC", server_default="UTC")
    language: Mapped[str] = mapped_column(sa.String(10), default="en", server_default="en")

    # Access
    role: Mapped[str] = mapped_column(sa.String(20), default="user", server_default="user", index=True)
    is_active: Mapped[bool] = mapped_column(sa.Boolean, default=True, server_default=sa.true())
    is_email_verified: Mapped[bool] = mapped_column(sa.Boolean, default=False, server_default=sa.false())

    # Timestamps
    created_at: Mapped[datetime] = mapped_column(
        sa.TIMESTAMP(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        server_default=sa.func.now(),
    )
    updated_at: Mapped[datetime] = mapped_column(
        sa.TIMESTAMP(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        server_default=sa.func.now(),
        onupdate=lambda: datetime.now(timezone.utc),
    )
    last_active_at: Mapped[datetime] = mapped_column(
        sa.TIMESTAMP(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        server_default=sa.func.now(),
    )

    # Relationships
    refresh_tokens: Mapped[list["RefreshToken"]] = relationship(
        "RefreshToken", back_populates="user", cascade="all, delete-orphan"
    )
    user_tokens: Mapped[list["UserToken"]] = relationship(
        "UserToken", back_populates="user", cascade="all, delete-orphan"
    )
    xp_record: Mapped["UserXP | None"] = relationship(  # type: ignore[name-defined]
        "UserXP", back_populates="user", uselist=False, cascade="all, delete-orphan"
    )


class RefreshToken(Base):
    __tablename__ = "refresh_tokens"

    id: Mapped[int] = mapped_column(sa.Integer, primary_key=True)
    user_id: Mapped[int] = mapped_column(sa.Integer, sa.ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    token_hash: Mapped[str] = mapped_column(sa.String(255), nullable=False, index=True)
    expires_at: Mapped[datetime] = mapped_column(sa.TIMESTAMP(timezone=True), nullable=False)
    is_revoked: Mapped[bool] = mapped_column(sa.Boolean, default=False, server_default=sa.false())
    created_at: Mapped[datetime] = mapped_column(
        sa.TIMESTAMP(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        server_default=sa.func.now(),
    )
    device_info: Mapped[Optional[str]] = mapped_column(sa.Text)

    user: Mapped["User"] = relationship("User", back_populates="refresh_tokens")


class UserToken(Base):
    __tablename__ = "user_tokens"

    id: Mapped[int] = mapped_column(sa.Integer, primary_key=True)
    user_id: Mapped[int] = mapped_column(sa.Integer, sa.ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    token_type: Mapped[str] = mapped_column(sa.String(30), nullable=False)
    token_hash: Mapped[str] = mapped_column(sa.String(255), nullable=False)
    expires_at: Mapped[datetime] = mapped_column(sa.TIMESTAMP(timezone=True), nullable=False)
    is_used: Mapped[bool] = mapped_column(sa.Boolean, default=False, server_default=sa.false())
    created_at: Mapped[datetime] = mapped_column(
        sa.TIMESTAMP(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        server_default=sa.func.now(),
    )

    user: Mapped["User"] = relationship("User", back_populates="user_tokens")
