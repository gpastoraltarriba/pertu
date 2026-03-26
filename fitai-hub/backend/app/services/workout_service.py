from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from app.models.workout import (
    WorkoutPlan, WorkoutSession, SessionExercise,
    WorkoutLog, SetLog, Exercise
)
from app.schemas.workout import WorkoutPlanCreate
import uuid
from datetime import datetime, timezone


async def create_workout_plan(
    db: AsyncSession,
    user_id: str,
    data: WorkoutPlanCreate,
    source: str = "user",
    created_by: str = None,
) -> WorkoutPlan:
    plan = WorkoutPlan(
        id=str(uuid.uuid4()),
        user_id=user_id,
        created_by=created_by,
        title=data.title,
        description=data.description,
        source=source,
        goal=data.goal,
        weeks_duration=data.weeks_duration,
        days_per_week=data.days_per_week,
        is_active=True,
        is_public=data.is_public,
    )
    db.add(plan)
    await db.flush()

    for session_data in data.sessions:
        session = WorkoutSession(
            id=str(uuid.uuid4()),
            plan_id=plan.id,
            name=session_data.name,
            day_of_week=session_data.day_of_week,
            order_in_plan=session_data.order_in_plan,
            estimated_duration_min=session_data.estimated_duration_min,
            notes=session_data.notes,
        )
        db.add(session)
        await db.flush()

        for ex_data in session_data.exercises:
            session_ex = SessionExercise(
                id=str(uuid.uuid4()),
                session_id=session.id,
                exercise_id=ex_data.exercise_id,
                order=ex_data.order,
                sets=ex_data.sets,
                reps_min=ex_data.reps_min,
                reps_max=ex_data.reps_max,
                rest_seconds=ex_data.rest_seconds,
                notes=ex_data.notes,
                rir=ex_data.rir,
            )
            db.add(session_ex)

    await db.commit()
    await db.refresh(plan)
    return plan


async def check_and_mark_pr(
    db: AsyncSession,
    user_id: str,
    exercise_id: str,
    weight_kg: float,
    reps: int,
) -> bool:
    """Comprueba si el set es un PR y lo marca automáticamente."""
    result = await db.execute(
        select(func.max(SetLog.weight_kg))
        .join(WorkoutLog)
        .where(
            WorkoutLog.user_id == user_id,
            SetLog.exercise_id == exercise_id,
        )
    )
    max_weight = result.scalar()
    return max_weight is None or weight_kg > max_weight