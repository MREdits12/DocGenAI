"""DocGen AI - Configuration"""
from pydantic_settings import BaseSettings
from functools import lru_cache


class Settings(BaseSettings):
    app_name: str = "DocGen AI"
    app_env: str = "development"
    database_url: str = "sqlite:///./docgen.db"
    gemini_api_key: str = ""
    secret_key: str = "change-me-in-production"
    
    # Stripe Settings
    stripe_secret_key: str = ""
    stripe_webhook_secret: str = ""
    stripe_pro_price_id: str = ""

    class Config:
        env_file = ".env"


@lru_cache()
def get_settings() -> Settings:
    return Settings()
