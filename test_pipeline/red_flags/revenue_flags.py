"""Category 7: Revenue Quality Red Flags (5 flags, 5% weight)."""

import re
import logging
from typing import Dict

from red_flags.models import FlagCategory, FlagSeverity
from red_flags.base import RedFlagBase
from red_flags.registry import flag_registry

logger = logging.getLogger(__name__)


class Q4RevenueConcentrationFlag(RedFlagBase):
    """Flag #44: Revenue Concentrated in Q4 (MEDIUM)."""
    def __init__(self):
        self.flag_number = 44
        self.flag_name = "Revenue Concentrated in Q4"
        self.category = FlagCategory.REVENUE
        self.severity = FlagSeverity.MEDIUM

    def check(self, data: Dict):
        fd = data.get("financial_data", {})
        quarterly = fd.get("quarterly_revenue", {})
        q4 = self.extract_value(quarterly, "q4", "value", default=0.0)
        annual = self.extract_value(fd, "profit_loss", "revenue", "value", default=0.0)
        if not annual or not q4:
            return self.create_not_triggered_result("Quarterly/annual revenue data not available")
        pct = (q4 / annual) * 100
        if pct > 40:
            return self.create_triggered_result(evidence=f"Q4 revenue is {pct:.1f}% of annual ({q4:,.0f} of {annual:,.0f}). May indicate channel stuffing.", confidence=75.0, extracted_data={"q4_percentage": pct, "q4_revenue": q4, "annual_revenue": annual})
        return self.create_not_triggered_result("Revenue distribution balanced")


class CustomerConcentrationFlag(RedFlagBase):
    """Flag #45: Top Customer > 25% of Revenue (MEDIUM)."""
    def __init__(self):
        self.flag_number = 45
        self.flag_name = "Top Customer > 25%"
        self.category = FlagCategory.REVENUE
        self.severity = FlagSeverity.MEDIUM

    def check(self, data: Dict):
        fd = data.get("financial_data", {})
        notes = fd.get("notes", {})
        notes_text = data.get("sections", {}).get("notes_to_accounts", "")
        top_pct = self.extract_value(notes, "top_customer_percentage", default=0.0)
        if top_pct == 0 and notes_text:
            notes_lower = notes_text.lower()
            if any(kw in notes_lower for kw in ["top customer", "largest customer", "single customer", "customer concentration"]):
                matches = re.findall(r'(?:customer|single).*?(\d+(?:\.\d+)?)\s*%', notes_lower)
                if matches:
                    try:
                        top_pct = max(float(m) for m in matches if 0 < float(m) <= 100)
                    except (ValueError, TypeError):
                        pass
        if top_pct > 25:
            return self.create_triggered_result(evidence=f"Top customer accounts for {top_pct:.1f}% of revenue. High dependency risk.", confidence=80.0, extracted_data={"top_customer_pct": top_pct})
        return self.create_not_triggered_result("No significant customer concentration")


class RevenuePolicyChangeFlag(RedFlagBase):
    """Flag #46: Revenue Recognition Policy Changed (HIGH)."""
    def __init__(self):
        self.flag_number = 46
        self.flag_name = "Revenue Policy Change"
        self.category = FlagCategory.REVENUE
        self.severity = FlagSeverity.HIGH

    def check(self, data: Dict):
        notes_text = data.get("sections", {}).get("notes_to_accounts", "")
        combined = notes_text.lower()
        keywords = ["change in revenue recognition", "revenue recognition policy changed", "revised revenue recognition", "adopted new revenue standard", "change in accounting policy", "ind as 115", "ifrs 15", "revenue from contracts with customers"]
        mentions = [kw for kw in keywords if kw in combined]
        contextual = re.search(r'change.{0,50}revenue.{0,50}recogni|revenue.{0,50}recogni.{0,50}change', combined)
        if mentions or contextual:
            reason = "Adoption of new accounting standard" if any(x in combined for x in ["ind as", "ifrs"]) else "Not specified"
            return self.create_triggered_result(evidence=f"Revenue recognition policy change detected ({len(mentions)} references). Reason: {reason}. Can distort comparisons.", confidence=90.0, extracted_data={"mentions": mentions, "reason": reason})
        return self.create_not_triggered_result("No revenue recognition policy changes")


class UnbilledRevenueGrowingFlag(RedFlagBase):
    """Flag #47: Unbilled Revenue Growing Faster (MEDIUM)."""
    def __init__(self):
        self.flag_number = 47
        self.flag_name = "Unbilled Revenue Growing"
        self.category = FlagCategory.REVENUE
        self.severity = FlagSeverity.MEDIUM

    def check(self, data: Dict):
        fd = data.get("financial_data", {})
        bs = fd.get("balance_sheet", {})
        pl = fd.get("profit_loss", {})
        ub_curr = self.extract_value(bs, "current_assets", "unbilled_revenue", "value", default=0.0)
        ub_prev = self.extract_value(bs, "current_assets", "unbilled_revenue", "previous_year", default=0.0)
        if ub_curr == 0:
            ub_curr = self.extract_value(bs, "current_assets", "contract_assets", "value", default=0.0)
            ub_prev = self.extract_value(bs, "current_assets", "contract_assets", "previous_year", default=0.0)
        rev_curr = self.extract_value(pl, "revenue", "value", default=0.0)
        rev_prev = self.extract_value(pl, "revenue", "previous_year", default=0.0)
        if not all([ub_curr, ub_prev, rev_curr, rev_prev]):
            return self.create_not_triggered_result("Insufficient unbilled revenue data")
        ub_growth = self.calculate_growth_rate(ub_curr, ub_prev)
        rev_growth = self.calculate_growth_rate(rev_curr, rev_prev)
        if ub_growth > rev_growth + 0.15:
            return self.create_triggered_result(
                evidence=f"Unbilled revenue grew {self.safe_percentage(ub_growth):.1f}% vs revenue {self.safe_percentage(rev_growth):.1f}%. May indicate aggressive recognition.", confidence=75.0,
                extracted_data={"unbilled_growth": ub_growth, "revenue_growth": rev_growth})
        return self.create_not_triggered_result("Unbilled revenue growth normal")


class UnusualExportGeographyFlag(RedFlagBase):
    """Flag #48: Unusual Export Geography (LOW)."""
    def __init__(self):
        self.flag_number = 48
        self.flag_name = "Unusual Export Geography"
        self.category = FlagCategory.REVENUE
        self.severity = FlagSeverity.LOW

    def check(self, data: Dict):
        notes_text = data.get("sections", {}).get("notes_to_accounts", "")
        notes_lower = notes_text.lower()
        if not any(kw in notes_lower for kw in ["geographic", "geographical", "segment", "export"]):
            return self.create_not_triggered_result("Geographic revenue breakdown not found")
        havens = ["cayman", "bermuda", "british virgin islands", "bvi", "mauritius", "seychelles", "bahamas", "panama", "luxembourg", "jersey", "guernsey", "isle of man", "monaco", "liechtenstein"]
        found = [j for j in havens if j in notes_lower]
        if found:
            return self.create_triggered_result(evidence=f"Exports to tax haven jurisdictions: {', '.join(set(found))}. May indicate transfer pricing schemes.", confidence=60.0, extracted_data={"jurisdictions": found})
        return self.create_not_triggered_result("No unusual export geographies")


flag_registry.register(Q4RevenueConcentrationFlag())
flag_registry.register(CustomerConcentrationFlag())
flag_registry.register(RevenuePolicyChangeFlag())
flag_registry.register(UnbilledRevenueGrowingFlag())
flag_registry.register(UnusualExportGeographyFlag())
