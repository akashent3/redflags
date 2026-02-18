"""Gemini prompt analyzer for PDF-based red flags. Non-banks: 22 flags, Banks: 24 flags."""

import google.generativeai as genai
import json
import logging
import os
import re
from typing import Dict, List

logger = logging.getLogger(__name__)

# The single comprehensive prompt for Gemini to analyze the annual report PDF
ANALYSIS_PROMPT = """You are an expert Indian financial analyst specializing in forensic accounting and red flag detection. You are analyzing an annual report PDF of an Indian listed company.

**CRITICAL INSTRUCTION - CONSOLIDATED vs STANDALONE:**
- You MUST look for CONSOLIDATED financial statements FIRST.
- ONLY if the annual report does NOT contain consolidated statements (i.e., it is a standalone-only company with no subsidiaries), then use standalone statements.
- If both consolidated and standalone are present, STRICTLY use ONLY consolidated figures.
- State clearly at the top which type you used: "consolidated" or "standalone".

Analyze this annual report and check for ALL 22 red flags listed below. For each flag, provide:
1. "triggered": true/false
2. "confidence": 0-100 (how confident you are)
3. "evidence": specific text/numbers from the report supporting your finding
4. "details": any additional context

**CRITICAL JSON FORMATTING RULES:**
- Return ONLY a valid JSON object. No markdown, no ```json blocks, no text before or after.
- In ALL string values, NEVER use double quotes. Use single quotes (') instead when quoting text from the report.
- Example: "evidence": "The auditor states 'there has been no resignation' on page 344"
- Keep evidence VERY short (under 100 characters). Just state the finding. Example: 'No auditor resignation found (page 344)' or 'Qualified opinion issued on inventory valuation (page 89)'.
- Keep details field VERY short (under 80 characters) or empty string.
- This is essential to avoid JSON parsing errors.

Return your response as a valid JSON object with the exact structure shown below.

{
  "statement_type_used": "consolidated" or "standalone",
  "analysis_year": "FY ending year e.g. 2024",
  "flags": {
    "qualified_opinion": {
      "flag_number": 2,
      "flag_name": "Qualified/Adverse/Disclaimer Opinion",
      "category": "Auditor",
      "severity": "CRITICAL",
      "rule": "Auditor issued a qualified, adverse, or disclaimer opinion instead of unmodified/clean opinion",
      "triggered": false,
      "confidence": 0,
      "evidence": "explanation",
      "details": ""
    },
    "emphasis_of_matter": {
      "flag_number": 3,
      "flag_name": "Emphasis of Matter",
      "category": "Auditor",
      "severity": "MEDIUM",
      "rule": "Auditor included Emphasis of Matter paragraph highlighting concerns",
      "triggered": false,
      "confidence": 0,
      "evidence": "explanation",
      "details": ""
    },
    "going_concern": {
      "flag_number": 4,
      "flag_name": "Going Concern Doubt",
      "category": "Auditor",
      "severity": "CRITICAL",
      "rule": "Auditor or notes mention material uncertainty about ability to continue as going concern",
      "triggered": false,
      "confidence": 0,
      "evidence": "explanation",
      "details": ""
    },
    "audit_fees": {
      "flag_number": 6,
      "flag_name": "Audit Fees Unusual",
      "category": "Auditor",
      "severity": "MEDIUM",
      "rule": "Audit fees unusually HIGH (>0.5% of revenue) or non-audit fees exceed audit fees",
      "triggered": false,
      "confidence": 0,
      "evidence": "explanation",
      "details": ""
    },
    "rpt_high": {
      "flag_number": 15,
      "flag_name": "RPT > 10% Revenue",
      "category": "Related Party",
      "severity": "HIGH",
      "rule": "Total related party transactions exceed 10% of revenue from operations",
      "triggered": false,
      "confidence": 0,
      "evidence": "explanation",
      "details": ""
    },
    "loans_to_rp": {
      "flag_number": 16,
      "flag_name": "Loans to Related Parties",
      "category": "Related Party",
      "severity": "HIGH",
      "rule": "Loans/advances to related parties exceed 5% of revenue OR 5% of net profit (PAT)",
      "triggered": false,
      "confidence": 0,
      "evidence": "explanation",
      "details": ""
    },
    "rp_premium": {
      "flag_number": 17,
      "flag_name": "RP Premium/Non-Arms Length Transactions",
      "category": "Related Party",
      "severity": "HIGH",
      "rule": "Transactions with related parties at prices different from market/arms length",
      "triggered": false,
      "confidence": 0,
      "evidence": "explanation",
      "details": ""
    },
    "rpt_revenue_increasing": {
      "flag_number": 18,
      "flag_name": "RPT Revenue Increasing",
      "category": "Related Party",
      "severity": "MEDIUM",
      "rule": "Revenue from related parties increasing as proportion of total revenue YoY",
      "triggered": false,
      "confidence": 0,
      "evidence": "explanation",
      "details": ""
    },
    "loans_to_directors": {
      "flag_number": 20,
      "flag_name": "Loans to Directors",
      "category": "Related Party",
      "severity": "CRITICAL",
      "rule": "Any loans or advances given to directors, KMP, or their relatives (Sec 185/186)",
      "triggered": false,
      "confidence": 0,
      "evidence": "explanation",
      "details": ""
    },
    "disproportionate_salary": {
      "flag_number": 25,
      "flag_name": "Disproportionate Director Salary",
      "category": "Promoter",
      "severity": "MEDIUM",
      "rule": "Director remuneration >10% of net profit or increased despite declining profits",
      "triggered": false,
      "confidence": 0,
      "evidence": "explanation",
      "details": ""
    },
    "icds": {
      "flag_number": 27,
      "flag_name": "Inter-Corporate Deposits",
      "category": "Promoter",
      "severity": "HIGH",
      "rule": "Material inter-corporate deposits or loans given to group/associate companies",
      "triggered": false,
      "confidence": 0,
      "evidence": "explanation",
      "details": ""
    },
    "audit_committee": {
      "flag_number": 29,
      "flag_name": "Audit Committee Issues",
      "category": "Governance",
      "severity": "MEDIUM",
      "rule": "Audit committee has <3 members, <2/3 independent, no financial expert, or <4 meetings/year",
      "triggered": false,
      "confidence": 0,
      "evidence": "explanation",
      "details": ""
    },
    "sebi_penalties": {
      "flag_number": 30,
      "flag_name": "SEBI/Legal Penalties",
      "category": "Governance",
      "severity": "HIGH",
      "rule": "SEBI orders, show cause notices, penalties, or regulatory non-compliance reported",
      "triggered": false,
      "confidence": 0,
      "evidence": "explanation",
      "details": ""
    },
    "whistleblower": {
      "flag_number": 31,
      "flag_name": "Whistleblower Complaints",
      "category": "Governance",
      "severity": "CRITICAL",
      "rule": "Whistleblower/vigil mechanism complaints received, or fraud reported under Sec 143(12)",
      "triggered": false,
      "confidence": 0,
      "evidence": "explanation",
      "details": ""
    },
    "contingent_liabilities": {
      "flag_number": 35,
      "flag_name": "Contingent Liabilities High",
      "category": "Balance Sheet",
      "severity": "HIGH",
      "rule": "Contingent liabilities (tax demands, legal cases, guarantees) exceed 20% of net worth",
      "triggered": false,
      "confidence": 0,
      "evidence": "explanation",
      "details": ""
    },
    "debt_restructuring": {
      "flag_number": 36,
      "flag_name": "Debt Restructuring",
      "category": "Balance Sheet",
      "severity": "CRITICAL",
      "rule": "Any sign of debt restructuring, OTS, CDR, moratorium, or change in repayment terms",
      "triggered": false,
      "confidence": 0,
      "evidence": "explanation",
      "details": ""
    },
    "asset_pledging": {
      "flag_number": 37,
      "flag_name": "Asset Pledging",
      "category": "Balance Sheet",
      "severity": "MEDIUM",
      "rule": "Significant assets (>30% of total) pledged as collateral for borrowings",
      "triggered": false,
      "confidence": 0,
      "evidence": "explanation",
      "details": ""
    },
    "bad_debt_provisioning": {
      "flag_number": 50,
      "flag_name": "Bad Debt Provisioning Increasing",
      "category": "Balance Sheet",
      "severity": "MEDIUM",
      "rule": "Provision for doubtful debts increased >50% YoY or increasing for 2+ consecutive years",
      "triggered": false,
      "confidence": 0,
      "evidence": "explanation",
      "details": ""
    },
    "revenue_policy_change": {
      "flag_number": 40,
      "flag_name": "Revenue Recognition Policy Change",
      "category": "Revenue",
      "severity": "HIGH",
      "rule": "Change in revenue recognition accounting policy during the year",
      "triggered": false,
      "confidence": 0,
      "evidence": "explanation",
      "details": ""
    },
    "unbilled_revenue": {
      "flag_number": 41,
      "flag_name": "Unbilled Revenue High",
      "category": "Revenue",
      "severity": "MEDIUM",
      "rule": "Unbilled revenue or contract assets exceed 10% of total revenue and growing",
      "triggered": false,
      "confidence": 0,
      "evidence": "explanation",
      "details": ""
    },
    "mda_tone": {
      "flag_number": 42,
      "flag_name": "MD&A Tone Defensive",
      "category": "Textual",
      "severity": "MEDIUM",
      "rule": "MD&A uses excessive blame on external factors, avoids specifics, or is evasive about problems",
      "triggered": false,
      "confidence": 0,
      "evidence": "explanation",
      "details": ""
    },
    "jv_associate_losses": {
      "flag_number": 51,
      "flag_name": "JV/Associate Loss Hiding",
      "category": "Related Party",
      "severity": "MEDIUM",
      "rule": "Persistent losses in JVs/associates for 2+ years or significant investment write-downs",
      "triggered": false,
      "confidence": 0,
      "evidence": "explanation",
      "details": ""
    }
  }
}

**DETAILED CHECKING INSTRUCTIONS FOR EACH FLAG:**

**FLAG 2 - Qualified/Adverse/Disclaimer Opinion:**
- Read the Independent Auditor's Report carefully
- Look for the exact words: "Qualified Opinion", "Adverse Opinion", "Disclaimer of Opinion"
- An "Unmodified Opinion" or "Clean Opinion" means this flag is NOT triggered
- "Except for" language in the opinion paragraph indicates qualification

**FLAG 3 - Emphasis of Matter (EOM):**
- Check ONLY for "Emphasis of Matter" paragraphs in the auditor's report
- DO NOT consider "Other Matter" paragraphs - ONLY "Emphasis of Matter"
- These highlight important issues without qualifying the opinion
- Look for references to contingencies, going concern, litigation, regulatory issues
- Multiple EOM paragraphs increase severity
- Note: "Other Matter" sections should be IGNORED for this flag

**FLAG 4 - Going Concern Doubt:**
- Search for "going concern", "material uncertainty", "ability to continue as a going concern"
- Check both auditor's report and notes to financial statements
- Also check for "accumulated losses exceed net worth" or similar language

**FLAG 6 - Audit Fees Unusual:**
- Find statutory audit fees in the notes (usually under "Payments to Auditors" or similar)
- Calculate: (Audit Fees / Revenue) * 100 to get percentage
- Compare audit fees to company revenue - unusually HIGH fees (>0.5% of revenue) may indicate complex audit or concerns
- Flag if audit fees exceed 0.5% of total revenue from operations
- Also check for high non-audit fees relative to audit fees (independence concern - flag if non-audit fees > audit fees)
- Example: If revenue is ₹1,000 crore and audit fees are ₹6 crore, that's 0.6% → FLAG IT
- Example: If revenue is ₹1,000 crore and audit fees are ₹4 crore, that's 0.4% → DO NOT FLAG

**FLAG 15 - RPT > 10% Revenue:**
- Find the Related Party Transactions disclosure (Note/Schedule)
- Sum all transaction values with related parties
- Compare total RPT to total revenue from operations
- Flag if RPT exceeds 10% of revenue

**FLAG 16 - Loans to Related Parties:**
- In the RPT note, look for: loans given, advances, deposits with related parties
- Check for outstanding balances at year end
- Calculate if loans/advances to related parties exceed 5% of revenue from operations OR 5% of profit after tax (PAT)
- Use the actual numbers from the related party transaction table
- Flag if either threshold is breached

**FLAG 17 - RP Premium/Non-Arms Length Transactions:**
- Look for language about "arm's length" pricing in RPT disclosures
- Check if any transactions are noted as being at rates different from market
- Look for "at cost", "below market", "at a premium" in RPT descriptions
- Board/audit committee observations on RPT pricing

**FLAG 18 - RPT Revenue Increasing:**
- Compare current year RPT revenue with previous year (if disclosed)
- Check if the proportion of revenue from related parties is increasing
- Growing dependence on group companies for revenue is a concern

**FLAG 20 - Loans to Directors:**
- Specifically search for loans/advances to directors, KMP, or their relatives
- Check Section 185/186 of Companies Act compliance disclosures
- Any loan to a director is a serious red flag under Indian law
- Strictly check for loans given only not any other instruments.

**FLAG 25 - Disproportionate Director Salary:**
- Find director/KMP remuneration details (in Corporate Governance Report or Notes)
- Compare total director remuneration to company's net profit
- If director pay > 10% of net profit or increased despite declining profits, flag it
- Check for commission, stock options, and perquisites separately

**FLAG 27 - Inter-Corporate Deposits (ICDs):**
- Search for "inter-corporate deposits", "ICDs", "inter corporate loans"
- Check loans and advances given to group/associate companies
- Material ICDs to related or group companies are a significant red flag
- Check the interest rate and repayment terms

**FLAG 29 - Audit Committee Issues:**
- Check audit committee composition - needs minimum 3 members, 2/3 independent
- Look for frequent changes in audit committee membership
- Check if the audit committee chairperson is a financial expert
- Review number of audit committee meetings held (minimum 4 per year)

**FLAG 30 - SEBI/Legal Penalties:**
- Search for SEBI orders, show cause notices, penalties
- Check for "non-compliance" with listing regulations
- Look in legal proceedings/contingent liabilities for regulatory actions
- Check if the company or its directors face any SEBI/RoC/NCLT proceedings

**FLAG 31 - Whistleblower Complaints:**
- Check the whistleblower/vigil mechanism section
- Look for mentions of complaints received, investigated, or pending
- Also search for fraud reported by auditors under Section 143(12)
- Any substantiated whistleblower complaint is a critical red flag

**FLAG 35 - Contingent Liabilities High:**
- Find contingent liabilities note in the financial statements
- Sum all contingent liabilities (tax demands, legal cases, guarantees, etc.)
- Compare to net worth/total equity
- Flag if contingent liabilities > 20% of net worth

**FLAG 36 - Debt Restructuring:**
- Search for "restructuring", "one-time settlement", "OTS", "CDR", "SDR"
- Check for "change in repayment terms", "moratorium", "standstill"
- Look for RBI circulars or NCLT references related to debt
- Any debt restructuring is a critical concern

**FLAG 37 - Asset Pledging:**
- Look for "charge created", "assets pledged", "security offered"
- Check the borrowing notes for details of assets pledged as collateral
- Flag if significant portion of assets (>30%) are pledged
- Compare pledged assets to total assets

**FLAG 50 - Bad Debt Provisioning Increasing:**
- Check Notes to Accounts for provision for doubtful debts / expected credit losses
- Look for allowance for bad and doubtful debts, write-offs
- Flag if provisions increased >50% YoY or have been increasing for 2+ consecutive years
- Increasing bad debt provisions suggest deteriorating receivables quality

**FLAG 40 - Revenue Recognition Policy Change:**
- Check accounting policies section for changes in revenue recognition
- Look for "change in accounting policy", "restatement", "Ind AS 115 transition"
- Recent changes to revenue recognition methods are a concern
- Check if the change increased reported revenue

**FLAG 41 - Unbilled Revenue High:**
- Search for "unbilled revenue", "contract assets", "accrued revenue"
- Especially relevant for IT, construction, and project-based companies
- Compare unbilled revenue to total revenue
- Flag if unbilled revenue > 10% of total revenue and growing

**FLAG 42 - MD&A Tone Defensive:**
- Read the Management Discussion & Analysis (MD&A) section
- Look for: excessive blame on external factors, vague future promises without specifics
- Check for: absence of quantitative targets, excessive use of "challenging", "headwinds"
- Flag if management avoids discussing specific problems or uses overly defensive language
- Compare management commentary with actual financial performance

**FLAG 51 - JV/Associate Loss Hiding:**
- Check for investments in joint ventures and associates in the Notes
- Look for share of profit/loss from associates and JVs in the P&L
- Flag if: (a) JVs/associates have reported losses for 2+ consecutive years, (b) significant impairment/write-down of JV/associate investments, or (c) company's share of JV/associate losses exceeds 5% of PAT
- Persistent losses in JVs/associates suggest potential loss-parking in off-balance-sheet entities

Remember: Return ONLY the JSON object, no other text. Be precise and cite specific page numbers, amounts, or quotes from the report where possible.
"""

# Bank/NBFC/Financial Services prompt — COMPLETE REVAMP.
# 17 Gemini-analyzed flags for banks (B16-B32), flag_numbers 116-132.
# ONLY these 17 flags are shown for banks from Gemini analysis.
# No non-bank flags (#2-#51) are included here — banks get their own complete set.
ANALYSIS_PROMPT_BANK = """You are an expert Indian financial analyst specializing in forensic accounting and red flag detection for **banks, NBFCs, and financial services companies**. You are analyzing an annual report PDF.

**CRITICAL INSTRUCTION - CONSOLIDATED vs STANDALONE:**
- You MUST look for CONSOLIDATED financial statements FIRST.
- ONLY if the annual report does NOT contain consolidated statements (i.e., it is a standalone-only entity with no subsidiaries), then use standalone statements.
- If both consolidated and standalone are present, STRICTLY use ONLY consolidated figures.
- State clearly at the top which type you used: "consolidated" or "standalone".

Analyze this annual report and check for ALL 17 red flags listed below. These are BANK/NBFC-specific flags only. For each flag, provide:
1. "triggered": true/false
2. "confidence": 0-100 (how confident you are)
3. "evidence": specific text/numbers from the report supporting your finding
4. "details": any additional context

**CRITICAL JSON FORMATTING RULES:**
- Return ONLY a valid JSON object. No markdown, no ```json blocks, no text before or after.
- In ALL string values, NEVER use double quotes. Use single quotes (') instead when quoting text from the report.
- Example: "evidence": "The auditor states 'there has been no resignation' on page 344"
- Keep evidence VERY short (under 100 characters). Just state the finding.
- Keep details field VERY short (under 80 characters) or empty string.
- This is essential to avoid JSON parsing errors.

Return your response as a valid JSON object with the exact structure shown below.

{
  "statement_type_used": "consolidated" or "standalone",
  "analysis_year": "FY ending year e.g. 2024",
  "flags": {
    "npa_divergence": {
      "flag_number": 116,
      "flag_name": "NPA Divergence",
      "category": "Balance Sheet",
      "severity": "CRITICAL",
      "rule": "Any non-zero divergence between bank-declared NPAs and RBI-assessed NPAs reported in annual report",
      "triggered": false,
      "confidence": 0,
      "evidence": "explanation",
      "details": ""
    },
    "slippage_ratio": {
      "flag_number": 117,
      "flag_name": "Slippage Ratio",
      "category": "Balance Sheet",
      "severity": "HIGH",
      "rule": "Year-over-year rising trend in slippage ratio (fresh NPA additions / opening gross advances). Rising trend e.g. 1.5% to 3% indicates failing underwriting.",
      "triggered": false,
      "confidence": 0,
      "evidence": "explanation",
      "details": ""
    },
    "writeoff_dependency": {
      "flag_number": 118,
      "flag_name": "Write-off Dependency",
      "category": "Balance Sheet",
      "severity": "HIGH",
      "rule": "Write-offs exceed 25% of opening Gross NPA. Formula: (Amounts Written Off / Opening Gross NPA) * 100 > 25%. Indicates hiding bad loans by destroying value.",
      "triggered": false,
      "confidence": 0,
      "evidence": "explanation",
      "details": ""
    },
    "sma2_book": {
      "flag_number": 119,
      "flag_name": "Watchlist / SMA-2 Book",
      "category": "Balance Sheet",
      "severity": "HIGH",
      "rule": "SMA-2 accounts (overdue 61-90 days) represent more than 2% of Total Advances. This is the imminent NPA pipeline.",
      "triggered": false,
      "confidence": 0,
      "evidence": "explanation",
      "details": ""
    },
    "restructured_book": {
      "flag_number": 120,
      "flag_name": "Restructured Book Size",
      "category": "Balance Sheet",
      "severity": "HIGH",
      "rule": "Restructured advances exceed 2% of Total Advances. These are often non-viable businesses kept on life support.",
      "triggered": false,
      "confidence": 0,
      "evidence": "explanation",
      "details": ""
    },
    "security_receipts": {
      "flag_number": 121,
      "flag_name": "Security Receipts (SR) Buildup",
      "category": "Balance Sheet",
      "severity": "HIGH",
      "rule": "High or growing Security Receipts (SRs) balance from ARC sales — bad loans sold on paper but no actual cash recovery.",
      "triggered": false,
      "confidence": 0,
      "evidence": "explanation",
      "details": ""
    },
    "evergreening_proxy": {
      "flag_number": 122,
      "flag_name": "Evergreening Proxy",
      "category": "Balance Sheet",
      "severity": "CRITICAL",
      "rule": "Sudden conversion of Term Loans into Cash Credit/Overdraft accounts to prevent NPA classification (evergreening signal).",
      "triggered": false,
      "confidence": 0,
      "evidence": "explanation",
      "details": ""
    },
    "alm_mismatch": {
      "flag_number": 123,
      "flag_name": "ALM Mismatch",
      "category": "Cash Flow",
      "severity": "HIGH",
      "rule": "Liabilities exceed assets in the 1-14 day and 15-28 day maturity buckets (negative mismatch) — indicates imminent liquidity stress.",
      "triggered": false,
      "confidence": 0,
      "evidence": "explanation",
      "details": ""
    },
    "bulk_deposit_dependence": {
      "flag_number": 124,
      "flag_name": "Bulk Deposit Dependence",
      "category": "Cash Flow",
      "severity": "MEDIUM",
      "rule": "(Inter-bank + Corporate/Bulk Deposits) / Total Deposits > 30-40%. High reliance on hot money that will vanish during a crisis.",
      "triggered": false,
      "confidence": 0,
      "evidence": "explanation",
      "details": ""
    },
    "casa_erosion": {
      "flag_number": 125,
      "flag_name": "CASA Ratio Erosion",
      "category": "Cash Flow",
      "severity": "MEDIUM",
      "rule": "CASA ratio declining YoY by >300bps OR below 30%. Losing cheap funds and paying expensive debt.",
      "triggered": false,
      "confidence": 0,
      "evidence": "explanation",
      "details": ""
    },
    "contingent_liability_overload": {
      "flag_number": 126,
      "flag_name": "Contingent Liability Overload",
      "category": "Balance Sheet",
      "severity": "HIGH",
      "rule": "Guarantees given and Letters of Credit exceed 5x Net Worth (capital + reserves). Off-balance-sheet guarantees that if invoked can wipe out the bank.",
      "triggered": false,
      "confidence": 0,
      "evidence": "explanation",
      "details": ""
    },
    "dta_bloat": {
      "flag_number": 127,
      "flag_name": "Deferred Tax Asset (DTA) Bloat",
      "category": "Balance Sheet",
      "severity": "MEDIUM",
      "rule": "Rapid creation of Deferred Tax Assets (DTA) — artificially boosts Book Value based only on hope of future profits.",
      "triggered": false,
      "confidence": 0,
      "evidence": "explanation",
      "details": ""
    },
    "related_party_transactions": {
      "flag_number": 128,
      "flag_name": "Related Party Transactions",
      "category": "Related Party",
      "severity": "HIGH",
      "rule": "High volume or value of loans, investments, or service fees to director-owned or non-subsidiary related party entities (siphoning risk).",
      "triggered": false,
      "confidence": 0,
      "evidence": "explanation",
      "details": ""
    },
    "auditor_remuneration_skew": {
      "flag_number": 129,
      "flag_name": "Auditor Remuneration Skew",
      "category": "Auditor",
      "severity": "MEDIUM",
      "rule": "Non-audit service fees exceed statutory audit fees. High ratio means auditors earn more from consulting than auditing — independence compromised.",
      "triggered": false,
      "confidence": 0,
      "evidence": "explanation",
      "details": ""
    },
    "top20_borrower_exposure": {
      "flag_number": 130,
      "flag_name": "Top 20 Borrowers Exposure",
      "category": "Balance Sheet",
      "severity": "HIGH",
      "rule": "Top 20 borrowers represent more than 15-20% of Total Advances. High concentration risk — default of a few can destabilize the bank.",
      "triggered": false,
      "confidence": 0,
      "evidence": "explanation",
      "details": ""
    },
    "sectoral_concentration": {
      "flag_number": 131,
      "flag_name": "Sectoral Concentration",
      "category": "Balance Sheet",
      "severity": "MEDIUM",
      "rule": "Exposure to a single high-risk sector (Real Estate, Aviation, Infra) exceeds 20% of total advances.",
      "triggered": false,
      "confidence": 0,
      "evidence": "explanation",
      "details": ""
    },
    "auditor_qualifications": {
      "flag_number": 132,
      "flag_name": "Auditor Qualifications",
      "category": "Auditor",
      "severity": "CRITICAL",
      "rule": "Any Qualified Opinion, Adverse Opinion, Emphasis of Matter, or Material Uncertainty regarding going concern in the Independent Auditor's Report.",
      "triggered": false,
      "confidence": 0,
      "evidence": "explanation",
      "details": ""
    }
  }
}

**DETAILED CHECKING INSTRUCTIONS FOR EACH FLAG:**

**FLAG B16 (116) - NPA Divergence:**
- Search specifically for the section titled "Divergence in Asset Classification and Provisioning" or similar
- Look for notes disclosing the RBI's risk-based supervision (RBS) assessment vs bank's own classification
- Any non-zero divergence figure means the regulator caught the bank hiding bad loans
- Also check for any RBI communication or annual inspection findings referenced in the report
- A divergence of even ₹1 in NPA recognition is a red flag

**FLAG B17 (117) - Slippage Ratio:**
- Find the "Movement of NPAs" note or asset quality section
- Look for "Fresh additions to NPAs" or "Slippages" during the year
- Calculate: Fresh NPA additions / Opening Gross Advances
- A year-over-year rising trend (e.g., 1.5% → 2% → 3%) indicates failing underwriting standards
- Flag if slippage ratio is rising for 2+ consecutive years

**FLAG B18 (118) - Write-off Dependency:**
- Find the NPA movement schedule or "Movement of NPAs" note
- Look for "Amounts Written Off" or "Technical Write-offs" during the year
- Calculate: (Amounts Written Off / Opening Gross NPA) * 100
- Flag if this ratio exceeds 25%
- High write-offs vs NPAs means the bank is destroying value rather than recovering cash

**FLAG B19 (119) - Watchlist / SMA-2 Book:**
- Search for "SMA" (Special Mention Account) disclosures in Asset Quality section
- SMA-2 = accounts overdue 61-90 days (just before NPA classification)
- Flag if SMA-2 accounts > 2% of Total Advances
- This represents the imminent NPA pipeline and a leading indicator of future stress

**FLAG B20 (120) - Restructured Book Size:**
- Find "Restructured Assets" note or Schedule
- Look for total value of loans under any restructuring scheme
- Flag if restructured advances > 2% of Total Gross Advances
- Look for mentions of: MSME restructuring, COVID restructuring, Resolution Framework 1.0/2.0 carryovers

**FLAG B21 (121) - Security Receipts (SR) Buildup:**
- Check Schedule 8 (Investments) or equivalent for "Security Receipts" (SRs)
- SRs are issued by ARCs (Asset Reconstruction Companies) when banks sell NPAs
- A high or growing SR balance means bad loans were sold on paper but the bank retains the risk
- Flag if SR balance is significant (>1% of advances) or growing YoY

**FLAG B22 (122) - Evergreening Proxy:**
- Compare the composition of the advances book: Term Loans vs Cash Credit / Overdraft / Working Capital
- Look for sudden large increases in Cash Credit / Overdraft limits
- A sudden conversion of Term Loans into Cash Credit prevents NPA classification (evergreening)
- Also look for "fresh disbursements to stressed accounts" or RBI comments on evergreening
- This is a direct fraud indicator — flag with high confidence if found

**FLAG B23 (123) - ALM Mismatch:**
- Find the "Maturity Pattern of Assets and Liabilities" table (required under RBI guidelines)
- Check the 1-14 days and 15-28 days maturity buckets specifically
- Flag if Liabilities exceed Assets in these short-term buckets (Negative Mismatch)
- A negative mismatch in short buckets implies imminent liquidity stress

**FLAG B24 (124) - Bulk Deposit Dependence:**
- Find the "Concentration of Deposits" or deposit composition disclosure
- Look for: Inter-bank deposits, Corporate deposits, Bulk deposits (typically >₹2 crore)
- Calculate: (Inter-bank deposits + Corporate/Bulk deposits) / Total Deposits
- Flag if this ratio exceeds 30-40%
- High reliance on hot money that will disappear during a crisis

**FLAG B25 (125) - CASA Ratio Erosion:**
- Find CASA (Current Account + Savings Account) ratio in the report
- Usually in management commentary, key ratios table, or deposit breakdown
- Flag if CASA ratio declined by >300 basis points (3 percentage points) YoY
- Also flag if CASA ratio is below 30% (high dependence on costly term deposits)
- A declining CASA means rising cost of funds

**FLAG B26 (126) - Contingent Liability Overload:**
- Find Schedule 12 (Contingent Liabilities) or equivalent
- Sum up: Guarantees Given + Letters of Credit + other off-balance-sheet exposures
- Compare to Net Worth (Capital + Reserves)
- Flag if total off-balance-sheet guarantees + LCs exceed 5x Net Worth
- If these contingent liabilities are invoked, the bank is wiped out

**FLAG B27 (127) - Deferred Tax Asset (DTA) Bloat:**
- Check "Other Assets" section for Deferred Tax Assets (DTA)
- Track if DTA grew rapidly in the current year
- A sudden large DTA creation means the bank is booking future tax benefits on losses
- This artificially boosts Book Value — flag if DTA grew >50% YoY or is >5% of Net Worth

**FLAG B28 (128) - Related Party Transactions:**
- Find the Related Party Disclosures note
- Look for: loans given to director-related entities, investments in related parties, service fees paid to promoter companies
- Focus specifically on NON-SUBSIDIARY related parties (not consolidated subsidiaries)
- Flag if there are high-value transactions (>1% of advances or >5% of net profit) with non-subsidiary related parties
- This is a siphoning risk indicator

**FLAG B29 (129) - Auditor Remuneration Skew:**
- Find "Payments to Auditors" or "Statutory Auditor Remuneration" note
- Identify: (1) Statutory audit fees, (2) Tax audit fees, (3) Non-audit/consulting fees
- Calculate: Non-audit fees / Statutory audit fees ratio
- Flag if non-audit fees EXCEED statutory audit fees
- When auditors earn more from consulting than auditing, their independence is compromised

**FLAG B30 (130) - Top 20 Borrowers Exposure:**
- Find "Concentration of Advances" or "Top 20 Borrowers" disclosure (Basel III Pillar 3 or credit risk note)
- Check: Total advances to Top 20 borrowers / Total Gross Advances
- Flag if Top 20 borrowers represent >15-20% of Total Advances
- Also check if individual single-borrower limit breaches are disclosed

**FLAG B31 (131) - Sectoral Concentration:**
- Find sector-wise or industry-wise credit exposure breakdown
- Check exposure to volatile/high-risk sectors: Real Estate, Aviation, Infrastructure, Gems & Jewellery
- Flag if exposure to any single high-risk sector exceeds 20% of total advances
- Also look for RBI-mandated disclosures on sectors under stress

**FLAG B32 (132) - Auditor Qualifications:**
- Read the Independent Auditor's Report carefully from beginning to end
- Look for: "Qualified Opinion", "Adverse Opinion", "Disclaimer of Opinion"
- Also look for "Emphasis of Matter" paragraphs regarding: NPA classification, provisioning adequacy, going concern
- Any "Material Uncertainty" language about the bank's ability to continue operations
- An "Unmodified Opinion" with no Emphasis of Matter = NOT triggered
- Even a single Emphasis of Matter about asset quality or provisioning = TRIGGERED

Remember: Return ONLY the JSON object, no other text. Be precise and cite specific page numbers, amounts, or quotes from the report where possible.
"""


def _repair_json(json_str: str) -> str:
    """Attempt to repair common JSON issues from LLM output.
    Mainly fixes unescaped double quotes inside string values.
    """
    # Strategy: walk through character by character, track if we're inside a string
    result = []
    i = 0
    in_string = False
    escape_next = False

    while i < len(json_str):
        ch = json_str[i]

        if escape_next:
            result.append(ch)
            escape_next = False
            i += 1
            continue

        if ch == '\\' and in_string:
            result.append(ch)
            escape_next = True
            i += 1
            continue

        if ch == '"':
            if not in_string:
                # Opening a string
                in_string = True
                result.append(ch)
            else:
                # Could be closing the string or an unescaped inner quote
                # Look ahead to determine: if followed by , : } ] or whitespace+these, it's closing
                rest = json_str[i + 1:].lstrip()
                if not rest or rest[0] in ',:}]':
                    # This is the real closing quote
                    in_string = False
                    result.append(ch)
                else:
                    # Unescaped quote inside string - escape it
                    result.append("'")
            i += 1
            continue

        result.append(ch)
        i += 1

    return ''.join(result)


def _fix_truncated_json(json_str: str) -> str:
    """Fix truncated JSON by removing the last incomplete field and closing all open braces."""
    # First apply quote repair
    json_str = _repair_json(json_str)

    # Find the last successfully complete key-value pair
    # Look for the last complete "}" that closes a flag object
    last_complete = json_str.rfind('}')
    if last_complete == -1:
        return json_str

    # Try progressively trimming from the end to find valid JSON
    for i in range(last_complete, max(last_complete - 2000, 0), -1):
        if json_str[i] == '}':
            attempt = json_str[:i + 1]
            # Count open/close braces and brackets
            open_braces = attempt.count('{') - attempt.count('}')
            open_brackets = attempt.count('[') - attempt.count(']')
            # Close them
            attempt += '}' * open_braces + ']' * open_brackets
            try:
                json.loads(attempt)
                return attempt
            except json.JSONDecodeError:
                continue

    return json_str


def analyze_pdf_with_gemini(pdf_path: str, api_key: str = None, is_financial_sector: bool = False) -> Dict:
    """Analyze an annual report PDF using Gemini. Non-banks: 22 flags, Banks: 17 flags (B16-B32).

    Banks get a completely separate flag set (B16/116 through B32/132) — no non-bank flags.
    Non-banks continue using the original 22 flags (#2-#51).

    Args:
        pdf_path: Path to the annual report PDF file
        api_key: Gemini API key (or set GEMINI_API_KEY env var)
        is_financial_sector: If True, use bank-specific prompt (17 bank-only flags B16-B32)

    Returns:
        Dict with flag results from Gemini analysis
    """
    api_key = api_key or os.getenv("GEMINI_API_KEY")
    if not api_key:
        raise ValueError("Gemini API key required. Set GEMINI_API_KEY env var.")

    genai.configure(api_key=api_key)

    logger.info(f"Uploading PDF to Gemini: {pdf_path}")
    pdf_file = genai.upload_file(pdf_path, mime_type="application/pdf")
    logger.info(f"PDF uploaded successfully: {pdf_file.name}")

    model = genai.GenerativeModel("gemini-2.5-pro")

    prompt = ANALYSIS_PROMPT_BANK if is_financial_sector else ANALYSIS_PROMPT
    logger.info(f"Sending analysis request to Gemini ({'bank' if is_financial_sector else 'non-bank'} prompt)...")
    response = model.generate_content(
        [pdf_file, prompt],
        generation_config=genai.GenerationConfig(
            temperature=0.1,
            max_output_tokens=16384
        )     
    )

    # Parse the JSON response
    raw_text = response.text.strip()

    # Strip markdown code fences if present
    if raw_text.startswith("```"):
        raw_text = re.sub(r'^```(?:json)?\s*', '', raw_text)
        raw_text = re.sub(r'\s*```$', '', raw_text)

    # Try to extract JSON from the response
    json_match = re.search(r'\{[\s\S]*\}', raw_text)
    if not json_match:
        logger.error(f"No JSON found in Gemini response: {raw_text[:500]}")
        raise ValueError("Gemini did not return valid JSON")

    json_str = json_match.group()

    # Attempt 1: Direct parse
    result = None
    try:
        result = json.loads(json_str)
    except json.JSONDecodeError:
        pass

    # Attempt 2: Fix common issues - unescaped quotes inside string values
    if result is None:
        try:
            repaired = _repair_json(json_str)
            result = json.loads(repaired)
            logger.info("JSON repaired successfully after initial parse failure")
        except (json.JSONDecodeError, Exception):
            pass

    # Attempt 3: Truncated response - close all open braces/brackets
    if result is None:
        try:
            fixed = _fix_truncated_json(json_str)
            result = json.loads(fixed)
            logger.info("Truncated JSON fixed successfully")
        except (json.JSONDecodeError, Exception) as e3:
            logger.error(f"Failed to parse Gemini JSON after all attempts: {e3}\nRaw: {raw_text[:1500]}")
            raise ValueError(f"Invalid JSON from Gemini: {e3}")

    logger.info(f"Gemini analysis complete. Statement type: {result.get('statement_type_used', 'unknown')}")
    return result


def parse_gemini_flags(gemini_result: Dict) -> List[Dict]:
    """Convert Gemini's response into standardized flag format matching API flags."""
    flags_data = gemini_result.get("flags", {})
    parsed = []

    for key, flag_info in flags_data.items():
        parsed.append({
            "flag_number": flag_info.get("flag_number", 0),
            "flag_name": flag_info.get("flag_name", key),
            "category": flag_info.get("category", "Unknown"),
            "severity": flag_info.get("severity", "MEDIUM"),
            "source": "PDF/Gemini",
            "rule": flag_info.get("rule", ""),
            "triggered": flag_info.get("triggered", False),
            "confidence": flag_info.get("confidence", 0),
            "evidence": flag_info.get("evidence", ""),
            "details": flag_info.get("details", ""),
            "data": {},
        })

    # Sort by flag number
    parsed.sort(key=lambda x: x["flag_number"])
    return parsed