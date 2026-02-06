"""Section detection using Google Gemini LLM."""

import json
import logging
from typing import Dict, List, Optional

from app.llm.gemini_client import gemini_client
from app.llm.prompts import SECTION_DETECTION_PROMPT

logger = logging.getLogger(__name__)


class SectionDetector:
    """Detect financial statement sections in annual reports using LLM."""

    # Standard sections to detect
    STANDARD_SECTIONS = [
        "auditor_report",
        "directors_report",
        "corporate_governance",
        "balance_sheet",
        "profit_loss_statement",
        "cash_flow_statement",
        "notes_to_accounts",
        "related_party_transactions",
        "management_discussion_analysis",
    ]

    def __init__(self):
        """Initialize section detector."""
        self.max_pages_for_detection = 50  # Analyze first 50 pages for TOC

    def detect_sections(
        self, full_text: str, pages_data: List[Dict], total_pages: int
    ) -> Dict[str, Dict[str, int]]:
        """
        Detect section page ranges in an annual report.

        Args:
            full_text: Full extracted text from PDF
            pages_data: List of page-level data
            total_pages: Total number of pages in PDF

        Returns:
            Dict mapping section names to page ranges:
            {
                "auditor_report": {"start": 12, "end": 15},
                "balance_sheet": {"start": 45, "end": 47},
                ...
            }
        """
        try:
            logger.info(f"Detecting sections in {total_pages}-page document")

            # Step 1: Extract text from first 50 pages (usually contains TOC)
            sample_text = self._extract_sample_text(pages_data)

            # Step 2: Use LLM to detect section page ranges
            sections = self._detect_with_llm(sample_text, total_pages)

            # Step 3: Refine boundaries by checking actual content
            refined_sections = self._refine_boundaries(sections, pages_data)

            logger.info(f"Detected {len(refined_sections)} sections")
            return refined_sections

        except Exception as e:
            logger.error(f"Section detection failed: {e}", exc_info=True)
            # Return empty dict on failure
            return {}

    def _extract_sample_text(self, pages_data: List[Dict]) -> str:
        """Extract text from first N pages for section detection."""
        sample_pages = pages_data[: self.max_pages_for_detection]

        text_parts = []
        for page_data in sample_pages:
            page_num = page_data["page_number"]
            text = page_data["text"]
            text_parts.append(f"--- Page {page_num} ---\n{text[:500]}\n")  # First 500 chars per page

        return "\n".join(text_parts)

    def _detect_with_llm(self, sample_text: str, total_pages: int) -> Dict[str, Dict[str, int]]:
        """
        Use Gemini LLM to detect section page ranges.

        Returns:
            Dict with section names and page ranges
        """
        try:
            # Build prompt with sample text
            prompt = SECTION_DETECTION_PROMPT.format(
                sample_text=sample_text,
                total_pages=total_pages,
                sections=", ".join(self.STANDARD_SECTIONS),
            )

            # Call Gemini
            response_text = gemini_client.generate_text(
                prompt=prompt,
                max_tokens=2000,
                temperature=0.1,  # Low temperature for factual extraction
            )

            logger.debug(f"LLM response: {response_text}")

            # Parse JSON response
            sections = self._parse_llm_response(response_text)

            return sections

        except Exception as e:
            logger.error(f"LLM section detection failed: {e}")
            return {}

    def _parse_llm_response(self, response_text: str) -> Dict[str, Dict[str, int]]:
        """
        Parse LLM response to extract section page ranges.

        Expected format:
        {
            "auditor_report": {"start": 12, "end": 15},
            "balance_sheet": {"start": 45, "end": 47}
        }
        """
        try:
            # Try to extract JSON from response
            # LLM might include markdown code blocks
            if "```json" in response_text:
                json_start = response_text.find("```json") + 7
                json_end = response_text.find("```", json_start)
                json_text = response_text[json_start:json_end].strip()
            elif "```" in response_text:
                json_start = response_text.find("```") + 3
                json_end = response_text.find("```", json_start)
                json_text = response_text[json_start:json_end].strip()
            else:
                json_text = response_text.strip()

            # Parse JSON
            sections = json.loads(json_text)

            # Validate structure
            validated_sections = {}
            for section_name, page_range in sections.items():
                if isinstance(page_range, dict) and "start" in page_range and "end" in page_range:
                    start = int(page_range["start"])
                    end = int(page_range["end"])

                    if start > 0 and end >= start:
                        validated_sections[section_name] = {"start": start, "end": end}
                    else:
                        logger.warning(f"Invalid page range for {section_name}: {page_range}")

            return validated_sections

        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse LLM JSON response: {e}")
            logger.debug(f"Response text: {response_text}")
            return {}
        except Exception as e:
            logger.error(f"Failed to parse LLM response: {e}")
            return {}

    def _refine_boundaries(
        self, sections: Dict[str, Dict[str, int]], pages_data: List[Dict]
    ) -> Dict[str, Dict[str, int]]:
        """
        Refine section boundaries by checking actual page content.

        This is a placeholder for more sophisticated boundary refinement.
        """
        # For now, just return the LLM-detected sections
        # Future improvement: Use keywords to verify section starts/ends
        refined = {}

        for section_name, page_range in sections.items():
            start = page_range["start"]
            end = page_range["end"]

            # Validate against total pages
            if start <= len(pages_data) and end <= len(pages_data):
                refined[section_name] = page_range
            else:
                logger.warning(
                    f"Section {section_name} exceeds page count: {start}-{end} (total: {len(pages_data)})"
                )

        return refined

    def extract_section_text(
        self, section_name: str, sections: Dict[str, Dict[str, int]], pages_data: List[Dict]
    ) -> Optional[str]:
        """
        Extract text from a specific section.

        Args:
            section_name: Name of the section to extract
            sections: Dict of detected sections with page ranges
            pages_data: List of page-level data

        Returns:
            Extracted text from the section, or None if section not found
        """
        if section_name not in sections:
            logger.warning(f"Section '{section_name}' not found")
            return None

        page_range = sections[section_name]
        start = page_range["start"]
        end = page_range["end"]

        # Extract text from page range (1-indexed)
        text_parts = []
        for page_data in pages_data:
            page_num = page_data["page_number"]
            if start <= page_num <= end:
                text_parts.append(f"--- Page {page_num} ---\n{page_data['text']}\n")

        return "\n".join(text_parts)


# Singleton instance
section_detector = SectionDetector()
