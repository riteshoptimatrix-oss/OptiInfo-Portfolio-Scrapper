from typing import List, Union
from pydantic import AnyHttpUrl, validator
from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    PROJECT_NAME: str = "OptiInfo Portfolio Scraper API"
    VERSION: str = "1.0.0"
    API_V1_STR: str = "/api"
    LOG_LEVEL: str = "INFO"

    # Database
    DATABASE_URL: str = "sqlite:///./portfolio_scraper.db"

    # Playwright Scraper
    TARGET_URL: str = "https://www.optiinfo.com/our-works/"
    HEADLESS: bool = True
    NAVIGATION_TIMEOUT_MS: int = 30000
    MAX_RETRIES: int = 3

    # CORS Configuration
    CORS_ORIGINS: List[str] = [
        "http://localhost:3000",
        "http://127.0.0.1:3000",
        "http://localhost:3001",
    ]

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

settings = Settings()
