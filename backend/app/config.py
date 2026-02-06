from pydantic_settings import BaseSettings
from functools import lru_cache
from typing import Optional

class Settings(BaseSettings):
    # Application
    app_name: str = "RedFlag AI"
    app_version: str = "1.0.0"
    debug: bool = True
    environment: str = "development"
    secret_key: str = "change-this-in-production"

    # Database
    database_url: str
    database_pool_size: int = 20

    # Redis
    redis_url: str
    celery_broker_url: str
    celery_result_backend: str

    # Storage
    r2_access_key_id: str
    r2_secret_access_key: str
    r2_bucket_name: str
    r2_endpoint_url: str
    r2_public_url: str  # Public URL for accessing uploaded files

    # AI
    gemini_api_key: str
    google_vision_api_key: Optional[str] = None

    # CORS
    frontend_url: str = "http://localhost:3000"

    # JWT
    jwt_secret_key: str
    jwt_algorithm: str = "HS256"
    access_token_expire_minutes: int = 1440

    # Payments
    razorpay_key_id: Optional[str] = None
    razorpay_key_secret: Optional[str] = None

    # Email (Brevo)
    brevo_api_key: Optional[str] = None
    from_email: Optional[str] = None
    from_name: Optional[str] = None

    # Web Push Notifications
    vapid_private_key: Optional[str] = None
    vapid_public_key: Optional[str] = None
    vapid_claim_email: Optional[str] = None

    class Config:
        env_file = ".env"
        case_sensitive = False

@lru_cache()
def get_settings() -> Settings:
    return Settings()

settings = get_settings()
