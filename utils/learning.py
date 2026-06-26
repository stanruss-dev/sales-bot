import re
import sqlite3
import logging
from pathlib import Path

logger = logging.getLogger(__name__)

DB_PATH = Path("data/bot_learning.db")

_BUDGET_RE = re.compile(
    r"(?:бюджет|до|около|примерно|рублей|руб|₽)[^\d]*(\d[\d\s]{2,6})|(\d[\d\s]{2,6})\s*(?:рублей|руб|₽|р\.)",
    re.IGNORECASE,
)

_OCCASIONS = {
    "новый год": "Новый год",
    "нового года": "Новый год",
    "свадьб": "Свадьба",
    "день рождения": "День рождения",
    "дне рождения": "День рождения",
    "днюха": "День рождения",
    "корпоратив": "Корпоратив",
    "юбилей": "Юбилей",
    "8 марта": "8 марта",
    "23 февраля": "23 февраля",
    "выпускной": "Выпускной",
}

_PRODUCTS = {
    "батарея": "батареи салютов",
    "батареи": "батареи салютов",
    "салют": "батареи салютов",
    "фонтан": "фонтаны",
    "ракет": "ракеты",
    "бенгальск": "бенгальские свечи",
    "петард": "петарды",
    "фейерверк": "фейерверк",
    "фестивальн": "фестивальные шары",
    "римск": "римские свечи",
}

_QUESTIONS = {
    "доставк": "доставка",
    "безопасн": "безопасность",
    "вернут": "возврат",
    "возврат": "возврат",
    "гарантия": "гарантия",
    "стоимост": "цена",
    "цена": "цена",
    "скидка": "скидки",
    "акция": "акции",
}

# Cache to avoid reading DB on every message
_insights_cache: str = ""
_insights_call_count: int = 0
_CACHE_TTL = 50  # refresh every 50 calls


def _init_db() -> None:
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    conn.execute("""
        CREATE TABLE IF NOT EXISTS customer_signals (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            signal_type TEXT NOT NULL,
            signal_value TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    conn.execute("CREATE INDEX IF NOT EXISTS idx_signal_type ON customer_signals(signal_type)")
    conn.commit()
    conn.close()


_init_db()


def extract_signals(text: str) -> list[tuple[str, str]]:
    signals = []
    lower = text.lower()

    # Budget
    match = _BUDGET_RE.search(text)
    if match:
        raw = (match.group(1) or match.group(2) or "").replace(" ", "")
        try:
            amount = int(raw)
            if 500 <= amount <= 200_000:
                # Bucket into ranges
                if amount < 2000:
                    bucket = "до 2000 ₽"
                elif amount < 5000:
                    bucket = "2000-5000 ₽"
                elif amount < 10000:
                    bucket = "5000-10000 ₽"
                else:
                    bucket = "от 10000 ₽"
                signals.append(("budget", bucket))
        except ValueError:
            pass

    # Occasion
    for keyword, label in _OCCASIONS.items():
        if keyword in lower:
            signals.append(("occasion", label))
            break

    # Product
    for keyword, label in _PRODUCTS.items():
        if keyword in lower:
            signals.append(("product", label))
            break

    # Question topic
    for keyword, label in _QUESTIONS.items():
        if keyword in lower:
            signals.append(("question", label))
            break

    return signals


async def record_signals(user_id: int, text: str) -> None:
    signals = extract_signals(text)
    if not signals:
        return
    try:
        conn = sqlite3.connect(DB_PATH)
        conn.executemany(
            "INSERT INTO customer_signals (user_id, signal_type, signal_value) VALUES (?, ?, ?)",
            [(user_id, stype, svalue) for stype, svalue in signals],
        )
        conn.commit()
        conn.close()
        logger.debug("Recorded %d signals for user %d", len(signals), user_id)
    except Exception:
        logger.exception("Failed to record learning signals")


def _build_insights() -> str:
    try:
        conn = sqlite3.connect(DB_PATH)

        total = conn.execute("SELECT COUNT(*) FROM customer_signals").fetchone()[0]
        if total < 10:
            conn.close()
            return ""

        def top3(signal_type: str) -> list[str]:
            rows = conn.execute(
                """SELECT signal_value, COUNT(*) as cnt
                   FROM customer_signals WHERE signal_type = ?
                   GROUP BY signal_value ORDER BY cnt DESC LIMIT 3""",
                (signal_type,),
            ).fetchall()
            return [r[0] for r in rows]

        budgets = top3("budget")
        occasions = top3("occasion")
        products = top3("product")
        conn.close()

        parts = []
        if budgets:
            parts.append(f"- Бюджеты клиентов: {', '.join(budgets)}")
        if occasions:
            parts.append(f"- Частые поводы: {', '.join(occasions)}")
        if products:
            parts.append(f"- Интересуют товары: {', '.join(products)}")

        if not parts:
            return ""

        return "РЕАЛЬНЫЕ ЗАПРОСЫ КЛИЕНТОВ (статистика из разговоров):\n" + "\n".join(parts)

    except Exception:
        logger.exception("Failed to build insights")
        return ""


def get_insights_text() -> str:
    global _insights_cache, _insights_call_count
    _insights_call_count += 1
    if _insights_call_count % _CACHE_TTL == 1 or not _insights_cache:
        _insights_cache = _build_insights()
    return _insights_cache
