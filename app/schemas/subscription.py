import uuid
from datetime import datetime

from app.models.subscription import SubscriptionBase, SubscriptionStatus


class SubscriptionCreate(SubscriptionBase):
    tier_id: uuid.UUID


class SubscriptionRead(SubscriptionBase):
    id: uuid.UUID
    supporter_id: uuid.UUID
    tier_id: uuid.UUID
    status: SubscriptionStatus
    started_at: datetime | None
    expires_at: datetime | None
    created_at: datetime | None
    updated_at: datetime | None
