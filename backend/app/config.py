import os
from typing import Optional
from pydantic_settings import BaseSettings
from pydantic import Field

class Settings(BaseSettings):
    # Database
    database_url: str = Field(default="postgresql://user:password@localhost:5432/lazulite_ppt")
    
    # Redis
    redis_url: str = Field(default="redis://localhost:6379/0")
    
    # JWT
    secret_key: str = Field(default="your-secret-key-change-in-production")
    algorithm: str = Field(default="HS256")
    access_token_expire_minutes: int = Field(default=30)
    
    # OpenAI
    openai_api_key: Optional[str] = Field(default=None)
    
    # Anthropic (alternative to OpenAI)
    anthropic_api_key: Optional[str] = Field(default=None)
    
    # File Storage
    upload_dir: str = Field(default="uploads")
    generated_dir: str = Field(default="generated")
    template_dir: str = Field(default="templates")
    max_file_size: int = Field(default=10 * 1024 * 1024)  # 10MB
    
    # Scraping
    lazulite_base_url: str = Field(default="https://lazulite.ae/activations")
    selenium_timeout: int = Field(default=30)
    max_images_per_product: int = Field(default=10)
    
    # Celery
    celery_broker_url: str = Field(default="redis://localhost:6379/0")
    celery_result_backend: str = Field(default="redis://localhost:6379/0")
    
    # CORS
    allowed_origins: list = Field(default=["http://localhost:3000", "http://localhost:5173"])
    
    # Environment
    environment: str = Field(default="development")
    debug: bool = Field(default=True)
    
    class Config:
        env_file = ".env"
        case_sensitive = False

settings = Settings()