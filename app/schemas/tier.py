from app.models.tier import TierBase


class TierCreate(TierBase):
    pass


class TierUpdate(TierBase):
    name: str | None = None
    description: str | None = None
    price: float | None = None


class TierRead(TierBase):
    id: str
    creator_id: str
    created_at: str | None
    updated_at: str | None
