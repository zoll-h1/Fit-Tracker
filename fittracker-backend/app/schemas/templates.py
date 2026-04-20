from __future__ import annotations
from datetime import datetime
from typing import Optional
from pydantic import BaseModel, ConfigDict, field_validator


class TemplateExerciseCreate(BaseModel):
    exercise_library_id: int
    exercise_order: int = 1
    target_sets: Optional[int] = None
    target_reps: Optional[int] = None
    target_weight_kg: Optional[float] = None
    rest_seconds: int = 60
    notes: Optional[str] = None


class TemplateExerciseOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    exercise_library_id: int
    exercise_order: int
    target_sets: Optional[int] = None
    target_reps: Optional[int] = None
    target_weight_kg: Optional[float] = None
    rest_seconds: int
    notes: Optional[str] = None
    exercise_name: Optional[str] = None  # populated manually


class TemplateCreate(BaseModel):
    name: str
    description: Optional[str] = None
    is_public: bool = False
    estimated_duration_min: Optional[int] = None
    exercises: list[TemplateExerciseCreate] = []

    @field_validator('name')
    @classmethod
    def name_not_empty(cls, v: str) -> str:
        if not v.strip():
            raise ValueError('Name cannot be empty')
        return v.strip()


class TemplateUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    is_public: Optional[bool] = None
    estimated_duration_min: Optional[int] = None


class TemplateOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    user_id: int
    name: str
    description: Optional[str] = None
    is_public: bool
    estimated_duration_min: Optional[int] = None
    times_used: int
    created_at: datetime
    exercise_count: int = 0  # populated manually


class TemplateDetailOut(TemplateOut):
    exercises: list[TemplateExerciseOut] = []
    creator_username: Optional[str] = None  # populated manually


class TemplateSaveFromWorkout(BaseModel):
    name: str
    description: Optional[str] = None
    is_public: bool = False
    estimated_duration_min: Optional[int] = None
