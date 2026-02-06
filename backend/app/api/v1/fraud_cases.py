"""Fraud cases API endpoints."""

import json
import logging
from pathlib import Path
from typing import List, Optional
from uuid import UUID

from fastapi import APIRouter, HTTPException, Query, status

from app.database import SessionLocal
from app.models.analysis_result import AnalysisResult

logger = logging.getLogger(__name__)
router = APIRouter()

# Load fraud cases from JSON file
FRAUD_CASES_FILE = Path(__file__).parent.parent.parent / "data" / "fraud_cases.json"


def load_fraud_cases():
    """Load fraud cases from JSON file."""
    try:
        with open(FRAUD_CASES_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception as e:
        logger.error(f"Failed to load fraud cases: {e}")
        return {"cases": [], "patterns": []}


FRAUD_DATA = load_fraud_cases()


@router.get(
    "/",
    summary="Get fraud cases",
    description="Get fraud cases with optional filtering and pagination.",
)
async def get_fraud_cases(
    sector: Optional[str] = Query(None, description="Filter by sector"),
    search: Optional[str] = Query(None, description="Search in company name or industry"),
    skip: int = Query(0, ge=0, description="Number of records to skip"),
    limit: int = Query(20, ge=1, le=100, description="Maximum number of records"),
):
    """Get fraud cases with filtering."""
    try:
        cases = FRAUD_DATA.get('cases', [])

        # Apply filters
        if sector:
            cases = [c for c in cases if c.get('sector', '').lower() == sector.lower()]

        if search:
            search_lower = search.lower()
            cases = [
                c for c in cases
                if search_lower in c.get('company_name', '').lower() or
                search_lower in c.get('industry', '').lower()
            ]

        # Pagination
        total = len(cases)
        cases = cases[skip:skip + limit]

        return {
            "total": total,
            "skip": skip,
            "limit": limit,
            "cases": cases,
        }

    except Exception as e:
        logger.error(f"Error fetching fraud cases: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to fetch fraud cases"
        )


@router.get(
    "/{case_id}",
    summary="Get fraud case details",
    description="Get detailed information about a specific fraud case.",
)
async def get_fraud_case_detail(case_id: str):
    """Get detailed fraud case."""
    try:
        cases = FRAUD_DATA.get('cases', [])
        case = next((c for c in cases if c.get('case_id') == case_id), None)

        if not case:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Fraud case not found: {case_id}"
            )

        return case

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error fetching fraud case detail: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to fetch fraud case details"
        )


@router.post(
    "/pattern-match",
    summary="Match fraud patterns",
    description="Match company's red flags against historical fraud patterns.",
)
async def match_fraud_patterns(company_id: str):
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
