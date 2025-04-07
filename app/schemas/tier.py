import uuid
from datetime import datetime

from app.models.tier import TierBase


class TierCreate(TierBase):
    pass


class TierUpdate(TierBase):
    name: str | None = None
    description: str | None = None
    price: float | None = None
    currency: str | None = None


class TierRead(TierBase):
    id: uuid.UUID
    creator_id: uuid.UUID
    created_at: datetime | None
    updated_at: datetime | None
