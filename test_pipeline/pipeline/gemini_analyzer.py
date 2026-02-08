"""Gemini Flash PDF analyzer - sends sliced PDF directly to Gemini."""

import json
import logging
import os
import tempfile
import time
from typing import Dict, Optional

import google.generativeai as genai

from pipeline.prompts import (
    FINANCIAL_DATA_EXTRACTION_PROMPT,
    QUALITATIVE_ANALYSIS_PROMPT,
    TEXTUAL_ANALYSIS_PROMPT,
    SECTION_DETECTION_FALLBACK_PROMPT,
)

logger = logging.getLogger(__name__)


class GeminiAnalyzer:
    """Analyze annual report PDFs using Gemini Flash with native PDF support."""

    def __init__(self, api_key: Optional[str] = None):
        """Initialize Gemini client."""
        key = api_key or os.getenv("GEMINI_API_KEY", "")
        if not key:
            raise ValueError("GEMINI_API_KEY environment variable is required")

        genai.configure(api_key=key)

        # Use Gemini 2.5 Flash (latest) - good accuracy, fast, cheap
        self.model_name = "models/gemini-2.5-flash"
        try:
            self.model = genai.GenerativeModel(self.model_name)
            logger.info(f"Gemini initialized with model: {self.model_name}")
        except Exception as e:
            logger.warning(f"Failed to init {self.model_name}: {e}. Trying gemini-2.0-flash...")
            self.model_name = "models/gemini-2.0-flash"
            self.model = genai.GenerativeModel(self.model_name)

    def analyze_pdf(
        self,
        pdf_bytes: bytes,
        sections_description: str = "",
        financial_summary: str = "",
    ) -> Dict:
        """
        Run full analysis on a PDF using 3 Gemini calls.

        Returns combined analysis data suitable for red flag checks.
        """
        # Upload PDF to Gemini
        uploaded_file = self._upload_pdf(pdf_bytes)

        if not uploaded_file:
            raise Exception("Failed to upload PDF to Gemini")

        logger.info("PDF uploaded to Gemini. Running analysis calls...")

        results = {}

        # Call 1: Financial data extraction
        logger.info("Call 1/3: Extracting financial data...")
        t1 = time.time()
        financial_data = self._call_financial_extraction(uploaded_file, sections_description)
        logger.info(f"Call 1 done in {time.time() - t1:.1f}s")
        results["financial_data"] = financial_data

        # Call 2: Qualitative analysis (auditor + RPT + governance)
        logger.info("Call 2/3: Qualitative analysis...")
        t2 = time.time()
        qualitative_data = self._call_qualitative_analysis(uploaded_file, sections_description)
        logger.info(f"Call 2 done in {time.time() - t2:.1f}s")

        # Merge qualitative into financial_data
        if "auditor_analysis" in qualitative_data:
            results["financial_data"]["auditor_analysis"] = qualitative_data["auditor_analysis"]
        if "related_party_transactions" in qualitative_data:
            results["financial_data"]["related_party_transactions"] = qualitative_data["related_party_transactions"]
        if "governance" in qualitative_data:
            results["financial_data"]["governance"] = qualitative_data["governance"]

        # Call 3: Textual analysis (tone, contradictions, language)
        logger.info("Call 3/3: Textual analysis...")
        t3 = time.time()
        textual_data = self._call_textual_analysis(
            uploaded_file, sections_description, financial_summary
        )
        logger.info(f"Call 3 done in {time.time() - t3:.1f}s")
        results["textual_analysis"] = textual_data

        # Cleanup uploaded file
        try:
            genai.delete_file(uploaded_file.name)
        except Exception:
            pass

        return results

    def detect_sections_fallback(
        self, pdf_bytes: bytes, pages_sample: str, total_pages: int
    ) -> Dict:
        """Fallback: Use Gemini to detect section page ranges when regex fails."""
        uploaded_file = self._upload_pdf(pdf_bytes)
        if not uploaded_file:
            return {}

        prompt = SECTION_DETECTION_FALLBACK_PROMPT.format(
            sample_text=pages_sample, total_pages=total_pages
        )

        response_text = self._generate(uploaded_file, prompt)
        result = self._parse_json(response_text)

        try:
            genai.delete_file(uploaded_file.name)
        except Exception:
            pass

        return result

    def _upload_pdf(self, pdf_bytes: bytes):
        """Upload PDF bytes to Gemini file API."""
        try:
            # Write to temp file
            with tempfile.NamedTemporaryFile(suffix=".pdf", delete=False) as f:
                f.write(pdf_bytes)
                temp_path = f.name

            # Upload to Gemini
            uploaded_file = genai.upload_file(temp_path, mime_type="application/pdf")

            # Wait for processing
            while uploaded_file.state.name == "PROCESSING":
                time.sleep(1)
                uploaded_file = genai.get_file(uploaded_file.name)

            if uploaded_file.state.name != "ACTIVE":
                logger.error(f"File upload failed. State: {uploaded_file.state.name}")
                return None

            logger.info(f"PDF uploaded: {uploaded_file.name}")

            # Clean up temp file
            os.unlink(temp_path)

            return uploaded_file

        except Exception as e:
            logger.error(f"PDF upload failed: {e}", exc_info=True)
            return None

    def _generate(self, uploaded_file, prompt: str, temperature: float = 0.1) -> str:
        """Generate content with PDF context."""
        try:
            generation_config = {
                "max_output_tokens": 8192,
                "temperature": temperature,
            }

            response = self.model.generate_content(
                [uploaded_file, prompt],
                generation_config=generation_config,
            )

            try:
                return response.text
            except (ValueError, AttributeError):
                if response.candidates and len(response.candidates) > 0:
                    candidate = response.candidates[0]
                    if hasattr(candidate, "content") and hasattr(candidate.content, "parts"):
                        if len(candidate.content.parts) > 0:
                            return candidate.content.parts[0].text
                return ""

        except Exception as e:
            logger.error(f"Gemini generation failed: {e}", exc_info=True)
            return ""

    def _call_financial_extraction(self, uploaded_file, sections_desc: str) -> Dict:
        """Call 1: Extract financial metrics."""
        prompt = FINANCIAL_DATA_EXTRACTION_PROMPT.format(
            section_pages_description=sections_desc or "Full annual report PDF attached."
        )

        response_text = self._generate(uploaded_file, prompt)
        data = self._parse_json(response_text)

        # Ensure required top-level keys exist
        for key in ["balance_sheet", "profit_loss", "cash_flow", "notes", "shareholding_pattern"]:
            if key not in data:
                data[key] = {}

        return data

    def _call_qualitative_analysis(self, uploaded_file, sections_desc: str) -> Dict:
        """Call 2: Auditor + RPT + Governance analysis."""
        prompt = QUALITATIVE_ANALYSIS_PROMPT.format(
            section_pages_description=sections_desc or "Full annual report PDF attached."
        )

        response_text = self._generate(uploaded_file, prompt)
        data = self._parse_json(response_text)

        # Ensure required keys
        for key in ["auditor_analysis", "related_party_transactions", "governance"]:
            if key not in data:
                data[key] = {}

        return data

    def _call_textual_analysis(
        self, uploaded_file, sections_desc: str, financial_summary: str
    ) -> Dict:
        """Call 3: Textual/tone analysis."""
        prompt = TEXTUAL_ANALYSIS_PROMPT.format(
            section_pages_description=sections_desc or "Full annual report PDF attached.",
            financial_summary=financial_summary or "Not available.",
        )

        response_text = self._generate(uploaded_file, prompt)
        data = self._parse_json(response_text)

        # Ensure required keys
        for key in ["mda_tone", "contradictions", "risk_factors", "unusual_audit_language", "disclosure_quality"]:
            if key not in data:
                data[key] = {}

        return data

    def _parse_json(self, response_text: str) -> Dict:
        """Parse JSON from LLM response, handling markdown blocks."""
        if not response_text:
            return {}

        try:
            # Remove markdown code blocks
            text = response_text.strip()
            if "```json" in text:
                start = text.find("```json") + 7
                end = text.find("```", start)
                text = text[start:end].strip()
            elif "```" in text:
                start = text.find("```") + 3
                end = text.find("```", start)
                text = text[start:end].strip()

            return json.loads(text)

        except json.JSONDecodeError as e:
            logger.error(f"JSON parse failed: {e}")
            logger.debug(f"Response: {response_text[:500]}")
            return {}
