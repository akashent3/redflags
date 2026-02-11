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

    Non-banks: 21 flags | Banks: 8 flags (5 bank-specific + 3 promoter)
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
        # Bank PL uses: interestEarned, interestExpended, profitLossBeforeTax,
        #   profitLossForThePeriod, percentageOfGrossNpa, percentageOfNpa,
        #   cET1Ratio, additionalTier1Ratio, provisionsForLoanLoss
        # Bank BS uses: deposits, advances, borrowings, capital, reserves, assets
        flags.append(_check_gnpa_rising(pl_years))                              # #52
        flags.append(_check_nnpa_high(pl_years))                                # #53
        flags.append(_check_nim_compression(pl_years, bs_years))                # #54
        flags.append(_check_cd_ratio(bs_years))                                 # #55
        flags.append(_check_capital_adequacy(pl_years))                         # #56
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

    return {**flag, "triggered": triggered, "confidence": 80 if triggered else 0,
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
    interest_received = safe_get(cf[0], "interestReceivedClassifiedAsOperating")

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

    return {**flag, "triggered": triggered, "confidence": 80 if triggered else 0,
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

    interest_paid = abs(safe_get(cf[0], "interestPaidClassifiedAsOperating"))

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
# BANK / NBFC / FINANCIAL SERVICES SPECIFIC FLAGS
# These use bank-specific FinEdge API field names which are completely
# different from the standard (non-bank) schema.
# ===========================================================================

def _check_gnpa_rising(pl: list) -> Dict:
    """Flag #52: Gross NPA % rising YoY or above 3%."""
    flag = {"flag_number": 52, "flag_name": "Gross NPA Rising",
            "category": "Balance Sheet", "severity": "CRITICAL", "source": "API",
            "rule": "Triggers if Gross NPA % increased YoY or exceeds 3% of gross advances"}

    if len(pl) < 2:
        return {**flag, "triggered": False, "reason": "Insufficient data (need 2 years)"}

    gnpa_current = safe_get(pl[0], "percentageOfGrossNpa")
    gnpa_prev = safe_get(pl[1], "percentageOfGrossNpa")

    if gnpa_current == 0 and gnpa_prev == 0:
        return {**flag, "triggered": False, "reason": "No GNPA data available"}

    increasing = gnpa_current > gnpa_prev and gnpa_prev > 0
    above_threshold = gnpa_current > 3.0
    triggered = increasing or above_threshold

    return {**flag, "triggered": triggered, "confidence": 85 if triggered else 0,
            "evidence": f"GNPA: {gnpa_current:.2f}% (prev: {gnpa_prev:.2f}%). "
                        f"{'Increasing YoY. ' if increasing else ''}"
                        f"{'Above 3% threshold!' if above_threshold else ''}",
            "data": {"gnpa_current": gnpa_current, "gnpa_prev": gnpa_prev}}


def _check_nnpa_high(pl: list) -> Dict:
    """Flag #53: Net NPA % rising or above 1.5%."""
    flag = {"flag_number": 53, "flag_name": "Net NPA High",
            "category": "Balance Sheet", "severity": "HIGH", "source": "API",
            "rule": "Triggers if Net NPA % increased YoY or exceeds 1.5%"}

    if len(pl) < 2:
        return {**flag, "triggered": False, "reason": "Insufficient data (need 2 years)"}

    nnpa_current = safe_get(pl[0], "percentageOfNpa")
    nnpa_prev = safe_get(pl[1], "percentageOfNpa")

    if nnpa_current == 0 and nnpa_prev == 0:
        return {**flag, "triggered": False, "reason": "No NNPA data available"}

    increasing = nnpa_current > nnpa_prev and nnpa_prev > 0
    above_threshold = nnpa_current > 1.5
    triggered = increasing or above_threshold

    return {**flag, "triggered": triggered, "confidence": 85 if triggered else 0,
            "evidence": f"NNPA: {nnpa_current:.2f}% (prev: {nnpa_prev:.2f}%). "
                        f"{'Increasing YoY. ' if increasing else ''}"
                        f"{'Above 1.5% threshold!' if above_threshold else ''}",
            "data": {"nnpa_current": nnpa_current, "nnpa_prev": nnpa_prev}}


def _check_nim_compression(pl: list, bs: list) -> Dict:
    """Flag #54: Net Interest Margin declining >30bps YoY."""
    flag = {"flag_number": 54, "flag_name": "NIM Compression",
            "category": "Cash Flow", "severity": "MEDIUM", "source": "API",
            "rule": "Triggers if Net Interest Margin declined >30 basis points YoY"}

    if len(pl) < 2 or len(bs) < 2:
        return {**flag, "triggered": False, "reason": "Insufficient data (need 2 years)"}

    def calc_nim(pl_data, bs_data):
        interest_earned = safe_get(pl_data, "interestEarned")
        interest_expended = safe_get(pl_data, "interestExpended")
        total_assets = safe_get(bs_data, "assets")
        if total_assets <= 0:
            return 0
        return (interest_earned - interest_expended) / total_assets * 100

    nim_current = calc_nim(pl[0], bs[0])
    nim_prev = calc_nim(pl[1], bs[1])

    if nim_current == 0 and nim_prev == 0:
        return {**flag, "triggered": False, "reason": "Cannot calculate NIM"}

    decline_bps = (nim_prev - nim_current) * 100  # in basis points
    triggered = decline_bps > 30

    return {**flag, "triggered": triggered, "confidence": 70 if triggered else 0,
            "evidence": f"NIM: {nim_current:.2f}% (prev: {nim_prev:.2f}%), "
                        f"Change: {-decline_bps:+.0f} bps",
            "data": {"nim_current": nim_current, "nim_prev": nim_prev,
                     "decline_bps": decline_bps}}


def _check_cd_ratio(bs: list) -> Dict:
    """Flag #55: Credit-to-Deposit ratio abnormal."""
    flag = {"flag_number": 55, "flag_name": "Credit-Deposit Ratio Abnormal",
            "category": "Balance Sheet", "severity": "MEDIUM", "source": "API",
            "rule": "Triggers if CD ratio >80% (liquidity risk) or <55% (poor lending efficiency)"}

    if len(bs) < 1:
        return {**flag, "triggered": False, "reason": "Insufficient data"}

    advances = safe_get(bs[0], "advances")
    deposits = safe_get(bs[0], "deposits")

    if deposits <= 0:
        return {**flag, "triggered": False, "reason": "No deposit data available"}

    cd_ratio = (advances / deposits) * 100
    triggered = cd_ratio > 80 or cd_ratio < 55

    if cd_ratio > 80:
        direction = "High - liquidity risk"
    elif cd_ratio < 55:
        direction = "Low - poor lending efficiency"
    else:
        direction = "Normal range"

    trend = ""
    if len(bs) >= 2:
        prev_adv = safe_get(bs[1], "advances")
        prev_dep = safe_get(bs[1], "deposits")
        if prev_dep > 0:
            prev_cd = (prev_adv / prev_dep) * 100
            trend = f" (prev: {prev_cd:.1f}%)"

    return {**flag, "triggered": triggered, "confidence": 70 if triggered else 0,
            "evidence": f"CD ratio: {cd_ratio:.1f}%{trend} - {direction}. "
                        f"Advances: {fmt_b(advances)}, Deposits: {fmt_b(deposits)}",
            "data": {"cd_ratio": cd_ratio, "advances": advances, "deposits": deposits}}


def _check_capital_adequacy(pl: list) -> Dict:
    """Flag #56: Capital adequacy ratio near regulatory minimum."""
    flag = {"flag_number": 56, "flag_name": "Capital Adequacy Low",
            "category": "Balance Sheet", "severity": "HIGH", "source": "API",
            "rule": "Triggers if CET1 <7% or Tier-1 <9.5% or Tier-1 declined >1.5pp YoY"}

    if len(pl) < 1:
        return {**flag, "triggered": False, "reason": "Insufficient data"}

    cet1 = safe_get(pl[0], "cET1Ratio")
    at1 = safe_get(pl[0], "additionalTier1Ratio")
    tier1 = cet1 + at1

    if cet1 == 0:
        return {**flag, "triggered": False, "reason": "No capital adequacy data available"}

    low_cet1 = cet1 < 7.0
    low_tier1 = tier1 < 9.5

    declining = False
    prev_tier1 = 0
    if len(pl) >= 2:
        prev_cet1 = safe_get(pl[1], "cET1Ratio")
        prev_at1 = safe_get(pl[1], "additionalTier1Ratio")
        prev_tier1 = prev_cet1 + prev_at1
        if prev_tier1 > 0:
            declining = (prev_tier1 - tier1) > 1.5

    triggered = low_cet1 or low_tier1 or declining

    evidence = f"CET1: {cet1:.2f}%, AT1: {at1:.2f}%, Tier-1: {tier1:.2f}%"
    if prev_tier1 > 0:
        evidence += f" (prev Tier-1: {prev_tier1:.2f}%)"
    if low_cet1:
        evidence += " - CET1 below 7% minimum!"
    if low_tier1:
        evidence += " - Tier-1 below 9.5%!"
    if declining:
        evidence += " - Declining >1.5pp YoY!"

    return {**flag, "triggered": triggered, "confidence": 80 if triggered else 0,
            "evidence": evidence,
            "data": {"cet1": cet1, "at1": at1, "tier1": tier1,
                     "prev_tier1": prev_tier1}}
