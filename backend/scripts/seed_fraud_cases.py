#!/usr/bin/env python3
"""
Seed script: Generate 50 Indian corporate fraud cases using Gemini AI.

This script replaces the old PDF-based analyze_fraud_case.py workflow.
Instead of requiring PDFs + FinEdge API, it uses Gemini's knowledge of
well-documented Indian corporate frauds to generate structured data that
is COMPATIBLE with the real analysis engine's flag schema.

Red flags generated use the SAME flag_number, flag_name, category, severity
as the real analysis engine (api_flags.py + gemini_analyzer.py) so that
pattern matching works correctly.

Usage:
    cd backend
    python scripts/seed_fraud_cases.py

Optional flags:
    --limit 10          # Only generate first 10 cases (for testing)
    --skip-existing     # Skip cases already in DB (default: True)
    --clear-all         # Delete all existing fraud cases before seeding

Requirements:
    - GEMINI_API_KEY set in backend/.env
    - Database running and migrated
"""

import argparse
import json
import logging
import sys
import time
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

import google.generativeai as genai
from app.database import SessionLocal
from app.models.fraud_case import FraudCase
from app.config import settings

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Configure Gemini
# ---------------------------------------------------------------------------
genai.configure(api_key=settings.gemini_api_key)
model = genai.GenerativeModel('gemini-2.5-pro')

# ---------------------------------------------------------------------------
# EXACT red flag registry from the real analysis engine.
#
# Sources:
#   api_flags.py  — Non-bank: #7,8,9,11,13,14,43,46,47,32,33,34,38,44,45,48,49,60,39 + #22,23,24
#                 — Bank:     B1-B15 (flag_numbers 101-115) + #22,23,24
#   gemini_analyzer.py — Non-bank: #2,3,4,6,15,16,17,18,20,25,27,29,30,31,35,36,37,50,40,41,42,51
#                       — Bank:    B16-B32 (flag_numbers 116-132) — COMPLETELY SEPARATE SET
#
# BANKING FLAGS REVAMP: Banks/NBFCs now use flag_numbers 101-132 exclusively.
# Old bank flags (#52-#59) are retired. Non-bank flags do NOT appear for banks.
#
# flag_name, category, severity must EXACTLY match source files for
# Jaccard-similarity pattern matching to work correctly.
# ---------------------------------------------------------------------------
FLAG_REGISTRY = {
    # ── Auditor Flags (gemini_analyzer.py — non-bank only) ─────────────────
    2:  {"flag_name": "Qualified/Adverse/Disclaimer Opinion", "category": "Auditor",       "severity": "CRITICAL"},
    3:  {"flag_name": "Emphasis of Matter",                   "category": "Auditor",       "severity": "MEDIUM"},
    4:  {"flag_name": "Going Concern Doubt",                  "category": "Auditor",       "severity": "CRITICAL"},
    6:  {"flag_name": "Audit Fees Unusual",                   "category": "Auditor",       "severity": "MEDIUM"},

    # ── Cash Flow Flags (api_flags.py — non-bank only) ──────────────────────
    7:  {"flag_name": "PAT vs CFO Divergence",                "category": "Cash Flow",     "severity": "HIGH"},
    8:  {"flag_name": "Receivables > Revenue Growth",         "category": "Cash Flow",     "severity": "HIGH"},
    9:  {"flag_name": "Inventory > COGS Growth",              "category": "Cash Flow",     "severity": "MEDIUM"},
    11: {"flag_name": "Exceptional Items Material",           "category": "Cash Flow",     "severity": "MEDIUM"},
    13: {"flag_name": "Cash Conversion Cycle Deteriorating",  "category": "Cash Flow",     "severity": "MEDIUM"},
    14: {"flag_name": "Other Income Dependency",              "category": "Cash Flow",     "severity": "LOW"},
    43: {"flag_name": "Low CFO to EBITDA Ratio (3Y)",         "category": "Cash Flow",     "severity": "HIGH"},
    46: {"flag_name": "Low Cash Yield",                       "category": "Cash Flow",     "severity": "MEDIUM"},
    47: {"flag_name": "Low Free Cash vs Obligations",         "category": "Cash Flow",     "severity": "LOW"},

    # ── Related Party Flags (gemini_analyzer.py — non-bank only) ────────────
    15: {"flag_name": "RPT > 10% Revenue",                    "category": "Related Party", "severity": "HIGH"},
    16: {"flag_name": "Loans to Related Parties",             "category": "Related Party", "severity": "HIGH"},
    17: {"flag_name": "RP Premium/Non-Arms Length Transactions","category":"Related Party", "severity": "HIGH"},
    18: {"flag_name": "RPT Revenue Increasing",               "category": "Related Party", "severity": "MEDIUM"},
    20: {"flag_name": "Loans to Directors",                   "category": "Related Party", "severity": "CRITICAL"},
    51: {"flag_name": "JV/Associate Loss Hiding",             "category": "Related Party", "severity": "MEDIUM"},

    # ── Promoter Flags (api_flags.py — both non-bank and bank) ──────────────
    22: {"flag_name": "High Promoter Pledge",                 "category": "Promoter",      "severity": "CRITICAL"},
    23: {"flag_name": "Promoter Pledge Increasing",           "category": "Promoter",      "severity": "HIGH"},
    24: {"flag_name": "Promoter Holding Declining",           "category": "Promoter",      "severity": "MEDIUM"},

    # ── Promoter Flags (gemini_analyzer.py — non-bank only) ─────────────────
    25: {"flag_name": "Disproportionate Director Salary",     "category": "Promoter",      "severity": "MEDIUM"},
    27: {"flag_name": "Inter-Corporate Deposits",             "category": "Promoter",      "severity": "HIGH"},

    # ── Governance Flags (gemini_analyzer.py — non-bank only) ───────────────
    29: {"flag_name": "Audit Committee Issues",               "category": "Governance",    "severity": "MEDIUM"},
    30: {"flag_name": "SEBI/Legal Penalties",                 "category": "Governance",    "severity": "HIGH"},
    31: {"flag_name": "Whistleblower Complaints",             "category": "Governance",    "severity": "CRITICAL"},

    # ── Balance Sheet Flags (api_flags.py — non-bank only) ──────────────────
    32: {"flag_name": "High Debt to Equity",                  "category": "Balance Sheet", "severity": "HIGH"},
    33: {"flag_name": "Low Interest Coverage",                "category": "Balance Sheet", "severity": "HIGH"},
    34: {"flag_name": "High Short-Term Debt Ratio",           "category": "Balance Sheet", "severity": "MEDIUM"},
    38: {"flag_name": "Intangibles Growing",                  "category": "Balance Sheet", "severity": "MEDIUM"},
    44: {"flag_name": "CWIP Aging",                           "category": "Balance Sheet", "severity": "MEDIUM"},
    45: {"flag_name": "Depreciation Rate Declining",          "category": "Balance Sheet", "severity": "MEDIUM"},
    48: {"flag_name": "Abnormal Implied Interest Rate",       "category": "Balance Sheet", "severity": "MEDIUM"},
    49: {"flag_name": "Net Worth Declining",                  "category": "Balance Sheet", "severity": "MEDIUM"},

    # ── Balance Sheet Flags (gemini_analyzer.py — non-bank only) ────────────
    35: {"flag_name": "Contingent Liabilities High",          "category": "Balance Sheet", "severity": "HIGH"},
    36: {"flag_name": "Debt Restructuring",                   "category": "Balance Sheet", "severity": "CRITICAL"},
    37: {"flag_name": "Asset Pledging",                       "category": "Balance Sheet", "severity": "MEDIUM"},
    50: {"flag_name": "Bad Debt Provisioning Increasing",     "category": "Balance Sheet", "severity": "MEDIUM"},

    # ── Revenue Flags (api_flags.py — non-bank only) ─────────────────────────
    39: {"flag_name": "Q4 Revenue Concentration",             "category": "Revenue",       "severity": "MEDIUM"},

    # ── Revenue Flags (gemini_analyzer.py — non-bank only) ───────────────────
    40: {"flag_name": "Revenue Recognition Policy Change",    "category": "Revenue",       "severity": "HIGH"},
    41: {"flag_name": "Unbilled Revenue High",                "category": "Revenue",       "severity": "MEDIUM"},

    # ── Textual Flags (gemini_analyzer.py — non-bank only) ───────────────────
    42: {"flag_name": "MD&A Tone Defensive",                  "category": "Textual",       "severity": "MEDIUM"},

    # ── Revenue / Balance Sheet (api_flags.py — non-bank only) ─────────────
    60: {"flag_name": "Tax Divergence",                       "category": "Revenue",       "severity": "HIGH"},

    # ═══════════════════════════════════════════════════════════════════════
    # BANK/NBFC FLAG BLOCK (101-132) — Complete revamp, replaces old #52-#59
    # B1-B15 (101-115): api_flags.py  |  B16-B32 (116-132): gemini_analyzer.py
    # ═══════════════════════════════════════════════════════════════════════

    # ── B1-B15: API-calculated bank flags (api_flags.py — bank only) ────────
    101: {"flag_name": "Yield on Advances",                   "category": "Balance Sheet", "severity": "MEDIUM"},
    102: {"flag_name": "Cost of Funds",                       "category": "Balance Sheet", "severity": "MEDIUM"},
    103: {"flag_name": "Net Interest Margin (NIM) Proxy",     "category": "Cash Flow",     "severity": "MEDIUM"},
    104: {"flag_name": "Cost-to-Income Ratio",                "category": "Cash Flow",     "severity": "MEDIUM"},
    105: {"flag_name": "Provision Coverage Ratio (PCR)",      "category": "Balance Sheet", "severity": "HIGH"},
    106: {"flag_name": "Credit Cost",                         "category": "Balance Sheet", "severity": "HIGH"},
    107: {"flag_name": "Texas Ratio",                         "category": "Balance Sheet", "severity": "CRITICAL"},
    108: {"flag_name": "Return on Assets (ROA)",              "category": "Cash Flow",     "severity": "MEDIUM"},
    109: {"flag_name": "Return on Equity (ROE)",              "category": "Cash Flow",     "severity": "MEDIUM"},
    110: {"flag_name": "CFO to PAT Ratio (Earnings Quality)", "category": "Cash Flow",     "severity": "HIGH"},
    111: {"flag_name": "Treasury Dependence",                 "category": "Cash Flow",     "severity": "MEDIUM"},
    112: {"flag_name": "Employee Cost Burden",                "category": "Cash Flow",     "severity": "LOW"},
    113: {"flag_name": "Gross NPA Ratio",                     "category": "Balance Sheet", "severity": "CRITICAL"},
    114: {"flag_name": "Net NPA Ratio",                       "category": "Balance Sheet", "severity": "HIGH"},
    115: {"flag_name": "Core Capital Quality (CET1)",         "category": "Balance Sheet", "severity": "HIGH"},

    # ── B16-B32: Gemini-analyzed bank flags (gemini_analyzer.py — bank only) ─
    116: {"flag_name": "NPA Divergence",                      "category": "Balance Sheet", "severity": "CRITICAL"},
    117: {"flag_name": "Slippage Ratio",                      "category": "Balance Sheet", "severity": "HIGH"},
    118: {"flag_name": "Write-off Dependency",                "category": "Balance Sheet", "severity": "HIGH"},
    119: {"flag_name": "Watchlist / SMA-2 Book",              "category": "Balance Sheet", "severity": "HIGH"},
    120: {"flag_name": "Restructured Book Size",              "category": "Balance Sheet", "severity": "HIGH"},
    121: {"flag_name": "Security Receipts (SR) Buildup",      "category": "Balance Sheet", "severity": "HIGH"},
    122: {"flag_name": "Evergreening Proxy",                  "category": "Balance Sheet", "severity": "CRITICAL"},
    123: {"flag_name": "ALM Mismatch",                        "category": "Cash Flow",     "severity": "HIGH"},
    124: {"flag_name": "Bulk Deposit Dependence",             "category": "Cash Flow",     "severity": "MEDIUM"},
    125: {"flag_name": "CASA Ratio Erosion",                  "category": "Cash Flow",     "severity": "MEDIUM"},
    126: {"flag_name": "Contingent Liability Overload",       "category": "Balance Sheet", "severity": "HIGH"},
    127: {"flag_name": "Deferred Tax Asset (DTA) Bloat",      "category": "Balance Sheet", "severity": "MEDIUM"},
    128: {"flag_name": "Related Party Transactions",          "category": "Related Party", "severity": "HIGH"},
    129: {"flag_name": "Auditor Remuneration Skew",           "category": "Auditor",       "severity": "MEDIUM"},
    130: {"flag_name": "Top 20 Borrowers Exposure",           "category": "Balance Sheet", "severity": "HIGH"},
    131: {"flag_name": "Sectoral Concentration",              "category": "Balance Sheet", "severity": "MEDIUM"},
    132: {"flag_name": "Auditor Qualifications",              "category": "Auditor",       "severity": "CRITICAL"},
}

# ---------------------------------------------------------------------------
# 50 well-documented Indian corporate fraud cases
# Covering diverse sectors, years, fraud types
# ---------------------------------------------------------------------------
FRAUD_COMPANIES = [
    # --- Landmark / Large Cases ---
    {"company": "Satyam Computer Services", "symbol": "SATYAM", "year": 2009, "sector": "IT Services",     "industry": "Software Services",    "fraud_type": "Accounting Fraud"},
    {"company": "Kingfisher Airlines",      "symbol": "KINGFISHERAIR", "year": 2012, "sector": "Aviation", "industry": "Airlines",              "fraud_type": "Diversion of Funds"},
    {"company": "IL&FS",                    "symbol": "ILFS",    "year": 2018, "sector": "Infrastructure", "industry": "Infrastructure Finance","fraud_type": "Debt Concealment"},
    {"company": "DHFL",                     "symbol": "DHFL",    "year": 2019, "sector": "NBFC",           "industry": "Housing Finance",       "fraud_type": "Diversion of Funds"},
    {"company": "Punjab National Bank",     "symbol": "PNB",     "year": 2018, "sector": "Banking",        "industry": "Public Sector Banking", "fraud_type": "Bank Fraud"},
    # --- Mid-Size Fraud Cases ---
    {"company": "Unitech",                  "symbol": "UNITECH", "year": 2017, "sector": "Real Estate",    "industry": "Real Estate Development","fraud_type": "Diversion of Funds"},
    {"company": "Vakrangee",                "symbol": "VAKRANGEE","year": 2018,"sector": "IT Services",    "industry": "Technology Services",   "fraud_type": "Accounting Fraud"},
    {"company": "PC Jeweller",              "symbol": "PCJEWELLER","year": 2018,"sector": "Retail",        "industry": "Jewellery Retail",      "fraud_type": "Related Party Transactions"},
    {"company": "Manpasand Beverages",      "symbol": "MANPASAND","year": 2019,"sector": "FMCG",          "industry": "Beverages",             "fraud_type": "Accounting Fraud"},
    {"company": "Café Coffee Day",          "symbol": "COFFEDAY", "year": 2019,"sector": "Retail",         "industry": "F&B Retail",            "fraud_type": "Diversion of Funds"},
    # --- NBFC / Finance Sector ---
    {"company": "Dewan Housing Finance",    "symbol": "DHFL",    "year": 2019, "sector": "NBFC",           "industry": "Housing Finance",       "fraud_type": "Diversion of Funds"},
    {"company": "Reliance Capital",         "symbol": "RELCAPITAL","year": 2021,"sector": "NBFC",         "industry": "Diversified Finance",   "fraud_type": "Diversion of Funds"},
    {"company": "SREI Infrastructure Finance","symbol":"SREINFRA","year": 2021,"sector": "NBFC",           "industry": "Infrastructure Finance","fraud_type": "Diversion of Funds"},
    {"company": "Altico Capital",           "symbol": "ALTICO",  "year": 2019, "sector": "NBFC",           "industry": "Real Estate Finance",   "fraud_type": "Debt Concealment"},
    {"company": "Cox & Kings",              "symbol": "COXANDKINGS","year": 2019,"sector": "Travel",       "industry": "Travel & Tourism",      "fraud_type": "Accounting Fraud"},
    # --- Banking Frauds ---
    {"company": "Yes Bank",                 "symbol": "YESBANK", "year": 2020, "sector": "Banking",        "industry": "Private Sector Banking","fraud_type": "Ever-greening of Loans"},
    {"company": "Lakshmi Vilas Bank",       "symbol": "LAKSHVIL","year": 2020, "sector": "Banking",        "industry": "Private Sector Banking","fraud_type": "Governance Failure"},
    {"company": "PMC Bank",                 "symbol": "PMCBANK", "year": 2019, "sector": "Banking",        "industry": "Cooperative Banking",   "fraud_type": "Accounting Fraud"},
    {"company": "Bank of Baroda Forex Fraud","symbol":"BANKBARODA","year": 2015,"sector": "Banking",       "industry": "Public Sector Banking", "fraud_type": "Bank Fraud"},
    {"company": "ABG Shipyard",             "symbol": "ABGSHIP", "year": 2022, "sector": "Manufacturing",  "industry": "Shipbuilding",          "fraud_type": "Bank Fraud"},
    # --- Real Estate / Construction ---
    {"company": "Amrapali Group",           "symbol": "AMRAPALI","year": 2017, "sector": "Real Estate",    "industry": "Real Estate Development","fraud_type": "Diversion of Funds"},
    {"company": "Jaypee Infratech",         "symbol": "JPINFRA", "year": 2017, "sector": "Infrastructure", "industry": "Real Estate",           "fraud_type": "Diversion of Funds"},
    {"company": "Omaxe",                    "symbol": "OMAXE",   "year": 2018, "sector": "Real Estate",    "industry": "Real Estate Development","fraud_type": "Accounting Fraud"},
    {"company": "Supertech",                "symbol": "SUPERTECH","year": 2021, "sector": "Real Estate",   "industry": "Real Estate Development","fraud_type": "Diversion of Funds"},
    {"company": "3i Infotech",              "symbol": "3IINFO",  "year": 2014, "sector": "IT Services",    "industry": "IT & BPO",              "fraud_type": "Accounting Fraud"},
    # --- Pharma / Healthcare ---
    {"company": "Ranbaxy Laboratories",     "symbol": "RANBAXY", "year": 2013, "sector": "Pharmaceuticals","industry": "Pharmaceuticals",       "fraud_type": "Regulatory Fraud"},
    {"company": "Agrimony Group",           "symbol": "AGRIMONY","year": 2020, "sector": "Pharmaceuticals","industry": "Pharmaceuticals",       "fraud_type": "Accounting Fraud"},
    {"company": "Surana Solar",             "symbol": "SURANASL","year": 2016, "sector": "Energy",         "industry": "Solar Energy",          "fraud_type": "Accounting Fraud"},
    # --- Telecom ---
    {"company": "Aircel",                   "symbol": "AIRCEL",  "year": 2018, "sector": "Telecom",        "industry": "Mobile Telecom",        "fraud_type": "Diversion of Funds"},
    {"company": "Videocon Industries",      "symbol": "VIDEOIND","year": 2019, "sector": "Manufacturing",  "industry": "Consumer Electronics",  "fraud_type": "Diversion of Funds"},
    # --- Metals / Mining ---
    {"company": "Bhushan Steel",            "symbol": "BHUSANSTL","year": 2017,"sector": "Manufacturing",  "industry": "Steel Manufacturing",   "fraud_type": "Diversion of Funds"},
    {"company": "Electrotherm India",       "symbol": "ELECTHERM","year": 2015,"sector": "Manufacturing",  "industry": "Steel & Power",         "fraud_type": "Accounting Fraud"},
    {"company": "KSK Energy Ventures",      "symbol": "KSKPWR",  "year": 2018, "sector": "Energy",         "industry": "Power Generation",      "fraud_type": "Diversion of Funds"},
    {"company": "Ruchi Soya (pre-2019)",    "symbol": "RUCHISOYA","year": 2019,"sector": "FMCG",           "industry": "Edible Oils & Food",    "fraud_type": "Debt Concealment"},
    {"company": "Lanco Infratech",          "symbol": "LANCI",   "year": 2016, "sector": "Infrastructure", "industry": "Power & Infrastructure","fraud_type": "Diversion of Funds"},
    # --- Smaller Cap / Micro-Cap Frauds ---
    {"company": "Gitanjali Gems",           "symbol": "GITANJALI","year": 2018,"sector": "Retail",         "industry": "Gems & Jewellery",      "fraud_type": "Bank Fraud"},
    {"company": "Winsome Diamonds",         "symbol": "WINSOME", "year": 2013, "sector": "Retail",         "industry": "Gems & Jewellery",      "fraud_type": "Bank Fraud"},
    {"company": "Shree Ganesh Jewellery",   "symbol": "SHREEGJ", "year": 2014, "sector": "Retail",         "industry": "Gems & Jewellery",      "fraud_type": "Accounting Fraud"},
    {"company": "HDIL",                     "symbol": "HDIL",    "year": 2019, "sector": "Real Estate",    "industry": "Real Estate Development","fraud_type": "Diversion of Funds"},
    {"company": "Deccan Chronicle",         "symbol": "DECCHRONI","year": 2014,"sector": "Media",          "industry": "Print Media",           "fraud_type": "Accounting Fraud"},
    # --- Promoter Diversion / Pledge Triggers ---
    {"company": "Zee Entertainment (2019 crisis)","symbol":"ZEEL","year": 2019,"sector": "Media",          "industry": "Broadcasting",          "fraud_type": "Promoter Pledge"},
    {"company": "Essel Group Companies",    "symbol": "ESSEL",   "year": 2019, "sector": "Media",          "industry": "Diversified Media",     "fraud_type": "Promoter Pledge"},
    {"company": "Indiabulls Housing Finance","symbol":"IBULHSGFIN","year": 2019,"sector":"NBFC",            "industry": "Housing Finance",       "fraud_type": "Related Party Transactions"},
    {"company": "ADAG Group Companies",     "symbol": "RCOM",    "year": 2019, "sector": "Telecom",        "industry": "Telecom & Finance",     "fraud_type": "Diversion of Funds"},
    {"company": "Radius Developer",         "symbol": "RADIUS",  "year": 2020, "sector": "Real Estate",    "industry": "Real Estate Development","fraud_type": "Diversion of Funds"},
    # --- Recent / Post-2020 ---
    {"company": "Future Retail",            "symbol": "FRETAIL", "year": 2021, "sector": "Retail",         "industry": "Retail Chains",         "fraud_type": "Diversion of Funds"},
    {"company": "Go First Airlines",        "symbol": "GOAIR",   "year": 2023, "sector": "Aviation",       "industry": "Airlines",              "fraud_type": "Debt Concealment"},
    {"company": "Srei Equipment Finance",   "symbol": "SREI",    "year": 2021, "sector": "NBFC",           "industry": "Equipment Finance",     "fraud_type": "Diversion of Funds"},
    {"company": "BLS International",        "symbol": "BLS",     "year": 2020, "sector": "IT Services",    "industry": "E-governance Services", "fraud_type": "Accounting Fraud"},
    {"company": "Kwality",                  "symbol": "KWALITY", "year": 2018, "sector": "FMCG",           "industry": "Dairy Products",        "fraud_type": "Accounting Fraud"},
]


# ---------------------------------------------------------------------------
# Gemini Prompt
# ---------------------------------------------------------------------------
def build_prompt(company: str, year: int, sector: str, industry: str, fraud_type: str) -> str:
    """Build the Gemini prompt to generate structured fraud case data."""

    is_bank_sector = sector.lower() in ("banking", "nbfc", "financial services")

    if is_bank_sector:
        # For banks/NBFCs: use ONLY the new banking flag block (101-132) + promoter flags (22-24)
        bank_flag_numbers = list(range(101, 133)) + [22, 23, 24]
        relevant_flags = {k: v for k, v in FLAG_REGISTRY.items() if k in bank_flag_numbers}
        sector_note = (
            "IMPORTANT: This is a BANK/NBFC company. Use ONLY the bank-specific flags "
            "(flag_numbers 101-132) plus promoter flags (22, 23, 24). "
            "Do NOT use non-bank flags (2-60)."
        )
    else:
        # Non-bank: use all non-bank flags (everything below 101)
        relevant_flags = {k: v for k, v in FLAG_REGISTRY.items() if k < 101}
        sector_note = (
            "This is a NON-BANK company. Use ONLY non-bank flags (flag_numbers 2-60). "
            "Do NOT use bank-specific flags (101-132)."
        )

    # Build flag registry as JSON for Gemini to reference
    flag_list = "\n".join([
        f'  {num}: {{ "flag_name": "{v["flag_name"]}", "category": "{v["category"]}", "severity": "{v["severity"]}" }}'
        for num, v in relevant_flags.items()
    ])

    return f"""You are an expert Indian forensic financial analyst with deep knowledge of Indian corporate fraud cases.

Generate a comprehensive and ACCURATE structured analysis for this well-documented Indian corporate fraud case:
- Company: {company}
- Year of fraud exposure: {year}
- Sector: {sector}
- Industry: {industry}
- Fraud Type: {fraud_type}

CRITICAL REQUIREMENTS:
1. Use ONLY real, publicly documented facts about this company's fraud. Do not fabricate.
2. Red flags MUST use flag_numbers from the registry below. Pick ALL flags that were actually present (typically 8-15 for major frauds).
3. All financial figures must be realistic and close to actual reported values.
4. Timeline must reflect real chronological events for this case.
5. Return ONLY valid JSON. No markdown, no ```json, no explanation text.
6. {sector_note}

FLAG REGISTRY (use ONLY these flag_numbers for this sector):
{flag_list}

Return this EXACT JSON structure:
{{
  "company_name": "Full official company name",
  "year": {year},
  "sector": "{sector}",
  "industry": "{industry}",
  "fraud_type": "{fraud_type}",
  "detection_difficulty": "Easy|Medium|Hard",
  "stock_decline_percent": <realistic negative number e.g. -97.4>,
  "market_cap_lost_cr": <realistic number in crores e.g. 14000>,
  "outcome": "2-3 sentence description of what happened after the fraud was exposed",
  "regulatory_action": "What SEBI/CBI/ED/RBI/NCLT did in response",
  "primary_flags": ["Top flag name 1", "Top flag name 2", "Top flag name 3"],
  "red_flags_detected": [
    {{
      "flag_number": <from registry>,
      "flag_name": "<exact name from registry>",
      "category": "<exact category from registry>",
      "severity": "<exact severity from registry>",
      "triggered": true,
      "confidence": <70-100>,
      "evidence": "Specific factual evidence of this flag in this company (1-2 sentences max)"
    }}
  ],
  "timeline": [
    {{ "date": "YYYY or Month YYYY", "event": "What happened", "type": "normal|red_flag|investigation|collapse" }}
  ],
  "what_investors_missed": [
    "Specific warning sign investors ignored 1",
    "Specific warning sign investors ignored 2",
    "Specific warning sign investors ignored 3"
  ],
  "lessons_learned": [
    "Actionable lesson for investors 1",
    "Actionable lesson for investors 2",
    "Actionable lesson for investors 3"
  ]
}}

STRICT LENGTH LIMITS (to avoid JSON truncation — keep each string SHORT):
- red_flags_detected: 8-15 entries (include ALL genuinely triggered flags), evidence max 100 chars each
- timeline: exactly 5-6 events, event text max 80 chars each
- what_investors_missed: exactly 3 items, max 100 chars each
- lessons_learned: exactly 3 items, max 100 chars each
- outcome: max 200 chars
- regulatory_action: max 200 chars
"""


# ---------------------------------------------------------------------------
# Generate and save one fraud case
# ---------------------------------------------------------------------------
def generate_fraud_case(db, company_info: dict, skip_existing: bool = True) -> bool:
    """Generate one fraud case via Gemini and save to DB. Returns True if saved."""

    company = company_info["company"]
    year = company_info["year"]
    sector = company_info["sector"]
    industry = company_info["industry"]
    fraud_type = company_info["fraud_type"]

    # Create case_id
    case_id = f"{company.lower().replace(' ', '-').replace('(', '').replace(')', '').replace('&', 'and')[:50]}-{year}"

    # Check if exists
    if skip_existing:
        existing = db.query(FraudCase).filter(FraudCase.case_id == case_id).first()
        if existing:
            logger.info(f"⏭️  Skipping (exists): {company} ({year})")
            return False

    logger.info(f"🤖 Generating: {company} ({year}) ...")

    try:
        prompt = build_prompt(company, year, sector, industry, fraud_type)
        response = model.generate_content(
            prompt,
            generation_config=genai.types.GenerationConfig(
                temperature=0.3,       # Low temp for factual accuracy
                max_output_tokens=8192,  # gemini-2.5-pro needs more tokens for detailed JSON
            )
        )

        raw_text = response.text.strip()

        # Strip markdown code fences if present
        if raw_text.startswith("```"):
            raw_text = raw_text.split("```")[1]
            if raw_text.startswith("json"):
                raw_text = raw_text[4:]
            raw_text = raw_text.strip()

        data = json.loads(raw_text)

        # Validate required fields
        required = ["company_name", "year", "red_flags_detected", "stock_decline_percent", "market_cap_lost_cr"]
        for field in required:
            if field not in data:
                logger.error(f"❌ Missing required field '{field}' in Gemini response for {company}")
                return False

        # Validate and normalise red_flags_detected against registry
        validated_flags = []
        for flag in data.get("red_flags_detected", []):
            flag_num = flag.get("flag_number")
            if flag_num in FLAG_REGISTRY:
                registry_entry = FLAG_REGISTRY[flag_num]
                validated_flags.append({
                    "flag_number": flag_num,
                    "flag_name": registry_entry["flag_name"],  # Use canonical name
                    "category": registry_entry["category"],    # Use canonical category
                    "severity": registry_entry["severity"],    # Use canonical severity
                    "triggered": True,
                    "confidence": flag.get("confidence", 85),
                    "evidence": flag.get("evidence", "Documented in public records")
                })
            else:
                logger.warning(f"  ⚠️  Unknown flag_number {flag_num} for {company} — skipping")

        if not validated_flags:
            logger.error(f"❌ No valid flags generated for {company}")
            return False

        # Build primary_flags from top 3 triggered flags by severity
        severity_order = {"CRITICAL": 0, "HIGH": 1, "MEDIUM": 2, "LOW": 3}
        sorted_flags = sorted(validated_flags, key=lambda f: severity_order.get(f["severity"], 4))
        primary_flags = data.get("primary_flags") or [f["flag_name"] for f in sorted_flags[:3]]

        # Create FraudCase object
        fraud_case = FraudCase(
            case_id=case_id,
            company_name=data["company_name"],
            year=data["year"],
            sector=data.get("sector", sector),
            industry=data.get("industry", industry),
            fraud_type=data.get("fraud_type", fraud_type),
            detection_difficulty=data.get("detection_difficulty", "Medium"),
            stock_decline_percent=float(data["stock_decline_percent"]),
            market_cap_lost_cr=float(data["market_cap_lost_cr"]),
            primary_flags=primary_flags[:5],  # Max 5 primary flags
            red_flags_detected=validated_flags,
            timeline=data.get("timeline", []),
            what_investors_missed=data.get("what_investors_missed", []),
            lessons_learned=data.get("lessons_learned", []),
            outcome=data.get("outcome", ""),
            regulatory_action=data.get("regulatory_action", ""),
            pdf_url=None,  # No PDF needed for AI-generated cases
        )

        db.add(fraud_case)
        db.commit()

        logger.info(f"  ✅ Saved: {fraud_case.company_name} | Flags: {len(validated_flags)} | Stock decline: {fraud_case.stock_decline_percent}%")
        return True

    except json.JSONDecodeError as e:
        logger.error(f"❌ JSON parse error for {company}: {e}")
        logger.debug(f"Raw response: {raw_text[:500]}")
        db.rollback()
        return False
    except Exception as e:
        logger.error(f"❌ Failed to generate {company}: {e}")
        db.rollback()
        return False


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------
def main():
    parser = argparse.ArgumentParser(
        description='Seed fraud cases database using Gemini AI',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Seed all 50 cases (skip existing)
  python scripts/seed_fraud_cases.py

  # Test with first 5 cases only
  python scripts/seed_fraud_cases.py --limit 5

  # Clear all existing cases and re-seed
  python scripts/seed_fraud_cases.py --clear-all

  # Force re-generate even if case exists
  python scripts/seed_fraud_cases.py --no-skip-existing
        """
    )
    parser.add_argument('--limit',          type=int, default=None, help='Only process first N companies (for testing)')
    parser.add_argument('--clear-all',      action='store_true',    help='Delete ALL existing fraud cases before seeding')
    parser.add_argument('--no-skip-existing', action='store_true',  help='Re-generate even if case already exists in DB')
    parser.add_argument('--delay',          type=float, default=2.0, help='Seconds to wait between Gemini API calls (default: 2)')
    args = parser.parse_args()

    db = SessionLocal()

    try:
        # Optionally clear all existing cases
        if args.clear_all:
            count = db.query(FraudCase).count()
            logger.warning(f"⚠️  Deleting {count} existing fraud cases...")
            db.query(FraudCase).delete()
            db.commit()
            logger.info("✅ All fraud cases deleted")

        companies = FRAUD_COMPANIES
        if args.limit:
            companies = companies[:args.limit]
            logger.info(f"📋 Processing {len(companies)} of {len(FRAUD_COMPANIES)} companies (--limit {args.limit})")
        else:
            logger.info(f"📋 Processing all {len(companies)} companies")

        skip_existing = not args.no_skip_existing

        saved = 0
        skipped = 0
        failed = 0

        for i, company_info in enumerate(companies, 1):
            logger.info(f"\n[{i}/{len(companies)}] {company_info['company']} ({company_info['year']})")

            success = generate_fraud_case(db, company_info, skip_existing=skip_existing)
            if success:
                saved += 1
            elif not skip_existing:
                failed += 1
            else:
                skipped += 1

            # Rate limit: wait between API calls to avoid quota issues
            if i < len(companies):
                time.sleep(args.delay)

        # Final summary
        print("\n" + "=" * 60)
        print("✅ SEEDING COMPLETE!")
        print("=" * 60)
        print(f"  ✅ Saved:   {saved} fraud cases")
        print(f"  ⏭️  Skipped: {skipped} (already existed)")
        print(f"  ❌ Failed:  {failed}")
        total = db.query(FraudCase).count()
        print(f"  📊 Total in DB: {total} fraud cases")
        print("=" * 60)

    except KeyboardInterrupt:
        logger.warning("\n⚠️  Interrupted by user")
        total = db.query(FraudCase).count()
        print(f"\n📊 Total in DB so far: {total} fraud cases")
    finally:
        db.close()


if __name__ == '__main__':
    main()
