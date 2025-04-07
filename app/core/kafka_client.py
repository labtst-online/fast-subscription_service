import asyncio
import datetime
import json
import logging

from confluent_kafka import Consumer, KafkaError, Message
from fastapi import Depends
from pydantic import ValidationError
from sqlalchemy.ext.asyncio import AsyncSession
from sqlmodel import select

from app.core.database import get_async_session
from app.models.subscription import Subscription, SubscriptionStatus
from app.schemas.kafka_events import PaymentSucceededEvent

from .config import settings

logger = logging.getLogger(__name__)


class SubscriptionHandler:
    """Handles subscription-related database operations"""

    def __init__(self, session: AsyncSession):
        self.session = session

    async def process_subscription(self, event: PaymentSucceededEvent) -> bool:
        """Process subscription creation or update based on payment event"""
        try:
            statement = select(Subscription).where(
                Subscription.supporter_id == event.user_id,
                Subscription.tier_id == event.tier_id
            ).with_for_update()

            result = await self.session.execute(statement)
            subscription = result.scalar_one_or_none()

            if subscription and subscription.status == SubscriptionStatus.ACTIVE:
                logger.warning(
                    f"Subscription for user {event.user_id}, "
                    f"tier {event.tier_id} already ACTIVE"
                )
                return True

            await self._update_or_create_subscription(subscription, event)
            return True

        except Exception as e:
            logger.exception(f"Database error processing subscription: {e}")
            await self.session.rollback()
            return False

    async def _update_or_create_subscription(
        self,
        subscription: Subscription | None,
        event: PaymentSucceededEvent
    ):
        """Update existing or create new subscription"""
        start_time = datetime.datetime.now(datetime.UTC)
        expiry_time = start_time + datetime.timedelta(days=30)

        if subscription:
            subscription.status = SubscriptionStatus.ACTIVE
            subscription.started_at = start_time
            subscription.expires_at = expiry_time
            logger.info(f"Updating subscription {subscription.id}")
        else:
            subscription = Subscription(
                supporter_id=event.user_id,
                tier_id=event.tier_id,
                status=SubscriptionStatus.ACTIVE,
                started_at=start_time,
                expires_at=expiry_time
            )
            self.session.add(subscription)
            logger.info(f"Creating new subscription for {event.user_id}")

        await self.session.commit()

class MessageProcessor:
    """Processes Kafka messages and handles event dispatch"""

    def __init__(self, session: AsyncSession):
        self.session = session
        self.subscription_handler = SubscriptionHandler(session)

    async def process_message(self, msg: Message) -> bool:
        """Process a single Kafka message"""
        try:
            event_data = json.loads(msg.value().decode('utf-8'))

            if event_data.get("event_type") != "payment.succeeded":
                logger.debug(f"Ignoring event type: {event_data.get('event_type')}")
                return True

            event = PaymentSucceededEvent(**event_data)
            logger.info(f"Processing payment event for user {event.user_id}")

            return await self.subscription_handler.process_subscription(event)

        except (json.JSONDecodeError, ValidationError) as e:
            logger.error(f"Message validation error: {e}")
            return True
        except Exception as e:
            logger.exception(f"Message processing error: {e}")
            return False

class KafkaConsumer:
    """Handles Kafka consumer operations"""

    def __init__(self):
        self._running = True
        self._consumer: Consumer | None = None

    def _initialize_consumer(self) -> Consumer:
        """Initialize and configure Kafka consumer"""
        conf = {
            'bootstrap.servers': settings.KAFKA_BOOTSTRAP_SERVERS,
            'group.id': settings.KAFKA_CONSUMER_GROUP_ID,
            'auto.offset.reset': 'earliest'
        }
        consumer = Consumer(conf)
        consumer.subscribe([settings.KAFKA_PAYMENT_EVENTS_TOPIC])
        return consumer

    async def _handle_message_error(self, msg: Message) -> bool:
        """Handle Kafka message errors"""
        if msg.error().code() == KafkaError._PARTITION_EOF:
            logger.debug(f"Reached partition end: {msg.topic()} @ {msg.offset()}")
            return True
        elif msg.error().fatal():
            logger.error(f"Fatal Kafka error: {msg.error()}")
            self._running = False
            return False
        else:
            logger.warning(f"Non-fatal Kafka error: {msg.error()}")
            return True

class KafkaClient:
    """Main Kafka client class orchestrating message consumption"""

    def __init__(self):
        self.consumer = KafkaConsumer()

    async def consume_messages(
        self,
        topic: str,
        session: AsyncSession = Depends(get_async_session)
    ):
        """Start consuming messages from Kafka"""
        processor = MessageProcessor(session)
        self.consumer._consumer = self.consumer._initialize_consumer()

        try:
            while self.consumer._running:
                msg = self.consumer._consumer.poll(1.0)

                if msg is None:
                    await asyncio.sleep(0.1)
                    continue

                if msg.error():
                    if not await self.consumer._handle_message_error(msg):
                        break
                    continue

                if await processor.process_message(msg):
                    self.consumer._consumer.commit(message=msg)
                else:
                    await asyncio.sleep(5)

        except asyncio.CancelledError:
            logger.info("Consumer task cancelled")
        except Exception as e:
            logger.exception(f"Consumer loop error: {e}")
        finally:
            self._cleanup()

    def _cleanup(self):
        """Clean up Kafka consumer resources"""
        if self.consumer._consumer:
            logger.info("Closing Kafka consumer...")
            self.consumer._consumer.close()
            logger.info("Kafka consumer closed")

    def close_consumer(self):
        """Signal consumer to stop"""
        self.consumer._running = False
        logger.info("Stop signal sent to consumer")


kafka_client = KafkaClient()
