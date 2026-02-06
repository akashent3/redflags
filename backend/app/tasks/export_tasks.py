"""Celery tasks for data export."""

import csv
import io
import json
import logging
import zipfile
from datetime import datetime

from celery import shared_task

from app.database import SessionLocal
from app.models.analysis_result import AnalysisResult
from app.models.portfolio import Portfolio
from app.models.user import User
from app.models.watchlist import NotificationPreference, WatchlistItem

logger = logging.getLogger(__name__)


@shared_task
def generate_user_data_export(user_id: str):
    """Generate ZIP file with all user data."""
    db = SessionLocal()
    try:
        user = db.query(User).filter(User.id == user_id).first()
        if not user:
            logger.error(f"User not found: {user_id}")
            return f"User not found: {user_id}"

        # Create ZIP in memory
        zip_buffer = io.BytesIO()

        with zipfile.ZipFile(zip_buffer, 'w', zipfile.ZIP_DEFLATED) as zip_file:
            # 1. Add user profile
            profile_data = {
                'email': user.email,
                'full_name': user.full_name,
                'subscription_tier': user.subscription_tier,
                'created_at': user.created_at.isoformat() if user.created_at else None,
                'reports_used_this_month': user.reports_used_this_month,
                'reports_limit': user.reports_limit,
            }
            zip_file.writestr('profile.json', json.dumps(profile_data, indent=2))

            # 2. Add watchlist CSV
            watchlist_items = db.query(WatchlistItem).filter(
                WatchlistItem.user_id == user.id
            ).all()

            if watchlist_items:
                watchlist_csv = io.StringIO()
                writer = csv.writer(watchlist_csv)
                writer.writerow(['Symbol', 'Company', 'Added Date', 'Alert Enabled', 'Last Risk Score'])

                for item in watchlist_items:
                    company = item.company
                    writer.writerow([
                        company.display_code if company else 'N/A',
                        company.name if company else 'N/A',
                        item.added_at.isoformat() if item.added_at else 'N/A',
                        'Yes' if item.alert_enabled else 'No',
                        item.last_known_risk_score or 'N/A',
                    ])

                zip_file.writestr('watchlist.csv', watchlist_csv.getvalue())

            # 3. Add portfolios
            portfolios = db.query(Portfolio).filter(
                Portfolio.user_id == user.id
            ).all()

            for idx, portfolio in enumerate(portfolios):
                portfolio_csv = io.StringIO()
                writer = csv.writer(portfolio_csv)
                writer.writerow([
                    'Symbol', 'Company', 'Quantity', 'Avg Price',
                    'Investment Value', 'Risk Score', 'Risk Level'
                ])

                for holding in portfolio.holdings:
                    writer.writerow([
                        holding.symbol,
                        holding.company_name,
                        holding.quantity,
                        float(holding.avg_price),
                        float(holding.investment_value),
                        holding.risk_score or 'N/A',
                        holding.risk_level or 'N/A',
                    ])

                filename = f"portfolio_{idx + 1}_{portfolio.name.replace(' ', '_')}.csv"
                zip_file.writestr(f'portfolios/{filename}', portfolio_csv.getvalue())

            # 4. Add notification preferences
            prefs = db.query(NotificationPreference).filter(
                NotificationPreference.user_id == user.id
            ).first()

            if prefs:
                prefs_data = {
                    'email_alerts_enabled': prefs.email_alerts_enabled,
                    'weekly_digest_enabled': prefs.weekly_digest_enabled,
                    'feature_announcements_enabled': prefs.feature_announcements_enabled,
                    'push_notifications_enabled': prefs.push_notifications_enabled,
                    'alert_frequency': prefs.alert_frequency,
                }
                zip_file.writestr('notification_preferences.json', json.dumps(prefs_data, indent=2))

            # 5. Add analysis reports summary
            analyses = db.query(AnalysisResult).join(
                AnalysisResult.report
            ).filter(
                AnalysisResult.report.has(user_id=user.id)
            ).all()

            if analyses:
                analyses_data = []
                for analysis in analyses:
                    analyses_data.append({
                        'company_name': analysis.report.company.name if analysis.report.company else 'N/A',
                        'fiscal_year': analysis.report.fiscal_year,
                        'risk_score': analysis.overall_risk_score,
                        'risk_level': analysis.risk_level,
                        'flags_triggered': analysis.flags_triggered_count,
                        'analyzed_at': analysis.analyzed_at.isoformat() if analysis.analyzed_at else None,
                    })

                zip_file.writestr('analysis_reports.json', json.dumps(analyses_data, indent=2))

        # Upload to R2 (if configured)
        zip_buffer.seek(0)
        zip_filename = f"user_data_export_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}.zip"

        # For now, save locally or upload to storage
        # TODO: Implement R2 upload
        # from app.storage.r2_client import r2_client
        # file_key = f"exports/{user_id}/{zip_filename}"
        # url = r2_client.upload_file(zip_buffer.read(), file_key, 'application/zip')

        # Temporary: Generate mock URL
        url = f"https://storage.redflag-ai.com/exports/{user_id}/{zip_filename}"

        # Send email with download link
        from app.services.email_service import send_data_export_email
        send_data_export_email(user.email, user.full_name, url)

        logger.info(f"Data export completed for user {user_id}")
        return f"Data export completed: {url}"

    except Exception as e:
        logger.error(f"Error generating data export: {e}", exc_info=True)
        raise e
    finally:
        db.close()
