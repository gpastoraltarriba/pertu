import uuid
from datetime import datetime
from typing import Optional, List
from sqlalchemy import String, Boolean, DateTime, ForeignKey, Enum as SAEnum, Integer, Text
from sqlalchemy.dialects.postgresql import UUID, ARRAY
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.database import Base
from app.models.base import TimestampMixin
import enum


class UserRole(str, enum.Enum):
    FREE = "free"
    PRO = "pro"
    TRAINER = "trainer"
    GYM = "gym"


class OAuthProvider(str, enum.Enum):
    GOOGLE = "google"
    FACEBOOK = "facebook"


class FitnessGoal(str, enum.Enum):
    LOSE_WEIGHT = "lose_weight"
    GAIN_MUSCLE = "gain_muscle"
    MAINTAIN = "maintain"
    ENDURANCE = "endurance"
    FLEXIBILITY = "flexibility"


class FitnessLevel(str, enum.Enum):
    BEGINNER = "beginner"
    INTERMEDIATE = "intermediate"
    ADVANCED = "advanced"


class DietPreference(str, enum.Enum):
    OMNIVORE = "omnivore"
    VEGETARIAN = "vegetarian"
    VEGAN = "vegan"
    KETO = "keto"
    PALEO = "paleo"


class User(Base, TimestampMixin):
    __tablename__ = "users"

    id: Mapped[str] = mapped_column(
        UUID(as_uuid=False), primary_key=True, default=lambda: str(uuid.uuid4())
    )
    email: Mapped[str] = mapped_column(String(255), unique=True, nullable=False, index=True)
    password_hash: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    username: Mapped[str] = mapped_column(String(50), unique=True, nullable=False, index=True)
    avatar_url: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    role: Mapped[UserRole] = mapped_column(
        SAEnum(UserRole), default=UserRole.FREE, nullable=False
    )
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    is_verified: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    stripe_customer_id: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)

    # Relationships
    profile: Mapped[Optional["UserProfile"]] = relationship(
        back_populates="user", uselist=False, cascade="all, delete-orphan"
    )
    oauth_accounts: Mapped[List["OAuthAccount"]] = relationship(
        back_populates="user", cascade="all, delete-orphan"
    )
    subscription: Mapped[Optional["Subscription"]] = relationship(
        back_populates="user", uselist=False, cascade="all, delete-orphan"
    )
    workout_plans: Mapped[List["WorkoutPlan"]] = relationship(
        back_populates="user", foreign_keys="WorkoutPlan.user_id"
    )
    workout_logs: Mapped[List["WorkoutLog"]] = relationship(back_populates="user")
    meal_logs: Mapped[List["MealLog"]] = relationship(back_populates="user")
    body_measurements: Mapped[List["BodyMeasurement"]] = relationship(back_populates="user")

    # Social
    following: Mapped[List["Follow"]] = relationship(
        foreign_keys="Follow.follower_id", back_populates="follower"
    )
    followers: Mapped[List["Follow"]] = relationship(
        foreign_keys="Follow.following_id", back_populates="following"
    )

    def __repr__(self):
        return f"<User {self.username} ({self.role})>"


class OAuthAccount(Base, TimestampMixin):
    __tablename__ = "oauth_accounts"

    id: Mapped[str] = mapped_column(
        UUID(as_uuid=False), primary_key=True, default=lambda: str(uuid.uuid4())
    )
    user_id: Mapped[str] = mapped_column(
        UUID(as_uuid=False), ForeignKey("users.id", ondelete="CASCADE"), nullable=False
    )
    provider: Mapped[OAuthProvider] = mapped_column(SAEnum(OAuthProvider), nullable=False)
    provider_user_id: Mapped[str] = mapped_column(String(255), nullable=False)
    access_token: Mapped[str] = mapped_column(Text, nullable=False)

    user: Mapped["User"] = relationship(back_populates="oauth_accounts")


class UserProfile(Base):
    __tablename__ = "user_profiles"

    id: Mapped[str] = mapped_column(
        UUID(as_uuid=False), primary_key=True, default=lambda: str(uuid.uuid4())
    )
    user_id: Mapped[str] = mapped_column(
        UUID(as_uuid=False), ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False, unique=True
    )
    age: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    weight_kg: Mapped[Optional[float]] = mapped_column(nullable=True)
    height_cm: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    goal: Mapped[Optional[FitnessGoal]] = mapped_column(SAEnum(FitnessGoal), nullable=True)
    fitness_level: Mapped[Optional[FitnessLevel]] = mapped_column(
        SAEnum(FitnessLevel), nullable=True
    )
    available_days: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    session_duration_min: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    diet_preference: Mapped[Optional[DietPreference]] = mapped_column(
        SAEnum(DietPreference), nullable=True
    )
    injuries: Mapped[Optional[List[str]]] = mapped_column(ARRAY(Text), nullable=True)
    allergies: Mapped[Optional[List[str]]] = mapped_column(ARRAY(Text), nullable=True)
    bio: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    is_public: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)

    user: Mapped["User"] = relationship(back_populates="profile")


class Subscription(Base, TimestampMixin):
    __tablename__ = "subscriptions"

    id: Mapped[str] = mapped_column(
        UUID(as_uuid=False), primary_key=True, default=lambda: str(uuid.uuid4())
    )
    user_id: Mapped[str] = mapped_column(
        UUID(as_uuid=False), ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False, unique=True
    )
    stripe_subscription_id: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    plan: Mapped[UserRole] = mapped_column(SAEnum(UserRole), nullable=False)
    status: Mapped[str] = mapped_column(
        SAEnum("active", "past_due", "cancelled", "trialing", name="sub_status"),
        default="active", nullable=False
    )
    current_period_start: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
    current_period_end: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
    cancel_at_period_end: Mapped[bool] = mapped_column(Boolean, default=False)

    user: Mapped["User"] = relationship(back_populates="subscription")


class Follow(Base):
    __tablename__ = "follows"

    follower_id: Mapped[str] = mapped_column(
        UUID(as_uuid=False), ForeignKey("users.id", ondelete="CASCADE"),
        primary_key=True
    )
    following_id: Mapped[str] = mapped_column(
        UUID(as_uuid=False), ForeignKey("users.id", ondelete="CASCADE"),
        primary_key=True
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default="now()", nullable=False
    )

    follower: Mapped["User"] = relationship(foreign_keys=[follower_id], back_populates="following")
    following: Mapped["User"] = relationship(foreign_keys=[following_id], back_populates="followers")