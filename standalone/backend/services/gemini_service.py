"""Gemini API integration for PDF analysis and 28 flags extraction."""

import json
import logging
import os
import time
from typing import Dict, List, Optional

import google.generativeai as genai

logger = logging.getLogger(__name__)


class GeminiService:
    """Service for analyzing PDFs using Gemini API and extracting 28 flags."""
    
    def __init__(self, api_key: Optional[str] = None, model: Optional[str] = None):
        """Initialize Gemini service."""
        key = api_key or os.getenv("GEMINI_API_KEY", "")
        if not key:
            raise ValueError("GEMINI_API_KEY is required")
        
        genai.configure(api_key=key)
        
        self.model_name = model or os.getenv("GEMINI_MODEL", "models/gemini-2.0-flash-exp")
        
        try:
            self.model = genai.GenerativeModel(self.model_name)
            logger.info(f"Gemini initialized with model: {self.model_name}")
        except Exception as e:
            logger.warning(f"Failed to init {self.model_name}: {e}. Trying gemini-2.0-flash...")
            self.model_name = "models/gemini-2.0-flash"
            self.model = genai.GenerativeModel(self.model_name)
    
    def analyze_pdf(self, pdf_path: str, fiscal_year: int) -> Dict:
        """
        Analyze PDF and extract 28 Gemini-based flags.
        
        Args:
            pdf_path: Path to PDF file
            fiscal_year: Fiscal year for context
            
        Returns:
            Dictionary with flags list and metadata
        """
        try:
            # Read PDF
            with open(pdf_path, 'rb') as f:
                pdf_bytes = f.read()
            
            # Upload PDF to Gemini
            logger.info(f"Uploading PDF to Gemini: {pdf_path}")
            uploaded_file = self._upload_pdf(pdf_bytes, os.path.basename(pdf_path))
            
            if not uploaded_file:
                raise Exception("Failed to upload PDF to Gemini")
            
            # Wait for file to be processed
            logger.info("Waiting for PDF processing...")
            time.sleep(2)
            
            # Load prompt template
            prompt = self._load_prompt_template(fiscal_year)
            
            # Call Gemini API
            logger.info("Calling Gemini API for analysis...")
            response = self._call_gemini(uploaded_file, prompt)
            
            # Parse response
            result = self._parse_response(response, fiscal_year)
            
            # Cleanup
            try:
                genai.delete_file(uploaded_file.name)
                logger.info("Cleaned up uploaded file")
            except Exception:
                pass
            
            return result
            
        except Exception as e:
            logger.error(f"Error analyzing PDF with Gemini: {e}")
            return self._get_default_result(fiscal_year, str(e))
    
    def _upload_pdf(self, pdf_bytes: bytes, filename: str) -> Optional[object]:
        """Upload PDF to Gemini File API."""
        try:
            # Save to temp file for upload
            import tempfile
            with tempfile.NamedTemporaryFile(delete=False, suffix='.pdf') as tmp_file:
                tmp_file.write(pdf_bytes)
                tmp_path = tmp_file.name
            
            # Upload to Gemini
            uploaded_file = genai.upload_file(tmp_path, display_name=filename)
            logger.info(f"Uploaded file: {uploaded_file.name}")
            
            # Cleanup temp file
            os.unlink(tmp_path)
            
            return uploaded_file
            
        except Exception as e:
            logger.error(f"Error uploading PDF: {e}")
            return None
    
    def _load_prompt_template(self, fiscal_year: int) -> str:
        """Load Gemini prompt template."""
        try:
            prompt_path = os.path.join(
                os.path.dirname(__file__),
                "../prompts/gemini_prompt.txt"
            )
            
            with open(prompt_path, 'r') as f:
                prompt = f.read()
            
            return prompt
            
        except Exception as e:
            logger.error(f"Error loading prompt template: {e}")
            raise
    
    def _call_gemini(self, uploaded_file: object, prompt: str) -> str:
        """Call Gemini API with uploaded file and prompt."""
        try:
            # Generate content
            response = self.model.generate_content(
                [uploaded_file, prompt],
                generation_config={
                    "temperature": 0.1,  # Low temperature for consistent output
                    "max_output_tokens": 8000,
                }
            )
            
            return response.text
            
        except Exception as e:
            logger.error(f"Error calling Gemini API: {e}")
            raise
    
    def _parse_response(self, response_text: str, fiscal_year: int) -> Dict:
        """Parse Gemini JSON response."""
        try:
            # Extract JSON from response (in case there's extra text)
            # Find first { and last }
            start_idx = response_text.find('{')
            end_idx = response_text.rfind('}')
            
            if start_idx == -1 or end_idx == -1:
                raise ValueError("No JSON found in response")
            
            json_text = response_text[start_idx:end_idx+1]
            data = json.loads(json_text)
            
            # Validate structure
            if "flags" not in data:
                raise ValueError("Missing 'flags' in response")
            
            if not isinstance(data["flags"], list):
                raise ValueError("'flags' must be a list")
            
            # Ensure all 28 flags are present
            flags = data["flags"]
            if len(flags) != 28:
                logger.warning(f"Expected 28 flags, got {len(flags)}")
            
            # Add default metadata if missing
            if "metadata" not in data:
                data["metadata"] = {}
            
            data["metadata"].update({
                "total_flags_analyzed": len(flags),
                "total_flags_triggered": sum(1 for f in flags if f.get("triggered", False)),
                "fiscal_year": fiscal_year
            })
            
            return data
            
        except json.JSONDecodeError as e:
            logger.error(f"JSON parsing error: {e}")
            logger.error(f"Response text: {response_text[:500]}")
            return self._get_default_result(fiscal_year, "Failed to parse Gemini response")
        except Exception as e:
            logger.error(f"Error parsing response: {e}")
            return self._get_default_result(fiscal_year, str(e))
    
    def _get_default_result(self, fiscal_year: int, error_msg: str) -> Dict:
        """Return default result with all 28 flags not triggered."""
        # Define all 28 Gemini-based flags
        flag_definitions = [
            # Auditor (6)
            (1, "Auditor Resignation Mid-Term", "Auditor", "CRITICAL"),
            (2, "Qualified/Adverse/Disclaimer Opinion", "Auditor", "CRITICAL"),
            (3, "Emphasis of Matter Paragraph", "Auditor", "HIGH"),
            (4, "Going Concern Issue", "Auditor", "CRITICAL"),
            (5, "KAM on Revenue Recognition", "Auditor", "HIGH"),
            (6, "Audit Fees Declining", "Auditor", "MEDIUM"),
            # Related Party (7)
            (15, "RPT > 10% of Revenue", "Related Party", "HIGH"),
            (16, "Loans to Related Parties", "Related Party", "HIGH"),
            (17, "Purchases from RP at Premium", "Related Party", "MEDIUM"),
            (18, "Revenue from RP Increasing", "Related Party", "MEDIUM"),
            (19, "Complex Structure > 20 Subsidiaries", "Related Party", "MEDIUM"),
            (20, "Loans to Directors/KMP", "Related Party", "HIGH"),
            (21, "New Related Parties Added", "Related Party", "MEDIUM"),
            # Promoter (3)
            (25, "Disproportionate Managerial Remuneration", "Promoter", "MEDIUM"),
            (26, "Promoter Entity Name Change", "Promoter", "LOW"),
            (27, "ICDs to Promoter Group", "Promoter", "HIGH"),
            # Governance (4)
            (28, "Independent Director Resignation", "Governance", "HIGH"),
            (29, "Related Party on Audit Committee", "Governance", "MEDIUM"),
            (30, "SEBI/Stock Exchange Penalties", "Governance", "HIGH"),
            (31, "Whistle-blower Complaints", "Governance", "MEDIUM"),
            # Balance Sheet (4)
            (34, "Short-term Debt > 60% of Total", "Balance Sheet", "HIGH"),
            (35, "Contingent Liabilities > 20% NW", "Balance Sheet", "HIGH"),
            (36, "Frequent Debt Restructuring", "Balance Sheet", "MEDIUM"),
            (37, "Heavy Asset Pledging", "Balance Sheet", "MEDIUM"),
            # Revenue Quality (2)
            (40, "Revenue Recognition Policy Changed", "Revenue Quality", "HIGH"),
            (41, "Unbilled Revenue Growing Faster", "Revenue Quality", "MEDIUM"),
            # Textual Analysis (1)
            (42, "MD&A Tone is Defensive", "Textual Analysis", "MEDIUM"),
        ]
        
        flags = [
            {
                "flag_id": fid,
                "flag_name": name,
                "category": category,
                "triggered": False,
                "severity": severity,
                "evidence": error_msg,
                "page_references": [],
                "confidence": 0,
                "value": None
            }
            for fid, name, category, severity in flag_definitions
        ]
        
        return {
            "statement_type": "unknown",
            "fiscal_year": fiscal_year,
            "flags": flags,
            "metadata": {
                "total_flags_analyzed": 28,
                "total_flags_triggered": 0,
                "error": error_msg
            }
        }
