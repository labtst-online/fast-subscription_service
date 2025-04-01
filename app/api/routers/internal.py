# VERY IMPORTANT LOGIC
import logging
import uuid

from fastapi import APIRouter, Depends, Query
from fastapi.responses import JSONResponse
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_async_session

logger = logging.getLogger(__name__)
router = APIRouter()


@router.get(
    "internal/check-access",
    summary="Check Access",
    description="Check if the user has access to the internal API.",
)
async def check_access(
    supporter_id: uuid.UUID = Query(...),
    creator_id: uuid.UUID = Query(...),
    session: AsyncSession = Depends(get_async_session),
) -> JSONResponse:
    pass
