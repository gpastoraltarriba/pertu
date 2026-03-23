import uuid
from typing import Optional, List
from datetime import datetime, date
from sqlalchemy import String, Boolean, Text, Integer, ForeignKey, Enum as SAEnum, Numeric, DateTime, Date
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.database import Base
from app.models.base import TimestampMixin
import enum


class MealType(str, enum.Enum):
    BREAKFAST = "breakfast"
    LUNCH = "lunch"
    DINNER = "dinner"
    SNACK = "snack"


class FoodSource(str, enum.Enum):
    MANUAL = "manual"
    AI_PHOTO = "ai_photo"
    AI_TEXT = "ai_text"
    BARCODE = "barcode"


class DietPlan(Base, TimestampMixin):
    __tablename__ = "diet_plans"

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
    source: Mapped[str] = mapped_column(
        SAEnum("ai", "trainer", "user", name="diet_source"), nullable=False
    )
    target_calories: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    target_protein_g: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    target_carbs_g: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    target_fat_g: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    is_public: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    days_data: Mapped[Optional[dict]] = mapped_column(JSONB, nullable=True)  # estructura flexible

    user: Mapped["User"] = relationship(foreign_keys=[user_id])
    creator: Mapped[Optional["User"]] = relationship(foreign_keys=[created_by])


class MealLog(Base):
    __tablename__ = "meal_logs"

    id: Mapped[str] = mapped_column(
        UUID(as_uuid=False), primary_key=True, default=lambda: str(uuid.uuid4())
    )
    user_id: Mapped[str] = mapped_column(
        UUID(as_uuid=False), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True
    )
    logged_date: Mapped[date] = mapped_column(Date, nullable=False, index=True)
    meal_type: Mapped[MealType] = mapped_column(SAEnum(MealType), nullable=False)
    name: Mapped[str] = mapped_column(String(300), nullable=False)
    calories: Mapped[float] = mapped_column(Numeric(8, 2), nullable=False)
    protein_g: Mapped[float] = mapped_column(Numeric(6, 2), nullable=False, default=0)
    carbs_g: Mapped[float] = mapped_column(Numeric(6, 2), nullable=False, default=0)
    fat_g: Mapped[float] = mapped_column(Numeric(6, 2), nullable=False, default=0)
    source: Mapped[FoodSource] = mapped_column(SAEnum(FoodSource), nullable=False)
    photo_url: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    ai_confidence: Mapped[Optional[float]] = mapped_column(Numeric(3, 2), nullable=True)
    logged_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default="now()", nullable=False
    )

    user: Mapped["User"] = relationship(back_populates="meal_logs")


class BodyMeasurement(Base):
    __tablename__ = "body_measurements"

    id: Mapped[str] = mapped_column(
        UUID(as_uuid=False), primary_key=True, default=lambda: str(uuid.uuid4())
    )
    user_id: Mapped[str] = mapped_column(
        UUID(as_uuid=False), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True
    )
    weight_kg: Mapped[Optional[float]] = mapped_column(Numeric(5, 2), nullable=True)
    body_fat_pct: Mapped[Optional[float]] = mapped_column(Numeric(4, 1), nullable=True)
    muscle_mass_kg: Mapped[Optional[float]] = mapped_column(Numeric(5, 2), nullable=True)
    waist_cm: Mapped[Optional[float]] = mapped_column(Numeric(5, 1), nullable=True)
    chest_cm: Mapped[Optional[float]] = mapped_column(Numeric(5, 1), nullable=True)
    arms_cm: Mapped[Optional[float]] = mapped_column(Numeric(5, 1), nullable=True)
    photo_url: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    measured_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)

    user: Mapped["User"] = relationship(back_populates="body_measurements")


class Product(Base, TimestampMixin):
    __tablename__ = "products"

    id: Mapped[str] = mapped_column(
        UUID(as_uuid=False), primary_key=True, default=lambda: str(uuid.uuid4())
    )
    seller_id: Mapped[str] = mapped_column(
        UUID(as_uuid=False), ForeignKey("users.id", ondelete="CASCADE"), nullable=False
    )
    title: Mapped[str] = mapped_column(String(300), nullable=False)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    type: Mapped[str] = mapped_column(
        SAEnum("physical", "digital_plan", "course", "service", name="product_type"),
        nullable=False
    )
    price: Mapped[float] = mapped_column(Numeric(10, 2), nullable=False)
    currency: Mapped[str] = mapped_column(String(3), default="EUR", nullable=False)
    stripe_price_id: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    stock: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)  # NULL = ilimitado
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)

    seller: Mapped["User"] = relationship(foreign_keys=[seller_id])