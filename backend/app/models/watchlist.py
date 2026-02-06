"""Watchlist models for tracking companies and alerts."""

from datetime import datetime
from typing import TYPE_CHECKING
from uuid import UUID, uuid4

from sqlalchemy import Boolean, Column, DateTime, Enum, ForeignKey, Integer, String, Text
from sqlalchemy.dialects.postgresql import UUID as PostgresUUID
from sqlalchemy.orm import relationship

from app.database import Base

if TYPE_CHECKING:
    from app.models.company import Company
    from app.models.user import User


class WatchlistItem(Base):
    """User's watchlist item for tracking a company."""

    __tablename__ = "watchlist_items"

    id = Column(PostgresUUID(as_uuid=True), primary_key=True, default=uuid4)
    user_id = Column(PostgresUUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    company_id = Column(PostgresUUID(as_uuid=True), ForeignKey("companies.id", ondelete="CASCADE"), nullable=False, index=True)

    # Tracking
    added_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    alert_enabled = Column(Boolean, default=True, nullable=False)

    # Last known risk score for change detection
    last_known_risk_score = Column(Integer, nullable=True)
    last_checked_at = Column(DateTime, nullable=True)

    # Relationships
    user = relationship("User", back_populates="watchlist_items")
    company = relationship("Company")
    alerts = relationship("WatchlistAlert", back_populates="watchlist_item", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<WatchlistItem user_id={self.user_id} company_id={self.company_id}>"


class WatchlistAlert(Base):
    """Alerts generated for watchlist items."""

    __tablename__ = "watchlist_alerts"

    id = Column(PostgresUUID(as_uuid=True), primary_key=True, default=uuid4)
    watchlist_item_id = Column(PostgresUUID(as_uuid=True), ForeignKey("watchlist_items.id", ondelete="CASCADE"), nullable=False, index=True)

    # Alert details
    alert_type = Column(Enum("SCORE_CHANGE", "NEW_FLAGS", "NEW_REPORT", name="alert_type_enum"), nullable=False)
    severity = Column(Enum("INFO", "WARNING", "CRITICAL", name="alert_severity_enum"), nullable=False)
    message = Column(Text, nullable=False)

    # Metadata
    previous_risk_score = Column(Integer, nullable=True)
    current_risk_score = Column(Integer, nullable=True)
    score_change = Column(Integer, nullable=True)

    # Status
    is_read = Column(Boolean, default=False, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    read_at = Column(DateTime, nullable=True)

    # Relationships
    watchlist_item = relationship("WatchlistItem", back_populates="alerts")

    def __repr__(self):
        return f"<WatchlistAlert type={self.alert_type} severity={self.severity}>"


class NotificationPreference(Base):
    """User notification preferences."""

    __tablename__ = "notification_preferences"

    id = Column(PostgresUUID(as_uuid=True), primary_key=True, default=uuid4)
    user_id = Column(PostgresUUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, unique=True, index=True)

    # Email preferences
    email_alerts_enabled = Column(Boolean, default=True, nullable=False)
    weekly_digest_enabled = Column(Boolean, default=True, nullable=False)
    feature_announcements_enabled = Column(Boolean, default=True, nullable=False)

    # Push notification preferences (Premium only)
    push_notifications_enabled = Column(Boolean, default=False, nullable=False)
    push_subscription_endpoint = Column(String(500), nullable=True)
    push_subscription_keys = Column(Text, nullable=True)  # JSON string

    # Alert frequency
    alert_frequency = Column(
        Enum("real_time", "daily", "weekly", "none", name="alert_frequency_enum"),
        default="weekly",
        nullable=False
    )

    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    # Relationships
    user = relationship("User", back_populates="notification_preferences")

    def __repr__(self):
        return f"<NotificationPreference user_id={self.user_id}>"
