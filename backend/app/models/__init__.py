"""Database models for RedFlag AI."""

from app.database import Base
from app.models.user import User, SubscriptionTier
from app.models.company import Company
from app.models.annual_report import AnnualReport
from app.models.analysis_result import AnalysisResult
from app.models.red_flag import RedFlag, FlagSeverity, FlagCategory
from app.models.watchlist import WatchlistItem, WatchlistAlert, NotificationPreference
from app.models.portfolio import Portfolio, Holding

# Export all models
__all__ = [
    "Base",
    "User",
    "SubscriptionTier",
    "Company",
    "AnnualReport",
    "AnalysisResult",
    "RedFlag",
    "FlagSeverity",
    "FlagCategory",
    "WatchlistItem",
    "WatchlistAlert",
    "NotificationPreference",
    "Portfolio",
    "Holding",
]
