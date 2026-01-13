"""Configuration management for Chiron."""
from pydantic_settings import BaseSettings
from functools import lru_cache


class Settings(BaseSettings):
    """Application settings."""

    # Database
    database_url: str = "postgresql://localhost:5432/chiron"

    # API Keys
    gemini_api_key: str
    api_secret_key: str

    # TrueCoach
    truecoach_client_id: str = ""
    truecoach_client_secret: str = ""
    truecoach_redirect_uri: str = "http://localhost:8000/auth/truecoach/callback"

    # MyFitnessPal
    mfp_username: str = ""
    mfp_password: str = ""

    # App Settings
    sync_interval_minutes: int = 30
    log_level: str = "INFO"

    class Config:
        env_file = ".env"
        case_sensitive = False


@lru_cache()
def get_settings() -> Settings:
    """Get cached settings instance."""
    return Settings()
