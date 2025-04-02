import logging
import uuid
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Query, Response, status
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession
from sqlmodel import select

from app.api.dependencies import CurrentUserUUID
from app.core.database import get_async_session
from app.models.tier import Tier
from app.schemas.tier import TierCreate, TierRead, TierUpdate

logger = logging.getLogger(__name__)
router = APIRouter()


@router.post(
    "/tiers", response_model=TierRead,
    summary="Create a new tier",
    description="Create a new tier with the specified details.",
)
async def create_tier(
    tier_create: TierCreate,
    creator_id: CurrentUserUUID = Depends(CurrentUserUUID),
    session: AsyncSession = Depends(get_async_session),
):
    logger.info(f"Creating new tier with creator_id: {creator_id}")
    create_data = tier_create.model_dump()
    db_tier = Tier(**create_data, creator_id=creator_id)
    session.add(db_tier)
    tier_to_return = db_tier

    try:
        await session.commit()
        await session.refresh(tier_to_return)
        logger.info(f"Successfully committed tier changes for tier_id: {tier_to_return.id}")
        return tier_to_return
    except IntegrityError:
        await session.rollback()
        logger.error(f"Integrity error for tier_id: {tier_to_return.id}")
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Content potentially already exists or data conflict.",
        )
    except Exception as e:
        await session.rollback()
        logger.exception(f"Error saving content for tier_id: {tier_to_return.id} - {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Could not save content",
        )


@router.get(
    "/tiers/{tier_id}",
    response_model=TierRead,
    summary="Get a tier by ID",
    description="Retrieve a tier by its unique identifier.",
)
async def get_tier(
    tier_id: uuid.UUID,
    session: AsyncSession = Depends(get_async_session),
):
    statement = select(Tier).where(Tier.id==tier_id)
    result = await session.execute(statement)
    tier = result.scalar_one_or_none()

    if not tier:
        logger.info(f"The tier not found for tier_id: {tier_id}")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Tier not found"
        )
    logger.info(f"Tier found for tier_id: {tier_id}")
    return tier


@router.put(
    "/tiers/{tier_id}",
    response_model=TierRead,
    summary="Update a tier",
    description="Update the details of an existing tier.",
)
async def update_tier(
    tier_id: uuid.UUID,
    tier_update: TierUpdate,
    session: AsyncSession = Depends(get_async_session),
    current_user: CurrentUserUUID = Depends(CurrentUserUUID),
):
    statement = select(Tier).where(Tier.id == tier_id)
    result = await session.execute(statement)
    db_tier = result.scalar_one_or_none()

    if not db_tier:
        logger.info(f"The tier not found for tier_id: {tier_id}")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Tier not found."
        )

    if not db_tier.creator_id == current_user:
        logger.info(f"You don't have permissins to edit tier with tier_id: {tier_id}")
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="It seems you don't have enough permissions to edit this tier."
        )

    logger.info(f"Updating tier for tier_id: {tier_id}")
    update_data = tier_update.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(db_tier, key, value)
    await session.add(db_tier)
    tier_to_return = db_tier

    try:
        await session.commit()
        await session.refresh(tier_to_return)
        logger.info(f"Successfully committed tier changes for tier_id: {tier_to_return.id}")
        return tier_to_return
    except IntegrityError:
        await session.rollback()
        logger.error(f"Integrity error for tier_id: {tier_to_return.id}")
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Content potentially already exists or data conflict.",
        )
    except Exception as e:
        await session.rollback()
        logger.exception(f"Error saving content for tier_id: {tier_to_return.id} - {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Could not save content",
        )


@router.delete(
    "/tiers/{tier_id}",
    summary="Delete a tier",
    description="Delete a tier by its unique identifier.",
)
async def delete_tier(
    tier_id: uuid.UUID,
    session: AsyncSession = Depends(get_async_session),
    current_user: CurrentUserUUID = Depends(CurrentUserUUID),
):
    statement = select(Tier).where(Tier.id == tier_id)
    result = await session.execute(statement)
    tier_to_delete = result.scalar_one_or_none()

    if not tier_to_delete:
        logger.info(f"The tier not found for tier_id: {tier_id}")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Tier not found."
        )

    if not tier_to_delete.creator_id == current_user:
        logger.info(f"You don't have permissins to edit tier with tier_id: {tier_id}")
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="It seems you don't have enough permissions to edit this tier."
        )

    logger.info(f"Deleting tier with tier_id: {tier_id}")
    await session.delete(tier_to_delete)

    try:
        await session.commit()
        logger.info(f"Successfully deleted tier_id: {tier_id}")
        return Response(status_code=status.HTTP_204_NO_CONTENT)
    except Exception as e:
        await session.rollback()
        logger.exception(f"Error deleting tier_id: {tier_id} - {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Could not delete tier",
        )


@router.get(
    "/users/{creator_id}/tiers",
    response_model=list[TierRead],
    summary="Get all tiers for a creator",
    description="Retrieve all tiers associated with a specific creator.",
)
async def get_all_tiers_by_creator(
    creator_id: uuid.UUID,
    limit: Annotated[int, Query(ge=1, le=50)] = 20,
    offset: Annotated[int, Query(ge=0)] = 0,
    session: AsyncSession = Depends(get_async_session),
):
    statement = (
        select(Tier)
        .where(Tier.creator_id == creator_id)
        .order_by(Tier.created_at.desc()) # Usually want newest first
        .offset(offset)
        .limit(limit)
    )
    result = await session.execute(statement)
    tiers = result.scalars().all()

    logger.info(f"Retrieved {len(tiers)} posts for creator_id: {creator_id}")
    return tiers
