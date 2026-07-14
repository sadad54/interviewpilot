from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    groq_api_key: str | None = None
    database_url: str = "sqlite:///./interviewpilot.db"

    model_config = SettingsConfigDict(env_file=".env")

settings = Settings()