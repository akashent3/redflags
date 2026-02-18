"""Celery tasks for watchlist alerts and notifications."""

import logging
from datetime import datetime, timedelta

from celery import shared_task
from sqlalchemy.orm import Session

from app.database import SessionLocal
from app.models.analysis_result import AnalysisResult
from app.models.annual_report import AnnualReport
from app.models.user import User
from app.models.watchlist import NotificationPreference, WatchlistAlert, WatchlistItem

logger = logging.getLogger(__name__)


@shared_task
def check_watchlist_alerts():
    """
    Daily task to check watchlist items for score changes.
    Runs at 8 AM IST daily.
    """
    db = SessionLocal()
    try:
        items = db.query(WatchlistItem).filter(
            WatchlistItem.alert_enabled == True
        ).all()

        alerts_created = 0

        for item in items:
            # Get latest analysis — join via AnnualReport (AnalysisResult has no direct company_id)
            latest_analysis = db.query(AnalysisResult).join(
                AnnualReport, AnalysisResult.report_id == AnnualReport.id
            ).filter(
                AnnualReport.company_id == item.company_id
            ).order_by(AnalysisResult.created_at.desc()).first()

            if not latest_analysis:
                continue

            current_score = latest_analysis.risk_score
            previous_score = item.last_known_risk_score

            # Check for significant change (threshold: 10 points)
            if previous_score is not None and abs(current_score - previous_score) >= 10:
                # Determine severity
                score_change = current_score - previous_score
                if current_score >= 60:
                    severity = "CRITICAL"
                elif current_score >= 40 or abs(score_change) >= 20:
                    severity = "WARNING"
                else:
                    severity = "INFO"

                # Create message
                direction = "increased" if score_change > 0 else "decreased"
                message = f"Risk score {direction} from {previous_score} to {current_score} ({score_change:+d} points)"

                # Create alert
                alert = WatchlistAlert(
                    watchlist_item_id=item.id,
                    alert_type="SCORE_CHANGE",
                    severity=severity,
                    message=message,
                    previous_risk_score=previous_score,
                    current_risk_score=current_score,
                    score_change=score_change,
                )
                db.add(alert)
                alerts_created += 1

                # Send real-time notifications (for Premium users with real_time frequency)
                user = item.user
                prefs = user.notification_preferences
                if prefs and prefs.alert_frequency == 'real_time' and user.subscription_tier == 'premium':
                    # Send email
                    if prefs.email_alerts_enabled:
                        send_real_time_alert_email.delay(str(user.id), str(alert.id))

                    # Send push notification
                    if prefs.push_notifications_enabled:
                        from app.services.push_service import send_watchlist_alert_push
                        company = item.company
                        send_watchlist_alert_push(str(user.id), {
                            'alert_id': str(alert.id),
                            'company_id': str(company.id),
                            'company_name': company.name,
                            'severity': severity,
                            'message': message,
                        })

            # Update watchlist item
            item.last_known_risk_score = current_score
            item.last_checked_at = datetime.utcnow()

        db.commit()
        logger.info(f"Checked {len(items)} watchlist items, created {alerts_created} alerts")
        return f"Checked {len(items)} watchlist items, created {alerts_created} alerts"

    except Exception as e:
        logger.error(f"Error checking watchlist alerts: {e}", exc_info=True)
        db.rollback()
        raise e
    finally:
        db.close()


@shared_task
def send_weekly_digest():
    """
    Weekly task to send digest emails.
    Runs Monday 9 AM IST.
    """
    db = SessionLocal()
    try:
        # Get users with weekly digest enabled
        prefs = db.query(NotificationPreference).filter(
            NotificationPreference.weekly_digest_enabled == True
        ).all()

        emails_sent = 0
        seven_days_ago = datetime.utcnow() - timedelta(days=7)

        for pref in prefs:
            user = pref.user

            # Get user's unread alerts from past 7 days
            alerts = db.query(WatchlistAlert).join(
                WatchlistItem
            ).filter(
                WatchlistItem.user_id == user.id,
                WatchlistAlert.created_at >= seven_days_ago,
                WatchlistAlert.is_read == False
            ).order_by(
                WatchlistAlert.severity.desc(),
                WatchlistAlert.created_at.desc()
            ).all()

            if alerts:
                # Send digest email
                from app.services.email_service import send_weekly_digest_email
                send_weekly_digest_email(
                    to_email=user.email,
                    user_name=user.full_name,
                    alerts=[{
                        'company_name': a.watchlist_item.company.name,
                        'message': a.message,
                        'severity': a.severity,
                    } for a in alerts]
                )
                emails_sent += 1

        logger.info(f"Sent {emails_sent} weekly digest emails")
        return f"Sent {emails_sent} weekly digest emails"

    except Exception as e:
        logger.error(f"Error sending weekly digest: {e}", exc_info=True)
        raise e
    finally:
        db.close()


@shared_task
def send_real_time_alert_email(user_id: str, alert_id: str):
    """
    Send immediate email for critical alert (Premium users only).
    """
    db = SessionLocal()
    try:
        from app.services.email_service import send_watchlist_alert_email

        user = db.query(User).filter(User.id == user_id).first()
        alert = db.query(WatchlistAlert).filter(WatchlistAlert.id == alert_id).first()

        if user and alert:
            company = alert.watchlist_item.company
            send_watchlist_alert_email(
                to_email=user.email,
                user_name=user.full_name,
                company_name=company.name,
                symbol=company.display_code,
                alert_type=alert.alert_type,
                severity=alert.severity,
                message=alert.message,
                current_score=alert.current_risk_score,
                previous_score=alert.previous_risk_score,
            )
            logger.info(f"Sent real-time alert email to {user.email}")
    except Exception as e:
        logger.error(f"Error sending real-time alert email: {e}", exc_info=True)
        raise e
    finally:
        db.close()
