from __future__ import annotations
from datetime import datetime, date
from typing import Optional
from pydantic import BaseModel, ConfigDict


# ── Food ─────────────────────────────────────────────────────────────────────

class FoodResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str
    brand: Optional[str] = None
    calories_per_100g: float
    protein_g: float
    carbs_g: float
    fat_g: float
    fiber_g: float
    sugar_g: float
    sodium_mg: float
    is_custom: bool


class FoodListResponse(BaseModel):
    total: int
    page: int
    per_page: int
    items: list[FoodResponse]


# ── Meal Logs ─────────────────────────────────────────────────────────────────

class MealLogCreate(BaseModel):
    food_id: int
    meal_type: str  # breakfast / lunch / dinner / snack
    quantity_g: float
    logged_at: Optional[datetime] = None


class MealLogResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    food_id: int
    meal_type: str
    quantity_g: float
    logged_at: datetime
    calories: float
    protein_g: float
    carbs_g: float
    fat_g: float
    fiber_g: float


class MealTypeGroup(BaseModel):
    meal_type: str
    items: list[MealLogResponse]
    subtotal_calories: float
    subtotal_protein_g: float
    subtotal_carbs_g: float
    subtotal_fat_g: float


class DailySummaryResponse(BaseModel):
    date: str
    total_calories: float
    total_protein_g: float
    total_carbs_g: float
    total_fat_g: float
    total_fiber_g: float
    meals: list[MealTypeGroup]


class WeeklyDayAdherence(BaseModel):
    date: str
    calories: float
    target: int
    adherence_pct: float


class WeeklyAdherenceResponse(BaseModel):
    days: list[WeeklyDayAdherence]
    avg_adherence_pct: float


# ── Nutrition Goals ───────────────────────────────────────────────────────────

class NutritionGoalUpsert(BaseModel):
    calories_target: int = 2000
    protein_g: int = 150
    carbs_g: int = 200
    fat_g: int = 65
    fiber_g: int = 25


class NutritionGoalResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    calories_target: int
    protein_g: int
    carbs_g: int
    fat_g: int
    fiber_g: int
    updated_at: datetime
