import asyncio
import logging
import os

import aio_pika

from handlers import handle_message
from healthcheck import clear_ready, mark_ready

QUEUE_NAME = "fight.inbox"
logger = logging.getLogger(__name__)


async def run_worker(stop: asyncio.Event) -> None:
    clear_ready()
    connection = await aio_pika.connect(
        host=os.getenv("RABBITMQ_HOST", "localhost"),
        port=int(os.getenv("RABBITMQ_PORT", "5672")),
        login=os.environ["RABBITMQ_USER"],
        password=os.environ["RABBITMQ_PASSWORD"],
        heartbeat=10,
        timeout=10,
    )
    try:
        async with connection:
            channel = await connection.channel()
            await channel.set_qos(prefetch_count=1)
            queue = await channel.declare_queue(QUEUE_NAME, durable=True)
            consumer_tag = await queue.consume(handle_message)
            logger.info("Waiting for messages in %s", QUEUE_NAME)

            while not stop.is_set():
                if connection.is_closed or channel.is_closed:
                    raise RuntimeError("RabbitMQ connection or channel closed")
                mark_ready()
                try:
                    await asyncio.wait_for(stop.wait(), timeout=2)
                except TimeoutError:
                    pass

            await queue.cancel(consumer_tag)
    finally:
        clear_ready()
