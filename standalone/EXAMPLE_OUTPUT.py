"""
Example output structure for standalone app.

This shows what the complete analysis result looks like.
"""

EXAMPLE_ANALYSIS_RESULT = {
    "analysis_id": "uuid-string",
    "status": "completed",
    "symbol": "RELIANCE",
    "fiscal_year": 2025,
    "statement_type": "consolidated",
    "created_at": "2025-02-09T12:00:00Z",
    "completed_at": "2025-02-09T12:01:30Z",
    "flags": [
        # Auditor flags (6) - from Gemini
        {
            "flag_id": 1,
            "flag_name": "Auditor Resignation Mid-Term",
            "category": "Auditor",
            "triggered": False,
            "severity": "CRITICAL",
            "evidence": "No auditor resignation mentioned in the annual report.",
            "page_references": [45],
            "confidence": 95,
            "value": None
        },
        # Cash Flow flags (8) - from FinEdge
        {
            "flag_id": 7,
            "flag_name": "PAT Growing, CFO Flat",
            "category": "Cash Flow",
            "triggered": False,
            "severity": "HIGH",
            "evidence": "PAT growth: 12.5%, CFO growth: 10.2%",
            "page_references": [],
            "confidence": 85,
            "value": {
                "pat_growth": 12.5,
                "cfo_growth": 10.2
            }
        },
        # ... 40 more flags
    ],
    "risk_score": {
        "risk_score": 45.2,
        "risk_level": "ELEVATED",
        "risk_description": "Multiple red flags detected across categories. Increased scrutiny recommended.",
        "category_scores": {
            "Auditor": 15.5,
            "Cash Flow": 42.3,
            "Related Party": 38.7,
            "Promoter": 52.1,
            "Governance": 25.0,
            "Balance Sheet": 48.9,
            "Revenue Quality": 30.5,
            "Textual Analysis": 20.0
        },
        "flags_triggered_count": 12,
        "flags_total_count": 42,
        "trigger_percentage": 28.6,
        "flags_by_severity": {
            "critical": 1,
            "high": 4,
            "medium": 6,
            "low": 1
        },
        "top_concerns": [
            {
                "flag_number": 22,
                "flag_name": "Promoter Pledge > 50%",
                "severity": "CRITICAL",
                "category": "Promoter",
                "confidence": 90,
                "evidence": "Promoter pledge at 55% of holdings"
            },
            # ... more concerns
        ],
        "category_breakdown": {
            "Auditor": {
                "score": 15.5,
                "flags_triggered": 1,
                "flags_total": 6,
                "max_possible_points": 200,
                "actual_points": 31.0
            },
            # ... other categories
        }
    },
    "errors": [],
    "metadata": {
        "total_flags": 42,
        "finedge_flags": 14,
        "gemini_flags": 28
    }
}

# Flag Distribution
FLAG_DISTRIBUTION = {
    "total": 42,
    "by_source": {
        "finedge": 14,
        "gemini": 28
    },
    "by_category": {
        "Auditor": {"total": 6, "finedge": 0, "gemini": 6, "weight": 0.20},
        "Cash Flow": {"total": 8, "finedge": 8, "gemini": 0, "weight": 0.18},
        "Related Party": {"total": 7, "finedge": 0, "gemini": 7, "weight": 0.15},
        "Promoter": {"total": 6, "finedge": 3, "gemini": 3, "weight": 0.15},
        "Governance": {"total": 4, "finedge": 0, "gemini": 4, "weight": 0.12},
        "Balance Sheet": {"total": 7, "finedge": 3, "gemini": 4, "weight": 0.10},
        "Revenue Quality": {"total": 3, "finedge": 1, "gemini": 2, "weight": 0.05},
        "Textual Analysis": {"total": 1, "finedge": 0, "gemini": 1, "weight": 0.05}
    },
    "by_severity": {
        "CRITICAL": 9,
        "HIGH": 16,
        "MEDIUM": 16,
        "LOW": 1
    }
}

# FinEdge Flags (14 total)
FINEDGE_FLAGS = {
    7: {"name": "PAT Growing, CFO Flat", "category": "Cash Flow", "severity": "HIGH"},
    8: {"name": "Receivables Growing > Revenue", "category": "Cash Flow", "severity": "HIGH"},
    9: {"name": "Inventory Growing > COGS", "category": "Cash Flow", "severity": "HIGH"},
    10: {"name": "Capex > Depreciation (>3x)", "category": "Cash Flow", "severity": "MEDIUM"},
    11: {"name": "Frequent Exceptional Items", "category": "Cash Flow", "severity": "MEDIUM"},
    12: {"name": "Negative CFO", "category": "Cash Flow", "severity": "HIGH"},
    13: {"name": "CCC > 120 days", "category": "Cash Flow", "severity": "MEDIUM"},
    14: {"name": "Unusual Other Income > 10%", "category": "Cash Flow", "severity": "MEDIUM"},
    22: {"name": "Promoter Pledge > 50%", "category": "Promoter", "severity": "CRITICAL"},
    23: {"name": "Promoter Pledge Increasing QoQ", "category": "Promoter", "severity": "HIGH"},
    24: {"name": "Promoter Selling Shares", "category": "Promoter", "severity": "MEDIUM"},
    32: {"name": "Debt Growing Faster than Equity", "category": "Balance Sheet", "severity": "HIGH"},
    33: {"name": "Interest Coverage < 2x", "category": "Balance Sheet", "severity": "HIGH"},
    38: {"name": "Intangible Assets Growing Fast", "category": "Balance Sheet", "severity": "MEDIUM"},
    39: {"name": "Revenue Concentrated in Q4 (>40%)", "category": "Revenue Quality", "severity": "MEDIUM"},
}

# Gemini Flags (28 total)
GEMINI_FLAGS = {
    1: {"name": "Auditor Resignation Mid-Term", "category": "Auditor", "severity": "CRITICAL"},
    2: {"name": "Qualified/Adverse/Disclaimer Opinion", "category": "Auditor", "severity": "CRITICAL"},
    3: {"name": "Emphasis of Matter Paragraph", "category": "Auditor", "severity": "HIGH"},
    4: {"name": "Going Concern Issue", "category": "Auditor", "severity": "CRITICAL"},
    5: {"name": "KAM on Revenue Recognition", "category": "Auditor", "severity": "HIGH"},
    6: {"name": "Audit Fees Declining", "category": "Auditor", "severity": "MEDIUM"},
    15: {"name": "RPT > 10% of Revenue", "category": "Related Party", "severity": "HIGH"},
    16: {"name": "Loans to Related Parties", "category": "Related Party", "severity": "HIGH"},
    17: {"name": "Purchases from RP at Premium", "category": "Related Party", "severity": "MEDIUM"},
    18: {"name": "Revenue from RP Increasing", "category": "Related Party", "severity": "MEDIUM"},
    19: {"name": "Complex Structure > 20 Subsidiaries", "category": "Related Party", "severity": "MEDIUM"},
    20: {"name": "Loans to Directors/KMP", "category": "Related Party", "severity": "HIGH"},
    21: {"name": "New Related Parties Added", "category": "Related Party", "severity": "MEDIUM"},
    25: {"name": "Disproportionate Managerial Remuneration", "category": "Promoter", "severity": "MEDIUM"},
    26: {"name": "Promoter Entity Name Change", "category": "Promoter", "severity": "LOW"},
    27: {"name": "ICDs to Promoter Group", "category": "Promoter", "severity": "HIGH"},
    28: {"name": "Independent Director Resignation", "category": "Governance", "severity": "HIGH"},
    29: {"name": "Related Party on Audit Committee", "category": "Governance", "severity": "MEDIUM"},
    30: {"name": "SEBI/Stock Exchange Penalties", "category": "Governance", "severity": "HIGH"},
    31: {"name": "Whistle-blower Complaints", "category": "Governance", "severity": "MEDIUM"},
    34: {"name": "Short-term Debt > 60% of Total", "category": "Balance Sheet", "severity": "HIGH"},
    35: {"name": "Contingent Liabilities > 20% NW", "category": "Balance Sheet", "severity": "HIGH"},
    36: {"name": "Frequent Debt Restructuring", "category": "Balance Sheet", "severity": "MEDIUM"},
    37: {"name": "Heavy Asset Pledging", "category": "Balance Sheet", "severity": "MEDIUM"},
    40: {"name": "Revenue Recognition Policy Changed", "category": "Revenue Quality", "severity": "HIGH"},
    41: {"name": "Unbilled Revenue Growing Faster", "category": "Revenue Quality", "severity": "MEDIUM"},
    42: {"name": "MD&A Tone is Defensive", "category": "Textual Analysis", "severity": "MEDIUM"},
}

if __name__ == "__main__":
    import json
    print("Example Analysis Result Structure:")
    print("=" * 60)
    print(json.dumps(EXAMPLE_ANALYSIS_RESULT, indent=2))
    print("\n" + "=" * 60)
    print(f"\nTotal Flags: {FLAG_DISTRIBUTION['total']}")
    print(f"FinEdge Flags: {FLAG_DISTRIBUTION['by_source']['finedge']}")
    print(f"Gemini Flags: {FLAG_DISTRIBUTION['by_source']['gemini']}")
