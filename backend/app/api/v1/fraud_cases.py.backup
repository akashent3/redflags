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

        # Convert to response schema
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
    Match company's red flags against historical fraud patterns.

    Algorithm:
    1. Fetch company's latest analysis
    2. Get list of triggered red flags
    3. For each fraud pattern, count matching flags
    4. Calculate similarity score
    5. Return matches with similarity >= 50%
    """
    db = SessionLocal()
    try:
        # Get latest analysis
        analysis = db.query(AnalysisResult).filter(
            AnalysisResult.company_id == UUID(company_id)
        ).order_by(AnalysisResult.created_at.desc()).first()

        if not analysis:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="No analysis found for company"
            )

        # Get triggered flags
        triggered_flags = [f.flag_number for f in analysis.red_flags if f.is_triggered]

        if not triggered_flags:
            return {
                'company_id': company_id,
                'similarity_score': 0,
                'matched_patterns': [],
                'risk_assessment': 'LOW',
                'recommendation': 'No significant red flags detected. Standard due diligence recommended.',
            }

        # Match against patterns
        patterns = FRAUD_DATA.get('patterns', [])
        matches = []

        for pattern in patterns:
            common_flags = pattern.get('common_flags', [])
            if not common_flags:
                continue

            matching = set(triggered_flags) & set(common_flags)
            similarity = (len(matching) / len(common_flags)) * 100 if common_flags else 0

            if similarity >= 50:
                matches.append({
                    'pattern_name': pattern.get('pattern_name'),
                    'confidence': round(similarity, 2),
                    'matching_flags': list(matching),
                    'total_pattern_flags': len(common_flags),
                    'description': pattern.get('description'),
                    'risk_indicators': pattern.get('risk_indicators', []),
                })

        # Sort by confidence
        matches.sort(key=lambda x: x['confidence'], reverse=True)

        # Determine overall risk
        if matches:
            max_confidence = matches[0]['confidence']
            if max_confidence >= 80:
                risk_level = "CRITICAL"
            elif max_confidence >= 60:
                risk_level = "HIGH"
            else:
                risk_level = "MEDIUM"
        else:
            risk_level = "LOW"

        recommendation = _get_recommendation(risk_level, len(matches))

        return {
            'company_id': company_id,
            'similarity_score': round(max([m['confidence'] for m in matches]), 2) if matches else 0,
            'matched_patterns': matches,
            'risk_assessment': risk_level,
            'recommendation': recommendation,
            'total_triggered_flags': len(triggered_flags),
        }

    except HTTPException:
        raise
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid company ID: {str(e)}"
        )
    except Exception as e:
        logger.error(f"Error matching fraud patterns: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to match fraud patterns"
        )
    finally:
        db.close()


def _get_recommendation(risk_level: str, pattern_count: int) -> str:
    """Get recommendation based on risk level and pattern count."""
    recommendations = {
        'CRITICAL': f'⚠️ EXTREME CAUTION: {pattern_count} fraud pattern(s) strongly match this company. Multiple red flags detected that are commonly seen in major frauds. Consider avoiding this stock or conducting very thorough due diligence with professional advisors.',
        'HIGH': f'⚠️ HIGH RISK: {pattern_count} fraud pattern(s) detected with significant similarity. Several concerning red flags present. Thorough forensic analysis and expert consultation strongly recommended before investing.',
        'MEDIUM': f'⚠️ MODERATE RISK: {pattern_count} fraud pattern(s) show some similarities. Some red flags detected that warrant closer examination. Detailed review of financial statements and management practices recommended.',
        'LOW': 'Low fraud pattern similarity detected. However, standard due diligence is always recommended. Review the company\'s financial statements, management quality, and industry position carefully.',
    }
    return recommendations.get(risk_level, 'Unable to assess risk level.')


@router.get(
    "/patterns/",
    summary="Get fraud patterns",
    description="Get all known fraud patterns with their characteristics.",
)
async def get_fraud_patterns():
    """Get all fraud patterns."""
    try:
        patterns = FRAUD_DATA.get('patterns', [])
        return {
            "total": len(patterns),
            "patterns": patterns,
        }
    except Exception as e:
        logger.error(f"Error fetching fraud patterns: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to fetch fraud patterns"
        )
