"""Analysis API endpoints."""

import logging
from typing import Optional

from celery.result import AsyncResult
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.celery_app import celery_app
from app.database import get_db
from app.models.analysis_result import AnalysisResult
from app.models.annual_report import AnnualReport
from app.models.red_flag import FlagCategory, FlagSeverity, RedFlag
from app.models.user import User
from app.schemas import (
    AnalysisResponse,
    FlagListResponse,
    RedFlagResponse,
    TaskStatusResponse,
    TaskSubmitResponse,
)
from app.tasks.analysis_tasks import analyze_report_task
from app.utils import get_current_active_user

logger = logging.getLogger(__name__)
router = APIRouter()


@router.post(
    "/analyze/{report_id}",
    response_model=TaskSubmitResponse,
    status_code=status.HTTP_202_ACCEPTED,
    summary="Trigger analysis on a report (async)",
    description="Submit report for background analysis using Celery. Returns task ID immediately.",
)
async def analyze_report(
    report_id: str,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    """
    Trigger asynchronous analysis on an annual report.

    This endpoint will:
    1. Submit analysis job to Celery queue
    2. Return task ID immediately (responds in <1 second)
    3. Analysis runs in background (~30-60 seconds)

    Use GET /analysis/task/{task_id} to check status.
    """
    try:
        # Verify report exists
        report = db.query(AnnualReport).filter(AnnualReport.id == report_id).first()

        if not report:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Report not found: {report_id}",
            )

        # Check if analysis already exists
        existing_analysis = (
            db.query(AnalysisResult)
            .filter(AnalysisResult.report_id == report_id)
            .first()
        )

        if existing_analysis:
            logger.info(f"Analysis already exists for report {report_id}")
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=f"Analysis already exists for this report. Analysis ID: {existing_analysis.id}",
            )

        # Check if already being processed
        if report.is_processed == "processing":
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Report is already being processed",
            )

        logger.info(f"Submitting analysis task for report {report_id}")

        # Submit to Celery
        task = analyze_report_task.delay(report_id)

        logger.info(f"Analysis task submitted: {task.id}")

        return TaskSubmitResponse(
            task_id=task.id,
            report_id=report_id,
            status="PENDING",
            message="Analysis task submitted. Check status at /api/v1/analysis/task/{task_id}",
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to submit analysis task: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to submit analysis task: {str(e)}",
        )


@router.get(
    "/task/{task_id}",
    response_model=TaskStatusResponse,
    summary="Check analysis task status",
    description="Get the current status of a background analysis task",
)
async def get_task_status(
    task_id: str,
    current_user: User = Depends(get_current_active_user),
):
    """
    Check the status of an analysis task.

    Possible statuses:
    - PENDING: Task is waiting in queue
    - STARTED: Task has started
    - PROGRESS: Task is running (with progress updates)
    - SUCCESS: Task completed successfully
    - FAILURE: Task failed

    When SUCCESS, response includes analysis_id and risk score.
    """
    try:
        # Get task result from Celery
        task_result = AsyncResult(task_id, app=celery_app)

        response = {"task_id": task_id, "status": task_result.state}

        if task_result.state == "PENDING":
            response["message"] = "Task is waiting in queue"

        elif task_result.state == "STARTED":
            response["message"] = "Task has started processing"
            response["percent"] = 10

        elif task_result.state == "PROGRESS":
            info = task_result.info
            response["message"] = info.get("status", "Processing")
            response["current"] = info.get("progress", 0)
            response["total"] = 100
            response["percent"] = info.get("progress", 0)

        elif task_result.state == "SUCCESS":
            result = task_result.result
            response["message"] = result.get("message", "Analysis completed")
            response["analysis_id"] = result.get("analysis_id")
            response["risk_score"] = result.get("risk_score")
            response["risk_level"] = result.get("risk_level")
            response["flags_triggered"] = result.get("flags_triggered")
            response["processing_time"] = result.get("processing_time")
            response["percent"] = 100

        elif task_result.state == "FAILURE":
            result = task_result.result
            response["message"] = "Analysis failed"
            response["error"] = str(result) if isinstance(result, Exception) else result.get("error", "Unknown error")

        return TaskStatusResponse(**response)

    except Exception as e:
        logger.error(f"Failed to get task status: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to retrieve task status: {str(e)}",
        )


@router.get(
    "/{analysis_id}",
    response_model=AnalysisResponse,
    summary="Get analysis result",
    description="Get detailed analysis result by ID",
)
async def get_analysis(
    analysis_id: str,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    """
    Get analysis result by ID.

    Returns complete analysis including:
    - Risk score and level
    - Category scores
    - Flag counts by severity
    - Summary and key concerns
    """
    try:
        analysis = (
            db.query(AnalysisResult)
            .filter(AnalysisResult.id == analysis_id)
            .first()
        )

        if not analysis:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Analysis not found: {analysis_id}",
            )

        return analysis

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get analysis: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to retrieve analysis: {str(e)}",
        )


@router.get(
    "/report/{report_id}",
    response_model=AnalysisResponse,
    summary="Get analysis by report ID",
    description="Get analysis result for a specific report",
)
async def get_analysis_by_report(
    report_id: str,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    """
    Get analysis result for a specific report.

    Useful for checking if a report has been analyzed.
    """
    try:
        # Verify report exists
        report = db.query(AnnualReport).filter(AnnualReport.id == report_id).first()

        if not report:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Report not found: {report_id}",
            )

        # Get analysis
        analysis = (
            db.query(AnalysisResult)
            .filter(AnalysisResult.report_id == report_id)
            .first()
        )

        if not analysis:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"No analysis found for report: {report_id}. Please trigger analysis first.",
            )

        return analysis

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get analysis by report: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to retrieve analysis: {str(e)}",
        )


@router.get(
    "/{analysis_id}/flags",
    response_model=FlagListResponse,
    summary="Get red flags",
    description="Get all red flags for an analysis with optional filtering",
)
async def get_red_flags(
    analysis_id: str,
    triggered_only: bool = Query(False, description="Show only triggered flags"),
    category: Optional[str] = Query(None, description="Filter by category (Auditor, Cash Flow, etc.)"),
    severity: Optional[str] = Query(None, description="Filter by severity (CRITICAL, HIGH, MEDIUM, LOW)"),
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    """
    Get red flags for an analysis.

    Optional filters:
    - **triggered_only**: Show only flags that were triggered
    - **category**: Filter by category (Auditor, Cash Flow, Related Party, etc.)
    - **severity**: Filter by severity level (CRITICAL, HIGH, MEDIUM, LOW)

    Returns all 54 flags by default.
    """
    try:
        # Verify analysis exists
        analysis = (
            db.query(AnalysisResult)
            .filter(AnalysisResult.id == analysis_id)
            .first()
        )

        if not analysis:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Analysis not found: {analysis_id}",
            )

        # Build query
        query = db.query(RedFlag).filter(RedFlag.analysis_id == analysis_id)

        # Apply filters
        if triggered_only:
            query = query.filter(RedFlag.is_triggered == True)

        if category:
            try:
                category_enum = FlagCategory(category)
                query = query.filter(RedFlag.category == category_enum)
            except ValueError:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Invalid category: {category}. Valid categories: {[c.value for c in FlagCategory]}",
                )

        if severity:
            try:
                severity_enum = FlagSeverity(severity)
                query = query.filter(RedFlag.severity == severity_enum)
            except ValueError:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Invalid severity: {severity}. Valid severities: {[s.value for s in FlagSeverity]}",
                )

        # Get flags ordered by flag number
        flags = query.order_by(RedFlag.flag_number).all()

        return FlagListResponse(
            total=len(flags),
            flags=flags,
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get red flags: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to retrieve red flags: {str(e)}",
        )
