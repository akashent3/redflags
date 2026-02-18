"""Watchlist API endpoints with auto-analysis trigger."""

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
from app.models.annual_report import AnnualReport
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
# ========== NEW IMPORTS ==========
from app.services.portfolio_service import get_real_time_price, map_broker_symbol
from app.tasks.analysis_tasks import analyze_company_by_symbol_task
# =================================

logger = logging.getLogger(__name__)

router = APIRouter()


@router.get(
    "/",
    response_model=WatchlistResponse,
    summary="Get user's watchlist",
    description="Get all companies in user's watchlist with risk scores, recent alerts, and real-time prices.",
)
async def get_watchlist(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """Get user's complete watchlist with alerts and real-time prices."""
    try:
        # Get watchlist items
        watchlist_items = db.query(WatchlistItem).filter(
            WatchlistItem.user_id == current_user.id
        ).all()

        # Build response items
        response_items = []
        for item in watchlist_items:
            company = item.company

            # Get latest analysis for risk score — join via AnnualReport
            latest_analysis = db.query(AnalysisResult).join(
                AnnualReport, AnalysisResult.report_id == AnnualReport.id
            ).filter(
                AnnualReport.company_id == company.id
            ).order_by(AnalysisResult.created_at.desc()).first()

            current_risk_score = latest_analysis.risk_score if latest_analysis else None
            current_risk_level = latest_analysis.risk_level if latest_analysis else None
            last_analysis_date = latest_analysis.created_at if latest_analysis else None

            # Calculate score change
            score_change = None
            if item.last_known_risk_score and current_risk_score:
                score_change = current_risk_score - item.last_known_risk_score

            # ========== NEW: Get real-time price ==========
            price_data = get_real_time_price(company.nse_symbol or company.display_code)
            # ==============================================

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
                latest_analysis_id=latest_analysis.id if latest_analysis else None,
                # ========== Real-time price data ==========
                current_price=price_data.get("current_price") or None if price_data else None,
                price_change=None,  # API returns percent only, no absolute change
                price_change_percent=price_data.get("change_percent") if price_data and price_data.get("current_price") else None,
                high=price_data.get("high52") or None if price_data else None,
                low=price_data.get("low52") or None if price_data else None,
                volume=price_data.get("volume") or None if price_data else None,
                # ==========================================
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
            alerts=alert_responses,
        )

    except Exception as e:
        logger.error(f"Error fetching watchlist: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to fetch watchlist: {str(e)}"
        )


@router.post(
    "/",
    response_model=WatchlistItemResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Add company to watchlist",
    description="Add a company to user's watchlist. AUTO-TRIGGERS analysis if not already exists.",
)
async def add_to_watchlist(
    data: WatchlistItemCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """
    Add company to watchlist.
    
    AUTO-TRIGGERS analysis if no analysis exists for this company.
    """
    try:
        # Check if company exists
        company = db.query(Company).filter(Company.id == data.company_id).first()
        if not company:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Company not found"
            )

        # Check if already in watchlist
        existing = db.query(WatchlistItem).filter(
            WatchlistItem.user_id == current_user.id,
            WatchlistItem.company_id == data.company_id
        ).first()

        if existing:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Company already in watchlist"
            )

        # Get latest analysis for risk score — join via AnnualReport
        latest_analysis = db.query(AnalysisResult).join(
            AnnualReport, AnalysisResult.report_id == AnnualReport.id
        ).filter(
            AnnualReport.company_id == company.id
        ).order_by(AnalysisResult.created_at.desc()).first()

        # Create watchlist item
        watchlist_item = WatchlistItem(
            user_id=current_user.id,
            company_id=company.id,
            alert_enabled=data.alert_enabled,
            last_known_risk_score=latest_analysis.risk_score if latest_analysis else None
        )
        db.add(watchlist_item)
        db.commit()
        db.refresh(watchlist_item)

        # ========== AUTO-TRIGGER ANALYSIS IF NOT EXISTS ==========
        auto_analysis_triggered = False
        if not latest_analysis:
            logger.info(f"🚀 Auto-triggering analysis for {company.display_code} (added to watchlist)")
            symbol = map_broker_symbol(company.nse_symbol or company.display_code)
            # Call .delay() directly — Celery dispatches the task to the worker queue
            task = analyze_company_by_symbol_task.delay(symbol, str(current_user.id))
            logger.info(f"✓ Celery task dispatched: {task.id} for symbol {symbol}")
            auto_analysis_triggered = True
        # ==========================================================

        # ========== NEW: Get real-time price ==========
        price_data = get_real_time_price(company.nse_symbol or company.display_code)
        # ==============================================

        return WatchlistItemResponse(
            watchlist_id=watchlist_item.id,
            company_id=company.id,
            symbol=company.display_code,
            company_name=company.name,
            industry=company.industry,
            sector=company.sector,
            current_risk_score=latest_analysis.risk_score if latest_analysis else None,
            current_risk_level=latest_analysis.risk_level if latest_analysis else None,
            previous_risk_score=None,
            score_change=None,
            last_analysis_date=latest_analysis.created_at if latest_analysis else None,
            added_date=watchlist_item.added_at,
            alert_enabled=watchlist_item.alert_enabled,
            latest_analysis_id=latest_analysis.id if latest_analysis else None,
            auto_analysis_triggered=auto_analysis_triggered,
            # ========== Real-time price data ==========
            current_price=price_data.get("current_price") or None if price_data else None,
            price_change=None,  # API returns percent only, no absolute change
            price_change_percent=price_data.get("change_percent") if price_data and price_data.get("current_price") else None,
            high=price_data.get("high52") or None if price_data else None,
            low=price_data.get("low52") or None if price_data else None,
            volume=price_data.get("volume") or None if price_data else None,
            # ==========================================
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
            detail="Failed to remove from watchlist"
        )


@router.patch(
    "/{watchlist_id}/alerts",
    summary="Toggle watchlist alerts",
    description="Enable/disable alerts for a watchlist item.",
)
async def toggle_watchlist_alerts(
    watchlist_id: UUID,
    alert_enabled: bool,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """Toggle alerts for watchlist item."""
    try:
        item = db.query(WatchlistItem).filter(
            WatchlistItem.id == watchlist_id,
            WatchlistItem.user_id == current_user.id
        ).first()

        if not item:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Watchlist item not found"
            )

        item.alert_enabled = alert_enabled
        db.commit()

        return {"message": "Alert settings updated", "alert_enabled": alert_enabled}

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error toggling alerts: {e}", exc_info=True)
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to update alert settings"
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
            # Check if user has Premium subscription for push notifications — admins bypass
            if data.push_notifications_enabled and not current_user.is_admin and current_user.subscription_tier != "premium":
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

        # Check Premium subscription — admins always bypass
        if not current_user.is_admin and current_user.subscription_tier != 'premium':
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