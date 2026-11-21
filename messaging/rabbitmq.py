from __future__ import annotations

import asyncio
import json
import os
from collections.abc import Awaitable, Callable

import aio_pika
from dotenv import load_dotenv


load_dotenv()


class RabbitMQPublishError(RuntimeError):
    """Raised when an event cannot be published."""


async def publish_event(event_type: str, payload: dict) -> None:
    url = os.getenv("RABBITMQ_URL", "amqp://guest:guest@localhost:5672/")
    try:
        connection = await aio_pika.connect_robust(url)
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
    except Exception as exc:
        raise RabbitMQPublishError(
            "No fue posible publicar el evento en RabbitMQ."
        ) from exc
    finally:
        if "connection" in locals():
            await connection.close()


async def consume_events(
    handler: Callable[[dict], Awaitable[None]],
) -> None:
    url = os.getenv("RABBITMQ_URL", "amqp://guest:guest@localhost:5672/")
    connection = await aio_pika.connect_robust(url)
    try:
        channel = await connection.channel()
        await channel.set_qos(prefetch_count=20)

        exchange = await channel.declare_exchange(
            "shopfast.events",
            aio_pika.ExchangeType.TOPIC,
            durable=True,
        )
        retry_exchange = await channel.declare_exchange(
            "shopfast.retry",
            aio_pika.ExchangeType.DIRECT,
            durable=True,
        )
        retry_queue = await channel.declare_queue(
            "shopfast.interactions.retry",
            durable=True,
            arguments={
                "x-message-ttl": 5000,
                "x-dead-letter-exchange": "shopfast.events",
                "x-dead-letter-routing-key": "user.interaction",
            },
        )
        await retry_queue.bind(retry_exchange, "user.interaction.retry")

        dlx = await channel.declare_exchange(
            "shopfast.dlx",
            aio_pika.ExchangeType.DIRECT,
            durable=True,
        )
        dlq = await channel.declare_queue(
            "shopfast.interactions.failed",
            durable=True,
        )
        await dlq.bind(dlx, "interaction.failed")

        queue = await channel.declare_queue(
            "shopfast.interactions",
            durable=True,
        )
        await queue.bind(exchange, "user.interaction")

        async with queue.iterator() as messages:
            async for message in messages:
                try:
                    event = json.loads(message.body)
                except json.JSONDecodeError:
                    await dlx.publish(
                        aio_pika.Message(
                            body=message.body,
                            headers={"shopfast_error": "invalid_json"},
                            content_type="application/json",
                            delivery_mode=aio_pika.DeliveryMode.PERSISTENT,
                        ),
                        routing_key="interaction.failed",
                    )
                    await message.ack()
                    continue

                attempt = int(message.headers.get("shopfast_attempt", 1))
                try:
                    await asyncio.wait_for(handler(event), timeout=30)
                    await message.ack()
                except Exception:
                    if attempt >= 3:
                        await dlx.publish(
                            aio_pika.Message(
                                body=message.body,
                                headers={
                                    "shopfast_attempt": attempt,
                                    "shopfast_error": "maximum_retries_exceeded",
                                },
                                content_type="application/json",
                                delivery_mode=aio_pika.DeliveryMode.PERSISTENT,
                            ),
                            routing_key="interaction.failed",
                        )
                        await message.ack()
                    else:
                        await retry_exchange.publish(
                            aio_pika.Message(
                                body=message.body,
                                headers={
                                    "shopfast_attempt": attempt + 1,
                                },
                                content_type="application/json",
                                delivery_mode=aio_pika.DeliveryMode.PERSISTENT,
                            ),
                            routing_key="user.interaction.retry",
                        )
                        await message.ack()
    finally:
        await connection.close()

