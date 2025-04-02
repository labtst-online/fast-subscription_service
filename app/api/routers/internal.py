# VERY IMPORTANT LOGIC
import datetime
import logging
import uuid

from fastapi import APIRouter, Depends, HTTPException, Query, Response, status
from fastapi.responses import JSONResponse
from sqlalchemy.ext.asyncio import AsyncSession
from sqlmodel import exists, select

from app.core.database import get_async_session
from app.models.subscription import Subscription, SubscriptionStatus
from app.models.tier import Tier

logger = logging.getLogger(__name__)
router = APIRouter()


@router.get(
    "/internal/check-access",
    status_code=status.HTTP_200_OK,
    summary="Check Access",
    description="Check if the user has access to the internal API.",
)
async def check_access(
    supporter_id: uuid.UUID = Query(...),
    creator_id: uuid.UUID = Query(...),
    session: AsyncSession = Depends(get_async_session),
) -> JSONResponse:

    logger.info(f"Checking access {supporter_id} to content {creator_id}")
    statement = (
        select(exists().where(
            (Subscription.supporter_id == supporter_id) &
            (Tier.creator_id == creator_id) &
            (Subscription.status == SubscriptionStatus.ACTIVE) &
            (Subscription.expires_at > datetime.datetime.now(datetime.UTC))
        ))
        .select_from(Subscription) # Explicitly state the FROM clause
        .join(Tier, Subscription.tier_id == Tier.id) # Perform the join
    )
    result = await session.execute(statement)
    has_access = result.scalar()

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
