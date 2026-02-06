"""User schemas for profile management."""

from pydantic import BaseModel, EmailStr, Field
from typing import Optional


class ProfileUpdate(BaseModel):
    """Request to update user profile."""
    full_name: Optional[str] = Field(None, max_length=255, description="User's full name")
    email: Optional[EmailStr] = Field(None, description="User's email address")


class PasswordChange(BaseModel):
    """Request to change password."""
    old_password: str = Field(..., min_length=1, description="Current password")
    new_password: str = Field(..., min_length=8, description="New password (min 8 characters)")


class UserProfileResponse(BaseModel):
    """User profile response."""
    full_name: Optional[str] = Field(None, description="User's full name")
    email: str = Field(..., description="User's email")
    subscription_tier: str = Field(..., description="Subscription tier")
    reports_used_this_month: int = Field(..., description="Reports used this month")
    reports_limit: int = Field(..., description="Monthly report limit")

    class Config:
        from_attributes = True
