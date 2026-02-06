"""Watchlist API endpoints."""

import logging
from typing import List, Optional
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.user import User
from app.models.watchlist import WatchlistItem, WatchlistAlert, NotificationPreference
from app.models.company import Company
from app.models.analysis_result import AnalysisResult
from app.utils.dependencies import get_current_active_user
from app.schemas.watchlist import (
    WatchlistItemCreate,
    WatchlistItemResponse,
    WatchlistAlertResponse,
    WatchlistResponse,
    WatchlistAlertMarkRead,
    NotificationPreferencesUpdate,
    NotificationPreferencesResponse,
)

logger = logging.getLogger(__name__)

router = APIRouter()


@router.get(
    "/",
    response_model=WatchlistResponse,
    summary="Get user's watchlist",
    description="Get all companies in user's watchlist with risk scores and recent alerts.",
)
async def get_watchlist(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """Get user's complete watchlist with alerts."""
    try:
        # Get watchlist items
        watchlist_items = db.query(WatchlistItem).filter(
            WatchlistItem.user_id == current_user.id
        ).all()

        # Build response items
        response_items = []
        for item in watchlist_items:
            company = item.company

            # Get latest analysis for risk score
            latest_analysis = db.query(AnalysisResult).filter(
                AnalysisResult.company_id == company.id
            ).order_by(AnalysisResult.created_at.desc()).first()

            current_risk_score = latest_analysis.overall_risk_score if latest_analysis else None
            current_risk_level = latest_analysis.risk_level if latest_analysis else None
            last_analysis_date = latest_analysis.created_at if latest_analysis else None

            # Calculate score change
            score_change = None
            if item.last_known_risk_score and current_risk_score:
                score_change = current_risk_score - item.last_known_risk_score

            response_items.append(WatchlistItemResponse(
                watchlist_id=item.id,
                company_id=company.id,
                symbol=company.display_code,
                company_name=company.name,
                industry=company.industry,
                sector=company.sector,
                current_risk_score=current_risk_score,
                current_risk_level=current_risk_level,
                previous_risk_score=item.last_known_risk_score,
                score_change=score_change,
                last_analysis_date=last_analysis_date,
                added_date=item.added_at,
                alert_enabled=item.alert_enabled,
            ))

        # Get recent alerts (last 30 days, unread first)
        alerts = db.query(WatchlistAlert).join(
            WatchlistItem
        ).filter(
            WatchlistItem.user_id == current_user.id
        ).order_by(
            WatchlistAlert.is_read.asc(),
            WatchlistAlert.created_at.desc()
        ).limit(50).all()

        alert_responses = []
        for alert in alerts:
            item = alert.watchlist_item
            company = item.company

            alert_responses.append(WatchlistAlertResponse(
                alert_id=alert.id,
                company_id=company.id,
                symbol=company.display_code,
                company_name=company.name,
                alert_type=alert.alert_type,
                severity=alert.severity,
                message=alert.message,
                created_at=alert.created_at,
                is_read=alert.is_read,
                previous_risk_score=alert.previous_risk_score,
                current_risk_score=alert.current_risk_score,
                score_change=alert.score_change,
            ))

        return WatchlistResponse(
            user_id=current_user.id,
            items=response_items,
            total_watched=len(response_items),
            recent_alerts=alert_responses,
        )

    except Exception as e:
        logger.error(f"Error getting watchlist: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get watchlist: {str(e)}"
        )


@router.post(
    "/",
    response_model=WatchlistItemResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Add company to watchlist",
    description="Add a company to user's watchlist.",
)
async def add_to_watchlist(
    data: WatchlistItemCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """Add company to watchlist."""
    try:
        # Check if company exists
        company = db.query(Company).filter(Company.id == data.company_id).first()
        if not company:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Company not found: {data.company_id}"
            )

        # Check if already in watchlist
        existing = db.query(WatchlistItem).filter(
            WatchlistItem.user_id == current_user.id,
            WatchlistItem.company_id == data.company_id
        ).first()

        if existing:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Company already in watchlist"
            )

        # Get latest risk score
        latest_analysis = db.query(AnalysisResult).filter(
            AnalysisResult.company_id == company.id
        ).order_by(AnalysisResult.created_at.desc()).first()

        # Create watchlist item
        watchlist_item = WatchlistItem(
            user_id=current_user.id,
            company_id=data.company_id,
            alert_enabled=data.alert_enabled,
            last_known_risk_score=latest_analysis.overall_risk_score if latest_analysis else None,
        )

        db.add(watchlist_item)
        db.commit()
        db.refresh(watchlist_item)

        # Build response
        return WatchlistItemResponse(
            watchlist_id=watchlist_item.id,
            company_id=company.id,
            symbol=company.display_code,
            company_name=company.name,
            industry=company.industry,
            sector=company.sector,
            current_risk_score=latest_analysis.overall_risk_score if latest_analysis else None,
            current_risk_level=latest_analysis.risk_level if latest_analysis else None,
            previous_risk_score=None,
            score_change=None,
            last_analysis_date=latest_analysis.created_at if latest_analysis else None,
            added_date=watchlist_item.added_at,
            alert_enabled=watchlist_item.alert_enabled,
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error adding to watchlist: {e}", exc_info=True)
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to add to watchlist: {str(e)}"
        )


@router.delete(
    "/{watchlist_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Remove from watchlist",
    description="Remove a company from user's watchlist.",
)
async def remove_from_watchlist(
    watchlist_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """Remove company from watchlist."""
    try:
        # Find watchlist item
        item = db.query(WatchlistItem).filter(
            WatchlistItem.id == watchlist_id,
            WatchlistItem.user_id == current_user.id
        ).first()

        if not item:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Watchlist item not found"
            )

        db.delete(item)
        db.commit()

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error removing from watchlist: {e}", exc_info=True)
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to remove from watchlist: {str(e)}"
        )


@router.get(
    "/alerts",
    response_model=List[WatchlistAlertResponse],
    summary="Get watchlist alerts",
    description="Get user's watchlist alerts with optional filtering.",
)
async def get_alerts(
    unread_only: bool = Query(False, description="Show only unread alerts"),
    limit: int = Query(50, ge=1, le=200, description="Maximum number of alerts"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """Get user's watchlist alerts."""
    try:
        query = db.query(WatchlistAlert).join(
            WatchlistItem
        ).filter(
            WatchlistItem.user_id == current_user.id
        )

        if unread_only:
            query = query.filter(WatchlistAlert.is_read == False)

        alerts = query.order_by(
            WatchlistAlert.created_at.desc()
        ).limit(limit).all()

        responses = []
        for alert in alerts:
            item = alert.watchlist_item
            company = item.company

            responses.append(WatchlistAlertResponse(
                alert_id=alert.id,
                company_id=company.id,
                symbol=company.display_code,
                company_name=company.name,
                alert_type=alert.alert_type,
                severity=alert.severity,
                message=alert.message,
                created_at=alert.created_at,
                is_read=alert.is_read,
                previous_risk_score=alert.previous_risk_score,
                current_risk_score=alert.current_risk_score,
                score_change=alert.score_change,
            ))

        return responses

    except Exception as e:
        logger.error(f"Error getting alerts: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get alerts: {str(e)}"
        )


@router.patch(
    "/alerts/{alert_id}",
    response_model=WatchlistAlertResponse,
    summary="Mark alert as read/unread",
    description="Update alert read status.",
)
async def update_alert_status(
    alert_id: UUID,
    data: WatchlistAlertMarkRead,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """Mark alert as read or unread."""
    try:
        # Find alert
        alert = db.query(WatchlistAlert).join(
            WatchlistItem
        ).filter(
            WatchlistAlert.id == alert_id,
            WatchlistItem.user_id == current_user.id
        ).first()

        if not alert:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Alert not found"
            )

        # Update status
        alert.is_read = data.is_read
        if data.is_read:
            from datetime import datetime
            alert.read_at = datetime.utcnow()

        db.commit()
        db.refresh(alert)

        # Build response
        item = alert.watchlist_item
        company = item.company

        return WatchlistAlertResponse(
            alert_id=alert.id,
            company_id=company.id,
            symbol=company.display_code,
            company_name=company.name,
            alert_type=alert.alert_type,
            severity=alert.severity,
            message=alert.message,
            created_at=alert.created_at,
            is_read=alert.is_read,
            previous_risk_score=alert.previous_risk_score,
            current_risk_score=alert.current_risk_score,
            score_change=alert.score_change,
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error updating alert: {e}", exc_info=True)
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to update alert: {str(e)}"
        )


@router.get(
    "/preferences",
    response_model=NotificationPreferencesResponse,
    summary="Get notification preferences",
    description="Get user's notification preferences.",
)
async def get_notification_preferences(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """Get user's notification preferences."""
    try:
        prefs = db.query(NotificationPreference).filter(
            NotificationPreference.user_id == current_user.id
        ).first()

        # Create default if not exists
        if not prefs:
            prefs = NotificationPreference(user_id=current_user.id)
            db.add(prefs)
            db.commit()
            db.refresh(prefs)

        return NotificationPreferencesResponse(
            user_id=prefs.user_id,
            email_alerts_enabled=prefs.email_alerts_enabled,
            weekly_digest_enabled=prefs.weekly_digest_enabled,
            feature_announcements_enabled=prefs.feature_announcements_enabled,
            push_notifications_enabled=prefs.push_notifications_enabled,
            alert_frequency=prefs.alert_frequency,
            created_at=prefs.created_at,
            updated_at=prefs.updated_at,
        )

    except Exception as e:
        logger.error(f"Error getting preferences: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get preferences: {str(e)}"
        )


@router.patch(
    "/preferences",
    response_model=NotificationPreferencesResponse,
    summary="Update notification preferences",
    description="Update user's notification preferences.",
)
async def update_notification_preferences(
    data: NotificationPreferencesUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """Update user's notification preferences."""
    try:
        prefs = db.query(NotificationPreference).filter(
            NotificationPreference.user_id == current_user.id
        ).first()

        # Create if not exists
        if not prefs:
            prefs = NotificationPreference(user_id=current_user.id)
            db.add(prefs)

        # Update fields
        if data.email_alerts_enabled is not None:
            prefs.email_alerts_enabled = data.email_alerts_enabled
        if data.weekly_digest_enabled is not None:
            prefs.weekly_digest_enabled = data.weekly_digest_enabled
        if data.feature_announcements_enabled is not None:
            prefs.feature_announcements_enabled = data.feature_announcements_enabled
        if data.push_notifications_enabled is not None:
            # Check if user has Premium subscription for push notifications
            if data.push_notifications_enabled and current_user.subscription_tier != "premium":
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="Push notifications require Premium subscription"
                )
            prefs.push_notifications_enabled = data.push_notifications_enabled
        if data.alert_frequency is not None:
            prefs.alert_frequency = data.alert_frequency

        db.commit()
        db.refresh(prefs)

        return NotificationPreferencesResponse(
            user_id=prefs.user_id,
            email_alerts_enabled=prefs.email_alerts_enabled,
            weekly_digest_enabled=prefs.weekly_digest_enabled,
            feature_announcements_enabled=prefs.feature_announcements_enabled,
            push_notifications_enabled=prefs.push_notifications_enabled,
            alert_frequency=prefs.alert_frequency,
            created_at=prefs.created_at,
            updated_at=prefs.updated_at,
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error updating preferences: {e}", exc_info=True)
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to update preferences: {str(e)}"
        )


@router.post(
    "/push-subscription",
    summary="Save push subscription",
    description="Save push notification subscription (Premium only).",
)
async def save_push_subscription(
    subscription: dict,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """Save push notification subscription."""
    try:
        import json

        # Check Premium subscription
        if current_user.subscription_tier != 'premium':
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Push notifications require Premium subscription"
            )

        prefs = db.query(NotificationPreference).filter(
            NotificationPreference.user_id == current_user.id
        ).first()

        if not prefs:
            prefs = NotificationPreference(user_id=current_user.id)
            db.add(prefs)

        prefs.push_subscription_endpoint = subscription.get('endpoint')
        prefs.push_subscription_keys = json.dumps(subscription.get('keys', {}))
        prefs.push_notifications_enabled = True

        db.commit()

        return {"message": "Push subscription saved successfully"}

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error saving push subscription: {e}", exc_info=True)
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to save push subscription"
        )
