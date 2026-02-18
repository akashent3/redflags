"""Simplified Analysis Service using FinEdge API + Gemini approach (mini_app logic).

This replaces the complex PDF pipeline with a faster, simpler approach:
1. Fetch numerical data from FinEdge API (21 flags)
2. Analyze PDF with single Gemini call (23 flags for non-banks, 25 for banks)
3. Combine flags and calculate risk score
4. Save to database
"""

import logging
from typing import Dict, List, Optional
from uuid import UUID
import os

from sqlalchemy.orm import Session

from app.models.analysis_result import AnalysisResult
from app.models.annual_report import AnnualReport
from app.models.red_flag import RedFlag as RedFlagModel
from app.services.finedge_client import finedge_client
from app.services.api_flags import calculate_api_flags
from app.services.gemini_analyzer import analyze_pdf_with_gemini, parse_gemini_flags
from app.config import settings

logger = logging.getLogger(__name__)

# Category weights for risk scoring
CATEGORY_WEIGHTS = {
    "Auditor": 18,
    "Cash Flow": 18,
    "Related Party": 14,
    "Promoter": 15,
    "Governance": 12,
    "Balance Sheet": 13,
    "Revenue": 5,
    "Textual": 5,
}

# Severity points
SEVERITY_POINTS = {
    "CRITICAL": 25,
    "HIGH": 15,
    "MEDIUM": 8,
    "LOW": 3,
}


class AnalysisServiceV2:
    """Simplified analysis service using mini_app logic."""

    def analyze_report(
        self,
        db: Session,
        report_id: UUID,
        pdf_path: str = None,
        pdf_bytes: bytes = None,
        company_symbol: str = None,
        company_name: str = "",
        fiscal_year: str = "",
    ) -> AnalysisResult:
        """
        Run complete analysis using FinEdge API + Gemini.

        Args:
            db: Database session
            report_id: UUID of the AnnualReport record
            pdf_path: Path to PDF file (for Gemini)
            pdf_bytes: PDF bytes (alternative to path)
            company_symbol: NSE/BSE symbol for FinEdge API
            company_name: Company name
            fiscal_year: Fiscal year

        Returns:
            AnalysisResult object with complete analysis
        """
        logger.info(f"Starting simplified analysis for report {report_id}, symbol={company_symbol}")

        try:
            all_flags = []
            is_financial_sector = False

            # Step 1: Fetch API-based flags from FinEdge (if symbol provided)
            if company_symbol:
                logger.info(f"Step 1/3: Fetching financial data from FinEdge API for {company_symbol}")
                try:
                    # First fetch profile only to determine sector (needed to pick correct statement type)
                    try:
                        profile_data = finedge_client.get_company_profile(company_symbol)
                    except Exception:
                        profile_data = {}

                    industry = profile_data.get("industry", "").lower()
                    sector = profile_data.get("sector", "").lower()
                    is_financial_sector = any(
                        term in industry or term in sector
                        for term in ["bank", "nbfc", "financial services", "finance"]
                    )

                    logger.info(
                        f"Company sector: '{sector}', industry: '{industry}', "
                        f"is_financial_sector: {is_financial_sector}"
                    )

                    # Fetch all financials — banks always get standalone, others auto-detect
                    finedge_data = finedge_client.fetch_all_data(
                        company_symbol,
                        is_financial_sector=is_financial_sector
                    )
                    finedge_data["profile"] = profile_data  # reuse the already-fetched profile

                    # Log statement type used
                    statement_type = finedge_data.get("statement_type", "unknown")
                    logger.info(
                        f"Statement type used for {company_symbol}: {statement_type}"
                    )

                    # Calculate API flags
                    api_flags = calculate_api_flags(finedge_data, is_financial_sector)
                    all_flags.extend(api_flags)

                    logger.info(
                        f"FinEdge API analysis complete: {len(api_flags)} flags, "
                        f"{sum(1 for f in api_flags if f.get('triggered'))} triggered"
                    )
                except Exception as e:
                    logger.error(f"FinEdge API analysis failed: {e}", exc_info=True)
                    logger.warning("Continuing with PDF-only analysis")

            # Step 2: Analyze PDF with Gemini (if PDF provided)
            gemini_flags = []
            if pdf_path or pdf_bytes:
                logger.info("Step 2/3: Analyzing PDF with Gemini")

                # Save bytes to temp file if needed
                temp_pdf_path = None
                if pdf_bytes and not pdf_path:
                    import tempfile
                    temp_fd, temp_pdf_path = tempfile.mkstemp(suffix=".pdf")
                    os.write(temp_fd, pdf_bytes)
                    os.close(temp_fd)
                    pdf_path = temp_pdf_path

                try:
                    gemini_result = analyze_pdf_with_gemini(
                        pdf_path=pdf_path,
                        api_key=settings.gemini_api_key,
                        is_financial_sector=is_financial_sector,
                    )

                    gemini_flags = parse_gemini_flags(gemini_result)
                    all_flags.extend(gemini_flags)

                    logger.info(
                        f"Gemini PDF analysis complete: {len(gemini_flags)} flags, "
                        f"{sum(1 for f in gemini_flags if f.get('triggered'))} triggered"
                    )
                except Exception as e:
                    logger.error(f"Gemini PDF analysis failed: {e}", exc_info=True)
                    logger.warning("Continuing without PDF analysis")
                finally:
                    # Clean up temp file
                    if temp_pdf_path and os.path.exists(temp_pdf_path):
                        os.remove(temp_pdf_path)

            if not all_flags:
                raise Exception("Analysis produced no flags - both API and PDF analysis failed")

            logger.info(f"Total flags: {len(all_flags)}, triggered: {sum(1 for f in all_flags if f.get('triggered'))}")

            # Step 3: Calculate risk score
            logger.info("Step 3/3: Calculating risk score")
            risk_data = self._calculate_risk_score(all_flags)

            logger.info(
                f"Risk Score: {risk_data['overall_score']} ({risk_data['risk_level']}), "
                f"Flags Triggered: {risk_data['summary']['total_triggered']}/{len(all_flags)}"
            )

            # Step 4: Save to database
            logger.info("Saving results to database")
            analysis_result = self._save_results(
                db=db,
                report_id=report_id,
                risk_data=risk_data,
                all_flags=all_flags,
            )

            logger.info(f"Analysis complete. Result ID: {analysis_result.id}")
            return analysis_result

        except Exception as e:
            logger.error(f"Analysis failed for report {report_id}: {e}", exc_info=True)
            raise

    def _calculate_risk_score(self, all_flags: List[Dict]) -> Dict:
        """Calculate weighted risk score from all flag results."""
        # Group flags by category
        category_flags = {}
        for flag in all_flags:
            cat = flag.get("category", "Unknown")
            if cat not in category_flags:
                category_flags[cat] = []
            category_flags[cat].append(flag)

        # Calculate category scores
        category_scores = {}
        total_weighted_score = 0

        for cat, weight in CATEGORY_WEIGHTS.items():
            flags_in_cat = category_flags.get(cat, [])
            triggered_flags = [f for f in flags_in_cat if f.get("triggered", False)]

            # Calculate raw points for this category
            raw_points = 0
            max_possible = 0
            for f in flags_in_cat:
                severity = f.get("severity", "MEDIUM")
                points = SEVERITY_POINTS.get(severity, 8)
                max_possible += points
                if f.get("triggered", False):
                    confidence = f.get("confidence", 50) / 100
                    raw_points += points * confidence

            # Normalize to 0-100 for this category
            cat_score = (raw_points / max_possible * 100) if max_possible > 0 else 0
            cat_score = min(cat_score, 100)

            category_scores[cat] = {
                "score": round(cat_score, 1),
                "weight": weight,
                "triggered_count": len(triggered_flags),
                "total_flags": len(flags_in_cat),
                "weighted_contribution": round(cat_score * weight / 100, 1),
            }

            total_weighted_score += cat_score * weight / 100

        # Overall risk score (0-100)
        overall_score = int(round(min(total_weighted_score, 100)))

        # Determine risk level
        if overall_score >= 60:
            risk_level = "CRITICAL"
            risk_color = "#dc2626"
            risk_description = "Very high risk - multiple serious red flags detected"
        elif overall_score >= 40:
            risk_level = "HIGH"
            risk_color = "#ea580c"
            risk_description = "High risk - several concerning red flags detected"
        elif overall_score >= 20:
            risk_level = "MEDIUM"
            risk_color = "#ca8a04"
            risk_description = "Moderate risk - some red flags need attention"
        elif overall_score >= 5:
            risk_level = "LOW"
            risk_color = "#16a34a"
            risk_description = "Low risk - minor concerns only"
        else:
            risk_level = "CLEAN"
            risk_color = "#059669"
            risk_description = "Very low risk - no significant red flags"

        # Summary stats
        triggered_total = sum(1 for f in all_flags if f.get("triggered", False))
        critical_flags = [f for f in all_flags if f.get("triggered") and f.get("severity") == "CRITICAL"]
        high_flags = [f for f in all_flags if f.get("triggered") and f.get("severity") == "HIGH"]

        return {
            "overall_score": overall_score,
            "risk_level": risk_level,
            "risk_color": risk_color,
            "risk_description": risk_description,
            "category_scores": category_scores,
            "summary": {
                "total_flags_checked": len(all_flags),
                "total_triggered": triggered_total,
                "critical_flags": len(critical_flags),
                "high_flags": len(high_flags),
                "critical_flag_names": [f["flag_name"] for f in critical_flags],
                "high_flag_names": [f["flag_name"] for f in high_flags],
            },
        }

    def _save_results(
        self,
        db: Session,
        report_id: UUID,
        risk_data: Dict,
        all_flags: List[Dict],
    ) -> AnalysisResult:
        """Save analysis results to database."""
        try:
            # Convert category_scores dict to DB format
            category_scores_db = {
                cat: details["score"] for cat, details in risk_data["category_scores"].items()
            }

            # Create AnalysisResult record
            analysis = AnalysisResult(
                report_id=report_id,
                risk_score=risk_data["overall_score"],
                risk_level=risk_data["risk_level"],
                category_scores=category_scores_db,
                flags_triggered_count=risk_data["summary"]["total_triggered"],
                flags_critical_count=risk_data["summary"]["critical_flags"],
                flags_high_count=risk_data["summary"]["high_flags"],
                flags_medium_count=sum(1 for f in all_flags if f.get("triggered") and f.get("severity") == "MEDIUM"),
                flags_low_count=sum(1 for f in all_flags if f.get("triggered") and f.get("severity") == "LOW"),
                summary_text=risk_data["risk_description"],
                key_concerns=risk_data["summary"]["critical_flag_names"] + risk_data["summary"]["high_flag_names"],
                failed_checks_count=0,
                failed_checks_details=None,
            )

            db.add(analysis)
            db.flush()  # Get analysis.id

            logger.info(f"Created AnalysisResult: {analysis.id}")

            # Create RedFlag records for each flag result
            for flag in all_flags:
                # Normalize category to uppercase to match database ENUM
                category = flag.get("category", "Unknown").upper().replace(" ", "_")

                red_flag = RedFlagModel(
                    analysis_id=analysis.id,
                    flag_number=flag.get("flag_number", 0),
                    flag_name=flag.get("flag_name", "Unknown"),
                    flag_description=flag.get("rule", ""),
                    category=category,
                    severity=flag.get("severity", "MEDIUM"),
                    is_triggered=flag.get("triggered", False),
                    confidence_score=flag.get("confidence", 0),
                    evidence_text=flag.get("evidence", ""),
                    page_references=[],
                    extracted_data=flag.get("data", {}),
                    detection_method=flag.get("source", "unknown"),
                )

                db.add(red_flag)

            db.commit()
            db.refresh(analysis)

            logger.info(f"Saved {len(all_flags)} red flag records")

            return analysis

        except Exception as e:
            db.rollback()
            logger.error(f"Failed to save analysis results: {e}", exc_info=True)
            raise

    def get_analysis_by_id(self, db: Session, analysis_id: UUID) -> Optional[AnalysisResult]:
        """Retrieve analysis result by ID."""
        return db.query(AnalysisResult).filter(AnalysisResult.id == analysis_id).first()

    def get_analysis_by_report(self, db: Session, report_id: UUID) -> Optional[AnalysisResult]:
        """Retrieve analysis result by report ID."""
        return db.query(AnalysisResult).filter(AnalysisResult.report_id == report_id).first()


# Singleton instance
analysis_service_v2 = AnalysisServiceV2()