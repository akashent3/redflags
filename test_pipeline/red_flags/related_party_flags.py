"""Category 3: Related Party Transaction Red Flags (7 flags, 15% weight)."""

import re
import logging
from typing import Dict

from red_flags.models import FlagCategory, FlagSeverity
from red_flags.base import RedFlagBase
from red_flags.registry import flag_registry

logger = logging.getLogger(__name__)


class RPTHighPercentageFlag(RedFlagBase):
    """Flag #17: RPT > 10% of Revenue (HIGH)."""
    def __init__(self):
        self.flag_number = 17
        self.flag_name = "RPT > 10% of Revenue"
        self.category = FlagCategory.RELATED_PARTY
        self.severity = FlagSeverity.HIGH

    def check(self, data: Dict):
        fd = data.get("financial_data", {})
        rpt = fd.get("related_party_transactions", {})
        pl = fd.get("profit_loss", {})
        revenue = self.extract_value(pl, "revenue", "value", default=0.0)
        if not revenue:
            return self.create_not_triggered_result("Revenue data not available")
        total_rpt = 0.0
        for rpt_type in ["sales", "purchases", "loans_given", "loans_taken", "investments", "guarantees", "other"]:
            amount = self.extract_value(rpt, rpt_type, "value", default=0.0)
            total_rpt += abs(amount)
        # Also check total_rpt_amount from structured data
        if total_rpt == 0:
            total_rpt = abs(self.extract_value(rpt, "total_rpt_amount", default=0.0))
        if total_rpt == 0:
            notes_text = data.get("sections", {}).get("notes_to_accounts", "")
            if "related party" in notes_text.lower():
                return self.create_not_triggered_result("RPT mentioned but amounts not extracted (manual review needed)")
            return self.create_not_triggered_result("No RPT data found")
        rpt_pct = (total_rpt / revenue) * 100
        if rpt_pct > 10:
            return self.create_triggered_result(
                evidence=f"Total RPT are {rpt_pct:.1f}% of revenue (RPT: {total_rpt:,.0f}, Revenue: {revenue:,.0f}). High RPT volume increases non-arm's length risk.", confidence=85.0,
                extracted_data={"total_rpt": total_rpt, "revenue": revenue, "rpt_percentage": rpt_pct})
        return self.create_not_triggered_result("RPT within acceptable range")


class LoansToRelatedPartiesFlag(RedFlagBase):
    """Flag #18: Loans to Related Parties (HIGH)."""
    def __init__(self):
        self.flag_number = 18
        self.flag_name = "Loans to Related Parties"
        self.category = FlagCategory.RELATED_PARTY
        self.severity = FlagSeverity.HIGH

    def check(self, data: Dict):
        fd = data.get("financial_data", {})
        rpt = fd.get("related_party_transactions", {})
        notes_text = data.get("sections", {}).get("notes_to_accounts", "")
        loans_given = abs(self.extract_value(rpt, "loans_given", "value", default=0.0))
        advances = abs(self.extract_value(rpt, "advances", "value", default=0.0))
        total_loans = loans_given + advances
        loan_keywords = ["loan given to", "advance to related party", "inter-corporate deposit", "icd given", "funds advanced to"]
        notes_lower = notes_text.lower()
        loan_mentions = sum(1 for kw in loan_keywords if kw in notes_lower)
        if total_loans > 0 or loan_mentions >= 2:
            parts = []
            if total_loans > 0:
                parts.append(f"Loans/advances to related parties: {total_loans:,.0f}")
            if loan_mentions >= 2:
                parts.append(f"Multiple loan references in notes ({loan_mentions} mentions)")
            return self.create_triggered_result(evidence=". ".join(parts) + ". Fund diversion risk.", confidence=90.0, extracted_data={"total_loans": total_loans, "loan_mentions": loan_mentions})
        return self.create_not_triggered_result("No significant loans to related parties")


class RPTPremiumPricingFlag(RedFlagBase):
    """Flag #19: Purchases from RP at Premium (MEDIUM)."""
    def __init__(self):
        self.flag_number = 19
        self.flag_name = "Purchases from RP at Premium"
        self.category = FlagCategory.RELATED_PARTY
        self.severity = FlagSeverity.MEDIUM

    def check(self, data: Dict):
        fd = data.get("financial_data", {})
        rpt = fd.get("related_party_transactions", {})
        pl = fd.get("profit_loss", {})
        notes_text = data.get("sections", {}).get("notes_to_accounts", "")
        rpt_purchases = abs(self.extract_value(rpt, "purchases", "value", default=0.0))
        rpt_expenses = abs(self.extract_value(rpt, "expenses", "value", default=0.0))
        total_rpt_purchases = rpt_purchases + rpt_expenses
        total_cogs = self.extract_value(pl, "cost_of_goods_sold", "value", default=0.0)
        rpt_purchase_pct = (total_rpt_purchases / total_cogs) * 100 if total_cogs > 0 else 0
        premium_keywords = ["arm's length", "market price", "fair value", "transfer pricing", "at cost", "at premium"]
        notes_lower = notes_text.lower()
        premium_mentions = sum(1 for kw in premium_keywords if kw in notes_lower)
        if rpt_purchase_pct > 20 or premium_mentions >= 3:
            parts = []
            if rpt_purchase_pct > 20:
                parts.append(f"Purchases from RP: {rpt_purchase_pct:.1f}% of COGS ({total_rpt_purchases:,.0f})")
            if premium_mentions >= 3:
                parts.append(f"Multiple pricing justifications ({premium_mentions} references)")
            return self.create_triggered_result(evidence=". ".join(parts) + ". Significant RPT purchases require fair pricing scrutiny.", confidence=65.0, extracted_data={"rpt_purchases": total_rpt_purchases, "rpt_purchase_pct": rpt_purchase_pct})
        return self.create_not_triggered_result("RPT purchases appear normal")


class RPTRevenueIncreasingFlag(RedFlagBase):
    """Flag #20: Revenue from RP Increasing (MEDIUM)."""
    def __init__(self):
        self.flag_number = 20
        self.flag_name = "Revenue from RP Increasing"
        self.category = FlagCategory.RELATED_PARTY
        self.severity = FlagSeverity.MEDIUM

    def check(self, data: Dict):
        fd = data.get("financial_data", {})
        rpt = fd.get("related_party_transactions", {})
        pl = fd.get("profit_loss", {})
        rpt_sales_curr = self.extract_value(rpt, "sales", "value", default=0.0)
        rpt_sales_prev = self.extract_value(rpt, "sales", "previous_year", default=0.0)
        rev_curr = self.extract_value(pl, "revenue", "value", default=0.0)
        rev_prev = self.extract_value(pl, "revenue", "previous_year", default=0.0)
        if not rev_curr or not rev_prev:
            return self.create_not_triggered_result("Insufficient revenue data")
        rpt_pct_curr = (abs(rpt_sales_curr) / rev_curr) * 100 if rev_curr else 0
        rpt_pct_prev = (abs(rpt_sales_prev) / rev_prev) * 100 if rev_prev else 0
        increase = rpt_pct_curr - rpt_pct_prev
        if increase > 5:
            return self.create_triggered_result(
                evidence=f"RPT revenue increased from {rpt_pct_prev:.1f}% to {rpt_pct_curr:.1f}% of total (+{increase:.1f}pp). May indicate channel stuffing.", confidence=75.0,
                extracted_data={"rpt_pct_current": rpt_pct_curr, "rpt_pct_previous": rpt_pct_prev, "increase": increase})
        return self.create_not_triggered_result("RPT revenue percentage stable")


class ComplexSubsidiaryStructureFlag(RedFlagBase):
    """Flag #21: Complex Structure > 20 Subsidiaries (MEDIUM)."""
    def __init__(self):
        self.flag_number = 21
        self.flag_name = "Complex Structure > 20 Subsidiaries"
        self.category = FlagCategory.RELATED_PARTY
        self.severity = FlagSeverity.MEDIUM

    def check(self, data: Dict):
        fd = data.get("financial_data", {})
        rpt = fd.get("related_party_transactions", {})
        notes_text = data.get("sections", {}).get("notes_to_accounts", "")
        subs = rpt.get("subsidiaries", [])
        assocs = rpt.get("associates", [])
        jvs = rpt.get("joint_ventures", [])
        total = len(subs) + len(assocs) + len(jvs)
        notes_lower = notes_text.lower()
        patterns = [r'(\d+)\s+subsidiar', r'subsidiar.*?(\d+)', r'(\d+)\s+group compan']
        for pattern in patterns:
            matches = re.findall(pattern, notes_lower)
            if matches:
                try:
                    total = max(total, max(int(m) for m in matches))
                except (ValueError, TypeError):
                    pass
        if total >= 20:
            return self.create_triggered_result(
                evidence=f"Complex corporate structure with {total} related entities. Complex structures can obscure financial reality.", confidence=80.0,
                extracted_data={"total_entities": total})
        return self.create_not_triggered_result("Corporate structure appears manageable")


class LoansToDirectorsFlag(RedFlagBase):
    """Flag #22: Loans to Directors/KMP (HIGH)."""
    def __init__(self):
        self.flag_number = 22
        self.flag_name = "Loans to Directors/KMP"
        self.category = FlagCategory.RELATED_PARTY
        self.severity = FlagSeverity.HIGH

    def check(self, data: Dict):
        fd = data.get("financial_data", {})
        rpt = fd.get("related_party_transactions", {})
        notes_text = data.get("sections", {}).get("notes_to_accounts", "")
        governance_text = data.get("sections", {}).get("corporate_governance", "")
        director_loans = abs(self.extract_value(rpt, "loans_to_kmp", "value", default=0.0))
        kmp_advances = abs(self.extract_value(rpt, "advances_to_directors", "value", default=0.0))
        total = director_loans + kmp_advances
        keywords = ["loan to director", "loan to key management", "advance to director", "loan to kmp", "director borrowing", "loan to promoter"]
        combined = (notes_text + " " + governance_text).lower()
        mentions = [kw for kw in keywords if kw in combined]
        if total > 0 or mentions:
            parts = []
            if total > 0:
                parts.append(f"Loans/advances to Directors/KMP: {total:,.0f}")
            if mentions:
                parts.append(f"Director loan references: {', '.join(set(mentions))}")
            return self.create_triggered_result(evidence=". ".join(parts) + ". Significant governance and fund diversion risk.", confidence=95.0, extracted_data={"director_loans": total, "loan_mentions": mentions})
        return self.create_not_triggered_result("No loans to directors or KMP detected")


class NewRelatedPartiesFlag(RedFlagBase):
    """Flag #23: New Related Parties Added (MEDIUM)."""
    def __init__(self):
        self.flag_number = 23
        self.flag_name = "New Related Parties Added"
        self.category = FlagCategory.RELATED_PARTY
        self.severity = FlagSeverity.MEDIUM

    def check(self, data: Dict):
        notes_text = data.get("sections", {}).get("notes_to_accounts", "")
        keywords = ["newly incorporated", "new subsidiary", "newly acquired", "incorporated during the year", "became subsidiary", "became associate", "new related party"]
        notes_lower = notes_text.lower()
        mentions = [kw for kw in keywords if kw in notes_lower]
        if len(mentions) >= 2:
            return self.create_triggered_result(
                evidence=f"Multiple new related parties added ({len(mentions)} references: {', '.join(set(mentions))}). New entities may be used for fund transfers.", confidence=70.0,
                extracted_data={"mentions": mentions})
        return self.create_not_triggered_result("No significant new related parties detected")


flag_registry.register(RPTHighPercentageFlag())
flag_registry.register(LoansToRelatedPartiesFlag())
flag_registry.register(RPTPremiumPricingFlag())
flag_registry.register(RPTRevenueIncreasingFlag())
flag_registry.register(ComplexSubsidiaryStructureFlag())
flag_registry.register(LoansToDirectorsFlag())
flag_registry.register(NewRelatedPartiesFlag())
