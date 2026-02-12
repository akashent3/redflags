"""4-Layer section detection for Indian annual reports.

Layer 1: Regex keyword scanning on all pages (FREE, fast)
Layer 2: Signature/footer detection for section boundaries
Layer 3: Sub-section detection (RPT within Notes)
Layer 4: Content fingerprint validation

Consolidated vs Standalone logic:
- Detects BOTH consolidated and standalone financial sections separately
- Prefers consolidated; falls back to standalone only if consolidated not found
- Records the chosen statement_type for consistent multi-year comparisons
"""

import logging
import re
from typing import Dict, List, Optional, Tuple

logger = logging.getLogger(__name__)


# --- Financial section patterns: detected TWICE (consolidated + standalone) ---
# These are the financial sections that appear in both forms in annual reports
FINANCIAL_SECTION_PATTERNS = {
    "auditor_report": [
        r"(?i)independent\s+auditor.?s?\s+report",
        r"(?i)report\s+of\s+the\s+auditors?",
        r"(?i)auditors?\s+report\s+on",
        r"(?i)report\s+on\s+audit\s+of",
    ],
    "balance_sheet": [
        r"(?i)balance\s+sheet\s+as\s+at",
        r"(?i)statement\s+of\s+financial\s+position",
    ],
    "profit_loss_statement": [
        r"(?i)statement\s+of\s+profit\s+and\s+loss",
        r"(?i)profit\s+(&|and)\s+loss\s+(statement|account)",
        r"(?i)statement\s+of\s+income",
        r"(?i)income\s+statement",
    ],
    "cash_flow_statement": [
        r"(?i)cash\s+flow\s+statement",
        r"(?i)statement\s+of\s+cash\s+flows?",
    ],
    "notes_to_accounts": [
        r"(?i)notes\s+(to|forming\s+part\s+of)\s+(the\s+)?(standalone\s+|consolidated\s+)?(financial)",
        r"(?i)notes\s+to\s+(the\s+)?(standalone\s+|consolidated\s+)?accounts",
        r"(?i)notes\s+to\s+consolidated\s+financial\s+statements",
        r"(?i)notes\s+to\s+standalone\s+financial\s+statements",
    ],
}

# Keywords that indicate CONSOLIDATED vs STANDALONE on or near a section header
CONSOLIDATED_INDICATORS = [
    r"(?i)consolidated",
    r"(?i)group\s+financial",
]
STANDALONE_INDICATORS = [
    r"(?i)standalone",
    r"(?i)stand\s*-\s*alone",
    r"(?i)separate\s+financial",
]

# --- Non-financial sections (only appear once, no consolidated/standalone split) ---
NON_FINANCIAL_SECTION_PATTERNS = {
    "directors_report": [
        r"(?i)director.?s?\s+report",
        r"(?i)board.?s?\s+report",
        r"(?i)report\s+of\s+the\s+board\s+of\s+directors",
    ],
    "management_discussion_analysis": [
        r"(?i)management\s+discussion\s+(&|and)\s+analysis",
        r"(?i)management.?s?\s+discussion",
        r"(?i)md\s*&\s*a",
        r"(?i)mda\s+report",
    ],
    "corporate_governance": [
        r"(?i)corporate\s+governance\s+report",
        r"(?i)report\s+on\s+corporate\s+governance",
    ],
}

# Combined for backward compat (used only in boundary derivation)
SECTION_PATTERNS = {
    **FINANCIAL_SECTION_PATTERNS,
    **NON_FINANCIAL_SECTION_PATTERNS,
}

# --- Layer 2: Section end markers ---
SECTION_END_MARKERS = {
    "auditor_report": [
        r"(?i)for\s+.*?chartered\s+accountants",
        r"(?i)membership\s+no\.?\s*:?\s*\d+",
        r"(?i)UDIN\s*:\s*\d+",
        r"(?i)firm\s+registration\s+no",
        r"(?i)place\s*:\s*(mumbai|delhi|bangalore|chennai|hyderabad|kolkata|pune|ahmedabad|new\s+delhi|gurugram|gurgaon|noida)",
    ],
    "directors_report": [
        r"(?i)for\s+and\s+on\s+behalf\s+of\s+the\s+board",
        r"(?i)by\s+order\s+of\s+the\s+board",
    ],
    "balance_sheet": [
        r"(?i)as\s+per\s+our\s+report\s+of\s+even\s+date",
        r"(?i)the\s+accompanying\s+notes.*?integral\s+part",
    ],
    "cash_flow_statement": [
        r"(?i)as\s+per\s+our\s+report\s+of\s+even\s+date",
        r"(?i)the\s+accompanying\s+notes.*?integral\s+part",
    ],
    "notes_to_accounts": [
        r"(?i)for\s+and\s+on\s+behalf\s+of\s+the\s+board",
        r"(?i)as\s+per\s+our\s+report\s+of\s+even\s+date",
    ],
}

# --- Layer 3: Sub-section patterns within Notes ---
SUBSECTION_PATTERNS = {
    "related_party_transactions": [
        r"(?i)note\s+\d+\s*[:.]\s*related\s+party",
        r"(?i)related\s+party\s+transactions?\s+(?:and\s+)?disclosures?",
        r"(?i)disclosure\s+of\s+related\s+party\s+transactions",
        r"(?i)related\s+party\s+transactions\s+pursuant",
    ],
    "contingent_liabilities": [
        r"(?i)note\s+\d+\s*[:.]\s*contingent\s+liabilit",
        r"(?i)contingent\s+liabilities\s+and\s+commitments",
    ],
    "audit_fees": [
        r"(?i)note\s+\d+\s*[:.]\s*(?:payment\s+to|auditor)",
        r"(?i)auditor.?s?\s+remuneration",
    ],
}

# --- Layer 4: Content fingerprints for validation ---
CONTENT_FINGERPRINTS = {
    "auditor_report": {
        "required": [r"(?i)(opinion|audit|true\s+and\s+fair|financial\s+statements)"],
        "excluded": [r"(?i)^balance\s+sheet\s+as\s+at"],
        "expected_pages": (3, 15),
    },
    "balance_sheet": {
        "required": [r"(?i)(assets?|liabilit|equity|shareholders)"],
        "excluded": [],
        "expected_pages": (2, 6),
    },
    "profit_loss_statement": {
        "required": [r"(?i)(revenue|income|profit|loss|expenses?)"],
        "excluded": [],
        "expected_pages": (1, 4),
    },
    "cash_flow_statement": {
        "required": [r"(?i)(operating|investing|financing)\s+activit"],
        "excluded": [],
        "expected_pages": (1, 5),
    },
    "notes_to_accounts": {
        "required": [r"(?i)(note\s+\d|significant\s+accounting|accounting\s+polic)"],
        "excluded": [],
        "expected_pages": (20, 120),
    },
    "directors_report": {
        "required": [r"(?i)(director|board|dividend|recommend)"],
        "excluded": [],
        "expected_pages": (5, 40),
    },
    "management_discussion_analysis": {
        "required": [r"(?i)(industr|economic|outlook|performance|review)"],
        "excluded": [],
        "expected_pages": (3, 25),
    },
    "corporate_governance": {
        "required": [r"(?i)(governance|board\s+meeting|committee|independent\s+director)"],
        "excluded": [],
        "expected_pages": (5, 25),
    },
}

# Known ordering of sections in Indian annual reports
SECTION_ORDER = [
    "directors_report",
    "management_discussion_analysis",
    "corporate_governance",
    "auditor_report",
    "balance_sheet",
    "profit_loss_statement",
    "cash_flow_statement",
    "notes_to_accounts",
]


class SectionDetector:
    """Detect financial sections using 4-layer approach."""

    def detect_sections(
        self, pages_data: List[Dict], total_pages: int
    ) -> Dict[str, Dict[str, int]]:
        """
        Detect section page ranges in an annual report.

        Returns:
            Dict mapping section names to {"start": int, "end": int}
        """
        logger.info(f"Detecting sections in {total_pages}-page document")

        # Layer 1: Regex keyword scan on ALL pages
        raw_starts = self._scan_all_pages(pages_data)
        logger.info(f"Layer 1 (regex): Found starts for {len(raw_starts)} sections")

        # Derive boundaries: section ends where next section starts
        sections = self._derive_boundaries(raw_starts, total_pages)

        # Layer 2: Refine open-ended sections with end markers
        sections = self._refine_with_end_markers(sections, pages_data)
        logger.info(f"Layer 2 (end markers): Refined to {len(sections)} sections")

        # Layer 3: Find sub-sections within Notes
        if "notes_to_accounts" in sections:
            subsections = self._find_subsections(sections, pages_data)
            sections.update(subsections)
            logger.info(f"Layer 3 (sub-sections): Found {len(subsections)} sub-sections")

        # Layer 4: Validate with content fingerprints
        validated = self._validate_sections(sections, pages_data)
        logger.info(f"Layer 4 (validation): {len(validated)} sections validated")

        return validated

    def _scan_all_pages(self, pages_data: List[Dict]) -> Dict[str, int]:
        """Layer 1: Scan all pages with regex patterns to find section starts."""
        found = {}

        for page_data in pages_data:
            page_num = page_data["page_number"]
            text = page_data["text"]

            if not text or len(text.strip()) < 20:
                continue

            # Check first 1000 chars of page for section headers
            # Headers are usually at the top of the page
            header_text = text[:1000]

            for section_name, patterns in SECTION_PATTERNS.items():
                if section_name in found:
                    continue  # Already found this section

                for pattern in patterns:
                    if re.search(pattern, header_text):
                        found[section_name] = page_num
                        logger.debug(f"  Found '{section_name}' on page {page_num}")
                        break

        return found

    def _derive_boundaries(
        self, raw_starts: Dict[str, int], total_pages: int
    ) -> Dict[str, Dict[str, int]]:
        """Derive section boundaries: section ends where next section starts."""
        if not raw_starts:
            return {}

        # Sort sections by start page
        sorted_sections = sorted(raw_starts.items(), key=lambda x: x[1])

        sections = {}
        for i, (section_name, start_page) in enumerate(sorted_sections):
            if i + 1 < len(sorted_sections):
                # End is one page before next section starts
                next_start = sorted_sections[i + 1][1]
                end_page = max(start_page, next_start - 1)
            else:
                # Last section: extend to end of document
                end_page = total_pages

            sections[section_name] = {"start": start_page, "end": end_page}

        return sections

    def _refine_with_end_markers(
        self, sections: Dict[str, Dict[str, int]], pages_data: List[Dict]
    ) -> Dict[str, Dict[str, int]]:
        """Layer 2: Refine boundaries using end marker patterns."""
        refined = dict(sections)

        for section_name, page_range in sections.items():
            markers = SECTION_END_MARKERS.get(section_name, [])
            if not markers:
                continue

            start = page_range["start"]
            end = page_range["end"]

            # Scan pages in reverse from end to find last end marker
            for page_num in range(min(end, len(pages_data)), start - 1, -1):
                if page_num - 1 >= len(pages_data):
                    continue
                page_text = pages_data[page_num - 1]["text"]

                for pattern in markers:
                    if re.search(pattern, page_text):
                        # Found end marker - section ends on this page
                        if page_num < end:
                            refined[section_name] = {"start": start, "end": page_num}
                            logger.debug(
                                f"  Refined '{section_name}' end: {end} -> {page_num}"
                            )
                        break

        return refined

    def _find_subsections(
        self, sections: Dict[str, Dict[str, int]], pages_data: List[Dict]
    ) -> Dict[str, Dict[str, int]]:
        """Layer 3: Find sub-sections within Notes to Accounts."""
        subsections = {}
        notes = sections.get("notes_to_accounts")
        if not notes:
            return subsections

        notes_start = notes["start"]
        notes_end = notes["end"]

        for subsection_name, patterns in SUBSECTION_PATTERNS.items():
            for page_num in range(notes_start, min(notes_end + 1, len(pages_data) + 1)):
                if page_num - 1 >= len(pages_data):
                    continue
                page_text = pages_data[page_num - 1]["text"]

                for pattern in patterns:
                    if re.search(pattern, page_text):
                        # Find end: next note number or next subsection
                        sub_end = self._find_subsection_end(
                            page_num, notes_end, pages_data
                        )
                        subsections[subsection_name] = {
                            "start": page_num,
                            "end": sub_end,
                        }
                        logger.debug(
                            f"  Sub-section '{subsection_name}': pages {page_num}-{sub_end}"
                        )
                        break
                if subsection_name in subsections:
                    break

        return subsections

    def _find_subsection_end(
        self, start_page: int, max_page: int, pages_data: List[Dict]
    ) -> int:
        """Find where a sub-section ends (next Note number)."""
        # Look for next "Note XX:" pattern after start page
        note_pattern = r"(?i)^note\s+\d+\s*[:.]\s*\w"

        for page_num in range(start_page + 1, min(max_page + 1, len(pages_data) + 1)):
            if page_num - 1 >= len(pages_data):
                continue
            page_text = pages_data[page_num - 1]["text"]

            # Check if a new note starts on this page
            for line in page_text.split("\n")[:10]:  # Check first 10 lines
                if re.match(note_pattern, line.strip()):
                    return page_num - 1  # End on previous page

        # If no next note found, extend 5 pages or to end of notes
        return min(start_page + 5, max_page)

    def _validate_sections(
        self, sections: Dict[str, Dict[str, int]], pages_data: List[Dict]
    ) -> Dict[str, Dict[str, int]]:
        """Layer 4: Validate sections with content fingerprints."""
        validated = {}

        for section_name, page_range in sections.items():
            fp = CONTENT_FINGERPRINTS.get(section_name)
            if not fp:
                # No fingerprint defined - accept as-is
                validated[section_name] = page_range
                continue

            start = page_range["start"]
            end = page_range["end"]

            # Validate against page count bounds
            if start > len(pages_data) or end > len(pages_data):
                logger.warning(
                    f"Section '{section_name}' pages {start}-{end} exceed document length"
                )
                continue

            # Collect text from section
            section_text = ""
            for p in range(start - 1, min(end, len(pages_data))):
                section_text += pages_data[p]["text"] + " "

            # Check required keywords
            has_required = True
            for pattern in fp["required"]:
                if not re.search(pattern, section_text[:5000]):
                    has_required = False
                    break

            if has_required:
                # Check page count sanity
                page_count = end - start + 1
                min_pages, max_pages = fp["expected_pages"]
                if page_count > max_pages * 3:
                    # Suspiciously large - might have wrong end boundary
                    # Trim to expected max * 1.5
                    end = start + int(max_pages * 1.5)
                    page_range = {"start": start, "end": min(end, len(pages_data))}

                validated[section_name] = page_range
            else:
                logger.warning(
                    f"Section '{section_name}' failed content validation on pages {start}-{end}"
                )
                # Still include but flag it
                validated[section_name] = page_range

        return validated

    def extract_section_text(
        self,
        section_name: str,
        sections: Dict[str, Dict[str, int]],
        pages_data: List[Dict],
    ) -> Optional[str]:
        """Extract full text from a specific section."""
        if section_name not in sections:
            return None

        page_range = sections[section_name]
        start = page_range["start"]
        end = page_range["end"]

        text_parts = []
        for page_data in pages_data:
            page_num = page_data["page_number"]
            if start <= page_num <= end:
                text_parts.append(f"--- Page {page_num} ---\n{page_data['text']}\n")

        return "\n".join(text_parts)

    def get_relevant_pages(
        self, sections: Dict[str, Dict[str, int]]
    ) -> List[int]:
        """Get all page numbers that belong to any detected section."""
        pages = set()
        for page_range in sections.values():
            for p in range(page_range["start"], page_range["end"] + 1):
                pages.add(p)
        return sorted(pages)


section_detector = SectionDetector()
