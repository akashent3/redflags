"""Gemini API integration for 27 PDF-based flags."""

import logging
import os
import time
import json
import re
from typing import Dict, List, Optional
from datetime import datetime
import google.generativeai as genai

logger = logging.getLogger(__name__)


class GeminiService:
    """Service for analyzing PDFs with Gemini API and extracting 27 flags."""
    
    def __init__(self, api_key: Optional[str] = None, model_name: Optional[str] = None):
        """Initialize Gemini service."""
        self.api_key = api_key or os.getenv("GEMINI_API_KEY", "")
        self.model_name = model_name or os.getenv("GEMINI_MODEL", "gemini-2.0-flash-exp")
        
        if not self.api_key:
            raise ValueError("GEMINI_API_KEY is required")
        
        genai.configure(api_key=self.api_key)
        
    def _load_prompt(self, symbol: str, fiscal_year: int) -> str:
        """Load and format the Gemini prompt template."""
        try:
            prompt_path = os.path.join(
                os.path.dirname(__file__),
                "../prompts/gemini_prompt.txt"
            )
            
            with open(prompt_path, 'r', encoding='utf-8') as f:
                template = f.read()
            
            # Replace placeholders
            prompt = template.replace("{SYMBOL}", symbol)
            prompt = prompt.replace("{FISCAL_YEAR}", str(fiscal_year))
            
            return prompt
            
        except FileNotFoundError:
            logger.error(f"Prompt template not found: {prompt_path}")
            return self._get_default_prompt(symbol, fiscal_year)
        except Exception as e:
            logger.error(f"Error loading prompt: {e}")
            return self._get_default_prompt(symbol, fiscal_year)
    
    def _get_default_prompt(self, symbol: str, fiscal_year: int) -> str:
        """Return default prompt if template not found."""
        return f"""Analyze the annual report for {symbol} (FY{fiscal_year}) and extract information for 27 red flags.

CRITICAL INSTRUCTION: Use ONLY CONSOLIDATED financial statements if available. Only if consolidated statements are NOT available, use standalone statements. Explicitly state which type was used.

Return valid JSON only (no markdown code blocks) with this exact structure:
{{
  "statement_type": "consolidated" or "standalone",
  "fiscal_year": {fiscal_year},
  "flags": [array of 27 flag objects]
}}"""
    
    def analyze_pdf(self, pdf_path: str, symbol: str, fiscal_year: int) -> Dict:
        """Analyze PDF using Gemini API."""
        try:
            # Upload file
            logger.info(f"Uploading PDF to Gemini: {pdf_path}")
            with open(pdf_path, 'rb') as f:
                uploaded_file = genai.upload_file(f, mime_type='application/pdf')
            
            logger.info(f"Uploaded file: {uploaded_file.name}")
            
            # Wait for file processing
            logger.info("Waiting for PDF processing...")
            max_wait = 120  # 2 minutes max
            wait_time = 0
            while uploaded_file.state.name == "PROCESSING":
                if wait_time >= max_wait:
                    raise Exception("PDF processing timeout")
                time.sleep(2)
                wait_time += 2
                uploaded_file = genai.get_file(uploaded_file.name)
            
            if uploaded_file.state.name == "FAILED":
                raise Exception(f"File processing failed: {uploaded_file.state}")
            
            # Load prompt
            prompt = self._load_prompt(symbol, fiscal_year)
            
            # Call Gemini API
            logger.info("Calling Gemini API for analysis...")
            model = genai.GenerativeModel(self.model_name)
            
            # Configure generation to get longer responses and JSON output
            generation_config = {
                "temperature": 0.1,
                "max_output_tokens": 8192,
                "response_mime_type": "application/json",  # Force JSON output
            }
            
            response = model.generate_content(
                [uploaded_file, prompt],
                generation_config=generation_config,
                request_options={"timeout": 300}  # 5 minutes timeout
            )
            
            # Clean up uploaded file
            try:
                genai.delete_file(uploaded_file.name)
                logger.info("Cleaned up uploaded file")
            except:
                pass
            
            # Extract and parse JSON from response
            response_text = response.text.strip()
            
            # Remove markdown code blocks if present
            if "```json" in response_text:
                start = response_text.find("```json") + 7
                end = response_text.rfind("```")
                if end > start:
                    response_text = response_text[start:end].strip()
            elif "```" in response_text:
                start = response_text.find("```") + 3
                end = response_text.rfind("```")
                if end > start:
                    response_text = response_text[start:end].strip()
            
            # Try to parse JSON
            try:
                result = json.loads(response_text)
                
                # Validate structure
                if not isinstance(result, dict):
                    raise ValueError("Response is not a dictionary")
                
                if "flags" not in result:
                    raise ValueError("Response missing 'flags' key")
                
                flags = result.get("flags", [])
                logger.info(f"Successfully parsed Gemini response with {len(flags)} flags")
                
                # Ensure we have 27 flags (fill missing ones with defaults)
                if len(flags) < 27:
                    logger.warning(f"Only {len(flags)} flags returned, expected 27")
                    existing_ids = {f.get("flag_id") for f in flags}
                    default_flags = self._get_default_flags("Not analyzed by Gemini")
                    
                    for default_flag in default_flags:
                        if default_flag["flag_id"] not in existing_ids:
                            flags.append(default_flag)
                    
                    result["flags"] = flags[:27]  # Cap at 27
                
                return result
                
            except json.JSONDecodeError as e:
                logger.error(f"JSON parsing error: {e}")
                logger.error(f"Response text (first 2000 chars): {response_text[:2000]}")
                
                # Try to fix common JSON issues
                response_text = self._fix_json(response_text)
                
                try:
                    result = json.loads(response_text)
                    logger.info(f"Successfully parsed after JSON fix with {len(result.get('flags', []))} flags")
                    return result
                except json.JSONDecodeError as e2:
                    logger.error(f"JSON parsing failed after fix: {e2}")
                    logger.error(f"Problematic JSON: {response_text[:1000]}")
                    
                    # Return default flags
                    return self._get_default_response(
                        symbol, 
                        fiscal_year,
                        f"Failed to parse Gemini response: {str(e2)}"
                    )
        
        except Exception as e:
            logger.error(f"Gemini API error: {e}")
            import traceback
            logger.error(traceback.format_exc())
            return self._get_default_response(symbol, fiscal_year, str(e))
    
    def _fix_json(self, json_text: str) -> str:
        """Attempt to fix common JSON formatting issues."""
        # Remove trailing commas before closing braces/brackets
        json_text = re.sub(r',(\s*[}\]])', r'\1', json_text)
        
        # Fix incomplete strings (add closing quote if missing)
        lines = json_text.split('\n')
        fixed_lines = []
        
        for line in lines:
            # If line has opening quote but no closing quote, try to fix
            if line.count('"') % 2 == 1:
                # Check if it's a value line
                if '":' in line:
                    # Add closing quote before comma or brace
                    if line.rstrip().endswith(','):
                        line = line.rstrip()[:-1] + '",'
                    else:
                        line = line.rstrip() + '"'
            fixed_lines.append(line)
        
        return '\n'.join(fixed_lines)
    
    def _get_default_response(self, symbol: str, fiscal_year: int, reason: str) -> Dict:
        """Return default response when Gemini fails."""
        return {
            "statement_type": "unknown",
            "fiscal_year": fiscal_year,
            "flags": self._get_default_flags(reason),
            "metadata": {
                "total_flags_analyzed": 27,
                "total_flags_triggered": 0,
                "analysis_timestamp": datetime.now().isoformat(),
                "error": reason
            }
        }
    
    def _get_default_flags(self, reason: str) -> List[Dict]:
        """Return all 27 default Gemini flags."""
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
                "evidence": reason,
                "page_references": [],
                "confidence": 0,
                "value": None
            }
            for fid, name, cat, sev in flag_definitions
        ]