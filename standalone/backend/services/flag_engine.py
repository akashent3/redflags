"""Flag aggregation engine - combines FinEdge and Gemini flags."""

import logging
from typing import Dict, List

from services.finedge_service import FinEdgeService
from services.gemini_service import GeminiService
from services.risk_calculator import RiskCalculator
from services.models import RedFlagResult, FlagCategory, FlagSeverity

logger = logging.getLogger(__name__)


class FlagEngine:
    """Orchestrate flag detection from multiple sources."""
    
    def __init__(self, finedge_service: FinEdgeService, gemini_service: GeminiService):
        """Initialize flag engine with services."""
        self.finedge_service = finedge_service
        self.gemini_service = gemini_service
        self.risk_calculator = RiskCalculator()
    
    def analyze(self, symbol: str, fiscal_year: int, pdf_path: str) -> Dict:
        """
        Run complete analysis: FinEdge + Gemini + Risk Calculation.
        
        Args:
            symbol: Stock symbol
            fiscal_year: Fiscal year
            pdf_path: Path to PDF file
            
        Returns:
            Complete analysis results with all 42 flags and risk score
        """
        logger.info(f"Starting analysis for {symbol}, FY{fiscal_year}")
        
        results = {
            "symbol": symbol,
            "fiscal_year": fiscal_year,
            "finedge_flags": [],
            "gemini_flags": [],
            "all_flags": [],
            "risk_score": {},
            "errors": []
        }
        
        # Get FinEdge flags (14 flags)
        try:
            logger.info("Fetching FinEdge flags...")
            finedge_flags = self.finedge_service.calculate_flags(symbol, fiscal_year)
            results["finedge_flags"] = finedge_flags
            logger.info(f"FinEdge analysis complete: {len(finedge_flags)} flags")
        except Exception as e:
            logger.error(f"FinEdge analysis failed: {e}")
            results["errors"].append(f"FinEdge error: {str(e)}")
            finedge_flags = []
        
        # Get Gemini flags (28 flags)
        try:
            logger.info("Analyzing PDF with Gemini...")
            gemini_result = self.gemini_service.analyze_pdf(pdf_path, fiscal_year)
            gemini_flags = gemini_result.get("flags", [])
            results["gemini_flags"] = gemini_flags
            results["gemini_metadata"] = gemini_result.get("metadata", {})
            results["statement_type"] = gemini_result.get("statement_type", "unknown")
            logger.info(f"Gemini analysis complete: {len(gemini_flags)} flags")
        except Exception as e:
            logger.error(f"Gemini analysis failed: {e}")
            results["errors"].append(f"Gemini error: {str(e)}")
            gemini_flags = []
        
        # Combine all flags (42 total)
        all_flags = finedge_flags + gemini_flags
        results["all_flags"] = all_flags
        
        logger.info(f"Total flags: {len(all_flags)}")
        
        # Convert to RedFlagResult objects for risk calculation
        flag_results = self._convert_to_flag_results(all_flags)
        
        # Calculate risk score
        try:
            logger.info("Calculating risk score...")
            risk_score = self.risk_calculator.calculate_risk_score(flag_results)
            results["risk_score"] = risk_score
            logger.info(f"Risk score: {risk_score.get('risk_score', 0):.1f} ({risk_score.get('risk_level', 'UNKNOWN')})")
        except Exception as e:
            logger.error(f"Risk calculation failed: {e}")
            results["errors"].append(f"Risk calculation error: {str(e)}")
            results["risk_score"] = {
                "risk_score": 0,
                "risk_level": "UNKNOWN",
                "error": str(e)
            }
        
        return results
    
    def _convert_to_flag_results(self, flags: List[Dict]) -> List[RedFlagResult]:
        """Convert flag dictionaries to RedFlagResult objects."""
        results = []
        
        for flag in flags:
            try:
                # Map category string to enum
                category_map = {
                    "Auditor": FlagCategory.AUDITOR,
                    "Cash Flow": FlagCategory.CASH_FLOW,
                    "Related Party": FlagCategory.RELATED_PARTY,
                    "Promoter": FlagCategory.PROMOTER,
                    "Governance": FlagCategory.GOVERNANCE,
                    "Corporate Governance": FlagCategory.GOVERNANCE,
                    "Balance Sheet": FlagCategory.BALANCE_SHEET,
                    "Revenue Quality": FlagCategory.REVENUE,
                    "Revenue": FlagCategory.REVENUE,
                    "Textual Analysis": FlagCategory.TEXTUAL,
                }
                
                category = category_map.get(flag.get("category", ""), FlagCategory.AUDITOR)
                
                # Map severity string to enum
                severity_map = {
                    "CRITICAL": FlagSeverity.CRITICAL,
                    "HIGH": FlagSeverity.HIGH,
                    "MEDIUM": FlagSeverity.MEDIUM,
                    "LOW": FlagSeverity.LOW,
                }
                
                severity = severity_map.get(flag.get("severity", ""), FlagSeverity.MEDIUM)
                
                result = RedFlagResult(
                    flag_number=flag.get("flag_id", 0),
                    flag_name=flag.get("flag_name", "Unknown"),
                    category=category,
                    severity=severity,
                    is_triggered=flag.get("triggered", False),
                    confidence_score=flag.get("confidence", 0),
                    evidence_text=flag.get("evidence", ""),
                    page_references=flag.get("page_references", []),
                    extracted_data=flag.get("value", {}) or {}
                )
                
                results.append(result)
                
            except Exception as e:
                logger.error(f"Error converting flag {flag.get('flag_id', '?')}: {e}")
        
        return results
