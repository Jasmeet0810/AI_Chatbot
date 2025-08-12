import os
from typing import Optional
from pydantic_settings import BaseSettings
from pydantic import Field

class Settings(BaseSettings):
    # AWS Bedrock
    aws_access_key_id: Optional[str] = Field(default=None)
    aws_secret_access_key: Optional[str] = Field(default=None)
    aws_region: str = Field(default="us-east-1")
    
    # File Storage
    upload_dir: str = Field(default="uploads")
    generated_dir: str = Field(default="generated")
    template_dir: str = Field(default="templates")
    max_file_size: int = Field(default=10 * 1024 * 1024)  # 10MB
    
    # Scraping
    lazulite_base_url: str = Field(default="https://lazulite.ae/activations")
    selenium_timeout: int = Field(default=30)
    max_images_per_product: int = Field(default=10)
    
    # Environment
    environment: str = Field(default="development")
    debug: bool = Field(default=True)
    
    class Config:
        env_file = ".env"
        case_sensitive = False

settings = Settings()