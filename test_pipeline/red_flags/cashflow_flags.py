"""Category 2: Cash Flow Red Flags (8 flags, 18% weight)."""

import re
import logging
from typing import Dict

from red_flags.models import FlagCategory, FlagSeverity
from red_flags.base import RedFlagBase
from red_flags.registry import flag_registry

logger = logging.getLogger(__name__)


class ProfitGrowingCFOFlatFlag(RedFlagBase):
    """Flag #9: Profit Growing but CFO Flat/Declining (HIGH)."""
    def __init__(self):
        self.flag_number = 9
        self.flag_name = "PAT Growing, CFO Flat"
        self.category = FlagCategory.CASH_FLOW
        self.severity = FlagSeverity.HIGH

    def check(self, data: Dict):
        fd = data.get("financial_data", {})
        pl = fd.get("profit_loss", {})
        cf = fd.get("cash_flow", {})
        pat_curr = self.extract_value(pl, "net_profit", "value", default=0.0)
        pat_prev = self.extract_value(pl, "net_profit", "previous_year", default=0.0)
        cfo_curr = self.extract_value(cf, "cash_from_operations", "value", default=0.0)
        cfo_prev = self.extract_value(cf, "cash_from_operations", "previous_year", default=0.0)
        if not all([pat_curr, pat_prev, cfo_curr, cfo_prev]):
            return self.create_not_triggered_result("Insufficient PAT/CFO data")
        pat_growth = self.calculate_growth_rate(pat_curr, pat_prev)
        cfo_growth = self.calculate_growth_rate(cfo_curr, cfo_prev)
        if pat_growth > 0.15 and cfo_growth < pat_growth - 0.20:
            return self.create_triggered_result(
                evidence=f"PAT grew {self.safe_percentage(pat_growth):.1f}% but CFO grew only {self.safe_percentage(cfo_growth):.1f}%. Profit not backed by cash.", confidence=85.0,
                extracted_data={"pat_growth": pat_growth, "cfo_growth": cfo_growth, "pat_curr": pat_curr, "cfo_curr": cfo_curr})
        return self.create_not_triggered_result("PAT and CFO growth aligned")


class ReceivablesGrowthFlag(RedFlagBase):
    """Flag #10: Receivables Growing Faster than Revenue (HIGH)."""
    def __init__(self):
        self.flag_number = 10
        self.flag_name = "Receivables Growing > Revenue"
        self.category = FlagCategory.CASH_FLOW
        self.severity = FlagSeverity.HIGH

    def check(self, data: Dict):
        fd = data.get("financial_data", {})
        bs = fd.get("balance_sheet", {})
        pl = fd.get("profit_loss", {})
        rec_curr = self.extract_value(bs, "current_assets", "trade_receivables", "value", default=0.0)
        rec_prev = self.extract_value(bs, "current_assets", "trade_receivables", "previous_year", default=0.0)
        rev_curr = self.extract_value(pl, "revenue", "value", default=0.0)
        rev_prev = self.extract_value(pl, "revenue", "previous_year", default=0.0)
        if not all([rec_curr, rec_prev, rev_curr, rev_prev]):
            return self.create_not_triggered_result("Insufficient receivables/revenue data")
        rec_growth = self.calculate_growth_rate(rec_curr, rec_prev)
        rev_growth = self.calculate_growth_rate(rev_curr, rev_prev)
        if rec_growth > rev_growth + 0.15:
            return self.create_triggered_result(
                evidence=f"Receivables grew {self.safe_percentage(rec_growth):.1f}% vs revenue growth of {self.safe_percentage(rev_growth):.1f}%. May indicate channel stuffing or collection issues.", confidence=85.0,
                extracted_data={"receivables_growth": rec_growth, "revenue_growth": rev_growth})
        return self.create_not_triggered_result("Receivables growth aligned with revenue")


class InventoryGrowthFlag(RedFlagBase):
    """Flag #11: Inventory Growing Faster than COGS (HIGH)."""
    def __init__(self):
        self.flag_number = 11
        self.flag_name = "Inventory Growing > COGS"
        self.category = FlagCategory.CASH_FLOW
        self.severity = FlagSeverity.HIGH

    def check(self, data: Dict):
        fd = data.get("financial_data", {})
        bs = fd.get("balance_sheet", {})
        pl = fd.get("profit_loss", {})
        inv_curr = self.extract_value(bs, "current_assets", "inventory", "value", default=0.0)
        inv_prev = self.extract_value(bs, "current_assets", "inventory", "previous_year", default=0.0)
        cogs_curr = self.extract_value(pl, "cost_of_goods_sold", "value", default=0.0)
        cogs_prev = self.extract_value(pl, "cost_of_goods_sold", "previous_year", default=0.0)
        if not all([inv_curr, inv_prev]):
            return self.create_not_triggered_result("Insufficient inventory data")
        if not all([cogs_curr, cogs_prev]):
            rev_curr = self.extract_value(pl, "revenue", "value", default=0.0)
            rev_prev = self.extract_value(pl, "revenue", "previous_year", default=0.0)
            cogs_curr, cogs_prev = rev_curr, rev_prev
        if not all([cogs_curr, cogs_prev]):
            return self.create_not_triggered_result("Insufficient COGS/revenue data")
        inv_growth = self.calculate_growth_rate(inv_curr, inv_prev)
        cogs_growth = self.calculate_growth_rate(cogs_curr, cogs_prev)
        if inv_growth > cogs_growth + 0.15:
            return self.create_triggered_result(
                evidence=f"Inventory grew {self.safe_percentage(inv_growth):.1f}% vs COGS growth of {self.safe_percentage(cogs_growth):.1f}%. May indicate obsolete inventory or demand weakness.", confidence=80.0,
                extracted_data={"inventory_growth": inv_growth, "cogs_growth": cogs_growth})
        return self.create_not_triggered_result("Inventory growth aligned with COGS")


class CapexDepreciationFlag(RedFlagBase):
    """Flag #12: Capex >> Depreciation (MEDIUM)."""
    def __init__(self):
        self.flag_number = 12
        self.flag_name = "Capex >> Depreciation"
        self.category = FlagCategory.CASH_FLOW
        self.severity = FlagSeverity.MEDIUM

    def check(self, data: Dict):
        fd = data.get("financial_data", {})
        cf = fd.get("cash_flow", {})
        pl = fd.get("profit_loss", {})
        capex = abs(self.extract_value(cf, "capital_expenditure", "value", default=0.0))
        depreciation = self.extract_value(pl, "depreciation", "value", default=0.0)
        if not capex or not depreciation:
            return self.create_not_triggered_result("Capex or depreciation data not available")
        ratio = self.calculate_ratio(capex, depreciation) if depreciation else 0
        if ratio > 3.0:
            return self.create_triggered_result(
                evidence=f"Capex ({capex:,.0f}) is {ratio:.1f}x depreciation ({depreciation:,.0f}). Extremely high capex may indicate capitalizing expenses.", confidence=75.0,
                extracted_data={"capex": capex, "depreciation": depreciation, "ratio": ratio})
        return self.create_not_triggered_result("Capex to depreciation ratio is normal")


class FrequentExceptionalItemsFlag(RedFlagBase):
    """Flag #13: Frequent Exceptional Items (MEDIUM)."""
    def __init__(self):
        self.flag_number = 13
        self.flag_name = "Frequent Exceptional Items"
        self.category = FlagCategory.CASH_FLOW
        self.severity = FlagSeverity.MEDIUM

    def check(self, data: Dict):
        fd = data.get("financial_data", {})
        pl = fd.get("profit_loss", {})
        exceptional = self.extract_value(pl, "exceptional_items", "value", default=0.0)
        pat = self.extract_value(pl, "net_profit", "value", default=0.0)
        notes_text = data.get("sections", {}).get("notes_to_accounts", "").lower()
        keywords = ["exceptional item", "extraordinary item", "one-time", "non-recurring", "one-off"]
        mentions = sum(1 for kw in keywords if kw in notes_text)
        if abs(exceptional) > 0 and pat != 0:
            exceptional_pct = (abs(exceptional) / abs(pat)) * 100
            if exceptional_pct > 10 or mentions >= 3:
                return self.create_triggered_result(
                    evidence=f"Exceptional items ({exceptional:,.0f}) are {exceptional_pct:.1f}% of PAT. {mentions} mentions in notes. Frequent exceptional items distort earnings quality.", confidence=75.0,
                    extracted_data={"exceptional_items": exceptional, "pat": pat, "pct": exceptional_pct})
        if mentions >= 3:
            return self.create_triggered_result(evidence=f"Multiple exceptional item references ({mentions}) in notes. Frequent non-recurring items raise earnings quality concerns.", confidence=65.0)
        return self.create_not_triggered_result("No significant exceptional items")


class NegativeCFOFlag(RedFlagBase):
    """Flag #14: Negative CFO (HIGH)."""
    def __init__(self):
        self.flag_number = 14
        self.flag_name = "Negative CFO"
        self.category = FlagCategory.CASH_FLOW
        self.severity = FlagSeverity.HIGH

    def check(self, data: Dict):
        fd = data.get("financial_data", {})
        cf = fd.get("cash_flow", {})
        cfo_curr = self.extract_value(cf, "cash_from_operations", "value", default=0.0)
        cfo_prev = self.extract_value(cf, "cash_from_operations", "previous_year", default=0.0)
        if cfo_curr < 0:
            evidence = f"Cash from Operations is negative ({cfo_curr:,.0f}). "
            if cfo_prev < 0:
                evidence += f"Previous year was also negative ({cfo_prev:,.0f}). Persistent negative CFO is a severe warning."
                return self.create_triggered_result(evidence=evidence, confidence=95.0, extracted_data={"cfo_current": cfo_curr, "cfo_previous": cfo_prev})
            evidence += "Company is not generating cash from its core business."
            return self.create_triggered_result(evidence=evidence, confidence=85.0, extracted_data={"cfo_current": cfo_curr, "cfo_previous": cfo_prev})
        return self.create_not_triggered_result("CFO is positive")


class CashConversionCycleFlag(RedFlagBase):
    """Flag #15: Cash Conversion Cycle Increasing (MEDIUM)."""
    def __init__(self):
        self.flag_number = 15
        self.flag_name = "CCC Increasing"
        self.category = FlagCategory.CASH_FLOW
        self.severity = FlagSeverity.MEDIUM

    def check(self, data: Dict):
        fd = data.get("financial_data", {})
        bs = fd.get("balance_sheet", {})
        pl = fd.get("profit_loss", {})
        receivables = self.extract_value(bs, "current_assets", "trade_receivables", "value", default=0.0)
        inventory = self.extract_value(bs, "current_assets", "inventory", "value", default=0.0)
        payables = self.extract_value(bs, "current_liabilities", "trade_payables", "value", default=0.0)
        revenue = self.extract_value(pl, "revenue", "value", default=0.0)
        cogs = self.extract_value(pl, "cost_of_goods_sold", "value", default=0.0) or revenue * 0.7
        if not revenue or revenue == 0:
            return self.create_not_triggered_result("Revenue data not available")
        dso = (receivables / revenue * 365) if revenue else 0
        dio = (inventory / cogs * 365) if cogs else 0
        dpo = (payables / cogs * 365) if cogs else 0
        ccc = dso + dio - dpo
        if ccc > 120:
            return self.create_triggered_result(
                evidence=f"Cash Conversion Cycle is {ccc:.0f} days (DSO:{dso:.0f} + DIO:{dio:.0f} - DPO:{dpo:.0f}). Extended CCC indicates working capital inefficiency.", confidence=75.0,
                extracted_data={"ccc": ccc, "dso": dso, "dio": dio, "dpo": dpo})
        return self.create_not_triggered_result(f"CCC at {ccc:.0f} days is acceptable")


class UnusualOtherIncomeFlag(RedFlagBase):
    """Flag #16: Unusual Other Income (MEDIUM)."""
    def __init__(self):
        self.flag_number = 16
        self.flag_name = "Unusual Other Income"
        self.category = FlagCategory.CASH_FLOW
        self.severity = FlagSeverity.MEDIUM

    def check(self, data: Dict):
        fd = data.get("financial_data", {})
        pl = fd.get("profit_loss", {})
        other_income = self.extract_value(pl, "other_income", "value", default=0.0)
        revenue = self.extract_value(pl, "revenue", "value", default=0.0)
        if not revenue or revenue == 0:
            return self.create_not_triggered_result("Revenue data not available")
        if other_income <= 0:
            return self.create_not_triggered_result("No significant other income")
        oi_pct = (other_income / revenue) * 100
        if oi_pct > 10:
            return self.create_triggered_result(
                evidence=f"Other income ({other_income:,.0f}) is {oi_pct:.1f}% of revenue ({revenue:,.0f}). High other income may be masking weak core operations.", confidence=70.0,
                extracted_data={"other_income": other_income, "revenue": revenue, "oi_pct": oi_pct})
        return self.create_not_triggered_result("Other income within normal range")


flag_registry.register(ProfitGrowingCFOFlatFlag())
flag_registry.register(ReceivablesGrowthFlag())
flag_registry.register(InventoryGrowthFlag())
flag_registry.register(CapexDepreciationFlag())
flag_registry.register(FrequentExceptionalItemsFlag())
flag_registry.register(NegativeCFOFlag())
flag_registry.register(CashConversionCycleFlag())
flag_registry.register(UnusualOtherIncomeFlag())
