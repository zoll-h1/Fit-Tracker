from __future__ import annotations
from datetime import datetime
from typing import Optional
from pydantic import BaseModel, ConfigDict


class ExerciseResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str
    slug: str
    muscle_primary: Optional[str] = None
    muscle_secondary: Optional[str] = None
    equipment: Optional[str] = None
    force_type: Optional[str] = None
    difficulty: str
    category: str
    description: Optional[str] = None
    instructions: Optional[str] = None
    video_url: Optional[str] = None
    image_url: Optional[str] = None
    is_custom: bool
    met_value: float
    created_at: datetime


class ExerciseListResponse(BaseModel):
    total: int
    page: int
    per_page: int
    items: list[ExerciseResponse]
