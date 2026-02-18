"""Admin utilities and middleware for protecting admin-only endpoints."""

import logging
from fastapi import Depends, HTTPException, status

from app.models.user import User
from app.utils.dependencies import get_current_active_user

logger = logging.getLogger(__name__)


def require_admin(current_user: User = Depends(get_current_active_user)) -> User:
    """
    Dependency that ensures the current user has admin privileges.

    Args:
        current_user: The currently authenticated user

    Returns:
        User object if user is admin

    Raises:
        HTTPException: 403 Forbidden if user is not an admin
    """
    if not current_user.is_admin:
        logger.warning(
            f"Admin access denied for user {current_user.id} ({current_user.email})"
        )
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin access required. You do not have permission to access this resource."
        )

    logger.info(f"Admin access granted for user {current_user.id} ({current_user.email})")
    return current_user


def check_admin_or_self(
    target_user_id: str,
    current_user: User = Depends(get_current_active_user)
) -> User:
    """
    Check if current user is admin OR accessing their own data.

    Args:
        target_user_id: The user ID being accessed
        current_user: The currently authenticated user

    Returns:
        User object if authorized

    Raises:
        HTTPException: 403 Forbidden if not admin and not accessing own data
    """
    # Allow if admin
    if current_user.is_admin:
        return current_user

    # Allow if accessing own data
    if str(current_user.id) == str(target_user_id):
        return current_user

    # Deny otherwise
    logger.warning(
        f"Unauthorized access attempt: user {current_user.id} tried to access "
        f"user {target_user_id}'s data"
    )
    raise HTTPException(
        status_code=status.HTTP_403_FORBIDDEN,
        detail="You can only access your own data unless you are an admin."
    )
