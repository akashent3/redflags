"""Admin API endpoints for user management, system monitoring, and administration."""

import logging
from typing import List, Optional
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import func
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.user import User, SubscriptionTier
from app.models.company import Company
from app.models.analysis_result import AnalysisResult
from app.models.annual_report import AnnualReport
from app.models.fraud_case import FraudCase
from app.models.watchlist import WatchlistItem
from app.models.portfolio import Portfolio
from app.utils.admin import require_admin
from app.schemas.user import UserResponse

logger = logging.getLogger(__name__)
router = APIRouter()


# ============================================================================
# SYSTEM STATS
# ============================================================================

@router.get(
    "/stats",
    summary="Get system statistics",
    description="Get overall system statistics (admin only).",
)
async def get_system_stats(
    db: Session = Depends(get_db),
    admin: User = Depends(require_admin),
):
    """Get system-wide statistics."""
    try:
        stats = {
            "users": {
                "total": db.query(User).count(),
                "active": db.query(User).filter(User.is_active == True).count(),
                "verified": db.query(User).filter(User.is_verified == True).count(),
                "free": db.query(User).filter(User.subscription_tier == SubscriptionTier.FREE).count(),
                "pro": db.query(User).filter(User.subscription_tier == SubscriptionTier.PRO).count(),
                "premium": db.query(User).filter(User.subscription_tier == SubscriptionTier.PREMIUM).count(),
            },
            "analyses": {
                "total": db.query(AnalysisResult).count(),
                "clean": db.query(AnalysisResult).filter(AnalysisResult.risk_level == "CLEAN").count(),
                "low": db.query(AnalysisResult).filter(AnalysisResult.risk_level == "LOW").count(),
                "medium": db.query(AnalysisResult).filter(AnalysisResult.risk_level == "MEDIUM").count(),
                "high": db.query(AnalysisResult).filter(AnalysisResult.risk_level == "HIGH").count(),
                "critical": db.query(AnalysisResult).filter(AnalysisResult.risk_level == "CRITICAL").count(),
            },
            "companies": {
                "total": db.query(Company).count(),
                "nifty_50": db.query(Company).filter(Company.is_nifty_50 == True).count(),
                "nifty_500": db.query(Company).filter(Company.is_nifty_500 == True).count(),
            },
            "fraud_cases": {
                "total": db.query(FraudCase).count(),
            },
            "watchlist_items": {
                "total": db.query(WatchlistItem).count(),
            },
            "portfolios": {
                "total": db.query(Portfolio).count(),
            }
        }

        return stats

    except Exception as e:
        logger.error(f"Error fetching system stats: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to fetch system statistics: {str(e)}"
        )


# ============================================================================
# USER MANAGEMENT
# ============================================================================

@router.get(
    "/users",
    response_model=List[UserResponse],
    summary="List all users",
    description="Get list of all users (admin only).",
)
async def list_users(
    skip: int = Query(0, ge=0, description="Number of records to skip"),
    limit: int = Query(50, ge=1, le=500, description="Maximum number of results"),
    subscription_tier: Optional[str] = Query(None, description="Filter by subscription tier"),
    is_active: Optional[bool] = Query(None, description="Filter by active status"),
    db: Session = Depends(get_db),
    admin: User = Depends(require_admin),
):
    """List all users with filters."""
    try:
        query = db.query(User)

        # Apply filters
        if subscription_tier:
            query = query.filter(User.subscription_tier == subscription_tier)
        if is_active is not None:
            query = query.filter(User.is_active == is_active)

        # Get users
        users = query.order_by(User.created_at.desc()).offset(skip).limit(limit).all()

        return [
            UserResponse(
                id=user.id,
                email=user.email,
                full_name=user.full_name,
                subscription_tier=user.subscription_tier,
                subscription_active=user.subscription_active,
                reports_used_this_month=user.reports_used_this_month,
                reports_limit=user.reports_limit,
                is_active=user.is_active,
                is_verified=user.is_verified,
                created_at=user.created_at,
                updated_at=user.updated_at,
                last_login=user.last_login,
            )
            for user in users
        ]

    except Exception as e:
        logger.error(f"Error listing users: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to list users"
        )


@router.patch(
    "/users/{user_id}/subscription",
    summary="Update user subscription",
    description="Update a user's subscription tier (admin only).",
)
async def update_user_subscription(
    user_id: UUID,
    subscription_tier: SubscriptionTier,
    db: Session = Depends(get_db),
    admin: User = Depends(require_admin),
):
    """Update user's subscription tier."""
    try:
        user = db.query(User).filter(User.id == user_id).first()
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"User not found: {user_id}"
            )

        old_tier = user.subscription_tier
        user.subscription_tier = subscription_tier
        db.commit()

        logger.info(
            f"Admin {admin.email} changed user {user.email} subscription from "
            f"{old_tier} to {subscription_tier}"
        )

        return {
            "message": "Subscription updated successfully",
            "user_id": str(user_id),
            "old_tier": old_tier,
            "new_tier": subscription_tier
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error updating subscription: {e}", exc_info=True)
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to update subscription"
        )


@router.delete(
    "/users/{user_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete user",
    description="Delete a user account (admin only).",
)
async def delete_user(
    user_id: UUID,
    db: Session = Depends(get_db),
    admin: User = Depends(require_admin),
):
    """Delete user account."""
    try:
        user = db.query(User).filter(User.id == user_id).first()
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"User not found: {user_id}"
            )

        # Prevent self-deletion
        if user.id == admin.id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Cannot delete your own admin account"
            )

        user_email = user.email
        db.delete(user)
        db.commit()

        logger.info(f"Admin {admin.email} deleted user {user_email}")

        return None

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting user: {e}", exc_info=True)
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to delete user"
        )


# ============================================================================
# ANALYSIS MANAGEMENT
# ============================================================================

@router.get(
    "/analyses",
    summary="List all analyses",
    description="Get list of all analysis results (admin only).",
)
async def list_analyses(
    skip: int = Query(0, ge=0, description="Number of records to skip"),
    limit: int = Query(50, ge=1, le=500, description="Maximum number of results"),
    risk_level: Optional[str] = Query(None, description="Filter by risk level"),
    db: Session = Depends(get_db),
    admin: User = Depends(require_admin),
):
    """List all analyses with filters."""
    try:
        # Join AnalysisResult → AnnualReport to get company_id and fiscal_year
        query = db.query(AnalysisResult, AnnualReport).join(
            AnnualReport, AnalysisResult.report_id == AnnualReport.id
        )

        # Apply filters
        if risk_level:
            query = query.filter(AnalysisResult.risk_level == risk_level.upper())

        # Get analyses
        results = query.order_by(AnalysisResult.created_at.desc()).offset(skip).limit(limit).all()

        return [
            {
                "id": str(analysis.id),
                "company_id": str(report.company_id),
                "fiscal_year": report.fiscal_year,
                "risk_score": analysis.risk_score,
                "risk_level": analysis.risk_level,
                "flags_triggered": analysis.flags_triggered_count,
                "created_at": analysis.created_at,
            }
            for analysis, report in results
        ]

    except Exception as e:
        logger.error(f"Error listing analyses: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to list analyses"
        )


@router.delete(
    "/analyses/{analysis_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete analysis",
    description="Delete an analysis result (admin only).",
)
async def delete_analysis(
    analysis_id: UUID,
    db: Session = Depends(get_db),
    admin: User = Depends(require_admin),
):
    """Delete analysis result."""
    try:
        analysis = db.query(AnalysisResult).filter(AnalysisResult.id == analysis_id).first()
        if not analysis:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Analysis not found: {analysis_id}"
            )

        db.delete(analysis)
        db.commit()

        logger.info(f"Admin {admin.email} deleted analysis {analysis_id}")

        return None

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting analysis: {e}", exc_info=True)
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to delete analysis"
        )


# ============================================================================
# FRAUD CASE MANAGEMENT
# ============================================================================

@router.delete(
    "/fraud-cases/{case_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete fraud case",
    description="Delete a fraud case (admin only).",
)
async def delete_fraud_case(
    case_id: str,
    db: Session = Depends(get_db),
    admin: User = Depends(require_admin),
):
    """Delete fraud case."""
    try:
        fraud_case = db.query(FraudCase).filter(FraudCase.case_id == case_id).first()
        if not fraud_case:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Fraud case not found: {case_id}"
            )

        db.delete(fraud_case)
        db.commit()

        logger.info(f"Admin {admin.email} deleted fraud case {case_id}")

        return None

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting fraud case: {e}", exc_info=True)
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to delete fraud case"
        )
