from pydantic import BaseModel
from typing import Optional, List, Dict, Any
from datetime import datetime, date
import enum


class MealTypeEnum(str, enum.Enum):
    BREAKFAST = "breakfast"
    LUNCH = "lunch"
    DINNER = "dinner"
    SNACK = "snack"


class FoodSourceEnum(str, enum.Enum):
    MANUAL = "manual"
    AI_PHOTO = "ai_photo"
    AI_TEXT = "ai_text"
    BARCODE = "barcode"


# --- DIET PLANS ---
class DietPlanCreate(BaseModel):
    title: str
    target_calories: Optional[int] = None
    target_protein_g: Optional[int] = None
    target_carbs_g: Optional[int] = None
    target_fat_g: Optional[int] = None
    is_public: bool = False
    days_data: Optional[Dict[str, Any]] = None


class DietPlanResponse(BaseModel):
    id: str
    title: str
    source: str
    target_calories: Optional[int] = None
    target_protein_g: Optional[int] = None
    target_carbs_g: Optional[int] = None
    target_fat_g: Optional[int] = None
    is_active: bool
    is_public: bool
    days_data: Optional[Dict[str, Any]] = None
    created_at: datetime

    class Config:
        from_attributes = True


class DietPlanSummary(BaseModel):
    id: str
    title: str
    source: str
    target_calories: Optional[int] = None
    is_active: bool
    created_at: datetime

    class Config:
        from_attributes = True


# --- MEAL LOGS ---
class MealLogCreate(BaseModel):
    logged_date: date
    meal_type: MealTypeEnum
    name: str
    calories: float
    protein_g: float = 0
    carbs_g: float = 0
    fat_g: float = 0
    source: FoodSourceEnum = FoodSourceEnum.MANUAL
    photo_url: Optional[str] = None


class MealLogUpdate(BaseModel):
    name: Optional[str] = None
    calories: Optional[float] = None
    protein_g: Optional[float] = None
    carbs_g: Optional[float] = None
    fat_g: Optional[float] = None


class MealLogResponse(BaseModel):
    id: str
    logged_date: date
    meal_type: str
    name: str
    calories: float
    protein_g: float
    carbs_g: float
    fat_g: float
    source: str
    photo_url: Optional[str] = None
    ai_confidence: Optional[float] = None
    logged_at: datetime

    class Config:
        from_attributes = True


# --- DAILY SUMMARY ---
class DailyNutritionSummary(BaseModel):
    date: date
    total_calories: float
    total_protein_g: float
    total_carbs_g: float
    total_fat_g: float
    meals: List[MealLogResponse]
    target_calories: Optional[int] = None
    target_protein_g: Optional[int] = None
    target_carbs_g: Optional[int] = None
    target_fat_g: Optional[int] = None
    adherence_pct: Optional[float] = None


# --- BODY MEASUREMENTS ---
class BodyMeasurementCreate(BaseModel):
    weight_kg: Optional[float] = None
    body_fat_pct: Optional[float] = None
    muscle_mass_kg: Optional[float] = None
    waist_cm: Optional[float] = None
    chest_cm: Optional[float] = None
    arms_cm: Optional[float] = None
    photo_url: Optional[str] = None
    measured_at: datetime


class BodyMeasurementResponse(BaseModel):
    id: str
    weight_kg: Optional[float] = None
    body_fat_pct: Optional[float] = None
    muscle_mass_kg: Optional[float] = None
    waist_cm: Optional[float] = None
    chest_cm: Optional[float] = None
    arms_cm: Optional[float] = None
    photo_url: Optional[str] = None
    measured_at: datetime

    class Config:
        from_attributes = True