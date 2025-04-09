import datetime
import logging
import uuid
from typing import Annotated

import httpx
from fastapi import APIRouter, Depends, HTTPException, Query, Request, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlmodel import select

from app.api.dependencies import CurrentUserUUID
from app.core.database import get_async_session
from app.models.subscription import Subscription, SubscriptionStatus
from app.models.tier import Tier
from app.schemas.subscription import PaymentInitiationResponse, SubscriptionCreate, SubscriptionRead

logger = logging.getLogger(__name__)
router = APIRouter()


@router.post(
    "/subscriptions",
    response_model=PaymentInitiationResponse,
    summary="Create a new subscription",
    description="Create a new subscription with the specified details.",
)
async def create_new_subscription(
    request: Request,
    subscription_create: SubscriptionCreate,
    supporter_id: CurrentUserUUID,
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

    if existing_sub_result.scalar_one_or_none() is not None:
        logger.info(f"User {supporter_id} already actively subscribed to creator {creator_id}")
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Already actively subscription to this creator"
        )
    # payment_service_url = f"{settings.PAYMENT_SERVICE_URL}/payment/checkout-sessions"
    payment_service_url = "http://payment_service:8004/payment/checkout-session"
    payload = {"tier_id": str(subscription_create.tier_id)}

    auth_header = request.headers.get("Authorization")
    headers = {}
    if auth_header:
        headers["Authorization"] = auth_header
        logger.debug("Forwarding Authorization header to Payment Service.")
    else:
        logger.error(
            f"Authorization header missing for user {supporter_id}. Cannot call Payment Service."
        )
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication token not found."
        )

    async with httpx.AsyncClient() as client:
        try:
            logger.info(
                f"Calling Payment Service at {payment_service_url} for"
                f" user {supporter_id}, tier {payload['tier_id']}"
            )
            response = await client.post(payment_service_url, json=payload, headers=headers)
            response.raise_for_status()

            payment_init_data = response.json()
            logger.info(f"Received successful response from Payment Service: {payment_init_data}")

            return PaymentInitiationResponse(
                session_id=payment_init_data.get("session_id"),
                checkout_url=payment_init_data.get("checkout_url")
            )

        except httpx.HTTPStatusError as e:
            error_detail = "Error initiating payment."
            try:
                error_detail = e.response.json().get("detail", error_detail)
            except Exception as e:
                logger.error(
                    f"Payment Service returned error ({e.response.status_code}): {error_detail}"
                )
                raise HTTPException(
                    status_code=status.HTTP_502_BAD_GATEWAY,
                    detail=f"Failed to initiate payment: {error_detail}"
                )
        except httpx.RequestError as e:
            logger.error(f"Could not connect to Payment Service at {payment_service_url}: {e}")
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="Payment service is unavailable."
            )
        except Exception as e:
            logger.exception(f"Unexpected error calling Payment Service: {e}", exc_info=True)
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="An unexpected error occurred while initiating payment."
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
