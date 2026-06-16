from aiogram import Router
from aiogram.filters import CommandStart
from aiogram.types import Message
from utils.sales_funnel import get_session, FunnelStage

router = Router()

GREETING = """👋 Привет! Рады видеть вас!

Я помощник нашего магазина. Помогу подобрать нужный товар, расскажу об акциях и отвечу на любые вопросы.

Чем могу помочь? 😊"""


@router.message(CommandStart())
async def start_handler(message: Message):
    session = get_session(message.from_user.id)
    session.stage = FunnelStage.DISCOVERY
    session.history = []

    await message.answer(GREETING)
