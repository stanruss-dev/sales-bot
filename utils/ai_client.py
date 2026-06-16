from openai import AsyncOpenAI
from config.settings import settings
from utils.knowledge_loader import KNOWLEDGE_BASE

client = AsyncOpenAI(
    api_key=settings.OPENROUTER_API_KEY,
    base_url="https://openrouter.ai/api/v1",
)

SYSTEM_PROMPT = f"""Ты — умный помощник по продажам в Telegram. Твоя задача — помогать клиентам, отвечать на их вопросы и мягко вести их к покупке.

БАЗА ЗНАНИЙ:
{KNOWLEDGE_BASE}

ПРАВИЛА:
1. Отвечай только на основе базы знаний выше
2. Будь вежливым, тёплым и человечным
3. Задавай уточняющие вопросы, чтобы понять потребность
4. Предлагай конкретные товары/услуги под запрос клиента
5. При возражениях — мягко отрабатывай их по скрипту из базы знаний
6. Если клиент готов купить — начни ответ словами: ГОТОВ К ПОКУПКЕ
7. Если нужен живой менеджер — начни ответ словами: НУЖЕН МЕНЕДЖЕР
8. Не придумывай информацию, которой нет в базе знаний
9. Пиши кратко — не более 3–4 абзацев за раз
"""


async def get_ai_response(messages: list[dict]) -> str:
    response = await client.chat.completions.create(
        model=settings.AI_MODEL,
        max_tokens=1000,
        messages=[{"role": "system", "content": SYSTEM_PROMPT}] + messages,
    )
    return response.choices[0].message.content
