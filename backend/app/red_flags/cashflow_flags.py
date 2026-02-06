"""Category 2: Cash Flow Red Flags (8 flags, 18% weight).

This category has the second-highest weight as cash flow quality is a critical
indicator of earnings quality and potential accounting manipulation.
"""

import logging
from typing import Dict

from app.models.red_flag import FlagCategory, FlagSeverity
from app.red_flags.base import RedFlagBase, RedFlagResult
from app.red_flags.registry import flag_registry

logger = logging.getLogger(__name__)


class ProfitGrowingCFOFlatFlag(RedFlagBase):
    """Flag #9: Profit Growing but CFO Flat (HIGH)."""

    def __init__(self):
        self.flag_number = 9
        self.flag_name = "Profit Growing, CFO Flat"
        self.category = FlagCategory.CASH_FLOW
        self.severity = FlagSeverity.HIGH
        self.description = "PAT growing rapidly but Cash Flow from Operations is flat/declining"

    def check(self, data: Dict) -> RedFlagResult:
        """Check for divergence between profit and cash flow growth."""
        financial_data = data.get("financial_data", {})

        # Extract PAT and CFO values
        profit_loss = financial_data.get("profit_loss", {})
        cash_flow = financial_data.get("cash_flow", {})

        pat_current = self.extract_value(profit_loss, "net_profit", "value", default=0.0)
        cfo_current = self.extract_value(cash_flow, "cash_from_operations", "value", default=0.0)

        # Check if we have multi-year data
        pat_previous = self.extract_value(profit_loss, "net_profit", "previous_year", default=0.0)
        cfo_previous = self.extract_value(cash_flow, "cash_from_operations", "previous_year", default=0.0)

        if not all([pat_current, pat_previous, cfo_current, cfo_previous]):
            return self.create_not_triggered_result("Insufficient data for PAT/CFO comparison")

        # Calculate growth rates
        pat_growth = self.calculate_growth_rate(pat_current, pat_previous)
        cfo_growth = self.calculate_growth_rate(cfo_current, cfo_previous)

        # Calculate CFO/PAT ratio
        cfo_pat_ratio = self.calculate_ratio(cfo_current, pat_current)

        # Trigger conditions:
        # 1. PAT growing > 15% but CFO growing < 5%
        # 2. CFO/PAT ratio < 0.5
        is_diverging = pat_growth > 0.15 and cfo_growth < 0.05
        is_low_ratio = cfo_pat_ratio < 0.5

        if is_diverging or is_low_ratio:
            evidence_parts = []

            if is_diverging:
                evidence_parts.append(
                    f"PAT growing at {self.safe_percentage(pat_growth):.1f}% "
                    f"while CFO growing at only {self.safe_percentage(cfo_growth):.1f}%"
                )

            if is_low_ratio:
                evidence_parts.append(
                    f"CFO/PAT ratio is {cfo_pat_ratio:.2f} (below 0.5 threshold, indicating poor cash conversion)"
                )

            evidence = ". ".join(evidence_parts)

            return self.create_triggered_result(
                evidence=evidence,
                confidence=90.0,
                extracted_data={
                    "pat_growth": pat_growth,
                    "cfo_growth": cfo_growth,
                    "cfo_pat_ratio": cfo_pat_ratio,
                    "pat_current": pat_current,
                    "cfo_current": cfo_current,
                },
            )

        return self.create_not_triggered_result("PAT and CFO growth aligned")


class ReceivablesGrowthFlag(RedFlagBase):
    """Flag #10: Receivables Growing Faster than Revenue (HIGH)."""

    def __init__(self):
        self.flag_number = 10
        self.flag_name = "Receivables > Revenue Growth"
        self.category = FlagCategory.CASH_FLOW
        self.severity = FlagSeverity.HIGH
        self.description = "Trade receivables growing faster than revenue (potential channel stuffing)"

    def check(self, data: Dict) -> RedFlagResult:
        """Check if receivables are growing faster than revenue."""
        financial_data = data.get("financial_data", {})

        balance_sheet = financial_data.get("balance_sheet", {})
        profit_loss = financial_data.get("profit_loss", {})

        # Extract current and previous year values
        receivables_current = self.extract_value(balance_sheet, "current_assets", "trade_receivables", "value", default=0.0)
        receivables_previous = self.extract_value(balance_sheet, "current_assets", "trade_receivables", "previous_year", default=0.0)

        revenue_current = self.extract_value(profit_loss, "revenue", "value", default=0.0)
        revenue_previous = self.extract_value(profit_loss, "revenue", "previous_year", default=0.0)

        if not all([receivables_current, receivables_previous, revenue_current, revenue_previous]):
            return self.create_not_triggered_result("Insufficient data for receivables/revenue comparison")

        # Calculate growth rates
        receivables_growth = self.calculate_growth_rate(receivables_current, receivables_previous)
        revenue_growth = self.calculate_growth_rate(revenue_current, revenue_previous)

        # Calculate Days Sales Outstanding (DSO)
        dso_current = (receivables_current / revenue_current) * 365
        dso_previous = (receivables_previous / revenue_previous) * 365

        # Trigger if receivables growing > revenue + 10%
        growth_divergence = receivables_growth > revenue_growth + 0.10
        dso_increasing = dso_current > dso_previous + 10  # DSO increased by 10+ days

        if growth_divergence or dso_increasing:
            evidence_parts = []

            if growth_divergence:
                evidence_parts.append(
                    f"Receivables grew {self.safe_percentage(receivables_growth):.1f}% "
                    f"while revenue grew only {self.safe_percentage(revenue_growth):.1f}% "
                    f"(divergence: {self.safe_percentage(receivables_growth - revenue_growth):.1f}%)"
                )

            if dso_increasing:
                evidence_parts.append(
                    f"Days Sales Outstanding increased from {dso_previous:.1f} to {dso_current:.1f} days "
                    f"(+{dso_current - dso_previous:.1f} days)"
                )

            evidence = ". ".join(evidence_parts)

            return self.create_triggered_result(
                evidence=evidence,
                confidence=85.0,
                extracted_data={
                    "receivables_growth": receivables_growth,
                    "revenue_growth": revenue_growth,
                    "dso_current": dso_current,
                    "dso_previous": dso_previous,
                },
            )

        return self.create_not_triggered_result("Receivables growth aligned with revenue")


class InventoryGrowthFlag(RedFlagBase):
    """Flag #11: Inventory Growing Faster than COGS (HIGH)."""

    def __init__(self):
        self.flag_number = 11
        self.flag_name = "Inventory > COGS Growth"
        self.category = FlagCategory.CASH_FLOW
        self.severity = FlagSeverity.HIGH
        self.description = "Inventory growing faster than Cost of Goods Sold (potential obsolescence)"

    def check(self, data: Dict) -> RedFlagResult:
        """Check if inventory is growing faster than COGS."""
        financial_data = data.get("financial_data", {})

        balance_sheet = financial_data.get("balance_sheet", {})
        profit_loss = financial_data.get("profit_loss", {})

        # Extract values
        inventory_current = self.extract_value(balance_sheet, "current_assets", "inventory", "value", default=0.0)
        inventory_previous = self.extract_value(balance_sheet, "current_assets", "inventory", "previous_year", default=0.0)

        cogs_current = self.extract_value(profit_loss, "cost_of_goods_sold", "value", default=0.0)
        cogs_previous = self.extract_value(profit_loss, "cost_of_goods_sold", "previous_year", default=0.0)

        if not all([inventory_current, inventory_previous, cogs_current, cogs_previous]):
            return self.create_not_triggered_result("Insufficient data for inventory/COGS comparison")

        # Calculate growth rates
        inventory_growth = self.calculate_growth_rate(inventory_current, inventory_previous)
        cogs_growth = self.calculate_growth_rate(cogs_current, cogs_previous)

        # Calculate Days Inventory Outstanding (DIO)
        dio_current = (inventory_current / cogs_current) * 365
        dio_previous = (inventory_previous / cogs_previous) * 365

        # Trigger if inventory growing > COGS + 15%
        growth_divergence = inventory_growth > cogs_growth + 0.15
        dio_increasing = dio_current > dio_previous + 15  # DIO increased by 15+ days

        if growth_divergence or dio_increasing:
            evidence_parts = []

            if growth_divergence:
                evidence_parts.append(
                    f"Inventory grew {self.safe_percentage(inventory_growth):.1f}% "
                    f"while COGS grew only {self.safe_percentage(cogs_growth):.1f}% "
                    f"(divergence: {self.safe_percentage(inventory_growth - cogs_growth):.1f}%)"
                )

            if dio_increasing:
                evidence_parts.append(
                    f"Days Inventory Outstanding increased from {dio_previous:.1f} to {dio_current:.1f} days "
                    f"(+{dio_current - dio_previous:.1f} days)"
                )

            evidence = ". ".join(evidence_parts)

            return self.create_triggered_result(
                evidence=evidence,
                confidence=85.0,
                extracted_data={
                    "inventory_growth": inventory_growth,
                    "cogs_growth": cogs_growth,
                    "dio_current": dio_current,
                    "dio_previous": dio_previous,
                },
            )

        return self.create_not_triggered_result("Inventory growth aligned with COGS")


class CapexDepreciationFlag(RedFlagBase):
    """Flag #12: Capex Significantly Higher than Depreciation (MEDIUM)."""

    def __init__(self):
        self.flag_number = 12
        self.flag_name = "Capex >> Depreciation"
        self.category = FlagCategory.CASH_FLOW
        self.severity = FlagSeverity.MEDIUM
        self.description = "Capital expenditure significantly exceeds depreciation (aggressive expansion or capitalization)"

    def check(self, data: Dict) -> RedFlagResult:
        """Check if capex is excessively high compared to depreciation."""
        financial_data = data.get("financial_data", {})

        cash_flow = financial_data.get("cash_flow", {})
        profit_loss = financial_data.get("profit_loss", {})

        # Extract values
        capex_current = abs(self.extract_value(cash_flow, "capital_expenditure", "value", default=0.0))
        depreciation_current = self.extract_value(profit_loss, "depreciation", "value", default=0.0)

        capex_previous = abs(self.extract_value(cash_flow, "capital_expenditure", "previous_year", default=0.0))
        depreciation_previous = self.extract_value(profit_loss, "depreciation", "previous_year", default=0.0)

        if not all([capex_current, depreciation_current]):
            return self.create_not_triggered_result("Insufficient capex/depreciation data")

        # Calculate ratios
        capex_dep_ratio_current = self.calculate_ratio(capex_current, depreciation_current)
        capex_dep_ratio_previous = self.calculate_ratio(capex_previous, depreciation_previous) if depreciation_previous else 0.0

        # Trigger if ratio > 3.0 for current year or sustained high ratio
        is_high_ratio = capex_dep_ratio_current > 3.0
        is_sustained = capex_dep_ratio_current > 2.5 and capex_dep_ratio_previous > 2.5

        if is_high_ratio or is_sustained:
            evidence = (
                f"Capex/Depreciation ratio is {capex_dep_ratio_current:.2f}x "
                f"(Capex: {capex_current:,.0f}, Depreciation: {depreciation_current:,.0f}). "
            )

            if is_sustained:
                evidence += f"Previous year ratio was {capex_dep_ratio_previous:.2f}x (sustained high capex). "

            evidence += "High capex may indicate aggressive expansion or capitalization of expenses."

            return self.create_triggered_result(
                evidence=evidence,
                confidence=75.0,
                extracted_data={
                    "capex_dep_ratio_current": capex_dep_ratio_current,
                    "capex_dep_ratio_previous": capex_dep_ratio_previous,
                    "capex_current": capex_current,
                    "depreciation_current": depreciation_current,
                },
            )

        return self.create_not_triggered_result("Capex/Depreciation ratio within normal range")


class FrequentExceptionalItemsFlag(RedFlagBase):
    """Flag #13: Frequent Exceptional Items (MEDIUM)."""

    def __init__(self):
        self.flag_number = 13
        self.flag_name = "Frequent Exceptional Items"
        self.category = FlagCategory.CASH_FLOW
        self.severity = FlagSeverity.MEDIUM
        self.description = "Company reports exceptional items frequently (income smoothing concern)"

    def check(self, data: Dict) -> RedFlagResult:
        """Check for frequent exceptional items in P&L."""
        financial_data = data.get("financial_data", {})
        notes_text = data.get("sections", {}).get("notes_to_accounts", "")
        profit_loss = financial_data.get("profit_loss", {})

        # Check structured data for exceptional items
        exceptional_items = profit_loss.get("exceptional_items", {})
        current_exceptional = self.extract_value(exceptional_items, "value", default=0.0)
        previous_exceptional = self.extract_value(exceptional_items, "previous_year", default=0.0)

        # Check notes text for exceptional item mentions
        exceptional_keywords = [
            "exceptional item",
            "exceptional items",
            "extraordinary item",
            "one-time charge",
            "non-recurring",
            "restructuring charge",
        ]

        notes_lower = notes_text.lower()
        keyword_mentions = sum(1 for keyword in exceptional_keywords if keyword in notes_lower)

        # Trigger if:
        # 1. Current year has exceptional items AND previous year had them (frequent)
        # 2. Multiple keyword mentions in notes (>= 3)
        has_current = abs(current_exceptional) > 0
        has_previous = abs(previous_exceptional) > 0
        has_frequent_mentions = keyword_mentions >= 3

        if (has_current and has_previous) or has_frequent_mentions:
            evidence_parts = []

            if has_current and has_previous:
                evidence_parts.append(
                    f"Exceptional items present in multiple years "
                    f"(Current: {current_exceptional:,.0f}, Previous: {previous_exceptional:,.0f})"
                )

            if has_frequent_mentions:
                evidence_parts.append(
                    f"Multiple exceptional item mentions in notes ({keyword_mentions} references)"
                )

            evidence = ". ".join(evidence_parts) + ". Frequent exceptional items may indicate income smoothing."

            return self.create_triggered_result(
                evidence=evidence,
                confidence=70.0,
                extracted_data={
                    "current_exceptional": current_exceptional,
                    "previous_exceptional": previous_exceptional,
                    "keyword_mentions": keyword_mentions,
                },
            )

        return self.create_not_triggered_result("No frequent exceptional items detected")


class NegativeCFOFlag(RedFlagBase):
    """Flag #14: Cash Flow from Operations Negative for 2+ Years (HIGH)."""

    def __init__(self):
        self.flag_number = 14
        self.flag_name = "CFO Negative 2+ Years"
        self.category = FlagCategory.CASH_FLOW
        self.severity = FlagSeverity.HIGH
        self.description = "Operating cash flow negative for multiple consecutive years"

    def check(self, data: Dict) -> RedFlagResult:
        """Check if CFO has been negative for 2+ years."""
        financial_data = data.get("financial_data", {})
        cash_flow = financial_data.get("cash_flow", {})

        cfo_current = self.extract_value(cash_flow, "cash_from_operations", "value", default=0.0)
        cfo_previous = self.extract_value(cash_flow, "cash_from_operations", "previous_year", default=0.0)

        # Check if we have data
        if cfo_current == 0.0 and cfo_previous == 0.0:
            return self.create_not_triggered_result("Cash flow data not available")

        # Trigger if both years are negative
        is_current_negative = cfo_current < 0
        is_previous_negative = cfo_previous < 0

        if is_current_negative and is_previous_negative:
            evidence = (
                f"Operating cash flow negative for 2+ consecutive years "
                f"(Current: {cfo_current:,.0f}, Previous: {cfo_previous:,.0f}). "
                f"Indicates core business is not generating cash."
            )

            return self.create_triggered_result(
                evidence=evidence,
                confidence=95.0,
                extracted_data={
                    "cfo_current": cfo_current,
                    "cfo_previous": cfo_previous,
                },
            )

        return self.create_not_triggered_result("Operating cash flow positive")


class CashConversionCycleFlag(RedFlagBase):
    """Flag #15: Cash Conversion Cycle Increasing (MEDIUM)."""

    def __init__(self):
        self.flag_number = 15
        self.flag_name = "Cash Conversion Cycle Up"
        self.category = FlagCategory.CASH_FLOW
        self.severity = FlagSeverity.MEDIUM
        self.description = "Cash conversion cycle increased significantly (working capital deterioration)"

    def check(self, data: Dict) -> RedFlagResult:
        """Check if Cash Conversion Cycle (CCC) is increasing."""
        financial_data = data.get("financial_data", {})

        balance_sheet = financial_data.get("balance_sheet", {})
        profit_loss = financial_data.get("profit_loss", {})

        # Extract values for current year
        receivables_current = self.extract_value(balance_sheet, "current_assets", "trade_receivables", "value", default=0.0)
        inventory_current = self.extract_value(balance_sheet, "current_assets", "inventory", "value", default=0.0)
        payables_current = self.extract_value(balance_sheet, "current_liabilities", "trade_payables", "value", default=0.0)
        revenue_current = self.extract_value(profit_loss, "revenue", "value", default=0.0)
        cogs_current = self.extract_value(profit_loss, "cost_of_goods_sold", "value", default=0.0)

        # Extract values for previous year
        receivables_previous = self.extract_value(balance_sheet, "current_assets", "trade_receivables", "previous_year", default=0.0)
        inventory_previous = self.extract_value(balance_sheet, "current_assets", "inventory", "previous_year", default=0.0)
        payables_previous = self.extract_value(balance_sheet, "current_liabilities", "trade_payables", "previous_year", default=0.0)
        revenue_previous = self.extract_value(profit_loss, "revenue", "previous_year", default=0.0)
        cogs_previous = self.extract_value(profit_loss, "cost_of_goods_sold", "previous_year", default=0.0)

        # Check if we have enough data
        if not all([revenue_current, cogs_current, revenue_previous, cogs_previous]):
            return self.create_not_triggered_result("Insufficient data for CCC calculation")

        # Calculate DSO, DIO, DPO for current year
        dso_current = (receivables_current / revenue_current) * 365 if revenue_current else 0
        dio_current = (inventory_current / cogs_current) * 365 if cogs_current else 0
        dpo_current = (payables_current / cogs_current) * 365 if cogs_current else 0
        ccc_current = dso_current + dio_current - dpo_current

        # Calculate for previous year
        dso_previous = (receivables_previous / revenue_previous) * 365 if revenue_previous else 0
        dio_previous = (inventory_previous / cogs_previous) * 365 if cogs_previous else 0
        dpo_previous = (payables_previous / cogs_previous) * 365 if cogs_previous else 0
        ccc_previous = dso_previous + dio_previous - dpo_previous

        # Trigger if CCC increased by more than 30 days
        ccc_increase = ccc_current - ccc_previous

        if ccc_increase > 30:
            evidence = (
                f"Cash Conversion Cycle increased by {ccc_increase:.1f} days "
                f"(from {ccc_previous:.1f} to {ccc_current:.1f} days). "
                f"Components: DSO={dso_current:.1f} days, DIO={dio_current:.1f} days, DPO={dpo_current:.1f} days. "
                f"Indicates deteriorating working capital management."
            )

            return self.create_triggered_result(
                evidence=evidence,
                confidence=80.0,
                extracted_data={
                    "ccc_current": ccc_current,
                    "ccc_previous": ccc_previous,
                    "ccc_increase": ccc_increase,
                    "dso_current": dso_current,
                    "dio_current": dio_current,
                    "dpo_current": dpo_current,
                },
            )

        return self.create_not_triggered_result("Cash Conversion Cycle stable or improving")


class UnusualOtherIncomeFlag(RedFlagBase):
    """Flag #16: Unusual Other Income (MEDIUM)."""

    def __init__(self):
        self.flag_number = 16
        self.flag_name = "Unusual Other Income"
        self.category = FlagCategory.CASH_FLOW
        self.severity = FlagSeverity.MEDIUM
        self.description = "Other income is unusually high relative to revenue (reliance on non-operating income)"

    def check(self, data: Dict) -> RedFlagResult:
        """Check if other income is disproportionately high."""
        financial_data = data.get("financial_data", {})
        profit_loss = financial_data.get("profit_loss", {})

        other_income = self.extract_value(profit_loss, "other_income", "value", default=0.0)
        revenue = self.extract_value(profit_loss, "revenue", "value", default=0.0)

        if not revenue or revenue == 0:
            return self.create_not_triggered_result("Revenue data not available")

        # Calculate other income as percentage of revenue
        other_income_pct = (other_income / revenue) * 100

        # Trigger if other income > 10% of revenue
        if other_income_pct > 10:
            evidence = (
                f"Other income is {other_income_pct:.1f}% of revenue "
                f"(Other Income: {other_income:,.0f}, Revenue: {revenue:,.0f}). "
                f"High reliance on non-operating income may mask weak core operations."
            )

            return self.create_triggered_result(
                evidence=evidence,
                confidence=75.0,
                extracted_data={
                    "other_income": other_income,
                    "revenue": revenue,
                    "other_income_pct": other_income_pct,
                },
            )

        return self.create_not_triggered_result("Other income within normal range")


# Register all cash flow flags
flag_registry.register(ProfitGrowingCFOFlatFlag())
flag_registry.register(ReceivablesGrowthFlag())
flag_registry.register(InventoryGrowthFlag())
flag_registry.register(CapexDepreciationFlag())
flag_registry.register(FrequentExceptionalItemsFlag())
flag_registry.register(NegativeCFOFlag())
flag_registry.register(CashConversionCycleFlag())
flag_registry.register(UnusualOtherIncomeFlag())

logger.info("Registered 8 cash flow flags (Category 2)")
