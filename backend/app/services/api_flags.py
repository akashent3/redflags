"""API-based red flag calculations using FinEdge financial data.

Non-banks: 21 API flags using standard field schema.
Banks/NBFCs: 8 API flags (5 bank-specific + 3 promoter) using bank field schema.
"""

import logging
from typing import Dict, List, Optional

logger = logging.getLogger(__name__)


def safe_get(data: dict, key: str, default=0) -> float:
    """Safely get a numeric value from dict."""
    val = data.get(key, default)
    if val is None:
        return default
    try:
        return float(val)
    except (TypeError, ValueError):
        return default


def get_latest_years(records: list, n: int = 3) -> list:
    """Get the latest N years of data, sorted by year descending."""
    sorted_recs = sorted(records, key=lambda x: x.get("year", 0), reverse=True)
    return sorted_recs[:n]


def growth_rate(current: float, previous: float) -> Optional[float]:
    """Calculate growth rate as percentage."""
    if previous == 0:
        return None
    return ((current - previous) / abs(previous)) * 100


def fmt_b(val: float) -> str:
    """Format large numbers as Billions for display."""
    if abs(val) >= 1e9:
        return f"{val / 1e9:.1f}B"
    if abs(val) >= 1e7:
        return f"{val / 1e7:.1f}Cr"
    return f"{val:,.0f}"


def calculate_api_flags(data: Dict, is_financial_sector: bool = False) -> List[Dict]:
    """Calculate all API-based flags. Returns list of flag results.

    Banks use completely different field schemas from FinEdge API, so we run
    separate flag sets for financial vs non-financial sector companies.

    Non-banks: 21 flags | Banks: 15 flags (B1-B15, flag_numbers 101-115) + 3 promoter flags
    Banking flags are a complete revamp — only these 15 new flags shown for banks/NBFCs.
    """
    pl = data.get("pl_annual", [])
    bs = data.get("bs_annual", [])
    cf = data.get("cf_annual", [])
    pl_q = data.get("pl_quarterly", [])
    sh_pattern = data.get("shareholding_pattern", {})
    sh_declaration = data.get("shareholding_declaration", {})

    pl_years = get_latest_years(pl, 3)
    bs_years = get_latest_years(bs, 3)
    cf_years = get_latest_years(cf, 3)

    flags = []

    if is_financial_sector:
        # ===== BANK / NBFC / FINANCIAL SERVICES =====
        # Complete revamp — 15 new API-calculated flags (B1–B15)
        # Bank PL fields: interestEarned, interestExpended, interestOrDiscountOnAdvancesOrBills,
        #   profitLossForThePeriod, percentageOfGrossNpa, percentageOfNpa, grossNonPerformingAssets,
        #   nonPerformingAssets, cET1Ratio, additionalTier1Ratio, provisionsForLoanLoss,
        #   employeesCost, otherOperatingExpenses, otherIncome, income, revenueOnInvestments
        # Bank BS fields: deposits, advances, borrowings, capital, reserves, assets
        # Bank CF fields: cashFlowsFromOperatingActivities
        flags.append(_bank_yield_on_advances(pl_years, bs_years))               # B1
        flags.append(_bank_cost_of_funds(pl_years, bs_years))                   # B2
        flags.append(_bank_nim_proxy(pl_years, bs_years))                       # B3
        flags.append(_bank_cost_to_income(pl_years))                            # B4
        flags.append(_bank_provision_coverage_ratio(pl_years))                  # B5
        flags.append(_bank_credit_cost(pl_years, bs_years))                     # B6
        flags.append(_bank_texas_ratio(pl_years, bs_years))                     # B7
        flags.append(_bank_roa(pl_years, bs_years))                             # B8
        flags.append(_bank_roe(pl_years, bs_years))                             # B9
        flags.append(_bank_cfo_to_pat(pl_years, cf_years))                      # B10
        flags.append(_bank_treasury_dependence(pl_years))                       # B11
        flags.append(_bank_employee_cost_burden(pl_years))                      # B12
        flags.append(_bank_gross_npa_ratio(pl_years))                           # B13
        flags.append(_bank_net_npa_ratio(pl_years))                             # B14
        flags.append(_bank_cet1_quality(pl_years))                              # B15
    else:
        # ===== NON-FINANCIAL (MANUFACTURING, SERVICES, etc.) =====
        # Cash Flow Flags
        flags.append(_check_pat_vs_cfo(pl_years, cf_years))                    # #7
        flags.append(_check_receivables_growth(pl_years, bs_years))             # #8
        flags.append(_check_inventory_growth(pl_years, bs_years))               # #9
        flags.append(_check_exceptional_items(pl_years))                        # #11
        flags.append(_check_ccc(pl_years, bs_years))                            # #13
        flags.append(_check_other_income(pl_years))                             # #14
        flags.append(_check_cfo_ebitda_ratio(pl_years, cf_years))               # #43
        flags.append(_check_cash_yield(bs_years, cf_years))                     # #46
        flags.append(_check_free_cash_vs_obligations(bs_years, cf_years))       # #47
        # Balance Sheet Flags
        flags.append(_check_debt_equity(bs_years))                              # #32
        flags.append(_check_interest_coverage(pl_years))                        # #33
        flags.append(_check_st_debt(bs_years))                                  # #34
        flags.append(_check_intangibles(bs_years))                              # #38
        flags.append(_check_cwip_aging(bs_years))                               # #44
        flags.append(_check_depreciation_trajectory(pl_years, bs_years))        # #45
        flags.append(_check_implied_interest_rate(bs_years, cf_years))          # #48
        flags.append(_check_net_worth_trajectory(bs_years))                     # #49
        flags.append(_check_tax_divergence(pl_years, cf_years))                  # #60
        # Revenue Flag
        flags.append(_check_q4_revenue(pl, pl_q))                              # #39

    # --- Promoter Flags (universal - use shareholding data, same for all) ---
    flags.append(_check_promoter_pledge(sh_declaration))                        # #22
    flags.append(_check_pledge_increasing(sh_declaration))                      # #23
    flags.append(_check_promoter_selling(sh_pattern))                           # #24

    return flags


# ---------------------------------------------------------------------------
# Category 2: Cash Flow Flags
# ---------------------------------------------------------------------------

def _check_pat_vs_cfo(pl: list, cf: list) -> Dict:
    """Flag #7: PAT vs CFO divergence - profit growing but CFO not keeping up."""
    flag = {"flag_number": 7, "flag_name": "PAT vs CFO Divergence",
            "category": "Cash Flow", "severity": "HIGH", "source": "API",
            "rule": "Triggers if PAT growth exceeds CFO growth by >30%, or PAT grows >10% while CFO declines >10%"}

    if len(pl) < 2 or len(cf) < 2:
        return {**flag, "triggered": False, "reason": "Insufficient data (need 2+ years)"}

    pat_current = safe_get(pl[0], "profitLossForPeriod")
    pat_prev = safe_get(pl[1], "profitLossForPeriod")
    cfo_current = safe_get(cf[0], "cashFlowsFromOperatingActivities")
    cfo_prev = safe_get(cf[1], "cashFlowsFromOperatingActivities")

    pat_growth = growth_rate(pat_current, pat_prev)
    cfo_growth = growth_rate(cfo_current, cfo_prev)

    if pat_growth is None or cfo_growth is None:
        return {**flag, "triggered": False, "reason": "Cannot calculate growth rates"}

    divergence = pat_growth - cfo_growth
    triggered = (pat_current > 0 and cfo_current > 0 and divergence > 30) or \
                (pat_growth > 10 and cfo_growth < -10)

    return {**flag, "triggered": triggered, "confidence": 100 if triggered else 0,
            "evidence": f"PAT growth: {pat_growth:.1f}%, CFO growth: {cfo_growth:.1f}%, "
                        f"Divergence: {divergence:.1f}%. "
                        f"PAT: {fmt_b(pat_current)}, CFO: {fmt_b(cfo_current)}",
            "data": {"pat_current": pat_current, "pat_prev": pat_prev,
                     "cfo_current": cfo_current, "cfo_prev": cfo_prev,
                     "pat_growth": pat_growth, "cfo_growth": cfo_growth}}


def _check_receivables_growth(pl: list, bs: list) -> Dict:
    """Flag #8: Trade receivables growing faster than revenue."""
    flag = {"flag_number": 8, "flag_name": "Receivables > Revenue Growth",
            "category": "Cash Flow", "severity": "HIGH", "source": "API",
            "rule": "Triggers if receivables growth exceeds revenue growth by >15% AND receivable days >45"}

    if len(pl) < 2 or len(bs) < 2:
        return {**flag, "triggered": False, "reason": "Insufficient data"}

    rev_current = safe_get(pl[0], "revenueFromOperations")
    rev_prev = safe_get(pl[1], "revenueFromOperations")
    rec_current = safe_get(bs[0], "tradeReceivablesCurrent")
    rec_prev = safe_get(bs[1], "tradeReceivablesCurrent")

    rev_growth = growth_rate(rev_current, rev_prev)
    rec_growth = growth_rate(rec_current, rec_prev)

    if rev_growth is None or rec_growth is None:
        return {**flag, "triggered": False, "reason": "Cannot calculate growth"}

    rec_days_current = (rec_current / rev_current * 365) if rev_current > 0 else 0
    rec_days_prev = (rec_prev / rev_prev * 365) if rev_prev > 0 else 0

    triggered = rec_growth > rev_growth + 15 and rec_days_current > 45

    return {**flag, "triggered": triggered, "confidence": 75 if triggered else 0,
            "evidence": f"Revenue growth: {rev_growth:.1f}%, Receivables growth: {rec_growth:.1f}%. "
                        f"Receivable days: {rec_days_current:.0f} (prev: {rec_days_prev:.0f})",
            "data": {"rev_growth": rev_growth, "rec_growth": rec_growth,
                     "rec_days_current": rec_days_current, "rec_days_prev": rec_days_prev}}


def _check_inventory_growth(pl: list, bs: list) -> Dict:
    """Flag #9: Inventory growing faster than COGS."""
    flag = {"flag_number": 9, "flag_name": "Inventory > COGS Growth",
            "category": "Cash Flow", "severity": "MEDIUM", "source": "API",
            "rule": "Triggers if inventory growth exceeds COGS growth by >20% AND inventory days >60"}

    if len(pl) < 2 or len(bs) < 2:
        return {**flag, "triggered": False, "reason": "Insufficient data"}

    cogs_current = safe_get(pl[0], "costofGoodsSold")
    cogs_prev = safe_get(pl[1], "costofGoodsSold")
    inv_current = safe_get(bs[0], "inventories")
    inv_prev = safe_get(bs[1], "inventories")

    if cogs_current == 0 and cogs_prev == 0:
        return {**flag, "triggered": False, "reason": "No COGS data (may be service company)"}

    cogs_growth = growth_rate(cogs_current, cogs_prev)
    inv_growth = growth_rate(inv_current, inv_prev)

    if cogs_growth is None or inv_growth is None:
        return {**flag, "triggered": False, "reason": "Cannot calculate growth"}

    inv_days = (inv_current / cogs_current * 365) if cogs_current > 0 else 0

    triggered = inv_growth > cogs_growth + 20 and inv_days > 60

    return {**flag, "triggered": triggered, "confidence": 70 if triggered else 0,
            "evidence": f"COGS growth: {cogs_growth:.1f}%, Inventory growth: {inv_growth:.1f}%. "
                        f"Inventory days: {inv_days:.0f}",
            "data": {"cogs_growth": cogs_growth, "inv_growth": inv_growth, "inv_days": inv_days}}


def _check_exceptional_items(pl: list) -> Dict:
    """Flag #11: Material exceptional items affecting profit."""
    flag = {"flag_number": 11, "flag_name": "Exceptional Items Material",
            "category": "Cash Flow", "severity": "MEDIUM", "source": "API",
            "rule": "Triggers if exceptional items exceed 10% of PAT"}

    if len(pl) < 1:
        return {**flag, "triggered": False, "reason": "Insufficient data"}

    exceptional = safe_get(pl[0], "exceptionalItemsBeforeTax")
    pat = safe_get(pl[0], "profitLossForPeriod")

    if pat == 0:
        return {**flag, "triggered": False, "reason": "No PAT data"}

    ratio = abs(exceptional) / abs(pat) * 100 if pat != 0 else 0
    triggered = ratio > 10

    return {**flag, "triggered": triggered, "confidence": 70 if triggered else 0,
            "evidence": f"Exceptional items: {fmt_b(exceptional)} ({ratio:.1f}% of PAT {fmt_b(pat)})",
            "data": {"exceptional": exceptional, "pat": pat, "ratio_pct": ratio}}


def _check_ccc(pl: list, bs: list) -> Dict:
    """Flag #13: Cash Conversion Cycle deteriorating significantly."""
    flag = {"flag_number": 13, "flag_name": "Cash Conversion Cycle Deteriorating",
            "category": "Cash Flow", "severity": "MEDIUM", "source": "API",
            "rule": "Triggers if CCC increased by >30 days YoY AND CCC >90 days"}

    if len(pl) < 2 or len(bs) < 2:
        return {**flag, "triggered": False, "reason": "Insufficient data"}

    def calc_ccc(pl_data, bs_data):
        rev = safe_get(pl_data, "revenueFromOperations")
        cogs = safe_get(pl_data, "costofGoodsSold")
        rec = safe_get(bs_data, "tradeReceivablesCurrent")
        inv = safe_get(bs_data, "inventories")
        pay = safe_get(bs_data, "tradePayablesCurrent")
        dso = (rec / rev * 365) if rev > 0 else 0
        dio = (inv / cogs * 365) if cogs > 0 else 0
        dpo = (pay / cogs * 365) if cogs > 0 else 0
        return dso + dio - dpo, dso, dio, dpo

    ccc_current, dso_c, dio_c, dpo_c = calc_ccc(pl[0], bs[0])
    ccc_prev, dso_p, dio_p, dpo_p = calc_ccc(pl[1], bs[1])

    change = ccc_current - ccc_prev
    triggered = change > 30 and ccc_current > 90

    return {**flag, "triggered": triggered, "confidence": 70 if triggered else 0,
            "evidence": f"CCC: {ccc_current:.0f} days (prev: {ccc_prev:.0f}), Change: {change:+.0f} days. "
                        f"DSO: {dso_c:.0f}, DIO: {dio_c:.0f}, DPO: {dpo_c:.0f}",
            "data": {"ccc_current": ccc_current, "ccc_prev": ccc_prev, "change": change,
                     "dso": dso_c, "dio": dio_c, "dpo": dpo_c}}


def _check_other_income(pl: list) -> Dict:
    """Flag #14: Other income unusually high relative to operating revenue."""
    flag = {"flag_number": 14, "flag_name": "Other Income Dependency",
            "category": "Cash Flow", "severity": "LOW", "source": "API",
            "rule": "Triggers if other income >15% of revenue OR >30% of PAT"}

    if len(pl) < 1:
        return {**flag, "triggered": False, "reason": "Insufficient data"}

    other_income = safe_get(pl[0], "otherIncome")
    revenue = safe_get(pl[0], "revenueFromOperations")
    pat = safe_get(pl[0], "profitLossForPeriod")

    if revenue == 0:
        return {**flag, "triggered": False, "reason": "No revenue data"}

    ratio_rev = (other_income / revenue) * 100
    ratio_pat = (other_income / pat * 100) if pat > 0 else 0

    triggered = ratio_rev > 15 or ratio_pat > 30

    return {**flag, "triggered": triggered, "confidence": 60 if triggered else 0,
            "evidence": f"Other income: {fmt_b(other_income)} "
                        f"({ratio_rev:.1f}% of revenue, {ratio_pat:.1f}% of PAT)",
            "data": {"other_income": other_income, "ratio_of_revenue": ratio_rev,
                     "ratio_of_pat": ratio_pat}}


def _check_cfo_ebitda_ratio(pl: list, cf: list) -> Dict:
    """Flag #43: 3-year cumulative CFO/EBITDA ratio below 70%."""
    flag = {"flag_number": 43, "flag_name": "Low CFO to EBITDA Ratio (3Y)",
            "category": "Cash Flow", "severity": "HIGH", "source": "API",
            "rule": "Triggers if 3-year cumulative CFO/EBITDA < 70%, suggesting poor earnings-to-cash conversion"}

    if len(pl) < 3 or len(cf) < 3:
        return {**flag, "triggered": False, "reason": "Insufficient data (need 3 years)"}

    cum_cfo = sum(safe_get(cf[i], "cashFlowsFromOperatingActivities") for i in range(3))
    cum_ebitda = sum(
        safe_get(pl[i], "profitBeforeTax") + safe_get(pl[i], "financeCosts") + safe_get(pl[i], "depreciationAndAmortisation")
        for i in range(3)
    )

    if cum_ebitda <= 0:
        return {**flag, "triggered": False, "reason": "Negative or zero cumulative EBITDA over 3 years"}

    ratio = cum_cfo / cum_ebitda
    triggered = ratio < 0.70

    return {**flag, "triggered": triggered, "confidence": 100 if triggered else 0,
            "evidence": f"3Y cumulative CFO: {fmt_b(cum_cfo)}, EBITDA: {fmt_b(cum_ebitda)}, "
                        f"Ratio: {ratio:.1%}",
            "data": {"cum_cfo": cum_cfo, "cum_ebitda": cum_ebitda, "ratio": ratio}}


def _check_cash_yield(bs: list, cf: list) -> Dict:
    """Flag #46: Cash yield test - interest received vs cash balance."""
    flag = {"flag_number": 46, "flag_name": "Low Cash Yield",
            "category": "Cash Flow", "severity": "MEDIUM", "source": "API",
            "rule": "Triggers if cash yield <5% when cash balance >5% of total assets, suggesting cash may not be real"}

    if len(bs) < 1 or len(cf) < 1:
        return {**flag, "triggered": False, "reason": "Insufficient data"}

    cash = safe_get(bs[0], "cashAndCashEquivalents")
    total_assets = safe_get(bs[0], "assets")
    interest_received = safe_get(cf[0], "interestReceivedClassifiedAsInvesting")

    if total_assets <= 0:
        return {**flag, "triggered": False, "reason": "No asset data"}

    cash_pct_of_assets = cash / total_assets * 100

    if cash_pct_of_assets < 5 or cash <= 0:
        return {**flag, "triggered": False,
                "reason": f"Cash ({cash_pct_of_assets:.1f}% of assets) not significant enough to test",
                "data": {"cash": cash, "cash_pct_of_assets": cash_pct_of_assets}}

    cash_yield = interest_received / cash if cash > 0 else 0
    triggered = cash_yield < 0.05

    return {**flag, "triggered": triggered, "confidence": 70 if triggered else 0,
            "evidence": f"Cash: {fmt_b(cash)} ({cash_pct_of_assets:.1f}% of assets), "
                        f"Interest received: {fmt_b(interest_received)}, Yield: {cash_yield:.1%}",
            "data": {"cash": cash, "interest_received": interest_received,
                     "cash_yield": cash_yield, "cash_pct_of_assets": cash_pct_of_assets}}


def _check_free_cash_vs_obligations(bs: list, cf: list) -> Dict:
    """Flag #47: Free cash flow vs short-term obligations."""
    flag = {"flag_number": 47, "flag_name": "Low Free Cash vs Obligations",
            "category": "Cash Flow", "severity": "LOW", "source": "API",
            "rule": "Triggers if free cash flow covers <15% of short-term obligations (borrowings + payables)"}

    if len(bs) < 1 or len(cf) < 1:
        return {**flag, "triggered": False, "reason": "Insufficient data"}

    cfo = safe_get(cf[0], "cashFlowsFromOperatingActivities")
    capex = abs(safe_get(cf[0], "purchaseOfFixed&IntangibleAssets"))
    fcf = cfo - capex

    st_debt = safe_get(bs[0], "borrowingsCurrent")
    payables = safe_get(bs[0], "tradePayablesCurrent")
    st_obligations = st_debt + payables

    if st_obligations <= 0:
        return {**flag, "triggered": False, "reason": "No short-term obligations found"}

    coverage = fcf / st_obligations
    triggered = coverage < 0.15

    return {**flag, "triggered": triggered, "confidence": 65 if triggered else 0,
            "evidence": f"FCF: {fmt_b(fcf)} (CFO: {fmt_b(cfo)} - Capex: {fmt_b(capex)}), "
                        f"ST obligations: {fmt_b(st_obligations)}, Coverage: {coverage:.1%}",
            "data": {"fcf": fcf, "cfo": cfo, "capex": capex,
                     "st_obligations": st_obligations, "coverage": coverage}}


# ---------------------------------------------------------------------------
# Category 4: Promoter Flags
# ---------------------------------------------------------------------------

def _check_promoter_pledge(declaration: dict) -> Dict:
    """Flag #22: Promoter shares pledged."""
    flag = {"flag_number": 22, "flag_name": "High Promoter Pledge",
            "category": "Promoter", "severity": "CRITICAL", "source": "API",
            "rule": "Triggers if promoter shares are pledged (per SEBI declaration)"}

    decl_list = declaration.get("declaration", [])
    if not decl_list:
        return {**flag, "triggered": False, "reason": "No declaration data available"}

    latest = decl_list[0]
    pledge_exists = latest.get("pledgedSharesPromoter", False) or \
                    latest.get("pledgedSharesForPromoterAndGroup", False)

    return {**flag, "triggered": pledge_exists, "confidence": 70 if pledge_exists else 0,
            "evidence": f"Promoter shares pledged: {'Yes' if pledge_exists else 'No'} "
                        f"(as of {latest.get('header', 'N/A')}). "
                        f"Exact pledge % requires annual report analysis.",
            "data": {"pledge_exists": pledge_exists, "period": latest.get("header")}}


def _check_pledge_increasing(declaration: dict) -> Dict:
    """Flag #23: Promoter pledge increasing over quarters."""
    flag = {"flag_number": 23, "flag_name": "Promoter Pledge Increasing",
            "category": "Promoter", "severity": "HIGH", "source": "API",
            "rule": "Triggers if promoter pledge appeared in recent quarters (was absent earlier)"}

    decl_list = declaration.get("declaration", [])
    if len(decl_list) < 4:
        return {**flag, "triggered": False, "reason": "Insufficient declaration history"}

    recent = decl_list[:4]
    pledge_trend = []
    for d in recent:
        has_pledge = d.get("pledgedSharesPromoter", False) or \
                     d.get("pledgedSharesForPromoterAndGroup", False)
        pledge_trend.append(has_pledge)

    # Flag if latest has pledge but older quarters didn't
    triggered = pledge_trend[0] and not all(pledge_trend[1:])

    labels = [d.get("header", "?") for d in recent]
    trend_str = ", ".join(f"{labels[i]}: {'Yes' if pledge_trend[i] else 'No'}" for i in range(len(recent)))

    return {**flag, "triggered": triggered, "confidence": 70 if triggered else 0,
            "evidence": f"Pledge trend: {trend_str}",
            "data": {"pledge_trend": pledge_trend, "labels": labels}}


def _check_promoter_selling(pattern: dict) -> Dict:
    """Flag #24: Promoter holding declining over quarters."""
    flag = {"flag_number": 24, "flag_name": "Promoter Holding Declining",
            "category": "Promoter", "severity": "MEDIUM", "source": "API",
            "rule": "Triggers if promoter holding declined by >2% over 4 quarters"}

    rows = pattern.get("rows", [])
    columns = pattern.get("columns", [])

    if not rows or not columns:
        return {**flag, "triggered": False, "reason": "No shareholding pattern data"}

    # Find promoter category
    promoter_row = None
    for row in rows:
        cat = (row.get("catagory", "") + " " + row.get("name", "")).lower()
        if "promoter" in cat and "non" not in cat:
            promoter_row = row
            break

    if not promoter_row:
        return {**flag, "triggered": False,
                "reason": "No promoter category found (may be widely held company like ITC)"}

    promo_data = promoter_row.get("data", {})
    if len(columns) < 4:
        return {**flag, "triggered": False, "reason": "Insufficient quarterly data"}

    recent_cols = columns[-4:]
    holdings = [promo_data.get(col, 0) for col in recent_cols]

    if not all(h > 0 for h in holdings):
        return {**flag, "triggered": False, "reason": "Incomplete promoter data"}

    decline = holdings[-1] - holdings[0]
    triggered = decline < -2

    return {**flag, "triggered": triggered, "confidence": 75 if triggered else 0,
            "evidence": f"Promoter holding: {holdings[0]:.1f}% -> {holdings[-1]:.1f}% "
                        f"(change: {decline:+.1f}% over 4 quarters)",
            "data": {"holdings": dict(zip(recent_cols, holdings)), "decline": decline}}


# ---------------------------------------------------------------------------
# Category 6: Balance Sheet Flags
# ---------------------------------------------------------------------------

def _check_debt_equity(bs: list) -> Dict:
    """Flag #32: Debt to Equity ratio > 1."""
    flag = {"flag_number": 32, "flag_name": "High Debt to Equity",
            "category": "Balance Sheet", "severity": "HIGH", "source": "API",
            "rule": "Triggers if Debt/Equity ratio >1.0 OR equity is negative"}

    if len(bs) < 1:
        return {**flag, "triggered": False, "reason": "Insufficient data"}

    lt_debt = safe_get(bs[0], "borrowingsNoncurrent")
    st_debt = safe_get(bs[0], "borrowingsCurrent")
    total_debt = lt_debt + st_debt
    equity = safe_get(bs[0], "totalEquity")

    if equity <= 0:
        return {**flag, "triggered": True, "confidence": 95,
                "evidence": f"Negative equity: {fmt_b(equity)}! Total debt: {fmt_b(total_debt)}",
                "data": {"total_debt": total_debt, "equity": equity, "de_ratio": None}}

    de_ratio = total_debt / equity
    triggered = de_ratio > 1.0

    trend = ""
    if len(bs) >= 2:
        prev_debt = safe_get(bs[1], "borrowingsNoncurrent") + safe_get(bs[1], "borrowingsCurrent")
        prev_eq = safe_get(bs[1], "totalEquity")
        prev_de = prev_debt / prev_eq if prev_eq > 0 else 0
        trend = f" (prev year: {prev_de:.2f})"

    return {**flag, "triggered": triggered, "confidence": 100 if triggered else 0,
            "evidence": f"D/E ratio: {de_ratio:.2f}{trend}. "
                        f"Debt: {fmt_b(total_debt)}, Equity: {fmt_b(equity)}",
            "data": {"de_ratio": de_ratio, "total_debt": total_debt, "equity": equity}}


def _check_interest_coverage(pl: list) -> Dict:
    """Flag #33: Interest coverage ratio below 2x."""
    flag = {"flag_number": 33, "flag_name": "Low Interest Coverage",
            "category": "Balance Sheet", "severity": "HIGH", "source": "API",
            "rule": "Triggers if interest coverage ratio (EBIT/Finance costs) is below 2.0x"}

    if len(pl) < 1:
        return {**flag, "triggered": False, "reason": "Insufficient data"}

    pbt = safe_get(pl[0], "profitBeforeTax")
    finance_costs = safe_get(pl[0], "financeCosts")

    if finance_costs <= 0:
        return {**flag, "triggered": False,
                "reason": f"Minimal finance costs ({fmt_b(finance_costs)}) - company appears debt-free",
                "data": {"pbt": pbt, "finance_costs": finance_costs}}

    ebit = pbt + finance_costs
    icr = ebit / finance_costs
    triggered = icr < 2.0

    return {**flag, "triggered": triggered, "confidence": 85 if triggered else 0,
            "evidence": f"Interest coverage: {icr:.1f}x. "
                        f"EBIT: {fmt_b(ebit)}, Finance costs: {fmt_b(finance_costs)}",
            "data": {"icr": icr, "ebit": ebit, "finance_costs": finance_costs}}


def _check_st_debt(bs: list) -> Dict:
    """Flag #34: Short-term debt > 60% of total debt."""
    flag = {"flag_number": 34, "flag_name": "High Short-Term Debt Ratio",
            "category": "Balance Sheet", "severity": "MEDIUM", "source": "API",
            "rule": "Triggers if short-term borrowings >60% of total borrowings AND total debt >1B INR"}

    if len(bs) < 1:
        return {**flag, "triggered": False, "reason": "Insufficient data"}

    st_debt = safe_get(bs[0], "borrowingsCurrent")
    lt_debt = safe_get(bs[0], "borrowingsNoncurrent")
    total_debt = st_debt + lt_debt

    if total_debt <= 0:
        return {**flag, "triggered": False, "reason": "No borrowings found"}

    st_pct = (st_debt / total_debt) * 100
    # Only flag if debt is material (> 1B INR)
    triggered = st_pct > 60 and total_debt > 1e9

    return {**flag, "triggered": triggered, "confidence": 70 if triggered else 0,
            "evidence": f"ST debt: {fmt_b(st_debt)} ({st_pct:.1f}% of total debt {fmt_b(total_debt)})",
            "data": {"st_debt": st_debt, "lt_debt": lt_debt, "st_pct": st_pct}}


def _check_intangibles(bs: list) -> Dict:
    """Flag #38: Intangible assets growing as % of total assets."""
    flag = {"flag_number": 38, "flag_name": "Intangibles Growing",
            "category": "Balance Sheet", "severity": "MEDIUM", "source": "API",
            "rule": "Triggers if intangibles (goodwill + intangible assets) >15% of total assets AND grew >3pp YoY"}

    if len(bs) < 2:
        return {**flag, "triggered": False, "reason": "Insufficient data"}

    def intangible_pct(bs_data):
        goodwill = safe_get(bs_data, "goodwill")
        intangibles = safe_get(bs_data, "otherIntangibleAssets")
        intangibles_dev = safe_get(bs_data, "intangibleAssetsUnderDev")
        total = goodwill + intangibles + intangibles_dev
        assets = safe_get(bs_data, "assets")
        return (total / assets * 100) if assets > 0 else 0, total

    pct_current, total_current = intangible_pct(bs[0])
    pct_prev, total_prev = intangible_pct(bs[1])

    growth = pct_current - pct_prev
    triggered = pct_current > 15 and growth > 3

    return {**flag, "triggered": triggered, "confidence": 65 if triggered else 0,
            "evidence": f"Intangibles: {pct_current:.1f}% of assets "
                        f"(prev: {pct_prev:.1f}%, change: {growth:+.1f}pp). "
                        f"Value: {fmt_b(total_current)}",
            "data": {"pct_current": pct_current, "pct_prev": pct_prev, "growth_pp": growth}}


def _check_cwip_aging(bs: list) -> Dict:
    """Flag #44: CWIP/Net Block > 30% for 3 consecutive years."""
    flag = {"flag_number": 44, "flag_name": "CWIP Aging",
            "category": "Balance Sheet", "severity": "MEDIUM", "source": "API",
            "rule": "Triggers if CWIP/Net Block ratio >30% for 3 consecutive years, suggesting stalled projects"}

    if len(bs) < 3:
        return {**flag, "triggered": False, "reason": "Insufficient data (need 3 years)"}

    ratios = []
    for i in range(3):
        cwip = safe_get(bs[i], "capitalWorkInProgress")
        net_block = safe_get(bs[i], "propertyPlantAndEquipment")
        if net_block <= 0:
            ratios.append(0)
        else:
            ratios.append(cwip / net_block)

    all_above_30 = all(r > 0.30 for r in ratios)
    triggered = all_above_30

    return {**flag, "triggered": triggered, "confidence": 75 if triggered else 0,
            "evidence": f"CWIP/Net Block: {ratios[0]:.1%} (latest), {ratios[1]:.1%} (mid), "
                        f"{ratios[2]:.1%} (oldest). CWIP: {fmt_b(safe_get(bs[0], 'capitalWorkInProgress'))}",
            "data": {"ratios": ratios}}


def _check_depreciation_trajectory(pl: list, bs: list) -> Dict:
    """Flag #45: Depreciation rate declining over 3 years."""
    flag = {"flag_number": 45, "flag_name": "Depreciation Rate Declining",
            "category": "Balance Sheet", "severity": "MEDIUM", "source": "API",
            "rule": "Triggers if depreciation rate declined consistently over 3 years AND total decline >20%"}

    if len(pl) < 3 or len(bs) < 3:
        return {**flag, "triggered": False, "reason": "Insufficient data (need 3 years)"}

    rates = []
    for i in range(3):
        dep = safe_get(pl[i], "depreciationAndAmortisation")
        ppe = safe_get(bs[i], "propertyPlantAndEquipment")
        cwip = safe_get(bs[i], "capitalWorkInProgress")
        base = ppe + cwip
        if base <= 0:
            rates.append(0)
        else:
            rates.append(dep / base)

    # rates[0] = latest, rates[2] = oldest
    # Declining means oldest > middle > latest
    consistently_declining = rates[2] > rates[1] > rates[0] and all(r > 0 for r in rates)

    if rates[2] > 0:
        total_decline_pct = (rates[2] - rates[0]) / rates[2] * 100
    else:
        total_decline_pct = 0

    triggered = consistently_declining and total_decline_pct > 20

    return {**flag, "triggered": triggered, "confidence": 70 if triggered else 0,
            "evidence": f"Dep rate: {rates[0]:.1%} (latest), {rates[1]:.1%} (mid), {rates[2]:.1%} (oldest). "
                        f"Decline: {total_decline_pct:.1f}%",
            "data": {"rates": rates, "total_decline_pct": total_decline_pct}}


def _check_implied_interest_rate(bs: list, cf: list) -> Dict:
    """Flag #48: Implied interest rate outside normal range."""
    flag = {"flag_number": 48, "flag_name": "Abnormal Implied Interest Rate",
            "category": "Balance Sheet", "severity": "MEDIUM", "source": "API",
            "rule": "Triggers if implied interest rate (interest paid / avg debt) is <4% or >18%"}

    if len(bs) < 2 or len(cf) < 1:
        return {**flag, "triggered": False, "reason": "Insufficient data (need 2 years BS + 1 year CF)"}

    interest_paid = abs(safe_get(cf[0], "interestPaidClassifiedAsFinancing"))

    debt_current = safe_get(bs[0], "borrowingsNoncurrent") + safe_get(bs[0], "borrowingsCurrent")
    debt_prev = safe_get(bs[1], "borrowingsNoncurrent") + safe_get(bs[1], "borrowingsCurrent")
    avg_debt = (debt_current + debt_prev) / 2

    if avg_debt <= 0:
        return {**flag, "triggered": False, "reason": "No significant debt (debt-free company)"}

    if interest_paid <= 0:
        return {**flag, "triggered": False, "reason": "No interest paid in cash flow"}

    implied_rate = interest_paid / avg_debt
    triggered = implied_rate < 0.04 or implied_rate > 0.18

    if implied_rate < 0.04:
        direction = "unusually low (possible understated debt)"
    elif implied_rate > 0.18:
        direction = "unusually high (distressed borrowing)"
    else:
        direction = "normal"

    return {**flag, "triggered": triggered, "confidence": 70 if triggered else 0,
            "evidence": f"Interest paid: {fmt_b(interest_paid)}, Avg debt: {fmt_b(avg_debt)}, "
                        f"Implied rate: {implied_rate:.1%} - {direction}",
            "data": {"interest_paid": interest_paid, "avg_debt": avg_debt,
                     "implied_rate": implied_rate}}


def _check_net_worth_trajectory(bs: list) -> Dict:
    """Flag #49: Net worth declining over 2+ years."""
    flag = {"flag_number": 49, "flag_name": "Net Worth Declining",
            "category": "Balance Sheet", "severity": "MEDIUM", "source": "API",
            "rule": "Triggers if net worth (total equity) declined for 2+ consecutive years OR >20% over 3 years"}

    if len(bs) < 2:
        return {**flag, "triggered": False, "reason": "Insufficient data"}

    equities = [safe_get(bs[i], "totalEquity") for i in range(min(3, len(bs)))]

    # Check consecutive decline (latest < older = declining)
    declining_years = 0
    for i in range(len(equities) - 1):
        if equities[i] < equities[i + 1]:
            declining_years += 1

    # Check total decline over available period
    if equities[-1] > 0:
        total_decline_pct = (equities[-1] - equities[0]) / equities[-1] * 100
    else:
        total_decline_pct = 0

    triggered = declining_years >= 2 or (len(equities) >= 3 and total_decline_pct > 20)

    equity_strs = [fmt_b(e) for e in equities]

    return {**flag, "triggered": triggered, "confidence": 75 if triggered else 0,
            "evidence": f"Net worth: {' -> '.join(equity_strs)} (latest first). "
                        f"Declining for {declining_years} year(s). Change: {total_decline_pct:+.1f}%",
            "data": {"equities": equities, "declining_years": declining_years,
                     "total_decline_pct": total_decline_pct}}

def _check_tax_divergence(pl: list, cf: list) -> Dict:
    """
    Flag #60: Tax Divergence - Cash tax vs P&L tax mismatch.
    
    Triggers if:
    1. P&L tax > 1.2x cash flow tax (accruing but not paying)
    2. Cash flow tax > 1.2x P&L tax (large DTL buildup)
    """
    flag = {
        "flag_number": 60,
        "flag_name": "Tax Divergence",
        "category": "Revenue",
        "severity": "HIGH",
        "source": "API",
        "rule": "Triggers if P&L tax > 1.2x cash flow tax OR cash flow tax > 1.2x P&L tax"
    }

    if len(pl) < 1 or len(cf) < 1:
        return {**flag, "triggered": False, "reason": "Insufficient P&L or CF data"}

    # Get latest year
    latest_pl = pl[0]
    latest_cf = cf[0]

    # Extract values
    tax_expense_pl = safe_get(latest_pl, "taxExpense")  # P&L tax expense
    tax_paid_cf = safe_get(latest_cf, "incomeTaxesPaidOrRefundClassifiedAsOperating")  # Cash flow tax paid

    if tax_expense_pl == 0 and tax_paid_cf == 0:
        return {**flag, "triggered": False, "reason": "No tax data available"}

    if tax_expense_pl == 0 or tax_paid_cf == 0:
        # If one is zero but other is significant
        if tax_expense_pl > 1000000 or abs(tax_paid_cf) > 1000000:  # > 1 Cr
            return {**flag, "triggered": True, "confidence": 80,
                    "evidence": f"Extreme divergence: P&L tax {fmt_b(tax_expense_pl)}, Cash tax {fmt_b(tax_paid_cf)}. "
                                f"Company may be deferring tax payments or understating liability.",
                    "data": {"tax_expense_pl": tax_expense_pl, "tax_paid_cf": tax_paid_cf}}
        return {**flag, "triggered": False, "reason": "Minimal tax amounts"}

    # Calculate ratio
    pl_to_cf_ratio = tax_expense_pl / abs(tax_paid_cf) if tax_paid_cf != 0 else 0
    cf_to_pl_ratio = abs(tax_paid_cf) / tax_expense_pl if tax_expense_pl != 0 else 0

    triggered = False
    evidence = ""

    # Case 1: P&L tax > 1.2x Cash tax (accruing but not paying)
    if pl_to_cf_ratio > 1.2:
        triggered = True
        evidence = (f"P&L tax ({fmt_b(tax_expense_pl)}) exceeds cash tax paid ({fmt_b(tax_paid_cf)}) by "
                   f"{pl_to_cf_ratio:.2f}x. Company is accruing tax liabilities faster than paying them, "
                   f"indicating potential cash flow stress or P&L understatement of tax.")

    # Case 2: Cash tax > 1.2x P&L tax (large DTL buildup)
    elif cf_to_pl_ratio > 1.2:
        triggered = True
        evidence = (f"Cash tax paid ({fmt_b(tax_paid_cf)}) exceeds P&L tax ({fmt_b(tax_expense_pl)}) by "
                   f"{cf_to_pl_ratio:.2f}x. Large Deferred Tax Liability (DTL) buildup suggests aggressive "
                   f"depreciation/deductions to boost P&L earnings while delaying actual tax payments.")

    return {**flag, "triggered": triggered, "confidence": 75 if triggered else 0,
            "evidence": evidence if triggered else f"Tax divergence within acceptable range (ratio: {min(pl_to_cf_ratio, cf_to_pl_ratio):.2f}x)",
            "data": {"tax_expense_pl": tax_expense_pl, "tax_paid_cf": tax_paid_cf,
                     "pl_to_cf_ratio": pl_to_cf_ratio, "cf_to_pl_ratio": cf_to_pl_ratio}}


# ---------------------------------------------------------------------------
# Category 7: Revenue Flag
# ---------------------------------------------------------------------------

def _check_q4_revenue(pl_annual: list, pl_quarterly: list) -> Dict:
    """Flag #39: Q4 revenue concentration (>35% of annual in a single quarter)."""
    flag = {"flag_number": 39, "flag_name": "Q4 Revenue Concentration",
            "category": "Revenue", "severity": "MEDIUM", "source": "API",
            "rule": "Triggers if any single quarter contributes >35% of annual revenue"}

    if not pl_annual or len(pl_quarterly) < 4:
        return {**flag, "triggered": False, "reason": "Insufficient quarterly data"}

    latest_annual = get_latest_years(pl_annual, 1)[0]
    annual_year = latest_annual.get("year", 0)

    # Get quarterly data for the latest financial year
    quarterly_sorted = sorted(pl_quarterly, key=lambda x: x.get("result_date", 0), reverse=True)

    q_revs = []
    for q in quarterly_sorted:
        q_year = q.get("year", 0)
        if q_year == annual_year:
            q_revs.append(safe_get(q, "revenueFromOperations"))

    if len(q_revs) < 4:
        # Fall back to latest 4 quarters
        q_revs = [safe_get(q, "revenueFromOperations") for q in quarterly_sorted[:4]]

    if len(q_revs) < 4:
        return {**flag, "triggered": False, "reason": "Cannot identify 4 quarters"}

    max_q = max(q_revs)
    total_q = sum(q_revs)
    max_pct = (max_q / total_q * 100) if total_q > 0 else 0

    triggered = max_pct > 35

    return {**flag, "triggered": triggered, "confidence": 65 if triggered else 0,
            "evidence": f"Highest quarter revenue: {fmt_b(max_q)} "
                        f"({max_pct:.1f}% of annual {fmt_b(total_q)}). "
                        f"Quarters: {[fmt_b(q) for q in q_revs]}",
            "data": {"max_quarter_rev": max_q, "max_pct": max_pct,
                     "quarterly_revs": q_revs}}


# ===========================================================================
# BANK / NBFC / FINANCIAL SERVICES — COMPLETE FLAG SET (B1–B15)
# Complete revamp. These replace the old #52–#56 flags entirely.
# Flag IDs use a dedicated banking block: B1–B15 (stored as flag_number 101–115).
# All use bank-specific FinEdge API field names.
# ===========================================================================

def _bank_yield_on_advances(pl: list, bs: list) -> Dict:
    """Bank Flag B1: Yield on Advances — outside industry range 8-10%."""
    flag = {"flag_number": 101, "flag_name": "Yield on Advances",
            "category": "Balance Sheet", "severity": "MEDIUM", "source": "API",
            "rule": "Triggers if Yield on Advances is outside 8-10% industry range. "
                    "Formula: (interestOrDiscountOnAdvancesOrBills / advances) * 100"}

    if len(pl) < 1 or len(bs) < 1:
        return {**flag, "triggered": False, "reason": "Insufficient data"}

    interest_on_adv = safe_get(pl[0], "interestOrDiscountOnAdvancesOrBills")
    advances = safe_get(bs[0], "advances")

    if advances <= 0:
        return {**flag, "triggered": False, "reason": "No advances data"}

    yield_pct = (interest_on_adv / advances) * 100
    triggered = yield_pct < 8.0 or yield_pct > 10.0

    if yield_pct < 8.0:
        direction = "Low — possible under-reporting of interest income or stressed book"
    elif yield_pct > 10.0:
        direction = "High — aggressive lending to risky borrowers"
    else:
        direction = "Within industry range (8-10%)"

    return {**flag, "triggered": triggered, "confidence": 70 if triggered else 0,
            "evidence": f"Yield on Advances: {yield_pct:.2f}% — {direction}. "
                        f"Interest on advances: {fmt_b(interest_on_adv)}, Advances: {fmt_b(advances)}",
            "data": {"yield_pct": yield_pct, "interest_on_adv": interest_on_adv, "advances": advances}}


def _bank_cost_of_funds(pl: list, bs: list) -> Dict:
    """Bank Flag B2: Cost of Funds — above 5% industry benchmark."""
    flag = {"flag_number": 102, "flag_name": "Cost of Funds",
            "category": "Balance Sheet", "severity": "MEDIUM", "source": "API",
            "rule": "Triggers if Cost of Funds exceeds 5% (industry avg 4-5%). "
                    "Formula: (interestExpended / (deposits + borrowings)) * 100"}

    if len(pl) < 1 or len(bs) < 1:
        return {**flag, "triggered": False, "reason": "Insufficient data"}

    interest_expended = safe_get(pl[0], "interestExpended")
    deposits = safe_get(bs[0], "deposits")
    borrowings = safe_get(bs[0], "borrowings")
    total_funds = deposits + borrowings

    if total_funds <= 0:
        return {**flag, "triggered": False, "reason": "No deposits/borrowings data"}

    cost_pct = (interest_expended / total_funds) * 100
    triggered = cost_pct > 5.0

    trend = ""
    if len(pl) >= 2 and len(bs) >= 2:
        prev_exp = safe_get(pl[1], "interestExpended")
        prev_dep = safe_get(bs[1], "deposits")
        prev_bor = safe_get(bs[1], "borrowings")
        prev_funds = prev_dep + prev_bor
        if prev_funds > 0:
            prev_cost = (prev_exp / prev_funds) * 100
            trend = f" (prev: {prev_cost:.2f}%)"

    return {**flag, "triggered": triggered, "confidence": 70 if triggered else 0,
            "evidence": f"Cost of Funds: {cost_pct:.2f}%{trend}. "
                        f"Interest expended: {fmt_b(interest_expended)}, "
                        f"Total funds (deposits+borrowings): {fmt_b(total_funds)}",
            "data": {"cost_pct": cost_pct, "interest_expended": interest_expended,
                     "deposits": deposits, "borrowings": borrowings}}


def _bank_nim_proxy(pl: list, bs: list) -> Dict:
    """Bank Flag B3: Net Interest Margin (NIM) Proxy — below 3%."""
    flag = {"flag_number": 103, "flag_name": "Net Interest Margin (NIM) Proxy",
            "category": "Cash Flow", "severity": "MEDIUM", "source": "API",
            "rule": "Triggers if NIM proxy falls below 3% (healthy threshold). "
                    "Formula: ((interestEarned - interestExpended) / assets) * 100"}

    if len(pl) < 1 or len(bs) < 1:
        return {**flag, "triggered": False, "reason": "Insufficient data"}

    interest_earned = safe_get(pl[0], "interestEarned")
    interest_expended = safe_get(pl[0], "interestExpended")
    assets = safe_get(bs[0], "assets")

    if assets <= 0:
        return {**flag, "triggered": False, "reason": "No assets data"}

    nim = ((interest_earned - interest_expended) / assets) * 100
    triggered = nim < 3.0

    trend = ""
    if len(pl) >= 2 and len(bs) >= 2:
        prev_ie = safe_get(pl[1], "interestEarned")
        prev_ix = safe_get(pl[1], "interestExpended")
        prev_a = safe_get(bs[1], "assets")
        if prev_a > 0:
            prev_nim = ((prev_ie - prev_ix) / prev_a) * 100
            trend = f" (prev: {prev_nim:.2f}%)"

    return {**flag, "triggered": triggered, "confidence": 75 if triggered else 0,
            "evidence": f"NIM: {nim:.2f}%{trend}. "
                        f"Net interest income: {fmt_b(interest_earned - interest_expended)}, "
                        f"Total assets: {fmt_b(assets)}",
            "data": {"nim": nim, "interest_earned": interest_earned,
                     "interest_expended": interest_expended, "assets": assets}}


def _bank_cost_to_income(pl: list) -> Dict:
    """Bank Flag B4: Cost-to-Income Ratio — above 50% (inefficient)."""
    flag = {"flag_number": 104, "flag_name": "Cost-to-Income Ratio",
            "category": "Cash Flow", "severity": "MEDIUM", "source": "API",
            "rule": "Triggers if Cost-to-Income Ratio exceeds 50%. Efficient banks are below 50%. "
                    "Formula: ((employeesCost + otherOperatingExpenses) / "
                    "((interestEarned - interestExpended) + otherIncome)) * 100"}

    if len(pl) < 1:
        return {**flag, "triggered": False, "reason": "Insufficient data"}

    employees_cost = safe_get(pl[0], "employeesCost")
    other_opex = safe_get(pl[0], "otherOperatingExpenses")
    interest_earned = safe_get(pl[0], "interestEarned")
    interest_expended = safe_get(pl[0], "interestExpended")
    other_income = safe_get(pl[0], "otherIncome")

    net_income = (interest_earned - interest_expended) + other_income
    total_opex = employees_cost + other_opex

    if net_income <= 0:
        return {**flag, "triggered": False, "reason": "Non-positive net income — cannot calculate ratio"}

    cir = (total_opex / net_income) * 100
    triggered = cir > 50.0

    return {**flag, "triggered": triggered, "confidence": 75 if triggered else 0,
            "evidence": f"Cost-to-Income Ratio: {cir:.2f}%. "
                        f"Total OpEx: {fmt_b(total_opex)}, Net Income: {fmt_b(net_income)}. "
                        f"{'Above 50% — operationally inefficient.' if triggered else 'Efficient (<50%).'}",
            "data": {"cir": cir, "total_opex": total_opex, "net_income": net_income,
                     "employees_cost": employees_cost, "other_opex": other_opex}}


def _bank_provision_coverage_ratio(pl: list) -> Dict:
    """Bank Flag B5: Provision Coverage Ratio (PCR) — below 70% (under-provisioned)."""
    flag = {"flag_number": 105, "flag_name": "Provision Coverage Ratio (PCR)",
            "category": "Balance Sheet", "severity": "HIGH", "source": "API",
            "rule": "Triggers if PCR falls below 70% (preferred threshold). "
                    "Formula: ((grossNonPerformingAssets - nonPerformingAssets) / "
                    "grossNonPerformingAssets) * 100"}

    if len(pl) < 1:
        return {**flag, "triggered": False, "reason": "Insufficient data"}

    gnpa = safe_get(pl[0], "grossNonPerformingAssets")
    nnpa = safe_get(pl[0], "nonPerformingAssets")

    if gnpa <= 0:
        return {**flag, "triggered": False, "reason": "No GNPA data — cannot calculate PCR"}

    pcr = ((gnpa - nnpa) / gnpa) * 100
    triggered = pcr < 70.0

    trend = ""
    if len(pl) >= 2:
        prev_gnpa = safe_get(pl[1], "grossNonPerformingAssets")
        prev_nnpa = safe_get(pl[1], "nonPerformingAssets")
        if prev_gnpa > 0:
            prev_pcr = ((prev_gnpa - prev_nnpa) / prev_gnpa) * 100
            trend = f" (prev: {prev_pcr:.2f}%)"

    return {**flag, "triggered": triggered, "confidence": 80 if triggered else 0,
            "evidence": f"PCR: {pcr:.2f}%{trend}. "
                        f"GNPA: {fmt_b(gnpa)}, NNPA: {fmt_b(nnpa)}, "
                        f"Provisions: {fmt_b(gnpa - nnpa)}. "
                        f"{'Below 70% — under-provisioned, masking bad loan severity.' if triggered else 'Adequately provisioned.'}",
            "data": {"pcr": pcr, "gnpa": gnpa, "nnpa": nnpa}}


def _bank_credit_cost(pl: list, bs: list) -> Dict:
    """Bank Flag B6: Credit Cost — above 1% (elevated loan loss expense)."""
    flag = {"flag_number": 106, "flag_name": "Credit Cost",
            "category": "Balance Sheet", "severity": "HIGH", "source": "API",
            "rule": "Triggers if Credit Cost exceeds 1% of total advances. "
                    "Formula: (provisionsForLoanLoss / advances) * 100"}

    if len(pl) < 1 or len(bs) < 1:
        return {**flag, "triggered": False, "reason": "Insufficient data"}

    provisions = safe_get(pl[0], "provisionsForLoanLoss")
    advances = safe_get(bs[0], "advances")

    if advances <= 0:
        return {**flag, "triggered": False, "reason": "No advances data"}

    credit_cost = (provisions / advances) * 100
    triggered = credit_cost > 1.0

    trend = ""
    if len(pl) >= 2 and len(bs) >= 2:
        prev_prov = safe_get(pl[1], "provisionsForLoanLoss")
        prev_adv = safe_get(bs[1], "advances")
        if prev_adv > 0:
            prev_cc = (prev_prov / prev_adv) * 100
            trend = f" (prev: {prev_cc:.2f}%)"

    return {**flag, "triggered": triggered, "confidence": 75 if triggered else 0,
            "evidence": f"Credit Cost: {credit_cost:.2f}%{trend}. "
                        f"Provisions for loan loss: {fmt_b(provisions)}, Advances: {fmt_b(advances)}. "
                        f"{'Above 1% — hidden NPAs surfacing.' if triggered else 'Stable (<1%).'}",
            "data": {"credit_cost": credit_cost, "provisions": provisions, "advances": advances}}


def _bank_texas_ratio(pl: list, bs: list) -> Dict:
    """Bank Flag B7: Texas Ratio — above 40% (dangerous solvency signal)."""
    flag = {"flag_number": 107, "flag_name": "Texas Ratio",
            "category": "Balance Sheet", "severity": "CRITICAL", "source": "API",
            "rule": "Triggers if Texas Ratio exceeds 40% — signals bank solvency risk. "
                    "Formula: (grossNonPerformingAssets / (capital + reserves)) * 100"}

    if len(pl) < 1 or len(bs) < 1:
        return {**flag, "triggered": False, "reason": "Insufficient data"}

    gnpa = safe_get(pl[0], "grossNonPerformingAssets")
    capital = safe_get(bs[0], "capital")
    reserves = safe_get(bs[0], "reserves")
    equity = capital + reserves

    if equity <= 0:
        return {**flag, "triggered": True, "confidence": 100,
                "evidence": "Negative/zero equity — extreme solvency risk. GNPA cannot be covered.",
                "data": {"gnpa": gnpa, "equity": equity, "texas_ratio": None}}

    texas_ratio = (gnpa / equity) * 100
    triggered = texas_ratio > 40.0

    risk_label = ""
    if texas_ratio > 100:
        risk_label = "EXTREME — NPAs exceed entire equity base!"
    elif texas_ratio > 40:
        risk_label = "DANGEROUS — bank solvency at risk"
    else:
        risk_label = "Safe (strong capital buffer)"

    return {**flag, "triggered": triggered, "confidence": 100 if triggered else 0,
            "evidence": f"Texas Ratio: {texas_ratio:.2f}% — {risk_label}. "
                        f"GNPA: {fmt_b(gnpa)}, Equity (capital+reserves): {fmt_b(equity)}",
            "data": {"texas_ratio": texas_ratio, "gnpa": gnpa, "equity": equity}}


def _bank_roa(pl: list, bs: list) -> Dict:
    """Bank Flag B8: Return on Assets (ROA) — below 1% (poor profitability)."""
    flag = {"flag_number": 108, "flag_name": "Return on Assets (ROA)",
            "category": "Cash Flow", "severity": "MEDIUM", "source": "API",
            "rule": "Triggers if ROA falls below 1% (excellent threshold). "
                    "Formula: (profitLossForThePeriod / assets) * 100"}

    if len(pl) < 1 or len(bs) < 1:
        return {**flag, "triggered": False, "reason": "Insufficient data"}

    pat = safe_get(pl[0], "profitLossForThePeriod")
    assets = safe_get(bs[0], "assets")

    if assets <= 0:
        return {**flag, "triggered": False, "reason": "No assets data"}

    roa = (pat / assets) * 100
    triggered = roa < 1.0

    trend = ""
    if len(pl) >= 2 and len(bs) >= 2:
        prev_pat = safe_get(pl[1], "profitLossForThePeriod")
        prev_assets = safe_get(bs[1], "assets")
        if prev_assets > 0:
            prev_roa = (prev_pat / prev_assets) * 100
            trend = f" (prev: {prev_roa:.2f}%)"

    return {**flag, "triggered": triggered, "confidence": 70 if triggered else 0,
            "evidence": f"ROA: {roa:.2f}%{trend}. "
                        f"PAT: {fmt_b(pat)}, Total Assets: {fmt_b(assets)}. "
                        f"{'Below 1% — weak profitability relative to asset base.' if triggered else 'Strong (>1%).'}",
            "data": {"roa": roa, "pat": pat, "assets": assets}}


def _bank_roe(pl: list, bs: list) -> Dict:
    """Bank Flag B9: Return on Equity (ROE) — below 12%."""
    flag = {"flag_number": 109, "flag_name": "Return on Equity (ROE)",
            "category": "Cash Flow", "severity": "MEDIUM", "source": "API",
            "rule": "Triggers if ROE falls below 12% (healthy benchmark 12-15%). "
                    "Formula: (profitLossForThePeriod / (capital + reserves)) * 100"}

    if len(pl) < 1 or len(bs) < 1:
        return {**flag, "triggered": False, "reason": "Insufficient data"}

    pat = safe_get(pl[0], "profitLossForThePeriod")
    capital = safe_get(bs[0], "capital")
    reserves = safe_get(bs[0], "reserves")
    equity = capital + reserves

    if equity <= 0:
        return {**flag, "triggered": False, "reason": "Negative/zero equity"}

    roe = (pat / equity) * 100
    triggered = roe < 12.0

    trend = ""
    if len(pl) >= 2 and len(bs) >= 2:
        prev_pat = safe_get(pl[1], "profitLossForThePeriod")
        prev_cap = safe_get(bs[1], "capital")
        prev_res = safe_get(bs[1], "reserves")
        prev_eq = prev_cap + prev_res
        if prev_eq > 0:
            prev_roe = (prev_pat / prev_eq) * 100
            trend = f" (prev: {prev_roe:.2f}%)"

    return {**flag, "triggered": triggered, "confidence": 65 if triggered else 0,
            "evidence": f"ROE: {roe:.2f}%{trend}. "
                        f"PAT: {fmt_b(pat)}, Equity (capital+reserves): {fmt_b(equity)}. "
                        f"{'Below 12% — insufficient shareholder returns.' if triggered else 'Healthy (12-15%+).'}",
            "data": {"roe": roe, "pat": pat, "equity": equity}}


def _bank_cfo_to_pat(pl: list, cf: list) -> Dict:
    """Bank Flag B10: CFO to PAT Ratio — below 1.0x (earnings not cash-backed)."""
    flag = {"flag_number": 110, "flag_name": "CFO to PAT Ratio (Earnings Quality)",
            "category": "Cash Flow", "severity": "HIGH", "source": "API",
            "rule": "Triggers if CFO/PAT ratio falls below 1.0x — profits not supported by operating cash. "
                    "Formula: cashFlowsFromOperatingActivities / profitLossForThePeriod"}

    if len(pl) < 1 or len(cf) < 1:
        return {**flag, "triggered": False, "reason": "Insufficient data"}

    cfo = safe_get(cf[0], "cashFlowsFromOperatingActivities")
    pat = safe_get(pl[0], "profitLossForThePeriod")

    if pat <= 0:
        return {**flag, "triggered": False, "reason": "Non-positive PAT — ratio not meaningful"}

    ratio = cfo / pat
    triggered = ratio < 1.0

    trend = ""
    if len(pl) >= 2 and len(cf) >= 2:
        prev_cfo = safe_get(cf[1], "cashFlowsFromOperatingActivities")
        prev_pat = safe_get(pl[1], "profitLossForThePeriod")
        if prev_pat > 0:
            prev_ratio = prev_cfo / prev_pat
            trend = f" (prev: {prev_ratio:.2f}x)"

    return {**flag, "triggered": triggered, "confidence": 80 if triggered else 0,
            "evidence": f"CFO/PAT: {ratio:.2f}x{trend}. "
                        f"CFO: {fmt_b(cfo)}, PAT: {fmt_b(pat)}. "
                        f"{'Below 1.0x — reported profits not backed by operating cash. Earnings quality concern.' if triggered else 'High quality (>1.0x) — cash-backed profits.'}",
            "data": {"ratio": ratio, "cfo": cfo, "pat": pat}}


def _bank_treasury_dependence(pl: list) -> Dict:
    """Bank Flag B11: Treasury Dependence — above 20% of total income (risky)."""
    flag = {"flag_number": 111, "flag_name": "Treasury Dependence",
            "category": "Cash Flow", "severity": "MEDIUM", "source": "API",
            "rule": "Triggers if Treasury/Investment income exceeds 20% of total income. "
                    "Formula: (revenueOnInvestments / income) * 100"}

    if len(pl) < 1:
        return {**flag, "triggered": False, "reason": "Insufficient data"}

    rev_investments = safe_get(pl[0], "revenueOnInvestments")
    total_income = safe_get(pl[0], "income")

    if total_income <= 0:
        return {**flag, "triggered": False, "reason": "No income data"}

    treasury_pct = (rev_investments / total_income) * 100
    triggered = treasury_pct > 20.0

    trend = ""
    if len(pl) >= 2:
        prev_ri = safe_get(pl[1], "revenueOnInvestments")
        prev_inc = safe_get(pl[1], "income")
        if prev_inc > 0:
            prev_pct = (prev_ri / prev_inc) * 100
            trend = f" (prev: {prev_pct:.2f}%)"

    return {**flag, "triggered": triggered, "confidence": 65 if triggered else 0,
            "evidence": f"Treasury Dependence: {treasury_pct:.2f}%{trend}. "
                        f"Investment income: {fmt_b(rev_investments)}, Total income: {fmt_b(total_income)}. "
                        f"{'Above 20% — over-reliance on volatile trading/treasury gains.' if triggered else 'Safe (<20%).'}",
            "data": {"treasury_pct": treasury_pct, "rev_investments": rev_investments,
                     "total_income": total_income}}


def _bank_employee_cost_burden(pl: list) -> Dict:
    """Bank Flag B12: Employee Cost Burden — above 20% of net income."""
    flag = {"flag_number": 112, "flag_name": "Employee Cost Burden",
            "category": "Cash Flow", "severity": "LOW", "source": "API",
            "rule": "Triggers if Employee Cost exceeds 20% of net income (standard range 15-20%). "
                    "Formula: (employeesCost / ((interestEarned - interestExpended) + otherIncome)) * 100"}

    if len(pl) < 1:
        return {**flag, "triggered": False, "reason": "Insufficient data"}

    employees_cost = safe_get(pl[0], "employeesCost")
    interest_earned = safe_get(pl[0], "interestEarned")
    interest_expended = safe_get(pl[0], "interestExpended")
    other_income = safe_get(pl[0], "otherIncome")

    net_income = (interest_earned - interest_expended) + other_income

    if net_income <= 0:
        return {**flag, "triggered": False, "reason": "Non-positive net income"}

    emp_burden = (employees_cost / net_income) * 100
    triggered = emp_burden > 20.0

    trend = ""
    if len(pl) >= 2:
        prev_ec = safe_get(pl[1], "employeesCost")
        prev_ie = safe_get(pl[1], "interestEarned")
        prev_ix = safe_get(pl[1], "interestExpended")
        prev_oi = safe_get(pl[1], "otherIncome")
        prev_ni = (prev_ie - prev_ix) + prev_oi
        if prev_ni > 0:
            prev_burden = (prev_ec / prev_ni) * 100
            trend = f" (prev: {prev_burden:.2f}%)"

    return {**flag, "triggered": triggered, "confidence": 55 if triggered else 0,
            "evidence": f"Employee Cost Burden: {emp_burden:.2f}%{trend}. "
                        f"Employee costs: {fmt_b(employees_cost)}, Net income: {fmt_b(net_income)}. "
                        f"{'Above 20% — high staffing cost load.' if triggered else 'Within standard range.'}",
            "data": {"emp_burden": emp_burden, "employees_cost": employees_cost,
                     "net_income": net_income}}


def _bank_gross_npa_ratio(pl: list) -> Dict:
    """Bank Flag B13: Gross NPA Ratio — above 3% (standard threshold)."""
    flag = {"flag_number": 113, "flag_name": "Gross NPA Ratio",
            "category": "Balance Sheet", "severity": "CRITICAL", "source": "API",
            "rule": "Triggers if Gross NPA Ratio exceeds 3% or is rising YoY. "
                    "Formula: percentageOfGrossNpa * 100"}

    if len(pl) < 1:
        return {**flag, "triggered": False, "reason": "Insufficient data"}

    gnpa_pct = safe_get(pl[0], "percentageOfGrossNpa")

    if gnpa_pct == 0:
        return {**flag, "triggered": False, "reason": "No GNPA % data available"}

    # API returns as decimal (e.g. 0.0133 = 1.33%), convert to percentage
    gnpa_display = gnpa_pct * 100 if gnpa_pct < 1 else gnpa_pct
    above_threshold = gnpa_display > 3.0

    rising = False
    trend = ""
    if len(pl) >= 2:
        gnpa_prev = safe_get(pl[1], "percentageOfGrossNpa")
        gnpa_prev_display = gnpa_prev * 100 if gnpa_prev < 1 else gnpa_prev
        if gnpa_prev_display > 0:
            rising = gnpa_display > gnpa_prev_display
            trend = f" (prev: {gnpa_prev_display:.2f}%)"

    triggered = above_threshold or rising

    return {**flag, "triggered": triggered, "confidence": 90 if triggered else 0,
            "evidence": f"Gross NPA Ratio: {gnpa_display:.2f}%{trend}. "
                        f"{'Rising YoY. ' if rising else ''}"
                        f"{'Above 3% threshold — poor asset quality.' if above_threshold else ''}",
            "data": {"gnpa_pct": gnpa_display, "above_threshold": above_threshold, "rising": rising}}


def _bank_net_npa_ratio(pl: list) -> Dict:
    """Bank Flag B14: Net NPA Ratio — above 1% (below excellent threshold)."""
    flag = {"flag_number": 114, "flag_name": "Net NPA Ratio",
            "category": "Balance Sheet", "severity": "HIGH", "source": "API",
            "rule": "Triggers if Net NPA Ratio exceeds 1% (excellent is <1%) or is rising YoY. "
                    "Formula: percentageOfNpa * 100"}

    if len(pl) < 1:
        return {**flag, "triggered": False, "reason": "Insufficient data"}

    nnpa_pct = safe_get(pl[0], "percentageOfNpa")

    if nnpa_pct == 0:
        return {**flag, "triggered": False, "reason": "No NNPA % data available"}

    nnpa_display = nnpa_pct * 100 if nnpa_pct < 1 else nnpa_pct
    above_threshold = nnpa_display > 1.0

    rising = False
    trend = ""
    if len(pl) >= 2:
        nnpa_prev = safe_get(pl[1], "percentageOfNpa")
        nnpa_prev_display = nnpa_prev * 100 if nnpa_prev < 1 else nnpa_prev
        if nnpa_prev_display > 0:
            rising = nnpa_display > nnpa_prev_display
            trend = f" (prev: {nnpa_prev_display:.2f}%)"

    triggered = above_threshold or rising

    return {**flag, "triggered": triggered, "confidence": 85 if triggered else 0,
            "evidence": f"Net NPA Ratio: {nnpa_display:.2f}%{trend}. "
                        f"{'Rising YoY. ' if rising else ''}"
                        f"{'Above 1% — post-provision asset quality concern.' if above_threshold else ''}",
            "data": {"nnpa_pct": nnpa_display, "above_threshold": above_threshold, "rising": rising}}


def _bank_cet1_quality(pl: list) -> Dict:
    """Bank Flag B15: Core Capital Quality (CET1) — below regulatory minimum 8%."""
    flag = {"flag_number": 115, "flag_name": "Core Capital Quality (CET1)",
            "category": "Balance Sheet", "severity": "HIGH", "source": "API",
            "rule": "Triggers if CET1 Ratio falls below 8% (regulatory minimum) or declined >1.5pp YoY. "
                    "Formula: cET1Ratio * 100"}

    if len(pl) < 1:
        return {**flag, "triggered": False, "reason": "Insufficient data"}

    cet1_raw = safe_get(pl[0], "cET1Ratio")

    if cet1_raw == 0:
        return {**flag, "triggered": False, "reason": "No CET1 data available"}

    # API may return as decimal (0.1955 = 19.55%) or percentage (19.55)
    cet1 = cet1_raw * 100 if cet1_raw < 1 else cet1_raw
    low_cet1 = cet1 < 8.0

    declining = False
    prev_cet1 = 0
    if len(pl) >= 2:
        prev_raw = safe_get(pl[1], "cET1Ratio")
        if prev_raw > 0:
            prev_cet1 = prev_raw * 100 if prev_raw < 1 else prev_raw
            declining = (prev_cet1 - cet1) > 1.5

    triggered = low_cet1 or declining

    evidence = f"CET1 Ratio: {cet1:.2f}%"
    if prev_cet1 > 0:
        evidence += f" (prev: {prev_cet1:.2f}%)"
    if low_cet1:
        evidence += " — Below 8% regulatory minimum! Capital inadequacy risk."
    if declining:
        evidence += f" — Declining >1.5pp YoY. Capital erosion in progress."
    if not triggered:
        evidence += f" — Well above 8% regulatory minimum. Strong capital buffer."

    return {**flag, "triggered": triggered, "confidence": 100 if triggered else 0,
            "evidence": evidence,
            "data": {"cet1": cet1, "prev_cet1": prev_cet1, "low_cet1": low_cet1,
                     "declining": declining}}
