"""Push notification service using Web Push API."""

import json
import logging
import os

from pywebpush import WebPushException, webpush

logger = logging.getLogger(__name__)

# VAPID keys (generate with: vapid --gen)
VAPID_PRIVATE_KEY = os.getenv('VAPID_PRIVATE_KEY', '')
VAPID_PUBLIC_KEY = os.getenv('VAPID_PUBLIC_KEY', '')
VAPID_CLAIMS = {"sub": f"mailto:{os.getenv('VAPID_CLAIM_EMAIL', 'support@redflag-ai.com')}"}


def send_push_notification(
    subscription_info: dict,
    title: str,
    body: str,
    icon: str = "/icon-192x192.png",
    badge: str = "/badge-72x72.png",
    data: dict = None,
) -> bool:
    """
    Send web push notification.

    Args:
        subscription_info: {endpoint, keys: {p256dh, auth}}
        title: Notification title
        body: Notification body
        icon: Icon URL
        badge: Badge URL
        data: Additional data

    Returns:
        True if successful, False otherwise
    """
    try:
        # Build notification payload
        payload = json.dumps({
            "title": title,
            "body": body,
            "icon": icon,
            "badge": badge,
            "data": data or {},
        })

        # Send push notification
        response = webpush(
            subscription_info=subscription_info,
            data=payload,
            vapid_private_key=VAPID_PRIVATE_KEY,
            vapid_claims=VAPID_CLAIMS,
        )

        logger.info(f"Push notification sent successfully: {response.status_code}")
        return True

    except WebPushException as e:
        logger.error(f"Failed to send push notification: {e}")

        # Handle gone subscriptions (410)
        if e.response and e.response.status_code == 410:
            logger.warning(f"Subscription expired: {subscription_info.get('endpoint')}")
            # TODO: Remove subscription from database

        return False
    except Exception as e:
        logger.error(f"Unexpected error sending push notification: {e}", exc_info=True)
        return False


def send_watchlist_alert_push(user_id: str, alert: dict) -> bool:
    """
    Send push notification for watchlist alert.

    Args:
        user_id: User ID
        alert: Alert data dict

    Returns:
        True if successful, False otherwise
    """
    from app.database import SessionLocal
    from app.models.user import User

    db = SessionLocal()
    try:
        user = db.query(User).filter(User.id == user_id).first()
        if not user or not user.notification_preferences:
            logger.warning(f"User or preferences not found: {user_id}")
            return False

        prefs = user.notification_preferences
        if not prefs.push_notifications_enabled or not prefs.push_subscription_endpoint:
            logger.info(f"Push notifications not enabled for user: {user_id}")
            return False

        # Parse subscription info
        try:
            subscription_info = {
                "endpoint": prefs.push_subscription_endpoint,
                "keys": json.loads(prefs.push_subscription_keys) if prefs.push_subscription_keys else {},
            }
        except json.JSONDecodeError as e:
            logger.error(f"Invalid subscription keys for user {user_id}: {e}")
            return False

        # Send push notification
        severity_emoji = {
            'INFO': 'ℹ️',
            'WARNING': '⚠️',
            'CRITICAL': '🚨',
        }
        emoji = severity_emoji.get(alert.get('severity', 'INFO'), '📊')

        return send_push_notification(
            subscription_info=subscription_info,
            title=f"{emoji} {alert.get('severity', 'Alert')}: {alert.get('company_name', 'Company')}",
            body=alert.get('message', 'New watchlist alert'),
            data={
                'alert_id': alert.get('alert_id'),
                'company_id': alert.get('company_id'),
                'url': f"/watchlist#alert-{alert.get('alert_id')}",
            },
        )

    except Exception as e:
        logger.error(f"Error sending watchlist alert push: {e}", exc_info=True)
        return False
    finally:
        db.close()
