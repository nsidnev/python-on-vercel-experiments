"""Application settings and configuration"""

from typing import Optional
from pydantic import computed_field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application configuration settings"""

    database_url: str
    app_name: str = "Tetris Game"
    debug: bool = False
    environment: str = "dev"

    # OAuth settings
    github_client_id: str
    github_client_secret: str
    secret_key: str

    # Auth URLs
    base_url: Optional[str] = None

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
    )

    @computed_field
    @property
    def cors_origins(self) -> list[str]:
        """Get CORS allowed origins based on environment"""
        vercel_hosts = [
            "https://tetris-nsidnev.vercel.app"
            "https://tetris-*-nsidnev.vercel.app",

        ]

        if self.environment == "dev":
            return [
                "http://localhost:3000",
                "http://127.0.0.1:3000",
                *vercel_hosts,
            ]

        return vercel_hosts

    @computed_field
    @property
    def async_database_url(self) -> str:
        """Convert PostgreSQL URL to async driver (asyncpg) and handle SSL params"""
        url = self.database_url

        # Replace driver with asyncpg
        if url.startswith("postgresql://"):
            url = url.replace("postgresql://", "postgresql+asyncpg://", 1)
        elif url.startswith("postgres://"):
            url = url.replace("postgres://", "postgresql+asyncpg://", 1)

        # Convert sslmode to ssl parameter for asyncpg
        if "sslmode=require" in url:
            url = url.replace("sslmode=require", "ssl=require")
        elif "sslmode=" in url:
            # Remove other sslmode values and add ssl=true for any SSL requirement
            import re
            url = re.sub(r'[?&]sslmode=[^&]*', '', url)
            separator = '&' if '?' in url else '?'
            url = f"{url}{separator}ssl=require"

        return url


settings = Settings()
