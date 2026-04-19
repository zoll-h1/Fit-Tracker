from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from pydantic import BaseModel, ConfigDict
from typing import Optional
from datetime import datetime

from app.database import get_db
from app.dependencies import get_current_user
from app.models.user import User
from app.models.social import UserFollow, ActivityFeed, FeedLike, FeedComment
from app.models.workout import WorkoutSession

router = APIRouter(prefix="/api/social", tags=["social"])
users_router = APIRouter(prefix="/api/users", tags=["users-social"])


# ─── Schemas ──────────────────────────────────────────────────────────────────

class FollowUserOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    username: str
    full_name: Optional[str]
    avatar_url: Optional[str]


class FeedItemOut(BaseModel):
    id: int
    user_id: int
    username: str
    avatar_url: Optional[str]
    activity_type: str
    title: str
    body: Optional[str]
    likes_count: int
    comments_count: int
    is_liked_by_me: bool
    created_at: datetime


class CommentCreate(BaseModel):
    content: str


class CommentOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    feed_id: int
    user_id: int
    username: str
    content: str
    created_at: datetime


class PublicProfileOut(BaseModel):
    id: int
    username: str
    full_name: Optional[str]
    avatar_url: Optional[str]
    created_at: datetime
    followers_count: int
    following_count: int
    is_following: bool


# ─── Follow endpoints ─────────────────────────────────────────────────────────

@router.post("/follow/{user_id}", status_code=200)
async def follow_user(
    user_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    if user_id == current_user.id:
        raise HTTPException(status_code=400, detail="Cannot follow yourself")

    # Check target user exists
    target = await db.get(User, user_id)
    if not target:
        raise HTTPException(status_code=404, detail="User not found")

    existing = await db.execute(
        select(UserFollow).where(
            UserFollow.follower_id == current_user.id,
            UserFollow.following_id == user_id,
        )
    )
    if existing.scalar_one_or_none():
        raise HTTPException(status_code=400, detail="Already following")

    follow = UserFollow(follower_id=current_user.id, following_id=user_id)
    db.add(follow)
    await db.flush()
    return {"detail": "Followed successfully"}


@router.delete("/follow/{user_id}", status_code=200)
async def unfollow_user(
    user_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    result = await db.execute(
        select(UserFollow).where(
            UserFollow.follower_id == current_user.id,
            UserFollow.following_id == user_id,
        )
    )
    follow = result.scalar_one_or_none()
    if not follow:
        raise HTTPException(status_code=404, detail="Not following this user")
    await db.delete(follow)
    await db.flush()
    return {"detail": "Unfollowed successfully"}


@router.get("/followers", response_model=list[FollowUserOut])
async def get_followers(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """List users who follow me."""
    result = await db.execute(
        select(User)
        .join(UserFollow, UserFollow.follower_id == User.id)
        .where(UserFollow.following_id == current_user.id)
    )
    return result.scalars().all()


@router.get("/following", response_model=list[FollowUserOut])
async def get_following(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """List users I follow."""
    result = await db.execute(
        select(User)
        .join(UserFollow, UserFollow.following_id == User.id)
        .where(UserFollow.follower_id == current_user.id)
    )
    return result.scalars().all()


# ─── Feed endpoints ───────────────────────────────────────────────────────────

@router.get("/feed", response_model=list[FeedItemOut])
async def get_feed(
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    following_ids_result = await db.execute(
        select(UserFollow.following_id).where(UserFollow.follower_id == current_user.id)
    )
    following_ids = [row[0] for row in following_ids_result.all()]
    feed_user_ids = following_ids + [current_user.id]

    stmt = (
        select(ActivityFeed, User.username, User.avatar_url)
        .join(User, User.id == ActivityFeed.user_id)
        .where(ActivityFeed.user_id.in_(feed_user_ids))
        .order_by(ActivityFeed.created_at.desc())
        .offset(skip)
        .limit(limit)
    )
    rows = (await db.execute(stmt)).all()

    liked_result = await db.execute(
        select(FeedLike.feed_id).where(FeedLike.user_id == current_user.id)
    )
    liked_ids = {row[0] for row in liked_result.all()}

    return [
        FeedItemOut(
            id=feed.id,
            user_id=feed.user_id,
            username=username,
            avatar_url=av,
            activity_type=feed.activity_type,
            title=feed.title,
            body=feed.body,
            likes_count=feed.likes_count,
            comments_count=feed.comments_count,
            is_liked_by_me=(feed.id in liked_ids),
            created_at=feed.created_at,
        )
        for feed, username, av in rows
    ]


@router.post("/feed/{feed_id}/like")
async def toggle_like(
    feed_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    feed_item = await db.get(ActivityFeed, feed_id)
    if not feed_item:
        raise HTTPException(status_code=404, detail="Feed item not found")

    existing = await db.execute(
        select(FeedLike).where(
            FeedLike.feed_id == feed_id,
            FeedLike.user_id == current_user.id,
        )
    )
    like = existing.scalar_one_or_none()

    if like:
        await db.delete(like)
        feed_item.likes_count = max(0, feed_item.likes_count - 1)
        await db.flush()
        return {"liked": False, "likes_count": feed_item.likes_count}
    else:
        new_like = FeedLike(feed_id=feed_id, user_id=current_user.id)
        db.add(new_like)
        feed_item.likes_count += 1
        await db.flush()
        return {"liked": True, "likes_count": feed_item.likes_count}


@router.post("/feed/{feed_id}/comments", response_model=CommentOut, status_code=201)
async def add_comment(
    feed_id: int,
    body: CommentCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    feed_item = await db.get(ActivityFeed, feed_id)
    if not feed_item:
        raise HTTPException(status_code=404, detail="Feed item not found")

    comment = FeedComment(
        feed_id=feed_id,
        user_id=current_user.id,
        content=body.content,
    )
    db.add(comment)
    feed_item.comments_count += 1
    await db.flush()
    await db.refresh(comment)

    return CommentOut(
        id=comment.id,
        feed_id=comment.feed_id,
        user_id=comment.user_id,
        username=current_user.username,
        content=comment.content,
        created_at=comment.created_at,
    )


@router.get("/feed/{feed_id}/comments", response_model=list[CommentOut])
async def get_comments(
    feed_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    result = await db.execute(
        select(FeedComment, User.username)
        .join(User, User.id == FeedComment.user_id)
        .where(FeedComment.feed_id == feed_id)
        .order_by(FeedComment.created_at.asc())
    )
    rows = result.all()
    return [
        CommentOut(
            id=c.id,
            feed_id=c.feed_id,
            user_id=c.user_id,
            username=username,
            content=c.content,
            created_at=c.created_at,
        )
        for c, username in rows
    ]


@router.delete("/feed/{feed_id}/comments/{comment_id}", status_code=200)
async def delete_comment(
    feed_id: int,
    comment_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    result = await db.execute(
        select(FeedComment).where(
            FeedComment.id == comment_id,
            FeedComment.feed_id == feed_id,
        )
    )
    comment = result.scalar_one_or_none()
    if not comment:
        raise HTTPException(status_code=404, detail="Comment not found")
    if comment.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Cannot delete another user's comment")

    feed_item = await db.get(ActivityFeed, feed_id)
    if feed_item:
        feed_item.comments_count = max(0, feed_item.comments_count - 1)

    await db.delete(comment)
    await db.flush()
    return {"detail": "Comment deleted"}


# ─── Users router: public profile + search ────────────────────────────────────

@users_router.get("/search", response_model=list[FollowUserOut])
async def search_users(
    q: str = Query(..., min_length=1),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    result = await db.execute(
        select(User).where(
            (User.username.ilike(f"%{q}%")) | (User.full_name.ilike(f"%{q}%"))
        ).limit(20)
    )
    return result.scalars().all()


@users_router.get("/{user_id}/profile", response_model=PublicProfileOut)
async def public_profile(
    user_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    user = await db.get(User, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    followers_count_result = await db.execute(
        select(func.count(UserFollow.id)).where(UserFollow.following_id == user_id)
    )
    followers_count = followers_count_result.scalar() or 0

    following_count_result = await db.execute(
        select(func.count(UserFollow.id)).where(UserFollow.follower_id == user_id)
    )
    following_count = following_count_result.scalar() or 0

    is_following_result = await db.execute(
        select(UserFollow).where(
            UserFollow.follower_id == current_user.id,
            UserFollow.following_id == user_id,
        )
    )
    is_following = is_following_result.scalar_one_or_none() is not None

    return PublicProfileOut(
        id=user.id,
        username=user.username,
        full_name=user.full_name,
        avatar_url=user.avatar_url,
        created_at=user.created_at,
        followers_count=followers_count,
        following_count=following_count,
        is_following=is_following,
    )
