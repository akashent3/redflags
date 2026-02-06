"""Email service using Brevo (formerly Sendinblue) for transactional emails."""

import logging
import os
from typing import Any, Dict, List

import sib_api_v3_sdk
from sib_api_v3_sdk.rest import ApiException

logger = logging.getLogger(__name__)

# Initialize Brevo API client
configuration = sib_api_v3_sdk.Configuration()
configuration.api_key['api-key'] = os.getenv('BREVO_API_KEY', '')
api_instance = sib_api_v3_sdk.TransactionalEmailsApi(sib_api_v3_sdk.ApiClient(configuration))

# Email configuration
FROM_EMAIL = os.getenv('FROM_EMAIL', 'noreply@redflag-ai.com')
FROM_NAME = os.getenv('FROM_NAME', 'RedFlag AI')


def send_email(to_email: str, to_name: str, subject: str, html_content: str):
    """Send email via Brevo."""
    try:
        send_smtp_email = sib_api_v3_sdk.SendSmtpEmail(
            to=[sib_api_v3_sdk.SendSmtpEmailTo(email=to_email, name=to_name)],
            sender=sib_api_v3_sdk.SendSmtpEmailSender(email=FROM_EMAIL, name=FROM_NAME),
            subject=subject,
            html_content=html_content,
        )

        response = api_instance.send_transac_email(send_smtp_email)
        logger.info(f"Email sent to {to_email}: {response}")
        return response

    except ApiException as e:
        logger.error(f"Failed to send email to {to_email}: {e}")
        raise


def send_watchlist_alert_email(
    to_email: str,
    user_name: str,
    company_name: str,
    symbol: str,
    alert_type: str,
    severity: str,
    message: str,
    current_score: int,
    previous_score: int,
):
    """Send watchlist alert email (real-time)."""
    severity_colors = {
        'INFO': '#3b82f6',
        'WARNING': '#f59e0b',
        'CRITICAL': '#ef4444',
    }
    color = severity_colors.get(severity, '#gray')

    html_content = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <style>
            body {{ font-family: Arial, sans-serif; color: #333; }}
            .header {{ background-color: {color}; color: white; padding: 20px; }}
            .content {{ padding: 20px; }}
            .score {{ font-size: 24px; font-weight: bold; }}
        </style>
    </head>
    <body>
        <div class="header">
            <h1>⚠️ Watchlist Alert: {company_name}</h1>
        </div>
        <div class="content">
            <p>Hi {user_name},</p>
            <p>A {severity} alert has been triggered for <strong>{company_name} ({symbol})</strong> in your watchlist:</p>

            <div style="background-color: #f3f4f6; padding: 15px; border-left: 4px solid {color};">
                <p><strong>Alert Type:</strong> {alert_type}</p>
                <p><strong>Message:</strong> {message}</p>
                <p class="score">
                    Previous Risk Score: {previous_score}<br>
                    Current Risk Score: {current_score}
                </p>
            </div>

            <p style="margin-top: 20px;">
                <a href="https://redflag-ai.com/watchlist" style="background-color: #3b82f6; color: white; padding: 10px 20px; text-decoration: none; border-radius: 5px;">
                    View Watchlist
                </a>
            </p>

            <p style="margin-top: 30px; color: #666; font-size: 12px;">
                This is an automated alert from RedFlag AI. To manage your watchlist alerts, visit your <a href="https://redflag-ai.com/settings">notification settings</a>.
            </p>
        </div>
    </body>
    </html>
    """

    send_email(
        to_email=to_email,
        to_name=user_name,
        subject=f"🚨 {severity} Alert: {company_name}",
        html_content=html_content,
    )


def send_weekly_digest_email(to_email: str, user_name: str, alerts: List[Dict[str, Any]]):
    """Send weekly digest email with all alerts."""
    # Group alerts by company
    alerts_by_company = {}
    for alert in alerts:
        company = alert['company_name']
        if company not in alerts_by_company:
            alerts_by_company[company] = []
        alerts_by_company[company].append(alert)

    # Build HTML table
    alerts_html = ""
    for company, company_alerts in alerts_by_company.items():
        alerts_html += f"<h3>{company}</h3><ul>"
        for alert in company_alerts:
            alerts_html += f"<li>{alert['message']} ({alert['severity']})</li>"
        alerts_html += "</ul>"

    html_content = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <style>
            body {{ font-family: Arial, sans-serif; }}
            .header {{ background: linear-gradient(to right, #6366f1, #3b82f6); color: white; padding: 30px; }}
        </style>
    </head>
    <body>
        <div class="header">
            <h1>📊 Your Weekly Watchlist Digest</h1>
        </div>
        <div style="padding: 20px;">
            <p>Hi {user_name},</p>
            <p>Here's your weekly summary of watchlist alerts:</p>

            {alerts_html}

            <p style="margin-top: 30px;">
                <a href="https://redflag-ai.com/watchlist" style="background-color: #3b82f6; color: white; padding: 12px 24px; text-decoration: none; border-radius: 5px;">
                    View Full Watchlist
                </a>
            </p>
        </div>
    </body>
    </html>
    """

    send_email(
        to_email=to_email,
        to_name=user_name,
        subject="📊 Your Weekly Watchlist Digest",
        html_content=html_content,
    )


def send_data_export_email(to_email: str, user_name: str, download_url: str):
    """Send data export ready email."""
    html_content = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <style>
            body {{ font-family: Arial, sans-serif; }}
        </style>
    </head>
    <body>
        <div style="padding: 20px;">
            <p>Hi {user_name},</p>
            <p>Your data export is ready! Download it here:</p>
            <p style="margin-top: 20px;">
                <a href="{download_url}" style="background-color: #3b82f6; color: white; padding: 12px 24px; text-decoration: none; border-radius: 5px;">
                    Download Data Export
                </a>
            </p>
            <p style="margin-top: 20px; color: #666;">This link will expire in 7 days.</p>
        </div>
    </body>
    </html>
    """

    send_email(
        to_email=to_email,
        to_name=user_name,
        subject="Your Data Export is Ready",
        html_content=html_content,
    )
