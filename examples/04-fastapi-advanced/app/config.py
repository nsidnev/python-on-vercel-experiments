"""
Configuration management for FastAPI Advanced Example
"""

import os
from typing import Optional


class Settings:
    """Application settings loaded from environment variables"""

    # Application
    APP_NAME: str = "FastAPI Advanced on Vercel"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = os.getenv("DEBUG", "false").lower() == "true"

    # API Configuration
    API_PREFIX: str = "/api"
    ALLOWED_ORIGINS: list[str] = [
        "http://localhost:3000",
        "http://localhost:8000",
        "https://*.vercel.app",
    ]

    # Feature Flags
    ENABLE_DOCS: bool = os.getenv("ENABLE_DOCS", "true").lower() == "true"

    # External Services (example)
    EXTERNAL_API_KEY: Optional[str] = os.getenv("EXTERNAL_API_KEY")
    EXTERNAL_API_URL: Optional[str] = os.getenv("EXTERNAL_API_URL")


settings = Settings()
