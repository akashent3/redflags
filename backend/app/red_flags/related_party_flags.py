"""Category 3: Related Party Transaction Red Flags (7 flags, 15% weight).

Related party transactions are a major source of accounting fraud as they can be used
to artificially inflate revenue, hide expenses, or transfer assets at non-market prices.
"""

import logging
from typing import Dict, List

from app.models.red_flag import FlagCategory, FlagSeverity
from app.red_flags.base import RedFlagBase, RedFlagResult
from app.red_flags.registry import flag_registry

logger = logging.getLogger(__name__)


class RPTHighPercentageFlag(RedFlagBase):
    """Flag #17: Related Party Transactions > 10% of Revenue (HIGH)."""

    def __init__(self):
        self.flag_number = 17
        self.flag_name = "RPT > 10% of Revenue"
        self.category = FlagCategory.RELATED_PARTY
        self.severity = FlagSeverity.HIGH
        self.description = "Related party transactions exceed 10% of revenue"

    def check(self, data: Dict) -> RedFlagResult:
        """Check if RPT volume is excessive relative to revenue."""
        financial_data = data.get("financial_data", {})

        rpt_data = financial_data.get("related_party_transactions", {})
        profit_loss = financial_data.get("profit_loss", {})

        revenue = self.extract_value(profit_loss, "revenue", "value", default=0.0)

        if not revenue:
            return self.create_not_triggered_result("Revenue data not available")

        # Sum all RPT amounts
        total_rpt = 0.0

        # Check for various RPT types
        rpt_types = ["sales", "purchases", "loans_given", "loans_taken", "investments", "guarantees", "other"]

        for rpt_type in rpt_types:
            amount = self.extract_value(rpt_data, rpt_type, "value", default=0.0)
            total_rpt += abs(amount)

        # If no structured data, check notes section
        if total_rpt == 0:
            notes_text = data.get("sections", {}).get("notes_to_accounts", "")
            if "related party" in notes_text.lower():
                return self.create_not_triggered_result(
                    "Related party transactions mentioned but amounts not extracted (manual review needed)"
                )
            else:
                return self.create_not_triggered_result("No related party transaction data found")

        # Calculate RPT as percentage of revenue
        rpt_percentage = (total_rpt / revenue) * 100

        # Trigger if RPT > 10% of revenue
        if rpt_percentage > 10:
            evidence = (
                f"Total Related Party Transactions are {rpt_percentage:.1f}% of revenue "
                f"(RPT: {total_rpt:,.0f}, Revenue: {revenue:,.0f}). "
                f"High RPT volume increases risk of non-arm's length transactions."
            )

            return self.create_triggered_result(
                evidence=evidence,
                confidence=85.0,
                extracted_data={
                    "total_rpt": total_rpt,
                    "revenue": revenue,
                    "rpt_percentage": rpt_percentage,
                },
            )

        return self.create_not_triggered_result("Related party transactions within acceptable range")


class LoansToRelatedPartiesFlag(RedFlagBase):
    """Flag #18: Loans to Related Parties (HIGH)."""

    def __init__(self):
        self.flag_number = 18
        self.flag_name = "Loans to Related Parties"
        self.category = FlagCategory.RELATED_PARTY
        self.severity = FlagSeverity.HIGH
        self.description = "Company has given loans to related parties (fund diversion risk)"

    def check(self, data: Dict) -> RedFlagResult:
        """Check for loans given to related parties."""
        financial_data = data.get("financial_data", {})
        notes_text = data.get("sections", {}).get("notes_to_accounts", "")

        rpt_data = financial_data.get("related_party_transactions", {})

        # Check structured data for loans given
        loans_given = self.extract_value(rpt_data, "loans_given", "value", default=0.0)
        advances_given = self.extract_value(rpt_data, "advances", "value", default=0.0)

        total_loans = abs(loans_given) + abs(advances_given)

        # Also check balance sheet for loans to related parties
        balance_sheet = financial_data.get("balance_sheet", {})
        loans_bs = self.extract_value(balance_sheet, "non_current_assets", "loans_to_related_parties", "value", default=0.0)

        total_loans = max(total_loans, abs(loans_bs))

        # Text search for loan keywords
        loan_keywords = [
            "loan given to",
            "advance to related party",
            "inter-corporate deposit",
            "icd given",
            "funds advanced to",
        ]

        notes_lower = notes_text.lower()
        loan_mentions = sum(1 for keyword in loan_keywords if keyword in notes_lower)

        # Trigger if loans > 0 or multiple mentions in notes
        if total_loans > 0 or loan_mentions >= 2:
            evidence_parts = []

            if total_loans > 0:
                evidence_parts.append(
                    f"Loans/advances to related parties: {total_loans:,.0f}"
                )

            if loan_mentions >= 2:
                evidence_parts.append(
                    f"Multiple loan references in notes ({loan_mentions} mentions)"
                )

            evidence = ". ".join(evidence_parts) + ". Loans to related parties pose fund diversion risk."

            return self.create_triggered_result(
                evidence=evidence,
                confidence=90.0,
                extracted_data={
                    "total_loans": total_loans,
                    "loan_mentions": loan_mentions,
                },
            )

        return self.create_not_triggered_result("No significant loans to related parties")


class RPTPremiumPricingFlag(RedFlagBase):
    """Flag #19: Purchases from Related Parties at Premium (MEDIUM)."""

    def __init__(self):
        self.flag_number = 19
        self.flag_name = "Purchases from RP at Premium"
        self.category = FlagCategory.RELATED_PARTY
        self.severity = FlagSeverity.MEDIUM
        self.description = "Purchases from related parties at above-market prices"

    def check(self, data: Dict) -> RedFlagResult:
        """Check for related party purchases that may be at premium prices."""
        financial_data = data.get("financial_data", {})
        notes_text = data.get("sections", {}).get("notes_to_accounts", "")

        rpt_data = financial_data.get("related_party_transactions", {})

        # Check for purchases from related parties
        rpt_purchases = self.extract_value(rpt_data, "purchases", "value", default=0.0)
        rpt_expenses = self.extract_value(rpt_data, "expenses", "value", default=0.0)

        total_rpt_purchases = abs(rpt_purchases) + abs(rpt_expenses)

        # Get total purchases/COGS for comparison
        profit_loss = financial_data.get("profit_loss", {})
        total_cogs = self.extract_value(profit_loss, "cost_of_goods_sold", "value", default=0.0)

        # Check if RPT purchases are significant portion
        if total_cogs > 0:
            rpt_purchase_pct = (total_rpt_purchases / total_cogs) * 100
        else:
            rpt_purchase_pct = 0

        # Text indicators of premium pricing
        premium_keywords = [
            "arm's length",
            "market price",
            "fair value",
            "transfer pricing",
            "at cost",
            "at premium",
        ]

        notes_lower = notes_text.lower()
        premium_mentions = sum(1 for keyword in premium_keywords if keyword in notes_lower)

        # Trigger if:
        # 1. RPT purchases > 20% of COGS (significant)
        # 2. Multiple pricing justification mentions (suggests scrutiny)
        significant_purchases = rpt_purchase_pct > 20
        excessive_justification = premium_mentions >= 3

        if significant_purchases or excessive_justification:
            evidence_parts = []

            if significant_purchases:
                evidence_parts.append(
                    f"Purchases from related parties: {rpt_purchase_pct:.1f}% of COGS "
                    f"({total_rpt_purchases:,.0f})"
                )

            if excessive_justification:
                evidence_parts.append(
                    f"Multiple pricing justifications in notes ({premium_mentions} references)"
                )

            evidence = ". ".join(evidence_parts) + ". Significant RPT purchases require scrutiny for fair pricing."

            return self.create_triggered_result(
                evidence=evidence,
                confidence=65.0,  # Lower confidence without actual price comparison
                extracted_data={
                    "rpt_purchases": total_rpt_purchases,
                    "rpt_purchase_pct": rpt_purchase_pct,
                    "premium_mentions": premium_mentions,
                },
            )

        return self.create_not_triggered_result("RPT purchases appear normal")


class RPTRevenueIncreasingFlag(RedFlagBase):
    """Flag #20: Revenue from Related Parties Increasing (MEDIUM)."""

    def __init__(self):
        self.flag_number = 20
        self.flag_name = "Revenue from RP Increasing"
        self.category = FlagCategory.RELATED_PARTY
        self.severity = FlagSeverity.MEDIUM
        self.description = "Revenue concentration from related parties is increasing"

    def check(self, data: Dict) -> RedFlagResult:
        """Check if related party revenue is growing."""
        financial_data = data.get("financial_data", {})

        rpt_data = financial_data.get("related_party_transactions", {})
        profit_loss = financial_data.get("profit_loss", {})

        # Extract current and previous year data
        rpt_sales_current = self.extract_value(rpt_data, "sales", "value", default=0.0)
        rpt_sales_previous = self.extract_value(rpt_data, "sales", "previous_year", default=0.0)

        revenue_current = self.extract_value(profit_loss, "revenue", "value", default=0.0)
        revenue_previous = self.extract_value(profit_loss, "revenue", "previous_year", default=0.0)

        if not revenue_current or not revenue_previous:
            return self.create_not_triggered_result("Insufficient revenue data")

        # Calculate RPT revenue percentage
        rpt_pct_current = (abs(rpt_sales_current) / revenue_current) * 100 if revenue_current else 0
        rpt_pct_previous = (abs(rpt_sales_previous) / revenue_previous) * 100 if revenue_previous else 0

        # Calculate change
        rpt_pct_increase = rpt_pct_current - rpt_pct_previous

        # Trigger if RPT revenue % increased by > 5 percentage points
        if rpt_pct_increase > 5:
            evidence = (
                f"Related party revenue increased from {rpt_pct_previous:.1f}% to {rpt_pct_current:.1f}% of total revenue "
                f"(+{rpt_pct_increase:.1f} percentage points). "
                f"Increasing RPT revenue concentration may indicate channel stuffing or artificial sales."
            )

            return self.create_triggered_result(
                evidence=evidence,
                confidence=75.0,
                extracted_data={
                    "rpt_pct_current": rpt_pct_current,
                    "rpt_pct_previous": rpt_pct_previous,
                    "rpt_pct_increase": rpt_pct_increase,
                },
            )

        return self.create_not_triggered_result("Related party revenue percentage stable")


class ComplexSubsidiaryStructureFlag(RedFlagBase):
    """Flag #21: Complex Structure with 20+ Subsidiaries (MEDIUM)."""

    def __init__(self):
        self.flag_number = 21
        self.flag_name = "Complex Structure > 20 Subsidiaries"
        self.category = FlagCategory.RELATED_PARTY
        self.severity = FlagSeverity.MEDIUM
        self.description = "Company has complex structure with many subsidiaries (opacity risk)"

    def check(self, data: Dict) -> RedFlagResult:
        """Check for overly complex corporate structure."""
        financial_data = data.get("financial_data", {})
        notes_text = data.get("sections", {}).get("notes_to_accounts", "")

        # Check structured data for subsidiary list
        rpt_data = financial_data.get("related_party_transactions", {})
        subsidiaries = rpt_data.get("subsidiaries", [])
        associates = rpt_data.get("associates", [])
        joint_ventures = rpt_data.get("joint_ventures", [])

        total_entities = len(subsidiaries) + len(associates) + len(joint_ventures)

        # Text search for entity counts
        notes_lower = notes_text.lower()

        # Try to extract entity count from text
        import re

        subsidiary_patterns = [
            r'(\d+)\s+subsidiar',
            r'subsidiar.*?(\d+)',
            r'(\d+)\s+group compan',
        ]

        extracted_counts = []
        for pattern in subsidiary_patterns:
            matches = re.findall(pattern, notes_lower)
            if matches:
                try:
                    extracted_counts.extend([int(m) for m in matches])
                except:
                    pass

        if extracted_counts:
            max_count = max(extracted_counts)
            total_entities = max(total_entities, max_count)

        # Trigger if > 20 entities
        if total_entities >= 20:
            evidence = (
                f"Complex corporate structure with {total_entities} related entities "
                f"(Subsidiaries: {len(subsidiaries)}, Associates: {len(associates)}, JVs: {len(joint_ventures)}). "
                f"Complex structures can obscure financial reality and facilitate fund transfers."
            )

            return self.create_triggered_result(
                evidence=evidence,
                confidence=80.0,
                extracted_data={
                    "total_entities": total_entities,
                    "subsidiaries_count": len(subsidiaries),
                    "associates_count": len(associates),
                    "jv_count": len(joint_ventures),
                },
            )

        return self.create_not_triggered_result("Corporate structure appears manageable")


class LoansToDirectorsFlag(RedFlagBase):
    """Flag #22: Loans to Directors/Key Management Personnel (HIGH)."""

    def __init__(self):
        self.flag_number = 22
        self.flag_name = "Loans to Directors/KMP"
        self.category = FlagCategory.RELATED_PARTY
        self.severity = FlagSeverity.HIGH
        self.description = "Loans given to directors or key management personnel"

    def check(self, data: Dict) -> RedFlagResult:
        """Check for loans to directors or KMP."""
        financial_data = data.get("financial_data", {})
        notes_text = data.get("sections", {}).get("notes_to_accounts", "")
        governance_text = data.get("sections", {}).get("corporate_governance_report", "")

        rpt_data = financial_data.get("related_party_transactions", {})

        # Check structured data
        director_loans = self.extract_value(rpt_data, "loans_to_kmp", "value", default=0.0)
        kmp_advances = self.extract_value(rpt_data, "advances_to_directors", "value", default=0.0)

        total_director_loans = abs(director_loans) + abs(kmp_advances)

        # Text search for director/KMP loan keywords
        loan_keywords = [
            "loan to director",
            "loan to key management",
            "advance to director",
            "loan to kmp",
            "director borrowing",
            "loan to promoter",
        ]

        combined_text = (notes_text + " " + governance_text).lower()
        loan_mentions = []

        for keyword in loan_keywords:
            if keyword in combined_text:
                loan_mentions.append(keyword)

        # Trigger if any loans to directors/KMP or keyword mentions
        if total_director_loans > 0 or len(loan_mentions) > 0:
            evidence_parts = []

            if total_director_loans > 0:
                evidence_parts.append(
                    f"Loans/advances to Directors/KMP: {total_director_loans:,.0f}"
                )

            if loan_mentions:
                evidence_parts.append(
                    f"Director loan references: {', '.join(set(loan_mentions))}"
                )

            evidence = ". ".join(evidence_parts) + ". Loans to directors/KMP pose significant governance and fund diversion risks."

            return self.create_triggered_result(
                evidence=evidence,
                confidence=95.0,
                extracted_data={
                    "director_loans": total_director_loans,
                    "loan_mentions": loan_mentions,
                },
            )

        return self.create_not_triggered_result("No loans to directors or KMP detected")


class NewRelatedPartiesFlag(RedFlagBase):
    """Flag #23: New Related Parties Added (MEDIUM)."""

    def __init__(self):
        self.flag_number = 23
        self.flag_name = "New Related Parties Added"
        self.category = FlagCategory.RELATED_PARTY
        self.severity = FlagSeverity.MEDIUM
        self.description = "Significant new related parties added during the year"

    def check(self, data: Dict) -> RedFlagResult:
        """Check for newly added related parties."""
        notes_text = data.get("sections", {}).get("notes_to_accounts", "")

        # Text indicators of new related parties
        new_party_keywords = [
            "newly incorporated",
            "new subsidiary",
            "newly acquired",
            "incorporated during the year",
            "became subsidiary",
            "became associate",
            "new related party",
        ]

        notes_lower = notes_text.lower()
        new_party_mentions = []

        for keyword in new_party_keywords:
            if keyword in notes_lower:
                new_party_mentions.append(keyword)

        # Count mentions
        mention_count = len(new_party_mentions)

        # Trigger if multiple new party mentions (>= 2)
        if mention_count >= 2:
            evidence = (
                f"Multiple new related parties added during the year "
                f"({mention_count} references: {', '.join(set(new_party_mentions))}). "
                f"New entities may be used for aggressive accounting or fund transfers."
            )

            return self.create_triggered_result(
                evidence=evidence,
                confidence=70.0,
                extracted_data={
                    "new_party_mentions": new_party_mentions,
                    "mention_count": mention_count,
                },
            )

        return self.create_not_triggered_result("No significant new related parties detected")


# Register all related party flags
flag_registry.register(RPTHighPercentageFlag())
flag_registry.register(LoansToRelatedPartiesFlag())
flag_registry.register(RPTPremiumPricingFlag())
flag_registry.register(RPTRevenueIncreasingFlag())
flag_registry.register(ComplexSubsidiaryStructureFlag())
flag_registry.register(LoansToDirectorsFlag())
flag_registry.register(NewRelatedPartiesFlag())

logger.info("Registered 7 related party flags (Category 3)")
