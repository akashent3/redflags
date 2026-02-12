"""LLM prompt templates for Gemini Flash analysis."""

# Comprehensive financial data extraction from PDF sections
FINANCIAL_DATA_EXTRACTION_PROMPT = """You are a financial analyst examining an Indian company's annual report.

Analyze the following financial statement pages and extract ALL key financial metrics.
Extract BOTH current year and previous year values wherever available.

PAGES PROVIDED:
{section_pages_description}

INSTRUCTIONS:
1. Extract exact numerical values with their units (crores, lakhs, millions)
2. For EVERY metric, try to find both current_year and previous_year values
3. If a value is not found, omit it entirely (do NOT guess)
4. Pay attention to table headers - they usually show "As at March 31, 2024" and "As at March 31, 2023"
5. Extract from Balance Sheet, P&L, Cash Flow, and Notes sections

OUTPUT FORMAT (JSON only):
{{
    "balance_sheet": {{
        "total_assets": {{"value": 50000, "previous_year": 45000, "unit": "cr"}},
        "shareholders_equity": {{"value": 20000, "previous_year": 18000, "unit": "cr"}},
        "total_debt": {{"value": 15000, "previous_year": 12000, "unit": "cr"}},
        "current_assets": {{
            "trade_receivables": {{"value": 5000, "previous_year": 4000, "unit": "cr"}},
            "inventory": {{"value": 3000, "previous_year": 2500, "unit": "cr"}},
            "unbilled_revenue": {{"value": 0, "previous_year": 0, "unit": "cr"}},
            "contract_assets": {{"value": 0, "previous_year": 0, "unit": "cr"}}
        }},
        "current_liabilities": {{
            "trade_payables": {{"value": 4000, "previous_year": 3500, "unit": "cr"}},
            "short_term_borrowings": {{"value": 5000, "previous_year": 4000, "unit": "cr"}}
        }},
        "non_current_liabilities": {{
            "long_term_borrowings": {{"value": 10000, "previous_year": 8000, "unit": "cr"}}
        }},
        "non_current_assets": {{
            "intangible_assets": {{"value": 2000, "previous_year": 1500, "unit": "cr"}}
        }}
    }},
    "profit_loss": {{
        "revenue": {{"value": 80000, "previous_year": 70000, "unit": "cr"}},
        "cost_of_goods_sold": {{"value": 50000, "previous_year": 44000, "unit": "cr"}},
        "ebit": {{"value": 12000, "previous_year": 10000, "unit": "cr"}},
        "interest_expense": {{"value": 1500, "previous_year": 1200, "unit": "cr"}},
        "tax_expense": {{"value": 3000, "previous_year": 2500, "unit": "cr"}},
        "net_profit": {{"value": 8000, "previous_year": 7000, "unit": "cr"}},
        "depreciation": {{"value": 3000, "previous_year": 2500, "unit": "cr"}},
        "other_income": {{"value": 500, "previous_year": 400, "unit": "cr"}},
        "exceptional_items": {{"value": 0, "previous_year": 0, "unit": "cr"}}
    }},
    "cash_flow": {{
        "cash_from_operations": {{"value": 10000, "previous_year": 9000, "unit": "cr"}},
        "capital_expenditure": {{"value": -5000, "previous_year": -4000, "unit": "cr"}},
        "cash_from_investing": {{"value": -6000, "previous_year": -5000, "unit": "cr"}},
        "cash_from_financing": {{"value": -2000, "previous_year": -1000, "unit": "cr"}}
    }},
    "notes": {{
        "contingent_liabilities": {{"value": 3000, "unit": "cr"}},
        "managerial_remuneration": {{"value": 15, "unit": "cr"}},
        "assets_pledged": {{"value": 8000, "unit": "cr"}},
        "audit_fees": {{"value": 2, "unit": "cr"}}
    }},
    "shareholding_pattern": {{
        "promoter_holding_percentage": 55.0,
        "promoter_holding_percentage_previous": 56.0,
        "promoter_pledge_percentage": 10.0,
        "promoter_pledge_percentage_previous": 8.0
    }}
}}

Return ONLY valid JSON. No explanations."""


# Auditor report + RPT + Governance analysis
QUALITATIVE_ANALYSIS_PROMPT = """You are a financial forensic analyst examining an Indian company's annual report.

Analyze the following sections and extract structured data for red flag detection.

SECTIONS PROVIDED:
{section_pages_description}

EXTRACT THE FOLLOWING:

1. AUDITOR ANALYSIS:
   - Opinion type (Unqualified/Qualified/Adverse/Disclaimer)
   - Has Emphasis of Matter? (true/false) and details
   - Going concern issues? (true/false)
   - Key Audit Matters related to revenue? (true/false)
   - Material uncertainties mentioned
   - Any auditor resignation/change mentioned

2. RELATED PARTY TRANSACTIONS:
   - List all related parties with relationship type
   - Transaction amounts by type (sales, purchases, loans, guarantees)
   - Total RPT volume
   - Any loans to directors/KMP
   - Inter-corporate deposits
   - Number of subsidiaries/associates/JVs

3. CORPORATE GOVERNANCE:
   - Any independent director resignations
   - CFO or Company Secretary changes
   - Board meeting attendance issues
   - Audit committee composition concerns
   - Any SEBI/exchange penalties
   - Whistle-blower complaints
   - Filing delays

OUTPUT FORMAT (JSON only):
{{
    "auditor_analysis": {{
        "opinion_type": "Unqualified",
        "has_emphasis_of_matter": false,
        "emphasis_of_matter_details": "",
        "going_concern_issues": false,
        "material_uncertainties": [],
        "kam_on_revenue": false,
        "auditor_resignation": false,
        "auditor_change": false,
        "red_flags": []
    }},
    "related_party_transactions": {{
        "total_rpt_amount": 0,
        "rpt_unit": "cr",
        "sales": {{"value": 0, "previous_year": 0}},
        "purchases": {{"value": 0, "previous_year": 0}},
        "loans_given": {{"value": 0}},
        "advances": {{"value": 0}},
        "inter_corporate_deposits": {{"value": 0}},
        "loans_to_kmp": {{"value": 0}},
        "advances_to_directors": {{"value": 0}},
        "expenses": {{"value": 0}},
        "investments": {{"value": 0}},
        "guarantees": {{"value": 0}},
        "related_parties": [
            {{"name": "XYZ Ltd", "relationship": "Subsidiary", "transactions": []}}
        ],
        "subsidiaries": [],
        "associates": [],
        "joint_ventures": []
    }},
    "governance": {{
        "independent_director_resignation": false,
        "cfo_change": false,
        "cs_change": false,
        "board_attendance_issues": false,
        "audit_committee_concerns": false,
        "sebi_penalties": false,
        "penalty_amount": 0,
        "whistleblower_complaints": 0,
        "filing_delays": false,
        "concerns": []
    }}
}}

Return ONLY valid JSON. No explanations."""


# Textual / qualitative red flag analysis
TEXTUAL_ANALYSIS_PROMPT = """You are a forensic financial text analyst. Analyze the Management Discussion & Analysis (MD&A) and Directors Report sections for qualitative red flags.

SECTIONS PROVIDED:
{section_pages_description}

ANALYZE:
1. TONE: Is the management tone optimistic, neutral, defensive, or negative?
2. EVASIVENESS: Does management use vague language to explain poor performance?
3. CONTRADICTIONS: Does the narrative contradict the financial numbers?
4. JARGON: Is there excessive use of complex language to obscure meaning?
5. RISK DISCLOSURES: Are risk factors expanding or unusually detailed?
6. UNUSUAL LANGUAGE: Any hedging statements, qualifiers, or concerning phrases in auditor report?

Financial context for comparison:
{financial_summary}

OUTPUT FORMAT (JSON only):
{{
    "mda_tone": {{
        "tone": "neutral",
        "tone_score": 5,
        "key_findings": [],
        "concerning_quotes": [],
        "red_flag_severity": "low"
    }},
    "contradictions": {{
        "found": false,
        "details": [],
        "severity_score": 0,
        "red_flags_found": []
    }},
    "risk_factors": {{
        "risk_count": 0,
        "risk_density_per_1000_words": 0,
        "expanding": false
    }},
    "unusual_audit_language": {{
        "found": false,
        "details": [],
        "severity_score": 0,
        "red_flags_found": []
    }},
    "disclosure_quality": {{
        "mda_word_count": 0,
        "notes_word_count": 0,
        "is_unusually_short": false
    }}
}}

Return ONLY valid JSON. No explanations."""


# Fallback section detection prompt (when regex fails)
SECTION_DETECTION_FALLBACK_PROMPT = """You are analyzing an Indian annual report PDF to identify key financial sections.

Below is sampled text from various pages of the document (total {total_pages} pages).

SAMPLE TEXT:
{sample_text}

SECTIONS TO FIND:
auditor_report, directors_report, corporate_governance, balance_sheet,
profit_loss_statement, cash_flow_statement, notes_to_accounts,
management_discussion_analysis, related_party_transactions

INSTRUCTIONS:
1. Identify the START and END page numbers for each section
2. Look for table of contents, section headers, and page numbers
3. If a section is not found, omit it
4. Use PDF page numbers (not printed page numbers)

OUTPUT FORMAT (JSON only):
{{
    "auditor_report": {{"start": 45, "end": 51}},
    "balance_sheet": {{"start": 52, "end": 54}},
    "profit_loss_statement": {{"start": 55, "end": 56}},
    "cash_flow_statement": {{"start": 57, "end": 59}},
    "notes_to_accounts": {{"start": 60, "end": 142}}
}}

Return ONLY JSON."""
