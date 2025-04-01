import logging

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.dependencies import CurrentUserUUID
from app.core.database import get_async_session
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
    pass

@router.get(
    "/tiers/{tier_id}",
    response_model=TierRead,
    summary="Get a tier by ID",
    description="Retrieve a tier by its unique identifier.",
)
async def get_tier(
    tier_id: str,
    session: AsyncSession = Depends(get_async_session),
    current_user: CurrentUserUUID = Depends(CurrentUserUUID),
):
    pass

@router.put(
    "/tiers/{tier_id}",
    response_model=TierRead,
    summary="Update a tier",
    description="Update the details of an existing tier.",
)
async def update_tier(
    tier_id: str,
    tier_update: TierUpdate,
    session: AsyncSession = Depends(get_async_session),
    current_user: CurrentUserUUID = Depends(CurrentUserUUID),
):
    pass


@router.delete(
    "/tiers/{tier_id}",
    summary="Delete a tier",
    description="Delete a tier by its unique identifier.",
)
async def delete_tier(
    tier_id: str,
    session: AsyncSession = Depends(get_async_session),
    current_user: CurrentUserUUID = Depends(CurrentUserUUID),
):
    pass


@router.get(
    "/users/{creator_id}/tiers",
    response_model=list[TierRead],
    summary="Get all tiers for a creator",
    description="Retrieve all tiers associated with a specific creator.",
)
async def get_all_tiers_by_creator(
    creator_id: str,
    session: AsyncSession = Depends(get_async_session),
    current_user: CurrentUserUUID = Depends(CurrentUserUUID),
):
    pass
