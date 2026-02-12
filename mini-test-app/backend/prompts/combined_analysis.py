"""
Combined analysis prompts - Extract financial data + detect flags in single call.
"""

def get_combined_year_analysis_prompt(year: str, flag_numbers: list) -> str:
    """
    Generate a combined prompt that extracts financial data AND checks specific flags.
    
    For now, simplified to just extract financial data per year.
    Full flag integration will be added once working.
    """
    
    from prompts.financial_extraction import get_financial_extraction_prompt
    
    # For now, just return the financial extraction prompt
    # We'll add flag checking after testing this works
    return get_financial_extraction_prompt(year)


def get_multi_year_flags_prompt(years: list) -> str:
    """
    Generate prompt for flags that require multi-year comparison.
    
    Simplified version - checks key multi-year flags.
    """
    
    prompt = f"""
# MULTI-YEAR TREND ANALYSIS

You have access to 3 consecutive annual reports for years: {', '.join(years)}

Analyze trends across all 3 years to detect red flags. Focus on:

1. **Auditor Changes**: Frequent auditor changes (Flag #1)
2. **Cash Flow vs Profit**: Profit growing but cash flow declining (Flag #9, #11)
3. **Revenue Quality**: Declining asset turnover, inventory issues (Flag #13, #15)
4. **Promoter Trends**: Increasing pledging, decreasing shareholding (Flag #25, #26, #27)
5. **Financial Deterioration**: Working capital issues, liquidity problems (Flag #35, #38, #41)
6. **Operational Issues**: Declining margins, growth concerns (Flag #45, #46, #50, #51, #52)

For EACH red flag check, return JSON:

{{
  "flag_number": 1-54,
  "flag_name": "descriptive name",
  "category": "AUDITOR/CASHFLOW/PROMOTER/etc",
  "severity": "LOW/MEDIUM/HIGH/CRITICAL",
  "is_triggered": true/false,
  "confidence_score": 0-100,
  "evidence_text": "specific evidence with numbers from reports",
  "page_references": [page numbers if available],
  "extracted_data": {{relevant calculations}},
  "detection_method": "llm"
}}

## OUTPUT FORMAT

Return JSON:

```json
{{
  "red_flags": [
    {{ flag result 1 }},
    {{ flag result 2 }},
    ...
  ]
}}
```

IMPORTANT: Return ONLY valid JSON, no markdown code blocks.
"""
    
    return prompt
