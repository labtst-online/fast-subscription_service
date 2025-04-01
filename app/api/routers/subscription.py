import logging

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.dependencies import CurrentUserUUID
from app.core.database import get_async_session
from app.schemas.subscription import SubscriptionCreate, SubscriptionRead

logger = logging.getLogger(__name__)
router = APIRouter()


router.post(
    "/subscriptions",
    response_model=SubscriptionRead,
    summary="Create a new subscription",
    description="Create a new subscription with the specified details.",
)
async def create_new_subscription(
    subscription_create: SubscriptionCreate,
    supporter_id: CurrentUserUUID = Depends(CurrentUserUUID),
    session: AsyncSession = Depends(get_async_session),
):
    pass


@router.get(
    "/users/{user_id}/subscriptions",
    response_model=list[SubscriptionRead],
    summary="Get all subscriptions for a user",
    description="Retrieve all subscriptions for a specific user.",
)
async def get_user_subscriptions(
    user_id: str,
    session: AsyncSession = Depends(get_async_session),
    current_user: CurrentUserUUID = Depends(CurrentUserUUID),
):
    pass
