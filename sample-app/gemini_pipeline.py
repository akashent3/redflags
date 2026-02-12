import os
import json
import logging
import re
import time
import google.generativeai as genai
from typing import List, Dict, Any
from dataclasses import dataclass

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# --- Configuration ---
if not os.getenv("GOOGLE_API_KEY"):
    logger.warning("GOOGLE_API_KEY not found in environment variables.")

@dataclass
class AnalysisResult:
    risk_score: float
    risk_level: str
    flags: List[Dict[str, Any]]
    category_breakdown: Dict[str, Any]
    summary: str
    financial_data: Dict[str, Any]  # New field for the extracted raw data

class GeminiRedFlagPipeline:
    def __init__(self, model_name: str = "models/gemini-2.5-flash"):
        # CRITICAL CHANGE: Switched to "gemini-1.5-pro". 
        # "Flash" is fast but can be lazy with complex math/extraction on large PDFs.
        # "Pro" is much better at finding needle-in-haystack data like "Audit Fees" in footnotes.
        self.model_name = model_name
        genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))
        self.model = genai.GenerativeModel(self.model_name)
        
        self.CATEGORY_WEIGHTS = {
            "Auditor": 0.20,
            "Cash Flow": 0.18,
            "Related Party": 0.15,
            "Promoter": 0.15,
            "Governance": 0.12,
            "Balance Sheet": 0.10,
            "Revenue Quality": 0.05,
            "Textual Analysis": 0.05,
        }
        
        self.SEVERITY_POINTS = {
            "CRITICAL": 25,
            "HIGH": 15,
            "MEDIUM": 8,
            "LOW": 3,
        }

    def _upload_files(self, file_paths: List[str]):
        """Uploads files and ensures they are fully processed."""
        uploaded_files = []
        for path in file_paths:
            logger.info(f"Uploading file: {path}")
            myfile = genai.upload_file(path)
            
            while myfile.state.name == "PROCESSING":
                logger.info(f"Waiting for {path} to process...")
                time.sleep(2)
                myfile = genai.get_file(myfile.name)
                
            if myfile.state.name != "ACTIVE":
                raise Exception(f"File {myfile.name} failed to process. State: {myfile.state.name}")
            
            uploaded_files.append(myfile)
        return uploaded_files

    def _clean_json_text(self, text: str) -> str:
        text = text.strip()
        match = re.search(r"```(?:json)?\s*(.*?)```", text, re.DOTALL)
        if match:
            return match.group(1).strip()
        return text

    def _get_master_prompt(self) -> str:
        return """
        You are an expert Forensic Accountant. You have been provided with Annual Reports for multiple years (e.g., 2023, 2024, 2025).

        **YOUR GOAL:** Detect 54 specific Red Flags by strictly following a 3-step process.

        ---
        
        ### STEP 1: EXTRACT FINANCIAL DATA (Mental Scratchpad)
        Before determining any flags, you MUST extract the following data for EACH year provided. 
        Look in the **Consolidated Financial Statements**, **Profit & Loss**, **Balance Sheet**, **Cash Flow Statement**, and **Notes to Accounts**.
        
        * **Revenue** (Revenue from Operations)
        * **Net Profit** (PAT)
        * **CFO** (Cash Flow from Operating Activities)
        * **Total Debt** (Long Term + Short Term Borrowings)
        * **Total Equity** (Share Capital + Reserves)
        * **Audit Fees** (Look in "Other Expenses" or Notes)
        * **Receivables** (Trade Receivables)
        * **Inventory**
        * **Related Party Transactions Total**
        * **Promoter Pledging %** (Look in Shareholding Pattern or Corporate Governance Report)

        *If a number is not explicitly stated, CALCULATE it from the components you find.*

        ---

        ### STEP 2: CALCULATE RATIOS
        Use the extracted data to calculate:
        * Revenue Growth % vs CFO Growth %
        * Debt Growth % vs Equity Growth %
        * Inventory Growth % vs COGS Growth %
        * CFO / PAT Ratio

        ---

        ### STEP 3: EVALUATE THE 54 FLAGS
        Now, evaluate the 54 flags based on the data and calculations from Steps 1 & 2.
        
        **CRITICAL RULE:** Do not say "Data unavailable" unless you have checked the Notes to Accounts and Schedules thoroughly. 
        For example, "Audit Fees" is ALWAYS in the Annual Report under "Payment to Auditors". Find it.

        Output must be valid JSON ONLY. Structure:
        {
            "financial_summary": {
                "2023": {"Revenue": 100, "PAT": 10, "CFO": 8, "Debt": 50},
                "2024": {"Revenue": 120, "PAT": 15, "CFO": 12, "Debt": 55},
                ...
            },
            "summary": "Executive summary of the risk profile...",
            "flags": [
                {
                    "flag_number": 1,
                    "flag_name": "Auditor Resigned Mid-Term",
                    "category": "Auditor",
                    "severity": "CRITICAL",
                    "is_triggered": boolean,
                    "confidence_score": int,
                    "evidence": "Quote the specific number or text. E.g., 'Audit fees dropped from 5Cr to 4Cr (Note 23)'"
                },
                ... (Return ALL 54 FLAGS)
            ]
        }

        ---

        ### THE 54 FLAGS TO CHECK:

        CATEGORY 1: AUDITOR
        1. Auditor Resigned Mid-Term (CRITICAL) - Check Directors Report & Auditor Report.
        2. Auditor Downgrade (Big4 to Small) (HIGH) - Compare Auditor names across years.
        3. Qualified/Adverse Opinion (CRITICAL) - Check Independent Auditor's Report opinion section.
        4. Emphasis of Matter Paragraphs (HIGH) - Check Auditor's Report.
        5. Going Concern Issues (CRITICAL) - Check Auditor's Report & Notes.
        6. KAM on Revenue Recognition (HIGH) - Check Key Audit Matters section.
        7. Audit Fees Declining vs Growth (MEDIUM) - Check 'Payment to Auditors' in Notes.
        8. Same Auditor 10+ Years (MEDIUM) - Check appointment date in Governance Report.

        CATEGORY 2: CASH FLOW
        9. Profit Growing, CFO Flat (HIGH) - Compare PAT growth vs CFO growth.
        10. Receivables > Revenue Growth (HIGH) - Compare Trade Receivables growth vs Revenue growth.
        11. Inventory > COGS Growth (HIGH) - Compare Inventory growth vs Cost of Materials/COGS growth.
        12. Capex >> Depreciation (Ratio > 3x) (MEDIUM) - Compare Cash Flow from Investing (Capex) vs Depreciation in P&L.
        13. Frequent Exceptional Items (MEDIUM) - Check P&L for 'Exceptional Items' line.
        14. CFO Negative 2+ Years (HIGH) - Check CFO line in Cash Flow Statement.
        15. Cash Conversion Cycle Up (MEDIUM) - Calculate (Receivable Days + Inventory Days - Payable Days).
        16. Unusual Other Income (>10% of Rev) (MEDIUM) - Check 'Other Income' line in P&L.

        CATEGORY 3: RELATED PARTY
        17. RPT > 10% of Revenue (HIGH) - Check 'Related Party Transactions' Note total amount vs Revenue.
        18. Loans to Related Parties (HIGH) - Check RPT Note for 'Loans given'.
        19. Purchases from RP at Premium (MEDIUM) - Check RPT Note for purchase value & terms.
        20. Revenue from RP Increasing (MEDIUM) - Compare 'Sales to Related Parties' across years.
        21. Complex Structure > 20 Subsidiaries (MEDIUM) - Check 'List of Subsidiaries' in Aoc-1 or Notes.
        22. Loans to Directors/KMP (HIGH) - Check RPT Note or Governance Report.
        23. New Related Parties Added (MEDIUM) - Compare RPT name lists between years.

        CATEGORY 4: PROMOTER
        24. Promoter Pledge > 50% (CRITICAL) - Check Shareholding Pattern table.
        25. Pledge Increasing QoQ (HIGH) - Check Shareholding Pattern table.
        26. Promoter Selling Shares (MEDIUM) - Check Change in Promoter Shareholding.
        27. Disproportionate Salary (>5% PAT) (MEDIUM) - Check 'Remuneration to Directors' in MGT-9 or Notes.
        28. Promoter Entity Name Change (LOW) - Check Notes/General Info.
        29. ICDs to Promoter Group (HIGH) - Check 'Inter-Corporate Deposits' in RPT Note.

        CATEGORY 5: GOVERNANCE
        30. Independent Director Exit (HIGH) - Check Board Changes in Directors Report.
        31. CFO/CS Change in Year (HIGH) - Check KMP Changes.
        32. Low Board Attendance (<75%) (MEDIUM) - Check Corporate Governance Report table.
        33. Related on Audit Committee (MEDIUM) - Check Audit Committee Composition.
        34. Delayed AGM/Results (MEDIUM) - Check Dates of AGM/Results.
        35. SEBI/Exchange Penalties (HIGH) - Check 'Secretarial Audit Report' or 'Corporate Governance'.
        36. Whistle-blower Complaints (MEDIUM) - Check 'Vigil Mechanism' section.

        CATEGORY 6: BALANCE SHEET
        37. Debt Growing > Equity (HIGH) - Compare Total Borrowings growth vs Net Worth growth.
        38. Interest Coverage < 2x (HIGH) - Calculate EBIT / Finance Costs.
        39. ST Debt Funding LT Assets (>60% of debt) (HIGH) - Check Short Term Borrowings vs Total Debt.
        40. Contingent Liabilities > 20% NW (HIGH) - Check 'Contingent Liabilities' Note vs Net Worth.
        41. Frequent Debt Restructuring (MEDIUM) - Check Notes on Borrowings.
        42. Heavy Asset Pledging (>50% Assets) (MEDIUM) - Check 'Assets Pledged' in Borrowings Note.
        43. Intangibles Growing Fast (>30%) (MEDIUM) - Check Intangible Assets in Balance Sheet.

        CATEGORY 7: REVENUE QUALITY
        44. Revenue Concentrated in Q4 (>40%) (MEDIUM) - Check Quarterly Results table if available, or text.
        45. Top Customer > 25% (MEDIUM) - Check Risk Factors or Segment Info.
        46. Revenue Policy Change (HIGH) - Check 'Significant Accounting Policies'.
        47. Unbilled Revenue Growing (MEDIUM) - Check 'Other Financial Assets' or Revenue Notes.
        48. Unusual Export Geography (Tax Havens) (LOW) - Check Geographic Segment info.

        CATEGORY 8: TEXTUAL ANALYSIS
        49. MD&A Tone Defensive (MEDIUM) - Analyze Management Discussion & Analysis.
        50. Increased Jargon (LOW) - Check complexity of language.
        51. Declining Disclosure (MEDIUM) - Compare volume of notes/MD&A.
        52. Risk Factors Expanding (MEDIUM) - Check 'Risk Management' section.
        53. Contradictions MD&A vs Financials (HIGH) - Compare text claims vs extracted numbers.
        54. Unusual Audit Language (MEDIUM) - Check Auditor's Report for 'Emphasis' or 'Qualification'.
        """

    def _calculate_score(self, flags: List[Dict]) -> Dict:
        """Same scoring logic as before"""
        category_scores = {cat: 0.0 for cat in self.CATEGORY_WEIGHTS}
        category_max_points = {cat: 0.0 for cat in self.CATEGORY_WEIGHTS}
        
        for flag in flags:
            cat = flag.get('category', 'Auditor')
            sev = flag.get('severity', 'LOW')
            points = self.SEVERITY_POINTS.get(sev, 0)
            
            category_max_points[cat] += points
            
            if flag.get('is_triggered', False):
                conf = flag.get('confidence_score', 100) / 100.0
                category_scores[cat] += (points * conf)

        final_cat_scores = {}
        weighted_sum = 0.0
        
        for cat, raw_score in category_scores.items():
            max_p = category_max_points.get(cat, 1)
            if max_p == 0: max_p = 1
            norm_score = (raw_score / max_p) * 100
            final_cat_scores[cat] = min(norm_score, 100)
            weight = self.CATEGORY_WEIGHTS.get(cat, 0)
            weighted_sum += (norm_score * weight)

        risk_level = "LOW"
        if weighted_sum >= 80: risk_level = "CRITICAL"
        elif weighted_sum >= 60: risk_level = "HIGH"
        elif weighted_sum >= 40: risk_level = "ELEVATED"
        elif weighted_sum >= 20: risk_level = "MODERATE"

        return {
            "risk_score": round(weighted_sum, 2),
            "risk_level": risk_level,
            "category_scores": {k: round(v, 2) for k, v in final_cat_scores.items()}
        }

    def analyze(self, file_paths: List[str]) -> AnalysisResult:
        uploaded_files = self._upload_files(file_paths)
        prompt = self._get_master_prompt()
        
        logger.info("Sending request to Gemini (Models 1.5 Pro)...")
        response = self.model.generate_content(
            [prompt, *uploaded_files],
            generation_config={"response_mime_type": "application/json"}
        )
        
        raw_text = response.text
        cleaned_text = self._clean_json_text(raw_text)
        
        try:
            result_json = json.loads(cleaned_text)
            flags = result_json.get("flags", [])
            summary = result_json.get("summary", "No summary provided.")
            financial_data = result_json.get("financial_summary", {}) # Capture the CoT data
        except json.JSONDecodeError as e:
            logger.error(f"JSON Error: {str(e)}")
            flags = []
            summary = "Error parsing analysis results."
            financial_data = {}

        scoring_result = self._calculate_score(flags)
        
        return AnalysisResult(
            risk_score=scoring_result["risk_score"],
            risk_level=scoring_result["risk_level"],
            flags=flags,
            category_breakdown=scoring_result["category_scores"],
            summary=summary,
            financial_data=financial_data
        )