# VERY IMPORTANT LOGIC
import datetime
import logging
import uuid

from fastapi import APIRouter, Depends, HTTPException, Query, Response, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlmodel import select

from app.core.database import get_async_session
from app.models.subscription import Subscription, SubscriptionStatus
from app.models.tier import Tier

logger = logging.getLogger(__name__)
router = APIRouter()


@router.get(
    "/check-access",
    status_code=status.HTTP_200_OK,
    summary="Check user access to creator content (Internal)",
    description="Checks if a supporter has an active subscription to any tier of creator.",
)
async def check_access_internal(
    supporter_id: uuid.UUID = Query(...),
    creator_id: uuid.UUID = Query(...),
    session: AsyncSession = Depends(get_async_session),
):
    logger.debug(f"Internal access check: Supporter {supporter_id} for Creator {creator_id}")

    statement = (
        select(1)
        .select_from(Subscription)
        .join(Tier, Subscription.tier_id == Tier.id)
        .where(
            (Subscription.supporter_id == supporter_id) &
            (Tier.creator_id == creator_id) &
            (Subscription.status == SubscriptionStatus.ACTIVE) &
            (Subscription.expires_at > datetime.datetime.now(datetime.UTC))
        )
    )
    result = await session.execute(statement)
    has_access = result.scalar()  # Returns True or False

    if has_access:
        logger.debug(f"Access GRANTED for Supporter {supporter_id} to Creator {creator_id}")
        # Return simple 200 OK by default if access is granted
        # Optionally: return {"has_access": True}
        return Response(status_code=status.HTTP_200_OK)
    else:
        logger.debug(f"Access DENIED for Supporter {supporter_id} to Creator {creator_id}")
        # Raise 404 (or 403) if no active subscription is found
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, # Or 403 Forbidden
            detail="No active subscription found for this creator."
        )
