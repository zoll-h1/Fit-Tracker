import os
import uuid
from datetime import datetime, timezone
from pathlib import Path

from fastapi import APIRouter, Depends, File, HTTPException, UploadFile, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import settings
from app.database import get_db
from app.dependencies import get_current_user
from app.models.user import User
from app.schemas.auth import UserResponse, UserUpdateRequest

router = APIRouter(prefix="/api/users", tags=["users"])

ALLOWED_IMAGE_TYPES = {"image/jpeg", "image/png", "image/webp", "image/gif"}
MAX_SIZE_BYTES = settings.MAX_UPLOAD_SIZE_MB * 1024 * 1024


@router.get("/profile", response_model=UserResponse)
async def get_profile(current_user: User = Depends(get_current_user)):
    return UserResponse.model_validate(current_user)


@router.put("/profile", response_model=UserResponse)
async def update_profile(
    body: UserUpdateRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    update_data = body.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(current_user, field, value)
    current_user.updated_at = datetime.now(timezone.utc)
    await db.commit()
    await db.refresh(current_user)
    return UserResponse.model_validate(current_user)


@router.post("/avatar", response_model=UserResponse)
async def upload_avatar(
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    if file.content_type not in ALLOWED_IMAGE_TYPES:
        raise HTTPException(
            status_code=status.HTTP_415_UNSUPPORTED_MEDIA_TYPE,
            detail=f"Unsupported file type. Allowed: {', '.join(ALLOWED_IMAGE_TYPES)}",
        )

    content = await file.read()
    if len(content) > MAX_SIZE_BYTES:
        raise HTTPException(
            status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
            detail=f"File too large. Max size: {settings.MAX_UPLOAD_SIZE_MB}MB",
        )

    ext = Path(file.filename or "avatar.jpg").suffix.lower() or ".jpg"
    filename = f"{uuid.uuid4().hex}{ext}"
    avatar_dir = Path(settings.UPLOAD_DIR) / "avatars"
    avatar_dir.mkdir(parents=True, exist_ok=True)

    file_path = avatar_dir / filename
    with open(file_path, "wb") as f:
        f.write(content)

    # Remove old avatar file if it exists locally
    if current_user.avatar_url and current_user.avatar_url.startswith("/uploads/"):
        old_path = Path(current_user.avatar_url.lstrip("/"))
        if old_path.exists():
            old_path.unlink(missing_ok=True)

    current_user.avatar_url = f"/uploads/avatars/{filename}"
    current_user.updated_at = datetime.now(timezone.utc)
    await db.commit()
    await db.refresh(current_user)
    return UserResponse.model_validate(current_user)
