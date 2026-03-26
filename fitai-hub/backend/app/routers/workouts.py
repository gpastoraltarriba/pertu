from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, desc
from sqlalchemy.orm import selectinload
from app.database import get_db
from app.middleware.auth import get_current_user
from app.models.user import User
from app.models.workout import (
    WorkoutPlan, WorkoutSession, SessionExercise,
    WorkoutLog, SetLog, Exercise
)
from app.schemas.workout import (
    WorkoutPlanCreate, WorkoutPlanResponse, WorkoutPlanSummary,
    WorkoutLogCreate, WorkoutLogUpdate, WorkoutLogResponse,
    SetLogCreate, SetLogResponse, ExerciseResponse, PRResponse
)
from app.services.workout_service import create_workout_plan, check_and_mark_pr
import uuid
from datetime import datetime, timezone

router = APIRouter(prefix="/workouts", tags=["Workouts"])


# ============================================================
# EXERCISES
# ============================================================
@router.get("/exercises", response_model=list[ExerciseResponse])
async def get_exercises(
    muscle: str = None,
    difficulty: str = None,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    query = select(Exercise)
    if muscle:
        query = query.where(Exercise.muscle_primary.ilike(f"%{muscle}%"))
    if difficulty:
        query = query.where(Exercise.difficulty == difficulty)
    result = await db.execute(query.limit(100))
    return result.scalars().all()


@router.get("/exercises/{exercise_id}", response_model=ExerciseResponse)
async def get_exercise(
    exercise_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    result = await db.execute(
        select(Exercise).where(Exercise.id == exercise_id)
    )
    exercise = result.scalar_one_or_none()
    if not exercise:
        raise HTTPException(status_code=404, detail="Ejercicio no encontrado")
    return exercise


# ============================================================
# WORKOUT PLANS
# ============================================================
@router.get("/plans", response_model=list[WorkoutPlanSummary])
async def get_my_plans(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    result = await db.execute(
        select(WorkoutPlan)
        .where(WorkoutPlan.user_id == current_user.id)
        .order_by(desc(WorkoutPlan.created_at))
    )
    return result.scalars().all()


@router.post("/plans", response_model=WorkoutPlanResponse, status_code=201)
async def create_plan(
    data: WorkoutPlanCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    plan = await create_workout_plan(db, current_user.id, data)
    result = await db.execute(
        select(WorkoutPlan)
        .options(
            selectinload(WorkoutPlan.sessions)
            .selectinload(WorkoutSession.exercises)
            .selectinload(SessionExercise.exercise)
        )
        .where(WorkoutPlan.id == plan.id)
    )
    return result.scalar_one()


@router.get("/plans/{plan_id}", response_model=WorkoutPlanResponse)
async def get_plan(
    plan_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    result = await db.execute(
        select(WorkoutPlan)
        .options(
            selectinload(WorkoutPlan.sessions)
            .selectinload(WorkoutSession.exercises)
            .selectinload(SessionExercise.exercise)
        )
        .where(
            WorkoutPlan.id == plan_id,
            WorkoutPlan.user_id == current_user.id
        )
    )
    plan = result.scalar_one_or_none()
    if not plan:
        raise HTTPException(status_code=404, detail="Plan no encontrado")
    return plan


@router.delete("/plans/{plan_id}", status_code=204)
async def delete_plan(
    plan_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    result = await db.execute(
        select(WorkoutPlan).where(
            WorkoutPlan.id == plan_id,
            WorkoutPlan.user_id == current_user.id
        )
    )
    plan = result.scalar_one_or_none()
    if not plan:
        raise HTTPException(status_code=404, detail="Plan no encontrado")
    await db.delete(plan)
    await db.commit()


# ============================================================
# WORKOUT LOGS (entrenamientos completados)
# ============================================================
@router.get("/logs", response_model=list[WorkoutLogResponse])
async def get_my_logs(
    limit: int = 20,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    result = await db.execute(
        select(WorkoutLog)
        .options(
            selectinload(WorkoutLog.set_logs)
            .selectinload(SetLog.exercise)
        )
        .where(WorkoutLog.user_id == current_user.id)
        .order_by(desc(WorkoutLog.started_at))
        .limit(limit)
    )
    return result.scalars().all()


@router.post("/logs", response_model=WorkoutLogResponse, status_code=201)
async def start_workout(
    data: WorkoutLogCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    log = WorkoutLog(
        id=str(uuid.uuid4()),
        user_id=current_user.id,
        session_id=data.session_id,
        started_at=data.started_at,
        notes=data.notes,
    )
    db.add(log)
    await db.commit()

    # Recargar con selectinload para evitar lazy loading
    result = await db.execute(
        select(WorkoutLog)
        .options(
            selectinload(WorkoutLog.set_logs)
            .selectinload(SetLog.exercise)
        )
        .where(WorkoutLog.id == log.id)
    )
    return result.scalar_one()


@router.put("/logs/{log_id}", response_model=WorkoutLogResponse)
async def finish_workout(
    log_id: str,
    data: WorkoutLogUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    result = await db.execute(
        select(WorkoutLog).where(
            WorkoutLog.id == log_id,
            WorkoutLog.user_id == current_user.id
        )
    )
    log = result.scalar_one_or_none()
    if not log:
        raise HTTPException(status_code=404, detail="Entrenamiento no encontrado")

    update_data = data.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(log, field, value)

    await db.commit()
    await db.refresh(log)
    return log


# ============================================================
# SET LOGS (series individuales)
# ============================================================
@router.post("/logs/{log_id}/sets", response_model=SetLogResponse, status_code=201)
async def log_set(
    log_id: str,
    data: SetLogCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    # Verificar que el log pertenece al usuario
    result = await db.execute(
        select(WorkoutLog).where(
            WorkoutLog.id == log_id,
            WorkoutLog.user_id == current_user.id
        )
    )
    if not result.scalar_one_or_none():
        raise HTTPException(status_code=404, detail="Entrenamiento no encontrado")

    # Comprobar si es PR
    is_pr = await check_and_mark_pr(
        db, current_user.id, data.exercise_id, data.weight_kg, data.reps
    )

    set_log = SetLog(
        id=str(uuid.uuid4()),
        log_id=log_id,
        exercise_id=data.exercise_id,
        set_number=data.set_number,
        reps=data.reps,
        weight_kg=data.weight_kg,
        rpe=data.rpe,
        pain_notes=data.pain_notes,
        is_pr=is_pr,
    )
    db.add(set_log)
    await db.commit()

    result = await db.execute(
        select(SetLog)
        .options(selectinload(SetLog.exercise))
        .where(SetLog.id == set_log.id)
    )
    return result.scalar_one()


# ============================================================
# PRs (Personal Records)
# ============================================================
@router.get("/prs", response_model=list[PRResponse])
async def get_prs(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    result = await db.execute(
        select(SetLog, Exercise)
        .join(Exercise, SetLog.exercise_id == Exercise.id)
        .join(WorkoutLog, SetLog.log_id == WorkoutLog.id)
        .where(
            WorkoutLog.user_id == current_user.id,
            SetLog.is_pr == True
        )
        .order_by(desc(SetLog.logged_at))
    )
    rows = result.all()
    return [
        PRResponse(
            exercise_id=row.SetLog.exercise_id,
            exercise_name=row.Exercise.name,
            weight_kg=float(row.SetLog.weight_kg),
            reps=row.SetLog.reps,
            logged_at=row.SetLog.logged_at,
        )
        for row in rows
    ]