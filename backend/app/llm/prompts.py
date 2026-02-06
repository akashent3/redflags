"""LLM prompt templates for various analysis tasks."""

# Section Detection Prompt
SECTION_DETECTION_PROMPT = """You are analyzing an annual report PDF to identify key financial sections.

Below is text from the first 50 pages of the document (total {total_pages} pages). Your task is to identify the page ranges where specific sections appear.

SAMPLE TEXT:
{sample_text}

SECTIONS TO FIND:
{sections}

INSTRUCTIONS:
1. Identify the START and END page numbers for each section
2. Look for table of contents, section headers, and page numbers
3. If a section is not found, omit it from the response
4. Use 1-based indexing (first page = 1)

OUTPUT FORMAT (JSON only):
{{
    "auditor_report": {{"start": 12, "end": 15}},
    "directors_report": {{"start": 18, "end": 35}},
    "balance_sheet": {{"start": 45, "end": 47}},
    ...
}}

Respond with JSON only, no additional text."""

# Financial Data Extraction Prompt
FINANCIAL_DATA_EXTRACTION_PROMPT = """Extract key financial metrics from the following financial statement text.

SECTION: {section_name}
FISCAL YEAR: {fiscal_year}

TEXT:
{section_text}

EXTRACT THE FOLLOWING (if present):
- Revenue (total revenue, sales)
- Net Profit / PAT (Profit After Tax)
- EBIT / Operating Profit
- Cash Flow from Operations (CFO)
- Total Debt
- Total Equity / Shareholders' Funds
- Accounts Receivable / Trade Receivables
- Inventory
- Current Assets
- Current Liabilities
- Audit Fees
- Promoter Shareholding %

OUTPUT FORMAT (JSON):
{{
    "revenue": {{"value": 150000, "unit": "cr", "currency": "INR"}},
    "net_profit": {{"value": 12000, "unit": "cr", "currency": "INR"}},
    "cash_flow_operations": {{"value": 10000, "unit": "cr", "currency": "INR"}},
    ...
}}

- Use "cr" for crores, "lakhs" for lakhs, "millions" for millions
- If a value is not found, omit it from the JSON
- Return only JSON, no explanation"""

# Related Party Transaction Analysis
RPT_ANALYSIS_PROMPT = """Analyze the related party transactions section to identify:

1. All related parties (subsidiaries, associates, joint ventures, promoter entities)
2. Nature of relationship
3. Transaction amounts
4. Transaction types (sales, purchases, loans, guarantees, etc.)

TEXT:
{rpt_text}

OUTPUT FORMAT (JSON):
{{
    "related_parties": [
        {{
            "name": "XYZ Limited",
            "relationship": "Subsidiary",
            "transactions": [
                {{"type": "Sales", "amount": 5000, "unit": "cr"}},
                {{"type": "Loans Given", "amount": 2000, "unit": "cr"}}
            ]
        }},
        ...
    ]
}}

Return only JSON."""

# Management Discussion & Analysis Tone
MDA_TONE_ANALYSIS_PROMPT = """Analyze the tone and language in this Management Discussion & Analysis section.

Assess:
1. Overall tone (optimistic, neutral, defensive, negative)
2. Use of vague or evasive language
3. Defensive explanations for poor performance
4. Increased complexity or jargon compared to previous years
5. Contradictions between text and reported numbers

TEXT:
{mda_text}

PREVIOUS YEAR CONTEXT (if available):
{previous_year_context}

OUTPUT FORMAT (JSON):
{{
    "tone": "defensive",
    "tone_score": 6.5,
    "key_findings": [
        "Increased use of passive voice when discussing losses",
        "Vague explanations for revenue decline",
        ...
    ],
    "concerning_quotes": [
        "Quote 1...",
        "Quote 2..."
    ],
    "red_flag_severity": "medium"
}}

Return only JSON."""

# Auditor Report Analysis
AUDITOR_REPORT_ANALYSIS_PROMPT = """Analyze the auditor's report for red flags or unusual language.

Look for:
1. Qualified opinion or disclaimers
2. "Emphasis of Matter" paragraphs
3. Going concern issues
4. Material uncertainties
5. Internal control weaknesses
6. Audit fee increases
7. Auditor changes

TEXT:
{auditor_report_text}

OUTPUT FORMAT (JSON):
{{
    "opinion_type": "Unqualified / Qualified / Adverse / Disclaimer",
    "has_emphasis_of_matter": true/false,
    "emphasis_of_matter_details": "...",
    "going_concern_issues": true/false,
    "material_uncertainties": ["..."],
    "red_flags": [
        "Auditor resigned after 2 years",
        "Qualified opinion on inventory valuation",
        ...
    ],
    "severity": "low / medium / high / critical"
}}

Return only JSON."""

# Cash Flow Quality Check
CASHFLOW_QUALITY_PROMPT = """Analyze the cash flow statement to assess cash flow quality.

Compare:
- Cash Flow from Operations (CFO) vs Net Profit
- CFO trend over 3 years
- Working capital changes
- Investing activities
- Financing activities

TEXT:
{cashflow_text}

NET PROFIT (for comparison): {net_profit}

OUTPUT FORMAT (JSON):
{{
    "cfo": {{"value": 10000, "unit": "cr"}},
    "cfo_pat_ratio": 0.85,
    "working_capital_increase": {{"value": -2000, "unit": "cr"}},
    "quality_score": 7.5,
    "concerns": [
        "CFO growing slower than PAT",
        "Large increase in receivables",
        ...
    ]
}}

Return only JSON."""

# Red Flag Text Detection
RED_FLAG_TEXT_DETECTION_PROMPT = """Analyze this text for financial red flags.

Look for:
- Defensive or evasive language
- Contradictions
- Unusual risk disclosures
- Changes in accounting policies
- One-time gains or exceptional items
- Related party concerns

TEXT:
{text}

CONTEXT: {context}

List any red flags found with severity (LOW/MEDIUM/HIGH/CRITICAL) and evidence quotes.

OUTPUT FORMAT (JSON):
{{
    "red_flags": [
        {{
            "flag": "Description",
            "severity": "HIGH",
            "evidence": "Quote from text",
            "category": "auditor / cashflow / related_party / etc."
        }},
        ...
    ]
}}

Return only JSON."""
