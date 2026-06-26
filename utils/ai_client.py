from openai import AsyncOpenAI
from config.settings import settings
from utils.knowledge_loader import KNOWLEDGE_BASE
from utils.learning import get_insights_text

client = AsyncOpenAI(
    api_key=settings.OPENROUTER_API_KEY,
    base_url="https://api.groq.com/openai/v1",
)

_KB_LIMIT = 8000
_kb = KNOWLEDGE_BASE[:_KB_LIMIT] if len(KNOWLEDGE_BASE) > _KB_LIMIT else KNOWLEDGE_BASE

_SYSTEM_TEMPLATE = """Ты — умный помощник по продажам в Telegram для магазина РУСАЛЮТ. Помогаешь клиентам выбрать пиротехнику.

ОБЯЗАТЕЛЬНЫЕ ПРАВИЛА (нарушать нельзя):
- ПОРЯДОК ТОВАРОВ: всегда перечисляй от самого дорогого к самому дешёвому. Делай это молча — клиенту не объясняй, почему именно в таком порядке.
- БЮДЖЕТ: если клиент назвал сумму — показывай ТОЛЬКО товары в диапазоне ±10%. Бюджет 5000 ₽ → от 4500 до 5500 ₽. Бюджет 7000 ₽ → от 6300 до 7700 ₽. Товары за пределами диапазона не упоминай вообще.
- ЯЗЫК: отвечай только по-русски, без единого английского слова.
- ИСТОЧНИК: используй только данные из базы знаний ниже, не придумывай.
- ТЕМА: если вопрос не связан с пиротехникой, фейерверками или магазином РУСАЛЮТ — вежливо откажи и верни разговор к теме. Пример ответа: «Я специализируюсь только на пиротехнике и фейерверках — здесь я точно помогу! Расскажите, какой праздник планируете?»

ОСТАЛЬНЫЕ ПРАВИЛА:
- Будь вежливым, тёплым, помогай с выбором
- Задавай вопросы: праздник, место запуска, бюджет
- При возражениях отрабатывай по скриптам из базы
- Если клиент готов купить — начни: ГОТОВ К ПОКУПКЕ
- Если нужен менеджер — начни: НУЖЕН МЕНЕДЖЕР
- Пиши кратко, не более 3-4 абзацев

{insights}

БАЗА ЗНАНИЙ:
{kb}
"""


def _build_system_prompt() -> str:
    insights = get_insights_text()
    insights_block = f"\n{insights}\n" if insights else ""
    return _SYSTEM_TEMPLATE.format(insights=insights_block, kb=_kb)


async def get_ai_response(messages: list[dict]) -> str:
    response = await client.chat.completions.create(
        model=settings.AI_MODEL,
        max_tokens=1000,
        messages=[{"role": "system", "content": _build_system_prompt()}] + messages,
    )
    return response.choices[0].message.content
