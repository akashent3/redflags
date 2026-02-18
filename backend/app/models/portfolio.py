"""Portfolio models for tracking user holdings."""

from datetime import datetime
from typing import TYPE_CHECKING
from uuid import UUID, uuid4

from sqlalchemy import Column, DateTime, Float, ForeignKey, Integer, Numeric, String
from sqlalchemy.dialects.postgresql import UUID as PostgresUUID
from sqlalchemy.orm import relationship

from app.database import Base

if TYPE_CHECKING:
    from app.models.company import Company
    from app.models.user import User


class Portfolio(Base):
    """User's portfolio container."""

    __tablename__ = "portfolios"

    id = Column(PostgresUUID(as_uuid=True), primary_key=True, default=uuid4)
    user_id = Column(PostgresUUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)

    # Portfolio metadata
    name = Column(String(200), nullable=False, default="My Portfolio")
    description = Column(String(500), nullable=True)

    # Aggregated metrics (cached)
    total_investment = Column(Numeric(15, 2), nullable=False, default=0)
    average_risk_score = Column(Float, nullable=True)
    high_risk_count = Column(Integer, nullable=False, default=0)

    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    # Relationships
    user = relationship("User", back_populates="portfolios")
    holdings = relationship("Holding", back_populates="portfolio", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<Portfolio id={self.id} user_id={self.user_id} name={self.name}>"


class Holding(Base):
    """Individual holding within a portfolio."""

    __tablename__ = "holdings"

    id = Column(PostgresUUID(as_uuid=True), primary_key=True, default=uuid4)
    portfolio_id = Column(PostgresUUID(as_uuid=True), ForeignKey("portfolios.id", ondelete="CASCADE"), nullable=False, index=True)
    company_id = Column(PostgresUUID(as_uuid=True), ForeignKey("companies.id", ondelete="SET NULL"), nullable=True, index=True)

    # Holding details
    symbol = Column(String(50), nullable=False)
    company_name = Column(String(300), nullable=False)
    quantity = Column(Integer, nullable=False)
    avg_price = Column(Numeric(15, 2), nullable=False)
    investment_value = Column(Numeric(15, 2), nullable=False)

    # Risk data (from latest analysis, if available)
    risk_score = Column(Integer, nullable=True)
    risk_level = Column(String(20), nullable=True)  # LOW, MEDIUM, HIGH, CRITICAL
    flags_count = Column(Integer, nullable=True)
    latest_analysis_id = Column(String(36), nullable=True)  # UUID of latest AnalysisResult for View Report link

    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    # Relationships
    portfolio = relationship("Portfolio", back_populates="holdings")
    company = relationship("Company")

    def __repr__(self):
        return f"<Holding symbol={self.symbol} quantity={self.quantity} portfolio_id={self.portfolio_id}>"
