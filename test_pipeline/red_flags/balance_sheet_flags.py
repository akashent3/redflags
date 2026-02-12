"""Category 6: Balance Sheet Red Flags (7 flags, 10% weight)."""

import re
import logging
from typing import Dict

from red_flags.models import FlagCategory, FlagSeverity
from red_flags.base import RedFlagBase
from red_flags.registry import flag_registry

logger = logging.getLogger(__name__)


class DebtGrowingFasterFlag(RedFlagBase):
    """Flag #37: Debt Growing Faster than Equity (HIGH)."""
    def __init__(self):
        self.flag_number = 37
        self.flag_name = "Debt Growing > Equity"
        self.category = FlagCategory.BALANCE_SHEET
        self.severity = FlagSeverity.HIGH

    def check(self, data: Dict):
        fd = data.get("financial_data", {})
        bs = fd.get("balance_sheet", {})
        debt_curr = self.extract_value(bs, "total_debt", "value", default=0.0)
        debt_prev = self.extract_value(bs, "total_debt", "previous_year", default=0.0)
        eq_curr = self.extract_value(bs, "shareholders_equity", "value", default=0.0)
        eq_prev = self.extract_value(bs, "shareholders_equity", "previous_year", default=0.0)
        if not all([debt_curr, debt_prev, eq_curr, eq_prev]):
            return self.create_not_triggered_result("Insufficient debt/equity data")
        debt_growth = self.calculate_growth_rate(debt_curr, debt_prev)
        eq_growth = self.calculate_growth_rate(eq_curr, eq_prev)
        de_ratio = self.calculate_ratio(debt_curr, eq_curr)
        if debt_growth > eq_growth + 0.20:
            return self.create_triggered_result(
                evidence=f"Debt grew {self.safe_percentage(debt_growth):.1f}% vs equity {self.safe_percentage(eq_growth):.1f}% (D/E: {de_ratio:.2f}). Excessive debt growth increases risk.", confidence=85.0,
                extracted_data={"debt_growth": debt_growth, "equity_growth": eq_growth, "de_ratio": de_ratio})
        return self.create_not_triggered_result("Debt growth aligned with equity")


class InterestCoverageLowFlag(RedFlagBase):
    """Flag #38: Interest Coverage < 2x (HIGH)."""
    def __init__(self):
        self.flag_number = 38
        self.flag_name = "Interest Coverage < 2x"
        self.category = FlagCategory.BALANCE_SHEET
        self.severity = FlagSeverity.HIGH

    def check(self, data: Dict):
        fd = data.get("financial_data", {})
        pl = fd.get("profit_loss", {})
        ebit = self.extract_value(pl, "ebit", "value", default=0.0)
        interest = self.extract_value(pl, "interest_expense", "value", default=0.0)
        if ebit == 0:
            pat = self.extract_value(pl, "net_profit", "value", default=0.0)
            tax = self.extract_value(pl, "tax_expense", "value", default=0.0)
            ebit = pat + tax + interest
        if not interest or interest == 0:
            return self.create_not_triggered_result("No interest expense or debt-free company")
        if ebit <= 0:
            return self.create_triggered_result(evidence=f"EBIT is negative ({ebit:,.0f}) with interest of {interest:,.0f}. Cannot service debt.", confidence=100.0, extracted_data={"ebit": ebit, "interest": interest, "coverage": 0.0})
        coverage = self.calculate_ratio(ebit, interest)
        if coverage < 2.0:
            return self.create_triggered_result(evidence=f"Interest Coverage: {coverage:.2f}x (EBIT: {ebit:,.0f}, Interest: {interest:,.0f}). Below 2x indicates difficulty servicing debt.", confidence=90.0, extracted_data={"coverage": coverage, "ebit": ebit, "interest": interest})
        return self.create_not_triggered_result("Interest coverage adequate")


class ShortTermDebtHighFlag(RedFlagBase):
    """Flag #39: Short-term Debt > 60% of Total Debt (HIGH)."""
    def __init__(self):
        self.flag_number = 39
        self.flag_name = "ST Debt Funding LT Assets"
        self.category = FlagCategory.BALANCE_SHEET
        self.severity = FlagSeverity.HIGH

    def check(self, data: Dict):
        fd = data.get("financial_data", {})
        bs = fd.get("balance_sheet", {})
        st_debt = self.extract_value(bs, "current_liabilities", "short_term_borrowings", "value", default=0.0)
        lt_debt = self.extract_value(bs, "non_current_liabilities", "long_term_borrowings", "value", default=0.0)
        total = st_debt + lt_debt
        if total == 0:
            return self.create_not_triggered_result("Company has minimal debt")
        st_pct = (st_debt / total) * 100
        if st_pct > 60:
            return self.create_triggered_result(evidence=f"Short-term debt is {st_pct:.1f}% of total (ST: {st_debt:,.0f}, Total: {total:,.0f}). Refinancing risk.", confidence=85.0, extracted_data={"st_pct": st_pct, "st_debt": st_debt, "total_debt": total})
        return self.create_not_triggered_result("Debt maturity profile balanced")


class ContingentLiabilitiesHighFlag(RedFlagBase):
    """Flag #40: Contingent Liabilities > 20% of Net Worth (HIGH)."""
    def __init__(self):
        self.flag_number = 40
        self.flag_name = "Contingent Liabilities > 20% NW"
        self.category = FlagCategory.BALANCE_SHEET
        self.severity = FlagSeverity.HIGH

    def check(self, data: Dict):
        fd = data.get("financial_data", {})
        notes = fd.get("notes", {})
        bs = fd.get("balance_sheet", {})
        contingent = self.extract_value(notes, "contingent_liabilities", "value", default=0.0)
        net_worth = self.extract_value(bs, "shareholders_equity", "value", default=0.0)
        if contingent == 0:
            notes_text = data.get("sections", {}).get("notes_to_accounts", "").lower()
            if "contingent liabilit" in notes_text:
                matches = re.findall(r'contingent.*?(?:rs|inr|₹)\.?\s*(\d+(?:,\d+)*(?:\.\d+)?)', notes_text)
                if matches:
                    try:
                        contingent = max(float(m.replace(',', '')) for m in matches)
                    except (ValueError, TypeError):
                        pass
        if not net_worth:
            return self.create_not_triggered_result("Net worth data not available")
        if contingent == 0:
            return self.create_not_triggered_result("No significant contingent liabilities")
        pct = (contingent / abs(net_worth)) * 100
        if pct > 20:
            return self.create_triggered_result(evidence=f"Contingent liabilities are {pct:.1f}% of net worth ({contingent:,.0f} vs {net_worth:,.0f}). Significant off-balance-sheet risk.", confidence=80.0, extracted_data={"contingent": contingent, "net_worth": net_worth, "pct": pct})
        return self.create_not_triggered_result("Contingent liabilities within acceptable range")


class FrequentDebtRestructuringFlag(RedFlagBase):
    """Flag #41: Frequent Debt Restructuring (MEDIUM)."""
    def __init__(self):
        self.flag_number = 41
        self.flag_name = "Frequent Debt Restructuring"
        self.category = FlagCategory.BALANCE_SHEET
        self.severity = FlagSeverity.MEDIUM

    def check(self, data: Dict):
        notes = data.get("sections", {}).get("notes_to_accounts", "")
        dr = data.get("sections", {}).get("directors_report", "")
        combined = (notes + " " + dr).lower()
        keywords = ["debt restructur", "loan restructur", "restructuring of debt", "debt renegotiat", "loan renegotiat", "refinanc", "debt repayment rescheduled", "restructuring scheme", "corporate debt restructuring", "cdr"]
        mentions = [kw for kw in keywords if kw in combined]
        if mentions:
            return self.create_triggered_result(evidence=f"Debt restructuring detected ({len(mentions)} references: {', '.join(set(mentions[:3]))}). Indicates financial stress.", confidence=85.0, extracted_data={"mentions": mentions})
        return self.create_not_triggered_result("No debt restructuring detected")


class HeavyAssetPledgingFlag(RedFlagBase):
    """Flag #42: Heavy Asset Pledging (MEDIUM)."""
    def __init__(self):
        self.flag_number = 42
        self.flag_name = "Heavy Asset Pledging"
        self.category = FlagCategory.BALANCE_SHEET
        self.severity = FlagSeverity.MEDIUM

    def check(self, data: Dict):
        fd = data.get("financial_data", {})
        notes_data = fd.get("notes", {})
        bs = fd.get("balance_sheet", {})
        notes_text = data.get("sections", {}).get("notes_to_accounts", "")
        pledged = self.extract_value(notes_data, "assets_pledged", "value", default=0.0)
        total_assets = self.extract_value(bs, "total_assets", "value", default=0.0)
        pledge_pct = (pledged / total_assets) * 100 if pledged > 0 and total_assets > 0 else 0
        keywords = ["asset pledged", "assets pledged", "charge created", "hypothecated", "mortgaged", "security for borrowing", "secured by"]
        notes_lower = notes_text.lower()
        mentions = sum(1 for kw in keywords if kw in notes_lower)
        if pledge_pct > 50 or mentions >= 5:
            parts = []
            if pledge_pct > 50:
                parts.append(f"Assets pledged: {pledge_pct:.1f}% of total assets")
            if mentions >= 5:
                parts.append(f"Extensive pledging disclosures ({mentions} references)")
            return self.create_triggered_result(evidence=". ".join(parts) + ". Reduces financial flexibility.", confidence=75.0, extracted_data={"pledge_pct": pledge_pct, "mentions": mentions})
        return self.create_not_triggered_result("Asset pledging within normal range")


class IntangiblesGrowingFastFlag(RedFlagBase):
    """Flag #43: Intangible Assets Growing Fast (MEDIUM)."""
    def __init__(self):
        self.flag_number = 43
        self.flag_name = "Intangibles Growing Fast"
        self.category = FlagCategory.BALANCE_SHEET
        self.severity = FlagSeverity.MEDIUM

    def check(self, data: Dict):
        fd = data.get("financial_data", {})
        bs = fd.get("balance_sheet", {})
        int_curr = self.extract_value(bs, "non_current_assets", "intangible_assets", "value", default=0.0)
        int_prev = self.extract_value(bs, "non_current_assets", "intangible_assets", "previous_year", default=0.0)
        if not int_curr:
            return self.create_not_triggered_result("No significant intangible assets")
        if not int_prev:
            return self.create_not_triggered_result("Cannot calculate growth (previous year missing)")
        growth = self.calculate_growth_rate(int_curr, int_prev)
        total_assets = self.extract_value(bs, "total_assets", "value", default=0.0)
        int_pct = (int_curr / total_assets) * 100 if total_assets else 0
        if growth > 0.30 or int_pct > 20:
            parts = []
            if growth > 0.30:
                parts.append(f"Intangibles grew {self.safe_percentage(growth):.1f}% ({int_prev:,.0f} to {int_curr:,.0f})")
            if int_pct > 20:
                parts.append(f"Intangibles are {int_pct:.1f}% of total assets")
            return self.create_triggered_result(evidence=". ".join(parts) + ". May indicate aggressive capitalization.", confidence=70.0, extracted_data={"growth": growth, "int_pct": int_pct})
        return self.create_not_triggered_result("Intangible asset growth is normal")


flag_registry.register(DebtGrowingFasterFlag())
flag_registry.register(InterestCoverageLowFlag())
flag_registry.register(ShortTermDebtHighFlag())
flag_registry.register(ContingentLiabilitiesHighFlag())
flag_registry.register(FrequentDebtRestructuringFlag())
flag_registry.register(HeavyAssetPledgingFlag())
flag_registry.register(IntangiblesGrowingFastFlag())
