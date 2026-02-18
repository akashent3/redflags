"""User profile management API endpoints."""

import logging
from fastapi import APIRouter, Depends, File, HTTPException, Query, UploadFile, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.user import User
from app.schemas.user import (
    PasswordChangeRequest,
    ProfileUpdateRequest,
    UserResponse,
    AvatarUploadResponse,
    DataExportResponse,
    AccountDeletionResponse,
)
from app.utils.dependencies import get_current_active_user

logger = logging.getLogger(__name__)
router = APIRouter()


@router.get(
    "/profile",
    response_model=UserResponse,
    summary="Get user profile",
    description="Get current user's profile information.",
)
async def get_profile(
    current_user: User = Depends(get_current_active_user),
):
    """Get user profile."""
    return UserResponse(
        id=current_user.id,
        email=current_user.email,
        full_name=current_user.full_name,
        subscription_tier=current_user.subscription_tier,
        subscription_active=current_user.subscription_active,
        reports_used_this_month=current_user.reports_used_this_month,
        reports_limit=current_user.reports_limit,
        is_active=current_user.is_active,
        is_verified=current_user.is_verified,
        created_at=current_user.created_at,
        updated_at=current_user.updated_at,
        last_login=current_user.last_login,
    )


@router.patch(
    "/profile",
    summary="Update profile",
    description="Update user profile (name, email).",
)
async def update_profile(
    data: ProfileUpdateRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """Update user profile."""
    try:
        updated = False

        if data.full_name is not None:
            current_user.full_name = data.full_name
            updated = True

        if data.email is not None:
            # Check if email already exists
            existing = db.query(User).filter(User.email == data.email).first()
            if existing and existing.id != current_user.id:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Email already in use"
                )
            current_user.email = data.email
            updated = True

        if updated:
            db.commit()
            db.refresh(current_user)

        return {
            "message": "Profile updated successfully",
            "email": current_user.email,
            "full_name": current_user.full_name,
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error updating profile: {e}", exc_info=True)
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to update profile"
        )


@router.post(
    "/password",
    summary="Change password",
    description="Change user password.",
)
async def change_password(
    data: PasswordChangeRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """Change user password."""
    try:
        from app.utils.security import get_password_hash, verify_password

        # Verify old password
        if not verify_password(data.old_password, current_user.hashed_password):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Incorrect current password"
            )

        # Update password
        current_user.hashed_password = get_password_hash(data.new_password)
        db.commit()

        return {"message": "Password changed successfully"}

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error changing password: {e}", exc_info=True)
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to change password"
        )


@router.delete(
    "/account",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete account",
    description="Permanently delete user account and all associated data.",
)
async def delete_account(
    confirmation: str = Query(..., description="User's email for confirmation"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """Permanently delete user account."""
    try:
        # Verify confirmation (user must enter their email)
        if confirmation != current_user.email:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email confirmation does not match"
            )

        # Delete all related data (cascade should handle this)
        db.delete(current_user)
        db.commit()

        return None

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting account: {e}", exc_info=True)
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to delete account"
        )


@router.post(
    "/upload-avatar",
    response_model=AvatarUploadResponse,
    summary="Upload avatar",
    description="Upload user avatar image to R2 storage.",
)
async def upload_avatar(
    file: UploadFile = File(..., description="Avatar image file"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """Upload user avatar to R2 storage."""
    try:
        # Validate file type
        allowed_types = ['image/jpeg', 'image/png', 'image/jpg', 'image/webp']
        if file.content_type not in allowed_types:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Invalid file type. Allowed: JPEG, PNG, WebP"
            )

        # Validate file size (max 5MB)
        content = await file.read()
        if len(content) > 5 * 1024 * 1024:  # 5MB
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="File too large. Maximum size: 5MB"
            )

        # Upload to R2
        from app.services.r2_storage import r2_client

        # Generate object key: avatars/{user_id}.jpg
        extension = file.content_type.split('/')[-1]
        if extension == 'jpeg':
            extension = 'jpg'
        object_key = f"avatars/{current_user.id}.{extension}"

        avatar_url = r2_client.upload_file(content, object_key)

        # Update user model
        if not hasattr(current_user, 'avatar_url'):
            # Add avatar_url field to User model if not exists
            logger.warning("avatar_url field not found in User model")
        else:
            current_user.avatar_url = avatar_url
            db.commit()

        return AvatarUploadResponse(
            avatar_url=avatar_url,
            message="Avatar uploaded successfully"
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error uploading avatar: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to upload avatar: {str(e)}"
        )


@router.get(
    "/export-data",
    summary="Export user data",
    description="Request a ZIP export of all user data (reports, watchlist, portfolios).",
)
async def export_user_data(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """
    Generate ZIP file with all user data.

    Note: This creates a background task. User will receive email with download link.
    """
    try:
        from app.tasks.export_tasks import generate_user_data_export

        # Queue background task
        task = generate_user_data_export.delay(str(current_user.id))

        return {
            "message": "Data export started. You will receive an email with download link when ready.",
            "task_id": task.id,
            "estimated_time": "5-10 minutes",
        }

    except Exception as e:
        logger.error(f"Error initiating data export: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to initiate data export"
        )
