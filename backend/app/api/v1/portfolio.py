"""Portfolio API endpoints."""

import logging
from typing import List
from uuid import UUID

from fastapi import APIRouter, Depends, File, Form, HTTPException, UploadFile, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.portfolio import Holding, Portfolio
from app.models.user import User
from app.schemas.portfolio import (
    CSVUploadResponse,
    HoldingResponse,
    PortfolioListResponse,
    PortfolioResponse,
)
from app.services.portfolio_service import (
    calculate_portfolio_metrics,
    get_risk_scores,
    match_symbols_to_companies,
    parse_portfolio_csv,
)
from app.utils.dependencies import get_current_active_user

logger = logging.getLogger(__name__)
router = APIRouter()

MAX_FILE_SIZE = 10 * 1024 * 1024  # 10MB


@router.post(
    "/upload",
    response_model=CSVUploadResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Upload portfolio CSV",
    description="Upload broker CSV and create portfolio with holdings.",
)
async def upload_portfolio_csv(
    file: UploadFile = File(...),
    portfolio_name: str = Form("My Portfolio"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """Upload portfolio CSV and create portfolio with holdings."""
    try:
        # Check subscription (Premium only)
        if current_user.subscription_tier != 'premium':
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Portfolio scanner requires Premium subscription"
            )

        # Validate file type
        if not file.filename.endswith('.csv'):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Only CSV files are supported"
            )

        # Read and validate file size
        file_content = await file.read()
        if len(file_content) > MAX_FILE_SIZE:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"File too large (max {MAX_FILE_SIZE // 1024 // 1024}MB)"
            )

        # Parse CSV
        holdings = parse_portfolio_csv(file_content)

        # Match symbols to companies
        matched, unmatched = match_symbols_to_companies(db, holdings)

        if not matched:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"No companies matched. Unmatched symbols: {', '.join(unmatched)}"
            )

        # Get risk scores for matched companies
        company_ids = [data['company'].id for data in matched.values()]
        risk_data = get_risk_scores(db, company_ids)

        # Create portfolio
        portfolio = Portfolio(
            user_id=current_user.id,
            name=portfolio_name,
        )
        db.add(portfolio)
        db.flush()  # Get portfolio ID

        # Create holdings
        holding_records = []
        for symbol, data in matched.items():
            company = data['company']
            holding_create = data['holding']
            risk_info = risk_data.get(str(company.id), {})

            holding = Holding(
                portfolio_id=portfolio.id,
                company_id=company.id,
                symbol=symbol,
                company_name=company.name,
                quantity=holding_create.quantity,
                avg_price=holding_create.avg_price,
                investment_value=holding_create.quantity * holding_create.avg_price,
                risk_score=risk_info.get('risk_score'),
                risk_level=risk_info.get('risk_level'),
                flags_count=risk_info.get('flags_count'),
            )
            db.add(holding)
            holding_records.append(holding)

        # Calculate and update portfolio metrics
        metrics = calculate_portfolio_metrics(holding_records)
        portfolio.total_investment = metrics['total_investment']
        portfolio.average_risk_score = metrics['average_risk_score']
        portfolio.high_risk_count = metrics['high_risk_count']

        db.commit()
        db.refresh(portfolio)

        return CSVUploadResponse(
            portfolio_id=portfolio.id,
            total_holdings=len(holdings),
            matched_companies=len(matched),
            unmatched_symbols=unmatched,
            total_investment=float(metrics['total_investment']),
        )

    except HTTPException:
        raise
    except ValueError as e:
        logger.error(f"CSV parsing error: {e}")
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        logger.error(f"Error uploading portfolio: {e}", exc_info=True)
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to process portfolio: {str(e)}"
        )


@router.get(
    "/",
    response_model=PortfolioListResponse,
    summary="Get portfolios",
    description="Get user's portfolios.",
)
async def get_portfolios(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """Get user's portfolios."""
    try:
        portfolios = db.query(Portfolio).filter(
            Portfolio.user_id == current_user.id
        ).order_by(Portfolio.created_at.desc()).all()

        portfolio_responses = []
        for portfolio in portfolios:
            holdings_response = [
                HoldingResponse(
                    holding_id=h.id,
                    symbol=h.symbol,
                    company_name=h.company_name,
                    quantity=h.quantity,
                    avg_price=float(h.avg_price),
                    investment_value=float(h.investment_value),
                    risk_score=h.risk_score,
                    risk_level=h.risk_level,
                    flags_count=h.flags_count,
                )
                for h in portfolio.holdings
            ]

            portfolio_responses.append(PortfolioResponse(
                portfolio_id=portfolio.id,
                user_id=portfolio.user_id,
                name=portfolio.name,
                description=portfolio.description,
                holdings=holdings_response,
                total_investment=float(portfolio.total_investment),
                average_risk_score=portfolio.average_risk_score,
                high_risk_count=portfolio.high_risk_count,
                created_at=portfolio.created_at,
                updated_at=portfolio.updated_at,
            ))

        return PortfolioListResponse(
            portfolios=portfolio_responses,
            total=len(portfolio_responses),
        )

    except Exception as e:
        logger.error(f"Error fetching portfolios: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to fetch portfolios"
        )


@router.get(
    "/{portfolio_id}",
    response_model=PortfolioResponse,
    summary="Get portfolio details",
    description="Get portfolio details with holdings.",
)
async def get_portfolio(
    portfolio_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """Get portfolio details with holdings."""
    try:
        portfolio = db.query(Portfolio).filter(
            Portfolio.id == portfolio_id,
            Portfolio.user_id == current_user.id
        ).first()

        if not portfolio:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Portfolio not found"
            )

        holdings_response = [
            HoldingResponse(
                holding_id=h.id,
                symbol=h.symbol,
                company_name=h.company_name,
                quantity=h.quantity,
                avg_price=float(h.avg_price),
                investment_value=float(h.investment_value),
                risk_score=h.risk_score,
                risk_level=h.risk_level,
                flags_count=h.flags_count,
            )
            for h in portfolio.holdings
        ]

        return PortfolioResponse(
            portfolio_id=portfolio.id,
            user_id=portfolio.user_id,
            name=portfolio.name,
            description=portfolio.description,
            holdings=holdings_response,
            total_investment=float(portfolio.total_investment),
            average_risk_score=portfolio.average_risk_score,
            high_risk_count=portfolio.high_risk_count,
            created_at=portfolio.created_at,
            updated_at=portfolio.updated_at,
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error fetching portfolio: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to fetch portfolio"
        )


@router.delete(
    "/{portfolio_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete portfolio",
    description="Delete portfolio (cascade deletes holdings).",
)
async def delete_portfolio(
    portfolio_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """Delete portfolio (cascade deletes holdings)."""
    try:
        portfolio = db.query(Portfolio).filter(
            Portfolio.id == portfolio_id,
            Portfolio.user_id == current_user.id
        ).first()

        if not portfolio:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Portfolio not found"
            )

        db.delete(portfolio)
        db.commit()

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting portfolio: {e}", exc_info=True)
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to delete portfolio"
        )
