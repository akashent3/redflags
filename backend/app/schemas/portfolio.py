"""Portfolio schemas for API requests and responses."""

from datetime import datetime
from typing import List, Optional
from uuid import UUID

from pydantic import BaseModel, Field


# Request schemas
class HoldingCreate(BaseModel):
    """Individual holding in CSV."""
    symbol: str = Field(..., description="Stock symbol")
    quantity: int = Field(..., gt=0, description="Number of shares")
    avg_price: float = Field(..., gt=0, description="Average purchase price")


class PortfolioCreate(BaseModel):
    """Request to create portfolio from CSV."""
    name: str = Field("My Portfolio", max_length=200, description="Portfolio name")
    description: Optional[str] = Field(None, max_length=500, description="Portfolio description")
    holdings: List[HoldingCreate] = Field(..., min_items=1, description="List of holdings from CSV")


# Response schemas
class HoldingResponse(BaseModel):
    """Individual holding response."""
    holding_id: UUID = Field(..., description="Holding ID")
    symbol: str = Field(..., description="Stock symbol")
    company_name: str = Field(..., description="Company name")
    quantity: int = Field(..., description="Number of shares")
    avg_price: float = Field(..., description="Average purchase price")
    investment_value: float = Field(..., description="Total investment value")
    risk_score: Optional[int] = Field(None, description="Risk score from latest analysis")
    risk_level: Optional[str] = Field(None, description="Risk level: LOW, MEDIUM, HIGH, CRITICAL")
    flags_count: Optional[int] = Field(None, description="Number of red flags")

    class Config:
        from_attributes = True


class PortfolioResponse(BaseModel):
    """Portfolio response."""
    portfolio_id: UUID = Field(..., description="Portfolio ID")
    user_id: UUID = Field(..., description="User ID")
    name: str = Field(..., description="Portfolio name")
    description: Optional[str] = Field(None, description="Portfolio description")
    holdings: List[HoldingResponse] = Field(..., description="Holdings in portfolio")
    total_investment: float = Field(..., description="Total investment value")
    average_risk_score: Optional[float] = Field(None, description="Average risk score across holdings")
    high_risk_count: int = Field(..., description="Number of high risk holdings (score >= 60)")
    created_at: datetime = Field(..., description="Portfolio creation date")
    updated_at: datetime = Field(..., description="Last update date")

    class Config:
        from_attributes = True


class PortfolioListResponse(BaseModel):
    """List of user's portfolios."""
    portfolios: List[PortfolioResponse] = Field(..., description="User's portfolios")
    total: int = Field(..., description="Total number of portfolios")

    class Config:
        from_attributes = True


class CSVUploadResponse(BaseModel):
    """Response after CSV upload and processing."""
    portfolio_id: UUID = Field(..., description="Created portfolio ID")
    total_holdings: int = Field(..., description="Number of holdings processed")
    matched_companies: int = Field(..., description="Companies matched in database")
    unmatched_symbols: List[str] = Field(..., description="Symbols not found in database")
    total_investment: float = Field(..., description="Total investment value")

    class Config:
        from_attributes = True
