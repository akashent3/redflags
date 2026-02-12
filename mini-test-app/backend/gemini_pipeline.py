"""Core Gemini 2.5 Flash Pipeline - Direct PDF Processing."""

import json
import logging
import time
from typing import List, Dict, Any
from datetime import datetime
import google.generativeai as genai

from schema import (
    create_analysis_output, 
    create_red_flag_result,
    CATEGORIES,
    SEVERITY_POINTS,
    RISK_LEVELS
)
from prompts.financial_extraction import get_financial_extraction_prompt
from prompts.red_flags.auditor_flags import get_all_auditor_prompts
from prompts.red_flags.cashflow_flags import get_all_cashflow_prompts
from prompts.red_flags.remaining_flags import get_all_remaining_flags, generate_flag_check_prompt

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class GeminiPipeline:
    """
    Main pipeline for analyzing annual reports using Gemini 2.5 Flash.
    
    Replaces the multi-stage Python pipeline with direct PDF processing.
    """
    
    def __init__(self, api_key: str):
        """Initialize Gemini client."""
        genai.configure(api_key=api_key)
        self.model = genai.GenerativeModel('gemini-2.5-flash')
        logger.info("Gemini Pipeline initialized")
    
    def analyze_company(
        self,
        company_name: str,
        pdf_files: List[str],
        years: List[str],
        file_info: List[Dict]
    ) -> Dict[str, Any]:
        """
        Main analysis function - processes 3 years of annual reports.
        
        Args:
            company_name: Company name
            pdf_files: List of 3 PDF file paths [Year1, Year2, Year3]
            years: List of year strings ["2021", "2022", "2023"]
            file_info: List of file metadata dicts
        
        Returns:
            Complete analysis results as JSON matching schema
        """
        logger.info(f"Starting analysis for {company_name}")
        logger.info(f"Processing {len(pdf_files)} annual reports for years: {years}")
        
        try:
            # Upload PDFs once at the start
            logger.info("Uploading PDFs to Gemini (one-time)...")
            uploaded_files = self._upload_files(pdf_files)
            logger.info(f"✓ All {len(uploaded_files)} PDFs uploaded successfully")
            
            # COMBINED ANALYSIS (4 API calls total instead of 57!)
            logger.info("Step 1-2/4: Running combined analysis (extraction + flags)...")
            financial_data, red_flags = self.analyze_with_combined_calls(uploaded_files, years)
            
            # Step 3: Calculate risk scores
            logger.info("Step 3/4: Calculating risk scores...")
            risk_result = self.calculate_risk_scores(red_flags)
            
            # Step 4: Format output
            logger.info("Step 4/4: Formatting final output...")
            output = create_analysis_output(
                company_name=company_name,
                annual_reports=file_info,
                risk_score=risk_result['risk_score'],
                risk_level=risk_result['risk_level'],
                category_scores=risk_result['category_scores'],
                red_flags=red_flags,
                financial_data=financial_data
            )
            
            logger.info(f"Analysis complete! Risk Score: {risk_result['risk_score']}/100 ({risk_result['risk_level']})")
            logger.info(f"Flags triggered: {risk_result['flags_triggered']}/54")
            
            return output
            
        except Exception as e:
            logger.error(f"Analysis failed: {str(e)}", exc_info=True)
            raise
    
    def _upload_files(self, file_paths: List[str]) -> List[Any]:
        """
        Uploads files to Gemini and ensures they are fully processed.
        
        Args:
            file_paths: List of file paths to upload
            
        Returns:
            List of uploaded file objects
        """
        uploaded_files = []
        for path in file_paths:
            logger.info(f"  Uploading {path}...")
            myfile = genai.upload_file(path)
            
            # Wait for file to be processed
            while myfile.state.name == "PROCESSING":
                logger.info(f"  Waiting for {path} to process...")
                time.sleep(2)
                myfile = genai.get_file(myfile.name)
                
            if myfile.state.name != "ACTIVE":
                raise Exception(f"File {myfile.name} failed to process. State: {myfile.state.name}")
            
            logger.info(f"  ✓ Uploaded and processed: {path}")
            uploaded_files.append(myfile)
            
        return uploaded_files
    
    def analyze_with_combined_calls(self, uploaded_files: List[Any], years: List[str]) -> tuple:
        """
        OPTIMIZED: 4 API calls total (avoids token limits).
        
        - Calls 1-3: Per-year (PDF + extraction + flags) - ~300K tokens each
        - Call 4: Multi-year trends (extracted data only, no PDFs) - ~50K tokens
        
        Total: 4 API calls instead of 57 (93% reduction!)
        
        Note: Can't do 1 call with all 3 PDFs due to 1M token limit.
        
        Returns:
            (financial_data_dict, red_flags_list)
        """
        all_financial_data = {}
        all_red_flags = []
        
        logger.info("Running optimized 4-call analysis...")
        
        # === CALLS 1-3: Per-Year Analysis ===
        for idx, (uploaded_file, year) in enumerate(zip(uploaded_files, years)):
            logger.info(f"  Call {idx+1}/4: Analyzing FY {year}...")
            
            try:
                prompt = f"""
# ANALYSIS FOR FISCAL YEAR {year}

Extract financial data AND check red flags for this year.

## PART 1: EXTRACT FINANCIAL DATA

### Balance Sheet (Crores ₹):
total_assets, total_liabilities, shareholders_equity, current_assets, current_liabilities, total_debt, short_term_debt, long_term_debt, receivables, inventory, intangible_assets, cash_and_equivalents, contingent_liabilities

### P&L (Crores ₹):
revenue, gross_profit, ebitda, ebit, net_profit, net_margin_percent, cost_of_goods_sold

### Cash Flow (Crores ₹):
cfo, cfi, cff, capex, free_cash_flow

### Auditor:
auditor_name, audit_opinion, audit_fees (Lakhs), going_concern_warning, emphasis_of_matter

### Promoter:
promoter_shareholding_percent, promoter_pledged_percent

### Related Party:
total_rpt_amount (Crores ₹)

## PART 2: CHECK SINGLE-YEAR FLAGS

Check these flags that DON'T require trend analysis:

**Flags 2-8** (Auditor): Qualified/adverse opinion, disclaimer, going concern, emphasis, high fees, resignation
**Flags 10,12,14,16** (Cashflow): Negative FCF, working capital, inventory, capex issues
**Flags 17,19-24** (RPT): High RPT, loans, guarantees, transfers, compensation, circular
**Flags 28-32** (Promoter): Pledge changes, loans, sales, complex structure
**Flags 33-34,36-37,39-40** (Governance): Directors, board, management, penalties, legal
**Flags 43-44,47-48** (Balance Sheet): Interest coverage, current ratio, contingent liabilities, off-BS
**Flags 49,52** (Revenue): Recognition issues, customer concentration
**Flags 53-54** (Textual): Risk disclosures, management tone

Return JSON:
{{
  "financial_data": {{ all extracted data }},
  "red_flags": [{{ flag results with flag_number, flag_name, category, severity, is_triggered, confidence_score, evidence_text, extracted_data }}]
}}
"""
                
                response = self.model.generate_content(
                    [uploaded_file, prompt],
                    generation_config=genai.GenerationConfig(
                        temperature=0.15,
                        max_output_tokens=32000,  # Increased for large responses
                        response_mime_type="application/json"
                    )
                )
                
                result = self._parse_json_response(response.text)
                
                if 'financial_data' in result:
                    all_financial_data[year] = result['financial_data']
                    logger.info(f"    ✓ Extracted financial data")
                else:
                    all_financial_data[year] = {"error": "No data"}
                
                if 'red_flags' in result:
                    year_flags = result['red_flags']
                    # Only keep flags from latest year to avoid duplicates
                    if idx == len(uploaded_files) - 1:  # Last year only
                        all_red_flags.extend(year_flags)
                        triggered = sum(1 for f in year_flags if f.get('is_triggered'))
                        logger.info(f"    ✓ Checked {len(year_flags)} flags ({triggered} triggered)")
                    else:
                        logger.info(f"    ✓ Checked flags (will use latest year)")
                
            except Exception as e:
                logger.error(f"Failed: {str(e)}")
                all_financial_data[year] = {"error": str(e)}
        
        # === CALL 4: Multi-Year Trends (using extracted data, NOT PDFs) ===
        logger.info(f"  Call 4/4: Checking multi-year trend flags...")
        
        trend_flags = [1, 9, 11, 13, 15, 18, 25, 26, 27, 35, 38, 41, 42, 45, 46, 50, 51]
        
        try:
            trend_prompt = f"""
# MULTI-YEAR TREND ANALYSIS

Years: {', '.join(years)}

Financial data (extracted):
{json.dumps(all_financial_data, indent=2)[:8000]}  

Check TREND FLAGS (require YoY comparison):

1. Auditor changes (2+ years)
9. CFO declining trend
11. CFO < Profit persistently
13. Asset turnover declining
15. Cash conversion worsening
18. RPT increasing trend
25. Pledging >50% AND increasing
26. Pledging % growing
27. Promoter stake declining
35. Audit committee changes
38. Disclosures worsening
41. D/E >2 AND increasing
42. Leverage increasing
45. Net worth negative/worsening
46. Intangibles growing
50. Margins declining
51. Revenue volatility

Return: {{"red_flags": [array of trend flag results]}}
"""
            
            response = self.model.generate_content(
                [trend_prompt],  # NO PDFs, just extracted data
                generation_config=genai.GenerationConfig(
                    temperature=0.2,
                    max_output_tokens=8000,
                    response_mime_type="application/json"
                )
            )
            
            result = self._parse_json_response(response.text)
            
            if 'red_flags' in result and isinstance(result['red_flags'], list):
                # Remove duplicates and add trend flags
                for flag in result['red_flags']:
                    if not isinstance(flag, dict):
                        continue  # Skip non-dict items
                    
                    flag_num = flag.get('flag_number')
                    if flag_num:
                        # Remove old version if exists
                        all_red_flags = [f for f in all_red_flags if isinstance(f, dict) and f.get('flag_number') != flag_num]
                        all_red_flags.append(flag)
                
                logger.info(f"    ✓ Checked {len(result['red_flags'])} trend flags")
        
        except Exception as e:
            logger.error(f"Multi-year analysis failed: {str(e)}")
        
        # Fill missing flags
        existing_nums = {f.get('flag_number') for f in all_red_flags if isinstance(f, dict) and f.get('flag_number')}
        for i in range(1, 55):
            if i not in existing_nums:
                all_red_flags.append(create_red_flag_result(
                    flag_number=i,
                    flag_name=f"Flag {i}",
                    category="UNKNOWN",
                    severity="MEDIUM",
                    is_triggered=False,
                    confidence_score=0,
                    evidence_text="Not analyzed",
                    page_references=[],
                    extracted_data={}
                ))
        
        all_red_flags.sort(key=lambda x: x.get('flag_number', 999))
        triggered = sum(1 for f in all_red_flags if f.get('is_triggered'))
        logger.info(f"✓ Complete: {len(all_red_flags)} flags, {triggered} triggered")
        
        return all_financial_data, all_red_flags
    
    def calculate_risk_scores(self, red_flags: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Calculate overall and category-wise risk scores.
        
        Uses the weighted scoring algorithm from the current system.
        """
        # Normalize category names (Gemini returns CASHFLOW, we need CASH_FLOW)
        CATEGORY_MAPPING = {
            'CASHFLOW': 'CASH_FLOW',
            'RELATEDPARTY': 'RELATED_PARTY',
            'RELATED_PARTY_TRANSACTIONS': 'RELATED_PARTY',
            'RPT': 'RELATED_PARTY',
            'BALANCESHEET': 'BALANCE_SHEET',
            'BALANCE': 'BALANCE_SHEET'
        }
        
        # Group flags by category
        category_flags = {}
        for category_name in CATEGORIES.keys():
            category_flags[category_name] = []
        
        for flag in red_flags:
            cat = flag.get('category', 'UNKNOWN').upper().replace(' ', '_')
            # Normalize category name
            cat = CATEGORY_MAPPING.get(cat, cat)
            
            if cat in category_flags:
                category_flags[cat].append(flag)
            else:
                logger.warning(f"Unknown category: {cat} for flag {flag.get('flag_number')}")
        
        # Calculate category scores
        category_scores = {}
        
        for category_name, category_info in CATEGORIES.items():
            flags = category_flags.get(category_name, [])
            
            if not flags:
                category_scores[category_name.lower().replace('_', '_')] = 0
                continue
            
            # Calculate max possible points for this category
            max_points = sum(
                SEVERITY_POINTS.get(flag.get('severity', 'MEDIUM'), 8)
                for flag in flags
            )
            
            # Calculate actual points (only count triggered flags)
            actual_points = sum(
                SEVERITY_POINTS.get(flag.get('severity', 'MEDIUM'), 8)
                for flag in flags
                if flag.get('is_triggered', False)
            )
            
            # Category score (0-100)
            category_score = (actual_points / max_points * 100) if max_points > 0 else 0
            category_scores[category_name.lower()] = round(category_score, 1)
        
        # Calculate overall risk score (weighted average)
        overall_risk_score = 0
        for category_name, category_info in CATEGORIES.items():
            weight = category_info['weight']
            score = category_scores.get(category_name.lower(), 0)
            overall_risk_score += weight * score
        
        overall_risk_score = round(overall_risk_score, 1)
        
        # Determine risk level
        risk_level = "LOW"
        for min_score, max_score, level in RISK_LEVELS:
            if min_score <= overall_risk_score < max_score:
                risk_level = level
                break
        
        # Count triggered flags
        flags_triggered = sum(1 for flag in red_flags if flag.get('is_triggered', False))
        
        return {
            'risk_score': int(overall_risk_score),
            'risk_level': risk_level,
            'category_scores': category_scores,
            'flags_triggered': flags_triggered
        }
    
    def _parse_json_response(self, response_text: str) -> Dict[str, Any]:
        """
        Parse JSON from Gemini response.
        
        Handles markdown code blocks and cleans response.
        """
        # Remove markdown code blocks if present
        text = response_text.strip()
        
        if text.startswith('```json'):
            text = text[7:]  # Remove ```json
        elif text.startswith('```'):
            text = text[3:]  # Remove ```
        
        if text.endswith('```'):
            text = text[:-3]  # Remove trailing ```
        
        text = text.strip()
        
        try:
            return json.loads(text)
        except json.JSONDecodeError as e:
            logger.warning(f"JSON parsing failed: {e}")
            
            # Try to extract and fix JSON
            import re
            
            # Find JSON object (may be incomplete)
            json_match = re.search(r'\{.*', text, re.DOTALL)
            if json_match:
                json_str = json_match.group(0)
                
                # Remove unterminated strings (lines with unclosed quotes)
                lines = json_str.split('\n')
                fixed_lines = []
                
                for line in lines:
                    stripped = line.rstrip()
                    if not stripped:
                        continue
                    
                    # Count quotes to detect unterminated strings
                    # Skip line if it has odd quotes (unterminated)
                    quote_count = stripped.count('"') - stripped.count('\\"')
                    
                    if quote_count % 2 != 0:
                        # Unterminated string, skip this line
                        logger.debug(f"Skipping unterminated line: {line[:50]}")
                        continue
                    
                    fixed_lines.append(line)
                
                json_str = '\n'.join(fixed_lines)
                
                # Add missing closing characters
                open_braces = json_str.count('{') - json_str.count('}')
                open_brackets = json_str.count('[') - json_str.count(']')
                
                if open_brackets > 0:
                    json_str += ']' * open_brackets
                if open_braces > 0:
                    json_str += '}' * open_braces
                
                try:
                    logger.info("Successfully recovered partial JSON")
                    return json.loads(json_str)
                except:
                    pass
            
            # Last resort: return error dict
            logger.error(f"Could not parse or recover JSON. First 500 chars: {text[:500]}")
            return {"error": "JSON parsing failed", "raw_response": text[:1000]}
