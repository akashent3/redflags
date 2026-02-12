"""Dashboard schemas for API responses."""

from typing import List, Optional
from pydantic import BaseModel, Field


class RecentAnalysisSchema(BaseModel):
    """Recent analysis item in dashboard."""
    
    analysis_id: str = Field(..., description="Analysis result ID")  # ✅ Primary ID
    report_id: str = Field(..., description="Annual report ID")  # Keep for reference
    company_name: str = Field(..., description="Company name")
    symbol: str = Field(..., description="NSE/BSE symbol")
    fiscal_year: str = Field(..., description="Fiscal year (e.g., '2024-2025')")
    risk_score: int = Field(..., ge=0, le=100, description="Risk score (0-100)")
    risk_level: str = Field(..., description="Risk level (LOW/MODERATE/HIGH/CRITICAL)")
    flags_triggered: int = Field(..., ge=0, description="Number of flags triggered")
    analyzed_at: Optional[str] = Field(None, description="Analysis timestamp")


class DashboardStatsResponse(BaseModel):
    """Dashboard statistics response."""
    
    total_reports: int = Field(..., ge=0, description="Total completed reports")
    avg_risk_score: int = Field(..., ge=0, le=100, description="Average risk score")
    total_red_flags: int = Field(..., ge=0, description="Total red flags triggered")
    last_analysis_date: Optional[str] = Field(None, description="Last analysis date ISO format")
    recent_analyses: List[RecentAnalysisSchema] = Field(default_factory=list, description="List of recent analyses")