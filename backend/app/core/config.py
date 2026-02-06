"""
Application Configuration
Loads settings from environment variables with validation.
"""
from typing import List
from pydantic_settings import BaseSettings
from pydantic import Field
from functools import lru_cache


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""
    
    # Database
    DATABASE_URL: str = Field(
        default="sqlite:///./sme_finance.db",
        description="Database connection URL (SQLite for dev, PostgreSQL for prod)"
    )
    REDIS_URL: str = Field(
        default="redis://localhost:6379",
        description="Redis connection URL"
    )
    
    # Security
    SECRET_KEY: str = Field(
        default="your-secret-key-change-in-production",
        min_length=32,
        description="Secret key for JWT encoding"
    )
    ENCRYPTION_KEY: str = Field(
        default="your-32-byte-encryption-key-here",
        description="AES-256 encryption key"
    )
    JWT_EXPIRY_HOURS: int = Field(default=24, description="JWT token expiry in hours")
    JWT_REFRESH_EXPIRY_DAYS: int = Field(default=7, description="Refresh token expiry in days")
    JWT_ALGORITHM: str = Field(default="HS256", description="JWT algorithm")
    
    # LLM APIs
    OPENAI_API_KEY: str = Field(default="", description="OpenAI API key")
    ANTHROPIC_API_KEY: str = Field(default="", description="Anthropic API key")
    
    # File Storage
    UPLOAD_DIR: str = Field(default="./uploads", description="Upload directory path")
    TEMP_DIR: str = Field(default="./temp", description="Temporary files directory")
    MAX_FILE_SIZE_MB: int = Field(default=10, description="Maximum file size in MB")
    ALLOWED_EXTENSIONS: str = Field(
        default="csv,xlsx,pdf",
        description="Comma-separated allowed file extensions"
    )
    
    # Application
    DEBUG: bool = Field(default=True, description="Debug mode")
    CORS_ORIGINS: List[str] = Field(
        default=["http://localhost:3000", "http://localhost:5173"],
        description="Allowed CORS origins"
    )
    API_V1_PREFIX: str = Field(default="/api/v1", description="API version prefix")
    
    # Rate Limiting
    RATE_LIMIT_PER_MINUTE: int = Field(default=100, description="API rate limit per minute")
    
    @property
    def allowed_extensions_list(self) -> List[str]:
        """Get allowed extensions as a list."""
        return [ext.strip().lower() for ext in self.ALLOWED_EXTENSIONS.split(",")]
    
    @property
    def max_file_size_bytes(self) -> int:
        """Get max file size in bytes."""
        return self.MAX_FILE_SIZE_MB * 1024 * 1024
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = True


@lru_cache()
def get_settings() -> Settings:
    """Get cached settings instance."""
    return Settings()


settings = get_settings()
