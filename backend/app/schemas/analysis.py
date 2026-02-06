"""Schema definitions for analysis endpoints."""

from datetime import datetime
from typing import Optional
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field


class AnalysisResponse(BaseModel):
    """Response schema for analysis result details."""

    id: UUID
    report_id: UUID
    risk_score: int = Field(..., ge=0, le=100, description="Overall risk score (0-100)")
    risk_level: str = Field(..., description="Risk level (LOW/MODERATE/ELEVATED/HIGH/CRITICAL)")
    risk_level_color: str = Field(..., description="Hex color code for risk level")
    category_scores: dict = Field(..., description="Risk scores by category")
    flags_triggered_count: int = Field(..., description="Total number of flags triggered")
    flags_critical_count: int = Field(..., description="Number of CRITICAL flags triggered")
    flags_high_count: int = Field(..., description="Number of HIGH flags triggered")
    flags_medium_count: int = Field(..., description="Number of MEDIUM flags triggered")
    flags_low_count: int = Field(..., description="Number of LOW flags triggered")
    summary_text: Optional[str] = Field(None, description="AI-generated executive summary")
    key_concerns: list[str] = Field(..., description="Top 3-5 key concerns identified")
    analyzed_at: datetime = Field(..., description="Timestamp when analysis was completed")

    model_config = ConfigDict(from_attributes=True)


class RedFlagResponse(BaseModel):
    """Response schema for individual red flag details."""

    id: UUID
    flag_number: int = Field(..., ge=1, le=54, description="Flag number (1-54)")
    flag_name: str = Field(..., description="Short name of the red flag")
    category: str = Field(..., description="Category (Auditor, Cash Flow, etc.)")
    severity: str = Field(..., description="Severity level (CRITICAL/HIGH/MEDIUM/LOW)")
    is_triggered: bool = Field(..., description="Whether this flag was triggered")
    confidence_score: int = Field(..., ge=0, le=100, description="Confidence score (0-100)")
    evidence_text: Optional[str] = Field(None, description="Evidence supporting the flag")
    page_references: Optional[list[int]] = Field(None, description="Page numbers where evidence was found")
    detection_method: Optional[str] = Field(None, description="Detection method (rule_based/llm/hybrid)")

    model_config = ConfigDict(from_attributes=True)


class FlagListResponse(BaseModel):
    """Response schema for paginated list of red flags."""

    total: int = Field(..., description="Total number of flags")
    flags: list[RedFlagResponse] = Field(..., description="List of red flag objects")
