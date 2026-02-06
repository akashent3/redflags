"""Pydantic schemas for User model."""

from datetime import datetime
from typing import Optional
from uuid import UUID

from pydantic import BaseModel, EmailStr

from app.models.user import SubscriptionTier


class UserResponse(BaseModel):
    """User data response (public fields only)."""

    id: UUID
    email: str
    full_name: Optional[str]
    subscription_tier: SubscriptionTier
    subscription_active: bool
    reports_used_this_month: int
    reports_limit: int
    is_active: bool
    is_verified: bool
    created_at: datetime
    updated_at: datetime
    last_login: Optional[datetime]

    model_config = {
        "from_attributes": True,  # SQLAlchemy 2.0 compatibility (was orm_mode)
        "json_schema_extra": {
            "example": {
                "id": "123e4567-e89b-12d3-a456-426614174000",
                "email": "user@example.com",
                "full_name": "John Doe",
                "subscription_tier": "free",
                "subscription_active": True,
                "reports_used_this_month": 1,
                "reports_limit": 3,
                "is_active": True,
                "is_verified": False,
                "created_at": "2024-02-05T10:30:00Z",
                "updated_at": "2024-02-05T10:30:00Z",
                "last_login": None
            }
        }
    }
