"""Authentication service layer for user management."""

import uuid
from datetime import datetime
from typing import Optional

from fastapi import HTTPException, status
from sqlalchemy import func
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.models.user import User
from app.utils.security import (
    get_password_hash,
    validate_password_strength,
    verify_password,
)


def create_user(
    db: Session,
    email: str,
    password: str,
    full_name: Optional[str] = None
) -> User:
    """
    Create a new user with hashed password.

    Args:
        db: Database session
        email: User's email address
        password: Plain text password
        full_name: Optional user's full name

    Returns:
        Created User object

    Raises:
        HTTPException 400 if email already exists or password is weak
    """
    # Validate password strength
    validate_password_strength(password)

    # Normalize email to lowercase
    email = email.lower().strip()

    # Check if email already exists
    existing_user = get_user_by_email(db, email)
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )

    # Hash password
    hashed_password = get_password_hash(password)

    # Create user
    user = User(
        id=uuid.uuid4(),
        email=email,
        hashed_password=hashed_password,
        full_name=full_name.strip() if full_name else None,
        is_verified=False,
        verification_token=str(uuid.uuid4()),
    )

    try:
        db.add(user)
        db.commit()
        db.refresh(user)
        return user
    except IntegrityError:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )


def authenticate_user(
    db: Session,
    email: str,
    password: str
) -> Optional[User]:
    """
    Authenticate user by email and password.

    Args:
        db: Database session
        email: User's email address
        password: Plain text password

    Returns:
        User object if authentication successful, None otherwise

    Note:
        Returns None for both "user not found" and "wrong password"
        to avoid revealing whether an email exists in the system
    """
    # Normalize email to lowercase
    email = email.lower().strip()

    # Get user by email
    user = get_user_by_email(db, email)
    if not user:
        return None

    # Verify password
    if not verify_password(password, user.hashed_password):
        return None

    # Update last_login timestamp
    user.last_login = datetime.utcnow()
    db.commit()
    db.refresh(user)

    return user


def get_user_by_email(db: Session, email: str) -> Optional[User]:
    """
    Get user by email (case-insensitive).

    Args:
        db: Database session
        email: User's email address

    Returns:
        User object if found, None otherwise
    """
    email = email.lower().strip()
    return db.query(User).filter(
        func.lower(User.email) == email
    ).first()


def get_user_by_id(db: Session, user_id: uuid.UUID) -> Optional[User]:
    """
    Get user by ID.

    Args:
        db: Database session
        user_id: User's UUID

    Returns:
        User object if found, None otherwise
    """
    return db.query(User).filter(User.id == user_id).first()
