from pydantic import BaseModel
from typing import Optional, List
from app.models.user import UserRole, FitnessGoal, FitnessLevel, DietPreference


class UpdateUserRequest(BaseModel):
    name: Optional[str] = None
    avatar_url: Optional[str] = None


class UserProfileUpdate(BaseModel):
    age: Optional[int] = None
    weight_kg: Optional[float] = None
    height_cm: Optional[int] = None
    goal: Optional[FitnessGoal] = None
    fitness_level: Optional[FitnessLevel] = None
    available_days: Optional[int] = None
    session_duration_min: Optional[int] = None
    diet_preference: Optional[DietPreference] = None
    injuries: Optional[List[str]] = None
    allergies: Optional[List[str]] = None
    bio: Optional[str] = None
    is_public: Optional[bool] = None


class UserProfileResponse(BaseModel):
    id: str
    age: Optional[int] = None
    weight_kg: Optional[float] = None
    height_cm: Optional[int] = None
    goal: Optional[str] = None
    fitness_level: Optional[str] = None
    available_days: Optional[int] = None
    session_duration_min: Optional[int] = None
    diet_preference: Optional[str] = None
    injuries: Optional[List[str]] = None
    allergies: Optional[List[str]] = None
    bio: Optional[str] = None
    is_public: bool = True

    class Config:
        from_attributes = True


class UserPublicResponse(BaseModel):
    id: str
    name: str
    username: str
    avatar_url: Optional[str] = None
    role: str
    bio: Optional[str] = None

    class Config:
        from_attributes = True