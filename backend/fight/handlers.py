import logging

from aio_pika.abc import AbstractIncomingMessage

logger = logging.getLogger(__name__)


async def handle_message(message: AbstractIncomingMessage) -> None:
    async with message.process():
        # Temporary handler until combat commands are implemented.
        logger.info("Received demo message: %r", message.body)
