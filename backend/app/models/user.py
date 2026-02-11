"""User model for authentication and subscription management."""

from sqlalchemy import Column, String, Boolean, Integer, DateTime, Enum as SQLEnum
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import uuid
import enum
from app.database import Base


class SubscriptionTier(str, enum.Enum):
    """Subscription tier enumeration."""
    FREE = "free"
    PRO = "pro"
    PREMIUM = "premium"


class User(Base):
    """User model with authentication and subscription info."""

    __tablename__ = "users"

    # Primary Key
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)

    # Authentication
    email = Column(String(255), unique=True, nullable=False, index=True)
    hashed_password = Column(String(255), nullable=False)
    full_name = Column(String(255), nullable=True)

    # Subscription & Usage
    subscription_tier = Column(
        SQLEnum(SubscriptionTier),
        default=SubscriptionTier.FREE,
        nullable=False
    )
    subscription_active = Column(Boolean, default=True, nullable=False)
    reports_used_this_month = Column(Integer, default=0, nullable=False)
    reports_limit = Column(Integer, default=999999, nullable=False)  # Unlimited for now

    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    last_login = Column(DateTime(timezone=True), nullable=True)

    # Status
    is_active = Column(Boolean, default=True, nullable=False)
    is_verified = Column(Boolean, default=False, nullable=False)
    verification_token = Column(String(255), nullable=True)

    # Relationships
    watchlist_items = relationship("WatchlistItem", back_populates="user", cascade="all, delete-orphan")
    portfolios = relationship("Portfolio", back_populates="user", cascade="all, delete-orphan")
    notification_preferences = relationship("NotificationPreference", back_populates="user", uselist=False, cascade="all, delete-orphan")

    def __repr__(self):
        return f"<User(email='{self.email}', tier='{self.subscription_tier}')>"

    @property
    def can_analyze(self) -> bool:
        """Check if user can perform more analyses this month."""
        # Unlimited for now - payment gateway disabled
        return True

    def increment_usage(self):
        """Increment monthly report usage counter."""
        self.reports_used_this_month += 1

    def reset_monthly_usage(self):
        """Reset monthly usage counter (call on 1st of each month)."""
        self.reports_used_this_month = 0
