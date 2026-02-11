"""API v1 router consolidation."""

from fastapi import APIRouter

from app.api.v1.analysis import router as analysis_router
from app.api.v1.auth import router as auth_router
from app.api.v1.companies import router as companies_router
# Disabled mock data
# from app.api.v1.fraud_cases import router as fraud_cases_router
from app.api.v1.portfolio import router as portfolio_router
from app.api.v1.reports import router as reports_router
from app.api.v1.users import router as users_router
from app.api.v1.watchlist import router as watchlist_router

# Create main API router
api_router = APIRouter()

# Include authentication routes
api_router.include_router(
    auth_router,
    prefix="/auth",
    tags=["Authentication"]
)

# Include company routes
api_router.include_router(
    companies_router,
    prefix="/companies",
    tags=["Companies"]
)

# Include reports routes
api_router.include_router(
    reports_router,
    prefix="/reports",
    tags=["Reports"]
)

# Include analysis routes
api_router.include_router(
    analysis_router,
    prefix="/analysis",
    tags=["Analysis"]
)

# Include portfolio routes
api_router.include_router(
    portfolio_router,
    prefix="/portfolio",
    tags=["Portfolio"]
)

# Include watchlist routes
api_router.include_router(
    watchlist_router,
    prefix="/watchlist",
    tags=["Watchlist"]
)

# Disabled mock data - fraud cases
# api_router.include_router(
#     fraud_cases_router,
#     prefix="/fraud-cases",
#     tags=["Fraud Cases"]
# )

# Include user routes
api_router.include_router(
    users_router,
    prefix="/users",
    tags=["Users"]
)

__all__ = ["api_router"]
