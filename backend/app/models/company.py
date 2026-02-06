"""Company model for BSE/NSE listed companies."""

from sqlalchemy import Column, String, Boolean, Integer, DECIMAL, DateTime, Index
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func
import uuid
from app.database import Base


class Company(Base):
    """Model for BSE/NSE listed companies."""

    __tablename__ = "companies"

    # Primary Key
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)

    # Basic Info
    name = Column(String(255), nullable=False, index=True)

    # Stock Identifiers
    bse_code = Column(String(10), nullable=True, index=True)
    nse_symbol = Column(String(20), nullable=True, index=True)
    isin = Column(String(12), nullable=True, unique=True)

    # Classification
    industry = Column(String(100), nullable=True)
    sector = Column(String(100), nullable=True)

    # Market Data
    market_cap_cr = Column(DECIMAL(20, 2), nullable=True)  # Market cap in Crores

    # Flags
    is_nifty_50 = Column(Boolean, default=False, nullable=False)
    is_nifty_500 = Column(Boolean, default=False, nullable=False, index=True)
    is_active = Column(Boolean, default=True, nullable=False)

    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Additional indexes for search
    __table_args__ = (
        Index('idx_company_search', 'name'),
        Index('idx_company_nifty500', 'is_nifty_500'),
    )

    def __repr__(self):
        return f"<Company(name='{self.name}', nse='{self.nse_symbol}')>"

    @property
    def display_code(self) -> str:
        """Return NSE symbol if available, otherwise BSE code."""
        return self.nse_symbol or self.bse_code or "N/A"

    @property
    def is_nifty(self) -> bool:
        """Check if company is in any NIFTY index."""
        return self.is_nifty_50 or self.is_nifty_500
