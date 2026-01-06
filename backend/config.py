"""
Configuration management for HealthRAG Backend API.

Uses Pydantic Settings for environment variable validation and type safety.
"""

from pydantic_settings import BaseSettings
from typing import List


class Settings(BaseSettings):
    """
    Application settings loaded from environment variables.

    All settings are validated and typed using Pydantic.
    """

    # Supabase Configuration
    supabase_url: str
    supabase_key: str
    supabase_service_key: str

    # Database Configuration
    database_url: str

    # JWT Configuration
    jwt_secret_key: str
    jwt_algorithm: str = "HS256"
    access_token_expire_minutes: int = 15

    # API Configuration
    api_host: str = "0.0.0.0"
    api_port: int = 8000
    environment: str = "development"

    # CORS Configuration
    cors_origins: str = "http://localhost:3000,http://localhost:8501"

    # External APIs
    usda_fdc_api_key: str = ""
    off_api_base_url: str = "https://world.openfoodfacts.org"

    class Config:
        env_file = ".env"
        case_sensitive = False

    @property
    def cors_origins_list(self) -> List[str]:
        """Parse CORS origins from comma-separated string"""
        return [origin.strip() for origin in self.cors_origins.split(",")]


# Global settings instance
settings = Settings()
