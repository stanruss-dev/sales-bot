from aiogram import Router, Bot
from aiogram.types import Message
from config.settings import settings
from utils.sales_funnel import get_session, FunnelStage
from utils.ai_client import get_ai_response
from utils.learning import record_signals

router = Router()


@router.message()
async def message_handler(message: Message, bot: Bot):
    user_id = message.from_user.id
    session = get_session(user_id)

    # Add user message to history
    session.add_message("user", message.text)

    # Record customer signals for self-learning
    await record_signals(user_id, message.text)

    # Get AI response
    await message.chat.do("typing")
    response = await get_ai_response(session.history)

    # Check for special signals in response
    if response.startswith("ГОТОВ К ПОКУПКЕ"):
        session.stage = FunnelStage.CLOSING
        response = response.replace("ГОТОВ К ПОКУПКЕ", "").strip()
        # Notify manager
        if settings.MANAGER_CHAT_ID:
            await bot.send_message(
                settings.MANAGER_CHAT_ID,
                f"🔥 Горячий лид!\n"
                f"Пользователь: @{message.from_user.username or user_id}\n"
                f"Имя: {message.from_user.full_name}\n"
                f"ID: {user_id}"
            )

    elif response.startswith("НУЖЕН МЕНЕДЖЕР"):
        response = response.replace("НУЖЕН МЕНЕДЖЕР", "").strip()
        if settings.MANAGER_CHAT_ID:
            await bot.send_message(
                settings.MANAGER_CHAT_ID,
                f"👤 Клиент просит менеджера!\n"
                f"Пользователь: @{message.from_user.username or user_id}\n"
                f"ID: {user_id}"
            )

    # Add assistant response to history
    session.add_message("assistant", response)

    await message.answer(response)
