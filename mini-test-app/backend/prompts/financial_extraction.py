"""Financial data extraction prompts for Gemini."""


FINANCIAL_EXTRACTION_PROMPT = """You are an expert financial analyst extracting data from annual reports.

TASK: Extract structured financial data from the {year} annual report.

CRITICAL INSTRUCTIONS:
1. Extract ONLY from the STANDALONE financial statements (not consolidated if both exist)
2. All amounts should be in CRORES (₹ Cr)
3. If a value is not found, use null (not 0)
4. Look for the most recent audited figures
5. For ratios/percentages, provide the actual number (not as text)

EXTRACT THE FOLLOWING:

## BALANCE SHEET DATA
- total_assets: Total Assets in crores
- total_liabilities: Total Liabilities in crores
- shareholders_equity: Shareholders' Equity / Net Worth in crores
- current_assets: Current Assets in crores
- current_liabilities: Current Liabilities in crores
- total_debt: Total Debt (Short-term + Long-term borrowings) in crores
- short_term_debt: Short-term borrowings in crores
- long_term_debt: Long-term borrowings in crores
- receivables: Trade Receivables / Debtors in crores
- inventory: Inventory / Stock in crores
- intangible_assets: Intangible Assets (including goodwill) in crores
- cash_and_equivalents: Cash and Cash Equivalents in crores
- contingent_liabilities: Contingent Liabilities (from notes to accounts) in crores

## PROFIT & LOSS DATA
- revenue: Total Revenue / Sales / Turnover in crores
- operating_revenue: Revenue from operations in crores
- other_income: Other Income in crores
- total_expenses: Total Expenses in crores
- ebitda: EBITDA (if explicitly stated) in crores
- ebit: EBIT / Operating Profit in crores
- pbt: Profit Before Tax in crores
- tax_expense: Tax Expense in crores
- pat: Profit After Tax / Net Profit in crores
- gross_profit_margin: Gross Profit Margin %
- net_profit_margin: Net Profit Margin %
- operating_margin: Operating Margin / EBITDA Margin %

## CASH FLOW DATA
- cfo: Cash Flow from Operating Activities in crores
- cfi: Cash Flow from Investing Activities in crores
- cff: Cash Flow from Financing Activities in crores
- capex: Capital Expenditure (usually negative in CFI) in crores
- free_cash_flow: Free Cash Flow (CFO - Capex) in crores

## AUDITOR INFORMATION
- auditor_name: Full name of statutory auditor firm (e.g., "Deloitte Haskins & Sells LLP")
- audit_opinion: Type of opinion (EXACTLY one of: "Unqualified", "Qualified", "Adverse", "Disclaimer")
- audit_date: Date of audit report (format: YYYY-MM-DD)
- audit_fees: Audit fees paid in lakhs
- going_concern_warning: true/false - Does the report mention going concern issues?
- emphasis_of_matter: true/false - Is there an Emphasis of Matter paragraph?
- qualified_reason: If qualified, the specific reason (else null)

## PROMOTER & SHAREHOLDING
- promoter_holding_percent: Promoter shareholding %
- promoter_pledge_percent: % of promoter shares pledged
- public_holding_percent: Public shareholding %
- number_of_independent_directors: Count of independent directors
- total_board_members: Total number of board members
- board_meetings_count: Number of board meetings held in the year

## RELATED PARTY TRANSACTIONS
- rpt_total: Total Related Party Transactions value in crores
- rpt_with_promoters: RPT with promoter entities in crores
- rpt_loans_given: Loans/advances given to related parties in crores
- rpt_purchases: Purchases from related parties in crores
- rpt_sales: Sales to related parties in crores

## KEY RATIOS (if explicitly stated in report)
- debt_to_equity: Debt to Equity Ratio
- current_ratio: Current Ratio
- return_on_equity: Return on Equity %
- return_on_assets: Return on Assets %
- receivables_days: Average receivables collection period (days)
- inventory_days: Average inventory holding period (days)
- payables_days: Average payables payment period (days)

## OTHER IMPORTANT DATA
- fiscal_year_end_date: Fiscal year end date (format: YYYY-MM-DD)
- number_of_employees: Total employee count
- revenue_per_employee: Revenue per employee (lakhs)
- top_customer_concentration: % of revenue from top customer (if disclosed)
- top_5_customer_concentration: % of revenue from top 5 customers (if disclosed)

OUTPUT FORMAT:
Return VALID JSON with this exact structure. Use null for any value not found:

{{
  "year": "{year}",
  "extracted_at": "<current_timestamp>",
  "balance_sheet": {{
    "total_assets": <number>,
    "total_liabilities": <number>,
    ...
  }},
  "profit_loss": {{
    "revenue": <number>,
    "pat": <number>,
    ...
  }},
  "cash_flow": {{
    "cfo": <number>,
    "cfi": <number>,
    ...
  }},
  "auditor": {{
    "auditor_name": "<string>",
    "audit_opinion": "<string>",
    ...
  }},
  "promoter": {{
    "promoter_holding_percent": <number>,
    ...
  }},
  "rpt": {{
    "rpt_total": <number>,
    ...
  }},
  "ratios": {{
    "debt_to_equity": <number>,
    ...
  }},
  "other": {{
    "fiscal_year_end_date": "<YYYY-MM-DD>",
    ...
  }}
}}

VALIDATION RULES:
- All monetary values must be positive (or null)
- Percentages must be between 0 and 100 (or null)
- Dates must be in YYYY-MM-DD format
- audit_opinion must be EXACTLY: "Unqualified", "Qualified", "Adverse", or "Disclaimer"
- Ensure balance sheet balances: total_assets ≈ total_liabilities + shareholders_equity

Begin extraction now.
"""


def get_financial_extraction_prompt(year: str) -> str:
    """Get the financial extraction prompt for a specific year."""
    return FINANCIAL_EXTRACTION_PROMPT.format(year=year)
