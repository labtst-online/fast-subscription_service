import asyncio
import logging
from contextlib import asynccontextmanager

from fastapi import Depends, FastAPI, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.routers.internal import router as internal_router
from app.api.routers.subscription import router as subscription_router
from app.api.routers.tier import router as tier_router
from app.core.kafka_client import kafka_client
from app.models.tier import Tier

from .core.config import settings
from .core.database import async_engine, get_async_session

# Configure logging
# Basic config, customize as needed (e.g., structured logging)
logging.basicConfig(level=logging.INFO if settings.APP_ENV == "production" else logging.DEBUG)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Application startup...")
    # You can add startup logic here, like checking DB connection
    try:
        async with async_engine.connect():
            logger.info("Database connection successful during startup.")
    except Exception as e:
        logger.error(f"Database connection failed during startup: {e}")
    asyncio.create_task(kafka_client.consume_messages())
    yield

    logger.info("Application shutdown...")
    await async_engine.dispose()
    logger.info("Database engine disposed.")
    kafka_client.close_consumer()
    logger.info("Kafka Consumer disposed.")


app = FastAPI(
    title="Subscription Service",
    description="Handles user profiles.",
    version="0.1.0",
    lifespan=lifespan
)


app.include_router(tier_router, prefix="/tier", tags=["Tier"])

app.include_router(subscription_router, prefix="/subscriptions", tags=["Subscriptions"])

app.include_router(internal_router, prefix="/internal", tags=["Internal"])


@app.get("/test-db/", summary="Test Database Connection", tags=["Test"])
async def test_db_connection(
    session: AsyncSession = Depends(get_async_session)
):
    """
    Attempts to retrieve the first tier from the database.
    """
    logger.info("Accessing /test-db/ endpoint")
    try:
        statement = select(Tier).limit(1)
        result = await session.execute(statement)
        tier = result.scalar_one_or_none()

        if tier:
            logger.info(f"Successfully retrieved tier: {tier.id}")
            return {"status": "success", "first_tier": tier.id}
        else:
            logger.info("No tier found in the database.")
            return {"status": "success", "message": "No tier found"}
    except Exception as e:
        logger.error(f"Database query failed: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Database error: {e}")


@app.get("/", summary="Health Check", tags=["Health"])
async def health_check():
    """Basic health check endpoint."""
    return {"status": "ok", "service": "Subscription Service"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
       "app.main:app",
       host="0.0.0.0",
       port=8003, # Or load from config
       reload=(settings.APP_ENV == "development"),
       log_level="info"
   )
