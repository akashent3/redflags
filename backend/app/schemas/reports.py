"""Schema definitions for annual report endpoints."""

from datetime import datetime
from typing import Optional
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field


class ReportUploadRequest(BaseModel):
    """Request schema for uploading an annual report."""

    company_name: str = Field(..., min_length=1, max_length=255, description="Company name")
    fiscal_year: int = Field(..., ge=2000, le=2100, description="Fiscal year (e.g., 2023 for FY2023-24)")


class ReportResponse(BaseModel):
    """Response schema for annual report details."""

    id: UUID
    company_id: UUID
    fiscal_year: str
    fiscal_year_display: str
    pdf_url: str
    file_size_mb: float
    pages_count: Optional[int] = None
    is_processed: str
    uploaded_at: datetime
    processed_at: Optional[datetime] = None

    model_config = ConfigDict(from_attributes=True)


class ReportListResponse(BaseModel):
    """Response schema for paginated list of reports."""

    total: int = Field(..., description="Total number of reports")
    skip: int = Field(..., description="Number of reports skipped")
    limit: int = Field(..., description="Maximum number of reports returned")
    reports: list[ReportResponse] = Field(..., description="List of report objects")
