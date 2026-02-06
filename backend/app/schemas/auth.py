"""Pydantic schemas for authentication requests and responses."""

from typing import Optional

from pydantic import BaseModel, EmailStr, Field


class SignupRequest(BaseModel):
    """Signup request with email and password."""

    email: EmailStr
    password: str = Field(
        min_length=8,
        max_length=128,
        description="Password (8-128 characters, must include uppercase, lowercase, digit, and special character)"
    )
    full_name: Optional[str] = Field(
        None,
        max_length=255,
        description="User's full name (optional)"
    )

    model_config = {
        "json_schema_extra": {
            "example": {
                "email": "user@example.com",
                "password": "SecurePass123!",
                "full_name": "John Doe"
            }
        }
    }


class LoginRequest(BaseModel):
    """Login request with email and password."""

    email: EmailStr
    password: str

    model_config = {
        "json_schema_extra": {
            "example": {
                "email": "user@example.com",
                "password": "SecurePass123!"
            }
        }
    }


class TokenResponse(BaseModel):
    """JWT access token response."""

    access_token: str
    token_type: str = "bearer"

    model_config = {
        "json_schema_extra": {
            "example": {
                "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
                "token_type": "bearer"
            }
        }
    }


class MessageResponse(BaseModel):
    """Generic message response."""

    message: str

    model_config = {
        "json_schema_extra": {
            "example": {
                "message": "Operation successful"
            }
        }
    }
