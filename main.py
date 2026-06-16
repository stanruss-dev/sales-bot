import asyncio
import logging
from aiogram import Bot, Dispatcher
from config.settings import settings
from handlers.start import router as start_router
from handlers.messages import router as messages_router

logging.basicConfig(level=logging.INFO)


async def main():
    bot = Bot(token=settings.TELEGRAM_BOT_TOKEN)
    dp = Dispatcher()

    dp.include_router(start_router)
    dp.include_router(messages_router)

    print("🤖 Sales Bot запущен!")
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
