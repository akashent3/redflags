"""Schema definitions for Celery task status."""

from typing import Optional

from pydantic import BaseModel, Field


class TaskSubmitResponse(BaseModel):
    """Response when a task is submitted."""

    task_id: str = Field(..., description="Celery task ID for tracking")
    report_id: str = Field(..., description="Report ID being analyzed")
    status: str = Field(..., description="Initial task status (PENDING)")
    message: str = Field(..., description="Human-readable message")


class TaskStatusResponse(BaseModel):
    """Response for task status check."""

    task_id: str = Field(..., description="Celery task ID")
    status: str = Field(..., description="Task status (PENDING/STARTED/PROGRESS/SUCCESS/FAILURE)")
    current: Optional[int] = Field(None, description="Current progress (0-100)")
    total: Optional[int] = Field(100, description="Total progress (always 100)")
    percent: Optional[int] = Field(None, description="Percentage complete")
    message: Optional[str] = Field(None, description="Status message")

    # Success fields
    analysis_id: Optional[str] = Field(None, description="Analysis ID (when complete)")
    risk_score: Optional[int] = Field(None, description="Risk score (when complete)")
    risk_level: Optional[str] = Field(None, description="Risk level (when complete)")
    flags_triggered: Optional[int] = Field(None, description="Flags triggered (when complete)")
    processing_time: Optional[int] = Field(None, description="Processing time in seconds")

    # Error fields
    error: Optional[str] = Field(None, description="Error message (when failed)")
