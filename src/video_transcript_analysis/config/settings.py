from typing import Optional
from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import Field, SecretStr

class Settings(BaseSettings):
    """Application settings with environment variable support."""
    
    # API Configuration
    GEMINI_API_KEY: SecretStr = Field(..., env='GEMINI_API_KEY')
    GEMINI_MODEL: str = Field(default="gemini-pro", env='GEMINI_MODEL')
    MAX_RETRIES: int = Field(default=3, env='MAX_RETRIES')
    RETRY_DELAY: float = Field(default=1.0, env='RETRY_DELAY')
    
    # Cache Configuration
    CACHE_TTL: int = Field(default=3600, env='CACHE_TTL')  # 1 hour
    CACHE_MAX_SIZE: int = Field(default=1000, env='CACHE_MAX_SIZE')
    REDIS_URL: Optional[str] = Field(default=None, env='REDIS_URL')
    
    # Processing Configuration
    MAX_CHUNK_SIZE: int = Field(default=1000, env='MAX_CHUNK_SIZE')
    CHUNK_OVERLAP: int = Field(default=100, env='CHUNK_OVERLAP')
    BATCH_SIZE: int = Field(default=5, env='BATCH_SIZE')
    
    # Monitoring
    ENABLE_METRICS: bool = Field(default=True, env='ENABLE_METRICS')
    PROMETHEUS_PORT: int = Field(default=9090, env='PROMETHEUS_PORT')
    
    # Security
    MAX_TOKENS_PER_REQUEST: int = Field(default=8000, env='MAX_TOKENS_PER_REQUEST')
    RATE_LIMIT_REQUESTS: int = Field(default=60, env='RATE_LIMIT_REQUESTS')
    RATE_LIMIT_PERIOD: int = Field(default=60, env='RATE_LIMIT_PERIOD')
    
    model_config = SettingsConfigDict(
        env_file='.env',
        env_file_encoding='utf-8',
        case_sensitive=True
    )

# Global settings instance
settings = Settings() 