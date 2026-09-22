"""DocGen AI - Configuration"""
from pydantic_settings import BaseSettings
from functools import lru_cache


class Settings(BaseSettings):
    app_name: str = "DocGen AI"
    app_env: str = "development"
    database_url: str = "sqlite:///./docgen.db"
    gemini_api_key: str = ""
    groq_api_key: str = ""
    secret_key: str = "change-me-in-production"
    
    # PayPal Settings
    paypal_client_id: str = ""
    paypal_client_secret: str = ""
    paypal_plan_id: str = ""
    paypal_mode: str = "sandbox"  # 'sandbox' or 'live'

    class Config:
        env_file = ".env"


@lru_cache()
def get_settings() -> Settings:
    return Settings()
