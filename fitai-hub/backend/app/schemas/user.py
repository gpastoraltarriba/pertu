from pydantic import BaseModel, EmailStr
from typing import Optional, List
from app.models.user import UserRole, FitnessGoal, FitnessLevel, DietPreference


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
    age: Optional[int]
    weight_kg: Optional[float]
    height_cm: Optional[int]
    goal: Optional[str]
    fitness_level: Optional[str]
    available_days: Optional[int]
    session_duration_min: Optional[int]
    diet_preference: Optional[str]
    injuries: Optional[List[str]]
    allergies: Optional[List[str]]
    bio: Optional[str]
    is_public: bool

    class Config:
        from_attributes = True


class UserPublicResponse(BaseModel):
    id: str
    name: str
    username: str
    avatar_url: Optional[str]
    role: str
    bio: Optional[str] = None

    class Config:
        from_attributes = True