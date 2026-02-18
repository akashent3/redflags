"""Pydantic schemas for User model."""

from datetime import datetime
from typing import Optional
from uuid import UUID

from pydantic import BaseModel, EmailStr, Field, field_validator

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
    is_admin: bool  # Admin flag for access control
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
                "is_admin": False,
                "created_at": "2024-02-05T10:30:00Z",
                "updated_at": "2024-02-05T10:30:00Z",
                "last_login": None
            }
        }
    }


# Settings-related request schemas
class ProfileUpdateRequest(BaseModel):
    """Profile update request."""
    full_name: Optional[str] = Field(None, min_length=1, max_length=255, description="Full name")
    email: Optional[EmailStr] = Field(None, description="Email address")


class PasswordChangeRequest(BaseModel):
    """Password change request."""
    old_password: str = Field(..., min_length=8, description="Current password")
    new_password: str = Field(..., min_length=8, description="New password")

    @field_validator('new_password')
    @classmethod
    def validate_password_strength(cls, v):
        """Validate password strength."""
        if len(v) < 8:
            raise ValueError('Password must be at least 8 characters long')
        if not any(c.isupper() for c in v):
            raise ValueError('Password must contain at least one uppercase letter')
        if not any(c.islower() for c in v):
            raise ValueError('Password must contain at least one lowercase letter')
        if not any(c.isdigit() for c in v):
            raise ValueError('Password must contain at least one digit')
        return v


class AvatarUploadResponse(BaseModel):
    """Avatar upload response."""
    avatar_url: str = Field(..., description="Avatar URL in R2 storage")
    message: str = Field(..., description="Success message")


class DataExportRequest(BaseModel):
    """Data export request."""
    include_analyses: bool = Field(True, description="Include analysis history")
    include_watchlist: bool = Field(True, description="Include watchlist")
    include_portfolio: bool = Field(True, description="Include portfolio data")
    include_preferences: bool = Field(True, description="Include notification preferences")


class DataExportResponse(BaseModel):
    """Data export response."""
    task_id: str = Field(..., description="Celery task ID")
    message: str = Field(..., description="Status message")
    estimated_time_seconds: int = Field(30, description="Estimated completion time")


class DataExportStatusResponse(BaseModel):
    """Data export status response."""
    task_id: str = Field(..., description="Task ID")
    status: str = Field(..., description="Task status (PENDING, PROCESSING, SUCCESS, FAILURE)")
    download_url: Optional[str] = Field(None, description="Download URL if ready")
    error: Optional[str] = Field(None, description="Error message if failed")


class AccountDeletionResponse(BaseModel):
    """Account deletion response."""
    message: str = Field(..., description="Confirmation message")
    deleted_at: datetime = Field(..., description="Deletion timestamp")
    data_retention_days: int = Field(30, description="Days before permanent deletion")
