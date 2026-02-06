"""Authentication API endpoints."""

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.user import User
from app.schemas import SignupRequest, TokenResponse, UserResponse
from app.services import auth_service
from app.utils import create_access_token, get_current_active_user

router = APIRouter()


@router.post(
    "/signup",
    response_model=UserResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Register new user",
    description="Create a new user account with email and password"
)
async def signup(
    request: SignupRequest,
    db: Session = Depends(get_db)
):
    """
    Register a new user.

    - **email**: Valid email address (will be converted to lowercase)
    - **password**: Strong password (8-128 chars, uppercase, lowercase, digit, special char)
    - **full_name**: Optional full name

    Returns the created user (without password).
    """
    user = auth_service.create_user(
        db=db,
        email=request.email,
        password=request.password,
        full_name=request.full_name
    )
    return user


@router.post(
    "/login",
    response_model=TokenResponse,
    summary="Login",
    description="Authenticate with email and password to receive JWT token"
)
async def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db)
):
    """
    Login with email and password.

    - **username**: Email address (OAuth2 form uses 'username' field)
    - **password**: User's password

    Returns a JWT access token that expires in 24 hours.
    Use this token in the Authorization header: `Bearer <token>`
    """
    user = auth_service.authenticate_user(
        db=db,
        email=form_data.username,  # OAuth2PasswordRequestForm uses 'username' field for email
        password=form_data.password
    )

    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # Create access token with user ID in 'sub' claim
    access_token = create_access_token(data={"sub": str(user.id)})

    return {"access_token": access_token, "token_type": "bearer"}


@router.get(
    "/me",
    response_model=UserResponse,
    summary="Get current user",
    description="Get the current authenticated user's information"
)
async def get_current_user_info(
    current_user: User = Depends(get_current_active_user)
):
    """
    Get current user information.

    Requires authentication (JWT token in Authorization header).

    Returns the authenticated user's profile.
    """
    return current_user
