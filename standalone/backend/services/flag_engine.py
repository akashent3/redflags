"""Flag aggregation engine - combines FinEdge and Gemini flags."""

import logging
from typing import Dict, List
from .finedge_service import FinEdgeService
from .gemini_service import GeminiService
from .risk_calculator import RiskCalculator

logger = logging.getLogger(__name__)


class FlagEngine:
    """Aggregates flags from FinEdge and Gemini services."""
    
    def __init__(self):
        """Initialize flag engine with services."""
        self.finedge_service = FinEdgeService()
        self.gemini_service = GeminiService()
        self.risk_calculator = RiskCalculator()
    
    def analyze(self, symbol: str, fiscal_year: int, pdf_path: str) -> Dict:
        """
        Run complete analysis combining FinEdge and Gemini.
        
        Args:
            symbol: Stock symbol
            fiscal_year: Fiscal year
            pdf_path: Path to uploaded PDF
            
        Returns:
            Complete analysis result with all flags and risk score
        """
        logger.info(f"Starting analysis for {symbol}, FY{fiscal_year}")
        
        all_flags = []
        
        # Get FinEdge flags
        try:
            logger.info("Fetching FinEdge flags...")
            finedge_flags = self.finedge_service.calculate_flags(symbol, fiscal_year)
            all_flags.extend(finedge_flags)
            logger.info(f"FinEdge analysis complete: {len(finedge_flags)} flags")
        except Exception as e:
            logger.error(f"FinEdge analysis failed: {e}")
            # Add default FinEdge flags
            all_flags.extend(self._get_default_finedge_flags(str(e)))
        
        # Get Gemini flags
        try:
            logger.info("Analyzing PDF with Gemini...")
            gemini_result = self.gemini_service.analyze_pdf(pdf_path, symbol, fiscal_year)
            gemini_flags = gemini_result.get("flags", [])
            all_flags.extend(gemini_flags)
            logger.info(f"Gemini analysis complete: {len(gemini_flags)} flags")
        except Exception as e:
            logger.error(f"Gemini analysis failed: {e}")
            import traceback
            logger.error(traceback.format_exc())
            # Add default Gemini flags
            all_flags.extend(self._get_default_gemini_flags(str(e)))
        
        # Sort flags by flag_id
        all_flags.sort(key=lambda x: x.get("flag_id", 0))
        
        logger.info(f"Total flags: {len(all_flags)}")
        
        # Calculate risk score
        logger.info("Calculating risk score...")
        risk_score, risk_level, category_scores = self.risk_calculator.calculate_risk_score(all_flags)
        logger.info(f"Risk score: {risk_score} ({risk_level})")
        
        # Build result
        result = {
            "symbol": symbol,
            "fiscal_year": fiscal_year,
            "risk_score": risk_score,
            "risk_level": risk_level,
            "total_flags": len(all_flags),
            "triggered_flags": sum(1 for f in all_flags if f.get("triggered", False)),
            "category_scores": category_scores,
            "flags": all_flags,
            "metadata": {
                "finedge_flags": len([f for f in all_flags if f.get("flag_id", 0) in [7,8,9,10,11,12,13,14,22,23,24,32,33,38,39]]),
                "gemini_flags": len([f for f in all_flags if f.get("flag_id", 0) not in [7,8,9,10,11,12,13,14,22,23,24,32,33,38,39]]),
            }
        }
        
        return result
    
    def _get_default_finedge_flags(self, reason: str) -> List[Dict]:
        """Return default FinEdge flags when service fails."""
        flag_definitions = [
            (7, "PAT Growing, CFO Flat", "Cash Flow", "HIGH"),
            (8, "Receivables Growing > Revenue", "Cash Flow", "HIGH"),
            (9, "Inventory Growing > COGS", "Cash Flow", "HIGH"),
            (10, "Capex > Depreciation (>3x)", "Cash Flow", "MEDIUM"),
            (11, "Frequent Exceptional Items", "Cash Flow", "MEDIUM"),
            (12, "Negative CFO", "Cash Flow", "HIGH"),
            (13, "CCC > 120 days", "Cash Flow", "MEDIUM"),
            (14, "Unusual Other Income > 10%", "Cash Flow", "MEDIUM"),
            (22, "Promoter Pledge > 50%", "Promoter", "CRITICAL"),
            (23, "Promoter Pledge Increasing QoQ", "Promoter", "HIGH"),
            (24, "Promoter Selling Shares", "Promoter", "MEDIUM"),
            (32, "Debt Growing Faster than Equity", "Balance Sheet", "HIGH"),
            (33, "Interest Coverage < 2x", "Balance Sheet", "HIGH"),
            (38, "Intangible Assets Growing Fast", "Balance Sheet", "MEDIUM"),
            (39, "Revenue Concentrated in Q4 (>40%)", "Revenue Quality", "MEDIUM"),
        ]
        
        return [
            {
                "flag_id": fid,
                "flag_name": name,
                "category": cat,
                "triggered": False,
                "severity": sev,
                "evidence": f"FinEdge service error: {reason}",
                "page_references": [],
                "confidence": 0,
                "value": None
            }
            for fid, name, cat, sev in flag_definitions
        ]
    
    def _get_default_gemini_flags(self, reason: str) -> List[Dict]:
        """Return default Gemini flags when service fails."""
        flag_definitions = [
            # Category 1: Auditor (6 flags)
            (1, "Auditor Resignation Mid-Term", "Auditor", "CRITICAL"),
            (2, "Qualified/Adverse/Disclaimer Opinion", "Auditor", "CRITICAL"),
            (3, "Emphasis of Matter Paragraph", "Auditor", "HIGH"),
            (4, "Going Concern Issue", "Auditor", "CRITICAL"),
            (5, "KAM on Revenue Recognition", "Auditor", "HIGH"),
            (6, "Audit Fees Declining", "Auditor", "MEDIUM"),
            
            # Category 3: Related Party (7 flags)
            (15, "RPT > 10% of Revenue", "Related Party", "HIGH"),
            (16, "Loans to Related Parties", "Related Party", "HIGH"),
            (17, "Purchases from RP at Premium", "Related Party", "MEDIUM"),
            (18, "Revenue from RP Increasing", "Related Party", "MEDIUM"),
            (19, "Complex Structure > 20 Subsidiaries", "Related Party", "MEDIUM"),
            (20, "Loans to Directors/KMP", "Related Party", "HIGH"),
            (21, "New Related Parties Added", "Related Party", "MEDIUM"),
            
            # Category 4: Promoter (3 flags)
            (25, "Disproportionate Managerial Remuneration", "Promoter", "MEDIUM"),
            (26, "Promoter Entity Name Change", "Promoter", "LOW"),
            (27, "ICDs to Promoter Group", "Promoter", "HIGH"),
            
            # Category 5: Corporate Governance (4 flags)
            (28, "Independent Director Resignation", "Corporate Governance", "HIGH"),
            (29, "Related Party on Audit Committee", "Corporate Governance", "MEDIUM"),
            (30, "SEBI/Stock Exchange Penalties", "Corporate Governance", "HIGH"),
            (31, "Whistle-blower Complaints", "Corporate Governance", "MEDIUM"),
            
            # Category 6: Balance Sheet (4 flags)
            (34, "Short-term Debt > 60% of Total", "Balance Sheet", "HIGH"),
            (35, "Contingent Liabilities > 20% NW", "Balance Sheet", "HIGH"),
            (36, "Frequent Debt Restructuring", "Balance Sheet", "MEDIUM"),
            (37, "Heavy Asset Pledging", "Balance Sheet", "MEDIUM"),
            
            # Category 7: Revenue Quality (2 flags)
            (40, "Revenue Recognition Policy Changed", "Revenue Quality", "HIGH"),
            (41, "Unbilled Revenue Growing Faster", "Revenue Quality", "MEDIUM"),
            
            # Category 8: Textual Analysis (1 flag)
            (42, "MD&A Tone is Defensive", "Textual Analysis", "MEDIUM"),
        ]
        
        return [
            {
                "flag_id": fid,
                "flag_name": name,
                "category": cat,
                "triggered": False,
                "severity": sev,
                "evidence": f"Gemini service error: {reason}",
                "page_references": [],
                "confidence": 0,
                "value": None
            }
            for fid, name, cat, sev in flag_definitions
        ]