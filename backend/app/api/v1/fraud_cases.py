"""Fraud cases API endpoints for pattern matching and fraud database."""

import logging
from typing import Optional
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.user import User
from app.models.fraud_case import FraudCase
from app.models.analysis_result import AnalysisResult
from app.models.company import Company
from app.utils.dependencies import get_current_active_user
from app.schemas.fraud_case import (
    FraudCaseListResponse,
    FraudCaseResponse,
    PatternMatchResponse,
    PatternMatchResult,
)

logger = logging.getLogger(__name__)
router = APIRouter()


@router.get(
    "/",
    response_model=FraudCaseListResponse,
    summary="Get all fraud cases",
    description="Get list of all historical fraud cases in the database.",
)
async def get_fraud_cases(
    skip: int = Query(0, ge=0, description="Number of records to skip"),
    limit: int = Query(50, ge=1, le=500, description="Maximum number of results"),
    fraud_type: str = Query(None, description="Filter by fraud type"),
    sector: str = Query(None, description="Filter by sector"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """Get all fraud cases from database with optional filtering."""
    try:
        query = db.query(FraudCase)

        # Apply filters
        if fraud_type:
            query = query.filter(FraudCase.fraud_type.ilike(f"%{fraud_type}%"))
        if sector:
            query = query.filter(FraudCase.sector.ilike(f"%{sector}%"))

        # Get total count
        total = query.count()

        # Get paginated results
        fraud_cases = query.order_by(FraudCase.year.desc()).offset(skip).limit(limit).all()

        # Convert to response schema — include all JSONB fields needed by Learn page
        case_responses = [
            FraudCaseResponse(
                id=case.id,
                case_id=case.case_id,
                company_name=case.company_name,
                year=case.year,
                sector=case.sector,
                industry=case.industry,
                fraud_type=case.fraud_type,
                detection_difficulty=case.detection_difficulty,
                stock_decline_percent=float(case.stock_decline_percent) if case.stock_decline_percent else None,
                market_cap_lost_cr=float(case.market_cap_lost_cr) if case.market_cap_lost_cr else None,
                primary_flags=case.primary_flags,
                red_flags_detected=case.red_flags_detected,
                timeline=case.timeline,
                what_investors_missed=case.what_investors_missed,
                lessons_learned=case.lessons_learned,
                outcome=case.outcome,
                regulatory_action=case.regulatory_action,
                created_at=case.created_at,
            )
            for case in fraud_cases
        ]

        return FraudCaseListResponse(
            total=total,
            cases=case_responses
        )

    except Exception as e:
        logger.error(f"Error fetching fraud cases: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to fetch fraud cases: {str(e)}"
        )


@router.get(
    "/{case_id}",
    response_model=FraudCaseResponse,
    summary="Get fraud case details",
    description="Get detailed information about a specific fraud case.",
)
async def get_fraud_case(
    case_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """Get fraud case details by case_id."""
    try:
        fraud_case = db.query(FraudCase).filter(FraudCase.case_id == case_id).first()

        if not fraud_case:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Fraud case not found: {case_id}"
            )

        return FraudCaseResponse(
            id=fraud_case.id,
            case_id=fraud_case.case_id,
            company_name=fraud_case.company_name,
            year=fraud_case.year,
            sector=fraud_case.sector,
            industry=fraud_case.industry,
            fraud_type=fraud_case.fraud_type,
            detection_difficulty=fraud_case.detection_difficulty,
            stock_decline_percent=float(fraud_case.stock_decline_percent) if fraud_case.stock_decline_percent else None,
            market_cap_lost_cr=float(fraud_case.market_cap_lost_cr) if fraud_case.market_cap_lost_cr else None,
            primary_flags=fraud_case.primary_flags,
            red_flags_detected=fraud_case.red_flags_detected,
            timeline=fraud_case.timeline,
            what_investors_missed=fraud_case.what_investors_missed,
            lessons_learned=fraud_case.lessons_learned,
            outcome=fraud_case.outcome,
            regulatory_action=fraud_case.regulatory_action,
            created_at=fraud_case.created_at,
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error fetching fraud case {case_id}: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to fetch fraud case: {str(e)}"
        )


@router.post(
    "/pattern-match/{analysis_id}",
    response_model=PatternMatchResponse,
    summary="Pattern match analysis against fraud cases",
    description="Analyze similarity between company's red flags and historical fraud cases.",
)
async def pattern_match_analysis(
    analysis_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """
    Pattern match analysis against historical fraud cases using Jaccard similarity.

    **Algorithm:**
    - Uses Jaccard similarity: (intersection / union) * 100
    - Threshold: 30% minimum for matches
    - Risk levels: <30% = LOW, 30-50% = MEDIUM, 50-70% = HIGH, >70% = CRITICAL
    """
    try:
        # Step 1: Get analysis
        analysis = db.query(AnalysisResult).filter(
            AnalysisResult.id == analysis_id
        ).first()

        if not analysis:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Analysis not found: {analysis_id}"
            )

        # Get company info via AnnualReport (AnalysisResult has no direct company_id)
        from app.models.annual_report import AnnualReport
        from app.models.red_flag import RedFlag
        annual_report = db.query(AnnualReport).filter(AnnualReport.id == analysis.report_id).first()
        company = db.query(Company).filter(Company.id == annual_report.company_id).first() if annual_report else None
        if not company:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Company not found for analysis: {analysis_id}"
            )

        # Step 2: Get triggered flags from analysis (red_flags relationship is commented out — query directly)
        triggered_flags = {
            flag.flag_number
            for flag in db.query(RedFlag).filter(
                RedFlag.analysis_id == analysis.id,
                RedFlag.is_triggered == True
            ).all()
        }

        if not triggered_flags:
            return PatternMatchResponse(
                analysis_id=analysis.id,
                company_id=company.id,
                company_name=company.name,
                risk_level="LOW",
                message="No red flags triggered. No fraud pattern similarity detected.",
                total_matches=0,
                triggered_flags_count=0,
                matches=[]
            )

        # Step 3: Load all fraud cases
        fraud_cases = db.query(FraudCase).all()

        if not fraud_cases:
            return PatternMatchResponse(
                analysis_id=analysis.id,
                company_id=company.id,
                company_name=company.name,
                risk_level="LOW",
                message="No historical fraud cases in database for comparison.",
                total_matches=0,
                triggered_flags_count=len(triggered_flags),
                matches=[]
            )

        # Step 4: Calculate similarity scores
        matches = []
        for case in fraud_cases:
            # Get fraud case flag numbers
            case_flags = set(case.triggered_flag_numbers)

            if not case_flags:
                continue

            # Calculate Jaccard similarity
            intersection = triggered_flags & case_flags
            union = triggered_flags | case_flags

            if not union:
                continue

            similarity = (len(intersection) / len(union)) * 100

            # Only include matches above 30% threshold
            if similarity >= 30:
                # Get matching flag details
                matching_flags = []
                for flag_data in case.red_flags_detected:
                    if flag_data.get('flag_number') in intersection:
                        matching_flags.append({
                            'flag_number': flag_data.get('flag_number'),
                            'flag_name': flag_data.get('flag_name'),
                            'category': flag_data.get('category'),
                            'severity': flag_data.get('severity'),
                            'when_visible': flag_data.get('when_visible', 'During fraud period')
                        })

                matches.append(PatternMatchResult(
                    case_id=case.case_id,
                    company_name=case.company_name,
                    year=case.year,
                    similarity_score=round(similarity, 2),
                    matching_flags=matching_flags,
                    stock_decline_percent=float(case.stock_decline_percent) if case.stock_decline_percent else None,
                    outcome=case.outcome,
                    lessons=case.lessons_learned
                ))

        # Step 5: Sort by similarity (highest first)
        matches.sort(key=lambda x: x.similarity_score, reverse=True)

        # Step 6: Generate risk assessment
        if matches:
            max_similarity = matches[0].similarity_score

            if max_similarity >= 70:
                risk_level = "CRITICAL"
                message = (
                    f"⚠️ EXTREME CAUTION: Strong similarity ({max_similarity:.1f}%) "
                    f"with {matches[0].company_name} fraud case. Immediate review recommended."
                )
            elif max_similarity >= 50:
                risk_level = "HIGH"
                message = (
                    f"⚠️ HIGH RISK: Significant similarity ({max_similarity:.1f}%) "
                    f"with historical fraud patterns. Detailed investigation recommended."
                )
            elif max_similarity >= 30:
                risk_level = "MEDIUM"
                message = (
                    f"⚠️ MODERATE RISK: Some similarities ({max_similarity:.1f}%) "
                    f"with fraud patterns detected. Enhanced due diligence advised."
                )
            else:
                risk_level = "LOW"
                message = "Low fraud pattern similarity. Standard due diligence recommended."
        else:
            risk_level = "LOW"
            message = (
                f"No significant fraud pattern matches found (threshold: 30%). "
                f"{len(triggered_flags)} red flags detected but pattern differs from known fraud cases."
            )

        return PatternMatchResponse(
            analysis_id=analysis.id,
            company_id=company.id,
            company_name=company.name,
            risk_level=risk_level,
            message=message,
            total_matches=len(matches),
            triggered_flags_count=len(triggered_flags),
            matches=matches[:5]  # Return top 5 matches
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error in pattern matching: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to perform pattern matching: {str(e)}"
        )
