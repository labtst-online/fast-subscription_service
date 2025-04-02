import datetime
import enum
import uuid

from sqlalchemy import Column, DateTime, Enum, func
from sqlmodel import Field, SQLModel


class SubscriptionStatus(enum.Enum):
    ACTIVE = "active"
    INACTIVE = "inactive"
    PENDING = "pending"
    CANCELLED = "cancelled"


class SubscriptionBase(SQLModel):
    pass


class Subscription(SubscriptionBase, table=True):
    __tablename__ = "subscription"
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    supporter_id: uuid.UUID = Field(index=True, nullable=False)
    tier_id: uuid.UUID = Field(index=True, foreign_key="tier.id")
    status: str = Field(
        sa_column=Column(
            Enum(SubscriptionStatus)
        )
    )
    started_at: datetime.datetime | None = Field(
        sa_column = Column(
            DateTime(timezone=True), nullable=False, server_default=func.now()
        )
    )
    expires_at: datetime.datetime | None = Field(
        sa_column = Column(
            DateTime(timezone=True), nullable=False, server_default=func.now()
        )
    )
    created_at: datetime.datetime | None = Field(
        sa_column=Column(
            DateTime(timezone=True), nullable=False, server_default=func.now()
        )
    )
    updated_at: datetime.datetime | None = Field(
        sa_column=Column(
            DateTime(timezone=True), nullable=False, server_default=func.now(), onupdate=func.now()
        )
    )
