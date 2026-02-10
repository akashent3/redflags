"""Gemini prompt analyzer for PDF-based red flags. Non-banks: 23 flags, Banks: 25 flags."""

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

Analyze this annual report and check for ALL 23 red flags listed below. For each flag, provide:
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
      "rule": "Auditor included Emphasis of Matter or Other Matter paragraphs highlighting concerns",
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
    "kam_revenue": {
      "flag_number": 5,
      "flag_name": "KAM Revenue Recognition",
      "category": "Auditor",
      "severity": "HIGH",
      "rule": "Revenue recognition listed as a Key Audit Matter (high risk area per auditor)",
      "triggered": false,
      "confidence": 0,
      "evidence": "explanation",
      "details": ""
    },
    "audit_fees": {
      "flag_number": 6,
      "flag_name": "Audit Fees Unusual",
      "category": "Auditor",
      "severity": "LOW",
      "rule": "Audit fees unusually low (<0.01% of revenue) or non-audit fees exceed audit fees",
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
- Check for "Emphasis of Matter" or "Other Matter" paragraphs in the auditor's report
- These highlight important issues without qualifying the opinion
- Look for references to contingencies, going concern, litigation, regulatory issues
- Multiple EOM paragraphs increase severity

**FLAG 4 - Going Concern Doubt:**
- Search for "going concern", "material uncertainty", "ability to continue as a going concern"
- Check both auditor's report and notes to financial statements
- Also check for "accumulated losses exceed net worth" or similar language

**FLAG 5 - KAM Revenue Recognition:**
- Look in the "Key Audit Matters" section of the auditor's report
- Check if "Revenue Recognition" or "Revenue from Operations" is listed as a KAM
- This suggests the auditor found revenue recognition to be a high-risk area
- Note the specific reason the auditor flagged it

**FLAG 6 - Audit Fees Unusual:**
- Find statutory audit fees in the notes (usually under "Payments to Auditors" or similar)
- Compare audit fees to company revenue - unusually low fees (<0.01% of revenue) may indicate inadequate audit
- Also check for high non-audit fees relative to audit fees (independence concern)

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
- Flag if: (a) JVs/associates have reported losses for 2+ consecutive years, (b) significant impairment/write-down of JV/associate investments, or (c) company's share of JV/associate losses exceeds 5% of consolidated profit
- Persistent losses in JVs/associates suggest potential loss-parking in off-balance-sheet entities

Remember: Return ONLY the JSON object, no other text. Be precise and cite specific page numbers, amounts, or quotes from the report where possible.
"""

# Bank/NBFC/Financial Services prompt - replaces #50 (bad_debt) with 3 bank-specific flags (#57 CASA, #58 PCR, #59 Restructured Book)
ANALYSIS_PROMPT_BANK = """You are an expert Indian financial analyst specializing in forensic accounting and red flag detection for **banks, NBFCs, and financial services companies**. You are analyzing an annual report PDF.

**CRITICAL INSTRUCTION - CONSOLIDATED vs STANDALONE:**
- You MUST look for CONSOLIDATED financial statements FIRST.
- ONLY if the annual report does NOT contain consolidated statements (i.e., it is a standalone-only entity with no subsidiaries), then use standalone statements.
- If both consolidated and standalone are present, STRICTLY use ONLY consolidated figures.
- State clearly at the top which type you used: "consolidated" or "standalone".

Analyze this annual report and check for ALL 25 red flags listed below. For each flag, provide:
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
      "rule": "Auditor included Emphasis of Matter or Other Matter paragraphs highlighting concerns",
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
    "kam_revenue": {
      "flag_number": 5,
      "flag_name": "KAM Revenue/Interest Income Recognition",
      "category": "Auditor",
      "severity": "HIGH",
      "rule": "Revenue or interest income recognition listed as a Key Audit Matter",
      "triggered": false,
      "confidence": 0,
      "evidence": "explanation",
      "details": ""
    },
    "audit_fees": {
      "flag_number": 6,
      "flag_name": "Audit Fees Unusual",
      "category": "Auditor",
      "severity": "LOW",
      "rule": "Audit fees unusually low (<0.01% of revenue) or non-audit fees exceed audit fees",
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
    "regulatory_penalties": {
      "flag_number": 30,
      "flag_name": "SEBI/RBI Penalties",
      "category": "Governance",
      "severity": "HIGH",
      "rule": "SEBI/RBI orders, penalties, NPA divergence flags, or regulatory non-compliance reported",
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
    "casa_declining": {
      "flag_number": 57,
      "flag_name": "CASA Ratio Declining",
      "category": "Cash Flow",
      "severity": "MEDIUM",
      "rule": "CASA ratio declined >300bps YoY or below 30%, indicating costlier funding mix",
      "triggered": false,
      "confidence": 0,
      "evidence": "explanation",
      "details": ""
    },
    "pcr_declining": {
      "flag_number": 58,
      "flag_name": "Provision Coverage Ratio Declining",
      "category": "Balance Sheet",
      "severity": "HIGH",
      "rule": "Provision coverage ratio declined >5 percentage points YoY or below 60%",
      "triggered": false,
      "confidence": 0,
      "evidence": "explanation",
      "details": ""
    },
    "restructured_book": {
      "flag_number": 59,
      "flag_name": "Restructured Book Increasing",
      "category": "Balance Sheet",
      "severity": "HIGH",
      "rule": "Restructured advances increased >20% YoY or exceed 2% of gross advances",
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
      "rule": "Change in revenue/interest income recognition accounting policy during the year",
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
      "rule": "Unbilled revenue, accrued interest, or contract assets exceed 10% of total revenue and growing",
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
- Check for "Emphasis of Matter" or "Other Matter" paragraphs in the auditor's report
- These highlight important issues without qualifying the opinion
- Look for references to contingencies, going concern, litigation, regulatory issues
- Multiple EOM paragraphs increase severity

**FLAG 4 - Going Concern Doubt:**
- Search for "going concern", "material uncertainty", "ability to continue as a going concern"
- Check both auditor's report and notes to financial statements
- Also check for "accumulated losses exceed net worth" or similar language

**FLAG 5 - KAM Revenue/Interest Income Recognition:**
- Look in the "Key Audit Matters" section of the auditor's report
- Check if "Revenue Recognition", "Interest Income", or "Advances Classification" is listed as a KAM
- For banks, also check if NPA classification or provision adequacy is a KAM
- Note the specific reason the auditor flagged it

**FLAG 6 - Audit Fees Unusual:**
- Find statutory audit fees in the notes (usually under "Payments to Auditors")
- Compare audit fees to company revenue - unusually low fees (<0.01% of revenue) may indicate inadequate audit
- Also check for high non-audit fees relative to audit fees (independence concern)

**FLAG 15 - RPT > 10% Revenue:**
- Find the Related Party Transactions disclosure (Note/Schedule)
- Sum all transaction values with related parties
- Compare total RPT to total revenue/interest income
- Flag if RPT exceeds 10% of revenue

**FLAG 16 - Loans to Related Parties:**
- In the RPT note, look for: loans given, advances, deposits with related parties
- Check for outstanding balances at year end
- Calculate if loans/advances to related parties exceed 5% of revenue OR 5% of PAT
- Flag if either threshold is breached

**FLAG 17 - RP Premium/Non-Arms Length Transactions:**
- Look for language about "arm's length" pricing in RPT disclosures
- Check if any transactions are noted as being at rates different from market
- Board/audit committee observations on RPT pricing

**FLAG 18 - RPT Revenue Increasing:**
- Compare current year RPT revenue with previous year (if disclosed)
- Check if the proportion of revenue from related parties is increasing

**FLAG 20 - Loans to Directors:**
- Specifically search for loans/advances to directors, KMP, or their relatives
- Check Section 185/186 of Companies Act compliance disclosures
- Any loan to a director is a serious red flag under Indian law

**FLAG 25 - Disproportionate Director Salary:**
- Find director/KMP remuneration details (in Corporate Governance Report or Notes)
- Compare total director remuneration to company's net profit
- If director pay > 10% of net profit or increased despite declining profits, flag it

**FLAG 27 - Inter-Corporate Deposits (ICDs):**
- Search for "inter-corporate deposits", "ICDs", "inter corporate loans"
- Check loans and advances given to group/associate companies
- Material ICDs to related or group companies are a significant red flag

**FLAG 29 - Audit Committee Issues:**
- Check audit committee composition - needs minimum 3 members, 2/3 independent
- Look for frequent changes in audit committee membership
- Review number of audit committee meetings held (minimum 4 per year)

**FLAG 30 - SEBI/RBI Penalties:**
- Search for SEBI/RBI orders, show cause notices, penalties
- For banks: check for RBI risk assessment observations, NPA divergence reports
- Look for monetary penalties imposed by RBI for regulatory non-compliance
- Check if the bank/NBFC faces any regulatory action or restrictions

**FLAG 31 - Whistleblower Complaints:**
- Check the whistleblower/vigil mechanism section
- Look for mentions of complaints received, investigated, or pending
- Also search for fraud reported by auditors under Section 143(12)

**FLAG 35 - Contingent Liabilities High:**
- Find contingent liabilities note in the financial statements
- Sum all contingent liabilities (tax demands, legal cases, guarantees)
- Compare to net worth (capital + reserves for banks)
- Flag if contingent liabilities > 20% of net worth

**FLAG 36 - Debt Restructuring:**
- Search for "restructuring", "one-time settlement", "OTS", "CDR", "SDR"
- Check for "change in repayment terms", "moratorium", "standstill"
- For banks: check if the bank itself has been subject to PCA (Prompt Corrective Action)

**FLAG 37 - Asset Pledging:**
- Look for "charge created", "assets pledged", "security offered"
- Check borrowing notes for details of assets pledged
- Flag if significant portion of assets (>30%) are pledged

**FLAG 57 - CASA Ratio Declining (BANK-SPECIFIC):**
- Find the CASA (Current Account Savings Account) ratio disclosure
- Usually reported in management commentary, operating metrics, or deposit breakdown
- Check current year CASA ratio vs previous year
- Flag if CASA ratio declined by >300 basis points (3 percentage points) YoY
- Also flag if CASA ratio is below 30% (indicates high dependence on costly term deposits)
- A declining CASA ratio means the bank's cost of funds is increasing

**FLAG 58 - Provision Coverage Ratio Declining (BANK-SPECIFIC):**
- Find the Provision Coverage Ratio (PCR) in the asset quality section
- PCR = Provisions held / Gross NPAs
- Check current year PCR vs previous year
- Flag if PCR declined by >5 percentage points YoY (e.g., from 75% to 69%)
- Also flag if PCR is below 60% (inadequate coverage of bad loans)
- Look in Basel III disclosures, asset quality section, or key ratios table

**FLAG 59 - Restructured Book Increasing (BANK-SPECIFIC):**
- Search for "restructured advances", "restructured book", "restructured accounts"
- Check the asset quality notes and Schedule 11/12
- Flag if restructured advances increased >20% YoY
- Also flag if restructured book exceeds 2% of gross advances
- Look for MSME restructuring, COVID restructuring carryovers, or other restructuring schemes
- High restructured book suggests hidden stress that may become future NPAs

**FLAG 40 - Revenue Recognition Policy Change:**
- Check accounting policies section for changes in revenue/interest income recognition
- For banks: check for changes in interest recognition on advances, fee income recognition
- Recent changes to revenue recognition methods are a concern

**FLAG 41 - Unbilled Revenue High:**
- Search for "unbilled revenue", "accrued interest", "contract assets"
- For banks: check accrued interest on advances (interest recognized but not received)
- Compare to total revenue and flag if > 10% and growing

**FLAG 42 - MD&A Tone Defensive:**
- Read the Management Discussion & Analysis (MD&A) section
- Look for excessive blame on external factors (RBI policy, global factors)
- Check for absence of quantitative targets on asset quality improvement
- Compare management commentary with actual financial performance

**FLAG 51 - JV/Associate Loss Hiding:**
- Check for investments in joint ventures and associates
- Look for share of profit/loss from associates and JVs in the P&L
- Flag if JVs/associates have reported losses for 2+ consecutive years
- Check for significant impairment/write-down of JV/associate investments

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
    """Analyze an annual report PDF using Gemini. Non-banks: 23 flags, Banks: 25 flags.

    Args:
        pdf_path: Path to the annual report PDF file
        api_key: Gemini API key (or set GEMINI_API_KEY env var)
        is_financial_sector: If True, use bank-specific prompt with CASA/PCR/restructured flags

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

    model = genai.GenerativeModel("gemini-2.5-flash-preview-05-20")

    prompt = ANALYSIS_PROMPT_BANK if is_financial_sector else ANALYSIS_PROMPT
    logger.info(f"Sending analysis request to Gemini ({'bank' if is_financial_sector else 'non-bank'} prompt)...")
    response = model.generate_content(
        [pdf_file, prompt],
        generation_config=genai.GenerationConfig(
            temperature=0.1,
            max_output_tokens=16384,
        ),
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
