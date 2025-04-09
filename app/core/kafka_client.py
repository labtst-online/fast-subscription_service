import asyncio
import datetime
import json
import logging

from confluent_kafka import Consumer, KafkaError, Message
from pydantic import ValidationError
from sqlalchemy.ext.asyncio import AsyncSession
from sqlmodel import select

from app.core.database import AsyncSessionFactory
from app.models.subscription import Subscription, SubscriptionStatus
from app.schemas.kafka_events import PaymentSucceededEvent

from .config import settings

logger = logging.getLogger(__name__)


class SubscriptionHandler:
    """Handles subscription-related database operations"""

    async def process_subscription(
        self, event: PaymentSucceededEvent, session: AsyncSession
        ) -> bool:
        """Process subscription creation or update based on payment event"""
        try:
            statement = select(Subscription).where(
                Subscription.supporter_id == event.user_id,
                Subscription.tier_id == event.tier_id
            ).with_for_update()

            result = await session.execute(statement)
            subscription = result.scalar_one_or_none()

            if subscription and subscription.status == SubscriptionStatus.ACTIVE:
                logger.warning(
                    f"Subscription for user {event.user_id}, "
                    f"tier {event.tier_id} already ACTIVE"
                )
                return True

            await self._update_or_create_subscription(subscription, event, session)
            return True

        except Exception as e:
            logger.exception(f"Database error processing subscription: {e}")
            return False

    async def _update_or_create_subscription(
        self,
        subscription: Subscription | None,
        event: PaymentSucceededEvent,
        session: AsyncSession
    ):
        """Update existing or create new subscription"""
        start_time = datetime.datetime.now(datetime.UTC)
        expiry_time = start_time + datetime.timedelta(days=30)

        if subscription:
            subscription.status = SubscriptionStatus.ACTIVE
            subscription.started_at = start_time
            subscription.expires_at = expiry_time
            logger.info(f"Updating subscription {subscription.id} for user {event.user_id}")
        else:
            subscription = Subscription(
                supporter_id=event.user_id,
                tier_id=event.tier_id,
                status=SubscriptionStatus.ACTIVE,
                started_at=start_time,
                expires_at=expiry_time
            )
            session.add(subscription)
            logger.info(f"Creating new subscription for user {event.user_id}, tier {event.tier_id}")

        await session.commit()
        logger.info(f"Committed subscription changes for user {event.user_id}")


class MessageProcessor:
    """Processes Kafka messages and handles event dispatch"""

    def __init__(self):
        self.subscription_handler = SubscriptionHandler()

    async def process_message(self, msg: Message, session: AsyncSession) -> bool:
        """Process a single Kafka message"""
        try:
            event_data = json.loads(msg.value().decode('utf-8'))
            event_type = event_data.get("event_type")

            if event_type != "payment.succeeded":
                logger.debug(f"Ignoring event type: {event_type}")
                return True

            event = PaymentSucceededEvent(**event_data)
            logger.info(
                f"Processing payment.succeeded event for user {event.user_id},"
                f" payment {event.payment_id}"
            )

            return await self.subscription_handler.process_subscription(event, session)

        except (json.JSONDecodeError, ValidationError) as e:
            logger.error(
                f"Message validation/parsing error: {e}."
                f" Message value: {msg.value()}", exc_info=True
            )
            return True
        except Exception as e:
            logger.exception(f"Unexpected message processing error: {e}")
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
            'auto.offset.reset': 'earliest',
            'enable.auto.commit': False
        }
        consumer = Consumer(conf)
        consumer.subscribe([settings.KAFKA_PAYMENT_EVENTS_TOPIC])
        logger.info(
            f"Kafka consumer initialized for group '{settings.KAFKA_CONSUMER_GROUP_ID}' "
            f"on topic '{settings.KAFKA_PAYMENT_EVENTS_TOPIC}'"
        )
        return consumer

    async def _handle_message_error(self, msg: Message) -> bool:
        """Handle Kafka message errors"""
        if msg.error().code() == KafkaError._PARTITION_EOF:
            return True
        elif msg.error().fatal():
            logger.error(f"Fatal Kafka error: {msg.error()}. Stopping consumer.")
            self._running = False
            return False
        else:
            logger.warning(f"Non-fatal Kafka error: {msg.error()}. Continuing.")
            return True


class KafkaClient:
    """Main Kafka client class orchestrating message consumption"""

    def __init__(self):
        self.consumer = KafkaConsumer()
        self.processor = MessageProcessor()

    async def consume_messages(self):
        """Start consuming messages from Kafka"""
        self.consumer._consumer = self.consumer._initialize_consumer()
        if not self.consumer._consumer:
            logger.error("Failed to initialize Kafka consumer. Aborting consumption.")
            return

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

                logger.debug(
                    f"Received message from Kafka: Topic={msg.topic()}, "
                    f"Partition={msg.partition()}, Offset={msg.offset()}"
                )
                processed_successfully = False
                try:
                    async with AsyncSessionFactory() as session:
                        logger.debug(f"Created new DB session for message at offset {msg.offset()}")
                        processed_successfully = await self.processor.process_message(msg, session)
                except Exception as e:
                    logger.exception(
                        f"Error managing session scope for message"
                        f" at offset {msg.offset()}: {e}"
                    )
                    processed_successfully = False

                if processed_successfully:
                    try:
                        self.consumer._consumer.commit(message=msg, asynchronous=False)
                        logger.debug(
                            f"Committed Kafka offset {msg.offset()} for partition {msg.partition()}"
                        )
                    except Exception as e:
                        logger.exception(f"Failed to commit Kafka offset {msg.offset()}: {e}")
                else:
                    logger.warning(
                        f"Processing failed for message at offset {msg.offset()}."
                        f" Offset not committed. Will likely retry."
                    )
                    await asyncio.sleep(5)

        except asyncio.CancelledError:
            logger.info("Consumer task cancelled")
        except Exception as e:
            logger.exception(f"Unexpected error in Kafka consumer loop: {e}")
        finally:
            self._cleanup()

    def _cleanup(self):
        """Clean up Kafka consumer resources"""
        if self.consumer._consumer:
            logger.info("Closing Kafka consumer...")
            try:
                self.consumer._consumer.close()
                logger.info("Kafka consumer closed")
            except Exception as e:
                logger.exception(f"Error closing Kafka consumer: {e}")

    def close_consumer(self):
        """Signal consumer to stop"""
        self.consumer._running = False
        logger.info("Stop signal sent to consumer")


kafka_client = KafkaClient()
