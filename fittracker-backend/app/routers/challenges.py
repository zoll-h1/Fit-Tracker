from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from pydantic import BaseModel, ConfigDict, field_validator
from typing import Optional
from datetime import date, datetime

from app.database import get_db
from app.dependencies import get_current_user
from app.models.user import User
from app.models.challenges import Challenge, ChallengeParticipant
from app.services.challenge_service import update_leaderboard_ranks

router = APIRouter(prefix="/api/challenges", tags=["challenges"])


# ─── Schemas ────────────────────────────────────────────────────────────────

class ChallengeCreate(BaseModel):
    title: str
    description: Optional[str] = None
    challenge_type: str
    target_value: float
    start_date: date
    end_date: date
    is_public: bool = True

    @field_validator("challenge_type")
    @classmethod
    def valid_type(cls, v: str) -> str:
        if v not in ("total_workouts", "total_volume", "streak"):
            raise ValueError("Invalid challenge type")
        return v

    @field_validator("end_date")
    @classmethod
    def end_after_start(cls, v: date, info) -> date:
        if "start_date" in info.data and v <= info.data["start_date"]:
            raise ValueError("end_date must be after start_date")
        return v


class ChallengeUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    is_public: Optional[bool] = None


class ParticipantOut(BaseModel):
    user_id: int
    username: str
    avatar_url: Optional[str]
    current_progress: float
    rank: Optional[int]
    joined_at: datetime


class ChallengeOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    creator_id: int
    title: str
    description: Optional[str]
    challenge_type: str
    target_value: float
    start_date: date
    end_date: date
    is_public: bool
    status: str
    winner_user_id: Optional[int]
    created_at: datetime
    participant_count: int = 0
    is_joined: bool = False
    my_progress: Optional[float] = None
    my_rank: Optional[int] = None


class ChallengeDetailOut(ChallengeOut):
    participants: list[ParticipantOut] = []


# ─── Helpers ─────────────────────────────────────────────────────────────────

async def _get_challenge_or_404(db: AsyncSession, challenge_id: int) -> Challenge:
    challenge = await db.get(Challenge, challenge_id)
    if not challenge:
        raise HTTPException(status_code=404, detail="Challenge not found")
    return challenge


async def _enrich(db: AsyncSession, challenge: Challenge, user_id: int) -> ChallengeOut:
    count_result = await db.execute(
        select(func.count(ChallengeParticipant.id)).where(
            ChallengeParticipant.challenge_id == challenge.id
        )
    )
    participant_count = count_result.scalar() or 0

    part_result = await db.execute(
        select(ChallengeParticipant).where(
            ChallengeParticipant.challenge_id == challenge.id,
            ChallengeParticipant.user_id == user_id,
        )
    )
    my_part = part_result.scalar_one_or_none()

    return ChallengeOut(
        id=challenge.id,
        creator_id=challenge.creator_id,
        title=challenge.title,
        description=challenge.description,
        challenge_type=challenge.challenge_type,
        target_value=float(challenge.target_value),
        start_date=challenge.start_date,
        end_date=challenge.end_date,
        is_public=challenge.is_public,
        status=challenge.status,
        winner_user_id=challenge.winner_user_id,
        created_at=challenge.created_at,
        participant_count=participant_count,
        is_joined=my_part is not None,
        my_progress=float(my_part.current_progress) if my_part else None,
        my_rank=my_part.rank if my_part else None,
    )


# ─── Endpoints ───────────────────────────────────────────────────────────────

@router.post("", response_model=ChallengeOut, status_code=201)
async def create_challenge(
    body: ChallengeCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    challenge = Challenge(
        creator_id=current_user.id,
        title=body.title,
        description=body.description,
        challenge_type=body.challenge_type,
        target_value=body.target_value,
        start_date=body.start_date,
        end_date=body.end_date,
        is_public=body.is_public,
        status="active",
    )
    db.add(challenge)
    await db.flush()

    # Creator auto-joins
    participant = ChallengeParticipant(
        challenge_id=challenge.id,
        user_id=current_user.id,
        current_progress=0,
        rank=1,
    )
    db.add(participant)
    await db.flush()

    return await _enrich(db, challenge, current_user.id)


@router.get("", response_model=list[ChallengeOut])
async def list_challenges(
    status: str = Query("active"),
    mine: bool = Query(False),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    if mine:
        # Challenges user participates in OR created
        subq = select(ChallengeParticipant.challenge_id).where(
            ChallengeParticipant.user_id == current_user.id
        )
        q = select(Challenge).where(
            (Challenge.id.in_(subq)) | (Challenge.creator_id == current_user.id)
        )
    else:
        q = select(Challenge).where(Challenge.is_public == True)  # noqa: E712
        if status != "all":
            q = q.where(Challenge.status == status)

    q = q.order_by(Challenge.created_at.desc())
    result = await db.execute(q)
    challenges = result.scalars().all()
    return [await _enrich(db, c, current_user.id) for c in challenges]


@router.get("/{challenge_id}", response_model=ChallengeDetailOut)
async def get_challenge(
    challenge_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    challenge = await _get_challenge_or_404(db, challenge_id)

    result = await db.execute(
        select(ChallengeParticipant, User.username, User.avatar_url)
        .join(User, User.id == ChallengeParticipant.user_id)
        .where(ChallengeParticipant.challenge_id == challenge_id)
        .order_by(ChallengeParticipant.current_progress.desc())
    )
    rows = result.all()

    participants = [
        ParticipantOut(
            user_id=part.user_id,
            username=username,
            avatar_url=avatar_url,
            current_progress=float(part.current_progress),
            rank=part.rank,
            joined_at=part.joined_at,
        )
        for part, username, avatar_url in rows
    ]

    base = await _enrich(db, challenge, current_user.id)
    return ChallengeDetailOut(**base.model_dump(), participants=participants)


@router.put("/{challenge_id}", response_model=ChallengeOut)
async def update_challenge(
    challenge_id: int,
    body: ChallengeUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    challenge = await _get_challenge_or_404(db, challenge_id)
    if challenge.creator_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not the creator")

    if body.title is not None:
        challenge.title = body.title
    if body.description is not None:
        challenge.description = body.description
    if body.is_public is not None:
        challenge.is_public = body.is_public

    await db.flush()
    return await _enrich(db, challenge, current_user.id)


@router.delete("/{challenge_id}", status_code=200)
async def cancel_challenge(
    challenge_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    challenge = await _get_challenge_or_404(db, challenge_id)
    if challenge.creator_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not the creator")

    challenge.status = "cancelled"
    await db.flush()
    return {"status": "cancelled"}


@router.post("/{challenge_id}/join", status_code=200)
async def join_challenge(
    challenge_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    challenge = await _get_challenge_or_404(db, challenge_id)
    if challenge.status != "active":
        raise HTTPException(status_code=400, detail="Challenge is not active")

    existing = await db.execute(
        select(ChallengeParticipant).where(
            ChallengeParticipant.challenge_id == challenge_id,
            ChallengeParticipant.user_id == current_user.id,
        )
    )
    if existing.scalar_one_or_none():
        raise HTTPException(status_code=400, detail="Already joined")

    participant = ChallengeParticipant(
        challenge_id=challenge_id,
        user_id=current_user.id,
        current_progress=0,
    )
    db.add(participant)
    await db.flush()

    await update_leaderboard_ranks(db, challenge_id)
    return {"joined": True}


@router.delete("/{challenge_id}/leave", status_code=200)
async def leave_challenge(
    challenge_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    challenge = await _get_challenge_or_404(db, challenge_id)

    if challenge.creator_id == current_user.id:
        raise HTTPException(status_code=400, detail="Creator cannot leave their own challenge")

    result = await db.execute(
        select(ChallengeParticipant).where(
            ChallengeParticipant.challenge_id == challenge_id,
            ChallengeParticipant.user_id == current_user.id,
        )
    )
    participant = result.scalar_one_or_none()
    if not participant:
        raise HTTPException(status_code=404, detail="Not a participant")

    await db.delete(participant)
    await db.flush()

    await update_leaderboard_ranks(db, challenge_id)
    return {"left": True}


@router.get("/{challenge_id}/leaderboard", response_model=list[ParticipantOut])
async def get_leaderboard(
    challenge_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    await _get_challenge_or_404(db, challenge_id)

    result = await db.execute(
        select(ChallengeParticipant, User.username, User.avatar_url)
        .join(User, User.id == ChallengeParticipant.user_id)
        .where(ChallengeParticipant.challenge_id == challenge_id)
        .order_by(ChallengeParticipant.current_progress.desc())
    )
    rows = result.all()

    return [
        ParticipantOut(
            user_id=part.user_id,
            username=username,
            avatar_url=avatar_url,
            current_progress=float(part.current_progress),
            rank=part.rank,
            joined_at=part.joined_at,
        )
        for part, username, avatar_url in rows
    ]
