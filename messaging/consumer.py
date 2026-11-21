from __future__ import annotations

import asyncio
import logging

from messaging.rabbitmq import consume_events


logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(message)s",
)
logger = logging.getLogger("shopfast.consumer")


async def handle_event(event: dict) -> None:
    event_type = event.get("event_type")
    payload = event.get("payload", {})
    logger.info("Evento recibido: %s | payload=%s", event_type, payload)


if __name__ == "__main__":
    asyncio.run(consume_events(handle_event))
