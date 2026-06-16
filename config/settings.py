from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    TELEGRAM_BOT_TOKEN: str
    OPENROUTER_API_KEY: str
    MANAGER_CHAT_ID: str = ""
    AI_MODEL: str = "openai/gpt-4o-mini"
    MAX_HISTORY: int = 10
    LOG_LEVEL: str = "INFO"

    class Config:
        env_file = ".env"


settings = Settings()
