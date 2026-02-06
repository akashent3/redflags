"""Watchlist schemas for API requests and responses."""

from datetime import datetime
from typing import List, Optional
from uuid import UUID

from pydantic import BaseModel, Field


# Request schemas
class WatchlistItemCreate(BaseModel):
    """Request to add company to watchlist."""
    company_id: UUID = Field(..., description="Company UUID to watch")
    alert_enabled: bool = Field(True, description="Enable alerts for this company")


class WatchlistAlertMarkRead(BaseModel):
    """Request to mark alert as read."""
    is_read: bool = Field(True, description="Mark as read (true) or unread (false)")


class NotificationPreferencesUpdate(BaseModel):
    """Request to update notification preferences."""
    email_alerts_enabled: Optional[bool] = Field(None, description="Enable email alerts")
    weekly_digest_enabled: Optional[bool] = Field(None, description="Enable weekly digest")
    feature_announcements_enabled: Optional[bool] = Field(None, description="Enable feature announcements")
    push_notifications_enabled: Optional[bool] = Field(None, description="Enable push notifications (Premium only)")
    alert_frequency: Optional[str] = Field(None, description="Alert frequency: real_time, daily, weekly, none")


# Response schemas
class WatchlistItemResponse(BaseModel):
    """Watchlist item response."""
    watchlist_id: UUID = Field(..., description="Watchlist item ID")
    company_id: UUID = Field(..., description="Company ID")
    symbol: str = Field(..., description="Company symbol")
    company_name: str = Field(..., description="Company name")
    industry: str = Field(..., description="Industry")
    sector: str = Field(..., description="Sector")
    current_risk_score: Optional[int] = Field(None, description="Current risk score")
    current_risk_level: Optional[str] = Field(None, description="Current risk level")
    previous_risk_score: Optional[int] = Field(None, description="Previous risk score")
    score_change: Optional[int] = Field(None, description="Score change")
    last_analysis_date: Optional[datetime] = Field(None, description="Last analysis date")
    added_date: datetime = Field(..., description="Date added to watchlist")
    alert_enabled: bool = Field(..., description="Alerts enabled")

    class Config:
        from_attributes = True


class WatchlistAlertResponse(BaseModel):
    """Watchlist alert response."""
    alert_id: UUID = Field(..., description="Alert ID")
    company_id: UUID = Field(..., description="Company ID")
    symbol: str = Field(..., description="Company symbol")
    company_name: str = Field(..., description="Company name")
    alert_type: str = Field(..., description="Alert type: SCORE_CHANGE, NEW_FLAGS, NEW_REPORT")
    severity: str = Field(..., description="Severity: INFO, WARNING, CRITICAL")
    message: str = Field(..., description="Alert message")
    created_at: datetime = Field(..., description="Alert creation time")
    is_read: bool = Field(..., description="Read status")
    previous_risk_score: Optional[int] = Field(None, description="Previous risk score")
    current_risk_score: Optional[int] = Field(None, description="Current risk score")
    score_change: Optional[int] = Field(None, description="Score change")

    class Config:
        from_attributes = True


class WatchlistResponse(BaseModel):
    """Complete watchlist response."""
    user_id: UUID = Field(..., description="User ID")
    items: List[WatchlistItemResponse] = Field(..., description="Watchlist items")
    total_watched: int = Field(..., description="Total watched companies")
    recent_alerts: List[WatchlistAlertResponse] = Field(..., description="Recent alerts")

    class Config:
        from_attributes = True


class NotificationPreferencesResponse(BaseModel):
    """Notification preferences response."""
    user_id: UUID = Field(..., description="User ID")
    email_alerts_enabled: bool = Field(..., description="Email alerts enabled")
    weekly_digest_enabled: bool = Field(..., description="Weekly digest enabled")
    feature_announcements_enabled: bool = Field(..., description="Feature announcements enabled")
    push_notifications_enabled: bool = Field(..., description="Push notifications enabled")
    alert_frequency: str = Field(..., description="Alert frequency")
    created_at: datetime = Field(..., description="Created at")
    updated_at: datetime = Field(..., description="Updated at")

    class Config:
        from_attributes = True
