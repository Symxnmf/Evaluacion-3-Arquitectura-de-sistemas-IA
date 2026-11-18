from __future__ import annotations

import asyncio

from messaging.rabbitmq import consume_events


async def handle_event(event: dict) -> None:
    event_type = event.get("event_type")
    payload = event.get("payload", {})
    print(f"Received {event_type}: {payload}", flush=True)


if __name__ == "__main__":
    asyncio.run(consume_events(handle_event))
