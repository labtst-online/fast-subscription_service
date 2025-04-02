import datetime
import logging
import uuid
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession
from sqlmodel import select

from app.api.dependencies import CurrentUserUUID
from app.core.database import get_async_session
from app.models.subscription import Subscription, SubscriptionStatus
from app.models.tier import Tier
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
    logger.info(
        f"User {supporter_id} attempting to subscribe to tier: {subscription_create.tier_id}"
    )
    tier_statement = select(Tier).where(Tier.id == subscription_create.tier_id)
    tier_result = await session.execute(tier_statement)
    tier = tier_result.scalar_one_or_none()

    if not tier:
        logger.info(f"Tier not found: {subscription_create.tier_id}")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Tier not found"
        )

    creator_id = tier.creator_id
    # Prevent self-subscription
    if creator_id == supporter_id:
        logger.info(f"User {supporter_id} attempted to self-subscribe to tier {tier.id}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot subscribe to your own tier"
        )

    # Prevent multiple active subscription to the same creator
    existing_sub_statement = (
        select(Subscription.id)
        .join(Tier, Subscription.tier_id == Tier.id)
        .where(Subscription.supporter_id == supporter_id)
        .where(Tier.creator_id == creator_id)
        .where(Subscription.status == SubscriptionStatus.ACTIVE)
        .where(Subscription.expires_at > datetime.datetime.now())
        .limit(1)
    )
    existing_sub_result = await session.execute(existing_sub_statement)
    existing_sub = existing_sub_result.scalar_one_or_none

    if existing_sub:
        logger.info(f"User {supporter_id} already actively subscribed to creator {creator_id}")
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Already actively subscription to this creator"
        )
    logger.info(f"Creating new subscription with supporter_id: {supporter_id}")
    db_subscription = Subscription(
        supporter_id=supporter_id,
        tier_id=subscription_create.tier_id,
        status=SubscriptionStatus.ACTIVE,
        started_at=datetime.datetime.now(datetime.UTC),
        expires_at=datetime.datetime.now(datetime.UTC) + datetime.timedelta(days=30)
    )
    await session.add(db_subscription)
    sub_to_return = db_subscription

    try:
        await session.commit()
        await session.refresh(db_subscription)
        logger.info(f"Successfully committed subscription changes for tier_id: {sub_to_return.id}")
        return sub_to_return
    except IntegrityError:
        await session.rollback()
        logger.error(f"Integrity error for tier_id: {sub_to_return.id}")
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Content potentially already exists or data conflict."
        )
    except Exception as e:
        await session.rollback()
        logger.exception(f"Error saving content for tier_id: {sub_to_return.id} - {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Could not save content"
        )


@router.get(
    "/users/{user_id}/subscriptions",
    response_model=list[SubscriptionRead],
    summary="Get all subscriptions for a user",
    description="Retrieve all subscriptions for a specific user.",
)
async def get_user_subscriptions(
    user_id: uuid.UUID,
    limit: Annotated[int, Query(ge=1, le=50)] = 20,
    offset: Annotated[int, Query(ge=0)] = 0,
    session: AsyncSession = Depends(get_async_session),
):
    statement = (
        select(Subscription)
        .where(Subscription.supporter_id == user_id)
        .order_by(Subscription.expires_at.desc())
        .offset(offset)
        .limit(limit)
    )
    result = await session.execute(statement)
    subscriptions = result.scalars().all()

    logger.info(f"Retrieved {len(subscriptions)} subscriptions for user_id: {user_id}")
    return subscriptions
