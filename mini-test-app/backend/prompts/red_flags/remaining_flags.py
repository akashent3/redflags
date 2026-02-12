"""
RED FLAG PROMPTS for flags 17-54

This file contains concise, accurate prompts for the remaining 38 red flags.
Due to file size, prompts are condensed but maintain specificity for 90-95% accuracy.
"""

# Flags 17-23: Related Party Transactions
RPT_FLAGS = {
    17: {
        "name": "RPT > 10% of revenue",
        "severity": "HIGH",
        "logic": "Total RPT / Revenue > 0.10 in Year 3",
        "prompt": "Calculate: (Total Related Party Transactions / Revenue) * 100. If > 10%, flag. Extract RPT from Notes to Accounts."
    },
    18: {
        "name": "RPT growing faster than revenue",
        "severity": "HIGH",
        "logic": "RPT CAGR > Revenue CAGR + 10%",
        "prompt": "Compare 3-year CAGR of RPT vs Revenue. If RPT growth exceeds revenue growth by >10 percentage points, flag."
    },
    19: {
        "name": "Loans to related parties",
        "severity": "CRITICAL",
        "logic": "Any loans/advances to related parties > ₹10 Cr",
        "prompt": "Find 'Loans and Advances to Related Parties' in notes. Any amount > ₹10 Cr triggers flag."
    },
    20: {
        "name": "Transactions with promoter entities",
        "severity": "MEDIUM",
        "logic": "Existence of significant promoter entity transactions",
        "prompt": "Check RPT note for transactions with promoter-owned entities. Material amounts trigger."
    },
    21: {
        "name": "Non-arm's length pricing",
        "severity": "HIGH",
        "logic": "LLM analysis of RPT pricing disclosures",
        "prompt": "Analyze RPT pricing disclosures. Flag if: prices differ from market rates, vague 'arm's length' claims without basis, or auditor raises concerns."
    },
    22: {
        "name": "Complex RPT structure",
        "severity": "MEDIUM",
        "logic": "Multiple layers/entities mentioned",
        "prompt": "Count distinct related party entities. If >10 entities with multiple transaction types, flag complexity."
    },
    23: {
        "name": "Undisclosed related parties",
        "severity": "HIGH",
        "logic": "Auditor/notes mention identification issues",
        "prompt": "Search for phrases: 'related party not disclosed', 'subsequently identified', 'potential related party'. Any mention triggers."
    }
}

# Flags 24-29: Promoter
PROMOTER_FLAGS = {
    24: {
        "name": "Promoter pledge > 50%",
        "severity": "CRITICAL",
        "logic": "Pledged % of promoter holdings > 50%",
        "prompt": "Find promoter pledge % in shareholding pattern. If >50%, flag. Look in 'Shareholding of Promoters' table."
    },
    25: {
        "name": "Promoter pledge increasing",
        "severity": "HIGH",
        "logic": "Year 3 pledge % > Year 1 pledge % + 10%",
        "prompt": "Compare pledge % across years. Increase >10 percentage points triggers flag."
    },
    26: {
        "name": "Promoter shareholding declining",
        "severity": "MEDIUM",
        "logic": "Promoter holding dropped >5% over 3 years",
        "prompt": "Compare promoter shareholding %. Decline >5 percentage points triggers."
    },
    27: {
        "name": "Frequent promoter changes",
        "severity": "HIGH",
        "logic": "Promoter director changes >2 in 3 years",
        "prompt": "Count promoter director resignations/appointments in Board composition notes. >2 changes triggers."
    },
    28: {
        "name": "Promoter transactions suspicious",
        "severity": "HIGH",
        "logic": "LLM analysis of promoter dealings",
        "prompt": "Analyze: large inter-corporate deposits to promoter entities, unexplained asset transfers, circular transactions. Suspicious patterns trigger."
    },
    29: {
        "name": "Promoter compensation excessive",
        "severity": "MEDIUM",
        "logic": "Promoter remuneration > 5% of revenue OR >10% of PAT",
        "prompt": "Sum all promoter director salaries. If (Total/Revenue>5%) OR (Total/PAT>10%), flag."
    }
}

# Flags 30-36: Corporate Governance
GOVERNANCE_FLAGS = {
    30: {
        "name": "Independent directors < 50%",
        "severity": "MEDIUM",
        "logic": "Independent directors / Total directors < 0.50",
        "prompt": "From board composition table: count independent vs total. If <50%, flag."
    },
    31: {
        "name": "CEO-Chairman same person",
        "severity": "LOW",
        "logic": "Same person holds both roles",
        "prompt": "Check if Chairman and MD/CEO are same person in management discussion. Triggers flag."
    },
    32: {
        "name": "Board meetings < 4 per year",
        "severity": "MEDIUM",
        "logic": "Number of board meetings < 4",
        "prompt": "Count board meetings from corporate governance report. <4 triggers (SEBI requirement minimum 4)."
    },
    33: {
        "name": "Audit committee composition weak",
        "severity": "MEDIUM",
        "logic": "Already covered in Flag 6, but check independence",
        "prompt": "Similar to Flag 6: <3 members, <67% independent, or non-independent chairman triggers."
    },
    34: {
        "name": "Related party on board",
        "severity": "MEDIUM",
        "logic": "Board member is also in RPT list",
        "prompt": "Cross-reference board member names with RPT disclosure entities. Match triggers."
    },
    35: {
        "name": "Frequent management changes",
        "severity": "HIGH",
        "logic": ">3 key management personnel changes in 3 years",
        "prompt": "Count CFO, CEO, COO, CS changes from annual reports. >3 changes triggers."
    },
    36: {
        "name": "Weak internal controls",
        "severity": "HIGH",
        "logic": "LLM analysis of internal control disclosures",
        "prompt": "Search for: 'material weakness', 'significant deficiency', 'control inadequacy'. Any mention triggers."
    }
}

# Flags 37-43: Balance Sheet
BALANCE_SHEET_FLAGS = {
    37: {
        "name": "Debt/Equity ratio > 2",
        "severity": "HIGH",
        "logic": "Total Debt / Equity > 2",
        "prompt": "Calculate: Total Debt / Shareholders Equity. If >2, flag. Use Year 3 data."
    },
    38: {
        "name": "Debt increasing rapidly",
        "severity": "MEDIUM",
        "logic": "Debt CAGR > 25%",
        "prompt": "Calculate debt 3-year CAGR. If >25%, flag rapid debt growth."
    },
    39: {
        "name": "Current ratio < 1",
        "severity": "HIGH",
        "logic": "Current Assets / Current Liabilities < 1",
        "prompt": "Calculate: Current Assets / Current Liabilities for Year 3. <1 triggers liquidity concern."
    },
    40: {
        "name": "Receivables days > 90",
        "severity": "MEDIUM",
        "logic": "DSO > 90 days",
        "prompt": "Calculate DSO = (Receivables / Revenue) * 365 for Year 3. >90 days triggers."
    },
    41: {
        "name": "Inventory days increasing",
        "severity": "MEDIUM",
        "logic": "DIO Year 3 > DIO Year 1 + 30 days",
        "prompt": "Calculate DIO = (Inventory / COGS) * 365 for Years 1,3. Increase >30 days triggers."
    },
    42: {
        "name": "Intangible assets > 30%",
        "severity": "MEDIUM",
        "logic": "Intangibles / Total Assets > 0.30",
        "prompt": "Calculate: (Intangible Assets / Total Assets) * 100. >30% triggers quality concern."
    },
    43: {
        "name": "Contingent liabilities large",
        "severity": "HIGH",
        "logic": "Contingent liabilities > 25% of equity",
        "prompt": "From notes: (Contingent Liabilities / Equity) * 100. >25% triggers."
    }
}

# Flags 44-48: Revenue 
REVENUE_FLAGS = {
    44: {
        "name": "Revenue recognition aggressive",
        "severity": "HIGH",
        "logic": "LLM analysis of revenue recognition policy",
        "prompt": "Analyze revenue recognition policy in accounting policies note. Flag if: bill-and-hold, channel stuffing indicators, revenue before delivery/acceptance, percentage completion issues."
    },
    45: {
        "name": "Revenue growth but margin decline",
        "severity": "MEDIUM",
        "logic": "Revenue up >10% but net margin down >200 bps",
        "prompt": "Compare Year 1 vs 3: If revenue growth >10% AND net margin declined >2%, flag quality concerns."
    },
    46: {
        "name": "One-time revenue spike",
        "severity": "MEDIUM",
        "logic": "Year 2 revenue >30% higher than both Year 1 and Year 3",
        "prompt": "Check if Year 2 revenue spikes significantly vs surrounding years, suggesting one-off event."
    },
    47: {
        "name": "Customer concentration high",
        "severity": "MEDIUM",
        "logic": "Top customer > 25% of revenue",
        "prompt": "From customer concentration disclosure: if any single customer >25%, flag dependency risk."
    },
    48: {
        "name": "Revenue reversals",
        "severity": "HIGH",
        "logic": "Mention of revenue write-backs",
        "prompt": "Search notes for: 'revenue reversal', 'sales return', 'write-back'. Material amounts trigger."
    }
}

# Flags 49-54: Textual (LLM-based)
TEXTUAL_FLAGS = {
    49: {
        "name": "MD&A tone defensive",
        "severity": "MEDIUM",
        "logic": "LLM sentiment analysis",
        "prompt": "Analyze Management Discussion & Analysis section. Flag if: excessive blame on external factors, minimal accountability, deflective language about underperformance, overly complex explanations for simple issues."
    },
    50: {
        "name": "Increased jargon/complexity",
        "severity": "MEDIUM",
        "logic": "Readability score declining",
        "prompt": "Compare MD&A complexity across years. Flag if Year 3 has significantly more jargon, longer sentences, or vague language vs Year 1."
    },
    51: {
        "name": "Disclosure quality declining",
        "severity": "MEDIUM",
        "logic": "Comparative disclosure analysis",
        "prompt": "Compare detail level in critical disclosures (RPT, contingencies, risks). Flag if Year 3 has less detail/transparency vs Year 1."
    },
    52: {
        "name": "Risk factors expanding",
        "severity": "MEDIUM",
        "logic": "Risk section length increased >50%",
        "prompt": "Compare risk factor section length. If Year 3 is >50% longer, suggests new concerns emerging."
    },
    53: {
        "name": "Contradictions in narrative",
        "severity": "HIGH",
        "logic": "LLM consistency check",
        "prompt": "Cross-check: MD&A claims vs actual numbers, director report vs notes, revenue explanation vs cash flow. Material contradictions trigger."
    },
    54: {
        "name": "Unusual audit language",
        "severity": "HIGH",
        "logic": "LLM analysis of audit hedging",
        "prompt": "Analyze auditor report for unusual hedging: excessive 'to the best of our knowledge', scope limitations, reliance on management representations beyond normal, vague language."
    }
}

def get_all_remaining_flags():
    """Combine all flags 17-54."""
    all_flags = {}
    
    # Combine all dictionaries
    all_flags.update({k: {**v, "category": "RELATED_PARTY"} for k, v in RPT_FLAGS.items()})
    all_flags.update({k: {**v, "category": "PROMOTER"} for k, v in PROMOTER_FLAGS.items()})
    all_flags.update({k: {**v, "category": "GOVERNANCE"} for k, v in GOVERNANCE_FLAGS.items()})
    all_flags.update({k: {**v, "category": "BALANCE_SHEET"} for k, v in BALANCE_SHEET_FLAGS.items()})
    all_flags.update({k: {**v, "category": "REVENUE"} for k, v in REVENUE_FLAGS.items()})
    all_flags.update({k: {**v, "category": "TEXTUAL"} for k, v in TEXTUAL_FLAGS.items()})
    
    return all_flags


def generate_flag_check_prompt(flag_num: int, flag_info: dict, financial_data: dict) -> str:
    """
    Generate a complete prompt for checking a specific flag.
    
    Args:
        flag_num: Flag number (17-54)
        flag_info: Flag configuration dict
        financial_data: Extracted financial data from all 3 years
    
    Returns:
        Complete prompt string
    """
    return f"""
RED FLAG #{flag_num}: {flag_info['name']}

SEVERITY: {flag_info['severity']}
CATEGORY: {flag_info['category']}

DETECTION LOGIC:
{flag_info['logic']}

SPECIFIC INSTRUCTIONS:
{flag_info['prompt']}

AVAILABLE DATA:
You have access to 3 years of extracted financial data and the full annual reports.

OUTPUT REQUIRED:
Return VALID JSON matching this structure:
{{
  "flag_number": {flag_num},
  "flag_name": "{flag_info['name']}",
  "category": "{flag_info['category']}",
  "severity": "{flag_info['severity']}",
  "is_triggered": true/false,
  "confidence_score": 0-100,
  "evidence_text": "Specific evidence from documents with numbers/quotes",
  "page_references": [list of page numbers],
  "extracted_data": {{"key": "value pairs showing your calculation/finding"}},
  "detection_method": "llm"
}}

CRITICAL: 
- Be specific in evidence_text with actual numbers
- Only trigger if criteria clearly met
- Confidence score should reflect data quality and certainty
- extracted_data should show your work (calculations, comparisons, etc.)

Begin analysis now.
"""
