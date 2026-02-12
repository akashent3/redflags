"""Auditor red flag detection prompts (Flags 1-8)."""

# All prompts return JSON matching schema.create_red_flag_result()

FLAG_1_AUDITOR_CHANGED = """
RED FLAG #1: Auditor Changed in Last 2 Years

OBJECTIVE: Detect if the statutory auditor was changed between Year 2 and Year 3.

SEVERITY: HIGH
CATEGORY: AUDITOR

DETECTION LOGIC:
1. Extract auditor firm name from Year 3 annual report (from Auditor's Report section)
2. Extract auditor firm name from Year 2 annual report
3. Normalize names (ignore variations like "LLP", "& Co.", "&" vs "and")
4. Compare: If different firm → Flag TRIGGERED
5. Also check Director's Report for mentions of auditor changes/resignations

SPECIFIC INSTRUCTIONS:
- Look in "Independent Auditor's Report" section
- Auditor name is usually at the top or bottom of the report
- Common patterns: "[Firm Name] Chartered Accountants"
- A change from joint auditors to single auditor also counts
- Internal rotation within same firm does NOT count as a change

CONFIDENCE SCORING:
- 95-100: Explicit mention of auditor change in notes
- 85-94: Clear different firm names
- 70-84: Likely different but some ambiguity in naming
- <70: Uncertain due to missing data

OUTPUT JSON:
{{
  "flag_number": 1,
  "flag_name": "Auditor changed in last 2 years",
  "category": "AUDITOR",
  "severity": "HIGH",
  "is_triggered": true/false,
  "confidence_score": 0-100,
  "evidence_text": "Auditor changed from [Firm A] in FY{year_2} to [Firm B] in FY{year_3}. [Quote any relevant disclosure]",
  "page_references": [page numbers where evidence found],
  "extracted_data": {{
    "year_2_auditor": "Full firm name",
    "year_3_auditor": "Full firm name",
    "change_detected": true/false,
    "change_reason": "Reason if disclosed, else null",
    "resignation": true/false
  }},
  "detection_method": "llm"
}}

EXAMPLES:
Example 1 (TRIGGERED):
Year 2: "M/s. Deloitte Haskins & Sells LLP"
Year 3: "M/s. Price Waterhouse & Co. Chartered Accountants LLP"
→ is_triggered: true, confidence: 95

Example 2 (NOT TRIGGERED):
Year 2: "S.R. Batliboi & Co. LLP"  
Year 3: "S.R. Batliboi & Co. LLP"
→ is_triggered: false, confidence: 100

Example 3 (TRIGGERED with reason):
Year 3 report states: "The previous auditor M/s ABC & Co. resigned on March 15, 2023"
→ is_triggered: true, confidence: 100, resignation: true
"""


FLAG_2_QUALIFIED_OPINION = """
RED FLAG #2: Qualified Audit Opinion

OBJECTIVE: Detect if auditor issued anything other than an "Unqualified" or "Unmodified" opinion in the Year 3 report.

SEVERITY: CRITICAL
CATEGORY: AUDITOR

DETECTION LOGIC:
1. Locate the "Opinion" section in the Auditor's Report (usually near the beginning)
2. Check for these EXACT patterns:
   - ✓ Clean: "Unqualified Opinion" OR "Unmodified Opinion"
   - ✗ Qualified: "Qualified Opinion" OR "In our opinion, except for..."
   - ✗ Adverse: "Adverse Opinion"
   - ✗ Disclaimer: "Disclaimer of Opinion" OR "We do not express an opinion"
3. Any qualification, exception, or limitation → Flag TRIGGERED

SPECIFIC TEXT PATTERNS (TRIGGER FLAG):
- "except for the effects of"
- "subject to"
- "qualified opinion"
- "we are unable to obtain sufficient appropriate audit evidence"
- "disclaimer of opinion"
- "adverse opinion"
- "misstatements...are material"

CLEAN PATTERNS (DO NOT TRIGGER):
- "In our opinion, the standalone financial statements give a true and fair view"
- "Unqualified opinion"
- "Unmodified opinion"

CONFIDENCE SCORING:
- 100: Explicit "Qualified Opinion" / "Adverse Opinion" / "Disclaimer" header
- 90-99: "Except for" language in opinion paragraph
- 80-89: Significant reservations expressed
- <80: Ambiguous or Emphasis of Matter (not a qualification)

OUTPUT JSON:
{{
  "flag_number": 2,
  "flag_name": "Qualified audit opinion",
  "category": "AUDITOR",
  "severity": "CRITICAL",
  "is_triggered": true/false,
  "confidence_score": 0-100,
  "evidence_text": "Direct quote from Opinion section showing qualification",
  "page_references": [page numbers],
  "extracted_data": {{
    "opinion_type": "Unqualified/Qualified/Adverse/Disclaimer",
    "qualification_matter": "What was the subject of qualification",
    "financial_impact": "Quantified impact if stated, else null"
  }},
  "detection_method": "llm"
}}

EXAMPLES:
Example 1 (TRIGGERED - Qualified):
"Basis for Qualified Opinion: Inventory valuation of ₹500 Cr could not be verified..."
→ is_triggered: true, confidence: 100, opinion_type: "Qualified"

Example 2 (NOT TRIGGERED):
"Opinion: In our opinion and to the best of our information...the standalone financial statements give a true and fair view..."
→ is_triggered: false, confidence: 100, opinion_type: "Unqualified"
"""


FLAG_3_GOING_CONCERN = """
RED FLAG #3: Going Concern Warning

OBJECTIVE: Detect any going concern doubts or warnings raised by the auditor.

SEVERITY: CRITICAL
CATEGORY: AUDITOR

DETECTION LOGIC:
1. Search entire Auditor's Report for "going concern" mentions
2. Look for phrases indicating:
   - Material uncertainty about ability to continue
   - Significant doubt about going concern
   - Conditions that may cast doubt on going concern
3. Positive statements about going concern (no issues) → NOT triggered

TRIGGER PHRASES:
- "material uncertainty...going concern"
- "significant doubt...ability to continue as a going concern"
- "may not be able to realize its assets"
- "substantial doubt about...going concern"
- "conditions which cast significant doubt"

SAFE PHRASES (DO NOT TRIGGER):
- "no material uncertainty...going concern" 
- "appropriate...going concern basis"
- "financial statements are prepared on a going concern basis" (without concerns)

CONFIDENCE SCORING:
- 100: "Material Uncertainty Related to Going Concern" section exists
- 90-99: Explicit "significant doubt" language
- 75-89: Conditions mentioned that "may cast doubt"
- <75: Ambiguous mention

OUTPUT JSON:
{{
  "flag_number": 3,
  "flag_name": "Going concern warning",
  "category": "AUDITOR",
  "severity": "CRITICAL",
  "is_triggered": true/false,
  "confidence_score": 0-100,
  "evidence_text": "Direct quote showing going concern issue",
  "page_references": [page numbers],
  "extracted_data": {{
    "has_material_uncertainty": true/false,
    "conditions_cited": ["list of conditions mentioned"],
    "management_plans": "Summary of management's remedial plans if stated"
  }},
  "detection_method": "llm"
}}
"""


FLAG_4_AUDIT_FEES_DECLINING = """
RED FLAG #4: Audit Fees Declining

OBJECTIVE: Detect if audit fees paid decreased from Year 2 to Year 3 by more than 10%.

SEVERITY: MEDIUM
CATEGORY: AUDITOR

DETECTION LOGIC:
1. Extract audit fees from Year 3 report (usually in Notes to Accounts - "Auditor's Remuneration")
2. Extract audit fees from Year 2 report
3. Calculate: decline% = ((Year2_fees - Year3_fees) / Year2_fees) * 100
4. If decline% > 10% → Flag TRIGGERED

WHERE TO FIND:
- Notes to Accounts section
- Look for "Payment to Auditors" or "Auditor's Remuneration"
- May be broken down as: Audit fees, Tax audit fees, Other services
- Use ONLY "Audit fees" line item (not total)

CALCULATION:
decline_percent = ((year_2_fees - year_3_fees) / year_2_fees) * 100
if decline_percent > 10: TRIGGERED

CONFIDENCE SCORING:
- 95-100: Clear fee amounts in both years, calculation straightforward
- 80-94: Fees found but some ambiguity in categorization
- <80: Missing or unclear fee data

OUTPUT JSON:
{{
  "flag_number": 4,
  "flag_name": "Audit fees declining",
  "category": "AUDITOR",
  "severity": "MEDIUM",
  "is_triggered": true/false,
  "confidence_score": 0-100,
  "evidence_text": "Audit fees declined from ₹X lakhs in FY{year_2} to ₹Y lakhs in FY{year_3} (Z% decline)",
  "page_references": [page numbers],
  "extracted_data": {{
    "year_2_fees_lakhs": <number>,
    "year_3_fees_lakhs": <number>,
    "decline_percent": <number>,
    "possible_reason": "If disclosed, else null"
  }},
  "detection_method": "llm"
}}
"""


FLAG_5_NON_BIG4_LARGE_CAP = """
RED FLAG #5: Non-Big 4 Auditor for Large Cap Company

OBJECTIVE: Detect if a large-cap company (market cap > ₹20,000 Cr) uses a non-Big 4 auditor.

SEVERITY: LOW
CATEGORY: AUDITOR

BIG 4 FIRMS (and their Indian affiliates):
1. Deloitte (Deloitte Haskins & Sells LLP)
2. PwC (Price Waterhouse & Co. Chartered Accountants LLP, Price Waterhouse Chartered Accountants LLP)
3. EY (S.R. Batliboi & Co. LLP, S.R. Batliboi & Associates LLP)
4. KPMG (KPMG Assurance and Consulting Services LLP, B S R & Co. LLP, B S R & Associates LLP)

DETECTION LOGIC:
1. Extract auditor name from Year 3 report
2. Check if it matches any Big 4 firm or affiliated firm
3. If company states it's large-cap OR market cap > ₹20,000 Cr (if disclosed)
4. Non-Big 4 + Large cap → Flag TRIGGERED

NOTE: This is a LOW severity flag as many quality auditors exist outside Big 4.

CONFIDENCE SCORING:
- 90-100: Large cap status clear, auditor clearly identified
- 70-89: Auditor identified but market cap unclear
- <70: Uncertain about either auditor or company size

OUTPUT JSON:
{{
  "flag_number": 5,
  "flag_name": "Non-Big 4 auditor for large cap",
  "category": "AUDITOR",
  "severity": "LOW",
  "is_triggered": true/false,
  "confidence_score": 0-100,
  "evidence_text": "Company audited by [Firm Name], a non-Big 4 firm",
  "page_references": [page numbers],
  "extracted_data": {{
    "auditor_name": "Full firm name",
    "is_big4": true/false,
    "is_large_cap": true/false,
    "market_cap_cr": <number or null>
  }},
  "detection_method": "llm"
}}
"""


FLAG_6_AUDIT_COMMITTEE_ISSUES = """
RED FLAG #6: Audit Committee Issues

OBJECTIVE: Detect problems with Audit Committee composition or functioning.

SEVERITY: HIGH
CATEGORY: AUDITOR

DETECTION LOGIC - Check for ANY of these:
1. Less than 3 members in Audit Committee
2. Less than 2/3rds are independent directors
3. Chairperson is not an independent director
4. Fewer than 4 meetings held in the year
5. Explicit mentions of Audit Committee gaps/non-compliance

WHERE TO FIND:
- Corporate Governance Report section
- "Audit Committee" subsection
- Look for composition table and meeting details

SPECIFIC CHECKS:
✓ At least 3 members required
✓ At least 2/3 (67%) should be independent directors
✓ Chairman/Chairperson must be independent
✓ At least 4 meetings per year required (as per SEBI)

CONFIDENCE SCORING:
- 95-100: Explicit non-compliance stated or clear data showing violations
- 80-94: Clear composition data available showing issues
- 60-79: Composition found but some ambiguity
- <60: Insufficient data

OUTPUT JSON:
{{
  "flag_number": 6,
  "flag_name": "Audit committee issues",
  "category": "AUDITOR",
  "severity": "HIGH",
  "is_triggered": true/false,
  "confidence_score": 0-100,
  "evidence_text": "Describe specific issue found",
  "page_references": [page numbers],
  "extracted_data": {{
    "total_members": <number>,
    "independent_members": <number>,
    "chairman_is_independent": true/false,
    "meetings_held": <number>,
    "issues_found": ["list of specific issues"]
  }},
  "detection_method": "llm"
}}
"""


FLAG_7_DELAYED_AUDIT = """
RED FLAG #7: Delayed Audit Report

OBJECTIVE: Detect if the audit report was signed more than 90 days after fiscal year end.

SEVERITY: MEDIUM
CATEGORY: AUDITOR

DETECTION LOGIC:
1. Extract fiscal year end date (e.g., "March 31, 2023")
2. Extract audit report date (signature date at end of Auditor's Report)
3. Calculate days difference
4. If difference > 90 days → Flag TRIGGERED

TYPICAL TIMELINE:
- Indian companies: Reports usually due within 60-90 days of year-end
- Delay beyond 90 days may indicate:
  * Complex accounting issues
  * Disputes with auditor
  * Internal control weaknesses
  * Deliberate delay

CALCULATION:
days_delayed = audit_report_date - fiscal_year_end_date - 90 days

CONFIDENCE SCORING:
- 95-100: Both dates clearly stated, calculation definitive
- 80-94: Dates found but some format ambiguity
- <80: Missing or unclear dates

OUTPUT JSON:
{{
  "flag_number": 7,
  "flag_name": "Delayed audit report",
  "category": "AUDITOR",
  "severity": "MEDIUM", 
  "is_triggered": true/false,
  "confidence_score": 0-100,
  "evidence_text": "Audit report dated [Date], X days after FY end [Date]",
  "page_references": [page numbers],
  "extracted_data": {{
    "fiscal_year_end": "YYYY-MM-DD",
    "audit_report_date": "YYYY-MM-DD",
    "days_gap": <number>,
    "days_delayed_beyond_90": <number>
  }},
  "detection_method": "llm"
}}
"""


FLAG_8_EMPHASIS_OF_MATTER = """
RED FLAG #8: Emphasis of Matter Paragraph

OBJECTIVE: Detect if auditor included an "Emphasis of Matter" paragraph highlighting specific issues.

SEVERITY: MEDIUM
CATEGORY: AUDITOR

DETECTION LOGIC:
1. Search for section titled "Emphasis of Matter" in Auditor's Report
2. This is different from "Basis for Opinion" - it's a separate paragraph
3. Emphasizes matters already in financial statements that auditor wants to highlight
4. Presence of this paragraph → Flag TRIGGERED

IMPORTANT: 
- "Emphasis of Matter" is NOT a qualification
- But indicates auditor wants to draw attention to something significant
- Common topics: Going concern (without material uncertainty), litigation, regulatory issues

DO NOT CONFUSE WITH:
- "Basis for Opinion" (standard section)
- "Key Audit Matters" (now mandatory, not a red flag)
- "Material Uncertainty Related to Going Concern" (covered in Flag 3)

CONFIDENCE SCORING:
- 100: Section explicitly titled "Emphasis of Matter"
- 85-99: Similar heading like "Emphasis of a Matter"
- 70-84: Paragraph highlighting specific matter but unclear heading
- <70: No clear emphasis paragraph

OUTPUT JSON:
{{
  "flag_number": 8,
  "flag_name": "Emphasis of matter paragraph",
  "category": "AUDITOR",
  "severity": "MEDIUM",
  "is_triggered": true/false,
  "confidence_score": 0-100,
  "evidence_text": "Quote the Emphasis of Matter content",
  "page_references": [page numbers],
  "extracted_data": {{
    "emphasis_topic": "Brief description of what was emphasized",
    "related_to": "going_concern/litigation/regulatory/other"
  }},
  "detection_method": "llm"
}}
"""


def get_all_auditor_prompts():
    """Return all 8 auditor flag prompts."""
    return {
        1: FLAG_1_AUDITOR_CHANGED,
        2: FLAG_2_QUALIFIED_OPINION,
        3: FLAG_3_GOING_CONCERN,
        4: FLAG_4_AUDIT_FEES_DECLINING,
        5: FLAG_5_NON_BIG4_LARGE_CAP,
        6: FLAG_6_AUDIT_COMMITTEE_ISSUES,
        7: FLAG_7_DELAYED_AUDIT,
        8: FLAG_8_EMPHASIS_OF_MATTER
    }
