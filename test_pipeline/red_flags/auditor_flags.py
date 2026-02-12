"""Category 1: Auditor Red Flags (8 flags, 20% weight)."""

import re
import logging
from typing import Dict

from red_flags.models import FlagCategory, FlagSeverity
from red_flags.base import RedFlagBase
from red_flags.registry import flag_registry

logger = logging.getLogger(__name__)


class AuditorResignationFlag(RedFlagBase):
    """Flag #1: Auditor Resignation Mid-Term (CRITICAL)."""
    def __init__(self):
        self.flag_number = 1
        self.flag_name = "Auditor Resignation"
        self.category = FlagCategory.AUDITOR
        self.severity = FlagSeverity.CRITICAL

    def check(self, data: Dict):
        auditor_text = data.get("sections", {}).get("auditor_report", "")
        directors_text = data.get("sections", {}).get("directors_report", "")
        combined = (auditor_text + " " + directors_text).lower()
        keywords = ["auditor resigned", "auditor resignation", "casual vacancy", "vacancy caused by resignation of auditor", "statutory auditor resigned", "resigned as auditor"]
        mentions = [kw for kw in keywords if kw in combined]
        # Also check structured data
        auditor_analysis = data.get("financial_data", {}).get("auditor_analysis", {})
        if auditor_analysis.get("auditor_resignation"):
            mentions.append("auditor_resignation (structured)")
        if mentions:
            return self.create_triggered_result(evidence=f"Auditor resignation detected ({len(mentions)} references: {', '.join(set(mentions[:3]))}). Mid-term auditor exits are a serious red flag.", confidence=95.0)
        return self.create_not_triggered_result("No auditor resignation detected")


class AuditorDowngradeFlag(RedFlagBase):
    """Flag #2: Auditor Downgrade (Big4 to small firm) (HIGH)."""
    def __init__(self):
        self.flag_number = 2
        self.flag_name = "Auditor Downgrade"
        self.category = FlagCategory.AUDITOR
        self.severity = FlagSeverity.HIGH

    def check(self, data: Dict):
        auditor_text = data.get("sections", {}).get("auditor_report", "").lower()
        directors_text = data.get("sections", {}).get("directors_report", "").lower()
        combined = auditor_text + " " + directors_text
        big4 = ["deloitte", "kpmg", "ernst & young", "e&y", "pricewaterhousecoopers", "pwc", "s r b c", "bsr", "price waterhouse", "walker chandiok"]
        change_keywords = ["change of auditor", "new auditor", "appointed as auditor", "auditor appointed", "replaced by", "succeeding auditor"]
        has_big4 = any(firm in combined for firm in big4)
        has_change = any(kw in combined for kw in change_keywords)
        auditor_analysis = data.get("financial_data", {}).get("auditor_analysis", {})
        if auditor_analysis.get("auditor_change"):
            has_change = True
        if has_change and not has_big4:
            return self.create_triggered_result(evidence="Auditor change detected without Big 4 firm involvement. Downgrade to smaller firm may reduce audit quality.", confidence=70.0)
        return self.create_not_triggered_result("No auditor downgrade detected")


class QualifiedOpinionFlag(RedFlagBase):
    """Flag #3: Qualified/Adverse/Disclaimer Opinion (CRITICAL)."""
    def __init__(self):
        self.flag_number = 3
        self.flag_name = "Qualified Opinion"
        self.category = FlagCategory.AUDITOR
        self.severity = FlagSeverity.CRITICAL

    def check(self, data: Dict):
        auditor_text = data.get("sections", {}).get("auditor_report", "").lower()
        auditor_analysis = data.get("financial_data", {}).get("auditor_analysis", {})
        opinion = auditor_analysis.get("opinion_type", "").lower()
        if opinion in ["qualified", "adverse", "disclaimer"]:
            return self.create_triggered_result(evidence=f"Auditor issued a {opinion.capitalize()} opinion. This is a severe red flag indicating material issues.", confidence=100.0, extracted_data={"opinion_type": opinion})
        keywords = ["qualified opinion", "adverse opinion", "disclaimer of opinion", "except for", "we do not express an opinion", "basis for qualified"]
        mentions = [kw for kw in keywords if kw in auditor_text]
        if mentions:
            return self.create_triggered_result(evidence=f"Qualified/Adverse opinion detected ({', '.join(mentions[:3])}). Material departures from accounting standards.", confidence=95.0)
        return self.create_not_triggered_result("Auditor opinion appears unqualified")


class EmphasisOfMatterFlag(RedFlagBase):
    """Flag #4: Emphasis of Matter Paragraph (HIGH)."""
    def __init__(self):
        self.flag_number = 4
        self.flag_name = "Emphasis of Matter"
        self.category = FlagCategory.AUDITOR
        self.severity = FlagSeverity.HIGH

    def check(self, data: Dict):
        auditor_text = data.get("sections", {}).get("auditor_report", "").lower()
        auditor_analysis = data.get("financial_data", {}).get("auditor_analysis", {})
        if auditor_analysis.get("has_emphasis_of_matter"):
            details = auditor_analysis.get("emphasis_of_matter_details", "")
            return self.create_triggered_result(evidence=f"Emphasis of Matter paragraph present. {details}", confidence=90.0)
        keywords = ["emphasis of matter", "material uncertainty", "without qualifying our opinion, we draw attention", "draw attention to"]
        mentions = [kw for kw in keywords if kw in auditor_text]
        if mentions:
            return self.create_triggered_result(evidence=f"Emphasis of Matter detected ({len(mentions)} references). Auditor drawing attention to specific concerns.", confidence=85.0)
        return self.create_not_triggered_result("No Emphasis of Matter paragraph found")


class GoingConcernFlag(RedFlagBase):
    """Flag #5: Going Concern Issue (CRITICAL)."""
    def __init__(self):
        self.flag_number = 5
        self.flag_name = "Going Concern"
        self.category = FlagCategory.AUDITOR
        self.severity = FlagSeverity.CRITICAL

    def check(self, data: Dict):
        auditor_text = data.get("sections", {}).get("auditor_report", "").lower()
        notes_text = data.get("sections", {}).get("notes_to_accounts", "").lower()
        auditor_analysis = data.get("financial_data", {}).get("auditor_analysis", {})
        if auditor_analysis.get("going_concern_issues"):
            return self.create_triggered_result(evidence="Going concern issues identified by auditor. Company's ability to continue operations is in doubt.", confidence=100.0)
        combined = auditor_text + " " + notes_text
        keywords = ["going concern", "material uncertainty related to going concern", "ability to continue as a going concern", "going concern basis", "significant doubt"]
        mentions = [kw for kw in keywords if kw in combined]
        if mentions:
            return self.create_triggered_result(evidence=f"Going concern language detected ({len(mentions)} references). Significant doubt about company's continuation.", confidence=95.0)
        return self.create_not_triggered_result("No going concern issues detected")


class KeyAuditMattersRevenueFlag(RedFlagBase):
    """Flag #6: KAM Related to Revenue Recognition (HIGH)."""
    def __init__(self):
        self.flag_number = 6
        self.flag_name = "KAM on Revenue"
        self.category = FlagCategory.AUDITOR
        self.severity = FlagSeverity.HIGH

    def check(self, data: Dict):
        auditor_text = data.get("sections", {}).get("auditor_report", "").lower()
        auditor_analysis = data.get("financial_data", {}).get("auditor_analysis", {})
        if auditor_analysis.get("kam_on_revenue"):
            return self.create_triggered_result(evidence="Key Audit Matter related to revenue recognition identified. Revenue recognition is a common area for manipulation.", confidence=90.0)
        # Check for KAM section and revenue mention
        if "key audit matter" in auditor_text:
            kam_start = auditor_text.find("key audit matter")
            kam_section = auditor_text[kam_start:kam_start + 3000]
            revenue_keywords = ["revenue recognition", "revenue from", "cut-off", "channel stuffing", "unbilled revenue"]
            mentions = [kw for kw in revenue_keywords if kw in kam_section]
            if mentions:
                return self.create_triggered_result(evidence=f"KAM references revenue: {', '.join(mentions[:3])}. Revenue recognition flagged as key risk by auditor.", confidence=85.0)
        return self.create_not_triggered_result("No KAM on revenue recognition")


class AuditFeesDeclineFlag(RedFlagBase):
    """Flag #7: Audit Fees Declining (MEDIUM)."""
    def __init__(self):
        self.flag_number = 7
        self.flag_name = "Audit Fees Decline"
        self.category = FlagCategory.AUDITOR
        self.severity = FlagSeverity.MEDIUM

    def check(self, data: Dict):
        financial_data = data.get("financial_data", {})
        notes = financial_data.get("notes", {})
        audit_fees = self.extract_value(notes, "audit_fees", "value", default=0.0)
        # Without historical data, check if fees are unusually low relative to revenue
        revenue = self.extract_value(financial_data.get("profit_loss", {}), "revenue", "value", default=0.0)
        if audit_fees > 0 and revenue > 0:
            fee_ratio = (audit_fees / revenue) * 10000  # basis points
            if fee_ratio < 0.5:  # Very low audit fee
                return self.create_triggered_result(evidence=f"Audit fees ({audit_fees:,.0f}) appear low relative to revenue ({revenue:,.0f}) — {fee_ratio:.2f} bps. Low fees may compromise audit quality.", confidence=60.0, extracted_data={"audit_fees": audit_fees, "revenue": revenue, "fee_ratio_bps": fee_ratio})
        return self.create_not_triggered_result("Audit fees data insufficient or within normal range")


class AuditorTenureFlag(RedFlagBase):
    """Flag #8: Same Auditor for 10+ Years (MEDIUM)."""
    def __init__(self):
        self.flag_number = 8
        self.flag_name = "Auditor Tenure > 10 Years"
        self.category = FlagCategory.AUDITOR
        self.severity = FlagSeverity.MEDIUM

    def check(self, data: Dict):
        auditor_text = data.get("sections", {}).get("auditor_report", "").lower()
        directors_text = data.get("sections", {}).get("directors_report", "").lower()
        combined = auditor_text + " " + directors_text
        tenure_patterns = [r'appointed\s+(?:as\s+)?(?:statutory\s+)?auditor.*?(\d{4})', r'auditor.*?since\s+(\d{4})', r'serving\s+as\s+auditor.*?(\d{4})']
        for pattern in tenure_patterns:
            matches = re.findall(pattern, combined)
            if matches:
                try:
                    years = [int(m) for m in matches if 1990 <= int(m) <= 2026]
                    if years:
                        earliest = min(years)
                        tenure = 2024 - earliest
                        if tenure >= 10:
                            return self.create_triggered_result(evidence=f"Auditor tenure appears to be {tenure}+ years (since {earliest}). Long tenure may reduce independence.", confidence=65.0, extracted_data={"tenure_years": tenure, "since_year": earliest})
                except (ValueError, TypeError):
                    pass
        return self.create_not_triggered_result("Auditor tenure data not available or within limits")


# Register all auditor flags
flag_registry.register(AuditorResignationFlag())
flag_registry.register(AuditorDowngradeFlag())
flag_registry.register(QualifiedOpinionFlag())
flag_registry.register(EmphasisOfMatterFlag())
flag_registry.register(GoingConcernFlag())
flag_registry.register(KeyAuditMattersRevenueFlag())
flag_registry.register(AuditFeesDeclineFlag())
flag_registry.register(AuditorTenureFlag())
