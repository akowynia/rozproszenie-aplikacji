import json
import logging
from datetime import datetime, timezone
from typing import Optional
from aiokafka import AIOKafkaProducer
from .config import settings

logger = logging.getLogger(__name__)

class KafkaAlertProducer:
    def __init__(self):
        self.producer: Optional[AIOKafkaProducer] = None
        self.bootstrap_servers = settings.kafka_bootstrap_servers
        self.topic = settings.kafka_topic

    async def start(self) -> None:
        if self.producer is not None:
            return
        
        logger.info(f"Initializing Kafka producer on {self.bootstrap_servers}")
        try:
            self.producer = AIOKafkaProducer(
                bootstrap_servers=self.bootstrap_servers,
                value_serializer=lambda v: json.dumps(v).encode("utf-8")
            )
            await self.producer.start()
            logger.info("Kafka producer successfully started.")
        except Exception as e:
            logger.error(f"Failed to start Kafka producer: {e}")
            self.producer = None

    async def stop(self) -> None:
        if self.producer is None:
            return
        
        logger.info("Stopping Kafka producer...")
        try:
            await self.producer.stop()
            logger.info("Kafka producer stopped.")
        except Exception as e:
            logger.error(f"Error while stopping Kafka producer: {e}")
        finally:
            self.producer = None

    async def send_alert(self, url: str, forbidden_word: str) -> None:
        if self.producer is None:
            logger.info("Kafka producer is not initialized or failed to start. Retrying startup...")
            await self.start()

        if self.producer is None:
            logger.warning(
                f"Kafka producer is not active. Alert for URL: '{url}' (word: '{forbidden_word}') was not sent."
            )
            return

        payload = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "url": url,
            "forbidden_word": forbidden_word
        }


        try:
            logger.info(f"Sending alert to Kafka topic '{self.topic}' for word '{forbidden_word}'")
            await self.producer.send_and_wait(self.topic, payload)
            logger.info("Alert successfully sent to Kafka.")
        except Exception as e:
            logger.error(f"Failed to send alert to Kafka: {e}")

# Global provider instance
alert_producer = KafkaAlertProducer()
