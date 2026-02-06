"""Category 1: Auditor Red Flags (8 flags, 20% weight).

This category has the highest weight as auditor-related issues are often
the most reliable early warning signs of accounting fraud.
"""

import logging
from typing import Dict

from app.models.red_flag import FlagCategory, FlagSeverity
from app.red_flags.base import RedFlagBase, RedFlagResult
from app.red_flags.registry import flag_registry

logger = logging.getLogger(__name__)


class AuditorResignationFlag(RedFlagBase):
    """Flag #1: Auditor Resigned Mid-Term (CRITICAL)."""

    def __init__(self):
        self.flag_number = 1
        self.flag_name = "Auditor Resigned Mid-Term"
        self.category = FlagCategory.AUDITOR
        self.severity = FlagSeverity.CRITICAL
        self.description = "Auditor resigned during the fiscal year, not at year-end"

    def check(self, data: Dict) -> RedFlagResult:
        """Check for auditor resignation keywords in auditor report."""
        auditor_text = data.get("sections", {}).get("auditor_report", "")

        if not auditor_text:
            return self.create_not_triggered_result("Auditor report section not found")

        auditor_text_lower = auditor_text.lower()

        # Keywords indicating resignation
        resignation_keywords = [
            "resignation",
            "resigned",
            "withdrawing",
            "withdraw",
            "ceased to be",
            "stepped down",
            "relinquished",
        ]

        # Check for resignation mentions
        for keyword in resignation_keywords:
            if keyword in auditor_text_lower:
                # Extract context around keyword
                index = auditor_text_lower.find(keyword)
                context_start = max(0, index - 100)
                context_end = min(len(auditor_text), index + 200)
                evidence_snippet = auditor_text[context_start:context_end]

                return self.create_triggered_result(
                    evidence=f"Auditor report mentions '{keyword}': ...{evidence_snippet}...",
                    confidence=95.0,
                    extracted_data={"keyword_found": keyword, "context": evidence_snippet},
                )

        return self.create_not_triggered_result("No resignation keywords found in auditor report")


class AuditorDowngradeFlag(RedFlagBase):
    """Flag #2: Auditor Change from Big4 to Small Firm (HIGH)."""

    def __init__(self):
        self.flag_number = 2
        self.flag_name = "Auditor Downgrade (Big4 to Small)"
        self.category = FlagCategory.AUDITOR
        self.severity = FlagSeverity.HIGH
        self.description = "Company changed from Big4 auditor to smaller firm"

    def check(self, data: Dict) -> RedFlagResult:
        """Check if auditor changed from Big4 to non-Big4."""
        # Big4 firms
        big4_firms = ["deloitte", "pwc", "pricewaterhousecoopers", "ey", "ernst & young", "kpmg"]

        auditor_text = data.get("sections", {}).get("auditor_report", "")

        if not auditor_text:
            return self.create_not_triggered_result("Auditor report section not found")

        auditor_text_lower = auditor_text.lower()

        # Check if current auditor is Big4
        current_is_big4 = any(firm in auditor_text_lower for firm in big4_firms)

        # Look for auditor change keywords
        change_keywords = ["appointment", "appointed", "resigned", "replaced", "change of auditor", "new auditor"]

        has_change_mention = any(keyword in auditor_text_lower for keyword in change_keywords)

        if has_change_mention and not current_is_big4:
            # Potential downgrade - check if previous auditor was Big4
            # Look for "previously" or "former" mentions with Big4 names
            previous_big4 = False
            for firm in big4_firms:
                if (
                    f"previous {firm}" in auditor_text_lower
                    or f"former {firm}" in auditor_text_lower
                    or f"resigned {firm}" in auditor_text_lower
                ):
                    previous_big4 = True
                    break

            if previous_big4:
                return self.create_triggered_result(
                    evidence="Company changed from Big4 auditor to smaller firm. "
                    "This may indicate disagreements or reluctance by Big4 to continue.",
                    confidence=80.0,
                    extracted_data={"has_change": True, "current_is_big4": False},
                )

        # For MVP, we can't definitively check without historical data
        # Flag as not triggered but note limitation
        return self.create_not_triggered_result(
            "No clear evidence of Big4 to non-Big4 downgrade (historical data needed for full check)"
        )


class QualifiedOpinionFlag(RedFlagBase):
    """Flag #3: Qualified/Adverse/Disclaimer Opinion (CRITICAL)."""

    def __init__(self):
        self.flag_number = 3
        self.flag_name = "Qualified/Adverse Opinion"
        self.category = FlagCategory.AUDITOR
        self.severity = FlagSeverity.CRITICAL
        self.description = "Auditor issued qualified, adverse, or disclaimer opinion"

    def check(self, data: Dict) -> RedFlagResult:
        """Check auditor opinion type."""
        auditor_analysis = data.get("financial_data", {}).get("auditor_analysis", {})
        auditor_text = data.get("sections", {}).get("auditor_report", "")

        # Check structured data first
        opinion_type = auditor_analysis.get("opinion_type", "").lower()

        if opinion_type in ["qualified", "adverse", "disclaimer"]:
            details = auditor_analysis.get("emphasis_of_matter_details", "")
            return self.create_triggered_result(
                evidence=f"Auditor issued {opinion_type.upper()} opinion. Details: {details}",
                confidence=100.0,
                extracted_data={"opinion_type": opinion_type, "details": details},
            )

        # Fallback: Check text for opinion keywords
        if auditor_text:
            auditor_text_lower = auditor_text.lower()

            qualified_indicators = [
                "qualified opinion",
                "adverse opinion",
                "disclaimer of opinion",
                "except for",
                "subject to",
                "we are unable to obtain sufficient",
                "limitation of scope",
            ]

            for indicator in qualified_indicators:
                if indicator in auditor_text_lower:
                    index = auditor_text_lower.find(indicator)
                    context = auditor_text[max(0, index - 50) : min(len(auditor_text), index + 200)]

                    return self.create_triggered_result(
                        evidence=f"Auditor report contains '{indicator}': ...{context}...",
                        confidence=90.0,
                        extracted_data={"indicator": indicator, "context": context},
                    )

        return self.create_not_triggered_result("Unqualified/Clean opinion")


class EmphasisOfMatterFlag(RedFlagBase):
    """Flag #4: Emphasis of Matter Paragraphs (HIGH)."""

    def __init__(self):
        self.flag_number = 4
        self.flag_name = "Emphasis of Matter Paragraphs"
        self.category = FlagCategory.AUDITOR
        self.severity = FlagSeverity.HIGH
        self.description = "Auditor included Emphasis of Matter (EOM) paragraph"

    def check(self, data: Dict) -> RedFlagResult:
        """Check for Emphasis of Matter paragraphs."""
        auditor_analysis = data.get("financial_data", {}).get("auditor_analysis", {})
        auditor_text = data.get("sections", {}).get("auditor_report", "")

        # Check structured data
        has_eom = auditor_analysis.get("has_emphasis_of_matter", False)
        eom_details = auditor_analysis.get("emphasis_of_matter_details", "")

        if has_eom and eom_details:
            return self.create_triggered_result(
                evidence=f"Auditor included Emphasis of Matter paragraph: {eom_details}",
                confidence=95.0,
                extracted_data={"has_eom": True, "details": eom_details},
            )

        # Fallback: Text search
        if auditor_text:
            auditor_text_lower = auditor_text.lower()

            eom_keywords = [
                "emphasis of matter",
                "emphasis-of-matter",
                "emphasis of a matter",
                "draw attention to",
                "material uncertainty",
            ]

            for keyword in eom_keywords:
                if keyword in auditor_text_lower:
                    index = auditor_text_lower.find(keyword)
                    context = auditor_text[max(0, index - 50) : min(len(auditor_text), index + 250)]

                    return self.create_triggered_result(
                        evidence=f"Emphasis of Matter found: ...{context}...",
                        confidence=85.0,
                        extracted_data={"keyword": keyword, "context": context},
                    )

        return self.create_not_triggered_result("No Emphasis of Matter paragraphs found")


class GoingConcernFlag(RedFlagBase):
    """Flag #5: Going Concern Qualification (CRITICAL)."""

    def __init__(self):
        self.flag_number = 5
        self.flag_name = "Going Concern Issues"
        self.category = FlagCategory.AUDITOR
        self.severity = FlagSeverity.CRITICAL
        self.description = "Auditor raised going concern doubts about company's ability to continue"

    def check(self, data: Dict) -> RedFlagResult:
        """Check for going concern issues."""
        auditor_analysis = data.get("financial_data", {}).get("auditor_analysis", {})
        auditor_text = data.get("sections", {}).get("auditor_report", "")

        # Check structured data
        has_going_concern = auditor_analysis.get("going_concern_issues", False)

        if has_going_concern:
            return self.create_triggered_result(
                evidence="Auditor raised going concern issues about company's ability to continue operations",
                confidence=100.0,
                extracted_data={"has_going_concern": True},
            )

        # Text search for going concern mentions
        if auditor_text:
            auditor_text_lower = auditor_text.lower()

            going_concern_keywords = [
                "going concern",
                "ability to continue",
                "continue as a going concern",
                "substantial doubt",
                "continuance of the company",
            ]

            for keyword in going_concern_keywords:
                if keyword in auditor_text_lower:
                    index = auditor_text_lower.find(keyword)
                    context = auditor_text[max(0, index - 100) : min(len(auditor_text), index + 250)]

                    return self.create_triggered_result(
                        evidence=f"Going concern mention: ...{context}...",
                        confidence=95.0,
                        extracted_data={"keyword": keyword, "context": context},
                    )

        return self.create_not_triggered_result("No going concern issues raised")


class KeyAuditMattersRevenueFlag(RedFlagBase):
    """Flag #6: Key Audit Matters on Revenue Recognition (HIGH)."""

    def __init__(self):
        self.flag_number = 6
        self.flag_name = "KAM on Revenue Recognition"
        self.category = FlagCategory.AUDITOR
        self.severity = FlagSeverity.HIGH
        self.description = "Key Audit Matters section highlights revenue recognition concerns"

    def check(self, data: Dict) -> RedFlagResult:
        """Check for revenue-related Key Audit Matters."""
        auditor_analysis = data.get("financial_data", {}).get("auditor_analysis", {})
        auditor_text = data.get("sections", {}).get("auditor_report", "")

        # Check structured data
        material_uncertainties = auditor_analysis.get("material_uncertainties", [])

        if material_uncertainties:
            for uncertainty in material_uncertainties:
                uncertainty_lower = str(uncertainty).lower()
                if "revenue" in uncertainty_lower or "income" in uncertainty_lower:
                    return self.create_triggered_result(
                        evidence=f"Key Audit Matter related to revenue: {uncertainty}",
                        confidence=90.0,
                        extracted_data={"material_uncertainty": uncertainty},
                    )

        # Text search
        if auditor_text:
            auditor_text_lower = auditor_text.lower()

            # Look for KAM section first
            kam_indicators = ["key audit matter", "key audit matters", "critical audit matter"]

            kam_found = any(indicator in auditor_text_lower for indicator in kam_indicators)

            if kam_found:
                # Now check if revenue is mentioned in KAM context
                revenue_keywords = [
                    "revenue recognition",
                    "revenue accounting",
                    "income recognition",
                    "sales recognition",
                    "timing of revenue",
                ]

                for keyword in revenue_keywords:
                    if keyword in auditor_text_lower:
                        index = auditor_text_lower.find(keyword)
                        context = auditor_text[max(0, index - 100) : min(len(auditor_text), index + 300)]

                        return self.create_triggered_result(
                            evidence=f"Revenue-related Key Audit Matter: ...{context}...",
                            confidence=85.0,
                            extracted_data={"keyword": keyword, "context": context},
                        )

        return self.create_not_triggered_result("No Key Audit Matters on revenue recognition")


class AuditFeesDeclineFlag(RedFlagBase):
    """Flag #7: Audit Fees Declining Despite Revenue Growth (MEDIUM)."""

    def __init__(self):
        self.flag_number = 7
        self.flag_name = "Audit Fees Declining vs Growth"
        self.category = FlagCategory.AUDITOR
        self.severity = FlagSeverity.MEDIUM
        self.description = "Audit fees declining while company is growing rapidly"

    def check(self, data: Dict) -> RedFlagResult:
        """Check if audit fees are declining despite revenue growth."""
        # Extract audit fees from notes
        notes_data = data.get("financial_data", {}).get("notes", {})

        # Extract current audit fees
        # This would need to be extracted by data_extractor
        # For now, check if we have the data structure

        # Since we don't have historical data in MVP, we'll implement basic check
        auditor_text = data.get("sections", {}).get("auditor_report", "")
        notes_text = data.get("sections", {}).get("notes_to_accounts", "")

        # Look for audit fee mentions in notes
        if notes_text:
            notes_lower = notes_text.lower()

            # Look for audit fee section
            if "audit fee" in notes_lower or "auditor remuneration" in notes_lower or "auditor's remuneration" in notes_lower:
                # For MVP, we flag this for manual review if we can't calculate
                # Full implementation would compare current vs previous year fees
                return self.create_not_triggered_result(
                    "Audit fees found in notes (historical comparison needed for full check)"
                )

        return self.create_not_triggered_result("Audit fees data not found (requires historical analysis)")


class AuditorTenureFlag(RedFlagBase):
    """Flag #8: Same Auditor for 10+ Years (MEDIUM)."""

    def __init__(self):
        self.flag_number = 8
        self.flag_name = "Same Auditor 10+ Years"
        self.category = FlagCategory.AUDITOR
        self.severity = FlagSeverity.MEDIUM
        self.description = "Company has had same auditor for 10 or more years (independence concern)"

    def check(self, data: Dict) -> RedFlagResult:
        """Check auditor tenure."""
        auditor_text = data.get("sections", {}).get("auditor_report", "")

        if not auditor_text:
            return self.create_not_triggered_result("Auditor report not found")

        auditor_text_lower = auditor_text.lower()

        # Look for tenure mentions
        tenure_keywords = [
            "appointed in",
            "appointment since",
            "auditor since",
            "continuing as auditor",
            "years as auditor",
            "tenure of",
        ]

        # This requires historical data which we don't have in MVP
        # We can flag if we find explicit tenure mentions

        for keyword in tenure_keywords:
            if keyword in auditor_text_lower:
                index = auditor_text_lower.find(keyword)
                context = auditor_text[max(0, index - 50) : min(len(auditor_text), index + 150)]

                # Try to extract year if mentioned
                return self.create_not_triggered_result(
                    f"Auditor tenure information found: ...{context}... (requires historical data for full check)"
                )

        return self.create_not_triggered_result("Auditor tenure data not available (requires historical analysis)")


# Register all auditor flags
flag_registry.register(AuditorResignationFlag())
flag_registry.register(AuditorDowngradeFlag())
flag_registry.register(QualifiedOpinionFlag())
flag_registry.register(EmphasisOfMatterFlag())
flag_registry.register(GoingConcernFlag())
flag_registry.register(KeyAuditMattersRevenueFlag())
flag_registry.register(AuditFeesDeclineFlag())
flag_registry.register(AuditorTenureFlag())

logger.info("Registered 8 auditor flags (Category 1)")
