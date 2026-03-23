import uuid
from typing import Optional, List
from datetime import datetime
from sqlalchemy import String, Boolean, Text, Integer, ForeignKey, Enum as SAEnum, Numeric, DateTime
from sqlalchemy.dialects.postgresql import UUID, ARRAY, JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.database import Base
from app.models.base import TimestampMixin
import enum


class WorkoutSource(str, enum.Enum):
    AI = "ai"
    TRAINER = "trainer"
    USER = "user"


class ExerciseDifficulty(str, enum.Enum):
    BEGINNER = "beginner"
    INTERMEDIATE = "intermediate"
    ADVANCED = "advanced"


class Exercise(Base):
    __tablename__ = "exercises"

    id: Mapped[str] = mapped_column(
        UUID(as_uuid=False), primary_key=True, default=lambda: str(uuid.uuid4())
    )
    name: Mapped[str] = mapped_column(String(200), nullable=False)
    muscle_primary: Mapped[str] = mapped_column(String(100), nullable=False)
    muscle_secondary: Mapped[Optional[List[str]]] = mapped_column(ARRAY(Text), nullable=True)
    equipment_type: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    difficulty: Mapped[ExerciseDifficulty] = mapped_column(
        SAEnum(ExerciseDifficulty), nullable=False
    )
    instructions: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    video_url: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    image_url: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    def __repr__(self):
        return f"<Exercise {self.name}>"


class WorkoutPlan(Base, TimestampMixin):
    __tablename__ = "workout_plans"

    id: Mapped[str] = mapped_column(
        UUID(as_uuid=False), primary_key=True, default=lambda: str(uuid.uuid4())
    )
    user_id: Mapped[str] = mapped_column(
        UUID(as_uuid=False), ForeignKey("users.id", ondelete="CASCADE"), nullable=False
    )
    created_by: Mapped[Optional[str]] = mapped_column(
        UUID(as_uuid=False), ForeignKey("users.id", ondelete="SET NULL"), nullable=True
    )
    title: Mapped[str] = mapped_column(String(200), nullable=False)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    source: Mapped[WorkoutSource] = mapped_column(SAEnum(WorkoutSource), nullable=False)
    goal: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    weeks_duration: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    days_per_week: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    is_public: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    ai_prompt_used: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    equipment_ids: Mapped[Optional[List[str]]] = mapped_column(ARRAY(UUID(as_uuid=False)), nullable=True)

    user: Mapped["User"] = relationship(back_populates="workout_plans", foreign_keys=[user_id])
    creator: Mapped[Optional["User"]] = relationship(foreign_keys=[created_by])
    sessions: Mapped[List["WorkoutSession"]] = relationship(
        back_populates="plan", cascade="all, delete-orphan", order_by="WorkoutSession.order_in_plan"
    )


class WorkoutSession(Base):
    __tablename__ = "workout_sessions"

    id: Mapped[str] = mapped_column(
        UUID(as_uuid=False), primary_key=True, default=lambda: str(uuid.uuid4())
    )
    plan_id: Mapped[str] = mapped_column(
        UUID(as_uuid=False), ForeignKey("workout_plans.id", ondelete="CASCADE"), nullable=False
    )
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    day_of_week: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)  # 0=Mon, 6=Sun
    order_in_plan: Mapped[int] = mapped_column(Integer, nullable=False)
    estimated_duration_min: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    notes: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    plan: Mapped["WorkoutPlan"] = relationship(back_populates="sessions")
    exercises: Mapped[List["SessionExercise"]] = relationship(
        back_populates="session", cascade="all, delete-orphan", order_by="SessionExercise.order"
    )


class SessionExercise(Base):
    __tablename__ = "session_exercises"

    id: Mapped[str] = mapped_column(
        UUID(as_uuid=False), primary_key=True, default=lambda: str(uuid.uuid4())
    )
    session_id: Mapped[str] = mapped_column(
        UUID(as_uuid=False), ForeignKey("workout_sessions.id", ondelete="CASCADE"), nullable=False
    )
    exercise_id: Mapped[str] = mapped_column(
        UUID(as_uuid=False), ForeignKey("exercises.id"), nullable=False
    )
    order: Mapped[int] = mapped_column(Integer, nullable=False)
    sets: Mapped[int] = mapped_column(Integer, nullable=False)
    reps_min: Mapped[int] = mapped_column(Integer, nullable=False)
    reps_max: Mapped[int] = mapped_column(Integer, nullable=False)
    rest_seconds: Mapped[int] = mapped_column(Integer, default=90, nullable=False)
    notes: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    rir: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)  # Reps In Reserve

    session: Mapped["WorkoutSession"] = relationship(back_populates="exercises")
    exercise: Mapped["Exercise"] = relationship()


class WorkoutLog(Base, TimestampMixin):
    __tablename__ = "workout_logs"

    id: Mapped[str] = mapped_column(
        UUID(as_uuid=False), primary_key=True, default=lambda: str(uuid.uuid4())
    )
    user_id: Mapped[str] = mapped_column(
        UUID(as_uuid=False), ForeignKey("users.id", ondelete="CASCADE"), nullable=False
    )
    session_id: Mapped[Optional[str]] = mapped_column(
        UUID(as_uuid=False), ForeignKey("workout_sessions.id", ondelete="SET NULL"), nullable=True
    )
    started_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    finished_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    duration_min: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    overall_feeling: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)  # 1-10
    notes: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    user: Mapped["User"] = relationship(back_populates="workout_logs")
    session: Mapped[Optional["WorkoutSession"]] = relationship()
    set_logs: Mapped[List["SetLog"]] = relationship(
        back_populates="workout_log", cascade="all, delete-orphan"
    )


class SetLog(Base):
    __tablename__ = "set_logs"

    id: Mapped[str] = mapped_column(
        UUID(as_uuid=False), primary_key=True, default=lambda: str(uuid.uuid4())
    )
    log_id: Mapped[str] = mapped_column(
        UUID(as_uuid=False), ForeignKey("workout_logs.id", ondelete="CASCADE"), nullable=False
    )
    exercise_id: Mapped[str] = mapped_column(
        UUID(as_uuid=False), ForeignKey("exercises.id"), nullable=False
    )
    set_number: Mapped[int] = mapped_column(Integer, nullable=False)
    reps: Mapped[int] = mapped_column(Integer, nullable=False)
    weight_kg: Mapped[float] = mapped_column(Numeric(6, 2), nullable=False)
    rpe: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    pain_notes: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    is_pr: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    logged_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default="now()", nullable=False
    )

    workout_log: Mapped["WorkoutLog"] = relationship(back_populates="set_logs")
    exercise: Mapped["Exercise"] = relationship()