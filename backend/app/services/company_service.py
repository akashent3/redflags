"""Business logic for company operations."""

import logging
from typing import Optional
from uuid import UUID

from sqlalchemy import func, or_
from sqlalchemy.orm import Session

from app.models.annual_report import AnnualReport
from app.models.company import Company

logger = logging.getLogger(__name__)


class CompanyService:
    """Service for company-related operations."""

    def search_companies(
        self,
        db: Session,
        query: str,
        limit: int = 20,
        nifty_500_only: bool = False
    ) -> tuple[list[Company], int]:
        """
        Search companies by name, NSE symbol, or BSE code.

        Args:
            db: Database session
            query: Search query string
            limit: Maximum number of results (default 20, max 100)
            nifty_500_only: Filter to only NIFTY 500 companies

        Returns:
            Tuple of (list of companies, total count)
        """
        # Sanitize query
        query = query.strip()

        if not query:
            # Return empty results for empty query
            return [], 0

        # Build base query
        db_query = db.query(Company).filter(Company.is_active == True)

        # Add NIFTY 500 filter if requested
        if nifty_500_only:
            db_query = db_query.filter(Company.is_nifty_500 == True)

        # Search by name, NSE symbol, or BSE code (case-insensitive)
        search_filter = or_(
            Company.name.ilike(f"%{query}%"),
            Company.nse_symbol.ilike(f"{query}%"),
            Company.bse_code.ilike(f"{query}%")
        )
        db_query = db_query.filter(search_filter)

        # Get total count
        total = db_query.count()

        # Order by relevance:
        # 1. Exact matches first
        # 2. NIFTY 50 companies
        # 3. NIFTY 500 companies
        # 4. Alphabetically by name
        db_query = db_query.order_by(
            Company.is_nifty_50.desc(),
            Company.is_nifty_500.desc(),
            Company.name.asc()
        )

        # Apply limit
        limit = min(limit, 100)  # Cap at 100 results
        companies = db_query.limit(limit).all()

        logger.info(f"Company search for '{query}': {len(companies)} results out of {total} total")

        return companies, total

    def get_company_by_id(self, db: Session, company_id: UUID) -> Optional[Company]:
        """
        Get company by ID.

        Args:
            db: Database session
            company_id: Company UUID

        Returns:
            Company object or None if not found
        """
        company = db.query(Company).filter(
            Company.id == company_id,
            Company.is_active == True
        ).first()

        if not company:
            logger.warning(f"Company not found: {company_id}")
            return None

        return company

    def get_company_reports(
        self,
        db: Session,
        company_id: UUID,
        skip: int = 0,
        limit: int = 20
    ) -> tuple[list[AnnualReport], int]:
        """
        Get annual reports for a company.

        Args:
            db: Database session
            company_id: Company UUID
            skip: Number of records to skip (pagination)
            limit: Maximum number of results

        Returns:
            Tuple of (list of reports, total count)
        """
        # Verify company exists
        company = self.get_company_by_id(db, company_id)
        if not company:
            return [], 0

        # Query reports for this company
        query = db.query(AnnualReport).filter(
            AnnualReport.company_id == company_id
        )

        # Get total count
        total = query.count()

        # Order by fiscal year descending (newest first)
        reports = query.order_by(
            AnnualReport.fiscal_year.desc()
        ).offset(skip).limit(limit).all()

        logger.info(f"Retrieved {len(reports)} reports for company {company_id} (total: {total})")

        return reports, total

    def get_company_report_stats(self, db: Session, company_id: UUID) -> dict:
        """
        Get statistics about company's annual reports.

        Args:
            db: Database session
            company_id: Company UUID

        Returns:
            Dictionary with report statistics
        """
        # Query report statistics
        stats = db.query(
            func.count(AnnualReport.id).label('total_reports'),
            func.max(AnnualReport.fiscal_year).label('latest_year'),
            func.min(AnnualReport.fiscal_year).label('earliest_year')
        ).filter(
            AnnualReport.company_id == company_id
        ).first()

        return {
            'total_reports': stats.total_reports or 0,
            'latest_report_year': stats.latest_year,
            'earliest_report_year': stats.earliest_year
        }


# Singleton instance
company_service = CompanyService()
