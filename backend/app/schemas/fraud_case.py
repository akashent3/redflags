"""Fraud case schemas for API requests and responses."""

from datetime import datetime
from typing import List, Optional
from uuid import UUID

from pydantic import BaseModel, Field


# Response schemas
class FraudCaseResponse(BaseModel):
    """Fraud case response — full detail including all JSONB fields for the Learn page."""
    id: UUID = Field(..., description="Fraud case ID")
    case_id: str = Field(..., description="Unique case identifier (e.g., 'satyam-2009')")
    company_name: str = Field(..., description="Company name")
    year: int = Field(..., description="Year of fraud")
    sector: Optional[str] = Field(None, description="Sector")
    industry: Optional[str] = Field(None, description="Industry")
    fraud_type: str = Field(..., description="Type of fraud")
    detection_difficulty: Optional[str] = Field(None, description="Detection difficulty")
    stock_decline_percent: Optional[float] = Field(None, description="Stock decline percentage")
    market_cap_lost_cr: Optional[float] = Field(None, description="Market cap lost (crores)")
    primary_flags: Optional[List[str]] = Field(None, description="Primary red flags")
    # Detail fields — stored as JSONB in DB, used by Learn page detail view
    red_flags_detected: Optional[List[dict]] = Field(None, description="Detailed red flag objects with flag_number, flag_name, category, severity, evidence")
    timeline: Optional[List[dict]] = Field(None, description="Chronological events [{date, event, type}]")
    what_investors_missed: Optional[List[str]] = Field(None, description="Key warning signs investors ignored")
    lessons_learned: Optional[List[str]] = Field(None, description="Actionable lessons for investors")
    outcome: Optional[str] = Field(None, description="What happened after the fraud was exposed")
    regulatory_action: Optional[str] = Field(None, description="SEBI/CBI/ED/RBI regulatory response")
    created_at: datetime = Field(..., description="Creation date")

    class Config:
        from_attributes = True


class PatternMatchResult(BaseModel):
    """Individual pattern match result."""
    case_id: str = Field(..., description="Fraud case ID")
    company_name: str = Field(..., description="Company name")
    year: int = Field(..., description="Year of fraud")
    similarity_score: float = Field(..., description="Similarity percentage")
    matching_flags: List[dict] = Field(..., description="Matching red flags")
    stock_decline_percent: Optional[float] = Field(None, description="Stock decline %")
    outcome: Optional[str] = Field(None, description="Fraud outcome")
    lessons: Optional[List[str]] = Field(None, description="Lessons learned")


class PatternMatchResponse(BaseModel):
    """Pattern matching analysis response."""
    analysis_id: UUID = Field(..., description="Analysis ID")
    company_id: UUID = Field(..., description="Company ID")
    company_name: str = Field(..., description="Company name")
    risk_level: str = Field(..., description="Pattern match risk level")
    message: str = Field(..., description="Risk assessment message")
    total_matches: int = Field(..., description="Total fraud cases matched")
    triggered_flags_count: int = Field(..., description="Number of triggered flags")
    matches: List[PatternMatchResult] = Field(..., description="Top matching fraud cases")


class FraudCaseListResponse(BaseModel):
    """List of fraud cases."""
    total: int = Field(..., description="Total number of fraud cases")
    cases: List[FraudCaseResponse] = Field(..., description="Fraud cases")

    class Config:
        from_attributes = True
