"""Company Analysis Schemas."""

from typing import Literal, Optional

from pydantic import BaseModel


class AnalyzeCompanyResponse(BaseModel):
    """Response for company analysis request."""
    
    status: Literal["existing_analysis", "analysis_triggered", "reports_missing"]
    message: str
    analysis_id: Optional[str] = None
    task_id: Optional[str] = None
    reports_count: Optional[int] = None
    
    class Config:
        from_attributes = True
