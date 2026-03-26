from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from app.models.diet import MealLog, DietPlan, BodyMeasurement
from datetime import date
from typing import Optional


async def get_daily_totals(
    db: AsyncSession,
    user_id: str,
    target_date: date,
) -> dict:
    result = await db.execute(
        select(
            func.coalesce(func.sum(MealLog.calories), 0).label("total_calories"),
            func.coalesce(func.sum(MealLog.protein_g), 0).label("total_protein_g"),
            func.coalesce(func.sum(MealLog.carbs_g), 0).label("total_carbs_g"),
            func.coalesce(func.sum(MealLog.fat_g), 0).label("total_fat_g"),
        )
        .where(
            MealLog.user_id == user_id,
            MealLog.logged_date == target_date,
        )
    )
    row = result.one()
    return {
        "total_calories": float(row.total_calories),
        "total_protein_g": float(row.total_protein_g),
        "total_carbs_g": float(row.total_carbs_g),
        "total_fat_g": float(row.total_fat_g),
    }


async def get_active_diet_plan(
    db: AsyncSession,
    user_id: str,
) -> Optional[DietPlan]:
    result = await db.execute(
        select(DietPlan).where(
            DietPlan.user_id == user_id,
            DietPlan.is_active == True,
        ).order_by(DietPlan.created_at.desc()).limit(1)
    )
    return result.scalar_one_or_none()


def calculate_adherence(actual: float, target: float) -> Optional[float]:
    if not target or target == 0:
        return None
    adherence = (actual / target) * 100
    return round(min(adherence, 100), 1)