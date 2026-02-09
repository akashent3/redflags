"""16 API-based red flag calculations using FinEdge financial data."""

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


def get_latest_years(records: list, n: int = 2) -> list:
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


def calculate_api_flags(data: Dict) -> List[Dict]:
    """Calculate all 16 API-based flags. Returns list of flag results."""
    pl = data.get("pl_annual", [])
    bs = data.get("bs_annual", [])
    cf = data.get("cf_annual", [])
    pl_q = data.get("pl_quarterly", [])
    sh_pattern = data.get("shareholding_pattern", {})
    sh_declaration = data.get("shareholding_declaration", {})

    pl_years = get_latest_years(pl, 3)
    bs_years = get_latest_years(bs, 3)
    cf_years = get_latest_years(cf, 3)

    flags = [
        _check_pat_vs_cfo(pl_years, cf_years),
        _check_receivables_growth(pl_years, bs_years),
        _check_inventory_growth(pl_years, bs_years),
        _check_capex_vs_depreciation(pl_years, cf_years),
        _check_exceptional_items(pl_years),
        _check_negative_cfo(cf_years),
        _check_ccc(pl_years, bs_years),
        _check_other_income(pl_years),
        _check_promoter_pledge(sh_declaration),
        _check_pledge_increasing(sh_declaration),
        _check_promoter_selling(sh_pattern),
        _check_debt_equity(bs_years),
        _check_interest_coverage(pl_years),
        _check_st_debt(bs_years),
        _check_intangibles(bs_years),
        _check_q4_revenue(pl, pl_q),
    ]
    return flags


# ---------------------------------------------------------------------------
# Category 2: Cash Flow Flags
# ---------------------------------------------------------------------------

def _check_pat_vs_cfo(pl: list, cf: list) -> Dict:
    """Flag #7: PAT vs CFO divergence - profit growing but CFO not keeping up."""
    flag = {"flag_number": 7, "flag_name": "PAT vs CFO Divergence",
            "category": "Cash Flow", "severity": "HIGH", "source": "API"}

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

    return {**flag, "triggered": triggered, "confidence": 80 if triggered else 0,
            "evidence": f"PAT growth: {pat_growth:.1f}%, CFO growth: {cfo_growth:.1f}%, "
                        f"Divergence: {divergence:.1f}%. "
                        f"PAT: {fmt_b(pat_current)}, CFO: {fmt_b(cfo_current)}",
            "data": {"pat_current": pat_current, "pat_prev": pat_prev,
                     "cfo_current": cfo_current, "cfo_prev": cfo_prev,
                     "pat_growth": pat_growth, "cfo_growth": cfo_growth}}


def _check_receivables_growth(pl: list, bs: list) -> Dict:
    """Flag #8: Trade receivables growing faster than revenue."""
    flag = {"flag_number": 8, "flag_name": "Receivables > Revenue Growth",
            "category": "Cash Flow", "severity": "HIGH", "source": "API"}

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
            "category": "Cash Flow", "severity": "MEDIUM", "source": "API"}

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


def _check_capex_vs_depreciation(pl: list, cf: list) -> Dict:
    """Flag #10: Capex significantly exceeding depreciation."""
    flag = {"flag_number": 10, "flag_name": "Capex >> Depreciation",
            "category": "Cash Flow", "severity": "MEDIUM", "source": "API"}

    if len(pl) < 1 or len(cf) < 1:
        return {**flag, "triggered": False, "reason": "Insufficient data"}

    dep = safe_get(pl[0], "depreciationAndAmortisation")
    # CF capex is negative (outflow), take absolute value
    capex = abs(safe_get(cf[0], "purchaseOfFixed&IntangibleAssets"))

    if dep == 0:
        return {**flag, "triggered": False, "reason": "No depreciation data"}

    ratio = capex / dep if dep > 0 else 0
    triggered = ratio > 3.0

    return {**flag, "triggered": triggered, "confidence": 65 if triggered else 0,
            "evidence": f"Capex: {fmt_b(capex)}, Depreciation: {fmt_b(dep)}, Ratio: {ratio:.1f}x",
            "data": {"capex": capex, "depreciation": dep, "ratio": ratio}}


def _check_exceptional_items(pl: list) -> Dict:
    """Flag #11: Material exceptional items affecting profit."""
    flag = {"flag_number": 11, "flag_name": "Exceptional Items Material",
            "category": "Cash Flow", "severity": "MEDIUM", "source": "API"}

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


def _check_negative_cfo(cf: list) -> Dict:
    """Flag #12: Negative operating cash flow."""
    flag = {"flag_number": 12, "flag_name": "Negative Operating Cash Flow",
            "category": "Cash Flow", "severity": "CRITICAL", "source": "API"}

    if len(cf) < 1:
        return {**flag, "triggered": False, "reason": "Insufficient data"}

    cfo = safe_get(cf[0], "cashFlowsFromOperatingActivities")
    triggered = cfo < 0

    consecutive_negative = 0
    for year_data in cf:
        if safe_get(year_data, "cashFlowsFromOperatingActivities") < 0:
            consecutive_negative += 1
        else:
            break

    conf = 95 if consecutive_negative >= 2 else 80

    return {**flag, "triggered": triggered, "confidence": conf if triggered else 0,
            "evidence": f"CFO: {fmt_b(cfo)}."
                        f"{' Negative for ' + str(consecutive_negative) + ' consecutive years!' if consecutive_negative > 1 else ''}",
            "data": {"cfo": cfo, "consecutive_negative": consecutive_negative}}


def _check_ccc(pl: list, bs: list) -> Dict:
    """Flag #13: Cash Conversion Cycle deteriorating significantly."""
    flag = {"flag_number": 13, "flag_name": "Cash Conversion Cycle Deteriorating",
            "category": "Cash Flow", "severity": "MEDIUM", "source": "API"}

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
            "category": "Cash Flow", "severity": "LOW", "source": "API"}

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


# ---------------------------------------------------------------------------
# Category 4: Promoter Flags
# ---------------------------------------------------------------------------

def _check_promoter_pledge(declaration: dict) -> Dict:
    """Flag #22: Promoter shares pledged."""
    flag = {"flag_number": 22, "flag_name": "High Promoter Pledge",
            "category": "Promoter", "severity": "CRITICAL", "source": "API"}

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
            "category": "Promoter", "severity": "HIGH", "source": "API"}

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
            "category": "Promoter", "severity": "MEDIUM", "source": "API"}

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
            "category": "Balance Sheet", "severity": "HIGH", "source": "API"}

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

    return {**flag, "triggered": triggered, "confidence": 80 if triggered else 0,
            "evidence": f"D/E ratio: {de_ratio:.2f}{trend}. "
                        f"Debt: {fmt_b(total_debt)}, Equity: {fmt_b(equity)}",
            "data": {"de_ratio": de_ratio, "total_debt": total_debt, "equity": equity}}


def _check_interest_coverage(pl: list) -> Dict:
    """Flag #33: Interest coverage ratio below 2x."""
    flag = {"flag_number": 33, "flag_name": "Low Interest Coverage",
            "category": "Balance Sheet", "severity": "HIGH", "source": "API"}

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
            "category": "Balance Sheet", "severity": "MEDIUM", "source": "API"}

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
            "category": "Balance Sheet", "severity": "MEDIUM", "source": "API"}

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


# ---------------------------------------------------------------------------
# Category 7: Revenue Flag
# ---------------------------------------------------------------------------

def _check_q4_revenue(pl_annual: list, pl_quarterly: list) -> Dict:
    """Flag #39: Q4 revenue concentration (>35% of annual in a single quarter)."""
    flag = {"flag_number": 39, "flag_name": "Q4 Revenue Concentration",
            "category": "Revenue", "severity": "MEDIUM", "source": "API"}

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
