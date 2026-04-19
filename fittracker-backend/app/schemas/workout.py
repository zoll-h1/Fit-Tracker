from __future__ import annotations
from datetime import datetime
from typing import Optional
from pydantic import BaseModel, ConfigDict, field_validator


# ── Sets ─────────────────────────────────────────────────────────────────────

class WorkoutSetCreate(BaseModel):
    set_number: int
    set_type: str = "normal"
    reps: Optional[int] = None
    weight_kg: Optional[float] = None
    duration_seconds: Optional[int] = None
    distance_km: Optional[float] = None
    rpe: Optional[int] = None


class WorkoutSetUpdate(BaseModel):
    reps: Optional[int] = None
    weight_kg: Optional[float] = None
    duration_seconds: Optional[int] = None
    distance_km: Optional[float] = None
    rpe: Optional[int] = None
    completed: Optional[bool] = None


class WorkoutSetResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    set_number: int
    set_type: str
    reps: Optional[int] = None
    weight_kg: Optional[float] = None
    duration_seconds: Optional[int] = None
    distance_km: Optional[float] = None
    rpe: Optional[int] = None
    completed: bool
    completed_at: Optional[datetime] = None
    is_pr: bool


# ── Exercises within a session ───────────────────────────────────────────────

class WorkoutExerciseCreate(BaseModel):
    exercise_library_id: int
    exercise_order: int = 1
    notes: Optional[str] = None
    rest_seconds: int = 60


class WorkoutExerciseResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    exercise_library_id: int
    exercise_order: int
    notes: Optional[str] = None
    rest_seconds: int
    sets: list[WorkoutSetResponse] = []


# ── Sessions ─────────────────────────────────────────────────────────────────

class WorkoutStartRequest(BaseModel):
    name: str = "Workout"
    template_id: Optional[int] = None
    notes: Optional[str] = None


class WorkoutFinishRequest(BaseModel):
    notes: Optional[str] = None


class WorkoutSessionResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str
    notes: Optional[str] = None
    started_at: datetime
    finished_at: Optional[datetime] = None
    duration_seconds: Optional[int] = None
    total_volume_kg: float
    total_sets: int
    total_reps: int
    calories_burned: Optional[int] = None
    status: str
    exercises: list[WorkoutExerciseResponse] = []


class WorkoutSessionListItem(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str
    started_at: datetime
    finished_at: Optional[datetime] = None
    duration_seconds: Optional[int] = None
    total_volume_kg: float
    total_sets: int
    total_reps: int
    status: str


class WorkoutHistoryResponse(BaseModel):
    total: int
    page: int
    per_page: int
    items: list[WorkoutSessionListItem]


# ── Personal Record ───────────────────────────────────────────────────────────

class PRResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    exercise_id: int
    exercise_name: str
    weight_kg: float
    reps: int
    achieved_at: datetime
