from app.models.subscription import SubscriptionBase


class SubscriptionCreate(SubscriptionBase):
    tier_id: str


class SubscriptionRead(SubscriptionBase):
    id: str
    supporter_id: str
    tier_id: str
    status: str
    started_at: str | None = None
    expires_at: str | None = None
    created_at: str | None = None
    updated_at: str | None = None
