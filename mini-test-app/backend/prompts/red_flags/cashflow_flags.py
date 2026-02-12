"""Cash Flow red flag detection prompts (Flags 9-16) - HIGHEST PRIORITY."""

FLAG_9_PROFIT_GROWTH_CFO_FLAT = """
RED FLAG #9: Profit Growing but CFO Flat/Declining

OBJECTIVE: Detect when Net Profit is growing but Cash Flow from Operations is stagnant or declining over 3 years.

SEVERITY: HIGH
CATEGORY: CASH_FLOW

DETECTION LOGIC:
1. Calculate Profit CAGR: ((Year3_PAT / Year1_PAT) ^ (1/2)) - 1
2. Calculate CFO CAGR: ((Year3_CFO / Year1_CFO) ^ (1/2)) - 1
3. If Profit_CAGR > 10% AND CFO_CAGR <5% → Flag TRIGGERED
4. OR If Profit_CAGR > 0% AND CFO_CAGR < -5% → Flag TRIGGERED

FORMULA:
CAGR = ((Ending_Value / Beginning_Value) ^ (1 / Number_of_Years)) - 1

WHY IT MATTERS:
- Profit can be manipulated via accounting choices
- Cash flow is harder to fake
- Divergence suggests aggressive revenue recognition or working capital buildup

CONFIDENCE SCORING:
- 95-100: All 3 years of data available, clear divergence
- 85-94: Data available but some minor gaps
- <85: Missing data or uncertain calculations

OUTPUT JSON:
{{
  "flag_number": 9,
  "flag_name": "Profit growing but CFO flat/declining",
  "category": "CASH_FLOW",
  "severity": "HIGH",
  "is_triggered": true/false,
  "confidence_score": 0-100,
  "evidence_text": "Net profit grew at X% CAGR (₹A Cr to ₹B Cr) while CFO declined/stagnated at Y% CAGR (₹C Cr to ₹D Cr) over FY{year_1} to FY{year_3}",
  "page_references": [page numbers],
  "extracted_data": {{
    "year_1_pat": <number>,
    "year_2_pat": <number>,
    "year_3_pat": <number>,
    "profit_cagr_percent": <number>,
    "year_1_cfo": <number>,
    "year_2_cfo": <number>,
    "year_3_cfo": <number>,
    "cfo_cagr_percent": <number>,
    "divergence_percent": <profit_cagr - cfo_cagr>
  }},
  "detection_method": "llm"
}}

EXAMPLE (TRIGGERED):
Year 1: PAT = 500 Cr, CFO = 450 Cr
Year 2: PAT = 575 Cr, CFO = 420 Cr  
Year 3: PAT = 658 Cr, CFO = 380 Cr
Profit CAGR = 14.7%, CFO CAGR = -8.4%
→ is_triggered: true, divergence: 23.1%
"""


FLAG_10_CFO_PAT_RATIO_LOW = """
RED FLAG #10: CFO/PAT Ratio < 0.5

OBJECTIVE: Detect if Cash Flow from Operations is less than 50% of Net Profit in Year 3.

SEVERITY: HIGH
CATEGORY: CASH_FLOW

DETECTION LOGIC:
1. Get Year 3 CFO (Cash Flow from Operating Activities)
2. Get Year 3 PAT (Profit After Tax)
3. Calculate Ratio = CFO / PAT
4. If Ratio < 0.5 → Flag TRIGGERED

HEALTHY BENCHMARK:
- Good companies: CFO/PAT > 0.8 (cash conversion >80%)
- Acceptable: CFO/PAT = 0.5-0.8
- Warning: CFO/PAT < 0.5 (less than half of profits converting to cash)

WHY IT MATTERS:
- Low ratio suggests profits trapped in receivables/inventory
- Possible aggressive revenue recognition
- Working capital management issues

SPECIAL CASES:
- If CFO is negative and PAT is positive → Ratio will be negative → DEFINITELY TRIGGERED

CONFIDENCE SCORING:
- 95-100: Both CFO and PAT clearly stated
- 80-94: Values found but some calculation ambiguity
- <80: Missing or unclear data

OUTPUT JSON:
{{
  "flag_number": 10,
  "flag_name": "CFO/PAT ratio < 0.5",
  "category": "CASH_FLOW",
  "severity": "HIGH",
  "is_triggered": true/false,
  "confidence_score": 0-100,
  "evidence_text": "CFO/PAT ratio of X (CFO: ₹A Cr, PAT: ₹B Cr) in FY{year_3}, indicating only X% cash conversion",
  "page_references": [page numbers],
  "extracted_data": {{
    "year_3_cfo": <number>,
    "year_3_pat": <number>,
    "cfo_pat_ratio": <number>,
    "cash_conversion_percent": <ratio * 100>
  }},
  "detection_method": "llm"
}}
"""


FLAG_11_NEGATIVE_CFO_2PLUS_YEARS = """
RED FLAG #11: Negative CFO for 2+ Years

OBJECTIVE: Detect if Cash Flow from Operations was negative in 2 or more of the last 3 years.

SEVERITY: CRITICAL
CATEGORY: CASH_FLOW

DETECTION LOGIC:
1. Check Year 1 CFO: Negative?
2. Check Year 2 CFO: Negative?
3. Check Year 3 CFO: Negative?
4. Count negative years
5. If count >= 2 → Flag TRIGGERED

WHY IT MATTERS:
- Core business is burning cash
- Cannot sustain operations from own cash generation
- Reliance on external funding/debt
- Potential liquidity crisis

SPECIAL NOTE:
- One negative year may be due to one-time factors
- Two or more consecutive/intermittent negative years is a major red flag

CONFIDENCE SCORING:
- 100: All 3 years of CFO data available and clear
- 85-99: Most years available
- <85: Missing data for one or more years

OUTPUT JSON:
{{
  "flag_number": 11,
  "flag_name": "Negative CFO for 2+ years",
  "category": "CASH_FLOW",
  "severity": "CRITICAL",
  "is_triggered": true/false,
  "confidence_score": 0-100,
  "evidence_text": "Negative CFO in X out of 3 years: FY{list years with negative CFO}",
  "page_references": [page numbers],
  "extracted_data": {{
    "year_1_cfo": <number>,
    "year_2_cfo": <number>,
    "year_3_cfo": <number>,
    "negative_year_count": <number>,
    "negative_years": ["year_1/year_2/year_3"]
  }},
  "detection_method": "llm"
}}
"""


FLAG_12_EBIT_CFO_GAP_LARGE = """
RED FLAG #12: Large Gap Between EBIT and CFO

OBJECTIVE: Detect when EBIT is significantly higher than CFO in Year 3, suggesting accrual manipulation.

SEVERITY: HIGH
CATEGORY: CASH_FLOW

DETECTION LOGIC:
1. Get Year 3 EBIT (Operating Profit)
2. Get Year 3 CFO
3. Calculate Gap = EBIT - CFO
4. Calculate Gap% = (Gap / EBIT) * 100
5. If Gap% > 30% → Flag TRIGGERED

RATIONALE:
- In steady state, CFO should be close to EBIT (after adjusting for working capital changes)
- Large gap suggests:
  * Revenue recognized but cash not collected
  * Increasing receivables/inventory
  * Potential accounting manipulation

FORMULA:
gap_percent = ((EBIT - CFO) / EBIT) * 100

CONFIDENCE SCORING:
- 95-100: Both EBIT and CFO clearly available
- 80-94: Values found but need to derive EBIT
- <80: Unclear or missing data

OUTPUT JSON:
{{
  "flag_number": 12,
  "flag_name": "Large gap between EBIT and CFO",
  "category": "CASH_FLOW",
  "severity": "HIGH",
  "is_triggered": true/false,
  "confidence_score": 0-100,
  "evidence_text": "EBIT of ₹X Cr vs CFO of ₹Y Cr in FY{year_3}, gap of Z% indicates weak cash conversion",
  "page_references": [page numbers],
  "extracted_data": {{
    "year_3_ebit": <number>,
    "year_3_cfo": <number>,
    "gap_amount": <number>,
    "gap_percent": <number>
  }},
  "detection_method": "llm"
}}
"""


FLAG_13_INCREASING_WORKING_CAPITAL = """
RED FLAG #13: Increasing Working Capital Needs

OBJECTIVE: Detect significant increase in working capital absorption over 3 years.

SEVERITY: MEDIUM
CATEGORY: CASH_FLOW

DETECTION LOGIC:
1. Calculate Working Capital for each year: Current Assets - Current Liabilities
2. Calculate Change: Year3_WC - Year1_WC
3. Calculate Change% = (Change / Year1_WC) * 100
4. If Change% > 50% → Flag TRIGGERED

ALTERNATIVE CHECK (if working capital data not explicit):
- Check "Changes in Working Capital" line in Cash Flow Statement
- If this is large negative number (reducing CFO), it's draining cash

WHY IT MATTERS:
- Growing working capital ties up cash
- May indicate:
  * Slowing collections (rising receivables)
  * Inventory buildup
  * Aggressive payment delays

CONFIDENCE SCORING:
- 95-100: Clear working capital data for all 3 years
- 80-94: Data available but needs calculation
- <80: Incomplete data

OUTPUT JSON:
{{
  "flag_number": 13,
  "flag_name": "Increasing working capital needs",
  "category": "CASH_FLOW",
  "severity": "MEDIUM",
  "is_triggered": true/false,
  "confidence_score": 0-100,
  "evidence_text": "Working capital increased by X% from ₹A Cr to ₹B Cr over 3 years",
  "page_references": [page numbers],
  "extracted_data": {{
    "year_1_working_capital": <number>,
    "year_3_working_capital": <number>,
    "change_amount": <number>,
    "change_percent": <number>
  }},
  "detection_method": "llm"
}}
"""


FLAG_14_FREE_CASH_FLOW_NEGATIVE = """
RED FLAG #14: Free Cash Flow Negative

OBJECTIVE: Detect if Free Cash Flow (CFO - Capex) is negative in Year 3.

SEVERITY: MEDIUM
CATEGORY: CASH_FLOW

DETECTION LOGIC:
1. Get Year 3 CFO
2. Get Year 3 Capex (Capital Expenditure - usually found in CFI as negative value)
3. Calculate FCF = CFO - abs(Capex)
4. If FCF < 0 → Flag TRIGGERED

WHERE TO FIND CAPEX:
- Cash Flow Statement, under "Cash Flow from Investing Activities"
- Look for: "Purchase of fixed assets" or "Capital expenditure" (usually negative)
- Take absolute value for calculation

WHY IT MATTERS:
- FCF is cash available after maintaining/growing the business
- Negative FCF means company needs external funding
- Not always bad (growth companies), but worth flagging

CONFIDENCE SCORING:
- 95-100: Both CFO and Capex clearly stated
- 80-94: Values found but Capex needs extraction from CFI
- <80: Missing or unclear data

OUTPUT JSON:
{{
  "flag_number": 14,
  "flag_name": "Free cash flow negative",
  "category": "CASH_FLOW",
  "severity": "MEDIUM",
  "is_triggered": true/false,
  "confidence_score": 0-100,
  "evidence_text": "Negative FCF of ₹X Cr (CFO: ₹Y Cr, Capex: ₹Z Cr) in FY{year_3}",
  "page_references": [page numbers],
  "extracted_data": {{
    "year_3_cfo": <number>,
    "year_3_capex": <number>,
    "year_3_fcf": <number>
  }},
  "detection_method": "llm"
}}
"""


FLAG_15_CFO_VOLATILITY_HIGH = """
RED FLAG #15: High CFO Volatility

OBJECTIVE: Detect if CFO fluctuates wildly across 3 years, suggesting unstable cash generation.

SEVERITY: MEDIUM
CATEGORY: CASH_FLOW

DETECTION LOGIC:
1. Calculate standard deviation of CFO across 3 years
2. Calculate mean CFO
3. Calculate Coefficient of Variation = (Std Dev / Mean) * 100
4. If CV > 40% → Flag TRIGGERED

FORMULA:
mean = (Year1_CFO + Year2_CFO + Year3_CFO) / 3
variance = [(Y1_CFO - mean)^2 + (Y2_CFO - mean)^2 + (Y3_CFO - mean)^2] / 3
std_dev = sqrt(variance)
coefficient_of_variation = (std_dev / mean) * 100

WHY IT MATTERS:
- Stable companies have predictable cash flows
- High volatility suggests:
  * Lumpy revenue recognition
  * Working capital swings
  * Seasonal business patterns
  * Accounting irregularities

CONFIDENCE SCORING:
- 100: All 3 years of CFO available and clean
- 85-99: Data available with minor gaps
- <85: Missing data

OUTPUT JSON:
{{
  "flag_number": 15,
  "flag_name": "CFO volatility high",
  "category": "CASH_FLOW",
  "severity": "MEDIUM",
  "is_triggered": true/false,
  "confidence_score": 0-100,
  "evidence_text": "CFO showed high volatility with coefficient of variation of X% across 3 years",
  "page_references": [page numbers],
  "extracted_data": {{
    "year_1_cfo": <number>,
    "year_2_cfo": <number>,
    "year_3_cfo": <number>,
    "mean_cfo": <number>,
    "std_deviation": <number>,
    "coefficient_of_variation": <number>
  }},
  "detection_method": "llm"
}}
"""


FLAG_16_CASH_CONVERSION_CYCLE_LENGTHENING = """
RED FLAG #16: Cash Conversion Cycle Lengthening

OBJECTIVE: Detect if Cash Conversion Cycle increased by more than 30 days over 3 years.

SEVERITY: MEDIUM
CATEGORY: CASH_FLOW

DETECTION LOGIC:
1. Calculate for both Year 1 and Year 3:
   - Days Sales Outstanding (DSO) = (Receivables / Revenue) * 365
   - Days Inventory Outstanding (DIO) = (Inventory / COGS) * 365
   - Days Payables Outstanding (DPO) = (Payables / COGS or Purchases) * 365
   - CCC = DSO + DIO - DPO

2. Calculate Change = Year3_CCC - Year1_CCC
3. If Change > 30 days → Flag TRIGGERED

APPROXIMATIONS (if COGS not available):
- Use Revenue instead of COGS (less accurate but acceptable)
- Or find "Cost of goods sold" / "Cost of materials consumed" in P&L

WHY IT MATTERS:
- Longer cycle means more cash tied up
- Indicates operational inefficiency
- Potential collection/inventory issues

CONFIDENCE SCORING:
- 95-100: All components available for calculation
- 75-94: Most data available, some approximations
- <75: Significant data missing

OUTPUT JSON:
{{
  "flag_number": 16,
  "flag_name": "Cash conversion cycle lengthening",
  "category": "CASH_FLOW",
  "severity": "MEDIUM",
  "is_triggered": true/false,
  "confidence_score": 0-100,
  "evidence_text": "CCC increased from X days to Y days (+Z days change)",
  "page_references": [page numbers],
  "extracted_data": {{
    "year_1_ccc_days": <number>,
    "year_3_ccc_days": <number>,
    "change_days": <number>,
    "year_1_dso": <number>,
    "year_1_dio": <number>,
    "year_1_dpo": <number>,
    "year_3_dso": <number>,
    "year_3_dio": <number>,
    "year_3_dpo": <number>
  }},
  "detection_method": "llm"
}}
"""


def get_all_cashflow_prompts():
    """Return all 8 cash flow flag prompts."""
    return {
        9: FLAG_9_PROFIT_GROWTH_CFO_FLAT,
        10: FLAG_10_CFO_PAT_RATIO_LOW,
        11: FLAG_11_NEGATIVE_CFO_2PLUS_YEARS,
        12: FLAG_12_EBIT_CFO_GAP_LARGE,
        13: FLAG_13_INCREASING_WORKING_CAPITAL,
        14: FLAG_14_FREE_CASH_FLOW_NEGATIVE,
        15: FLAG_15_CFO_VOLATILITY_HIGH,
        16: FLAG_16_CASH_CONVERSION_CYCLE_LENGTHENING
    }
