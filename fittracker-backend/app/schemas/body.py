from __future__ import annotations
from datetime import datetime
from typing import Optional
from pydantic import BaseModel, ConfigDict


# ── Body Metrics ──────────────────────────────────────────────────────────────

class BodyMetricCreate(BaseModel):
    weight_kg: Optional[float] = None
    body_fat_pct: Optional[float] = None
    muscle_mass_kg: Optional[float] = None
    waist_cm: Optional[float] = None
    chest_cm: Optional[float] = None
    hip_cm: Optional[float] = None
    notes: Optional[str] = None
    recorded_at: Optional[datetime] = None


class BodyMetricResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    weight_kg: Optional[float] = None
    body_fat_pct: Optional[float] = None
    muscle_mass_kg: Optional[float] = None
    bmi: Optional[float] = None
    waist_cm: Optional[float] = None
    chest_cm: Optional[float] = None
    hip_cm: Optional[float] = None
    notes: Optional[str] = None
    recorded_at: datetime


class BodyMetricHistoryResponse(BaseModel):
    total: int
    page: int
    per_page: int
    items: list[BodyMetricResponse]


# ── Body Goals ────────────────────────────────────────────────────────────────

class BodyGoalCreate(BaseModel):
    goal_type: str
    target_value: float
    start_value: Optional[float] = None
    unit: str = "kg"
    deadline: Optional[datetime] = None


class BodyGoalUpdate(BaseModel):
    target_value: Optional[float] = None
    current_value: Optional[float] = None
    unit: Optional[str] = None
    deadline: Optional[datetime] = None
    status: Optional[str] = None


class BodyGoalResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    goal_type: str
    target_value: float
    start_value: Optional[float] = None
    current_value: Optional[float] = None
    unit: str
    deadline: Optional[datetime] = None
    status: str
    completed_at: Optional[datetime] = None
    created_at: datetime
    progress_pct: Optional[float] = None
