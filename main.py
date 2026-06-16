import asyncio
import logging
import logging.handlers
import os
from aiogram import Bot, Dispatcher
from config.settings import settings
from handlers.start import router as start_router
from handlers.messages import router as messages_router

os.makedirs("logs", exist_ok=True)

log_level = getattr(logging, settings.LOG_LEVEL.upper(), logging.INFO)
logging.basicConfig(
    level=log_level,
    format="[%(asctime)s] [%(levelname)s] [%(module)s] %(message)s",
    handlers=[
        logging.StreamHandler(),
        logging.handlers.RotatingFileHandler(
            "logs/app.log", maxBytes=5 * 1024 * 1024, backupCount=3, encoding="utf-8"
        ),
    ],
)

logger = logging.getLogger(__name__)


async def main():
    bot = Bot(token=settings.TELEGRAM_BOT_TOKEN)
    dp = Dispatcher()

    dp.include_router(start_router)
    dp.include_router(messages_router)

    logger.info("Sales Bot запущен!")
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
