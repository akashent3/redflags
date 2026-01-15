import streamlit as st
import google.generativeai as genai
import tempfile
import os
import time
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from io import BytesIO

# 1. APP CONFIGURATION
st.set_page_config(page_title="Forensic Auditor - Pro Edition", layout="wide")
st.title("🛡️ Professional Forensic 'Red Flag' Auditor")
st.markdown("---")

# Sidebar for API Key and Model Detection
key = st.sidebar.text_input("Enter Gemini API Key", type="password")

# --- PDF GENERATOR FUNCTION ---
def create_pdf(report_text):
    buf = BytesIO()
    doc = SimpleDocTemplate(buf, pagesize=letter)
    styles = getSampleStyleSheet()
    
    # Professional styles mirroring the Pennar report
    title_style = ParagraphStyle('TitleStyle', parent=styles['Heading1'], textColor=colors.red, spaceAfter=14)
    header_style = ParagraphStyle('HeaderStyle', parent=styles['Heading2'], textColor=colors.darkblue, spaceBefore=12)
    body_style = styles['BodyText']
    
    elements = []
    lines = report_text.split('\n')
    for line in lines:
        if line.startswith('###'): # Small Header
            elements.append(Paragraph(line.replace('###', '').strip(), header_style))
        elif line.startswith('##'): # Big Header
            elements.append(Paragraph(line.replace('##', '').strip(), title_style))
        else:
            elements.append(Paragraph(line, body_style))
        elements.append(Spacer(1, 4))
        
    doc.build(elements)
    buf.seek(0)
    return buf

if key:
    try:
        genai.configure(api_key=key)
        
        # Auto-detect latest available model
        available_models = [m.name for m in genai.list_models() 
                            if 'flash' in m.name.lower() 
                            and 'generateContent' in m.supported_generation_methods]
        selected_model = available_models[-1] if available_models else "models/gemini-1.5-flash"
        model = genai.GenerativeModel(selected_model)
        st.sidebar.success(f"Audit Engine Active: {selected_model}")

        # 2. FILE UPLOADER
        uploaded_files = st.file_uploader("Upload 3 Years of Annual Reports (PDF)", type="pdf", accept_multiple_files=True)

        if st.button("🚀 Generate Full Forensic Report"):
            if len(uploaded_files) > 0:
                with st.spinner("Analyzing ~750 pages. Citing Notes to Accounts..."):
                    
                    # Direct PDF Upload to Google for 100% data access
                    google_files = []
                    for uploaded_file in uploaded_files:
                        with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp:
                            tmp.write(uploaded_file.getvalue())
                            tmp_path = tmp.name
                        
                        g_file = genai.upload_file(path=tmp_path, display_name=uploaded_file.name)
                        google_files.append(g_file)
                        os.unlink(tmp_path)

                    time.sleep(5) 

                    # 3. THE COMPLETE, NON-DILUTED 35-CHECK PROMPT
                    prompt = """
                    Act as a Senior Forensic Financial Auditor. Your goal is to generate a 'RED FLAG REPORT' for the company in the attached 3 years of documents, mirroring the Pennar Industries sample report exactly.

                    STRICT DATA EXTRACTION RULES:
                    1. Use ONLY primary financial statements (Balance Sheet, P&L, Cash Flow) and the 'Notes to Accounts'.
                    2. C1 CASH YIELD RULE: Strictly compare 'Interest Income' (from Other Income Notes) against ONLY 'Bank FDs' or 'Balances with Banks' in the 'Cash & Bank' notes. Ignore general investments.
                    3. SOURCE ATTRIBUTION: For every flag, cite the specific 'Note Number' or 'Statement' used for the calculation.

                    PHASE 1: EXECUTE THESE 35 DETAILED CHECKS:

                    Section A: Revenue & Earnings Quality
                    A1. OCF / EBITDA Ratio: Compares Operating Cash Flow (OCF) to EBITDA over 3 years. Ideally >0.7.
                    A2. Exceptional Items Recurrence: Scans for 'Exceptional Items' appearing every year to boost profits.
                    A3. Unbilled Revenue vs. Sales Growth: If unbilled revenue grows faster than sales, it suggests aggressive recognition.
                    A4. Receivables Aging vs. Quarterly Revenue: Compares trade receivables >6 months against quarterly revenue.
                    A5. DSO vs. Business Model: Measures speed of payment. Spike >120 days signals channel stuffing.
                    A6. Gross vs. Net Revenue Recognition: Verifies if company books full value (Gross) when it acts as an agent.
                    A7. Bad Debt Provisioning Trends: Checks if provisions decline while receivables rise.
                    A8. Working Capital Divergence: Checks if Working Capital growth > Revenue growth.

                    Section B: Asset Quality & Capitalization
                    B1. CWIP Aging: Monitors CWIP/Gross Block. If high for years without being capitalized, it may be fake.
                    B2. Depreciation Rate Trajectory: Ensures rates weren't lowered to boost profits.
                    B3. Intangible Capitalization / PBT: Checks if software/R&D is being capitalized aggressively.
                    B4. Business Model vs. Asset Profile: Does the asset base match the core business?
                    B5. Unit Economics Sanity Check: Compares margins to peers. 'Too good to be true' is a red flag.

                    Section C: Cash Quality
                    C1. Cash Yield Test: Interest Income (Notes) / Bank FD Balance (Notes). ROI significantly below market indicates fake cash.
                    C2. Cash Composition: Removes 'Cheques in Hand' from cash balance to find real bank liquidity.
                    C3. Statutory Dues vs. Cash Balance: Checks for government payment delays (GST, PF, TDS) in the CARO report despite high cash.
                    C4. Free Cash vs. Short-term Obligations: Can company pay debts due <1 year with free cash?
                    C5. Restricted / Trapped Cash: Identifies cash pledged as margin or stuck in foreign subsidiaries.
                    C6. Dividend Sustainability: Is dividend paid out of debt or real free cash flow?

                    Section D: Hidden Leverage
                    D1. Bill Discounting Reclassification: Checks if Bill Discounting is treated as Debt or a footnote.
                    D2. Contingent Liabilities / Net Worth: Checks for payouts (lawsuits) that could wipe out equity.
                    D3. Implied Interest Rate: Interest Expense / Total Debt. If far below market, debt is understated.
                    D4. JV / Associate Loss Hiding: Checks if losses are shifted to off-book entities.
                    D5. Balance Sheet Anomalies: Scans for large unexplained 'Other Current Assets'.

                    Section E: Solvency & Leverage
                    E1. Interest Coverage Ratio: EBIT / Interest Expense. Must be >1.5x.
                    E2. Debt-to-Equity: Ratio >1.0 is risky; >2.0 is critical.
                    E3. Debt-to-EBITDA: Years of earnings needed to pay off debt.
                    E4. Net Worth Trajectory: Growth from 'Retained Earnings' or 'Asset Revaluation'?

                    Section F: Related Party & Capital Extraction
                    F1. RPT Intensity (P&L): Related Party Transactions / Revenue.
                    F2. RPT Capital Flows (Balance Sheet): RPT Investments / Total Investments.
                    F3. Equity Raise Fund Flow Tracing: Did raised capital go to the stated purpose?
                    F4. Trade Payables Stress: If payable days are rising, company is stretching suppliers.

                    Section G: Governance & Other
                    G1. Audit Opinion Review: Scans for 'Qualified Opinions' or adverse remarks in Auditor Report.
                    G2. Other Income / PBT: Flag if >50% of profit is non-core.
                    G3. Peer Comparison Overrides: Compare ROCE/Margin with similar market-cap industry peers.

                    ---
                    PHASE 2: REPORT OUTPUT STRUCTURE (MANDATORY):
                    1. Executive Summary: Context, Debt status, and the 'Scorecard' (Passed vs Concerns).
                    2. Red Flag Table: Columns [Category, Area of Concern, Assessment, Rationale & Evidence (Cite Notes)].
                    3. Lifecycle Context: (e.g., Growth vs Stressed).
                    4. Post-Table Analysis: Deep dive into the top 3 risks (e.g. Cash Yield Mismatch).
                    5. Forensic Checklist: Mandatory table listing all A1-G3 checks with execution marks.
                    """

                    response = model.generate_content([prompt] + google_files)
                    
                    st.session_state['full_report'] = response.text
                    st.markdown(st.session_state['full_report'])
                    
                    # Cleanup
                    for f in google_files:
                        genai.delete_file(f.name)
            else:
                st.error("Please upload the PDF reports.")
        
        # 4. DOWNLOAD FUNCTIONALITY
        if 'full_report' in st.session_state:
            pdf_data = create_pdf(st.session_state['full_report'])
            st.download_button(
                label="📥 Download Forensic PDF Report",
                data=pdf_data,
                file_name="Forensic_Red_Flag_Audit.pdf",
                mime="application/pdf"
            )

    except Exception as e:
        st.error(f"Critical System Error: {e}")
else:
    st.info("👈 Enter your Gemini API Key in the sidebar to begin.")