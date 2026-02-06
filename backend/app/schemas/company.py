"""Pydantic schemas for company data."""

from datetime import datetime
from typing import Optional
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field


class CompanyBase(BaseModel):
    """Base company schema with common fields."""

    name: str = Field(..., description="Company name")
    bse_code: Optional[str] = Field(None, description="BSE company code")
    nse_symbol: Optional[str] = Field(None, description="NSE symbol")
    isin: Optional[str] = Field(None, description="ISIN code")
    industry: Optional[str] = Field(None, description="Industry classification")
    sector: Optional[str] = Field(None, description="Sector classification")
    market_cap_cr: Optional[float] = Field(None, description="Market cap in Crores")
    is_nifty_50: bool = Field(False, description="Is in NIFTY 50")
    is_nifty_500: bool = Field(False, description="Is in NIFTY 500")
    is_active: bool = Field(True, description="Is company active")


class CompanyResponse(CompanyBase):
    """Company response schema."""

    id: UUID = Field(..., description="Company UUID")
    display_code: str = Field(..., description="NSE symbol or BSE code")
    is_nifty: bool = Field(..., description="Is in any NIFTY index")
    created_at: datetime = Field(..., description="Creation timestamp")
    updated_at: Optional[datetime] = Field(None, description="Last update timestamp")

    model_config = ConfigDict(from_attributes=True)


class CompanySearchResult(BaseModel):
    """Single company in search results."""

    id: UUID = Field(..., description="Company UUID")
    name: str = Field(..., description="Company name")
    display_code: str = Field(..., description="NSE symbol or BSE code")
    industry: Optional[str] = Field(None, description="Industry")
    sector: Optional[str] = Field(None, description="Sector")
    is_nifty_50: bool = Field(False, description="Is in NIFTY 50")
    is_nifty_500: bool = Field(False, description="Is in NIFTY 500")
    market_cap_cr: Optional[float] = Field(None, description="Market cap in Crores")

    model_config = ConfigDict(from_attributes=True)


class CompanySearchResponse(BaseModel):
    """Response for company search."""

    total: int = Field(..., description="Total number of results")
    results: list[CompanySearchResult] = Field(..., description="List of matching companies")


class CompanyDetailResponse(CompanyResponse):
    """Detailed company information with related data."""

    total_reports: int = Field(0, description="Total number of annual reports")
    latest_report_year: Optional[int] = Field(None, description="Most recent fiscal year")
    earliest_report_year: Optional[int] = Field(None, description="Oldest fiscal year")
