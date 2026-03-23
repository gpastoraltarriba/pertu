import uuid
from typing import Optional, List
from sqlalchemy import String, Boolean, Text, Integer, ForeignKey, Enum as SAEnum, Numeric
from sqlalchemy.dialects.postgresql import UUID, ARRAY
from sqlalchemy.orm import Mapped, mapped_column, relationship
from datetime import datetime, date
from sqlalchemy import DateTime, Date
from app.database import Base
from app.models.base import TimestampMixin
import enum


class EquipmentCategory(str, enum.Enum):
    FREE_WEIGHTS = "free_weights"
    MACHINES = "machines"
    CARDIO = "cardio"
    FUNCTIONAL = "functional"
    ACCESSORIES = "accessories"


class MembershipStatus(str, enum.Enum):
    ACTIVE = "active"
    EXPIRED = "expired"
    SUSPENDED = "suspended"
    PENDING = "pending"


class Gym(Base, TimestampMixin):
    __tablename__ = "gyms"

    id: Mapped[str] = mapped_column(
        UUID(as_uuid=False), primary_key=True, default=lambda: str(uuid.uuid4())
    )
    owner_id: Mapped[str] = mapped_column(
        UUID(as_uuid=False), ForeignKey("users.id", ondelete="CASCADE"), nullable=False
    )
    name: Mapped[str] = mapped_column(String(200), nullable=False)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    address: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)
    city: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    phone: Mapped[Optional[str]] = mapped_column(String(30), nullable=True)
    logo_url: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    stripe_account_id: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)

    # Relationships
    owner: Mapped["User"] = relationship(foreign_keys=[owner_id])
    equipment: Mapped[List["GymEquipment"]] = relationship(
        back_populates="gym", cascade="all, delete-orphan"
    )
    memberships: Mapped[List["GymMembership"]] = relationship(
        back_populates="gym", cascade="all, delete-orphan"
    )

    def __repr__(self):
        return f"<Gym {self.name}>"


class GymEquipment(Base, TimestampMixin):
    __tablename__ = "gym_equipment"

    id: Mapped[str] = mapped_column(
        UUID(as_uuid=False), primary_key=True, default=lambda: str(uuid.uuid4())
    )
    gym_id: Mapped[str] = mapped_column(
        UUID(as_uuid=False), ForeignKey("gyms.id", ondelete="CASCADE"), nullable=False
    )
    name: Mapped[str] = mapped_column(String(200), nullable=False)
    category: Mapped[EquipmentCategory] = mapped_column(
        SAEnum(EquipmentCategory), nullable=False
    )
    muscle_groups: Mapped[Optional[List[str]]] = mapped_column(ARRAY(Text), nullable=True)
    quantity: Mapped[int] = mapped_column(Integer, default=1, nullable=False)
    photo_url: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    notes: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    is_available: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)

    gym: Mapped["Gym"] = relationship(back_populates="equipment")


class GymMembership(Base, TimestampMixin):
    __tablename__ = "gym_memberships"

    id: Mapped[str] = mapped_column(
        UUID(as_uuid=False), primary_key=True, default=lambda: str(uuid.uuid4())
    )
    gym_id: Mapped[str] = mapped_column(
        UUID(as_uuid=False), ForeignKey("gyms.id", ondelete="CASCADE"), nullable=False
    )
    user_id: Mapped[str] = mapped_column(
        UUID(as_uuid=False), ForeignKey("users.id", ondelete="CASCADE"), nullable=False
    )
    plan_name: Mapped[str] = mapped_column(String(100), nullable=False)
    price: Mapped[float] = mapped_column(Numeric(10, 2), nullable=False)
    status: Mapped[MembershipStatus] = mapped_column(
        SAEnum(MembershipStatus), default=MembershipStatus.ACTIVE, nullable=False
    )
    start_date: Mapped[date] = mapped_column(Date, nullable=False)
    end_date: Mapped[Optional[date]] = mapped_column(Date, nullable=True)
    last_payment_date: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
    next_payment_date: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
    stripe_sub_id: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)

    gym: Mapped["Gym"] = relationship(back_populates="memberships")
    user: Mapped["User"] = relationship(foreign_keys=[user_id])


class TrainerClient(Base, TimestampMixin):
    __tablename__ = "trainer_clients"

    id: Mapped[str] = mapped_column(
        UUID(as_uuid=False), primary_key=True, default=lambda: str(uuid.uuid4())
    )
    trainer_id: Mapped[str] = mapped_column(
        UUID(as_uuid=False), ForeignKey("users.id", ondelete="CASCADE"), nullable=False
    )
    client_id: Mapped[str] = mapped_column(
        UUID(as_uuid=False), ForeignKey("users.id", ondelete="CASCADE"), nullable=False
    )
    status: Mapped[str] = mapped_column(
        SAEnum("active", "inactive", "pending", name="trainer_client_status"),
        default="active", nullable=False
    )
    notes: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    trainer: Mapped["User"] = relationship(foreign_keys=[trainer_id])
    client: Mapped["User"] = relationship(foreign_keys=[client_id])