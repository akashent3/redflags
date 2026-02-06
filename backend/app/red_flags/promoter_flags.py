"""Category 4: Promoter Red Flags (6 flags, 15% weight).

Promoter behavior is a critical indicator of company health. High pledging,
selling shares, or extracting excessive compensation are warning signs.
"""

import logging
from typing import Dict

from app.models.red_flag import FlagCategory, FlagSeverity
from app.red_flags.base import RedFlagBase, RedFlagResult
from app.red_flags.registry import flag_registry

logger = logging.getLogger(__name__)


class PromoterPledgeHighFlag(RedFlagBase):
    """Flag #24: Promoter Pledge > 50% (CRITICAL)."""

    def __init__(self):
        self.flag_number = 24
        self.flag_name = "Promoter Pledge > 50%"
        self.category = FlagCategory.PROMOTER
        self.severity = FlagSeverity.CRITICAL
        self.description = "Promoter has pledged more than 50% of their shareholding"

    def check(self, data: Dict) -> RedFlagResult:
        """Check for high promoter pledge percentage."""
        financial_data = data.get("financial_data", {})
        governance_text = data.get("sections", {}).get("corporate_governance_report", "")
        notes_text = data.get("sections", {}).get("notes_to_accounts", "")

        # Check structured data for promoter pledge
        shareholding = financial_data.get("shareholding_pattern", {})
        promoter_pledge_pct = self.extract_value(shareholding, "promoter_pledge_percentage", default=0.0)

        # If no structured data, try to extract from text
        if promoter_pledge_pct == 0.0:
            combined_text = (governance_text + " " + notes_text).lower()

            # Search for pledge percentage mentions
            import re

            pledge_patterns = [
                r'pledged\s+(\d+(?:\.\d+)?)\s*%',
                r'pledge.*?(\d+(?:\.\d+)?)\s*%',
                r'(\d+(?:\.\d+)?)\s*%.*?pledged',
            ]

            for pattern in pledge_patterns:
                matches = re.findall(pattern, combined_text)
                if matches:
                    try:
                        promoter_pledge_pct = max([float(m) for m in matches])
                        break
                    except:
                        pass

        # Trigger if pledge > 50%
        if promoter_pledge_pct > 50:
            evidence = (
                f"Promoter has pledged {promoter_pledge_pct:.1f}% of their shareholding. "
                f"High pledge indicates financial stress and risk of margin calls/loss of control."
            )

            return self.create_triggered_result(
                evidence=evidence,
                confidence=95.0,
                extracted_data={
                    "promoter_pledge_pct": promoter_pledge_pct,
                },
            )

        return self.create_not_triggered_result("Promoter pledge within acceptable limits")


class PledgeIncreasingFlag(RedFlagBase):
    """Flag #25: Promoter Pledge Increasing QoQ (HIGH)."""

    def __init__(self):
        self.flag_number = 25
        self.flag_name = "Pledge Increasing QoQ"
        self.category = FlagCategory.PROMOTER
        self.severity = FlagSeverity.HIGH
        self.description = "Promoter pledge percentage increased significantly quarter-over-quarter"

    def check(self, data: Dict) -> RedFlagResult:
        """Check if promoter pledge is increasing."""
        financial_data = data.get("financial_data", {})

        # Check structured data
        shareholding = financial_data.get("shareholding_pattern", {})
        pledge_current = self.extract_value(shareholding, "promoter_pledge_percentage", default=0.0)
        pledge_previous = self.extract_value(shareholding, "promoter_pledge_percentage_previous", default=0.0)

        if pledge_current == 0.0 and pledge_previous == 0.0:
            return self.create_not_triggered_result("Promoter pledge data not available")

        # Calculate increase
        pledge_increase = pledge_current - pledge_previous

        # Trigger if pledge increased by > 5 percentage points
        if pledge_increase > 5:
            evidence = (
                f"Promoter pledge increased from {pledge_previous:.1f}% to {pledge_current:.1f}% "
                f"(+{pledge_increase:.1f} percentage points). "
                f"Increasing pledge suggests worsening promoter financial stress."
            )

            return self.create_triggered_result(
                evidence=evidence,
                confidence=90.0,
                extracted_data={
                    "pledge_current": pledge_current,
                    "pledge_previous": pledge_previous,
                    "pledge_increase": pledge_increase,
                },
            )

        return self.create_not_triggered_result("Promoter pledge stable or decreasing")


class PromoterSellingSharesFlag(RedFlagBase):
    """Flag #26: Promoter Selling Shares (MEDIUM)."""

    def __init__(self):
        self.flag_number = 26
        self.flag_name = "Promoter Selling Shares"
        self.category = FlagCategory.PROMOTER
        self.severity = FlagSeverity.MEDIUM
        self.description = "Promoter shareholding decreased (promoters selling stakes)"

    def check(self, data: Dict) -> RedFlagResult:
        """Check if promoter is reducing stake."""
        financial_data = data.get("financial_data", {})
        governance_text = data.get("sections", {}).get("corporate_governance_report", "")

        # Check structured data
        shareholding = financial_data.get("shareholding_pattern", {})
        promoter_holding_current = self.extract_value(shareholding, "promoter_holding_percentage", default=0.0)
        promoter_holding_previous = self.extract_value(shareholding, "promoter_holding_percentage_previous", default=0.0)

        if promoter_holding_current == 0.0 and promoter_holding_previous == 0.0:
            return self.create_not_triggered_result("Promoter holding data not available")

        # Calculate decrease
        holding_decrease = promoter_holding_previous - promoter_holding_current

        # Text search for selling mentions
        selling_keywords = [
            "promoter sale",
            "promoter sold",
            "reduction in promoter holding",
            "divestment by promoter",
            "offloaded stake",
        ]

        governance_lower = governance_text.lower()
        selling_mentions = sum(1 for keyword in selling_keywords if keyword in governance_lower)

        # Trigger if holding decreased > 2% or selling mentions
        significant_decrease = holding_decrease > 2
        selling_mentioned = selling_mentions > 0

        if significant_decrease or selling_mentioned:
            evidence_parts = []

            if significant_decrease:
                evidence_parts.append(
                    f"Promoter holding decreased from {promoter_holding_previous:.1f}% to {promoter_holding_current:.1f}% "
                    f"(-{holding_decrease:.1f} percentage points)"
                )

            if selling_mentioned:
                evidence_parts.append(
                    f"Promoter stake reduction mentioned in disclosures ({selling_mentions} references)"
                )

            evidence = ". ".join(evidence_parts) + ". Promoter selling may indicate lack of confidence in company prospects."

            return self.create_triggered_result(
                evidence=evidence,
                confidence=80.0,
                extracted_data={
                    "holding_current": promoter_holding_current,
                    "holding_previous": promoter_holding_previous,
                    "holding_decrease": holding_decrease,
                },
            )

        return self.create_not_triggered_result("Promoter holding stable or increasing")


class DisproportionateSalaryFlag(RedFlagBase):
    """Flag #27: Disproportionate Managerial Remuneration (MEDIUM)."""

    def __init__(self):
        self.flag_number = 27
        self.flag_name = "Disproportionate Salary"
        self.category = FlagCategory.PROMOTER
        self.severity = FlagSeverity.MEDIUM
        self.description = "Managerial remuneration excessive relative to profit"

    def check(self, data: Dict) -> RedFlagResult:
        """Check if director/promoter compensation is excessive."""
        financial_data = data.get("financial_data", {})
        notes_text = data.get("sections", {}).get("notes_to_accounts", "")

        # Extract managerial remuneration and profit
        notes_data = financial_data.get("notes", {})
        profit_loss = financial_data.get("profit_loss", {})

        managerial_remuneration = self.extract_value(notes_data, "managerial_remuneration", "value", default=0.0)
        pat = self.extract_value(profit_loss, "net_profit", "value", default=0.0)

        # If no structured data, search text for remuneration amounts
        if managerial_remuneration == 0.0:
            import re

            remuneration_patterns = [
                r'director.*?remuneration.*?(\d+(?:,\d+)*(?:\.\d+)?)',
                r'managerial remuneration.*?(\d+(?:,\d+)*(?:\.\d+)?)',
                r'compensation.*?directors.*?(\d+(?:,\d+)*(?:\.\d+)?)',
            ]

            notes_lower = notes_text.lower()
            for pattern in remuneration_patterns:
                matches = re.findall(pattern, notes_lower)
                if matches:
                    try:
                        # Extract highest amount
                        amounts = [float(m.replace(',', '')) for m in matches]
                        managerial_remuneration = max(amounts)
                        break
                    except:
                        pass

        if not pat or pat <= 0:
            return self.create_not_triggered_result("Profit data not available or company is loss-making")

        if managerial_remuneration == 0.0:
            return self.create_not_triggered_result("Managerial remuneration data not available")

        # Calculate remuneration as percentage of PAT
        remuneration_pct = (managerial_remuneration / pat) * 100

        # Trigger if remuneration > 5% of PAT
        if remuneration_pct > 5:
            evidence = (
                f"Managerial remuneration is {remuneration_pct:.1f}% of profit after tax "
                f"(Remuneration: {managerial_remuneration:,.0f}, PAT: {pat:,.0f}). "
                f"Excessive compensation may indicate profit extraction by promoters."
            )

            return self.create_triggered_result(
                evidence=evidence,
                confidence=75.0,
                extracted_data={
                    "managerial_remuneration": managerial_remuneration,
                    "pat": pat,
                    "remuneration_pct": remuneration_pct,
                },
            )

        return self.create_not_triggered_result("Managerial remuneration within reasonable limits")


class PromoterEntityNameChangeFlag(RedFlagBase):
    """Flag #28: Promoter Entity Name Change (LOW)."""

    def __init__(self):
        self.flag_number = 28
        self.flag_name = "Promoter Entity Name Change"
        self.category = FlagCategory.PROMOTER
        self.severity = FlagSeverity.LOW
        self.description = "Promoter or promoter group entity changed name during the year"

    def check(self, data: Dict) -> RedFlagResult:
        """Check for promoter entity name changes."""
        notes_text = data.get("sections", {}).get("notes_to_accounts", "")
        governance_text = data.get("sections", {}).get("corporate_governance_report", "")

        # Search for name change keywords
        name_change_keywords = [
            "name changed from",
            "formerly known as",
            "renamed to",
            "change of name",
            "name change",
            "erstwhile",
        ]

        combined_text = (notes_text + " " + governance_text).lower()
        name_change_mentions = []

        for keyword in name_change_keywords:
            if keyword in combined_text:
                name_change_mentions.append(keyword)

        # Count mentions
        mention_count = len(name_change_mentions)

        # Trigger if name change mentioned
        if mention_count > 0:
            evidence = (
                f"Promoter entity name change mentioned in disclosures "
                f"({mention_count} references: {', '.join(set(name_change_mentions))}). "
                f"Name changes may be used to obscure past issues or relationships."
            )

            return self.create_triggered_result(
                evidence=evidence,
                confidence=60.0,  # Lower confidence as not always problematic
                extracted_data={
                    "name_change_mentions": name_change_mentions,
                    "mention_count": mention_count,
                },
            )

        return self.create_not_triggered_result("No promoter entity name changes detected")


class ICDToPromoterGroupFlag(RedFlagBase):
    """Flag #29: Inter-Corporate Deposits to Promoter Group (HIGH)."""

    def __init__(self):
        self.flag_number = 29
        self.flag_name = "ICDs to Promoter Group"
        self.category = FlagCategory.PROMOTER
        self.severity = FlagSeverity.HIGH
        self.description = "Inter-corporate deposits given to promoter group entities"

    def check(self, data: Dict) -> RedFlagResult:
        """Check for ICDs to promoter entities."""
        financial_data = data.get("financial_data", {})
        notes_text = data.get("sections", {}).get("notes_to_accounts", "")

        # Check structured RPT data
        rpt_data = financial_data.get("related_party_transactions", {})
        icd_amount = self.extract_value(rpt_data, "inter_corporate_deposits", "value", default=0.0)

        # Text search for ICD keywords
        icd_keywords = [
            "inter-corporate deposit",
            "inter corporate deposit",
            "icd given",
            "icd to",
            "deposit given to",
            "short-term deposit to",
        ]

        notes_lower = notes_text.lower()
        icd_mentions = []

        for keyword in icd_keywords:
            if keyword in notes_lower:
                icd_mentions.append(keyword)

        # Check for promoter group references near ICD mentions
        promoter_keywords = ["promoter", "group company", "related party"]
        promoter_icd_context = any(
            promoter_kw in notes_lower[max(0, notes_lower.find(icd_kw) - 100):notes_lower.find(icd_kw) + 100]
            for icd_kw in icd_mentions
            for promoter_kw in promoter_keywords
        )

        # Trigger if ICD amount > 0 or ICD mentions with promoter context
        if abs(icd_amount) > 0 or (len(icd_mentions) > 0 and promoter_icd_context):
            evidence_parts = []

            if abs(icd_amount) > 0:
                evidence_parts.append(
                    f"Inter-corporate deposits to related parties: {abs(icd_amount):,.0f}"
                )

            if icd_mentions:
                evidence_parts.append(
                    f"ICD references in notes ({len(icd_mentions)} mentions)"
                )

            evidence = ". ".join(evidence_parts) + ". ICDs to promoter group pose fund diversion risk."

            return self.create_triggered_result(
                evidence=evidence,
                confidence=85.0,
                extracted_data={
                    "icd_amount": abs(icd_amount),
                    "icd_mentions": icd_mentions,
                    "promoter_context": promoter_icd_context,
                },
            )

        return self.create_not_triggered_result("No ICDs to promoter group detected")


# Register all promoter flags
flag_registry.register(PromoterPledgeHighFlag())
flag_registry.register(PledgeIncreasingFlag())
flag_registry.register(PromoterSellingSharesFlag())
flag_registry.register(DisproportionateSalaryFlag())
flag_registry.register(PromoterEntityNameChangeFlag())
flag_registry.register(ICDToPromoterGroupFlag())

logger.info("Registered 6 promoter flags (Category 4)")
