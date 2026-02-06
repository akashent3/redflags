"""Pydantic schemas for request/response validation."""

from app.schemas.analysis import AnalysisResponse, FlagListResponse, RedFlagResponse
from app.schemas.auth import (
    LoginRequest,
    MessageResponse,
    SignupRequest,
    TokenResponse,
)
from app.schemas.company import (
    CompanyDetailResponse,
    CompanyResponse,
    CompanySearchResponse,
    CompanySearchResult,
)
from app.schemas.reports import ReportListResponse, ReportResponse, ReportUploadRequest
from app.schemas.tasks import TaskStatusResponse, TaskSubmitResponse
from app.schemas.user import UserResponse

__all__ = [
    # Auth schemas
    "SignupRequest",
    "LoginRequest",
    "TokenResponse",
    "MessageResponse",
    # User schemas
    "UserResponse",
    # Company schemas
    "CompanyResponse",
    "CompanySearchResponse",
    "CompanySearchResult",
    "CompanyDetailResponse",
    # Report schemas
    "ReportUploadRequest",
    "ReportResponse",
    "ReportListResponse",
    # Analysis schemas
    "AnalysisResponse",
    "RedFlagResponse",
    "FlagListResponse",
    # Task schemas
    "TaskSubmitResponse",
    "TaskStatusResponse",
]
