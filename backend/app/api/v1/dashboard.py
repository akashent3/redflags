"""Dashboard API endpoints."""

import logging
from datetime import datetime, timedelta
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import func, and_
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.analysis_result import AnalysisResult
from app.models.annual_report import AnnualReport
from app.models.company import Company
from app.models.red_flag import RedFlag
from app.models.user import User
from app.utils import get_current_active_user

logger = logging.getLogger(__name__)
router = APIRouter()


@router.get(
    "/stats",
    summary="Get dashboard statistics",
    description="Get overall dashboard statistics for the current user",
)
async def get_dashboard_stats(
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    """
    Get dashboard statistics.

    Returns:
    - Total completed reports analyzed
    - Average risk score
    - Total red flags triggered
    - Last analysis date
    - Recent analyses (last 5)
    """
    try:
        # Get all completed analyses (only count completed reports)
        completed_analyses = (
            db.query(AnalysisResult)
            .join(AnnualReport, AnalysisResult.report_id == AnnualReport.id)
            .filter(AnnualReport.is_processed == "completed")
            .all()
        )

        total_reports = len(completed_analyses)

        # Calculate average risk score
        if total_reports > 0:
            avg_risk_score = sum(a.risk_score for a in completed_analyses) / total_reports
            avg_risk_score = round(avg_risk_score, 1)
        else:
            avg_risk_score = 0

        # Get total red flags triggered across all analyses
        total_red_flags = (
            db.query(func.count(RedFlag.id))
            .join(AnalysisResult, RedFlag.analysis_id == AnalysisResult.id)
            .join(AnnualReport, AnalysisResult.report_id == AnnualReport.id)
            .filter(
                and_(
                    RedFlag.is_triggered == True,
                    AnnualReport.is_processed == "completed"
                )
            )
            .scalar()
        ) or 0

        # Get last analysis date
        last_analysis = (
            db.query(AnalysisResult)
            .join(AnnualReport, AnalysisResult.report_id == AnnualReport.id)
            .filter(AnnualReport.is_processed == "completed")
            .order_by(AnalysisResult.analyzed_at.desc())
            .first()
        )

        last_analysis_date = last_analysis.analyzed_at if last_analysis else None

        # Get recent analyses (last 5)
        recent_analyses = (
            db.query(
                AnalysisResult.id,
                AnalysisResult.report_id,
                AnalysisResult.risk_score,
                AnalysisResult.risk_level,
                AnalysisResult.flags_triggered_count,
                AnalysisResult.analyzed_at,
                AnnualReport.fiscal_year,
                Company.name.label("company_name"),
                Company.nse_symbol,
            )
            .join(AnnualReport, AnalysisResult.report_id == AnnualReport.id)
            .join(Company, AnnualReport.company_id == Company.id)
            .filter(AnnualReport.is_processed == "completed")
            .order_by(AnalysisResult.analyzed_at.desc())
            .limit(5)
            .all()
        )

        recent_list = [
            {
                "analysis_id": str(a.id),
                "report_id": str(a.report_id),
                "company_name": a.company_name,
                "symbol": a.nse_symbol,
                "fiscal_year": a.fiscal_year,
                "risk_score": a.risk_score,
                "risk_level": a.risk_level,
                "flags_triggered": a.flags_triggered_count,
                "analyzed_at": a.analyzed_at.isoformat() if a.analyzed_at else None,
            }
            for a in recent_analyses
        ]

        return {
            "total_reports": total_reports,
            "avg_risk_score": avg_risk_score,
            "total_red_flags": total_red_flags,
            "last_analysis_date": last_analysis_date.isoformat() if last_analysis_date else None,
            "recent_analyses": recent_list,
        }

    except Exception as e:
        logger.error(f"Failed to get dashboard stats: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to retrieve dashboard statistics: {str(e)}",
        )


@router.get(
    "/risk-distribution",
    summary="Get risk level distribution",
    description="Get count of analyses by risk level",
)
async def get_risk_distribution(
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    """Get distribution of analyses by risk level (only completed)."""
    try:
        risk_counts = (
            db.query(
                AnalysisResult.risk_level,
                func.count(AnalysisResult.id).label("count")
            )
            .join(AnnualReport, AnalysisResult.report_id == AnnualReport.id)
            .filter(AnnualReport.is_processed == "completed")
            .group_by(AnalysisResult.risk_level)
            .all()
        )

        distribution = {
            "CLEAN": 0,
            "LOW": 0,
            "MEDIUM": 0,
            "HIGH": 0,
            "CRITICAL": 0,
        }

        for risk_level, count in risk_counts:
            distribution[risk_level] = count

        return distribution

    except Exception as e:
        logger.error(f"Failed to get risk distribution: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to retrieve risk distribution: {str(e)}",
        )