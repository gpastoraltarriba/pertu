from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime
import enum


class WorkoutSourceEnum(str, enum.Enum):
    AI = "ai"
    TRAINER = "trainer"
    USER = "user"


# --- EXERCISES ---
class ExerciseResponse(BaseModel):
    id: str
    name: str
    muscle_primary: str
    muscle_secondary: Optional[List[str]] = None
    equipment_type: Optional[str] = None
    difficulty: str
    instructions: Optional[str] = None
    video_url: Optional[str] = None
    image_url: Optional[str] = None

    class Config:
        from_attributes = True


# --- SESSION EXERCISES ---
class SessionExerciseCreate(BaseModel):
    exercise_id: str
    order: int
    sets: int
    reps_min: int
    reps_max: int
    rest_seconds: int = 90
    notes: Optional[str] = None
    rir: Optional[int] = None


class SessionExerciseResponse(BaseModel):
    id: str
    exercise_id: str
    order: int
    sets: int
    reps_min: int
    reps_max: int
    rest_seconds: int
    notes: Optional[str] = None
    rir: Optional[int] = None
    exercise: Optional[ExerciseResponse] = None

    class Config:
        from_attributes = True


# --- WORKOUT SESSIONS ---
class WorkoutSessionCreate(BaseModel):
    name: str
    day_of_week: Optional[int] = None
    order_in_plan: int
    estimated_duration_min: Optional[int] = None
    notes: Optional[str] = None
    exercises: List[SessionExerciseCreate] = []


class WorkoutSessionResponse(BaseModel):
    id: str
    name: str
    day_of_week: Optional[int] = None
    order_in_plan: int
    estimated_duration_min: Optional[int] = None
    notes: Optional[str] = None
    exercises: List[SessionExerciseResponse] = []

    class Config:
        from_attributes = True


# --- WORKOUT PLANS ---
class WorkoutPlanCreate(BaseModel):
    title: str
    description: Optional[str] = None
    goal: Optional[str] = None
    weeks_duration: Optional[int] = None
    days_per_week: Optional[int] = None
    is_public: bool = False
    sessions: List[WorkoutSessionCreate] = []


class WorkoutPlanResponse(BaseModel):
    id: str
    title: str
    description: Optional[str] = None
    source: str
    goal: Optional[str] = None
    weeks_duration: Optional[int] = None
    days_per_week: Optional[int] = None
    is_active: bool
    is_public: bool
    created_at: datetime
    sessions: List[WorkoutSessionResponse] = []

    class Config:
        from_attributes = True


class WorkoutPlanSummary(BaseModel):
    id: str
    title: str
    source: str
    goal: Optional[str] = None
    weeks_duration: Optional[int] = None
    days_per_week: Optional[int] = None
    is_active: bool
    is_public: bool
    created_at: datetime

    class Config:
        from_attributes = True


# --- SET LOGS ---
class SetLogCreate(BaseModel):
    exercise_id: str
    set_number: int
    reps: int
    weight_kg: float
    rpe: Optional[int] = None
    pain_notes: Optional[str] = None


class SetLogResponse(BaseModel):
    id: str
    exercise_id: str
    set_number: int
    reps: int
    weight_kg: float
    rpe: Optional[int] = None
    pain_notes: Optional[str] = None
    is_pr: bool
    logged_at: datetime
    exercise: Optional[ExerciseResponse] = None

    class Config:
        from_attributes = True


# --- WORKOUT LOGS ---
class WorkoutLogCreate(BaseModel):
    session_id: Optional[str] = None
    started_at: datetime
    notes: Optional[str] = None


class WorkoutLogUpdate(BaseModel):
    finished_at: Optional[datetime] = None
    duration_min: Optional[int] = None
    overall_feeling: Optional[int] = None
    notes: Optional[str] = None


class WorkoutLogResponse(BaseModel):
    id: str
    session_id: Optional[str] = None
    started_at: datetime
    finished_at: Optional[datetime] = None
    duration_min: Optional[int] = None
    overall_feeling: Optional[int] = None
    notes: Optional[str] = None
    set_logs: List[SetLogResponse] = []

    class Config:
        from_attributes = True


# --- PRs ---
class PRResponse(BaseModel):
    exercise_id: str
    exercise_name: str
    weight_kg: float
    reps: int
    logged_at: datetime