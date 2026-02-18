"""Company search and management endpoints."""

import logging
from typing import Optional
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.user import User
from app.utils.dependencies import get_current_active_user
from app.schemas.company import (
    CompanyDetailResponse,
    CompanyResponse,
    CompanySearchResponse,
    CompanySearchResult,
)
from app.schemas.reports import ReportListResponse, ReportResponse
from app.services.company_service import company_service
from app.services.finedge_client import finedge_client

logger = logging.getLogger(__name__)

router = APIRouter()


@router.get(
    "/search",
    response_model=CompanySearchResponse,
    summary="Search companies by name or code",
    description="Search for companies by name, NSE symbol, or BSE code. Returns up to 100 results.",
)
async def search_companies(
    q: str = Query(..., min_length=1, max_length=100, description="Search query (name, NSE symbol, or BSE code)"),
    limit: int = Query(20, ge=1, le=100, description="Maximum number of results"),
    nifty_500_only: bool = Query(False, description="Filter to only NIFTY 500 companies"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """
    Search for companies by name, NSE symbol, or BSE code.

    **Query Parameters:**
    - `q`: Search query (minimum 1 character)
    - `limit`: Maximum number of results (1-100, default 20)
    - `nifty_500_only`: Filter to only NIFTY 500 companies (default false)

    **Returns:**
    - List of matching companies with basic information
    - Ordered by: NIFTY 50 > NIFTY 500 > Alphabetically

    **Examples:**
    - `/api/v1/companies/search?q=reliance`
    - `/api/v1/companies/search?q=TCS&nifty_500_only=true`
    - `/api/v1/companies/search?q=500325` (BSE code)
    """
    try:
        companies, total = company_service.search_companies(
            db=db,
            query=q,
            limit=limit,
            nifty_500_only=nifty_500_only
        )

        # Convert to response schema
        results = [
            CompanySearchResult(
                id=company.id,
                name=company.name,
                display_code=company.display_code,
                industry=company.industry,
                sector=company.sector,
                is_nifty_50=company.is_nifty_50,
                is_nifty_500=company.is_nifty_500,
                market_cap_cr=float(company.market_cap_cr) if company.market_cap_cr else None
            )
            for company in companies
        ]

        return CompanySearchResponse(
            total=total,
            results=results
        )

    except Exception as e:
        logger.error(f"Error searching companies: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to search companies: {str(e)}"
        )


@router.get(
    "/{company_id}",
    response_model=CompanyDetailResponse,
    summary="Get company details",
    description="Get detailed information about a specific company including report statistics.",
)
async def get_company(
    company_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """
    Get detailed information about a specific company.

    **Path Parameters:**
    - `company_id`: Company UUID

    **Returns:**
    - Company details including:
      - Basic information (name, codes, industry, sector)
      - Market data
      - NIFTY index membership
      - Report statistics (total reports, latest/earliest years)

    **Errors:**
    - 404: Company not found
    """
    try:
        # Get company
        company = company_service.get_company_by_id(db, company_id)
        if not company:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Company not found: {company_id}"
            )

        # Get report statistics
        stats = company_service.get_company_report_stats(db, company_id)

        # Build response
        return CompanyDetailResponse(
            id=company.id,
            name=company.name,
            bse_code=company.bse_code,
            nse_symbol=company.nse_symbol,
            isin=company.isin,
            industry=company.industry,
            sector=company.sector,
            market_cap_cr=float(company.market_cap_cr) if company.market_cap_cr else None,
            is_nifty_50=company.is_nifty_50,
            is_nifty_500=company.is_nifty_500,
            is_active=company.is_active,
            display_code=company.display_code,
            is_nifty=company.is_nifty,
            created_at=company.created_at,
            updated_at=company.updated_at,
            total_reports=stats['total_reports'],
            latest_report_year=stats['latest_report_year'],
            earliest_report_year=stats['earliest_report_year']
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting company {company_id}: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get company details: {str(e)}"
        )


@router.get(
    "/{company_id}/reports",
    response_model=ReportListResponse,
    summary="Get company's annual reports",
    description="Get list of annual reports for a specific company.",
)
async def get_company_reports(
    company_id: UUID,
    skip: int = Query(0, ge=0, description="Number of records to skip"),
    limit: int = Query(20, ge=1, le=100, description="Maximum number of results"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """
    Get list of annual reports for a specific company.

    **Path Parameters:**
    - `company_id`: Company UUID

    **Query Parameters:**
    - `skip`: Number of records to skip (pagination, default 0)
    - `limit`: Maximum number of results (1-100, default 20)

    **Returns:**
    - List of annual reports ordered by fiscal year (newest first)
    - Each report includes:
      - PDF URL
      - Fiscal year
      - Processing status
      - File size and page count
      - Timestamps

    **Errors:**
    - 404: Company not found
    """
    try:
        # Verify company exists
        company = company_service.get_company_by_id(db, company_id)
        if not company:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Company not found: {company_id}"
            )

        # Get reports
        reports, total = company_service.get_company_reports(
            db=db,
            company_id=company_id,
            skip=skip,
            limit=limit
        )

        # Convert to response schema
        report_responses = [
            ReportResponse(
                id=report.id,
                company_id=report.company_id,
                fiscal_year=report.fiscal_year,
                fiscal_year_display=report.fiscal_year_display,
                pdf_url=report.pdf_url,
                file_size_mb=report.file_size_mb,
                pages_count=report.pages_count,
                is_processed=report.is_processed,
                uploaded_at=report.uploaded_at,
                processed_at=report.processed_at
            )
            for report in reports
        ]

        return ReportListResponse(
            total=total,
            skip=skip,
            limit=limit,
            reports=report_responses
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting reports for company {company_id}: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get company reports: {str(e)}"
        )


@router.get(
    "/{company_id}/latest-analysis",
    summary="Get latest analysis for company",
    description="Get the latest analysis result for a company if it exists.",
)
async def get_latest_analysis(
    company_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """
    Get latest analysis for a company.

    **Path Parameters:**
    - `company_id`: Company UUID

    **Returns:**
    - If analysis exists: { analysis_id, risk_score, risk_level, created_at }
    - If no analysis: { analysis_id: null }

    **Use Case:**
    - Watchlist: Check if analysis exists before redirecting or triggering new analysis
    - Portfolio: Check if risk scores are available
    """
    try:
        from app.models.analysis_result import AnalysisResult

        # Verify company exists
        company = company_service.get_company_by_id(db, company_id)
        if not company:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Company not found: {company_id}"
            )

        # Get latest analysis — join via AnnualReport (AnalysisResult has no direct company_id)
        from app.models.annual_report import AnnualReport
        latest_analysis = db.query(AnalysisResult).join(
            AnnualReport, AnalysisResult.report_id == AnnualReport.id
        ).filter(
            AnnualReport.company_id == company_id
        ).order_by(AnalysisResult.created_at.desc()).first()

        if latest_analysis:
            annual_report = db.query(AnnualReport).filter(AnnualReport.id == latest_analysis.report_id).first()
            return {
                "analysis_id": latest_analysis.id,
                "risk_score": latest_analysis.risk_score,
                "risk_level": latest_analysis.risk_level,
                "created_at": latest_analysis.created_at,
                "fiscal_year": annual_report.fiscal_year if annual_report else None,
            }
        else:
            return {
                "analysis_id": None,
                "message": "No analysis available for this company"
            }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting latest analysis for company {company_id}: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get latest analysis: {str(e)}"
        )


@router.post(
    "/ensure-by-symbol",
    summary="Ensure company exists in DB by symbol",
    description="Look up or create a company record by NSE symbol. Used when adding from FinEdge search.",
)
async def ensure_company_by_symbol(
    body: dict,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """
    Given a symbol from FinEdge search, ensure the company exists in local DB.

    - If company already in DB → return existing UUID immediately
    - If not in DB → create minimal record from provided FinEdge data → return new UUID

    Frontend calls this before POST /watchlist/ or POST /portfolio/{id}/holdings
    so those endpoints always receive a valid company_id UUID.
    """
    from app.models.company import Company as CompanyModel

    symbol = (body.get("symbol") or "").strip().upper()
    if not symbol:
        raise HTTPException(status_code=400, detail="symbol is required")

    name     = body.get("name") or symbol
    sector   = body.get("sector") or None
    industry = body.get("industry") or None

    # Check existing by nse_symbol or bse_code
    company = db.query(CompanyModel).filter(
        (CompanyModel.nse_symbol == symbol) | (CompanyModel.bse_code == symbol)
    ).first()

    created = False
    if not company:
        # Try to enrich from FinEdge profile (best-effort — never fail because of this)
        try:
            profile = finedge_client.get_company_profile(symbol)
            name     = profile.get("name") or name
            sector   = profile.get("sector") or sector
            industry = profile.get("industry") or industry
        except Exception:
            pass  # Use whatever the frontend passed

        company = CompanyModel(
            name=name,
            nse_symbol=symbol,
            sector=sector,
            industry=industry,
            is_active=True,
        )
        db.add(company)
        db.commit()
        db.refresh(company)
        created = True
        logger.info(f"Created new company record for {symbol}: {company.id}")
    else:
        logger.info(f"Found existing company record for {symbol}: {company.id}")

    return {
        "company_id": str(company.id),
        "symbol": company.nse_symbol or company.bse_code or symbol,
        "name": company.name,
        "sector": company.sector,
        "industry": company.industry,
        "created": created,
    }


@router.get(
    "/finedge/search",
    summary="Search companies via FinEdge API",
    description="Live search for companies using FinEdge API. Returns NSE/BSE listed companies.",
)
async def search_companies_finedge(
    q: str = Query(None, min_length=1, max_length=100, description="Search query (name or symbol)"),
    limit: int = Query(50, ge=1, le=500, description="Maximum number of results"),
    current_user: User = Depends(get_current_active_user),
):
    """
    Search for companies using FinEdge API (live data from NSE/BSE).

    This endpoint fetches fresh data from FinEdge API which includes all NSE/BSE listed companies.
    Use this for the company search dropdown to get real-time company data.

    **Query Parameters:**
    - `q`: Search query (optional - if not provided, returns all symbols up to limit)
    - `limit`: Maximum number of results (1-500, default 50)

    **Returns:**
    - List of companies with symbol, name, exchange info

    **Examples:**
    - `/api/v1/companies/finedge/search?q=reliance`
    - `/api/v1/companies/finedge/search?q=TCS`
    - `/api/v1/companies/finedge/search?limit=100` (all companies)
    """
    try:
        all_symbols = finedge_client.get_all_symbols()

        # Filter if search query provided
        if q:
            query_lower = q.lower()
            filtered = [
                s for s in all_symbols
                if query_lower in s.get("name", "").lower() or
                   query_lower in s.get("symbol", "").lower() or
                   query_lower in s.get("nse_code", "").lower() or
                   query_lower in s.get("bse_code", "").lower()
            ]
        else:
            filtered = all_symbols

        # Limit results
        results = filtered[:limit]

        # Format response
        formatted_results = [
            {
                "symbol": s.get("symbol", ""),
                "name": s.get("name", ""),
                "nse_code": s.get("nse_code", ""),
                "bse_code": s.get("bse_code", ""),
                "exchange": s.get("exchange", ""),
                "isin": s.get("isin", ""),
            }
            for s in results
        ]

        return {
            "total": len(filtered),
            "returned": len(formatted_results),
            "results": formatted_results
        }

    except Exception as e:
        logger.error(f"Error searching companies via FinEdge: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to search companies via FinEdge API: {str(e)}"
        )


@router.get(
    "/finedge/profile/{symbol}",
    summary="Get company profile from FinEdge",
    description="Get detailed company profile from FinEdge API.",
)
async def get_company_profile_finedge(
    symbol: str,
    current_user: User = Depends(get_current_active_user),
):
    """
    Get company profile from FinEdge API.

    **Path Parameters:**
    - `symbol`: NSE symbol (e.g., "RELIANCE", "TCS")

    **Returns:**
    - Company profile including sector, industry, market cap, etc.
    """
    try:
        profile = finedge_client.get_company_profile(symbol)
        return profile

    except Exception as e:
        logger.error(f"Error fetching company profile from FinEdge: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Company profile not found for symbol: {symbol}"
        )
