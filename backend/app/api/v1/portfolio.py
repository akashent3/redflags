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
    AddHoldingRequest,
    AddHoldingResponse,
    CSVUploadResponse,
    HoldingResponse,
    PortfolioListResponse,
    PortfolioResponse,
)
from app.services.portfolio_service import (
    calculate_portfolio_metrics,
    get_risk_scores,
    get_real_time_price,
    get_latest_analysis_id_for_company,
    match_symbols_to_companies,
    parse_portfolio_csv,
)
from app.utils.dependencies import get_current_active_user
from app.tasks.analysis_tasks import analyze_company_by_symbol_task
from app.services.portfolio_service import map_broker_symbol

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
        # Check subscription (Premium only) — admins always bypass
        if not current_user.is_admin and current_user.subscription_tier != 'premium':
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

        # Delete any existing portfolios for this user (replace/overwrite on re-upload)
        existing_portfolios = db.query(Portfolio).filter(
            Portfolio.user_id == current_user.id
        ).all()
        for old_portfolio in existing_portfolios:
            db.delete(old_portfolio)
        if existing_portfolios:
            db.flush()  # Ensure old portfolios + holdings are removed before creating new one
            logger.info(f"Replaced {len(existing_portfolios)} existing portfolio(s) for user {current_user.id}")

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
                latest_analysis_id=risk_info.get('latest_analysis_id'),
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

        # Auto-trigger analysis for holdings with no existing risk score
        triggered = 0
        for symbol, data in matched.items():
            company = data['company']
            risk_info = risk_data.get(str(company.id), {})
            if not risk_info.get('risk_score'):
                try:
                    nse_symbol = map_broker_symbol(company.nse_symbol or company.display_code or symbol)
                    task = analyze_company_by_symbol_task.delay(nse_symbol, str(current_user.id))
                    logger.info(f"🚀 Auto-triggered analysis for {nse_symbol} (portfolio upload): task {task.id}")
                    triggered += 1
                except Exception as e:
                    logger.warning(f"Failed to trigger analysis for {symbol}: {e}")

        if triggered:
            logger.info(f"✓ Triggered {triggered} analysis task(s) for portfolio holdings with no existing analysis")

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
            # Live-fetch risk scores for ALL holdings in this portfolio so that
            # analyses completed after the CSV upload are reflected immediately.
            company_ids = [str(h.company_id) for h in portfolio.holdings if h.company_id]
            live_risk_data = get_risk_scores(db, company_ids) if company_ids else {}

            holdings_response = []
            for h in portfolio.holdings:
                # Fetch real-time price data on page load
                price_data = get_real_time_price(h.symbol)

                # Calculate current value and P&L if price available
                current_price = price_data.get("current_price") if price_data else None
                current_value = (current_price * h.quantity) if current_price else None
                pnl = (current_value - float(h.investment_value)) if current_value else None
                pnl_percent = ((pnl / float(h.investment_value)) * 100) if pnl is not None else None

                # Always prefer live-queried risk data over stale stored values.
                # This ensures the UI updates as soon as analysis completes.
                live = live_risk_data.get(str(h.company_id), {}) if h.company_id else {}
                risk_score = live.get("risk_score") or h.risk_score
                risk_level = live.get("risk_level") or h.risk_level
                flags_count = live.get("flags_count") if live.get("flags_count") is not None else h.flags_count
                latest_analysis_id = live.get("latest_analysis_id") or h.latest_analysis_id

                # If live data has a newer risk score, persist it back to the holding
                # so future loads don't have to re-query unnecessarily.
                if risk_score and risk_score != h.risk_score:
                    h.risk_score = risk_score
                    h.risk_level = risk_level
                    h.flags_count = flags_count
                    h.latest_analysis_id = latest_analysis_id
                    db.add(h)

                holdings_response.append(HoldingResponse(
                    holding_id=h.id,
                    symbol=h.symbol,
                    company_name=h.company_name,
                    quantity=h.quantity,
                    avg_price=float(h.avg_price),
                    investment_value=float(h.investment_value),
                    risk_score=risk_score,
                    risk_level=risk_level,
                    flags_count=flags_count,
                    latest_analysis_id=latest_analysis_id,
                    # Real-time price data (fetched on page load)
                    current_price=current_price,
                    current_value=current_value,
                    pnl=pnl,
                    pnl_percent=pnl_percent,
                    price_change=price_data.get("change") if price_data else None,
                    price_change_percent=price_data.get("change_percent") if price_data else None,
                ))

            # Recompute aggregate metrics from live risk data and commit holding updates
            live_scores = [r.risk_score for r in holdings_response if r.risk_score is not None]
            live_avg = sum(live_scores) / len(live_scores) if live_scores else portfolio.average_risk_score
            live_high_risk = sum(1 for r in holdings_response if r.risk_score and r.risk_score >= 60)

            # Update portfolio-level aggregates if they changed
            if live_scores:
                portfolio.average_risk_score = live_avg
                portfolio.high_risk_count = live_high_risk

            try:
                db.commit()
            except Exception:
                db.rollback()

            portfolio_responses.append(PortfolioResponse(
                portfolio_id=portfolio.id,
                user_id=portfolio.user_id,
                name=portfolio.name,
                description=portfolio.description,
                holdings=holdings_response,
                total_investment=float(portfolio.total_investment),
                average_risk_score=live_avg,
                high_risk_count=live_high_risk,
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

        # Live-fetch risk scores so analyses completed after upload are reflected
        company_ids = [str(h.company_id) for h in portfolio.holdings if h.company_id]
        live_risk_data = get_risk_scores(db, company_ids) if company_ids else {}

        holdings_response = []
        for h in portfolio.holdings:
            # Fetch real-time price data on page load
            price_data = get_real_time_price(h.symbol)

            # Calculate current value and P&L if price available
            current_price = price_data.get("current_price") if price_data else None
            current_value = (current_price * h.quantity) if current_price else None
            pnl = (current_value - float(h.investment_value)) if current_value else None
            pnl_percent = ((pnl / float(h.investment_value)) * 100) if pnl is not None else None

            # Always prefer live-queried risk data over stale stored values
            live = live_risk_data.get(str(h.company_id), {}) if h.company_id else {}
            risk_score = live.get("risk_score") or h.risk_score
            risk_level = live.get("risk_level") or h.risk_level
            flags_count = live.get("flags_count") if live.get("flags_count") is not None else h.flags_count
            latest_analysis_id = live.get("latest_analysis_id") or h.latest_analysis_id

            # Persist back if live data is newer
            if risk_score and risk_score != h.risk_score:
                h.risk_score = risk_score
                h.risk_level = risk_level
                h.flags_count = flags_count
                h.latest_analysis_id = latest_analysis_id
                db.add(h)

            holdings_response.append(HoldingResponse(
                holding_id=h.id,
                symbol=h.symbol,
                company_name=h.company_name,
                quantity=h.quantity,
                avg_price=float(h.avg_price),
                investment_value=float(h.investment_value),
                risk_score=risk_score,
                risk_level=risk_level,
                flags_count=flags_count,
                latest_analysis_id=latest_analysis_id,
                # Real-time price data (fetched on page load)
                current_price=current_price,
                current_value=current_value,
                pnl=pnl,
                pnl_percent=pnl_percent,
                price_change=price_data.get("change") if price_data else None,
                price_change_percent=price_data.get("change_percent") if price_data else None,
            ))

        # Recompute aggregate metrics from live data
        live_scores = [r.risk_score for r in holdings_response if r.risk_score is not None]
        live_avg = sum(live_scores) / len(live_scores) if live_scores else portfolio.average_risk_score
        live_high_risk = sum(1 for r in holdings_response if r.risk_score and r.risk_score >= 60)

        if live_scores:
            portfolio.average_risk_score = live_avg
            portfolio.high_risk_count = live_high_risk

        # Commit holding + portfolio aggregate updates
        try:
            db.commit()
        except Exception:
            db.rollback()

        return PortfolioResponse(
            portfolio_id=portfolio.id,
            user_id=portfolio.user_id,
            name=portfolio.name,
            description=portfolio.description,
            holdings=holdings_response,
            total_investment=float(portfolio.total_investment),
            average_risk_score=live_avg,
            high_risk_count=live_high_risk,
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


@router.post(
    "/{portfolio_id}/holdings",
    response_model=AddHoldingResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Add a single holding to portfolio",
    description="Manually add one stock holding to an existing portfolio.",
)
async def add_holding(
    portfolio_id: UUID,
    body: AddHoldingRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """Add a single holding to an existing portfolio."""
    try:
        # Verify portfolio belongs to current user
        portfolio = db.query(Portfolio).filter(
            Portfolio.id == portfolio_id,
            Portfolio.user_id == current_user.id,
        ).first()
        if not portfolio:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Portfolio not found")

        # Verify company exists
        from app.models.company import Company
        company = db.query(Company).filter(Company.id == body.company_id).first()
        if not company:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Company not found")

        # Prevent duplicate holding for same company in same portfolio
        existing = db.query(Holding).filter(
            Holding.portfolio_id == portfolio_id,
            Holding.company_id == body.company_id,
        ).first()
        if existing:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=f"{body.symbol} is already in this portfolio",
            )

        # Get existing risk score if analysis already exists
        risk_data = get_risk_scores(db, [str(company.id)])
        risk_info = risk_data.get(str(company.id), {})

        # Create holding record
        investment_value = body.quantity * body.avg_price
        holding = Holding(
            portfolio_id=portfolio_id,
            company_id=company.id,
            symbol=body.symbol.upper(),
            company_name=company.name,
            quantity=body.quantity,
            avg_price=body.avg_price,
            investment_value=investment_value,
            risk_score=risk_info.get("risk_score"),
            risk_level=risk_info.get("risk_level"),
            flags_count=risk_info.get("flags_count"),
            latest_analysis_id=risk_info.get("latest_analysis_id"),
        )
        db.add(holding)

        # Update portfolio aggregate metrics
        portfolio.total_investment = float(portfolio.total_investment) + investment_value
        all_scores = [
            h.risk_score for h in portfolio.holdings if h.risk_score is not None
        ]
        if risk_info.get("risk_score"):
            all_scores.append(risk_info["risk_score"])
        portfolio.average_risk_score = sum(all_scores) / len(all_scores) if all_scores else None
        portfolio.high_risk_count = sum(1 for s in all_scores if s >= 60)

        db.commit()
        db.refresh(holding)

        # Fetch real-time price for the new holding
        price_data = get_real_time_price(body.symbol)
        current_price = price_data.get("current_price") if price_data else None
        current_value = (current_price * body.quantity) if current_price else None
        pnl = (current_value - investment_value) if current_value else None
        pnl_percent = ((pnl / investment_value) * 100) if pnl is not None else None

        holding_response = HoldingResponse(
            holding_id=holding.id,
            symbol=holding.symbol,
            company_name=holding.company_name,
            quantity=holding.quantity,
            avg_price=float(holding.avg_price),
            investment_value=float(holding.investment_value),
            risk_score=holding.risk_score,
            risk_level=holding.risk_level,
            flags_count=holding.flags_count,
            latest_analysis_id=holding.latest_analysis_id,
            current_price=current_price,
            current_value=current_value,
            pnl=pnl,
            pnl_percent=pnl_percent,
            price_change=price_data.get("change") if price_data else None,
            price_change_percent=price_data.get("change_percent") if price_data else None,
        )

        # Auto-trigger analysis if none exists yet
        analysis_triggered = False
        if not risk_info.get("risk_score"):
            try:
                nse_symbol = map_broker_symbol(company.nse_symbol or body.symbol)
                analyze_company_by_symbol_task.delay(nse_symbol, str(current_user.id))
                analysis_triggered = True
                logger.info(f"Auto-triggered analysis for {nse_symbol} (manual holding add)")
            except Exception as e:
                logger.warning(f"Failed to trigger analysis for {body.symbol}: {e}")

        return AddHoldingResponse(holding=holding_response, analysis_triggered=analysis_triggered)

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error adding holding: {e}", exc_info=True)
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to add holding: {str(e)}",
        )


@router.delete(
    "/{portfolio_id}/holdings/{holding_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Remove a single holding from portfolio",
    description="Remove one stock holding from a portfolio without deleting the whole portfolio.",
)
async def remove_holding(
    portfolio_id: UUID,
    holding_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """Remove a single holding from a portfolio."""
    try:
        # Verify portfolio belongs to current user
        portfolio = db.query(Portfolio).filter(
            Portfolio.id == portfolio_id,
            Portfolio.user_id == current_user.id,
        ).first()
        if not portfolio:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Portfolio not found")

        # Find the specific holding
        holding = db.query(Holding).filter(
            Holding.id == holding_id,
            Holding.portfolio_id == portfolio_id,
        ).first()
        if not holding:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Holding not found")

        investment_value = float(holding.investment_value)
        db.delete(holding)
        db.flush()

        # Recompute portfolio aggregate metrics after removal
        remaining = db.query(Holding).filter(Holding.portfolio_id == portfolio_id).all()
        portfolio.total_investment = sum(float(h.investment_value) for h in remaining)
        scores = [h.risk_score for h in remaining if h.risk_score is not None]
        portfolio.average_risk_score = sum(scores) / len(scores) if scores else None
        portfolio.high_risk_count = sum(1 for s in scores if s >= 60)

        db.commit()

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error removing holding: {e}", exc_info=True)
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to remove holding: {str(e)}",
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
