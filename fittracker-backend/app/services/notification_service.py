"""Notification service: create notifications, check user settings."""

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.models.notification import Notification, NotificationSettings


async def _get_settings(db: AsyncSession, user_id: int) -> NotificationSettings | None:
    result = await db.execute(
        select(NotificationSettings).where(NotificationSettings.user_id == user_id)
    )
    return result.scalar_one_or_none()


async def create_notification(
    db: AsyncSession,
    user_id: int,
    notification_type: str,
    title: str,
    body: str,
    action_url: str | None = None,
    related_type: str | None = None,
    related_id: int | None = None,
) -> Notification | None:
    """Create a notification if user settings allow it."""
    settings = await _get_settings(db, user_id)

    # Check per-type setting
    allowed = True
    if settings:
        type_map = {
            "achievement_earned": settings.achievement_alerts,
            "level_up": settings.achievement_alerts,
            "streak_warning": settings.streak_alerts,
            "pr_achieved": settings.achievement_alerts,
            "goal_reached": settings.achievement_alerts,
            "new_follower": settings.social_alerts,
            "feed_like": settings.social_alerts,
            "feed_comment": settings.social_alerts,
            "workout_reminder": settings.workout_reminders,
        }
        allowed = type_map.get(notification_type, True)

    if not allowed:
        return None

    notif = Notification(
        user_id=user_id,
        notification_type=notification_type,
        title=title,
        body=body,
        action_url=action_url,
        related_type=related_type,
        related_id=related_id,
    )
    db.add(notif)
    await db.flush()
    return notif
