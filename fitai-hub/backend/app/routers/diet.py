from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, desc
from app.database import get_db
from app.middleware.auth import get_current_user
from app.models.user import User
from app.models.diet import DietPlan, MealLog, BodyMeasurement
from app.schemas.diet import (
    DietPlanCreate, DietPlanResponse, DietPlanSummary,
    MealLogCreate, MealLogUpdate, MealLogResponse,
    DailyNutritionSummary,
    BodyMeasurementCreate, BodyMeasurementResponse,
)
from app.services.diet_service import (
    get_daily_totals, get_active_diet_plan, calculate_adherence
)
from datetime import date, datetime, timezone
import uuid

router = APIRouter(prefix="/diet", tags=["Diet & Nutrition"])


# ============================================================
# DIET PLANS
# ============================================================
@router.get("/plans", response_model=list[DietPlanSummary])
async def get_my_diet_plans(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    result = await db.execute(
        select(DietPlan)
        .where(DietPlan.user_id == current_user.id)
        .order_by(desc(DietPlan.created_at))
    )
    return result.scalars().all()


@router.post("/plans", response_model=DietPlanResponse, status_code=201)
async def create_diet_plan(
    data: DietPlanCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    plan = DietPlan(
        id=str(uuid.uuid4()),
        user_id=current_user.id,
        title=data.title,
        source="user",
        target_calories=data.target_calories,
        target_protein_g=data.target_protein_g,
        target_carbs_g=data.target_carbs_g,
        target_fat_g=data.target_fat_g,
        is_active=True,
        is_public=data.is_public,
        days_data=data.days_data,
    )
    db.add(plan)
    await db.commit()
    await db.refresh(plan)
    return plan


@router.get("/plans/{plan_id}", response_model=DietPlanResponse)
async def get_diet_plan(
    plan_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    result = await db.execute(
        select(DietPlan).where(
            DietPlan.id == plan_id,
            DietPlan.user_id == current_user.id,
        )
    )
    plan = result.scalar_one_or_none()
    if not plan:
        raise HTTPException(status_code=404, detail="Plan no encontrado")
    return plan


@router.delete("/plans/{plan_id}", status_code=204)
async def delete_diet_plan(
    plan_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    result = await db.execute(
        select(DietPlan).where(
            DietPlan.id == plan_id,
            DietPlan.user_id == current_user.id,
        )
    )
    plan = result.scalar_one_or_none()
    if not plan:
        raise HTTPException(status_code=404, detail="Plan no encontrado")
    await db.delete(plan)
    await db.commit()


# ============================================================
# MEAL LOGS
# ============================================================
@router.get("/logs", response_model=DailyNutritionSummary)
async def get_daily_nutrition(
    target_date: date = None,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    if not target_date:
        target_date = date.today()

    # Obtener comidas del día
    result = await db.execute(
        select(MealLog)
        .where(
            MealLog.user_id == current_user.id,
            MealLog.logged_date == target_date,
        )
        .order_by(MealLog.logged_at)
    )
    meals = result.scalars().all()

    # Totales del día
    totals = await get_daily_totals(db, current_user.id, target_date)

    # Plan activo para targets y adherencia
    active_plan = await get_active_diet_plan(db, current_user.id)
    target_calories = active_plan.target_calories if active_plan else None
    target_protein_g = active_plan.target_protein_g if active_plan else None
    target_carbs_g = active_plan.target_carbs_g if active_plan else None
    target_fat_g = active_plan.target_fat_g if active_plan else None

    adherence = calculate_adherence(
        totals["total_calories"], target_calories
    ) if target_calories else None

    return DailyNutritionSummary(
        date=target_date,
        **totals,
        meals=[MealLogResponse.model_validate(m) for m in meals],
        target_calories=target_calories,
        target_protein_g=target_protein_g,
        target_carbs_g=target_carbs_g,
        target_fat_g=target_fat_g,
        adherence_pct=adherence,
    )


@router.post("/logs", response_model=MealLogResponse, status_code=201)
async def add_meal_log(
    data: MealLogCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    meal = MealLog(
        id=str(uuid.uuid4()),
        user_id=current_user.id,
        logged_date=data.logged_date,
        meal_type=data.meal_type,
        name=data.name,
        calories=data.calories,
        protein_g=data.protein_g,
        carbs_g=data.carbs_g,
        fat_g=data.fat_g,
        source=data.source,
        photo_url=data.photo_url,
    )
    db.add(meal)
    await db.commit()
    await db.refresh(meal)
    return meal


@router.put("/logs/{meal_id}", response_model=MealLogResponse)
async def update_meal_log(
    meal_id: str,
    data: MealLogUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    result = await db.execute(
        select(MealLog).where(
            MealLog.id == meal_id,
            MealLog.user_id == current_user.id,
        )
    )
    meal = result.scalar_one_or_none()
    if not meal:
        raise HTTPException(status_code=404, detail="Comida no encontrada")

    update_data = data.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(meal, field, value)

    await db.commit()
    await db.refresh(meal)
    return meal


@router.delete("/logs/{meal_id}", status_code=204)
async def delete_meal_log(
    meal_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    result = await db.execute(
        select(MealLog).where(
            MealLog.id == meal_id,
            MealLog.user_id == current_user.id,
        )
    )
    meal = result.scalar_one_or_none()
    if not meal:
        raise HTTPException(status_code=404, detail="Comida no encontrada")
    await db.delete(meal)
    await db.commit()


# ============================================================
# BODY MEASUREMENTS
# ============================================================
@router.get("/measurements", response_model=list[BodyMeasurementResponse])
async def get_measurements(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    result = await db.execute(
        select(BodyMeasurement)
        .where(BodyMeasurement.user_id == current_user.id)
        .order_by(desc(BodyMeasurement.measured_at))
    )
    return result.scalars().all()


@router.post("/measurements", response_model=BodyMeasurementResponse, status_code=201)
async def add_measurement(
    data: BodyMeasurementCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    measurement = BodyMeasurement(
        id=str(uuid.uuid4()),
        user_id=current_user.id,
        weight_kg=data.weight_kg,
        body_fat_pct=data.body_fat_pct,
        muscle_mass_kg=data.muscle_mass_kg,
        waist_cm=data.waist_cm,
        chest_cm=data.chest_cm,
        arms_cm=data.arms_cm,
        photo_url=data.photo_url,
        measured_at=data.measured_at,
    )
    db.add(measurement)
    await db.commit()
    await db.refresh(measurement)
    return measurement


@router.delete("/measurements/{measurement_id}", status_code=204)
async def delete_measurement(
    measurement_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    result = await db.execute(
        select(BodyMeasurement).where(
            BodyMeasurement.id == measurement_id,
            BodyMeasurement.user_id == current_user.id,
        )
    )
    measurement = result.scalar_one_or_none()
    if not measurement:
        raise HTTPException(status_code=404, detail="Medición no encontrada")
    await db.delete(measurement)
    await db.commit()