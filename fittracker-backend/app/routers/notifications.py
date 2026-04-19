from fastapi import APIRouter, Depends, Query
from sqlalchemy import select, func, update
from sqlalchemy.ext.asyncio import AsyncSession
from pydantic import BaseModel

from app.database import get_db
from app.dependencies import get_current_active_user
from app.models.notification import Notification, NotificationSettings
from app.models.user import User

router = APIRouter(prefix="/api/notifications", tags=["notifications"])


# ── Schemas ───────────────────────────────────────────────────────────────────
class NotificationOut(BaseModel):
    id: int
    notification_type: str
    title: str
    body: str
    is_read: bool
    action_url: str | None
    created_at: str

    class Config:
        from_attributes = True


class NotificationSettingsOut(BaseModel):
    workout_reminders: bool
    streak_alerts: bool
    achievement_alerts: bool
    social_alerts: bool
    challenge_alerts: bool
    email_notifications: bool


class NotificationSettingsUpdate(BaseModel):
    workout_reminders: bool | None = None
    streak_alerts: bool | None = None
    achievement_alerts: bool | None = None
    social_alerts: bool | None = None
    challenge_alerts: bool | None = None
    email_notifications: bool | None = None


class UnreadCount(BaseModel):
    count: int


# ── Endpoints ─────────────────────────────────────────────────────────────────

@router.get("", response_model=list[NotificationOut])
async def list_notifications(
    unread_only: bool = Query(False),
    page: int = Query(1, ge=1),
    per_page: int = Query(20, ge=1, le=100),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    q = select(Notification).where(Notification.user_id == current_user.id)
    if unread_only:
        q = q.where(Notification.is_read == False)
    q = q.order_by(Notification.created_at.desc()).offset((page - 1) * per_page).limit(per_page)
    result = await db.execute(q)
    notifs = result.scalars().all()
    return [NotificationOut(
        id=n.id,
        notification_type=n.notification_type,
        title=n.title,
        body=n.body,
        is_read=n.is_read,
        action_url=n.action_url,
        created_at=str(n.created_at),
    ) for n in notifs]


@router.get("/unread-count", response_model=UnreadCount)
async def unread_count(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    result = await db.execute(
        select(func.count(Notification.id)).where(
            Notification.user_id == current_user.id,
            Notification.is_read == False,
        )
    )
    return UnreadCount(count=result.scalar() or 0)


@router.put("/{notif_id}/read", response_model=NotificationOut)
async def mark_read(
    notif_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    result = await db.execute(
        select(Notification).where(Notification.id == notif_id, Notification.user_id == current_user.id)
    )
    notif = result.scalar_one_or_none()
    if not notif:
        from fastapi import HTTPException
        raise HTTPException(404, "Notification not found")
    notif.is_read = True
    await db.commit()
    return NotificationOut(
        id=notif.id, notification_type=notif.notification_type,
        title=notif.title, body=notif.body, is_read=notif.is_read,
        action_url=notif.action_url, created_at=str(notif.created_at),
    )


@router.put("/read-all", status_code=204)
async def mark_all_read(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    await db.execute(
        update(Notification)
        .where(Notification.user_id == current_user.id, Notification.is_read == False)
        .values(is_read=True)
    )
    await db.commit()


@router.delete("/{notif_id}", status_code=204)
async def delete_notification(
    notif_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    result = await db.execute(
        select(Notification).where(Notification.id == notif_id, Notification.user_id == current_user.id)
    )
    notif = result.scalar_one_or_none()
    if notif:
        await db.delete(notif)
        await db.commit()


@router.get("/settings", response_model=NotificationSettingsOut)
async def get_settings(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    result = await db.execute(
        select(NotificationSettings).where(NotificationSettings.user_id == current_user.id)
    )
    settings = result.scalar_one_or_none()
    if not settings:
        settings = NotificationSettings(user_id=current_user.id)
        db.add(settings)
        await db.commit()
    return NotificationSettingsOut(
        workout_reminders=settings.workout_reminders,
        streak_alerts=settings.streak_alerts,
        achievement_alerts=settings.achievement_alerts,
        social_alerts=settings.social_alerts,
        challenge_alerts=settings.challenge_alerts,
        email_notifications=settings.email_notifications,
    )


@router.put("/settings", response_model=NotificationSettingsOut)
async def update_settings(
    body: NotificationSettingsUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    result = await db.execute(
        select(NotificationSettings).where(NotificationSettings.user_id == current_user.id)
    )
    settings = result.scalar_one_or_none()
    if not settings:
        settings = NotificationSettings(user_id=current_user.id)
        db.add(settings)

    for field, val in body.model_dump(exclude_none=True).items():
        setattr(settings, field, val)

    await db.commit()
    return NotificationSettingsOut(
        workout_reminders=settings.workout_reminders,
        streak_alerts=settings.streak_alerts,
        achievement_alerts=settings.achievement_alerts,
        social_alerts=settings.social_alerts,
        challenge_alerts=settings.challenge_alerts,
        email_notifications=settings.email_notifications,
    )
