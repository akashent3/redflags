"""Analysis Orchestration Service for RedFlag AI.

Coordinates the entire annual report analysis workflow:
1. PDF extraction
2. Section detection
3. Financial data extraction
4. Red flag detection (all 54 flags)
5. Risk score calculation
6. Results persistence
"""

import logging
from typing import Dict, List, Optional
from uuid import UUID

from sqlalchemy.orm import Session

from app.models.analysis_result import AnalysisResult
from app.models.annual_report import AnnualReport
from app.models.red_flag import RedFlag as RedFlagModel
from app.pdf_pipeline.data_extractor import financial_data_extractor
from app.pdf_pipeline.extractor import pdf_extractor
from app.pdf_pipeline.section_detector import section_detector
from app.red_flags.registry import flag_registry
from app.scoring.risk_calculator import risk_calculator

logger = logging.getLogger(__name__)


class AnalysisService:
    """Service to orchestrate complete annual report analysis."""

    def analyze_report(
        self, db: Session, report_id: UUID, pdf_bytes: bytes, company_name: str = "", fiscal_year: str = ""
    ) -> AnalysisResult:
        """
        Run complete analysis on an annual report PDF.

        Args:
            db: Database session
            report_id: UUID of the AnnualReport record
            pdf_bytes: PDF file content as bytes
            company_name: Optional company name for context
            fiscal_year: Optional fiscal year (e.g., "2023")

        Returns:
            AnalysisResult object with complete analysis

        Raises:
            Exception: If any step of analysis fails
        """
        logger.info(f"Starting analysis for report {report_id}")

        try:
            # Step 1: Extract PDF text and structure
            logger.info("Step 1/6: Extracting PDF text")
            extraction_result = pdf_extractor.extract_from_bytes(pdf_bytes)

            if not extraction_result or not extraction_result.get("text"):
                raise Exception("PDF extraction failed - no text extracted")

            logger.info(
                f"Extracted {extraction_result['total_pages']} pages, "
                f"{len(extraction_result['text'])} characters"
            )

            # Step 2: Detect financial sections
            logger.info("Step 2/6: Detecting financial sections")
            sections = section_detector.detect_sections(
                full_text=extraction_result["text"],
                pages_data=extraction_result["pages"],
                total_pages=extraction_result["total_pages"],
            )

            logger.info(f"Detected {len(sections)} sections: {list(sections.keys())}")

            # Step 3: Extract section texts
            logger.info("Step 3/6: Extracting section texts")
            section_texts = {}

            for section_name, page_range in sections.items():
                if page_range:
                    section_text = section_detector.extract_section_text(
                        section_name, sections, extraction_result["pages"]
                    )
                    section_texts[section_name] = section_text
                    logger.debug(f"  {section_name}: {len(section_text)} chars from pages {page_range}")

            # Step 4: Extract financial data
            logger.info("Step 4/6: Extracting financial data")
            financial_data = financial_data_extractor.extract_key_metrics(
                sections=section_texts, fiscal_year=fiscal_year or "2023"
            )

            logger.info(f"Extracted financial data: {list(financial_data.keys())}")

            # Step 5: Run all 54 red flag checks
            logger.info("Step 5/6: Running 54 red flag checks")

            # Prepare data package for flags
            analysis_data = {
                "sections": section_texts,
                "financial_data": financial_data,
                "extraction_result": extraction_result,
                "company_name": company_name,
                "fiscal_year": fiscal_year,
            }

            # Get all registered flags
            all_flags = flag_registry.get_all_flags()
            logger.info(f"Registry has {len(all_flags)} flags registered")

            if len(all_flags) != 54:
                logger.warning(f"Expected 54 flags, but registry has {len(all_flags)}")

            # Run each flag check
            flag_results = []
            failed_flags = []

            for flag in all_flags:
                try:
                    logger.debug(f"  Checking flag #{flag.flag_number}: {flag.flag_name}")
                    result = flag.check(analysis_data)
                    flag_results.append(result)

                    if result.is_triggered:
                        logger.info(
                            f"    🚩 TRIGGERED: {flag.flag_name} "
                            f"(confidence: {result.confidence_score:.1f}%)"
                        )

                except Exception as e:
                    logger.error(f"  Flag #{flag.flag_number} ({flag.flag_name}) check failed: {e}", exc_info=True)
                    failed_flags.append({"flag_number": flag.flag_number, "flag_name": flag.flag_name, "error": str(e)})
                    # Create a not-triggered result for failed flags
                    flag_results.append(
                        flag.create_not_triggered_result(f"Check failed: {str(e)}")
                    )

            logger.info(
                f"Completed red flag checks: "
                f"{sum(1 for r in flag_results if r.is_triggered)}/{len(flag_results)} triggered"
            )

            if failed_flags:
                logger.warning(f"{len(failed_flags)} flags failed to execute: {failed_flags}")

            # Step 6: Calculate risk score
            logger.info("Step 6/6: Calculating risk score")
            risk_data = risk_calculator.calculate_risk_score(flag_results)

            logger.info(
                f"Risk Score: {risk_data['risk_score']} ({risk_data['risk_level']}), "
                f"Flags Triggered: {risk_data['flags_triggered_count']}/54"
            )

            # Step 7: Save results to database
            logger.info("Saving results to database")
            analysis_result = self._save_results(
                db=db,
                report_id=report_id,
                risk_data=risk_data,
                flag_results=flag_results,
                failed_flags=failed_flags,
            )

            logger.info(f"Analysis complete. Result ID: {analysis_result.id}")

            return analysis_result

        except Exception as e:
            logger.error(f"Analysis failed for report {report_id}: {e}", exc_info=True)
            raise

    def _save_results(
        self,
        db: Session,
        report_id: UUID,
        risk_data: Dict,
        flag_results: List,
        failed_flags: List[Dict],
    ) -> AnalysisResult:
        """
        Save analysis results to database.

        Creates:
        - 1 AnalysisResult record (summary)
        - 54 RedFlag records (individual flag results)
        """
        try:
            # Create AnalysisResult record
            analysis = AnalysisResult(
                report_id=report_id,
                risk_score=risk_data["risk_score"],
                risk_level=risk_data["risk_level"],
                category_scores=risk_data["category_scores"],
                flags_triggered_count=risk_data["flags_triggered_count"],
                flags_critical_count=risk_data["flags_by_severity"]["critical"],
                flags_high_count=risk_data["flags_by_severity"]["high"],
                flags_medium_count=risk_data["flags_by_severity"]["medium"],
                flags_low_count=risk_data["flags_by_severity"]["low"],
                summary_text=self._generate_summary(risk_data),
                key_concerns=risk_data["top_concerns"],
                failed_checks_count=len(failed_flags),
                failed_checks_details=failed_flags if failed_flags else None,
            )

            db.add(analysis)
            db.flush()  # Get analysis.id

            logger.info(f"Created AnalysisResult: {analysis.id}")

            # Create RedFlag records for each flag result
            for flag_result in flag_results:
                red_flag = RedFlagModel(
                    analysis_id=analysis.id,
                    flag_number=flag_result.flag_number,
                    flag_name=flag_result.flag_name,
                    flag_description=self._get_flag_description(flag_result),
                    category=flag_result.category,
                    severity=flag_result.severity,
                    is_triggered=flag_result.is_triggered,
                    confidence_score=flag_result.confidence_score,
                    evidence_text=flag_result.evidence_text,
                    page_references=flag_result.page_references,
                    extracted_data=self._serialize_extracted_data(flag_result.extracted_data),
                    detection_method=flag_result.detection_method,
                )

                db.add(red_flag)

            db.commit()
            db.refresh(analysis)

            logger.info(f"Saved {len(flag_results)} red flag records")

            return analysis

        except Exception as e:
            db.rollback()
            logger.error(f"Failed to save analysis results: {e}", exc_info=True)
            raise

    def _generate_summary(self, risk_data: Dict) -> str:
        """Generate human-readable summary of analysis."""
        risk_score = risk_data["risk_score"]
        risk_level = risk_data["risk_level"]
        triggered = risk_data["flags_triggered_count"]
        critical = risk_data["flags_by_severity"]["critical"]
        high = risk_data["flags_by_severity"]["high"]

        summary = f"Risk Score: {risk_score}/100 ({risk_level}). "
        summary += f"Detected {triggered} red flags out of 54 checks. "

        if critical > 0:
            summary += f"CRITICAL: {critical} critical issues require immediate attention. "

        if high > 0:
            summary += f"HIGH: {high} high-severity concerns identified. "

        # Add category-specific insights
        category_scores = risk_data.get("category_breakdown", {})
        high_risk_categories = [
            cat for cat, details in category_scores.items() if details.get("score", 0) > 60
        ]

        if high_risk_categories:
            summary += f"High risk in: {', '.join(high_risk_categories)}. "

        # Add top concerns
        top_concerns = risk_data.get("top_concerns", [])
        if top_concerns:
            summary += f"Top concerns: {', '.join(top_concerns[:3])}."

        return summary

    def _get_flag_description(self, flag_result) -> str:
        """Get full description for a flag."""
        # This would ideally come from a central registry of descriptions
        # For now, use the flag name as description
        return flag_result.flag_name

    def _serialize_extracted_data(self, extracted_data: Dict) -> Optional[str]:
        """Serialize extracted data for storage."""
        if not extracted_data:
            return None

        try:
            import json

            # Convert to JSON string, handling non-serializable types
            return json.dumps(extracted_data, default=str)
        except Exception as e:
            logger.warning(f"Failed to serialize extracted data: {e}")
            return str(extracted_data)

    def get_analysis_by_id(self, db: Session, analysis_id: UUID) -> Optional[AnalysisResult]:
        """Retrieve analysis result by ID."""
        return db.query(AnalysisResult).filter(AnalysisResult.id == analysis_id).first()

    def get_analysis_by_report(self, db: Session, report_id: UUID) -> Optional[AnalysisResult]:
        """Retrieve analysis result by report ID."""
        return db.query(AnalysisResult).filter(AnalysisResult.report_id == report_id).first()

    def get_red_flags_for_analysis(
        self, db: Session, analysis_id: UUID, triggered_only: bool = False
    ) -> List[RedFlagModel]:
        """Get all red flags for an analysis."""
        query = db.query(RedFlagModel).filter(RedFlagModel.analysis_id == analysis_id)

        if triggered_only:
            query = query.filter(RedFlagModel.is_triggered == True)

        return query.order_by(RedFlagModel.flag_number).all()


# Singleton instance
analysis_service = AnalysisService()
