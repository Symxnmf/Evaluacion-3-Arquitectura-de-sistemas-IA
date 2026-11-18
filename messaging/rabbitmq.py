from __future__ import annotations

import asyncio
import json
import os
from collections.abc import Awaitable, Callable

import aio_pika


async def publish_event(event_type: str, payload: dict) -> None:
    url = os.getenv("RABBITMQ_URL", "amqp://guest:guest@localhost:5672/")
    connection = await aio_pika.connect_robust(url)
    try:
        channel = await connection.channel()
        exchange = await channel.declare_exchange(
            "shopfast.events",
            aio_pika.ExchangeType.TOPIC,
            durable=True,
        )
        message = aio_pika.Message(
            body=json.dumps(
                {"event_type": event_type, "payload": payload},
                default=str,
            ).encode(),
            content_type="application/json",
            delivery_mode=aio_pika.DeliveryMode.PERSISTENT,
        )
        await exchange.publish(message, routing_key=event_type)
    finally:
        await connection.close()


async def consume_events(
    handler: Callable[[dict], Awaitable[None]],
) -> None:
    url = os.getenv("RABBITMQ_URL", "amqp://guest:guest@localhost:5672/")
    connection = await aio_pika.connect_robust(url)
    channel = await connection.channel()
    await channel.set_qos(prefetch_count=20)

    exchange = await channel.declare_exchange(
        "shopfast.events",
        aio_pika.ExchangeType.TOPIC,
        durable=True,
    )
    queue = await channel.declare_queue(
        "shopfast.interactions",
        durable=True,
        arguments={
            "x-dead-letter-exchange": "shopfast.retry",
            "x-dead-letter-routing-key": "interaction.failed",
        },
    )
    await queue.bind(exchange, "user.interaction")

    async with queue.iterator() as messages:
        async for message in messages:
            async with message.process(requeue=False):
                try:
                    event = json.loads(message.body)
                    await asyncio.wait_for(handler(event), timeout=30)
                except Exception:
                    await asyncio.sleep(1)
                    raise

