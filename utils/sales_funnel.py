from enum import Enum
from dataclasses import dataclass, field


class FunnelStage(Enum):
    START = "start"
    DISCOVERY = "discovery"          # Выявление потребностей
    PRESENTATION = "presentation"    # Презентация
    OBJECTION = "objection"          # Работа с возражениями
    CLOSING = "closing"              # Закрытие


@dataclass
class UserSession:
    user_id: int
    stage: FunnelStage = FunnelStage.START
    history: list[dict] = field(default_factory=list)
    name: str = ""

    def add_message(self, role: str, content: str):
        self.history.append({"role": role, "content": content})
        # Keep last N messages to avoid context overflow
        from config.settings import settings
        max_h = settings.MAX_HISTORY * 2
        if len(self.history) > max_h:
            self.history = self.history[-max_h:]

    def advance_stage(self):
        stages = list(FunnelStage)
        current_idx = stages.index(self.stage)
        if current_idx < len(stages) - 1:
            self.stage = stages[current_idx + 1]


# In-memory session storage (replace with Redis/DB for production)
sessions: dict[int, UserSession] = {}


def get_session(user_id: int) -> UserSession:
    if user_id not in sessions:
        sessions[user_id] = UserSession(user_id=user_id)
    return sessions[user_id]
