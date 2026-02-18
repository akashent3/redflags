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
    """Watchlist item response with real-time price data."""
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
    
    # Real-time price data (NEW)
    current_price: Optional[float] = Field(None, description="Current market price")
    price_change: Optional[float] = Field(None, description="Price change (absolute)")
    price_change_percent: Optional[float] = Field(None, description="Price change (%)")
    high: Optional[float] = Field(None, description="Day high")
    low: Optional[float] = Field(None, description="Day low")
    volume: Optional[int] = Field(None, description="Trading volume")
    auto_analysis_triggered: bool = Field(False, description="Whether analysis was auto-triggered")
    latest_analysis_id: Optional[UUID] = Field(None, description="Latest analysis result ID for report navigation")

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
    alerts: List[WatchlistAlertResponse] = Field(..., description="Recent alerts")

    class Config:
        from_attributes = True


class NotificationPreferencesResponse(BaseModel):
    """Notification preferences response."""
    user_id: UUID
    email_alerts_enabled: bool
    weekly_digest_enabled: bool
    feature_announcements_enabled: bool
    push_notifications_enabled: bool
    alert_frequency: str

    class Config:
        from_attributes = True