import datetime
import uuid

from sqlalchemy import TEXT, Column, DateTime, func
from sqlmodel import Field, SQLModel


class TierBase(SQLModel):
    name: str = Field(index=True, max_length=100)
    description: TEXT | None = Field(default=None, sa_column=Column(TEXT))
    price: float = Field(default=None, ge=0.0)


class Tier(TierBase, table=True):
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    creator_id: uuid.UUID = Field(index=True, nullable=False)
    created_at: datetime.datetime | None = Field(
        sa_column = Column(
            DateTime(timezone=True), server_default=func.now()
        ),
    )
    updated_at: datetime.datetime | None = Field(
        sa_column=Column(
            DateTime(timezone=True), server_factory=func.now(), onupdate=func.now()
        ),
    )
