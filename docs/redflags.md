**REDFLAG AI**

AI-Powered Forensic Accounting Scanner

**COMPLETE SPECIFICATION v3.0**

All Features \| 12 App Pages \| LLM-Based PDF Pipeline \| Full Tech
Stack \| Cost Analysis

February 2026

**PART A: FEATURES & IMPLEMENTATION**

**1. Executive Summary**

RedFlag AI scans corporate annual reports using AI to detect early
warning signs of financial manipulation, governance failures, and
accounting fraud - democratizing forensic accounting for retail
investors.

+----------------------------------------------------------------------+
| **The Problem**                                                      |
|                                                                      |
| 89% of retail investors never read annual reports. When they do,     |
| they miss critical red flags. Result: catastrophic losses when       |
| companies collapse - Yes Bank (-90%), DHFL (-98%), Zee (-70%) - all  |
| had visible warning signs BEFORE the crash.                          |
+======================================================================+

+----------------------------------------------------------------------+
| **The Solution**                                                     |
|                                                                      |
| Upload any PDF or search by company. In 60 seconds: Risk Score       |
| 0-100, 54 red flag checks with evidence, page references, multi-year |
| trends, Related Party Spiderweb, peer comparison.                    |
+======================================================================+

**2. Core Features (8 Total)**

**Feature 1: Instant Report Analysis**

Upload PDF or search company name. Get comprehensive analysis in 60
seconds.

- Input: PDF upload (drag-drop) OR company search (name/BSE/NSE code)

- Processing: Celery background task with WebSocket progress updates

- Output: Risk Score, category breakdown, red flag list with evidence

**Feature 2: Risk Score & Category Breakdown**

Single number (0-100) that instantly communicates risk level.

- 8 categories with weights: Auditor (20%), Cash Flow (18%), Related
  Party (15%), Promoter (15%), Governance (12%), Balance Sheet (10%),
  Revenue (5%), Textual (5%)

- Visual: Circular gauge + 8-axis spider chart

**Feature 3: Related Party Spiderweb**

Interactive network graph showing money flows between company and
related entities.

- D3.js force-directed graph with draggable nodes

- Line thickness = transaction value, color = risk level

- Click node for transaction details

**Feature 4: Multi-Year Trend Analysis**

View how risk score and metrics evolved over 3-5 years.

- Risk score timeline with event markers

- Metric charts: Promoter pledge %, CFO/PAT ratio, Receivable days

**Feature 5: Peer Comparison**

Compare with industry peers for context.

- Auto-suggested peers by industry and size

- Side-by-side score and metric comparison

**Feature 6: Portfolio Scanner**

Scan all holdings at once (Premium feature).

- Upload CSV from Zerodha/Groww/Upstox

- Risk heatmap grid showing all holdings

**Feature 7: Watchlist & Alerts**

Track companies over time, get notified when risk changes.

- Alerts: New AR filed, score change \>10, critical flag triggered

**Feature 8: Historical Fraud Database**

50+ documented Indian corporate frauds with red flag timelines.

- Pattern matching: Your stock shows 4 of 7 flags that preceded Zee
  crash

**PART B: 54 RED FLAGS FRAMEWORK**

**Category 1: Auditor Red Flags (Weight: 10%)**

**Flags:** 8 \| Highest weight - auditor is last line of defense

  ----------------------------------------------------------------------------------
  **Red Flag**      **Severity**   **Detection Logic**            **Data Source**
  ----------------- -------------- ------------------------------ ------------------
  **1. Auditor      **CRITICAL**   Check if auditor changed       Auditor Report
  resignation                      before completing full year.   header, Board
  mid-term**                       Match appointment date vs AR   Resolution
                                   date.                          

  **2. Auditor      **HIGH**       Track auditor firm across 3    Auditor Report
  change Big4 to                   years. Flag if                 signature, compare
  small**                          Deloitte/PwC/EY/KPMG changed   YoY
                                   to smaller firm.               

  **3. Qualified    **CRITICAL**   NLP scan for: \'qualified      Auditor Report -
  opinion**                        opinion\', \'except for\',     Opinion section
                                   \'subject to\'. Parse Opinion  
                                   paragraph.                     

  **4. Emphasis of  **HIGH**       Count EOM paragraphs. Flag if  Auditor Report -
  Matter                           \>2 or mentions: going         EOM section
  paragraphs**                     concern, litigation, related   
                                   party.                         

  **5. Going        **CRITICAL**   Search: \'going concern\',     Auditor Report +
  concern                          \'material uncertainty\',      Notes 1-3
  qualification**                  \'ability to continue\'.       
                                   Context must be negative.      

  **6. Key Audit    **HIGH**       Extract KAM section. Flag if   Auditor Report -
  Matters on                       relates to: revenue            KAM section
  revenue**                        recognition, receivables, RPT. 

  **7. Audit fees   **MEDIUM**     Calculate (Audit fees/Revenue) Notes - Payment to
  declining vs                     ratio. Flag if declining \>20% Auditors
  growth**                         over 3 years while revenue     
                                   grew.                          

  **8. Same auditor **MEDIUM**     Count consecutive years with   Historical Auditor
  10+ years**                      same auditor firm. Flag if     Reports
                                   \>10 years.                    
  ----------------------------------------------------------------------------------

**Category 2: Cash Flow Red Flags (Weight: 23%)**

**Flags:** 8 \| All rule-based, zero LLM cost

  ---------------------------------------------------------------------------------
  **Red Flag**     **Severity**   **Detection Logic**            **Data Source**
  ---------------- -------------- ------------------------------ ------------------
  **9. Profit      **HIGH**       CFO/PAT ratio. Flag if PAT     Cash Flow (CFO) +
  growing, CFO                    growing \>15% CAGR but CFO     P&L (PAT)
  flat**                          flat OR CFO/PAT \< 0.5 for 3   
                                  years.                         

  **10.            **HIGH**       Receivable Days =              Balance Sheet +
  Receivables \>                  (Receivables/Revenue)\*365.    P&L
  Revenue growth**                Flag if increasing \>20% over  
                                  3 years.                       

  **11. Inventory  **HIGH**       Inventory Days =               Balance Sheet +
  \> COGS growth**                (Inventory/COGS)\*365. Flag if P&L
                                  increasing \>25% over 3 years. 

  **12. Capex \>\> **MEDIUM**     Compare Capex (from Cash Flow) Cash Flow + P&L
  Depreciation**                  to Depreciation. Flag if Capex 
                                  \> 2x Depreciation for 3+      
                                  years.                         

  **13. Frequent   **MEDIUM**     Count exceptional items over 5 P&L - Exceptional
  exceptional                     years. Flag if \>3 OR          Items
  items**                         cumulative \> 20% of           
                                  cumulative PAT.                

  **14. CFO        **HIGH**       Simple check: CFO \< 0 for 2+  Cash Flow
  negative 2+                     consecutive years. Immediate   Statement
  years**                         flag for profitable company.   

  **15. Cash       **MEDIUM**     CCC = Inv Days + Recv Days -   Balance Sheet +
  conversion cycle                Pay Days. Flag if increased    P&L
  up**                            \>30% over 3 years.            

  **16. Unusual    **MEDIUM**     Other Income / PBT ratio. Flag P&L - Other Income
  other income**                  if \>25% OR growing faster     
                                  than operating income.         
  ---------------------------------------------------------------------------------

**Category 3: Related Party Red Flags (Weight: 20%)**

**Flags:** 7 \| Source for Spiderweb visualization

  ----------------------------------------------------------------------------------
  **Red Flag**      **Severity**   **Detection Logic**            **Data Source**
  ----------------- -------------- ------------------------------ ------------------
  **17. RPT \> 10%  **HIGH**       Sum all RPT values. Calculate  Notes - RPT (Note
  of revenue**                     as % of total revenue. Flag if 35-40)
                                   \>10%.                         

  **18. Loans to    **HIGH**       Extract loans/advances to      Notes - RPT +
  related parties**                related parties. Flag if \>5%  Loans
                                   of assets OR increasing YoY.   

  **19. Purchases   **MEDIUM**     If RPT has price details,      Notes - RPT
  from RP at                       compare to market. Flag if     details
  premium**                        \>15% above market.            

  **20. Revenue     **MEDIUM**     Track % revenue from RP over 3 Notes - RPT +
  from RP                          years. Flag if increasing and  Segments
  increasing**                     now \>15%.                     

  **21. Complex     **MEDIUM**     Count subsidiaries +           Notes -
  structure \>20                   associates + JVs. Flag if \>20 Investments
  subs**                           OR added \>5 new in year.      

  **22. Loans to    **HIGH**       Search RPT for loans to        Notes - RPT
  directors/KMP**                  directors, KMP, relatives. Any 
                                   amount \> Rs.10L flagged.      

  **23. New related **MEDIUM**     Compare RP list YoY. Flag if   Notes - RPT list
  parties added**                  \>3 new OR new promoter-group  
                                   entity.                        
  ----------------------------------------------------------------------------------

**Category 4: Promoter Red Flags (Weight: 10%)**

**Flags:** 6

  -----------------------------------------------------------------------------------
  **Red Flag**       **Severity**   **Detection Logic**            **Data Source**
  ------------------ -------------- ------------------------------ ------------------
  **24. Promoter     **CRITICAL**   Extract \'Shares pledged\' as  Shareholding
  pledge \> 50%**                   % of promoter holding from     Pattern - Part A
                                    Shareholding Pattern. Flag if  
                                    \>50%.                         

  **25. Pledge       **HIGH**       Track pledge % across 4        Quarterly
  increasing QoQ**                  quarters. Flag if increasing   Shareholding
                                    3+ consecutive quarters OR     
                                    +15% single quarter.           

  **26. Promoter     **MEDIUM**     Compare promoter % YoY. Flag   Shareholding
  selling shares**                  if decreased \>2% while        Pattern YoY
                                    guidance was positive.         

  **27.              **MEDIUM**     MD/CEO remuneration as % of    Notes -
  Disproportionate                  PAT. Flag if \>5% OR grew      Remuneration
  salary**                          faster than PAT.               

  **28. Promoter     **LOW**        Track promoter entity names.   Shareholding -
  entity name                       Flag if any changed name.      Names YoY
  change**                                                         

  **29. ICDs to      **HIGH**       Search for ICDs to promoter    Notes - Loans +
  promoter group**                  entities. Flag if \>Rs.50 Cr   RPT
                                    OR \>2% of net worth.          
  -----------------------------------------------------------------------------------

**Category 5: Governance Red Flags (Weight: 5%)**

**Flags:** 7

  ---------------------------------------------------------------------------------
  **Red Flag**     **Severity**   **Detection Logic**            **Data Source**
  ---------------- -------------- ------------------------------ ------------------
  **30.            **HIGH**       Check Board changes. Flag if   Corp Gov - Board
  Independent                     independent director resigned  Changes
  director exit**                 mid-term.                      

  **31. CFO/CS     **HIGH**       Track CFO and Company          Corp Gov - KMP
  change in year**                Secretary names. Flag if       details
                                  changed during year.           

  **32. Low board  **MEDIUM**     Extract attendance %. Flag if  Corp Gov -
  attendance**                    any director \<50% OR average  Attendance
                                  \<75%.                         

  **33. Related on **MEDIUM**     Check Audit Committee          Corp Gov -
  Audit                           composition. Flag if           Committees
  Committee**                     non-independent person         
                                  present.                       

  **34. Delayed    **MEDIUM**     Check AGM date. Flag if after  Directors Report -
  AGM/results**                   Sept 30. Check filing          AGM
                                  deadlines.                     

  **35.            **HIGH**       Search for penalties/fines     Contingent Liab +
  SEBI/Exchange                   from SEBI, NSE, BSE.           Dir Report
  penalties**                                                    

  **36.            **MEDIUM**     Check whistle-blower section.  Corp Gov -
  Whistle-blower                  Flag if complaints pending.    Whistle-blower
  complaints**                                                   
  ---------------------------------------------------------------------------------

**Category 6: Balance Sheet Red Flags (Weight: 15%)**

**Flags:** 7

  ----------------------------------------------------------------------------------
  **Red Flag**      **Severity**   **Detection Logic**            **Data Source**
  ----------------- -------------- ------------------------------ ------------------
  **37. Debt        **HIGH**       D/E ratio for 3 years. Flag if Balance Sheet
  growing \>                       increased \>50% OR D/E \> 2.   
  equity**                                                        

  **38. Interest    **HIGH**       ICR = EBIT/Interest. Flag if   P&L
  coverage \< 2x**                 \<2 OR declined \>30% over 3   
                                   years.                         

  **39. ST debt     **HIGH**       Compare current ratio. Flag if Balance Sheet
  funding LT                       \<1 OR ST borrowings \>        
  assets**                         current assets - inventory.    

  **40. Contingent  **HIGH**       Sum all contingent             Notes - Contingent
  liab \> 20% NW**                 liabilities. Flag if \>20% of  Liab
                                   net worth.                     

  **41. Frequent    **MEDIUM**     Search for: \'restructuring\', Notes - Borrowings
  debt                             \'settlement\',                
  restructuring**                  \'moratorium\'. Flag any.      

  **42. Heavy asset **MEDIUM**     Check pledged assets. Flag if  Notes - Borrowings
  pledging**                       all major assets pledged OR    
                                   \>80% value.                   

  **43. Intangibles **MEDIUM**     Intangible assets as % of      Balance Sheet +
  growing fast**                   total. Flag if \>30% OR grew   Notes
                                   \> revenue.                    
  ----------------------------------------------------------------------------------

**Category 7: Revenue Quality Red Flags (Weight: 12%)**

**Flags:** 5

  --------------------------------------------------------------------------------
  **Red Flag**    **Severity**   **Detection Logic**            **Data Source**
  --------------- -------------- ------------------------------ ------------------
  **44. Revenue   **MEDIUM**     Q4 revenue as % of annual.     Quarterly results
  concentrated in                Flag if \>35% consistently.    
  Q4**                                                          

  **45. Top       **MEDIUM**     Customer concentration. Flag   Notes - Segments
  customer \>                    if single \>25% OR top 5       
  25%**                          \>60%.                         

  **46. Revenue   **HIGH**       Compare Accounting Policies    Notes - Policies
  policy change**                YoY. Flag any revenue          
                                 recognition change.            

  **47. Unbilled  **MEDIUM**     Track unbilled/contract        Balance Sheet +
  revenue                        assets. Flag if growing faster Notes
  growing**                      than billed for 2+ years.      

  **48. Unusual   **LOW**        Check geographic segment. Flag Notes - Segments
  export                         if significant revenue from    
  geography**                    tax havens.                    
  --------------------------------------------------------------------------------

**Category 8: Textual Red Flags (Weight: 5%)**

**Flags:** 6 \| Requires LLM analysis

  -----------------------------------------------------------------------------------
  **Red Flag**       **Severity**   **Detection Logic**            **Data Source**
  ------------------ -------------- ------------------------------ ------------------
  **49. MD&A tone    **MEDIUM**     NLP sentiment on MD&A. Flag if MD&A section
  defensive**                       negative sentiment increased   
                                    \>30% YoY.                     

  **50. Increased    **LOW**        Flesch-Kincaid readability.    MD&A + Directors
  jargon**                          Flag if difficulty increased   Report
                                    significantly.                 

  **51. Declining    **MEDIUM**     Compare detail level YoY. Flag Notes comparison
  disclosure**                      if fewer details than previous 
                                    year.                          

  **52. Risk factors **MEDIUM**     Count words in Risk section.   Directors Report -
  expanding**                       Flag if \>50% increase YoY.    Risk

  **53.              **HIGH**       LLM: Cross-reference MD&A      MD&A vs Financials
  Contradictions**                  claims with numbers. Flag      
                                    contradictions.                

  **54. Unusual      **MEDIUM**     LLM: Compare audit report to   Auditor Report
  audit language**                  template. Flag unusual         
                                    phrasing.                      
  -----------------------------------------------------------------------------------

+----------------------------------------------------------------------+
| **LLM Requirement**                                                  |
|                                                                      |
| Flags 49-54 need LLM analysis (\~Rs.5-8/doc). Flags 1-48 are 100%    |
| rule-based (Rs.0 LLM cost).                                          |
+======================================================================+

**PART B: APP INTERFACE (12 PAGES)**

**3. App Structure**

  -----------------------------------------------------------------------------------------
  **\#**         **Page**       **URL**                     **Purpose**      **Access**
  -------------- -------------- --------------------------- ---------------- --------------
  1              Landing        /                           Marketing,       Public
                                                            pricing          

  2              Login          /auth                       Authentication   Public

  3              Dashboard      /dashboard                  Home, recent,    User
                                                            alerts           

  4              New Analysis   /analyze                    Upload/search    User

  5              Results        /report/\[id\]              Score, flags,    User
                                                            visuals          

  6              Flag Detail    /report/\[id\]/flag/\[f\]   Deep dive        User

  7              Trends         /report/\[id\]/trends       Multi-year       Pro+

  8              Peers          /report/\[id\]/peers        Comparison       Pro+

  9              Portfolio      /portfolio                  Scan holdings    Premium

  10             Watchlist      /watchlist                  Track companies  Pro+

  11             Fraud DB       /learn                      Case studies     All

  12             Settings       /settings                   Profile, billing User
  -----------------------------------------------------------------------------------------

**Page 1: Landing Page**

**URL:** redflag.ai (root)

**Purpose:** Marketing page to convert visitors into signups

**Key Sections:** Hero, Demo Preview, Features, Case Studies, Pricing,
Footer

+-------------------------------------------------------------------------------------------------------------------------------------------------------+
| **LANDING PAGE - HERO SECTION**                                                                                                                       |
+=======================================================================================================================================================+
| +\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\--+ |
|                                                                                                                                                       |
| \| HEADER \|                                                                                                                                          |
|                                                                                                                                                       |
| \| \[RedFlag Logo\] Features Pricing Login \[Sign Up Free\] \|                                                                                        |
|                                                                                                                                                       |
| +\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\--+ |
|                                                                                                                                                       |
| \| \|                                                                                                                                                 |
|                                                                                                                                                       |
| \| \|                                                                                                                                                 |
|                                                                                                                                                       |
| \| YOUR AI FORENSIC ACCOUNTANT \|                                                                                                                     |
|                                                                                                                                                       |
| \| \|                                                                                                                                                 |
|                                                                                                                                                       |
| \| Detect hidden risks in annual reports \|                                                                                                           |
|                                                                                                                                                       |
| \| before they become headlines \|                                                                                                                    |
|                                                                                                                                                       |
| \| \|                                                                                                                                                 |
|                                                                                                                                                       |
| \| Yes Bank showed 5 critical red flags 18 months before collapsing. \|                                                                               |
|                                                                                                                                                       |
| \| Would you have spotted them? \|                                                                                                                    |
|                                                                                                                                                       |
| \| \|                                                                                                                                                 |
|                                                                                                                                                       |
| \| +\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\--+ +\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\--+ \|                                                         |
|                                                                                                                                                       |
| \| \| Analyze Free Now \| \| Watch Demo Video \| \|                                                                                                   |
|                                                                                                                                                       |
| \| +\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\--+ +\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\--+ \|                                                         |
|                                                                                                                                                       |
| \| \|                                                                                                                                                 |
|                                                                                                                                                       |
| \| \|                                                                                                                                                 |
|                                                                                                                                                       |
| \| \[54 Red Flags\] \[60 Sec Analysis\] \[10,000+ Users\] \|                                                                                          |
|                                                                                                                                                       |
| \| \|                                                                                                                                                 |
|                                                                                                                                                       |
| +\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\--+ |
+-------------------------------------------------------------------------------------------------------------------------------------------------------+

+-------------------------------------------------------------------------------------------------------------------------------------------------------+
| **LANDING PAGE - DEMO SECTION**                                                                                                                       |
+=======================================================================================================================================================+
| +\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\--+ |
|                                                                                                                                                       |
| \| SEE IT IN ACTION - Live Demo with Sample Company \|                                                                                                |
|                                                                                                                                                       |
| +\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\--+ |
|                                                                                                                                                       |
| \| \|                                                                                                                                                 |
|                                                                                                                                                       |
| \| +\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\--+ +\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\--+ \|               |
|                                                                                                                                                       |
| \| \| \| \| \| \|                                                                                                                                     |
|                                                                                                                                                       |
| \| \| SAMPLE RISK ANALYSIS \| \| TOP RED FLAGS DETECTED \| \|                                                                                         |
|                                                                                                                                                       |
| \| \| \| \| \| \|                                                                                                                                     |
|                                                                                                                                                       |
| \| \| +\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\--+ \| \| +\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\--+ \| \|                                     |
|                                                                                                                                                       |
| \| \| \| \| \| \| \| \[!!\] CRITICAL \| \| \|                                                                                                         |
|                                                                                                                                                       |
| \| \| \| 67 \| \| \| \| Promoter Pledge at 62% \| \| \|                                                                                               |
|                                                                                                                                                       |
| \| \| \| \| \| \| \| Evidence: Page 127 \| \| \|                                                                                                      |
|                                                                                                                                                       |
| \| \| +\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\--+ \| \| +\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\--+ \| \|                                     |
|                                                                                                                                                       |
| \| \| ELEVATED RISK \| \| \| \|                                                                                                                       |
|                                                                                                                                                       |
| \| \| \| \| +\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\--+ \| \|                                                                           |
|                                                                                                                                                       |
| \| \| +\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\--+ \| \| \| \[!!\] CRITICAL \| \| \|                                                                         |
|                                                                                                                                                       |
| \| \| \| \[Spider Chart\] \| \| \| \| Cash Flow Divergence \| \| \|                                                                                   |
|                                                                                                                                                       |
| \| \| \| 8 Categories \| \| \| \| CFO/PAT ratio: 0.25 \| \| \|                                                                                        |
|                                                                                                                                                       |
| \| \| +\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\--+ \| \| +\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\--+ \| \|                                     |
|                                                                                                                                                       |
| \| \| \| \| \| \|                                                                                                                                     |
|                                                                                                                                                       |
| \| +\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\--+ \| +\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\--+ \| \|                     |
|                                                                                                                                                       |
| \| \| \| \[!\] HIGH \| \| \|                                                                                                                          |
|                                                                                                                                                       |
| \| \| \| Related Party \> 10% \| \| \|                                                                                                                |
|                                                                                                                                                       |
| \| \| +\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\--+ \| \|                                                                                 |
|                                                                                                                                                       |
| \| +\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\--+ \|                                                                           |
|                                                                                                                                                       |
| \| \|                                                                                                                                                 |
|                                                                                                                                                       |
| \| \[ Try With Your Own Stock - Free \] \|                                                                                                            |
|                                                                                                                                                       |
| \| \|                                                                                                                                                 |
|                                                                                                                                                       |
| +\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\--+ |
+-------------------------------------------------------------------------------------------------------------------------------------------------------+

+-------------------------------------------------------------------------------------------------------------------------------------------------------+
| **LANDING PAGE - FEATURES SECTION**                                                                                                                   |
+=======================================================================================================================================================+
| +\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\--+ |
|                                                                                                                                                       |
| \| WHAT REDFLAG AI DETECTS \|                                                                                                                         |
|                                                                                                                                                       |
| +\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\--+ |
|                                                                                                                                                       |
| \| \|                                                                                                                                                 |
|                                                                                                                                                       |
| \| +\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\--+ +\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\--+ +\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\--+\|              |
|                                                                                                                                                       |
| \| \| \| \| \| \| \|\|                                                                                                                                |
|                                                                                                                                                       |
| \| \| \[Audit Icon\] \| \| \[Chart Icon\] \| \| \[Network Icon\] \|\|                                                                                 |
|                                                                                                                                                       |
| \| \| \| \| \| \| \|\|                                                                                                                                |
|                                                                                                                                                       |
| \| \| AUDITOR FLAGS \| \| CASH FLOW FLAGS \| \| RELATED PARTY \|\|                                                                                    |
|                                                                                                                                                       |
| \| \| \| \| \| \| \|\|                                                                                                                                |
|                                                                                                                                                       |
| \| \| Qualified opinions, \| \| Profit without cash,\| \| Money tunneling, \|\|                                                                       |
|                                                                                                                                                       |
| \| \| resignations, \| \| inventory bloat, \| \| complex structures, \|\|                                                                             |
|                                                                                                                                                       |
| \| \| going concern \| \| receivable games \| \| suspicious loans \|\|                                                                                |
|                                                                                                                                                       |
| \| +\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\--+ +\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\--+ +\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\--+\|              |
|                                                                                                                                                       |
| \| \|                                                                                                                                                 |
|                                                                                                                                                       |
| \| +\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\--+ +\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\--+ +\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\--+\|              |
|                                                                                                                                                       |
| \| \| \| \| \| \| \|\|                                                                                                                                |
|                                                                                                                                                       |
| \| \| \[Shield Icon\] \| \| \[User Icon\] \| \| \[Trend Icon\] \|\|                                                                                   |
|                                                                                                                                                       |
| \| \| \| \| \| \| \|\|                                                                                                                                |
|                                                                                                                                                       |
| \| \| GOVERNANCE FLAGS \| \| PROMOTER FLAGS \| \| TREND ANALYSIS \|\|                                                                                 |
|                                                                                                                                                       |
| \| \| \| \| \| \| \|\|                                                                                                                                |
|                                                                                                                                                       |
| \| \| Board changes, CFO \| \| Share pledging, \| \| 3-5 year trends, \|\|                                                                            |
|                                                                                                                                                       |
| \| \| exits, low \| \| selling while \| \| deterioration \|\|                                                                                         |
|                                                                                                                                                       |
| \| \| attendance, SEBI \| \| bullish guidance \| \| patterns visible \|\|                                                                             |
|                                                                                                                                                       |
| \| +\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\--+ +\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\--+ +\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\--+\|              |
|                                                                                                                                                       |
| \| \|                                                                                                                                                 |
|                                                                                                                                                       |
| +\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\--+ |
+-------------------------------------------------------------------------------------------------------------------------------------------------------+

+-------------------------------------------------------------------------------------------------------------------------------------------------------+
| **LANDING PAGE - CASE STUDY SECTION**                                                                                                                 |
+=======================================================================================================================================================+
| +\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\--+ |
|                                                                                                                                                       |
| \| LEARN FROM HISTORY \|                                                                                                                              |
|                                                                                                                                                       |
| +\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\--+ |
|                                                                                                                                                       |
| \| \|                                                                                                                                                 |
|                                                                                                                                                       |
| \| +\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\--+\|    |
|                                                                                                                                                       |
| \| \| YES BANK: The Rs. 404 to Rs. 5 Collapse \|\|                                                                                                    |
|                                                                                                                                                       |
| \| \| \|\|                                                                                                                                            |
|                                                                                                                                                       |
| \| \| RedFlag AI detected these warnings 18 MONTHS before crash: \|\|                                                                                 |
|                                                                                                                                                       |
| \| \| \|\|                                                                                                                                            |
|                                                                                                                                                       |
| \| \| FY2017 FY2018 FY2019 FY2020 \|\|                                                                                                                |
|                                                                                                                                                       |
| \| \| \| \| \| \| \|\|                                                                                                                                |
|                                                                                                                                                       |
| \| \| \*\-\-\-\-\-\-\-\-\-\-\-\--\*\-\-\-\-\-\-\-\-\-\-\-\-\--\*\-\-\-\-\-\-\-\-\-\-\-\-\--\* \|\|                                                    |
|                                                                                                                                                       |
| \| \| \| \| \| \| \|\|                                                                                                                                |
|                                                                                                                                                       |
| \| \| \[!\] RBI \[!!\] Auditor \[!!\] CEO \[XXX\] \|\|                                                                                                |
|                                                                                                                                                       |
| \| \| flags NPA qualified exits CRASH \|\|                                                                                                            |
|                                                                                                                                                       |
| \| \| divergence opinion -98.8% \|\|                                                                                                                  |
|                                                                                                                                                       |
| \| \| \|\|                                                                                                                                            |
|                                                                                                                                                       |
| \| +\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\--+\|    |
|                                                                                                                                                       |
| \| \|                                                                                                                                                 |
|                                                                                                                                                       |
| \| More cases: \[DHFL\] \[Zee\] \[Vakrangee\] \[PC Jeweller\] \[Satyam\] \[View All\] \|                                                              |
|                                                                                                                                                       |
| \| \|                                                                                                                                                 |
|                                                                                                                                                       |
| +\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\--+ |
+-------------------------------------------------------------------------------------------------------------------------------------------------------+

+-------------------------------------------------------------------------------------------------------------------------------------------------------+
| **LANDING PAGE - PRICING SECTION**                                                                                                                    |
+=======================================================================================================================================================+
| +\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\--+ |
|                                                                                                                                                       |
| \| SIMPLE, TRANSPARENT PRICING \|                                                                                                                     |
|                                                                                                                                                       |
| +\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\--+ |
|                                                                                                                                                       |
| \| \|                                                                                                                                                 |
|                                                                                                                                                       |
| \| +\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\--+ +\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\--+ +\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\--+\|              |
|                                                                                                                                                       |
| \| \| FREE \| \| PRO \| \| PREMIUM \|\|                                                                                                               |
|                                                                                                                                                       |
| \| \| \| \| \| \| \|\|                                                                                                                                |
|                                                                                                                                                       |
| \| \| Rs. 0 \| \| Rs. 599/month \| \| Rs. 1,499/month \|\|                                                                                            |
|                                                                                                                                                       |
| \| \| \| \| \| \| \|\|                                                                                                                                |
|                                                                                                                                                       |
| \| \| \* 3 reports/month \| \| \* 15 reports/month \| \| \* 50 reports/month \|\|                                                                     |
|                                                                                                                                                       |
| \| \| \* NIFTY 500 only \| \| \* Any company \| \| \* Any company \|\|                                                                                |
|                                                                                                                                                       |
| \| \| \* Risk score \| \| \* Full red flag \| \| \* Portfolio scanner \|\|                                                                            |
|                                                                                                                                                       |
| \| \| \* Basic summary \| \| details \| \| \* API access \|\|                                                                                         |
|                                                                                                                                                       |
| \| \| \| \| \* Page references \| \| \* Real-time alerts \|\|                                                                                         |
|                                                                                                                                                       |
| \| \| \| \| \* 2-year trends \| \| \* 5-year trends \|\|                                                                                              |
|                                                                                                                                                       |
| \| \| \| \| \* Peer comparison \| \| \* Priority support \|\|                                                                                         |
|                                                                                                                                                       |
| \| \| \| \| \* Watchlist (10) \| \| \* Watchlist (50) \|\|                                                                                            |
|                                                                                                                                                       |
| \| \| \| \| \| \| \|\|                                                                                                                                |
|                                                                                                                                                       |
| \| \| \[Get Started\] \| \| \[Start Pro\] \| \| \[Go Premium\] \|\|                                                                                   |
|                                                                                                                                                       |
| \| +\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\--+ +\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\--+ +\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\--+\|              |
|                                                                                                                                                       |
| \| \|                                                                                                                                                 |
|                                                                                                                                                       |
| \| All plans include: Fraud database access \|                                                                                                        |
|                                                                                                                                                       |
| \| \|                                                                                                                                                 |
|                                                                                                                                                       |
| +\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\--+ |
+-------------------------------------------------------------------------------------------------------------------------------------------------------+

**Landing Page Implementation**

- Framework: Next.js static page with Incremental Static Regeneration

- Animations: Framer Motion for scroll animations, counter animations

- Demo: Live embedded sample analysis (pre-computed, no API call)

- Analytics: PostHog for scroll depth, CTA clicks, pricing hover

- A/B Testing: Hero copy variants, CTA button colors

**Page 2: Login / Signup**

**URL:** /auth, /auth/login, /auth/signup, /auth/forgot-password

**Purpose:** User authentication with minimal friction

+-------------------------------------------------------------------------------------------------------------------------------------------------------+
| **LOGIN PAGE**                                                                                                                                        |
+=======================================================================================================================================================+
| +\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\--+ |
|                                                                                                                                                       |
| \| \|                                                                                                                                                 |
|                                                                                                                                                       |
| \| \[RedFlag Logo\] \|                                                                                                                                |
|                                                                                                                                                       |
| \| \|                                                                                                                                                 |
|                                                                                                                                                       |
| \| \|                                                                                                                                                 |
|                                                                                                                                                       |
| \| +\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\--+ \|                                                                               |
|                                                                                                                                                       |
| \| \| \| \|                                                                                                                                           |
|                                                                                                                                                       |
| \| \| Welcome Back \| \|                                                                                                                              |
|                                                                                                                                                       |
| \| \| \| \|                                                                                                                                           |
|                                                                                                                                                       |
| \| \| +\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\--+ \| \|                                                                                         |
|                                                                                                                                                       |
| \| \| \| \[G\] Continue with \| \| \|                                                                                                                 |
|                                                                                                                                                       |
| \| \| \| Google \| \| \|                                                                                                                              |
|                                                                                                                                                       |
| \| \| +\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\--+ \| \|                                                                                         |
|                                                                                                                                                       |
| \| \| \| \|                                                                                                                                           |
|                                                                                                                                                       |
| \| \| \-\-\-\-\-\-\-\-\-- OR \-\-\-\-\-\-\-\-\-- \| \|                                                                                                |
|                                                                                                                                                       |
| \| \| \| \|                                                                                                                                           |
|                                                                                                                                                       |
| \| \| Email \| \|                                                                                                                                     |
|                                                                                                                                                       |
| \| \| +\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\--+ \| \|                                                                                         |
|                                                                                                                                                       |
| \| \| \| name@example.com \| \| \|                                                                                                                    |
|                                                                                                                                                       |
| \| \| +\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\--+ \| \|                                                                                         |
|                                                                                                                                                       |
| \| \| \| \|                                                                                                                                           |
|                                                                                                                                                       |
| \| \| Password \| \|                                                                                                                                  |
|                                                                                                                                                       |
| \| \| +\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\--+ \| \|                                                                                         |
|                                                                                                                                                       |
| \| \| \| \*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\* \| \| \|                                                                                                |
|                                                                                                                                                       |
| \| \| +\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\--+ \| \|                                                                                         |
|                                                                                                                                                       |
| \| \| \| \|                                                                                                                                           |
|                                                                                                                                                       |
| \| \| \[ \] Remember me \| \|                                                                                                                         |
|                                                                                                                                                       |
| \| \| \| \|                                                                                                                                           |
|                                                                                                                                                       |
| \| \| +\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\--+ \| \|                                                                                         |
|                                                                                                                                                       |
| \| \| \| Sign In \| \| \|                                                                                                                             |
|                                                                                                                                                       |
| \| \| +\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\--+ \| \|                                                                                         |
|                                                                                                                                                       |
| \| \| \| \|                                                                                                                                           |
|                                                                                                                                                       |
| \| \| Forgot password? \| \|                                                                                                                          |
|                                                                                                                                                       |
| \| \| \| \|                                                                                                                                           |
|                                                                                                                                                       |
| \| \| \-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-- \| \|                                                                                         |
|                                                                                                                                                       |
| \| \| \| \|                                                                                                                                           |
|                                                                                                                                                       |
| \| \| Don\'t have an account? \| \|                                                                                                                   |
|                                                                                                                                                       |
| \| \| \[Sign up free\] \| \|                                                                                                                          |
|                                                                                                                                                       |
| \| \| \| \|                                                                                                                                           |
|                                                                                                                                                       |
| \| +\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\--+ \|                                                                               |
|                                                                                                                                                       |
| \| \|                                                                                                                                                 |
|                                                                                                                                                       |
| +\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\--+ |
+-------------------------------------------------------------------------------------------------------------------------------------------------------+

+-------------------------------------------------------------------------------------------------------------------------------------------------------+
| **SIGNUP PAGE**                                                                                                                                       |
+=======================================================================================================================================================+
| +\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\--+ |
|                                                                                                                                                       |
| \| \|                                                                                                                                                 |
|                                                                                                                                                       |
| \| \[RedFlag Logo\] \|                                                                                                                                |
|                                                                                                                                                       |
| \| \|                                                                                                                                                 |
|                                                                                                                                                       |
| \| +\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\--+ \|                                                                               |
|                                                                                                                                                       |
| \| \| \| \|                                                                                                                                           |
|                                                                                                                                                       |
| \| \| Create Your Account \| \|                                                                                                                       |
|                                                                                                                                                       |
| \| \| Start analyzing for free \| \|                                                                                                                  |
|                                                                                                                                                       |
| \| \| \| \|                                                                                                                                           |
|                                                                                                                                                       |
| \| \| +\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\--+ \| \|                                                                                         |
|                                                                                                                                                       |
| \| \| \| \[G\] Continue with \| \| \|                                                                                                                 |
|                                                                                                                                                       |
| \| \| \| Google \| \| \|                                                                                                                              |
|                                                                                                                                                       |
| \| \| +\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\--+ \| \|                                                                                         |
|                                                                                                                                                       |
| \| \| \| \|                                                                                                                                           |
|                                                                                                                                                       |
| \| \| \-\-\-\-\-\-\-\-\-- OR \-\-\-\-\-\-\-\-\-- \| \|                                                                                                |
|                                                                                                                                                       |
| \| \| \| \|                                                                                                                                           |
|                                                                                                                                                       |
| \| \| Full Name \| \|                                                                                                                                 |
|                                                                                                                                                       |
| \| \| +\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\--+ \| \|                                                                                         |
|                                                                                                                                                       |
| \| \| \| Manthan Patel \| \| \|                                                                                                                       |
|                                                                                                                                                       |
| \| \| +\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\--+ \| \|                                                                                         |
|                                                                                                                                                       |
| \| \| \| \|                                                                                                                                           |
|                                                                                                                                                       |
| \| \| Email \| \|                                                                                                                                     |
|                                                                                                                                                       |
| \| \| +\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\--+ \| \|                                                                                         |
|                                                                                                                                                       |
| \| \| \| manthan@example.com \| \| \|                                                                                                                 |
|                                                                                                                                                       |
| \| \| +\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\--+ \| \|                                                                                         |
|                                                                                                                                                       |
| \| \| \| \|                                                                                                                                           |
|                                                                                                                                                       |
| \| \| Password \| \|                                                                                                                                  |
|                                                                                                                                                       |
| \| \| +\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\--+ \| \|                                                                                         |
|                                                                                                                                                       |
| \| \| \| \*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\* \| \| \|                                                                                                |
|                                                                                                                                                       |
| \| \| +\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\--+ \| \|                                                                                         |
|                                                                                                                                                       |
| \| \| Min 8 chars, 1 number \| \|                                                                                                                     |
|                                                                                                                                                       |
| \| \| \| \|                                                                                                                                           |
|                                                                                                                                                       |
| \| \| \[ \] I agree to Terms of \| \|                                                                                                                 |
|                                                                                                                                                       |
| \| \| Service & Privacy Policy \| \|                                                                                                                  |
|                                                                                                                                                       |
| \| \| \| \|                                                                                                                                           |
|                                                                                                                                                       |
| \| \| +\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\--+ \| \|                                                                                         |
|                                                                                                                                                       |
| \| \| \| Create Account \| \| \|                                                                                                                      |
|                                                                                                                                                       |
| \| \| +\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\--+ \| \|                                                                                         |
|                                                                                                                                                       |
| \| \| \| \|                                                                                                                                           |
|                                                                                                                                                       |
| \| \| Already have account? \| \|                                                                                                                     |
|                                                                                                                                                       |
| \| \| \[Sign in\] \| \|                                                                                                                               |
|                                                                                                                                                       |
| \| \| \| \|                                                                                                                                           |
|                                                                                                                                                       |
| \| +\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\--+ \|                                                                               |
|                                                                                                                                                       |
| \| \|                                                                                                                                                 |
|                                                                                                                                                       |
| +\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\--+ |
+-------------------------------------------------------------------------------------------------------------------------------------------------------+

**Auth Implementation**

- Provider: Supabase Auth (email + Google OAuth)

- Session: JWT in httpOnly cookie, 7-day expiry

- Email verification required for email signups

- Password reset via email link (24-hour expiry)

**Page 4: New Analysis**

**URL:** /analyze

**Purpose:** Start a new analysis by uploading PDF or searching company

+-------------------------------------------------------------------------------------------------------------------------------------------------------+
| **NEW ANALYSIS PAGE**                                                                                                                                 |
+=======================================================================================================================================================+
| +\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\--+ |
|                                                                                                                                                       |
| \| \[Logo\] Dashboard \[Analyze\] Watchlist Portfolio \[User\] \|                                                                                     |
|                                                                                                                                                       |
| +\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\--+ |
|                                                                                                                                                       |
| \| \|                                                                                                                                                 |
|                                                                                                                                                       |
| \| ANALYZE ANNUAL REPORT \|                                                                                                                           |
|                                                                                                                                                       |
| \| \|                                                                                                                                                 |
|                                                                                                                                                       |
| +\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\--+ |
|                                                                                                                                                       |
| \| \|                                                                                                                                                 |
|                                                                                                                                                       |
| \| OPTION 1: SEARCH BY COMPANY \|                                                                                                                     |
|                                                                                                                                                       |
| +\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\--+ |
|                                                                                                                                                       |
| \| +\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\--+ \|   |
|                                                                                                                                                       |
| \| \| \[Q\] Search by company name, BSE code, or NSE symbol\... \| \|                                                                                 |
|                                                                                                                                                       |
| \| +\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\--+ \|   |
|                                                                                                                                                       |
| \| \|                                                                                                                                                 |
|                                                                                                                                                       |
| \| Popular searches: \|                                                                                                                               |
|                                                                                                                                                       |
| \| \[Reliance\] \[TCS\] \[HDFC Bank\] \[Infosys\] \[ICICI\] \[Tata Motors\] \[Wipro\] \|                                                              |
|                                                                                                                                                       |
| \| \|                                                                                                                                                 |
|                                                                                                                                                       |
| +\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\--+ |
|                                                                                                                                                       |
| \| \|                                                                                                                                                 |
|                                                                                                                                                       |
| \| OPTION 2: UPLOAD ANNUAL REPORT PDF \|                                                                                                              |
|                                                                                                                                                       |
| +\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\--+ |
|                                                                                                                                                       |
| \| +\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\--+ \|   |
|                                                                                                                                                       |
| \| \| \| \|                                                                                                                                           |
|                                                                                                                                                       |
| \| \| +\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\--+ \| \|                                                                                       |
|                                                                                                                                                       |
| \| \| \| \| \| \|                                                                                                                                     |
|                                                                                                                                                       |
| \| \| \| \[ PDF Icon \] \| \| \|                                                                                                                      |
|                                                                                                                                                       |
| \| \| \| \| \| \|                                                                                                                                     |
|                                                                                                                                                       |
| \| \| \| Drop PDF here \| \| \|                                                                                                                       |
|                                                                                                                                                       |
| \| \| \| or click to browse \| \| \|                                                                                                                  |
|                                                                                                                                                       |
| \| \| \| \| \| \|                                                                                                                                     |
|                                                                                                                                                       |
| \| \| +\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\--+ \| \|                                                                                       |
|                                                                                                                                                       |
| \| \| \| \|                                                                                                                                           |
|                                                                                                                                                       |
| \| \| Supported: PDF files up to 100MB \| \|                                                                                                          |
|                                                                                                                                                       |
| \| \| Best results with official ARs from BSE/NSE \| \|                                                                                               |
|                                                                                                                                                       |
| \| \| \| \|                                                                                                                                           |
|                                                                                                                                                       |
| \| +\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\--+ \|   |
|                                                                                                                                                       |
| \| \|                                                                                                                                                 |
|                                                                                                                                                       |
| +\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\--+ |
|                                                                                                                                                       |
| \| \|                                                                                                                                                 |
|                                                                                                                                                       |
| \| ANALYSIS OPTIONS \|                                                                                                                                |
|                                                                                                                                                       |
| +\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\--+ |
|                                                                                                                                                       |
| \| \| \| \|                                                                                                                                           |
|                                                                                                                                                       |
| \| \| \[x\] Include multi-year trend analysis (3 years) \[Pro Feature\] \| \|                                                                         |
|                                                                                                                                                       |
| \| \| \| \|                                                                                                                                           |
|                                                                                                                                                       |
| \| \| \[x\] Compare with industry peers (5 companies) \[Pro Feature\] \| \|                                                                           |
|                                                                                                                                                       |
| \| \| \| \|                                                                                                                                           |
|                                                                                                                                                       |
| \| \| \[ \] Deep forensic analysis (extended 80+ checks) \[Premium\] \| \|                                                                            |
|                                                                                                                                                       |
| \| \| \| \|                                                                                                                                           |
|                                                                                                                                                       |
| +\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\--+ |
|                                                                                                                                                       |
| \| \|                                                                                                                                                 |
|                                                                                                                                                       |
| \| +\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\--+ \|                                                                                         |
|                                                                                                                                                       |
| \| \| Start Analysis \| \|                                                                                                                            |
|                                                                                                                                                       |
| \| +\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\--+ \|                                                                                         |
|                                                                                                                                                       |
| \| \|                                                                                                                                                 |
|                                                                                                                                                       |
| +\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\--+ |
+-------------------------------------------------------------------------------------------------------------------------------------------------------+

+-------------------------------------------------------------------------------------------------------------------------------------------------------+
| **SEARCH AUTOCOMPLETE DROPDOWN**                                                                                                                      |
+=======================================================================================================================================================+
| +\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\--+ |
|                                                                                                                                                       |
| \| \[Q\] Zee ent \|                                                                                                                                   |
|                                                                                                                                                       |
| +\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\--+ |
|                                                                                                                                                       |
| \| +\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\--+ \|   |
|                                                                                                                                                       |
| \| \| \| \|                                                                                                                                           |
|                                                                                                                                                       |
| \| \| Zee Entertainment Enterprises Ltd \| \|                                                                                                         |
|                                                                                                                                                       |
| \| \| BSE: 505537 \| NSE: ZEEL \| Media & Entertainment \| \|                                                                                         |
|                                                                                                                                                       |
| \| \| \[Instant\] FY2024, FY2023, FY2022 available \| \|                                                                                              |
|                                                                                                                                                       |
| \| \| \| \|                                                                                                                                           |
|                                                                                                                                                       |
| \| +\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\--+ \|   |
|                                                                                                                                                       |
| \| \| \| \|                                                                                                                                           |
|                                                                                                                                                       |
| \| \| Zee Media Corporation Ltd \| \|                                                                                                                 |
|                                                                                                                                                       |
| \| \| BSE: 532794 \| NSE: ZEEMEDIA \| Media \| \|                                                                                                     |
|                                                                                                                                                       |
| \| \| \[Instant\] FY2024, FY2023 available \| \|                                                                                                      |
|                                                                                                                                                       |
| \| \| \| \|                                                                                                                                           |
|                                                                                                                                                       |
| \| +\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\--+ \|   |
|                                                                                                                                                       |
| \| \| \| \|                                                                                                                                           |
|                                                                                                                                                       |
| \| \| Zee Learn Ltd \| \|                                                                                                                             |
|                                                                                                                                                       |
| \| \| BSE: 533287 \| NSE: ZEELEARN \| Education \| \|                                                                                                 |
|                                                                                                                                                       |
| \| \| \[Fresh Analysis\] \~60 seconds \| \|                                                                                                           |
|                                                                                                                                                       |
| \| \| \| \|                                                                                                                                           |
|                                                                                                                                                       |
| \| +\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\--+ \|   |
|                                                                                                                                                       |
| +\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\--+ |
+-------------------------------------------------------------------------------------------------------------------------------------------------------+

+-------------------------------------------------------------------------------------------------------------------------------------------------------+
| **PROCESSING STATE**                                                                                                                                  |
+=======================================================================================================================================================+
| +\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\--+ |
|                                                                                                                                                       |
| \| \|                                                                                                                                                 |
|                                                                                                                                                       |
| \| Analyzing: Zee Entertainment \|                                                                                                                    |
|                                                                                                                                                       |
| \| FY 2023-24 Annual Report \|                                                                                                                        |
|                                                                                                                                                       |
| \| \|                                                                                                                                                 |
|                                                                                                                                                       |
| \| +\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\--+ \|                                                       |
|                                                                                                                                                       |
| \| \|████████████████████░░░░░░░░░░░░░░░░░░░░░░░░\| 45% \|                                                                                            |
|                                                                                                                                                       |
| \| +\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\--+ \|                                                       |
|                                                                                                                                                       |
| \| \|                                                                                                                                                 |
|                                                                                                                                                       |
| \| \[✓\] Extracting text from PDF \|                                                                                                                  |
|                                                                                                                                                       |
| \| \[✓\] Detecting sections \|                                                                                                                        |
|                                                                                                                                                       |
| \| \[\>\] Analyzing auditor report\... \|                                                                                                             |
|                                                                                                                                                       |
| \| \[ \] Extracting financial data \|                                                                                                                 |
|                                                                                                                                                       |
| \| \[ \] Checking red flags \|                                                                                                                        |
|                                                                                                                                                       |
| \| \[ \] Generating report \|                                                                                                                         |
|                                                                                                                                                       |
| \| \|                                                                                                                                                 |
|                                                                                                                                                       |
| \| Estimated time: 45 seconds \|                                                                                                                      |
|                                                                                                                                                       |
| \| \|                                                                                                                                                 |
|                                                                                                                                                       |
| +\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\--+ |
+-------------------------------------------------------------------------------------------------------------------------------------------------------+

**Page 6: Red Flag Detail**

**URL:** /report/\[id\]/flag/\[flagId\]

**Purpose:** Deep dive into a specific red flag with full evidence and
context

+-------------------------------------------------------------------------------------------------------------------------------------------------------+
| **RED FLAG DETAIL PAGE**                                                                                                                              |
+=======================================================================================================================================================+
| +\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\--+ |
|                                                                                                                                                       |
| \| \[\<- Back to Report\] Zee Entertainment - FY2024 \|                                                                                               |
|                                                                                                                                                       |
| +\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\--+ |
|                                                                                                                                                       |
| \| \|                                                                                                                                                 |
|                                                                                                                                                       |
| \| +\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\--+ \|   |
|                                                                                                                                                       |
| \| \| \[!!\] CRITICAL RED FLAG \| \|                                                                                                                  |
|                                                                                                                                                       |
| \| \| \| \|                                                                                                                                           |
|                                                                                                                                                       |
| \| \| PROMOTER PLEDGE EXCEEDS 50% \| \|                                                                                                               |
|                                                                                                                                                       |
| \| +\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\--+ \|   |
|                                                                                                                                                       |
| \| \|                                                                                                                                                 |
|                                                                                                                                                       |
| +\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\--+ |
|                                                                                                                                                       |
| \| WHAT THIS MEANS \|                                                                                                                                 |
|                                                                                                                                                       |
| +\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\--+ |
|                                                                                                                                                       |
| \| +\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\--+ \|   |
|                                                                                                                                                       |
| \| \| When promoters pledge more than 50% of their shares as collateral \| \|                                                                         |
|                                                                                                                                                       |
| \| \| for loans, it indicates significant financial stress at the promoter \| \|                                                                      |
|                                                                                                                                                       |
| \| \| level. If stock price falls, lenders may force-sell shares in open \| \|                                                                        |
|                                                                                                                                                       |
| \| \| market (margin call), causing further price decline - a dangerous \| \|                                                                         |
|                                                                                                                                                       |
| \| \| downward spiral that can crash the stock. \| \|                                                                                                 |
|                                                                                                                                                       |
| \| +\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\--+ \|   |
|                                                                                                                                                       |
| \| \|                                                                                                                                                 |
|                                                                                                                                                       |
| +\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\--+ |
|                                                                                                                                                       |
| \| CURRENT SITUATION \|                                                                                                                               |
|                                                                                                                                                       |
| +\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\--+ |
|                                                                                                                                                       |
| \| +\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\--+ \|   |
|                                                                                                                                                       |
| \| \| Promoter Name \| Shares Held \| Pledged \| Pledge % \| \|                                                                                       |
|                                                                                                                                                       |
| \| \|\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\--+\-\-\-\-\-\-\-\-\-\-\-\--+\-\-\-\-\-\-\-\-\-\-\-\--+\-\-\-\-\-\-\-\-\--\| \|         |
|                                                                                                                                                       |
| \| \| Essel Holdings Pvt Ltd \| 18.2 Cr \| 11.3 Cr \| 62.1% \| \|                                                                                     |
|                                                                                                                                                       |
| \| \| Cyquator Media Services \| 4.5 Cr \| 2.8 Cr \| 62.2% \| \|                                                                                      |
|                                                                                                                                                       |
| \| \| Other Promoter Entities \| 2.1 Cr \| 1.3 Cr \| 61.9% \| \|                                                                                      |
|                                                                                                                                                       |
| \| \|\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\--+\-\-\-\-\-\-\-\-\-\-\-\--+\-\-\-\-\-\-\-\-\-\-\-\--+\-\-\-\-\-\-\-\-\--\| \|         |
|                                                                                                                                                       |
| \| \| TOTAL PROMOTER HOLDING \| 24.8 Cr \| 15.4 Cr \| 62.1% \| \|                                                                                     |
|                                                                                                                                                       |
| \| +\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\--+ \|   |
|                                                                                                                                                       |
| \| \|                                                                                                                                                 |
|                                                                                                                                                       |
| +\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\--+ |
|                                                                                                                                                       |
| \| EVIDENCE FROM ANNUAL REPORT \|                                                                                                                     |
|                                                                                                                                                       |
| +\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\--+ |
|                                                                                                                                                       |
| \| +\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\--+ \|   |
|                                                                                                                                                       |
| \| \| Source: Shareholding Pattern (Page 127) \| \|                                                                                                   |
|                                                                                                                                                       |
| \| \| \| \|                                                                                                                                           |
|                                                                                                                                                       |
| \| \| \"As on 31st March 2024, 15,42,34,567 equity shares representing \| \|                                                                          |
|                                                                                                                                                       |
| \| \| 62.1% of the total promoter and promoter group shareholding have \| \|                                                                          |
|                                                                                                                                                       |
| \| \| been pledged with various lenders against borrowing facilities \| \|                                                                            |
|                                                                                                                                                       |
| \| \| availed by promoter group entities.\" \| \|                                                                                                     |
|                                                                                                                                                       |
| \| \| \| \|                                                                                                                                           |
|                                                                                                                                                       |
| \| \| \[View in PDF - Page 127\] \| \|                                                                                                                |
|                                                                                                                                                       |
| \| +\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\--+ \|   |
|                                                                                                                                                       |
| \| \|                                                                                                                                                 |
|                                                                                                                                                       |
| +\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\--+ |
|                                                                                                                                                       |
| \| HISTORICAL TREND \|                                                                                                                                |
|                                                                                                                                                       |
| +\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\--+ |
|                                                                                                                                                       |
| \| +\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\--+ \|   |
|                                                                                                                                                       |
| \| \| % \| \|                                                                                                                                         |
|                                                                                                                                                       |
| \| \| 70\| \*\-\-\-\-\--\* 62% \| \|                                                                                                                  |
|                                                                                                                                                       |
| \| \| 60\| \*\-\-\-\-\--\*\-\-\--\* \| \|                                                                                                             |
|                                                                                                                                                       |
| \| \| 50\| \*\-\-\-\-\-\-\--\* DANGER ZONE \| \|                                                                                                      |
|                                                                                                                                                       |
| \| \| 40\| \*\-\-\-\-\-\-\--\* \-\-\-\-\-\-\-\-\-\-- \| \|                                                                                            |
|                                                                                                                                                       |
| \| \| 30\| \*\-\-\-\--\* \| \|                                                                                                                        |
|                                                                                                                                                       |
| \| \| 20\| \| \|                                                                                                                                      |
|                                                                                                                                                       |
| \| \| +\-\-\--+\-\-\-\-\--+\-\-\-\-\--+\-\-\-\-\--+\-\-\-\-\--+\-\-\-\-\--+\-\-\-\-\--+\-\-\-\-\--+ \| \|                                             |
|                                                                                                                                                       |
| \| \| FY17 FY18 FY19 FY20 FY21 FY22 FY23 FY24 \| \|                                                                                                   |
|                                                                                                                                                       |
| \| \| \| \|                                                                                                                                           |
|                                                                                                                                                       |
| \| \| Pledge increased from 25% (FY2017) to 62% (FY2024) = +148% \| \|                                                                                |
|                                                                                                                                                       |
| \| \| Crossed 50% danger threshold in FY2021 \| \|                                                                                                    |
|                                                                                                                                                       |
| \| +\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\--+ \|   |
|                                                                                                                                                       |
| \| \|                                                                                                                                                 |
|                                                                                                                                                       |
| +\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\--+ |
|                                                                                                                                                       |
| \| PEER COMPARISON \|                                                                                                                                 |
|                                                                                                                                                       |
| +\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\--+ |
|                                                                                                                                                       |
| \| +\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\--+ \|   |
|                                                                                                                                                       |
| \| \| Company \| Promoter Pledge % \| Status \| \|                                                                                                    |
|                                                                                                                                                       |
| \| \|\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\--+\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\--+\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\--\| \|     |
|                                                                                                                                                       |
| \| \| Sun TV Network \| 0% \| No pledge - Excellent \| \|                                                                                             |
|                                                                                                                                                       |
| \| \| TV18 Broadcast \| 12% \| Low - Good \| \|                                                                                                       |
|                                                                                                                                                       |
| \| \| Network18 Media \| 8% \| Low - Good \| \|                                                                                                       |
|                                                                                                                                                       |
| \| \| Zee Entertainment \| 62% \| \[!!\] CRITICAL \| \|                                                                                               |
|                                                                                                                                                       |
| \| \| Dish TV India \| 78% \| \[!!\] CRITICAL \| \|                                                                                                   |
|                                                                                                                                                       |
| \| +\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\--+ \|   |
|                                                                                                                                                       |
| \| \|                                                                                                                                                 |
|                                                                                                                                                       |
| +\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\--+ |
|                                                                                                                                                       |
| \| HISTORICAL FRAUD PATTERN MATCH \|                                                                                                                  |
|                                                                                                                                                       |
| +\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\--+ |
|                                                                                                                                                       |
| \| +\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\--+ \|   |
|                                                                                                                                                       |
| \| \| \[!\] WARNING: This pattern was seen before major crashes: \| \|                                                                                |
|                                                                                                                                                       |
| \| \| \| \|                                                                                                                                           |
|                                                                                                                                                       |
| \| \| \* DHFL (2018): Promoter pledge reached 78% -\> Collapsed 2019 \| \|                                                                            |
|                                                                                                                                                       |
| \| \| \* Vakrangee (2017): Pledge at 65% -\> Stock crashed 85% in 2018 \| \|                                                                          |
|                                                                                                                                                       |
| \| \| \* Manpasand (2018): Pledge at 58% -\> Fraud discovered 2019 \| \|                                                                              |
|                                                                                                                                                       |
| \| \| \| \|                                                                                                                                           |
|                                                                                                                                                       |
| \| \| \[View Full Case Studies\] \| \|                                                                                                                |
|                                                                                                                                                       |
| \| +\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\--+ \|   |
|                                                                                                                                                       |
| +\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\--+ |
+-------------------------------------------------------------------------------------------------------------------------------------------------------+

**Page 7: Trend Analysis**

**URL:** /report/\[id\]/trends

**Purpose:** View multi-year trends in risk score and key metrics

**Access:** Pro and Premium users only

+-------------------------------------------------------------------------------------------------------------------------------------------------------+
| **TREND ANALYSIS PAGE**                                                                                                                               |
+=======================================================================================================================================================+
| +\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\--+ |
|                                                                                                                                                       |
| \| \[\<- Back\] TREND ANALYSIS: Zee Entertainment (5-Year View) \|                                                                                    |
|                                                                                                                                                       |
| +\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\--+ |
|                                                                                                                                                       |
| \| \|                                                                                                                                                 |
|                                                                                                                                                       |
| +\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\--+ |
|                                                                                                                                                       |
| \| RISK SCORE EVOLUTION \|                                                                                                                            |
|                                                                                                                                                       |
| +\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\--+ |
|                                                                                                                                                       |
| \| +\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\--+ \|   |
|                                                                                                                                                       |
| \| \| Score \| \|                                                                                                                                     |
|                                                                                                                                                       |
| \| \| 80 \| \*\-\-\-\-\--\* 67 \| \|                                                                                                                  |
|                                                                                                                                                       |
| \| \| \| \*\-\-\-\-\-\--\* \| \|                                                                                                                      |
|                                                                                                                                                       |
| \| \| 60 \| \*\-\-\-\-\-\-\--\* \| \|                                                                                                                 |
|                                                                                                                                                       |
| \| \| \| \*\-\-\-\-\-\-\--\* \| \|                                                                                                                    |
|                                                                                                                                                       |
| \| \| 40 \| \*\-\-\-\-\-\-\--\* \| \|                                                                                                                 |
|                                                                                                                                                       |
| \| \| \| \*\-\-\--\* \| \|                                                                                                                            |
|                                                                                                                                                       |
| \| \| 20 \| 28 \| \|                                                                                                                                  |
|                                                                                                                                                       |
| \| \| +\-\-\-\--+\-\-\-\-\-\-\--+\-\-\-\-\-\-\--+\-\-\-\-\-\-\--+\-\-\-\-\-\-\--+ \| \|                                                               |
|                                                                                                                                                       |
| \| \| FY20 FY21 FY22 FY23 FY24 \| \|                                                                                                                  |
|                                                                                                                                                       |
| \| \| \| \|                                                                                                                                           |
|                                                                                                                                                       |
| \| \| \[!!\] Risk score increased 139% over 5 years (28 -\> 67) \| \|                                                                                 |
|                                                                                                                                                       |
| \| +\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\--+ \|   |
|                                                                                                                                                       |
| \| \|                                                                                                                                                 |
|                                                                                                                                                       |
| +\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\--+ |
|                                                                                                                                                       |
| \| KEY EVENTS TIMELINE \|                                                                                                                             |
|                                                                                                                                                       |
| +\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\--+ |
|                                                                                                                                                       |
| \| +\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\--+ \|   |
|                                                                                                                                                       |
| \| \| \| \|                                                                                                                                           |
|                                                                                                                                                       |
| \| \| FY2020 FY2021 FY2022 FY2023 FY2024 \| \|                                                                                                        |
|                                                                                                                                                       |
| \| \| \| \| \| \| \| \| \|                                                                                                                            |
|                                                                                                                                                       |
| \| \| \*\-\-\-\-\-\-\-\-\-\-\--\*\-\-\-\-\-\-\-\-\-\-\--\*\-\-\-\-\-\-\-\-\-\-\--\*\-\-\-\-\-\-\-\-\-\-\--\* \| \|                                    |
|                                                                                                                                                       |
| \| \| \| \| \| \| \| \| \|                                                                                                                            |
|                                                                                                                                                       |
| \| \| Normal \[!\] \[!\] \[!!\] \[!!\] \| \|                                                                                                          |
|                                                                                                                                                       |
| \| \| Auditor CFO Qualified Promoter \| \|                                                                                                            |
|                                                                                                                                                       |
| \| \| Changed Resigned Opinion Pledge 62% \| \|                                                                                                       |
|                                                                                                                                                       |
| \| \| \| \|                                                                                                                                           |
|                                                                                                                                                       |
| \| +\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\--+ \|   |
|                                                                                                                                                       |
| \| \|                                                                                                                                                 |
|                                                                                                                                                       |
| +\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\--+ |
|                                                                                                                                                       |
| \| KEY METRICS TRENDS \|                                                                                                                              |
|                                                                                                                                                       |
| +\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\--+ |
|                                                                                                                                                       |
| \| \|                                                                                                                                                 |
|                                                                                                                                                       |
| \| +\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\--+ +\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\--+ \|                 |
|                                                                                                                                                       |
| \| \| PROMOTER PLEDGE % \| \| CFO/PAT RATIO \| \|                                                                                                     |
|                                                                                                                                                       |
| \| \| \| \| \| \|                                                                                                                                     |
|                                                                                                                                                       |
| \| \| 70\| \*\-\-\--\* \| \| 1.0\| \* \| \|                                                                                                           |
|                                                                                                                                                       |
| \| \| 60\| \*\-\-\--\* \| \| 0.8\| \\ \| \|                                                                                                           |
|                                                                                                                                                       |
| \| \| 50\| \*\-\-\--\* DANGER \| \| 0.6\| \*\-\-\--\* \| \|                                                                                           |
|                                                                                                                                                       |
| \| \| 40\| \-\-\-\-\-\-- \| \| 0.4\| \\ \| \|                                                                                                         |
|                                                                                                                                                       |
| \| \| 30\| \| \| 0.2\| \*\-\-\--\* DANGER \| \|                                                                                                       |
|                                                                                                                                                       |
| \| \| +-+\-\-\--+\-\-\--+\-\-\--+\-\-\--+ \| \| +-+\-\-\--+\-\-\--+\-\-\--+\-\-\--+ \| \|                                                             |
|                                                                                                                                                       |
| \| \| 20 21 22 23 24 \| \| 20 21 22 23 24 \| \|                                                                                                       |
|                                                                                                                                                       |
| \| \| \| \| \| \|                                                                                                                                     |
|                                                                                                                                                       |
| \| \| \[!!\] 32% -\> 62% (+94%) \| \| \[!!\] 0.95 -\> 0.25 (-74%) \| \|                                                                               |
|                                                                                                                                                       |
| \| +\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\--+ +\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\--+ \|                 |
|                                                                                                                                                       |
| \| \|                                                                                                                                                 |
|                                                                                                                                                       |
| \| +\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\--+ +\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\--+ \|                 |
|                                                                                                                                                       |
| \| \| RECEIVABLE DAYS \| \| DEBT/EQUITY RATIO \| \|                                                                                                   |
|                                                                                                                                                       |
| \| \| \| \| \| \|                                                                                                                                     |
|                                                                                                                                                       |
| \| \| 120\| \*\-\-\--\* \| \| 1.8\| \*\-\-\--\* \| \|                                                                                                 |
|                                                                                                                                                       |
| \| \| 100\| \*\-\-\--\* \| \| 1.5\| \*\-\-\--\* \| \|                                                                                                 |
|                                                                                                                                                       |
| \| \| 80\| \*\-\-\--\* \| \| 1.2\| \*\-\-\--\* \| \|                                                                                                  |
|                                                                                                                                                       |
| \| \| 60\| \| \| 0.9\| \| \|                                                                                                                          |
|                                                                                                                                                       |
| \| \| +-+\-\-\--+\-\-\--+\-\-\--+\-\-\--+ \| \| +-+\-\-\--+\-\-\--+\-\-\--+\-\-\--+ \| \|                                                             |
|                                                                                                                                                       |
| \| \| 20 21 22 23 24 \| \| 20 21 22 23 24 \| \|                                                                                                       |
|                                                                                                                                                       |
| \| \| \| \| \| \|                                                                                                                                     |
|                                                                                                                                                       |
| \| \| \[!\] 68 -\> 98 days (+44%) \| \| \[!\] 0.9 -\> 1.5 (+67%) \| \|                                                                                |
|                                                                                                                                                       |
| \| +\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\--+ +\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\--+ \|                 |
|                                                                                                                                                       |
| \| \|                                                                                                                                                 |
|                                                                                                                                                       |
| +\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\--+ |
+-------------------------------------------------------------------------------------------------------------------------------------------------------+

**Page 8: Peer Comparison**

**URL:** /report/\[id\]/peers

**Purpose:** Compare company with industry peers for context

**Access:** Pro (3 peers) and Premium (10 peers)

+-------------------------------------------------------------------------------------------------------------------------------------------------------+
| **PEER COMPARISON PAGE**                                                                                                                              |
+=======================================================================================================================================================+
| +\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\--+ |
|                                                                                                                                                       |
| \| \[\<- Back\] PEER COMPARISON: Zee Entertainment vs Media Sector \|                                                                                 |
|                                                                                                                                                       |
| +\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\--+ |
|                                                                                                                                                       |
| \| \|                                                                                                                                                 |
|                                                                                                                                                       |
| +\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\--+ |
|                                                                                                                                                       |
| \| RISK SCORE COMPARISON \|                                                                                                                           |
|                                                                                                                                                       |
| +\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\--+ |
|                                                                                                                                                       |
| \| +\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\--+ \|   |
|                                                                                                                                                       |
| \| \| \| \|                                                                                                                                           |
|                                                                                                                                                       |
| \| \| Sun TV Network ████████████░░░░░░░░░░░░░░░░░░░ 28 BEST \| \|                                                                                    |
|                                                                                                                                                       |
| \| \| \| \|                                                                                                                                           |
|                                                                                                                                                       |
| \| \| TV18 Broadcast ██████████████████░░░░░░░░░░░░░ 42 \| \|                                                                                         |
|                                                                                                                                                       |
| \| \| \| \|                                                                                                                                           |
|                                                                                                                                                       |
| \| \| INDUSTRY AVERAGE ███████████████████░░░░░░░░░░░░ 45 \-\-- \| \|                                                                                 |
|                                                                                                                                                       |
| \| \| \| \|                                                                                                                                           |
|                                                                                                                                                       |
| \| \| Network18 Media █████████████████████░░░░░░░░░░ 51 \| \|                                                                                        |
|                                                                                                                                                       |
| \| \| \| \|                                                                                                                                           |
|                                                                                                                                                       |
| \| \| \[\*\] Zee Entertainment ████████████████████████████░░░ 67 YOU \| \|                                                                           |
|                                                                                                                                                       |
| \| \| \| \|                                                                                                                                           |
|                                                                                                                                                       |
| \| \| Dish TV India ██████████████████████████████░ 73 WORST \| \|                                                                                    |
|                                                                                                                                                       |
| \| \| \| \|                                                                                                                                           |
|                                                                                                                                                       |
| \| \| 0 25 50 75 100 \| \|                                                                                                                            |
|                                                                                                                                                       |
| \| +\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\--+ \|   |
|                                                                                                                                                       |
| \| \|                                                                                                                                                 |
|                                                                                                                                                       |
| +\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\--+ |
|                                                                                                                                                       |
| \| DETAILED METRIC COMPARISON \|                                                                                                                      |
|                                                                                                                                                       |
| +\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\--+ |
|                                                                                                                                                       |
| \| +\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\--+ \|   |
|                                                                                                                                                       |
| \| \| Metric \| Zee \| Industry \| Best \| Rank \| Status \| \|                                                                                       |
|                                                                                                                                                       |
| \| \| \| \| Average \| Peer \| \| \| \|                                                                                                               |
|                                                                                                                                                       |
| \| \|\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\--+\-\-\-\-\--+\-\-\-\-\-\-\-\-\--+\-\-\-\-\-\-\-\--+\-\-\-\-\-\--+\-\-\-\-\-\-\-\--\| \|             |
|                                                                                                                                                       |
| \| \| Promoter Pledge % \| 62% \| 20% \| 0% \| 5/5 \| \[!!\] \| \|                                                                                    |
|                                                                                                                                                       |
| \| \| CFO/PAT Ratio \| 0.25 \| 0.72 \| 0.92 \| 5/5 \| \[!!\] \| \|                                                                                    |
|                                                                                                                                                       |
| \| \| Receivable Days \| 98 \| 65 \| 45 \| 4/5 \| \[!\] \| \|                                                                                         |
|                                                                                                                                                       |
| \| \| Debt/Equity Ratio \| 1.5 \| 0.8 \| 0.3 \| 4/5 \| \[!\] \| \|                                                                                    |
|                                                                                                                                                       |
| \| \| RPT % of Revenue \| 14% \| 6% \| 2% \| 5/5 \| \[!\] \| \|                                                                                       |
|                                                                                                                                                       |
| \| \| Interest Coverage \| 2.1x \| 4.5x \| 8.2x \| 4/5 \| \[!\] \| \|                                                                                 |
|                                                                                                                                                       |
| \| \| Inventory Days \| 12 \| 15 \| 8 \| 2/5 \| OK \| \|                                                                                              |
|                                                                                                                                                       |
| \| \| Auditor Type \| Big4 \| - \| - \| - \| OK \| \|                                                                                                 |
|                                                                                                                                                       |
| \| +\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\--+ \|   |
|                                                                                                                                                       |
| \| \|                                                                                                                                                 |
|                                                                                                                                                       |
| +\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\--+ |
|                                                                                                                                                       |
| \| CATEGORY-WISE COMPARISON \|                                                                                                                        |
|                                                                                                                                                       |
| +\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\--+ |
|                                                                                                                                                       |
| \| +\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\--+ \|   |
|                                                                                                                                                       |
| \| \| \| \|                                                                                                                                           |
|                                                                                                                                                       |
| \| \| Category \| Zee Score \| Industry Avg \| Peer Range \| Rank \| \|                                                                               |
|                                                                                                                                                       |
| \| \|\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\--+\-\-\-\-\-\-\-\-\-\--+\-\-\-\-\-\-\-\-\-\-\-\-\--+\-\-\-\-\-\-\-\-\-\-\-\--+\-\-\-\-\-\-\--\| \|           |
|                                                                                                                                                       |
| \| \| Auditor \| 45 \| 25 \| 15-45 \| 5/5 \| \|                                                                                                       |
|                                                                                                                                                       |
| \| \| Cash Flow \| 72 \| 35 \| 20-72 \| 5/5 \| \|                                                                                                     |
|                                                                                                                                                       |
| \| \| Related Party \| 58 \| 30 \| 18-58 \| 5/5 \| \|                                                                                                 |
|                                                                                                                                                       |
| \| \| Promoter \| 85 \| 25 \| 10-85 \| 5/5 \| \|                                                                                                      |
|                                                                                                                                                       |
| \| \| Governance \| 35 \| 28 \| 18-42 \| 3/5 \| \|                                                                                                    |
|                                                                                                                                                       |
| \| \| Balance Sheet \| 28 \| 22 \| 15-35 \| 3/5 \| \|                                                                                                 |
|                                                                                                                                                       |
| \| \| \| \|                                                                                                                                           |
|                                                                                                                                                       |
| \| +\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\--+ \|   |
|                                                                                                                                                       |
| \| \|                                                                                                                                                 |
|                                                                                                                                                       |
| \| \[Download Comparison Report as PDF\] \|                                                                                                           |
|                                                                                                                                                       |
| +\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\--+ |
+-------------------------------------------------------------------------------------------------------------------------------------------------------+

**Page 9: Portfolio Scanner**

**URL:** /portfolio

**Purpose:** Scan all holdings at once, identify positions needing
attention

**Access:** Premium users only

+-------------------------------------------------------------------------------------------------------------------------------------------------------+
| **PORTFOLIO SCANNER - UPLOAD STATE**                                                                                                                  |
+=======================================================================================================================================================+
| +\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\--+ |
|                                                                                                                                                       |
| \| \[Logo\] Dashboard Analyze Watchlist \[Portfolio\] \[User\] \|                                                                                     |
|                                                                                                                                                       |
| +\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\--+ |
|                                                                                                                                                       |
| \| \|                                                                                                                                                 |
|                                                                                                                                                       |
| \| PORTFOLIO RISK SCANNER \|                                                                                                                          |
|                                                                                                                                                       |
| \| \[Premium\] \|                                                                                                                                     |
|                                                                                                                                                       |
| +\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\--+ |
|                                                                                                                                                       |
| \| \|                                                                                                                                                 |
|                                                                                                                                                       |
| \| IMPORT YOUR HOLDINGS \|                                                                                                                            |
|                                                                                                                                                       |
| +\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\--+ |
|                                                                                                                                                       |
| \| +\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\--+ \|   |
|                                                                                                                                                       |
| \| \| \| \|                                                                                                                                           |
|                                                                                                                                                       |
| \| \| +\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\--+ +\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\--+ +\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\--+ \| \|                         |
|                                                                                                                                                       |
| \| \| \| \| \| \| \| \| \| \|                                                                                                                         |
|                                                                                                                                                       |
| \| \| \| \[Upload CSV\] \| \| \[Connect API\] \| \| \[Add Manually\] \| \| \|                                                                         |
|                                                                                                                                                       |
| \| \| \| \| \| \| \| \| \| \|                                                                                                                         |
|                                                                                                                                                       |
| \| \| \| Upload holdings \| \| Connect broker \| \| Enter stocks \| \| \|                                                                             |
|                                                                                                                                                       |
| \| \| \| CSV from broker \| \| API (coming) \| \| one by one \| \| \|                                                                                 |
|                                                                                                                                                       |
| \| \| +\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\--+ +\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\--+ +\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\--+ \| \|                         |
|                                                                                                                                                       |
| \| \| \| \|                                                                                                                                           |
|                                                                                                                                                       |
| \| \| Supported CSV formats: \| \|                                                                                                                    |
|                                                                                                                                                       |
| \| \| \[Zerodha\] \[Groww\] \[Upstox\] \[Angel One\] \[ICICI Direct\] \| \|                                                                           |
|                                                                                                                                                       |
| \| \| \| \|                                                                                                                                           |
|                                                                                                                                                       |
| \| +\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\--+ \|   |
|                                                                                                                                                       |
| \| \|                                                                                                                                                 |
|                                                                                                                                                       |
| +\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\--+ |
+-------------------------------------------------------------------------------------------------------------------------------------------------------+

+-------------------------------------------------------------------------------------------------------------------------------------------------------+
| **PORTFOLIO SCANNER - RESULTS**                                                                                                                       |
+=======================================================================================================================================================+
| +\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\--+ |
|                                                                                                                                                       |
| \| PORTFOLIO RISK OVERVIEW \|                                                                                                                         |
|                                                                                                                                                       |
| +\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\--+ |
|                                                                                                                                                       |
| \| \|                                                                                                                                                 |
|                                                                                                                                                       |
| \| Total Holdings: 15 companies Portfolio Value: Rs. 24,50,000 \|                                                                                     |
|                                                                                                                                                       |
| \| \|                                                                                                                                                 |
|                                                                                                                                                       |
| \| +\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\--+ +\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\--+ \|           |
|                                                                                                                                                       |
| \| \| RISK DISTRIBUTION \| \| \| \|                                                                                                                   |
|                                                                                                                                                       |
| \| \| \| \| \[████████████████░░░░░░░░░░░░░░░░░░░░░░░░\] \| \|                                                                                        |
|                                                                                                                                                       |
| \| \| Low Risk: 9 \| \| 60% Low 27% Medium 13% High \| \|                                                                                             |
|                                                                                                                                                       |
| \| \| Medium Risk: 4 \| \| \| \|                                                                                                                      |
|                                                                                                                                                       |
| \| \| High Risk: 2 \| \| \| \|                                                                                                                        |
|                                                                                                                                                       |
| \| +\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\--+ +\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\--+ \|           |
|                                                                                                                                                       |
| \| \|                                                                                                                                                 |
|                                                                                                                                                       |
| +\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\--+ |
|                                                                                                                                                       |
| \| HOLDINGS RISK HEATMAP \[List View\] \|                                                                                                             |
|                                                                                                                                                       |
| +\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\--+ |
|                                                                                                                                                       |
| \| +\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\--+ \|   |
|                                                                                                                                                       |
| \| \| +\-\-\-\-\-\-\--+\-\-\-\-\-\-\--+\-\-\-\-\-\-\--+\-\-\-\-\-\-\--+\-\-\-\-\-\-\--+\-\-\-\-\-\-\--+\-\-\-\-\-\-\--+ \| \|                         |
|                                                                                                                                                       |
| \| \| \| HDFC \| INFY \| TCS \| REL \| ICICI \| AXIS \| SBI \| \| \|                                                                                  |
|                                                                                                                                                       |
| \| \| \| 22 \| 18 \| 25 \| 28 \| 24 \| 35 \| 21 \| \| \|                                                                                              |
|                                                                                                                                                       |
| \| \| \| \[OK\] \| \[OK\] \| \[OK\] \| \[OK\] \| \[OK\] \| \[!\] \| \[OK\] \| \| \|                                                                   |
|                                                                                                                                                       |
| \| \| +\-\-\-\-\-\-\--+\-\-\-\-\-\-\--+\-\-\-\-\-\-\--+\-\-\-\-\-\-\--+\-\-\-\-\-\-\--+\-\-\-\-\-\-\--+\-\-\-\-\-\-\--+ \| \|                         |
|                                                                                                                                                       |
| \| \| \| WIPRO \| HCL \| TECHM \| L&T \| ZEE \| ADANI \| ITC \| \| \|                                                                                 |
|                                                                                                                                                       |
| \| \| \| 21 \| 19 \| 27 \| 24 \| 67 \| 58 \| 20 \| \| \|                                                                                              |
|                                                                                                                                                       |
| \| \| \| \[OK\] \| \[OK\] \| \[OK\] \| \[OK\] \| \[!!\] \| \[!\] \| \[OK\] \| \| \|                                                                   |
|                                                                                                                                                       |
| \| \| +\-\-\-\-\-\-\--+\-\-\-\-\-\-\--+\-\-\-\-\-\-\--+\-\-\-\-\-\-\--+\-\-\-\-\-\-\--+\-\-\-\-\-\-\--+\-\-\-\-\-\-\--+ \| \|                         |
|                                                                                                                                                       |
| \| \| \| KOTAK \| \| \|                                                                                                                               |
|                                                                                                                                                       |
| \| \| \| 23 \| Click any tile for detailed analysis \| \|                                                                                             |
|                                                                                                                                                       |
| \| \| \| \[OK\] \| \| \|                                                                                                                              |
|                                                                                                                                                       |
| \| \| +\-\-\-\-\-\-\--+ \| \|                                                                                                                         |
|                                                                                                                                                       |
| \| +\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\--+ \|   |
|                                                                                                                                                       |
| \| \|                                                                                                                                                 |
|                                                                                                                                                       |
| +\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\--+ |
|                                                                                                                                                       |
| \| PRIORITY ALERTS \|                                                                                                                                 |
|                                                                                                                                                       |
| +\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\--+ |
|                                                                                                                                                       |
| \| +\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\--+ \|   |
|                                                                                                                                                       |
| \| \| \| \|                                                                                                                                           |
|                                                                                                                                                       |
| \| \| \[!!\] ZEE ENTERTAINMENT - Risk Score: 67 (ELEVATED) \| \|                                                                                      |
|                                                                                                                                                       |
| \| \| 12 red flags triggered including: Promoter pledge 62%, \| \|                                                                                    |
|                                                                                                                                                       |
| \| \| Cash flow divergence, Complex group structure \| \|                                                                                             |
|                                                                                                                                                       |
| \| \| \[View Full Analysis\] \| \|                                                                                                                    |
|                                                                                                                                                       |
| \| \| \| \|                                                                                                                                           |
|                                                                                                                                                       |
| \| \| \[!\] ADANI ENTERPRISES - Risk Score: 58 (MODERATE-HIGH) \| \|                                                                                  |
|                                                                                                                                                       |
| \| \| 8 red flags triggered including: Rapid debt growth, \| \|                                                                                       |
|                                                                                                                                                       |
| \| \| Complex corporate structure, High RPT \| \|                                                                                                     |
|                                                                                                                                                       |
| \| \| \[View Full Analysis\] \| \|                                                                                                                    |
|                                                                                                                                                       |
| \| \| \| \|                                                                                                                                           |
|                                                                                                                                                       |
| \| \| \[!\] AXIS BANK - Risk Score: 35 (MODERATE) \| \|                                                                                               |
|                                                                                                                                                       |
| \| \| 3 red flags triggered: CFO concerns, Contingent liabilities \| \|                                                                               |
|                                                                                                                                                       |
| \| \| \[View Full Analysis\] \| \|                                                                                                                    |
|                                                                                                                                                       |
| \| \| \| \|                                                                                                                                           |
|                                                                                                                                                       |
| \| +\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\--+ \|   |
|                                                                                                                                                       |
| \| \|                                                                                                                                                 |
|                                                                                                                                                       |
| \| \[Download Portfolio Report PDF\] \[Re-scan All Holdings\] \|                                                                                      |
|                                                                                                                                                       |
| +\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\--+ |
+-------------------------------------------------------------------------------------------------------------------------------------------------------+

**Page 10: Watchlist**

**URL:** /watchlist

**Purpose:** Track companies over time, receive alerts on changes

**Access:** Pro (10 companies) and Premium (50 companies)

+-------------------------------------------------------------------------------------------------------------------------------------------------------+
| **WATCHLIST PAGE**                                                                                                                                    |
+=======================================================================================================================================================+
| +\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\--+ |
|                                                                                                                                                       |
| \| \[Logo\] Dashboard Analyze \[Watchlist\] Portfolio \[User\] \|                                                                                     |
|                                                                                                                                                       |
| +\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\--+ |
|                                                                                                                                                       |
| \| \|                                                                                                                                                 |
|                                                                                                                                                       |
| \| MY WATCHLIST (8 companies) \[+ Add Company\] \|                                                                                                    |
|                                                                                                                                                       |
| \| \|                                                                                                                                                 |
|                                                                                                                                                       |
| +\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\--+ |
|                                                                                                                                                       |
| \| NEW ALERTS (3) \|                                                                                                                                  |
|                                                                                                                                                       |
| +\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\--+ |
|                                                                                                                                                       |
| \| +\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\--+ \|   |
|                                                                                                                                                       |
| \| \| \| \|                                                                                                                                           |
|                                                                                                                                                       |
| \| \| \[!!\] ZEE ENTERTAINMENT - 2 hours ago \[New\] \| \|                                                                                            |
|                                                                                                                                                       |
| \| \| Risk score changed: 58 -\> 67 (+9 points) \| \|                                                                                                 |
|                                                                                                                                                       |
| \| \| New critical flag: CFO/PAT ratio dropped to 0.25 \| \|                                                                                          |
|                                                                                                                                                       |
| \| \| \[View Analysis\] \[Dismiss\] \| \|                                                                                                             |
|                                                                                                                                                       |
| \| \| \| \|                                                                                                                                           |
|                                                                                                                                                       |
| \| \| \[!\] ADANI ENTERPRISES - Yesterday \[New\] \| \|                                                                                               |
|                                                                                                                                                       |
| \| \| Promoter pledge increased from 42% to 47% \| \|                                                                                                 |
|                                                                                                                                                       |
| \| \| \[View Analysis\] \[Dismiss\] \| \|                                                                                                             |
|                                                                                                                                                       |
| \| \| \| \|                                                                                                                                           |
|                                                                                                                                                       |
| \| \| \[i\] HDFC BANK - 3 days ago \[New\] \| \|                                                                                                      |
|                                                                                                                                                       |
| \| \| New Annual Report (FY2024) available \| \|                                                                                                      |
|                                                                                                                                                       |
| \| \| \[Analyze New AR\] \[Dismiss\] \| \|                                                                                                            |
|                                                                                                                                                       |
| \| \| \| \|                                                                                                                                           |
|                                                                                                                                                       |
| \| +\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\--+ \|   |
|                                                                                                                                                       |
| \| \|                                                                                                                                                 |
|                                                                                                                                                       |
| +\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\--+ |
|                                                                                                                                                       |
| \| WATCHED COMPANIES \|                                                                                                                               |
|                                                                                                                                                       |
| +\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\--+ |
|                                                                                                                                                       |
| \| +\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\--+ \|   |
|                                                                                                                                                       |
| \| \| Company \| Score \| Change \| Last Updated \| Alerts \| \|                                                                                      |
|                                                                                                                                                       |
| \| \|\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\--+\-\-\-\-\-\--+\-\-\-\-\-\-\--+\-\-\-\-\-\-\-\-\-\-\-\-\--+\-\-\-\-\-\-\-\-\-\-\-\-\--\| \|           |
|                                                                                                                                                       |
| \| \| Zee Entertainment \| 67 \| +9 \[!\] \| 2 hours ago \| \[Settings\] \| \|                                                                        |
|                                                                                                                                                       |
| \| \| Reliance Industries \| 28 \| -2 \| Yesterday \| \[Settings\] \| \|                                                                              |
|                                                                                                                                                       |
| \| \| HDFC Bank \| 22 \| +1 \| 3 days ago \| \[Settings\] \| \|                                                                                       |
|                                                                                                                                                       |
| \| \| Adani Enterprises \| 58 \| +5 \[!\] \| Yesterday \| \[Settings\] \| \|                                                                          |
|                                                                                                                                                       |
| \| \| TCS \| 18 \| 0 \| 1 week ago \| \[Settings\] \| \|                                                                                              |
|                                                                                                                                                       |
| \| \| Infosys \| 20 \| -1 \| 1 week ago \| \[Settings\] \| \|                                                                                         |
|                                                                                                                                                       |
| \| \| ICICI Bank \| 24 \| +2 \| 2 weeks ago \| \[Settings\] \| \|                                                                                     |
|                                                                                                                                                       |
| \| \| Axis Bank \| 35 \| +3 \| 2 weeks ago \| \[Settings\] \| \|                                                                                      |
|                                                                                                                                                       |
| \| +\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\--+ \|   |
|                                                                                                                                                       |
| \| \|                                                                                                                                                 |
|                                                                                                                                                       |
| +\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\--+ |
|                                                                                                                                                       |
| \| ALERT SETTINGS (per company) \[Global Cfg\] \|                                                                                                     |
|                                                                                                                                                       |
| +\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\--+ |
|                                                                                                                                                       |
| \| +\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\--+ \|   |
|                                                                                                                                                       |
| \| \| Zee Entertainment - Alert Configuration \| \|                                                                                                   |
|                                                                                                                                                       |
| \| \| \| \|                                                                                                                                           |
|                                                                                                                                                       |
| \| \| \[x\] Alert when new Annual Report is filed \| \|                                                                                               |
|                                                                                                                                                       |
| \| \| \[x\] Alert when risk score changes by more than: \[10\] points \| \|                                                                           |
|                                                                                                                                                       |
| \| \| \[x\] Alert when any CRITICAL red flag is triggered \| \|                                                                                       |
|                                                                                                                                                       |
| \| \| \[x\] Alert when promoter pledge exceeds: \[50\] % \| \|                                                                                        |
|                                                                                                                                                       |
| \| \| \[ \] Weekly summary email \| \|                                                                                                                |
|                                                                                                                                                       |
| \| \| \| \|                                                                                                                                           |
|                                                                                                                                                       |
| \| \| \[Save Settings\] \[Remove from Watchlist\] \| \|                                                                                               |
|                                                                                                                                                       |
| \| +\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\--+ \|   |
|                                                                                                                                                       |
| +\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\--+ |
+-------------------------------------------------------------------------------------------------------------------------------------------------------+

**Page 11: Fraud Database**

**URL:** /learn

**Purpose:** Learn from historical frauds, see patterns

**Access:** All users (Free feature)

+-------------------------------------------------------------------------------------------------------------------------------------------------------+
| **FRAUD DATABASE PAGE**                                                                                                                               |
+=======================================================================================================================================================+
| +\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\--+ |
|                                                                                                                                                       |
| \| \[Logo\] Dashboard Analyze Watchlist Portfolio \[User\] \|                                                                                         |
|                                                                                                                                                       |
| +\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\--+ |
|                                                                                                                                                       |
| \| \|                                                                                                                                                 |
|                                                                                                                                                       |
| \| LEARN FROM HISTORY: Indian Corporate Frauds Database \|                                                                                            |
|                                                                                                                                                       |
| \| 50+ documented cases with red flags visible BEFORE the crash \|                                                                                    |
|                                                                                                                                                       |
| \| \|                                                                                                                                                 |
|                                                                                                                                                       |
| +\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\--+ |
|                                                                                                                                                       |
| \| FEATURED CASE STUDY \|                                                                                                                             |
|                                                                                                                                                       |
| +\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\--+ |
|                                                                                                                                                       |
| \| +\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\--+ \|   |
|                                                                                                                                                       |
| \| \| \| \|                                                                                                                                           |
|                                                                                                                                                       |
| \| \| YES BANK: The Rs. 404 to Rs. 5 Collapse \| \|                                                                                                   |
|                                                                                                                                                       |
| \| \| \| \|                                                                                                                                           |
|                                                                                                                                                       |
| \| \| +\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\--+ +\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\--+ \| \|                         |
|                                                                                                                                                       |
| \| \| \| Stock Price \| \| Red Flags in AR BEFORE Crash \| \| \|                                                                                      |
|                                                                                                                                                       |
| \| \| \| \| \| \| \| \|                                                                                                                               |
|                                                                                                                                                       |
| \| \| \| 404 \* \| \| FY2017: \| \| \|                                                                                                                |
|                                                                                                                                                       |
| \| \| \| \\ \| \| \[!\] RBI flags NPA divergence \| \| \|                                                                                             |
|                                                                                                                                                       |
| \| \| \| \\ \| \| \| \| \|                                                                                                                            |
|                                                                                                                                                       |
| \| \| \| \*\-\--\* \| \| FY2018: \| \| \|                                                                                                             |
|                                                                                                                                                       |
| \| \| \| \\ \| \| \[!!\] Auditor qualified opinion\| \| \|                                                                                            |
|                                                                                                                                                       |
| \| \| \| \\ \| \| \[!\] RPT increased 40% \| \| \|                                                                                                    |
|                                                                                                                                                       |
| \| \| \| \* \| \| \| \| \|                                                                                                                            |
|                                                                                                                                                       |
| \| \| \| \\ \| \| FY2019: \| \| \|                                                                                                                    |
|                                                                                                                                                       |
| \| \| \| \\ \| \| \[!!\] CEO exits \| \| \|                                                                                                           |
|                                                                                                                                                       |
| \| \| \| \* 5 \| \| \[!\] Multiple board changes \| \| \|                                                                                             |
|                                                                                                                                                       |
| \| \| +\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\--+ +\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\--+ \| \|                         |
|                                                                                                                                                       |
| \| \| \| \|                                                                                                                                           |
|                                                                                                                                                       |
| \| \| Key Lesson: NPA divergence flagged by RBI 3 years before collapse. \| \|                                                                        |
|                                                                                                                                                       |
| \| \| Auditor qualified opinion was the clearest warning sign. \| \|                                                                                  |
|                                                                                                                                                       |
| \| \| \| \|                                                                                                                                           |
|                                                                                                                                                       |
| \| \| \[View Complete Case Study\] \| \|                                                                                                              |
|                                                                                                                                                       |
| \| \| \| \|                                                                                                                                           |
|                                                                                                                                                       |
| \| +\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\--+ \|   |
|                                                                                                                                                       |
| \| \|                                                                                                                                                 |
|                                                                                                                                                       |
| +\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\--+ |
|                                                                                                                                                       |
| \| ALL CASES \[Filter by Sector\] \|                                                                                                                  |
|                                                                                                                                                       |
| +\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\--+ |
|                                                                                                                                                       |
| \| +\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\--+ \|   |
|                                                                                                                                                       |
| \| \| Company \| Year \| Decline \| Primary Red Flags \| \|                                                                                           |
|                                                                                                                                                       |
| \| \|\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\--+\-\-\-\-\--+\-\-\-\-\-\-\-\--+\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\--\| \|         |
|                                                                                                                                                       |
| \| \| Yes Bank \| 2020 \| -98.8% \| NPA divergence, qualified audit \| \|                                                                             |
|                                                                                                                                                       |
| \| \| DHFL \| 2019 \| -98.0% \| RPT \>15%, promoter pledge 78% \| \|                                                                                  |
|                                                                                                                                                       |
| \| \| Zee Group \| 2019 \| -70.0% \| Promoter pledge 90%+ \| \|                                                                                       |
|                                                                                                                                                       |
| \| \| Vakrangee \| 2018 \| -85.0% \| Auditor resigned mid-term \| \|                                                                                  |
|                                                                                                                                                       |
| \| \| PC Jeweller \| 2018 \| -90.0% \| Inventory 180+ days, selling \| \|                                                                             |
|                                                                                                                                                       |
| \| \| Manpasand \| 2019 \| -75.0% \| Auditor resigned, RPT \| \|                                                                                      |
|                                                                                                                                                       |
| \| \| Gitanjali Gems \| 2018 \| -99.0% \| Inventory fraud, cash flow \| \|                                                                            |
|                                                                                                                                                       |
| \| \| Satyam \| 2009 \| -100% \| Cash fabrication, CFO divergence\| \|                                                                                |
|                                                                                                                                                       |
| \| \| \[View 42 more cases\...\] \| \|                                                                                                                |
|                                                                                                                                                       |
| \| +\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\--+ \|   |
|                                                                                                                                                       |
| \| \|                                                                                                                                                 |
|                                                                                                                                                       |
| +\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\--+ |
|                                                                                                                                                       |
| \| PATTERN MATCHING \|                                                                                                                                |
|                                                                                                                                                       |
| +\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\--+ |
|                                                                                                                                                       |
| \| +\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\--+ \|   |
|                                                                                                                                                       |
| \| \| \| \|                                                                                                                                           |
|                                                                                                                                                       |
| \| \| See if your stock matches historical fraud patterns: \| \|                                                                                      |
|                                                                                                                                                       |
| \| \| \| \|                                                                                                                                           |
|                                                                                                                                                       |
| \| \| +\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\--+ \| \|                                     |
|                                                                                                                                                       |
| \| \| \| \[Q\] Enter company name to check pattern match\... \| \| \|                                                                                 |
|                                                                                                                                                       |
| \| \| +\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\--+ \| \|                                     |
|                                                                                                                                                       |
| \| \| \| \|                                                                                                                                           |
|                                                                                                                                                       |
| \| +\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\--+ \|   |
|                                                                                                                                                       |
| +\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\--+ |
+-------------------------------------------------------------------------------------------------------------------------------------------------------+

**Page 12: Settings**

**URL:** /settings

**Purpose:** User profile, subscription management, preferences

+-------------------------------------------------------------------------------------------------------------------------------------------------------+
| **SETTINGS PAGE**                                                                                                                                     |
+=======================================================================================================================================================+
| +\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\--+ |
|                                                                                                                                                       |
| \| \[Logo\] Dashboard Analyze Watchlist Portfolio \[User\] \|                                                                                         |
|                                                                                                                                                       |
| +\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\--+ |
|                                                                                                                                                       |
| \| \|                                                                                                                                                 |
|                                                                                                                                                       |
| \| SETTINGS \|                                                                                                                                        |
|                                                                                                                                                       |
| \| \|                                                                                                                                                 |
|                                                                                                                                                       |
| +\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\--+ |
|                                                                                                                                                       |
| \| PROFILE \|                                                                                                                                         |
|                                                                                                                                                       |
| +\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\--+ |
|                                                                                                                                                       |
| \| +\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\--+ \|   |
|                                                                                                                                                       |
| \| \| \| \|                                                                                                                                           |
|                                                                                                                                                       |
| \| \| Name \| \|                                                                                                                                      |
|                                                                                                                                                       |
| \| \| +\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\--+ \| \|                                         |
|                                                                                                                                                       |
| \| \| \| Manthan Patel \| \[Edit\] \| \|                                                                                                              |
|                                                                                                                                                       |
| \| \| +\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\--+ \| \|                                         |
|                                                                                                                                                       |
| \| \| \| \|                                                                                                                                           |
|                                                                                                                                                       |
| \| \| Email \| \|                                                                                                                                     |
|                                                                                                                                                       |
| \| \| +\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\--+ \| \|                                         |
|                                                                                                                                                       |
| \| \| \| manthan@example.com \| \[Change\] \| \|                                                                                                      |
|                                                                                                                                                       |
| \| \| +\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\--+ \| \|                                         |
|                                                                                                                                                       |
| \| \| \| \|                                                                                                                                           |
|                                                                                                                                                       |
| \| \| Password \| \|                                                                                                                                  |
|                                                                                                                                                       |
| \| \| +\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\--+ \| \|                                         |
|                                                                                                                                                       |
| \| \| \| \*\*\*\*\*\*\*\* \| \[Change\] \| \|                                                                                                         |
|                                                                                                                                                       |
| \| \| +\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\--+ \| \|                                         |
|                                                                                                                                                       |
| \| \| \| \|                                                                                                                                           |
|                                                                                                                                                       |
| \| +\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\--+ \|   |
|                                                                                                                                                       |
| \| \|                                                                                                                                                 |
|                                                                                                                                                       |
| +\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\--+ |
|                                                                                                                                                       |
| \| SUBSCRIPTION \|                                                                                                                                    |
|                                                                                                                                                       |
| +\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\--+ |
|                                                                                                                                                       |
| \| +\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\--+ \|   |
|                                                                                                                                                       |
| \| \| \| \|                                                                                                                                           |
|                                                                                                                                                       |
| \| \| Current Plan: FREE \| \|                                                                                                                        |
|                                                                                                                                                       |
| \| \| \| \|                                                                                                                                           |
|                                                                                                                                                       |
| \| \| Reports Used: 2 / 3 this month \| \|                                                                                                            |
|                                                                                                                                                       |
| \| \| Resets On: March 1, 2026 \| \|                                                                                                                  |
|                                                                                                                                                       |
| \| \| \| \|                                                                                                                                           |
|                                                                                                                                                       |
| \| \| +\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\--+ +\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\--+ \| \|                       |
|                                                                                                                                                       |
| \| \| \| Upgrade to PRO \| \| Upgrade to PREMIUM \| \| \|                                                                                             |
|                                                                                                                                                       |
| \| \| \| Rs. 599/month \| \| Rs. 1,499/month \| \| \|                                                                                                 |
|                                                                                                                                                       |
| \| \| \| 15 reports, all features \| \| 50 reports, API, portfolio \| \| \|                                                                           |
|                                                                                                                                                       |
| \| \| \| \[Upgrade Now\] \| \| \[Upgrade Now\] \| \| \|                                                                                               |
|                                                                                                                                                       |
| \| \| +\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\--+ +\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\--+ \| \|                       |
|                                                                                                                                                       |
| \| \| \| \|                                                                                                                                           |
|                                                                                                                                                       |
| \| +\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\--+ \|   |
|                                                                                                                                                       |
| \| \|                                                                                                                                                 |
|                                                                                                                                                       |
| +\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\--+ |
|                                                                                                                                                       |
| \| NOTIFICATION PREFERENCES \|                                                                                                                        |
|                                                                                                                                                       |
| +\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\--+ |
|                                                                                                                                                       |
| \| +\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\--+ \|   |
|                                                                                                                                                       |
| \| \| \| \|                                                                                                                                           |
|                                                                                                                                                       |
| \| \| \[x\] Email alerts for watchlist changes \| \|                                                                                                  |
|                                                                                                                                                       |
| \| \| \[x\] Weekly digest of portfolio risk \| \|                                                                                                     |
|                                                                                                                                                       |
| \| \| \[ \] Push notifications (browser) \| \|                                                                                                        |
|                                                                                                                                                       |
| \| \| \[x\] New feature announcements \| \|                                                                                                           |
|                                                                                                                                                       |
| \| \| \| \|                                                                                                                                           |
|                                                                                                                                                       |
| \| \| \[Save Preferences\] \| \|                                                                                                                      |
|                                                                                                                                                       |
| \| \| \| \|                                                                                                                                           |
|                                                                                                                                                       |
| \| +\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\--+ \|   |
|                                                                                                                                                       |
| \| \|                                                                                                                                                 |
|                                                                                                                                                       |
| +\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\--+ |
|                                                                                                                                                       |
| \| DATA & PRIVACY \|                                                                                                                                  |
|                                                                                                                                                       |
| +\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\--+ |
|                                                                                                                                                       |
| \| +\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\--+ \|   |
|                                                                                                                                                       |
| \| \| \| \|                                                                                                                                           |
|                                                                                                                                                       |
| \| \| \[Download My Data\] \[Delete Analysis History\] \| \|                                                                                          |
|                                                                                                                                                       |
| \| \| \| \|                                                                                                                                           |
|                                                                                                                                                       |
| \| +\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\--+ \|   |
|                                                                                                                                                       |
| \| \|                                                                                                                                                 |
|                                                                                                                                                       |
| +\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\--+ |
|                                                                                                                                                       |
| \| DANGER ZONE \|                                                                                                                                     |
|                                                                                                                                                       |
| +\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\--+ |
|                                                                                                                                                       |
| \| +\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\--+ \|   |
|                                                                                                                                                       |
| \| \| \| \|                                                                                                                                           |
|                                                                                                                                                       |
| \| \| \[Delete My Account\] \| \|                                                                                                                     |
|                                                                                                                                                       |
| \| \| This action is permanent and cannot be undone. \| \|                                                                                            |
|                                                                                                                                                       |
| \| \| \| \|                                                                                                                                           |
|                                                                                                                                                       |
| \| +\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\--+ \|   |
|                                                                                                                                                       |
| +\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\--+ |
+-------------------------------------------------------------------------------------------------------------------------------------------------------+

**Mobile Responsive Designs**

All pages are responsive. Here are key mobile wireframes (375px width).

+-----------------------------------------------------------------------+
| **MOBILE: LANDING PAGE**                                              |
+=======================================================================+
| +\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\--+ |
|                                                                       |
| \| \[=\] RedFlag AI \[Sign Up\] \|                                    |
|                                                                       |
| +\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\--+ |
|                                                                       |
| \| \|                                                                 |
|                                                                       |
| \| YOUR AI FORENSIC \|                                                |
|                                                                       |
| \| ACCOUNTANT \|                                                      |
|                                                                       |
| \| \|                                                                 |
|                                                                       |
| \| Detect hidden risks in \|                                          |
|                                                                       |
| \| annual reports before \|                                           |
|                                                                       |
| \| they become headlines \|                                           |
|                                                                       |
| \| \|                                                                 |
|                                                                       |
| \| +\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\--+ \|       |
|                                                                       |
| \| \| Analyze Free Now \| \|                                          |
|                                                                       |
| \| +\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\--+ \|       |
|                                                                       |
| \| \|                                                                 |
|                                                                       |
| \| \[54 Flags\] \[60 Sec\] \[10K Users\]\|                            |
|                                                                       |
| \| \|                                                                 |
|                                                                       |
| +\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\--+ |
|                                                                       |
| \| \|                                                                 |
|                                                                       |
| \| SAMPLE ANALYSIS \|                                                 |
|                                                                       |
| \| +\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\--+ \|                 |
|                                                                       |
| \| \| 67 \| \|                                                        |
|                                                                       |
| \| \| ELEVATED RISK \| \|                                             |
|                                                                       |
| \| +\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\--+ \|                 |
|                                                                       |
| \| \|                                                                 |
|                                                                       |
| \| \[!!\] Promoter Pledge 62% \|                                      |
|                                                                       |
| \| \[!!\] Cash Flow Divergence \|                                     |
|                                                                       |
| \| \[!\] Related Party \> 10% \|                                      |
|                                                                       |
| \| \|                                                                 |
|                                                                       |
| +\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\--+ |
+-----------------------------------------------------------------------+

+-----------------------------------------------------------------------+
| **MOBILE: NEW ANALYSIS**                                              |
+=======================================================================+
| +\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\--+ |
|                                                                       |
| \| \[\<\] Analyze \|                                                  |
|                                                                       |
| +\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\--+ |
|                                                                       |
| \| \|                                                                 |
|                                                                       |
| \| SEARCH COMPANY \|                                                  |
|                                                                       |
| \| +\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\--+ \|       |
|                                                                       |
| \| \| \[Q\] Search name or code\... \| \|                             |
|                                                                       |
| \| +\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\--+ \|       |
|                                                                       |
| \| \|                                                                 |
|                                                                       |
| \| Popular: \|                                                        |
|                                                                       |
| \| \[Reliance\] \[TCS\] \[HDFC\] \|                                   |
|                                                                       |
| \| \[Infosys\] \[ICICI\] \|                                           |
|                                                                       |
| \| \|                                                                 |
|                                                                       |
| +\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\--+ |
|                                                                       |
| \| \|                                                                 |
|                                                                       |
| \| OR UPLOAD PDF \|                                                   |
|                                                                       |
| \| +\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\--+ \|       |
|                                                                       |
| \| \| \| \|                                                           |
|                                                                       |
| \| \| \[ PDF Icon \] \| \|                                            |
|                                                                       |
| \| \| \| \|                                                           |
|                                                                       |
| \| \| Tap to upload \| \|                                             |
|                                                                       |
| \| \| annual report \| \|                                             |
|                                                                       |
| \| \| \| \|                                                           |
|                                                                       |
| \| +\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\--+ \|       |
|                                                                       |
| \| \|                                                                 |
|                                                                       |
| \| \[x\] Multi-year trends \[Pro\] \|                                 |
|                                                                       |
| \| \[x\] Peer comparison \[Pro\] \|                                   |
|                                                                       |
| \| \|                                                                 |
|                                                                       |
| \| +\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\--+ \|       |
|                                                                       |
| \| \| Start Analysis \| \|                                            |
|                                                                       |
| \| +\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\--+ \|       |
|                                                                       |
| \| \|                                                                 |
|                                                                       |
| +\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\--+ |
|                                                                       |
| \| \[Home\] \[Search\] \[+\] \[Watch\] \[Me\]\|                       |
|                                                                       |
| +\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\--+ |
+-----------------------------------------------------------------------+

+-----------------------------------------------------------------------+
| **MOBILE: PORTFOLIO SCANNER**                                         |
+=======================================================================+
| +\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\--+ |
|                                                                       |
| \| \[\<\] Portfolio \[Premium\]\|                                     |
|                                                                       |
| +\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\--+ |
|                                                                       |
| \| \|                                                                 |
|                                                                       |
| \| Holdings: 15 \|                                                    |
|                                                                       |
| \| Value: Rs. 24,50,000 \|                                            |
|                                                                       |
| \| \|                                                                 |
|                                                                       |
| \| +\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\--+ \|       |
|                                                                       |
| \| \| Low: 9 Med: 4 High: 2 \| \|                                     |
|                                                                       |
| \| +\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\--+ \|       |
|                                                                       |
| \| \|                                                                 |
|                                                                       |
| \| RISK HEATMAP \|                                                    |
|                                                                       |
| \| +\-\-\-\-\--+\-\-\-\-\--+\-\-\-\-\--+\-\-\-\-\--+ \|               |
|                                                                       |
| \| \| HDFC \| INFY \| TCS \| REL \| \|                                |
|                                                                       |
| \| \| 22 \| 18 \| 25 \| 28 \| \|                                      |
|                                                                       |
| \| +\-\-\-\-\--+\-\-\-\-\--+\-\-\-\-\--+\-\-\-\-\--+ \|               |
|                                                                       |
| \| \| ICIC \| AXIS \| SBI \| ZEE \| \|                                |
|                                                                       |
| \| \| 24 \| 35 \| 21 \| 67! \| \|                                     |
|                                                                       |
| \| +\-\-\-\-\--+\-\-\-\-\--+\-\-\-\-\--+\-\-\-\-\--+ \|               |
|                                                                       |
| \| \|                                                                 |
|                                                                       |
| \| ALERTS \|                                                          |
|                                                                       |
| \| +\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\--+ \|       |
|                                                                       |
| \| \| \[!!\] ZEE - Score 67 \| \|                                     |
|                                                                       |
| \| \| 12 red flags \[View\] \| \|                                     |
|                                                                       |
| \| +\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\--+ \|       |
|                                                                       |
| \| \| \[!\] ADANI - Score 58 \| \|                                    |
|                                                                       |
| \| \| 8 red flags \[View\] \| \|                                      |
|                                                                       |
| \| +\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\--+ \|       |
|                                                                       |
| \| \|                                                                 |
|                                                                       |
| +\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\--+ |
|                                                                       |
| \| \[Home\] \[Search\] \[+\] \[Watch\] \[Me\]\|                       |
|                                                                       |
| +\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\--+ |
+-----------------------------------------------------------------------+

+-----------------------------------------------------------------------+
| **MOBILE: WATCHLIST**                                                 |
+=======================================================================+
| +\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\--+ |
|                                                                       |
| \| \[\<\] Watchlist (8) \[+ Add\] \|                                  |
|                                                                       |
| +\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\--+ |
|                                                                       |
| \| \|                                                                 |
|                                                                       |
| \| NEW ALERTS \|                                                      |
|                                                                       |
| \| +\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\--+ \|       |
|                                                                       |
| \| \| \[!!\] ZEE \| \|                                                |
|                                                                       |
| \| \| Risk: 58 -\> 67 (+9) \| \|                                      |
|                                                                       |
| \| \| 2 hours ago \| \|                                               |
|                                                                       |
| \| +\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\--+ \|       |
|                                                                       |
| \| \| \[!\] ADANI \| \|                                               |
|                                                                       |
| \| \| Pledge +5% \| \|                                                |
|                                                                       |
| \| \| Yesterday \| \|                                                 |
|                                                                       |
| \| +\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\--+ \|       |
|                                                                       |
| \| \|                                                                 |
|                                                                       |
| \| WATCHED \|                                                         |
|                                                                       |
| \| +\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\--+ \|       |
|                                                                       |
| \| \| Zee Entertainment 67 ! \| \|                                    |
|                                                                       |
| \| +\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\--+ \|       |
|                                                                       |
| \| \| Reliance 28 \| \|                                               |
|                                                                       |
| \| +\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\--+ \|       |
|                                                                       |
| \| \| HDFC Bank 22 \| \|                                              |
|                                                                       |
| \| +\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\--+ \|       |
|                                                                       |
| \| \| Adani Ent 58 ! \| \|                                            |
|                                                                       |
| \| +\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\--+ \|       |
|                                                                       |
| \| \| TCS 18 \| \|                                                    |
|                                                                       |
| \| +\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\--+ \|       |
|                                                                       |
| \| \|                                                                 |
|                                                                       |
| +\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\--+ |
|                                                                       |
| \| \[Home\] \[Search\] \[+\] \[Watch\] \[Me\]\|                       |
|                                                                       |
| +\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\--+ |
+-----------------------------------------------------------------------+

**All 12 Pages Complete**

This supplement includes wireframes for:

Page 1: Landing Page (Hero, Demo, Features, Pricing)

Page 2: Login / Signup

Page 4: New Analysis (Search, Upload, Processing)

Page 6: Red Flag Detail (Evidence, Trend, Peers)

Page 7: Trend Analysis (5-Year View)

Page 8: Peer Comparison

Page 9: Portfolio Scanner

Page 10: Watchlist

Page 11: Fraud Database

Page 12: Settings

Mobile Responsive Designs (4 screens)

**PART C: TECHNICAL ARCHITECTURE**

**5. System Architecture**

+----------------------------------------------------------------------+
| CLIENTS (Web/Mobile/API)                                             |
|                                                                      |
| \|                                                                   |
|                                                                      |
| v                                                                    |
|                                                                      |
| CLOUDFLARE CDN -\> VERCEL (Next.js SSR)                              |
|                                                                      |
| \|                                                                   |
|                                                                      |
| v                                                                    |
|                                                                      |
| API GATEWAY (Railway)                                                |
|                                                                      |
| \|                                                                   |
|                                                                      |
| +\-\-\-\-\-\-\--+\-\-\-\-\-\-\--+                                    |
|                                                                      |
| \| \| \|                                                             |
|                                                                      |
| v v v                                                                |
|                                                                      |
| MAIN API WORKERS WEBHOOKS                                            |
|                                                                      |
| (FastAPI) (Celery) (Razorpay/BSE)                                    |
|                                                                      |
| \|                                                                   |
|                                                                      |
| v                                                                    |
|                                                                      |
| +\-\-\-\-\-\-\--+\-\-\-\-\-\-\--+\-\-\-\-\-\-\--+                    |
|                                                                      |
| \| \| \| \|                                                          |
|                                                                      |
| v v v v                                                              |
|                                                                      |
| Postgres Redis R2 LLM APIs                                           |
|                                                                      |
| (Supabase)(Upstash)(Storage)(Claude/Gemini)                          |
+======================================================================+

**6. LLM-Based PDF Processing**

Indian annual reports have unreliable Table of Contents. Our pipeline
uses intelligent LLM-based section detection instead of regex patterns.

+----------------------------------------------------------------------+
| **Why NOT Regex?**                                                   |
|                                                                      |
| Indian ARs have: (1) Inconsistent naming (\'Director Report\' vs     |
| \'Board Report\'), (2) Mixed Hindi/English, (3) OCR artifacts, (4)   |
| Creative formatting. LLM understands context.                        |
+======================================================================+

**Processing Pipeline**

+----------------------------------------------------------------------+
| STEP 1: TEXT EXTRACTION Cost: Rs.0-15                                |
|                                                                      |
| \- PyMuPDF for native PDF (60% of pages) - FREE                      |
|                                                                      |
| \- Surya OCR for scanned pages (40%) - FREE + GPU                    |
|                                                                      |
| \- Google Vision fallback (\<10%) - Rs.0.12/page                     |
|                                                                      |
| STEP 2: LLM SECTION DETECTION Cost: Rs.3-5                           |
|                                                                      |
| \- Sample every 10th page (reduce tokens)                            |
|                                                                      |
| \- LLM identifies: Auditor Report, Directors Report, MD&A,           |
|                                                                      |
| Balance Sheet, P&L, Cash Flow, Notes, RPT, Shareholding              |
|                                                                      |
| \- Second LLM call refines exact boundaries                          |
|                                                                      |
| \- Total: \~50K tokens = Rs.3-5                                      |
|                                                                      |
| STEP 3: TARGETED EXTRACTION Cost: Rs.0                               |
|                                                                      |
| \- Extract ONLY identified sections (\~100 pages, not 700)           |
|                                                                      |
| \- Auditor Report: 10 pages                                          |
|                                                                      |
| \- Directors/MD&A: 40 pages                                          |
|                                                                      |
| \- Financial Statements: 10 pages                                    |
|                                                                      |
| \- Key Notes (RPT, Contingent): 20 pages                             |
|                                                                      |
| \- Shareholding: 10 pages                                            |
|                                                                      |
| STEP 4: TABLE EXTRACTION Cost: Rs.0                                  |
|                                                                      |
| \- Camelot for native PDF tables                                     |
|                                                                      |
| \- Surya for scanned tables                                          |
|                                                                      |
| \- Multi-page table handling                                         |
|                                                                      |
| STEP 5: RED FLAG ANALYSIS Cost: Rs.5-8                               |
|                                                                      |
| \- Rule-based engine (48 flags): Rs.0                                |
|                                                                      |
| \- LLM analysis (6 flags): Rs.5-8                                    |
|                                                                      |
| \- Auditor opinion analysis                                          |
|                                                                      |
| \- MD&A sentiment                                                    |
|                                                                      |
| \- Executive summary generation                                      |
+======================================================================+

**LLM Prompt for Section Detection**

+----------------------------------------------------------------------+
| PROMPT: You are analyzing an Indian company annual report.           |
|                                                                      |
| Given sampled pages (every 10th page), identify where sections       |
| BEGIN:                                                               |
|                                                                      |
| 1\. Independent Auditor Report (Standalone)                          |
|                                                                      |
| 2\. Independent Auditor Report (Consolidated)                        |
|                                                                      |
| 3\. Directors Report / Board Report                                  |
|                                                                      |
| 4\. Management Discussion & Analysis                                 |
|                                                                      |
| 5\. Corporate Governance Report                                      |
|                                                                      |
| 6\. Balance Sheet                                                    |
|                                                                      |
| 7\. P&L Statement                                                    |
|                                                                      |
| 8\. Cash Flow Statement                                              |
|                                                                      |
| 9\. Notes to Financial Statements                                    |
|                                                                      |
| 10\. Related Party Transactions note                                 |
|                                                                      |
| 11\. Shareholding Pattern                                            |
|                                                                      |
| Return JSON: {\"section\": {\"start\": page, \"confidence\": 0-1}}   |
|                                                                      |
| Important: Headers may be ALL CAPS or Title Case.                    |
|                                                                      |
| Directors Report may be called \'Board Report\'.                     |
|                                                                      |
| There are usually TWO auditor reports (standalone + consolidated).   |
+======================================================================+

**DATABASE SCHEMA & API REFERENCE**

Complete PostgreSQL Schema \| RESTful API Endpoints \| Request/Response
Examples

*Appendix to RedFlag AI Specification v3.0*

**Table of Contents**

PART A: DATABASE SCHEMA

1\. Schema Overview & ERD
\...\...\...\...\...\...\...\...\...\...\...\...\...\...\...\...\...\...\....
3

2\. Core Tables (users, companies, annual_reports)
\...\...\...\...\...\...\...\... 4

3\. Analysis Tables (analysis_results, red_flags)
\...\...\...\...\...\...\...\...\...\... 7

4\. User Feature Tables (watchlist, portfolio, alerts)
\...\...\...\...\...\...\..... 10

5\. System Tables (cache, jobs, audit_log)
\...\...\...\...\...\...\...\...\...\...\...\.... 12

6\. Indexes & Performance Optimization
\...\...\...\...\...\...\...\...\...\...\...\...\..... 14

PART B: API REFERENCE

7\. API Overview & Authentication
\...\...\...\...\...\...\...\...\...\...\...\...\...\...\...\.... 16

8\. Auth Endpoints (/api/v1/auth/\*)
\...\...\...\...\...\...\...\...\...\...\...\...\...\...\..... 18

9\. Company Endpoints (/api/v1/companies/\*)
\...\...\...\...\...\...\...\...\...\.... 20

10\. Analysis Endpoints (/api/v1/analyze/\*)
\...\...\...\...\...\...\...\...\...\...\..... 22

11\. Report Endpoints (/api/v1/reports/\*)
\...\...\...\...\...\...\...\...\...\...\...\..... 25

12\. User Endpoints (/api/v1/user/\*)
\...\...\...\...\...\...\...\...\...\...\...\...\...\...\.... 28

13\. Watchlist Endpoints (/api/v1/watchlist/\*)
\...\...\...\...\...\...\...\...\...\.... 30

14\. Portfolio Endpoints (/api/v1/portfolio/\*)
\...\...\...\...\...\...\...\...\...\...\... 32

15\. Webhook Endpoints (/api/v1/webhooks/\*)
\...\...\...\...\...\...\...\...\...\... 34

16\. Error Codes & Rate Limiting
\...\...\...\...\...\...\...\...\...\...\...\...\...\...\...\...\.... 36

**PART A: DATABASE SCHEMA**

**1. Schema Overview**

RedFlag AI uses PostgreSQL (hosted on Supabase) with 12 main tables
organized into 4 categories.

  ----------------------- ----------------------- -----------------------
  **Category**            **Tables**              **Purpose**

  Core                    users, companies,       User accounts, company
                          annual_reports          master data, AR files

  Analysis                analysis_results,       Analysis outputs,
                          red_flags,              detected flags,
                          section_extracts        extracted text

  User Features           watchlist,              Watchlist tracking,
                          portfolio_holdings,     portfolio,
                          alerts, user_reports    notifications

  System                  cache_entries,          Caching, background
                          job_queue, audit_log,   jobs, logging, billing
                          subscriptions           
  ----------------------- ----------------------- -----------------------

**Entity Relationship Diagram**

+---------------------------------------------------------------------------------+
| ┌─────────────────────────────────────────────────────────────────────────────┐ |
|                                                                                 |
| │ REDFLAG AI - DATABASE ERD │                                                   |
|                                                                                 |
| └─────────────────────────────────────────────────────────────────────────────┘ |
|                                                                                 |
| ┌──────────────┐ ┌──────────────┐ ┌──────────────┐                              |
|                                                                                 |
| │ users │ │ companies │ │annual_reports│                                        |
|                                                                                 |
| ├──────────────┤ ├──────────────┤ ├──────────────┤                              |
|                                                                                 |
| │ id (PK) │ │ id (PK) │◄────────┤ company_id │                                  |
|                                                                                 |
| │ email │ │ name │ │ id (PK) │                                                  |
|                                                                                 |
| │ name │ │ bse_code │ │ fiscal_year │                                           |
|                                                                                 |
| │ subscription │ │ nse_symbol │ │ pdf_url │                                     |
|                                                                                 |
| └──────┬───────┘ │ industry │ │ pdf_hash │                                      |
|                                                                                 |
| │ └──────────────┘ └──────┬───────┘                                             |
|                                                                                 |
| │ │                                                                             |
|                                                                                 |
| │ │                                                                             |
|                                                                                 |
| │ ┌──────────────────────────────────────────────┘                              |
|                                                                                 |
| │ │                                                                             |
|                                                                                 |
| │ ▼                                                                             |
|                                                                                 |
| │ ┌──────────────┐ ┌──────────────┐                                             |
|                                                                                 |
| │ │analysis\_ │ │ red_flags │                                                   |
|                                                                                 |
| │ │results │ ├──────────────┤                                                   |
|                                                                                 |
| │ ├──────────────┤◄────────┤ analysis_id │                                      |
|                                                                                 |
| │ │ id (PK) │ │ id (PK) │                                                       |
|                                                                                 |
| │ │ report_id │ │ flag_code │                                                   |
|                                                                                 |
| │ │ risk_score │ │ severity │                                                   |
|                                                                                 |
| │ │ category\_ │ │ is_triggered │                                               |
|                                                                                 |
| │ │ scores │ │ evidence │                                                       |
|                                                                                 |
| │ └──────────────┘ │ page_number │                                              |
|                                                                                 |
| │ └──────────────┘                                                              |
|                                                                                 |
| │                                                                               |
|                                                                                 |
| ▼                                                                               |
|                                                                                 |
| ┌──────────────┐ ┌──────────────┐ ┌──────────────┐                              |
|                                                                                 |
| │ watchlist │ │ portfolio\_ │ │ alerts │                                        |
|                                                                                 |
| ├──────────────┤ │ holdings │ ├──────────────┤                                  |
|                                                                                 |
| │ user_id (FK) │ ├──────────────┤ │ user_id (FK) │                              |
|                                                                                 |
| │ company_id │ │ user_id (FK) │ │ company_id │                                  |
|                                                                                 |
| │ alert_config │ │ company_id │ │ alert_type │                                  |
|                                                                                 |
| └──────────────┘ │ quantity │ │ is_read │                                       |
|                                                                                 |
| └──────────────┘ └──────────────┘                                               |
+---------------------------------------------------------------------------------+

**2. Core Tables**

**2.1 users**

Stores user account information and subscription details.

+----------------------------------------------------------------------+
| CREATE TABLE users (                                                 |
|                                                                      |
| id UUID PRIMARY KEY DEFAULT gen_random_uuid(),                       |
|                                                                      |
| email VARCHAR(255) UNIQUE NOT NULL,                                  |
|                                                                      |
| password_hash VARCHAR(255), \-- NULL if OAuth login                  |
|                                                                      |
| name VARCHAR(255),                                                   |
|                                                                      |
| avatar_url TEXT,                                                     |
|                                                                      |
| \-- Subscription                                                     |
|                                                                      |
| subscription_tier VARCHAR(20) DEFAULT \'free\', \-- \'free\' \|      |
| \'pro\' \| \'premium\'                                               |
|                                                                      |
| subscription_id VARCHAR(100), \-- Razorpay subscription ID           |
|                                                                      |
| subscription_expires_at TIMESTAMP,                                   |
|                                                                      |
| \-- Usage tracking                                                   |
|                                                                      |
| reports_used_this_month INT DEFAULT 0,                               |
|                                                                      |
| reports_reset_at TIMESTAMP DEFAULT NOW(),                            |
|                                                                      |
| \-- OAuth                                                            |
|                                                                      |
| google_id VARCHAR(100),                                              |
|                                                                      |
| \-- Timestamps                                                       |
|                                                                      |
| created_at TIMESTAMP DEFAULT NOW(),                                  |
|                                                                      |
| updated_at TIMESTAMP DEFAULT NOW(),                                  |
|                                                                      |
| last_login_at TIMESTAMP,                                             |
|                                                                      |
| \-- Constraints                                                      |
|                                                                      |
| CONSTRAINT valid_subscription CHECK (subscription_tier IN (\'free\', |
| \'pro\', \'premium\'))                                               |
|                                                                      |
| );                                                                   |
|                                                                      |
| \-- Indexes                                                          |
|                                                                      |
| CREATE UNIQUE INDEX idx_users_email ON users(email);                 |
|                                                                      |
| CREATE INDEX idx_users_google ON users(google_id) WHERE google_id IS |
| NOT NULL;                                                            |
+----------------------------------------------------------------------+

  ------------------------- ----------------------- -----------------------
  **Column**                **Type**                **Description**

  id                        UUID                    Primary key,
                                                    auto-generated

  email                     VARCHAR(255)            User email, unique

  password_hash             VARCHAR(255)            Bcrypt hash, NULL for
                                                    OAuth

  subscription_tier         VARCHAR(20)             free, pro, or premium

  reports_used_this_month   INT                     Counter, resets monthly

  subscription_expires_at   TIMESTAMP               NULL for free tier
  ------------------------- ----------------------- -----------------------

**2.2 companies**

Master data for all companies. Pre-populated with NIFTY 500, extended as
users analyze new companies.

+----------------------------------------------------------------------+
| CREATE TABLE companies (                                             |
|                                                                      |
| id UUID PRIMARY KEY DEFAULT gen_random_uuid(),                       |
|                                                                      |
| \-- Identifiers                                                      |
|                                                                      |
| name VARCHAR(255) NOT NULL,                                          |
|                                                                      |
| bse_code VARCHAR(10),                                                |
|                                                                      |
| nse_symbol VARCHAR(20),                                              |
|                                                                      |
| isin VARCHAR(12),                                                    |
|                                                                      |
| cin VARCHAR(25), \-- Corporate Identity Number                       |
|                                                                      |
| \-- Classification                                                   |
|                                                                      |
| industry VARCHAR(100),                                               |
|                                                                      |
| sector VARCHAR(100),                                                 |
|                                                                      |
| sub_sector VARCHAR(100),                                             |
|                                                                      |
| \-- Market data (updated periodically)                               |
|                                                                      |
| market_cap_cr BIGINT, \-- In crores                                  |
|                                                                      |
| market_cap_category VARCHAR(20), \-- \'large\' \| \'mid\' \|         |
| \'small\'                                                            |
|                                                                      |
| \-- Index membership                                                 |
|                                                                      |
| is_nifty_50 BOOLEAN DEFAULT FALSE,                                   |
|                                                                      |
| is_nifty_100 BOOLEAN DEFAULT FALSE,                                  |
|                                                                      |
| is_nifty_500 BOOLEAN DEFAULT FALSE,                                  |
|                                                                      |
| \-- Status                                                           |
|                                                                      |
| is_active BOOLEAN DEFAULT TRUE, \-- FALSE if delisted                |
|                                                                      |
| \-- Timestamps                                                       |
|                                                                      |
| created_at TIMESTAMP DEFAULT NOW(),                                  |
|                                                                      |
| updated_at TIMESTAMP DEFAULT NOW()                                   |
|                                                                      |
| );                                                                   |
|                                                                      |
| \-- Indexes for search                                               |
|                                                                      |
| CREATE INDEX idx_companies_bse ON companies(bse_code) WHERE bse_code |
| IS NOT NULL;                                                         |
|                                                                      |
| CREATE INDEX idx_companies_nse ON companies(nse_symbol) WHERE        |
| nse_symbol IS NOT NULL;                                              |
|                                                                      |
| CREATE INDEX idx_companies_name ON companies USING gin(name          |
| gin_trgm_ops); \-- Fuzzy search                                      |
|                                                                      |
| CREATE INDEX idx_companies_nifty500 ON companies(is_nifty_500) WHERE |
| is_nifty_500 = TRUE;                                                 |
+----------------------------------------------------------------------+

**2.3 annual_reports**

Stores metadata about annual report PDFs. Actual PDFs stored in
Cloudflare R2.

+----------------------------------------------------------------------+
| CREATE TABLE annual_reports (                                        |
|                                                                      |
| id UUID PRIMARY KEY DEFAULT gen_random_uuid(),                       |
|                                                                      |
| company_id UUID NOT NULL REFERENCES companies(id),                   |
|                                                                      |
| \-- Identification                                                   |
|                                                                      |
| fiscal_year VARCHAR(10) NOT NULL, \-- \'FY2024\'                     |
|                                                                      |
| report_type VARCHAR(20) DEFAULT \'annual\', \-- \'annual\' \|        |
| \'quarterly\'                                                        |
|                                                                      |
| \-- File info                                                        |
|                                                                      |
| pdf_url TEXT NOT NULL, \-- R2 URL                                    |
|                                                                      |
| pdf_hash VARCHAR(64), \-- SHA-256 for deduplication                  |
|                                                                      |
| page_count INT,                                                      |
|                                                                      |
| file_size_mb DECIMAL(10, 2),                                         |
|                                                                      |
| \-- Source                                                           |
|                                                                      |
| source VARCHAR(50) DEFAULT \'bse\', \-- \'bse\' \| \'nse\' \|        |
| \'user_upload\'                                                      |
|                                                                      |
| source_url TEXT, \-- Original download URL                           |
|                                                                      |
| \-- Processing status                                                |
|                                                                      |
| text_extracted BOOLEAN DEFAULT FALSE,                                |
|                                                                      |
| extraction_status VARCHAR(20) DEFAULT \'pending\', \--               |
| \'pending\'\|\'processing\'\|\'completed\'\|\'failed\'               |
|                                                                      |
| \-- Timestamps                                                       |
|                                                                      |
| report_date DATE, \-- Date mentioned in AR                           |
|                                                                      |
| uploaded_at TIMESTAMP DEFAULT NOW(),                                 |
|                                                                      |
| processed_at TIMESTAMP,                                              |
|                                                                      |
| \-- Constraints                                                      |
|                                                                      |
| UNIQUE(company_id, fiscal_year, report_type)                         |
|                                                                      |
| );                                                                   |
|                                                                      |
| CREATE INDEX idx_ar_company ON annual_reports(company_id);           |
|                                                                      |
| CREATE INDEX idx_ar_fiscal ON annual_reports(fiscal_year);           |
|                                                                      |
| CREATE INDEX idx_ar_hash ON annual_reports(pdf_hash) WHERE pdf_hash  |
| IS NOT NULL;                                                         |
+----------------------------------------------------------------------+

**3. Analysis Tables**

**3.1 analysis_results**

Stores the output of each analysis run. One row per annual report
analyzed.

+----------------------------------------------------------------------+
| CREATE TABLE analysis_results (                                      |
|                                                                      |
| id UUID PRIMARY KEY DEFAULT gen_random_uuid(),                       |
|                                                                      |
| report_id UUID NOT NULL REFERENCES annual_reports(id),               |
|                                                                      |
| \-- Risk Assessment                                                  |
|                                                                      |
| risk_score INT NOT NULL CHECK (risk_score \>= 0 AND risk_score \<=   |
| 100),                                                                |
|                                                                      |
| risk_level VARCHAR(20) NOT NULL, \--                                 |
| \'low\'\|\'moderate\'\|\'elevated\'\|\'high\'                        |
|                                                                      |
| \-- Category breakdown (JSONB for flexibility)                       |
|                                                                      |
| category_scores JSONB NOT NULL,                                      |
|                                                                      |
| \-- Example: {                                                       |
|                                                                      |
| \-- \"auditor\": 45,                                                 |
|                                                                      |
| \-- \"cash_flow\": 72,                                               |
|                                                                      |
| \-- \"related_party\": 58,                                           |
|                                                                      |
| \-- \"promoter\": 85,                                                |
|                                                                      |
| \-- \"governance\": 35,                                              |
|                                                                      |
| \-- \"balance_sheet\": 28,                                           |
|                                                                      |
| \-- \"revenue_quality\": 38,                                         |
|                                                                      |
| \-- \"textual\": 42                                                  |
|                                                                      |
| \-- }                                                                |
|                                                                      |
| \-- Summary                                                          |
|                                                                      |
| executive_summary TEXT, \-- LLM-generated summary                    |
|                                                                      |
| key_concerns TEXT\[\], \-- Array of main concerns                    |
|                                                                      |
| \-- Metadata                                                         |
|                                                                      |
| red_flag_count INT DEFAULT 0,                                        |
|                                                                      |
| critical_count INT DEFAULT 0,                                        |
|                                                                      |
| high_count INT DEFAULT 0,                                            |
|                                                                      |
| \-- Processing info                                                  |
|                                                                      |
| processing_time_ms INT,                                              |
|                                                                      |
| llm_tokens_used INT,                                                 |
|                                                                      |
| processing_cost_inr DECIMAL(10, 4),                                  |
|                                                                      |
| model_version VARCHAR(50), \-- \'v1.0\', \'v1.1\', etc.              |
|                                                                      |
| \-- Timestamps                                                       |
|                                                                      |
| analyzed_at TIMESTAMP DEFAULT NOW(),                                 |
|                                                                      |
| \-- Unique constraint                                                |
|                                                                      |
| UNIQUE(report_id)                                                    |
|                                                                      |
| );                                                                   |
|                                                                      |
| CREATE INDEX idx_analysis_report ON analysis_results(report_id);     |
|                                                                      |
| CREATE INDEX idx_analysis_score ON analysis_results(risk_score);     |
+----------------------------------------------------------------------+

**3.2 red_flags**

Stores individual red flag results. 54 rows per analysis (one per flag).

+----------------------------------------------------------------------+
| CREATE TABLE red_flags (                                             |
|                                                                      |
| id UUID PRIMARY KEY DEFAULT gen_random_uuid(),                       |
|                                                                      |
| analysis_id UUID NOT NULL REFERENCES analysis_results(id) ON DELETE  |
| CASCADE,                                                             |
|                                                                      |
| \-- Flag identification                                              |
|                                                                      |
| flag_code VARCHAR(50) NOT NULL, \-- \'AUDITOR_QUALIFIED\',           |
| \'CFO_PAT_LOW\', etc.                                                |
|                                                                      |
| flag_name VARCHAR(255) NOT NULL, \-- Human-readable name             |
|                                                                      |
| category VARCHAR(50) NOT NULL, \-- \'auditor\', \'cash_flow\', etc.  |
|                                                                      |
| \-- Severity                                                         |
|                                                                      |
| severity VARCHAR(20) NOT NULL, \--                                   |
| \'CRITICAL\'\|\'HIGH\'\|\'MEDIUM\'\|\'LOW\'                          |
|                                                                      |
| weight DECIMAL(5, 4), \-- Weight in scoring (0.0 - 1.0)              |
|                                                                      |
| \-- Detection result                                                 |
|                                                                      |
| is_triggered BOOLEAN NOT NULL, \-- TRUE if flag was detected         |
|                                                                      |
| confidence DECIMAL(5, 4), \-- 0.0 - 1.0 confidence level             |
|                                                                      |
| \-- Evidence                                                         |
|                                                                      |
| evidence TEXT, \-- Quote or description                              |
|                                                                      |
| page_number INT, \-- Page in PDF                                     |
|                                                                      |
| section_name VARCHAR(100), \-- \'Auditor Report\', \'Notes\', etc.   |
|                                                                      |
| \-- Metric values (for quantitative flags)                           |
|                                                                      |
| metric_value DECIMAL(20, 4), \-- Current value (e.g., 0.62 for 62%)  |
|                                                                      |
| threshold_value DECIMAL(20, 4), \-- Threshold (e.g., 0.50)           |
|                                                                      |
| previous_value DECIMAL(20, 4), \-- Prior year value                  |
|                                                                      |
| yoy_change DECIMAL(10, 4), \-- Year-over-year change                 |
|                                                                      |
| \-- Timestamps                                                       |
|                                                                      |
| created_at TIMESTAMP DEFAULT NOW()                                   |
|                                                                      |
| );                                                                   |
|                                                                      |
| CREATE INDEX idx_flags_analysis ON red_flags(analysis_id);           |
|                                                                      |
| CREATE INDEX idx_flags_triggered ON red_flags(analysis_id,           |
| is_triggered) WHERE is_triggered = TRUE;                             |
|                                                                      |
| CREATE INDEX idx_flags_severity ON red_flags(severity) WHERE         |
| is_triggered = TRUE;                                                 |
|                                                                      |
| CREATE INDEX idx_flags_category ON red_flags(category);              |
+----------------------------------------------------------------------+

**Flag Codes Reference**

  ---------------------------- ---------------- ---------------- ----------------
  **Code**                     **Name**         **Category**     **Severity**

  AUDITOR_RESIGNED             Auditor resigned auditor          CRITICAL
                               mid-term                          

  AUDITOR_QUALIFIED            Qualified audit  auditor          CRITICAL
                               opinion                           

  AUDITOR_GOING_CONCERN        Going concern    auditor          CRITICAL
                               qualification                     

  CFO_PAT_LOW                  CFO/PAT ratio \< cash_flow        HIGH
                               0.5                               

  RECEIVABLES_GROWING          Receivables      cash_flow        HIGH
                               growing \>                        
                               revenue                           

  RPT_HIGH                     Related party    related_party    HIGH
                               transactions \>                   
                               10%                               

  PROMOTER_PLEDGE_HIGH         Promoter pledge  promoter         CRITICAL
                               \> 50%                            

  PROMOTER_PLEDGE_INCREASING   Pledge           promoter         HIGH
                               increasing QoQ                    

  BOARD_CHANGES                Independent      governance       HIGH
                               director                          
                               resigned                          

  DEBT_EQUITY_HIGH             D/E ratio \> 2   balance_sheet    HIGH
  ---------------------------- ---------------- ---------------- ----------------

**3.3 section_extracts**

Stores extracted text from AR sections for quick retrieval and
re-analysis.

+----------------------------------------------------------------------+
| CREATE TABLE section_extracts (                                      |
|                                                                      |
| id UUID PRIMARY KEY DEFAULT gen_random_uuid(),                       |
|                                                                      |
| report_id UUID NOT NULL REFERENCES annual_reports(id) ON DELETE      |
| CASCADE,                                                             |
|                                                                      |
| \-- Section identification                                           |
|                                                                      |
| section_name VARCHAR(100) NOT NULL, \-- \'auditor_standalone\',      |
| \'mda\', etc.                                                        |
|                                                                      |
| start_page INT NOT NULL,                                             |
|                                                                      |
| end_page INT NOT NULL,                                               |
|                                                                      |
| \-- Content                                                          |
|                                                                      |
| extracted_text TEXT,                                                 |
|                                                                      |
| extraction_method VARCHAR(50), \-- \'pymupdf\' \| \'surya_ocr\' \|   |
| \'google_vision\'                                                    |
|                                                                      |
| confidence DECIMAL(5, 4),                                            |
|                                                                      |
| \-- Structured data (for financial statements)                       |
|                                                                      |
| structured_data JSONB,                                               |
|                                                                      |
| \-- Example for balance_sheet:                                       |
|                                                                      |
| \-- {                                                                |
|                                                                      |
| \-- \"total_assets\": 15234.5,                                       |
|                                                                      |
| \-- \"total_liabilities\": 8234.5,                                   |
|                                                                      |
| \-- \"equity\": 7000.0,                                              |
|                                                                      |
| \-- \"trade_receivables\": 1234.5,                                   |
|                                                                      |
| \-- \"inventory\": 2345.6,                                           |
|                                                                      |
| \-- \...                                                             |
|                                                                      |
| \-- }                                                                |
|                                                                      |
| created_at TIMESTAMP DEFAULT NOW()                                   |
|                                                                      |
| );                                                                   |
|                                                                      |
| CREATE INDEX idx_sections_report ON section_extracts(report_id);     |
|                                                                      |
| CREATE INDEX idx_sections_name ON section_extracts(report_id,        |
| section_name);                                                       |
+----------------------------------------------------------------------+

**4. User Feature Tables**

**4.1 watchlist**

Tracks which companies each user is watching.

+----------------------------------------------------------------------+
| CREATE TABLE watchlist (                                             |
|                                                                      |
| id UUID PRIMARY KEY DEFAULT gen_random_uuid(),                       |
|                                                                      |
| user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,        |
|                                                                      |
| company_id UUID NOT NULL REFERENCES companies(id),                   |
|                                                                      |
| \-- Alert configuration (JSONB for flexibility)                      |
|                                                                      |
| alert_config JSONB DEFAULT \'{                                       |
|                                                                      |
| \"on_new_ar\": true,                                                 |
|                                                                      |
| \"on_score_change\": 10,                                             |
|                                                                      |
| \"on_critical_flag\": true,                                          |
|                                                                      |
| \"on_pledge_threshold\": 50,                                         |
|                                                                      |
| \"weekly_summary\": false                                            |
|                                                                      |
| }\'::jsonb,                                                          |
|                                                                      |
| \-- Last known values (for change detection)                         |
|                                                                      |
| last_risk_score INT,                                                 |
|                                                                      |
| last_analysis_id UUID REFERENCES analysis_results(id),               |
|                                                                      |
| last_checked_at TIMESTAMP,                                           |
|                                                                      |
| \-- Timestamps                                                       |
|                                                                      |
| created_at TIMESTAMP DEFAULT NOW(),                                  |
|                                                                      |
| \-- Unique constraint                                                |
|                                                                      |
| UNIQUE(user_id, company_id)                                          |
|                                                                      |
| );                                                                   |
|                                                                      |
| CREATE INDEX idx_watchlist_user ON watchlist(user_id);               |
|                                                                      |
| CREATE INDEX idx_watchlist_company ON watchlist(company_id);         |
+----------------------------------------------------------------------+

**4.2 portfolio_holdings**

Stores user portfolio for portfolio scanning feature.

+----------------------------------------------------------------------+
| CREATE TABLE portfolio_holdings (                                    |
|                                                                      |
| id UUID PRIMARY KEY DEFAULT gen_random_uuid(),                       |
|                                                                      |
| user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,        |
|                                                                      |
| company_id UUID NOT NULL REFERENCES companies(id),                   |
|                                                                      |
| \-- Holding details                                                  |
|                                                                      |
| quantity DECIMAL(20, 4),                                             |
|                                                                      |
| avg_buy_price DECIMAL(20, 4),                                        |
|                                                                      |
| current_value DECIMAL(20, 4),                                        |
|                                                                      |
| \-- Risk info (cached from latest analysis)                          |
|                                                                      |
| latest_risk_score INT,                                               |
|                                                                      |
| latest_analysis_id UUID REFERENCES analysis_results(id),             |
|                                                                      |
| \-- Source                                                           |
|                                                                      |
| source VARCHAR(50), \-- \'manual\' \| \'zerodha\' \| \'groww\' \|    |
| etc.                                                                 |
|                                                                      |
| \-- Timestamps                                                       |
|                                                                      |
| created_at TIMESTAMP DEFAULT NOW(),                                  |
|                                                                      |
| updated_at TIMESTAMP DEFAULT NOW(),                                  |
|                                                                      |
| \-- Unique constraint                                                |
|                                                                      |
| UNIQUE(user_id, company_id)                                          |
|                                                                      |
| );                                                                   |
|                                                                      |
| CREATE INDEX idx_portfolio_user ON portfolio_holdings(user_id);      |
+----------------------------------------------------------------------+

**4.3 alerts**

Stores alerts/notifications for users.

+----------------------------------------------------------------------+
| CREATE TABLE alerts (                                                |
|                                                                      |
| id UUID PRIMARY KEY DEFAULT gen_random_uuid(),                       |
|                                                                      |
| user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,        |
|                                                                      |
| \-- Alert details                                                    |
|                                                                      |
| alert_type VARCHAR(50) NOT NULL, \--                                 |
| \'new_ar\'\|\'score_change\'\|\'critical_flag\'\|\'pledge\'          |
|                                                                      |
| title VARCHAR(255) NOT NULL,                                         |
|                                                                      |
| message TEXT,                                                        |
|                                                                      |
| \-- Related entities                                                 |
|                                                                      |
| company_id UUID REFERENCES companies(id),                            |
|                                                                      |
| analysis_id UUID REFERENCES analysis_results(id),                    |
|                                                                      |
| \-- Additional data                                                  |
|                                                                      |
| metadata JSONB,                                                      |
|                                                                      |
| \-- Example: { \"old_score\": 58, \"new_score\": 67, \"change\": 9 } |
|                                                                      |
| \-- Status                                                           |
|                                                                      |
| is_read BOOLEAN DEFAULT FALSE,                                       |
|                                                                      |
| is_emailed BOOLEAN DEFAULT FALSE,                                    |
|                                                                      |
| is_pushed BOOLEAN DEFAULT FALSE,                                     |
|                                                                      |
| \-- Timestamps                                                       |
|                                                                      |
| created_at TIMESTAMP DEFAULT NOW(),                                  |
|                                                                      |
| read_at TIMESTAMP                                                    |
|                                                                      |
| );                                                                   |
|                                                                      |
| CREATE INDEX idx_alerts_user ON alerts(user_id, created_at DESC);    |
|                                                                      |
| CREATE INDEX idx_alerts_unread ON alerts(user_id, is_read) WHERE     |
| is_read = FALSE;                                                     |
+----------------------------------------------------------------------+

**4.4 user_reports**

Tracks which analyses a user has accessed (for recent reports).

+----------------------------------------------------------------------+
| CREATE TABLE user_reports (                                          |
|                                                                      |
| id UUID PRIMARY KEY DEFAULT gen_random_uuid(),                       |
|                                                                      |
| user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,        |
|                                                                      |
| analysis_id UUID NOT NULL REFERENCES analysis_results(id),           |
|                                                                      |
| \-- Access tracking                                                  |
|                                                                      |
| first_accessed_at TIMESTAMP DEFAULT NOW(),                           |
|                                                                      |
| last_accessed_at TIMESTAMP DEFAULT NOW(),                            |
|                                                                      |
| access_count INT DEFAULT 1,                                          |
|                                                                      |
| \-- Unique constraint                                                |
|                                                                      |
| UNIQUE(user_id, analysis_id)                                         |
|                                                                      |
| );                                                                   |
|                                                                      |
| CREATE INDEX idx_user_reports_recent ON user_reports(user_id,        |
| last_accessed_at DESC);                                              |
+----------------------------------------------------------------------+

**5. System Tables**

**5.1 cache_entries**

Application-level cache for analysis results and API responses.

+----------------------------------------------------------------------+
| CREATE TABLE cache_entries (                                         |
|                                                                      |
| key VARCHAR(255) PRIMARY KEY,                                        |
|                                                                      |
| value JSONB NOT NULL,                                                |
|                                                                      |
| expires_at TIMESTAMP,                                                |
|                                                                      |
| created_at TIMESTAMP DEFAULT NOW()                                   |
|                                                                      |
| );                                                                   |
|                                                                      |
| \-- Example keys:                                                    |
|                                                                      |
| \-- \'analysis:company_123:FY2024\' -\> cached analysis result       |
|                                                                      |
| \-- \'search:reliance\' -\> cached search results                    |
|                                                                      |
| \-- \'peers:media_sector\' -\> cached peer list                      |
|                                                                      |
| CREATE INDEX idx_cache_expires ON cache_entries(expires_at) WHERE    |
| expires_at IS NOT NULL;                                              |
+----------------------------------------------------------------------+

**5.2 job_queue**

Tracks background job status (analysis, alerts, etc.).

+----------------------------------------------------------------------+
| CREATE TABLE job_queue (                                             |
|                                                                      |
| id UUID PRIMARY KEY DEFAULT gen_random_uuid(),                       |
|                                                                      |
| \-- Job info                                                         |
|                                                                      |
| job_type VARCHAR(50) NOT NULL, \--                                   |
| \'analysis\'\|\'alert\'\|\'cache_refresh\'                           |
|                                                                      |
| status VARCHAR(20) DEFAULT \'pending\', \--                          |
| \'pending\'\|\'running\'\|\'completed\'\|\'failed\'                  |
|                                                                      |
| priority INT DEFAULT 5, \-- 1 = highest, 10 = lowest                 |
|                                                                      |
| \-- Input/Output                                                     |
|                                                                      |
| input_data JSONB,                                                    |
|                                                                      |
| output_data JSONB,                                                   |
|                                                                      |
| error_message TEXT,                                                  |
|                                                                      |
| \-- Related entities                                                 |
|                                                                      |
| user_id UUID REFERENCES users(id),                                   |
|                                                                      |
| report_id UUID REFERENCES annual_reports(id),                        |
|                                                                      |
| \-- Timing                                                           |
|                                                                      |
| created_at TIMESTAMP DEFAULT NOW(),                                  |
|                                                                      |
| started_at TIMESTAMP,                                                |
|                                                                      |
| completed_at TIMESTAMP,                                              |
|                                                                      |
| \-- Retry                                                            |
|                                                                      |
| attempts INT DEFAULT 0,                                              |
|                                                                      |
| max_attempts INT DEFAULT 3                                           |
|                                                                      |
| );                                                                   |
|                                                                      |
| CREATE INDEX idx_jobs_pending ON job_queue(status, priority,         |
| created_at)                                                          |
|                                                                      |
| WHERE status = \'pending\';                                          |
+----------------------------------------------------------------------+

**5.3 subscriptions**

Tracks subscription and payment history.

+----------------------------------------------------------------------+
| CREATE TABLE subscriptions (                                         |
|                                                                      |
| id UUID PRIMARY KEY DEFAULT gen_random_uuid(),                       |
|                                                                      |
| user_id UUID NOT NULL REFERENCES users(id),                          |
|                                                                      |
| \-- Razorpay details                                                 |
|                                                                      |
| razorpay_subscription_id VARCHAR(100),                               |
|                                                                      |
| razorpay_plan_id VARCHAR(100),                                       |
|                                                                      |
| razorpay_customer_id VARCHAR(100),                                   |
|                                                                      |
| \-- Subscription details                                             |
|                                                                      |
| tier VARCHAR(20) NOT NULL, \-- \'pro\' \| \'premium\'                |
|                                                                      |
| amount_inr INT NOT NULL, \-- 599 or 1499                             |
|                                                                      |
| billing_cycle VARCHAR(20) DEFAULT \'monthly\',                       |
|                                                                      |
| \-- Status                                                           |
|                                                                      |
| status VARCHAR(20) DEFAULT \'active\', \--                           |
| \'active\'\|\'cancelled\'\|\'expired\'                               |
|                                                                      |
| started_at TIMESTAMP DEFAULT NOW(),                                  |
|                                                                      |
| expires_at TIMESTAMP,                                                |
|                                                                      |
| cancelled_at TIMESTAMP,                                              |
|                                                                      |
| created_at TIMESTAMP DEFAULT NOW()                                   |
|                                                                      |
| );                                                                   |
|                                                                      |
| CREATE INDEX idx_subscriptions_user ON subscriptions(user_id);       |
+----------------------------------------------------------------------+

**6. Indexes & Performance**

**6.1 Key Indexes Summary**

  ------------------ ------------------------ ----------------- -----------------
  **Table**          **Index**                **Columns**       **Purpose**

  users              idx_users_email          email             Login lookup

  companies          idx_companies_name       name (gin_trgm)   Fuzzy search

  companies          idx_companies_nifty500   is_nifty_500      Filter NIFTY 500

  annual_reports     idx_ar_company           company_id        Find ARs by
                                                                company

  analysis_results   idx_analysis_score       risk_score        Sort by risk

  red_flags          idx_flags_triggered      analysis_id,      Find active flags
                                              is_triggered      

  watchlist          idx_watchlist_user       user_id           User\'s watchlist

  alerts             idx_alerts_unread        user_id, is_read  Unread alerts
  ------------------ ------------------------ ----------------- -----------------

**6.2 Query Patterns**

+----------------------------------------------------------------------+
| \-- 1. Search companies by name (fuzzy)                              |
|                                                                      |
| SELECT \* FROM companies                                             |
|                                                                      |
| WHERE name ILIKE \'%reliance%\'                                      |
|                                                                      |
| ORDER BY                                                             |
|                                                                      |
| CASE WHEN name ILIKE \'reliance%\' THEN 0 ELSE 1 END,                |
|                                                                      |
| is_nifty_500 DESC,                                                   |
|                                                                      |
| market_cap_cr DESC NULLS LAST                                        |
|                                                                      |
| LIMIT 10;                                                            |
|                                                                      |
| \-- 2. Get latest analysis for a company                             |
|                                                                      |
| SELECT ar.\*, an.\*                                                  |
|                                                                      |
| FROM annual_reports ar                                               |
|                                                                      |
| JOIN analysis_results an ON ar.id = an.report_id                     |
|                                                                      |
| WHERE ar.company_id = \$1                                            |
|                                                                      |
| ORDER BY ar.fiscal_year DESC                                         |
|                                                                      |
| LIMIT 1;                                                             |
|                                                                      |
| \-- 3. Get user\'s recent reports                                    |
|                                                                      |
| SELECT ur.\*, an.\*, c.name as company_name                          |
|                                                                      |
| FROM user_reports ur                                                 |
|                                                                      |
| JOIN analysis_results an ON ur.analysis_id = an.id                   |
|                                                                      |
| JOIN annual_reports ar ON an.report_id = ar.id                       |
|                                                                      |
| JOIN companies c ON ar.company_id = c.id                             |
|                                                                      |
| WHERE ur.user_id = \$1                                               |
|                                                                      |
| ORDER BY ur.last_accessed_at DESC                                    |
|                                                                      |
| LIMIT 10;                                                            |
|                                                                      |
| \-- 4. Get triggered red flags for an analysis                       |
|                                                                      |
| SELECT \* FROM red_flags                                             |
|                                                                      |
| WHERE analysis_id = \$1 AND is_triggered = TRUE                      |
|                                                                      |
| ORDER BY                                                             |
|                                                                      |
| CASE severity                                                        |
|                                                                      |
| WHEN \'CRITICAL\' THEN 1                                             |
|                                                                      |
| WHEN \'HIGH\' THEN 2                                                 |
|                                                                      |
| WHEN \'MEDIUM\' THEN 3                                               |
|                                                                      |
| ELSE 4                                                               |
|                                                                      |
| END,                                                                 |
|                                                                      |
| category;                                                            |
+----------------------------------------------------------------------+

**PART B: API REFERENCE**

**7. API Overview**

RedFlag AI exposes a RESTful API for all client interactions.

**7.1 Base URL**

+----------------------------------------------------------------------+
| Production: https://api.redflag.ai/v1                                |
|                                                                      |
| Staging: https://api-staging.redflag.ai/v1                           |
+----------------------------------------------------------------------+

**7.2 Authentication**

All authenticated endpoints require a JWT token in the Authorization
header.

+----------------------------------------------------------------------+
| Authorization: Bearer \<jwt_token\>                                  |
|                                                                      |
| \# Token structure (decoded):                                        |
|                                                                      |
| {                                                                    |
|                                                                      |
| \"sub\": \"user_uuid\",                                              |
|                                                                      |
| \"email\": \"user@example.com\",                                     |
|                                                                      |
| \"tier\": \"pro\",                                                   |
|                                                                      |
| \"exp\": 1709856000                                                  |
|                                                                      |
| }                                                                    |
+----------------------------------------------------------------------+

**7.3 Response Format**

All responses follow a consistent JSON structure.

+----------------------------------------------------------------------+
| // Success response                                                  |
|                                                                      |
| {                                                                    |
|                                                                      |
| \"success\": true,                                                   |
|                                                                      |
| \"data\": { \... },                                                  |
|                                                                      |
| \"meta\": {                                                          |
|                                                                      |
| \"request_id\": \"req_abc123\",                                      |
|                                                                      |
| \"timestamp\": \"2026-02-03T10:30:00Z\"                              |
|                                                                      |
| }                                                                    |
|                                                                      |
| }                                                                    |
|                                                                      |
| // Error response                                                    |
|                                                                      |
| {                                                                    |
|                                                                      |
| \"success\": false,                                                  |
|                                                                      |
| \"error\": {                                                         |
|                                                                      |
| \"code\": \"RATE_LIMIT_EXCEEDED\",                                   |
|                                                                      |
| \"message\": \"You have exceeded the rate limit. Please try again in |
| 60 seconds.\",                                                       |
|                                                                      |
| \"details\": { \"retry_after\": 60 }                                 |
|                                                                      |
| },                                                                   |
|                                                                      |
| \"meta\": {                                                          |
|                                                                      |
| \"request_id\": \"req_abc123\",                                      |
|                                                                      |
| \"timestamp\": \"2026-02-03T10:30:00Z\"                              |
|                                                                      |
| }                                                                    |
|                                                                      |
| }                                                                    |
+----------------------------------------------------------------------+

**7.4 Rate Limits**

  ----------------- --------------------- ------------------ -----------------
  **Tier**          **Requests/Minute**   **Requests/Day**   **Concurrent
                                                             Jobs**

  Free              20                    100                1

  Pro               60                    500                3

  Premium           120                   2000               10
  ----------------- --------------------- ------------------ -----------------

**8. Auth Endpoints**

+----------------------------------------------------------------------+
| **POST** /api/v1/auth/signup                                         |
|                                                                      |
| Create new user account                                              |
+----------------------------------------------------------------------+

+----------------------------------------------------------------------+
| // Request                                                           |
|                                                                      |
| {                                                                    |
|                                                                      |
| \"email\": \"user@example.com\",                                     |
|                                                                      |
| \"password\": \"securePassword123\",                                 |
|                                                                      |
| \"name\": \"Manthan Patel\"                                          |
|                                                                      |
| }                                                                    |
|                                                                      |
| // Response                                                          |
|                                                                      |
| {                                                                    |
|                                                                      |
| \"success\": true,                                                   |
|                                                                      |
| \"data\": {                                                          |
|                                                                      |
| \"user\": {                                                          |
|                                                                      |
| \"id\": \"usr_abc123\",                                              |
|                                                                      |
| \"email\": \"user@example.com\",                                     |
|                                                                      |
| \"name\": \"Manthan Patel\",                                         |
|                                                                      |
| \"subscription_tier\": \"free\"                                      |
|                                                                      |
| },                                                                   |
|                                                                      |
| \"token\": \"eyJhbGciOiJIUzI1NiIs\...\",                             |
|                                                                      |
| \"expires_at\": \"2026-02-10T10:30:00Z\"                             |
|                                                                      |
| }                                                                    |
|                                                                      |
| }                                                                    |
+----------------------------------------------------------------------+

+----------------------------------------------------------------------+
| **POST** /api/v1/auth/login                                          |
|                                                                      |
| Login with email and password                                        |
+----------------------------------------------------------------------+

+----------------------------------------------------------------------+
| // Request                                                           |
|                                                                      |
| {                                                                    |
|                                                                      |
| \"email\": \"user@example.com\",                                     |
|                                                                      |
| \"password\": \"securePassword123\"                                  |
|                                                                      |
| }                                                                    |
|                                                                      |
| // Response                                                          |
|                                                                      |
| {                                                                    |
|                                                                      |
| \"success\": true,                                                   |
|                                                                      |
| \"data\": {                                                          |
|                                                                      |
| \"user\": { \... },                                                  |
|                                                                      |
| \"token\": \"eyJhbGciOiJIUzI1NiIs\...\",                             |
|                                                                      |
| \"expires_at\": \"2026-02-10T10:30:00Z\"                             |
|                                                                      |
| }                                                                    |
|                                                                      |
| }                                                                    |
+----------------------------------------------------------------------+

+----------------------------------------------------------------------+
| **POST** /api/v1/auth/google                                         |
|                                                                      |
| Login/signup with Google OAuth                                       |
+----------------------------------------------------------------------+

+----------------------------------------------------------------------+
| // Request                                                           |
|                                                                      |
| {                                                                    |
|                                                                      |
| \"google_token\": \"\<google_oauth_token\>\"                         |
|                                                                      |
| }                                                                    |
|                                                                      |
| // Response - same as login/signup                                   |
+----------------------------------------------------------------------+

+----------------------------------------------------------------------+
| **POST** /api/v1/auth/refresh                                        |
|                                                                      |
| Refresh JWT token                                                    |
+----------------------------------------------------------------------+
| **POST** /api/v1/auth/logout                                         |
|                                                                      |
| Invalidate token                                                     |
+----------------------------------------------------------------------+
| **POST** /api/v1/auth/forgot-password                                |
|                                                                      |
| Request password reset email                                         |
+----------------------------------------------------------------------+
| **POST** /api/v1/auth/reset-password                                 |
|                                                                      |
| Reset password with token                                            |
+----------------------------------------------------------------------+

**9. Company Endpoints**

+----------------------------------------------------------------------+
| **GET** /api/v1/companies/search                                     |
|                                                                      |
| Search companies by name, BSE code, or NSE symbol                    |
+----------------------------------------------------------------------+

+----------------------------------------------------------------------+
| // Request                                                           |
|                                                                      |
| GET /api/v1/companies/search?q=reliance&limit=10                     |
|                                                                      |
| // Response                                                          |
|                                                                      |
| {                                                                    |
|                                                                      |
| \"success\": true,                                                   |
|                                                                      |
| \"data\": {                                                          |
|                                                                      |
| \"companies\": \[                                                    |
|                                                                      |
| {                                                                    |
|                                                                      |
| \"id\": \"comp_abc123\",                                             |
|                                                                      |
| \"name\": \"Reliance Industries Ltd\",                               |
|                                                                      |
| \"bse_code\": \"500325\",                                            |
|                                                                      |
| \"nse_symbol\": \"RELIANCE\",                                        |
|                                                                      |
| \"industry\": \"Oil & Gas\",                                         |
|                                                                      |
| \"market_cap_cr\": 1850000,                                          |
|                                                                      |
| \"is_nifty_500\": true,                                              |
|                                                                      |
| \"cache_status\": \"cached\", // \'cached\' \| \'fresh_required\'    |
|                                                                      |
| \"available_years\": \[\"FY2024\", \"FY2023\", \"FY2022\"\]          |
|                                                                      |
| },                                                                   |
|                                                                      |
| \...                                                                 |
|                                                                      |
| \],                                                                  |
|                                                                      |
| \"total\": 3                                                         |
|                                                                      |
| }                                                                    |
|                                                                      |
| }                                                                    |
+----------------------------------------------------------------------+

+----------------------------------------------------------------------+
| **GET** /api/v1/companies/{id}                                       |
|                                                                      |
| Get company details                                                  |
+----------------------------------------------------------------------+

+----------------------------------------------------------------------+
| // Response                                                          |
|                                                                      |
| {                                                                    |
|                                                                      |
| \"success\": true,                                                   |
|                                                                      |
| \"data\": {                                                          |
|                                                                      |
| \"company\": {                                                       |
|                                                                      |
| \"id\": \"comp_abc123\",                                             |
|                                                                      |
| \"name\": \"Reliance Industries Ltd\",                               |
|                                                                      |
| \"bse_code\": \"500325\",                                            |
|                                                                      |
| \"nse_symbol\": \"RELIANCE\",                                        |
|                                                                      |
| \"isin\": \"INE002A01018\",                                          |
|                                                                      |
| \"industry\": \"Oil & Gas\",                                         |
|                                                                      |
| \"sector\": \"Energy\",                                              |
|                                                                      |
| \"market_cap_cr\": 1850000,                                          |
|                                                                      |
| \"is_nifty_50\": true,                                               |
|                                                                      |
| \"is_nifty_500\": true                                               |
|                                                                      |
| },                                                                   |
|                                                                      |
| \"annual_reports\": \[                                               |
|                                                                      |
| {                                                                    |
|                                                                      |
| \"id\": \"ar_xyz789\",                                               |
|                                                                      |
| \"fiscal_year\": \"FY2024\",                                         |
|                                                                      |
| \"has_analysis\": true,                                              |
|                                                                      |
| \"analysis_id\": \"an_abc123\"                                       |
|                                                                      |
| },                                                                   |
|                                                                      |
| \...                                                                 |
|                                                                      |
| \],                                                                  |
|                                                                      |
| \"latest_analysis\": {                                               |
|                                                                      |
| \"risk_score\": 28,                                                  |
|                                                                      |
| \"risk_level\": \"low\",                                             |
|                                                                      |
| \"analyzed_at\": \"2026-01-15T08:00:00Z\"                            |
|                                                                      |
| }                                                                    |
|                                                                      |
| }                                                                    |
|                                                                      |
| }                                                                    |
+----------------------------------------------------------------------+

+----------------------------------------------------------------------+
| **GET** /api/v1/companies/{id}/peers                                 |
|                                                                      |
| Get peer companies for comparison                                    |
+----------------------------------------------------------------------+

+----------------------------------------------------------------------+
| // Request                                                           |
|                                                                      |
| GET /api/v1/companies/comp_abc123/peers?limit=5                      |
|                                                                      |
| // Response                                                          |
|                                                                      |
| {                                                                    |
|                                                                      |
| \"success\": true,                                                   |
|                                                                      |
| \"data\": {                                                          |
|                                                                      |
| \"target\": { \"id\": \"comp_abc123\", \"name\": \"Zee               |
| Entertainment\", \"risk_score\": 67 },                               |
|                                                                      |
| \"peers\": \[                                                        |
|                                                                      |
| { \"id\": \"comp_def456\", \"name\": \"Sun TV\", \"risk_score\": 28  |
| },                                                                   |
|                                                                      |
| { \"id\": \"comp_ghi789\", \"name\": \"TV18\", \"risk_score\": 42 }, |
|                                                                      |
| \...                                                                 |
|                                                                      |
| \],                                                                  |
|                                                                      |
| \"industry_average\": 45                                             |
|                                                                      |
| }                                                                    |
|                                                                      |
| }                                                                    |
+----------------------------------------------------------------------+

**10. Analysis Endpoints**

+----------------------------------------------------------------------+
| **POST** /api/v1/analyze                                             |
|                                                                      |
| Start new analysis (upload PDF or by company)                        |
+----------------------------------------------------------------------+

+----------------------------------------------------------------------+
| // Option A: By company ID                                           |
|                                                                      |
| {                                                                    |
|                                                                      |
| \"company_id\": \"comp_abc123\",                                     |
|                                                                      |
| \"fiscal_year\": \"FY2024\",                                         |
|                                                                      |
| \"options\": {                                                       |
|                                                                      |
| \"include_trends\": true, // Requires Pro+                           |
|                                                                      |
| \"trend_years\": 3,                                                  |
|                                                                      |
| \"include_peers\": true, // Requires Pro+                            |
|                                                                      |
| \"peer_count\": 5                                                    |
|                                                                      |
| }                                                                    |
|                                                                      |
| }                                                                    |
|                                                                      |
| // Option B: Upload PDF                                              |
|                                                                      |
| // Content-Type: multipart/form-data                                 |
|                                                                      |
| {                                                                    |
|                                                                      |
| \"file\": \<pdf_file\>,                                              |
|                                                                      |
| \"company_name\": \"Unknown Corp\", // Optional, for new companies   |
|                                                                      |
| \"fiscal_year\": \"FY2024\",                                         |
|                                                                      |
| \"options\": { \... }                                                |
|                                                                      |
| }                                                                    |
|                                                                      |
| // Response (async - returns job ID)                                 |
|                                                                      |
| {                                                                    |
|                                                                      |
| \"success\": true,                                                   |
|                                                                      |
| \"data\": {                                                          |
|                                                                      |
| \"job_id\": \"job_abc123\",                                          |
|                                                                      |
| \"status\": \"queued\",                                              |
|                                                                      |
| \"estimated_time_seconds\": 60,                                      |
|                                                                      |
| \"websocket_url\": \"wss://api.redflag.ai/ws/job/job_abc123\"        |
|                                                                      |
| }                                                                    |
|                                                                      |
| }                                                                    |
+----------------------------------------------------------------------+

+----------------------------------------------------------------------+
| **GET** /api/v1/analyze/{job_id}/status                              |
|                                                                      |
| Check analysis job status                                            |
+----------------------------------------------------------------------+

+----------------------------------------------------------------------+
| // Response                                                          |
|                                                                      |
| {                                                                    |
|                                                                      |
| \"success\": true,                                                   |
|                                                                      |
| \"data\": {                                                          |
|                                                                      |
| \"job_id\": \"job_abc123\",                                          |
|                                                                      |
| \"status\": \"processing\", //                                       |
| \'queued\'\|\'processing\'\|\'completed\'\|\'failed\'                |
|                                                                      |
| \"progress\": {                                                      |
|                                                                      |
| \"percent\": 45,                                                     |
|                                                                      |
| \"current_step\": \"Analyzing auditor report\",                      |
|                                                                      |
| \"steps_completed\": \[\"Text extraction\", \"Section detection\"\], |
|                                                                      |
| \"steps_remaining\": \[\"Red flag analysis\", \"Scoring\",           |
| \"Summary\"\]                                                        |
|                                                                      |
| },                                                                   |
|                                                                      |
| \"started_at\": \"2026-02-03T10:30:00Z\",                            |
|                                                                      |
| \"estimated_completion\": \"2026-02-03T10:31:00Z\"                   |
|                                                                      |
| }                                                                    |
|                                                                      |
| }                                                                    |
|                                                                      |
| // When completed                                                    |
|                                                                      |
| {                                                                    |
|                                                                      |
| \"success\": true,                                                   |
|                                                                      |
| \"data\": {                                                          |
|                                                                      |
| \"job_id\": \"job_abc123\",                                          |
|                                                                      |
| \"status\": \"completed\",                                           |
|                                                                      |
| \"analysis_id\": \"an_xyz789\",                                      |
|                                                                      |
| \"report_url\": \"/api/v1/reports/an_xyz789\"                        |
|                                                                      |
| }                                                                    |
|                                                                      |
| }                                                                    |
+----------------------------------------------------------------------+

**WebSocket Progress Updates**

+----------------------------------------------------------------------+
| // Connect to WebSocket for real-time updates                        |
|                                                                      |
| const ws = new                                                       |
| WebSocket(\'wss://api.redflag.ai/ws/job/job_abc123\');               |
|                                                                      |
| ws.onmessage = (event) =\> {                                         |
|                                                                      |
| const data = JSON.parse(event.data);                                 |
|                                                                      |
| // data.type: \'progress\' \| \'completed\' \| \'error\'             |
|                                                                      |
| // data.progress: { percent, current_step, \... }                    |
|                                                                      |
| // data.result: { analysis_id, \... } // when completed              |
|                                                                      |
| };                                                                   |
+----------------------------------------------------------------------+

**11. Report Endpoints**

+----------------------------------------------------------------------+
| **GET** /api/v1/reports/{analysis_id}                                |
|                                                                      |
| Get full analysis report                                             |
+----------------------------------------------------------------------+

+----------------------------------------------------------------------+
| // Response                                                          |
|                                                                      |
| {                                                                    |
|                                                                      |
| \"success\": true,                                                   |
|                                                                      |
| \"data\": {                                                          |
|                                                                      |
| \"analysis\": {                                                      |
|                                                                      |
| \"id\": \"an_xyz789\",                                               |
|                                                                      |
| \"risk_score\": 67,                                                  |
|                                                                      |
| \"risk_level\": \"elevated\",                                        |
|                                                                      |
| \"category_scores\": {                                               |
|                                                                      |
| \"auditor\": 45,                                                     |
|                                                                      |
| \"cash_flow\": 72,                                                   |
|                                                                      |
| \"related_party\": 58,                                               |
|                                                                      |
| \"promoter\": 85,                                                    |
|                                                                      |
| \"governance\": 35,                                                  |
|                                                                      |
| \"balance_sheet\": 28,                                               |
|                                                                      |
| \"revenue_quality\": 38,                                             |
|                                                                      |
| \"textual\": 42                                                      |
|                                                                      |
| },                                                                   |
|                                                                      |
| \"executive_summary\": \"Zee Entertainment shows elevated            |
| risk\...\",                                                          |
|                                                                      |
| \"analyzed_at\": \"2026-02-03T10:31:00Z\"                            |
|                                                                      |
| },                                                                   |
|                                                                      |
| \"company\": {                                                       |
|                                                                      |
| \"id\": \"comp_abc123\",                                             |
|                                                                      |
| \"name\": \"Zee Entertainment Enterprises Ltd\",                     |
|                                                                      |
| \"bse_code\": \"505537\",                                            |
|                                                                      |
| \"nse_symbol\": \"ZEEL\"                                             |
|                                                                      |
| },                                                                   |
|                                                                      |
| \"annual_report\": {                                                 |
|                                                                      |
| \"id\": \"ar_def456\",                                               |
|                                                                      |
| \"fiscal_year\": \"FY2024\",                                         |
|                                                                      |
| \"pdf_url\": \"https://storage.redflag.ai/\...\"                     |
|                                                                      |
| },                                                                   |
|                                                                      |
| \"red_flags\": {                                                     |
|                                                                      |
| \"summary\": {                                                       |
|                                                                      |
| \"total\": 54,                                                       |
|                                                                      |
| \"triggered\": 12,                                                   |
|                                                                      |
| \"critical\": 2,                                                     |
|                                                                      |
| \"high\": 5,                                                         |
|                                                                      |
| \"medium\": 5,                                                       |
|                                                                      |
| \"low\": 0                                                           |
|                                                                      |
| },                                                                   |
|                                                                      |
| \"flags\": \[                                                        |
|                                                                      |
| {                                                                    |
|                                                                      |
| \"id\": \"flag_001\",                                                |
|                                                                      |
| \"flag_code\": \"PROMOTER_PLEDGE_HIGH\",                             |
|                                                                      |
| \"flag_name\": \"Promoter Pledge Exceeds 50%\",                      |
|                                                                      |
| \"category\": \"promoter\",                                          |
|                                                                      |
| \"severity\": \"CRITICAL\",                                          |
|                                                                      |
| \"is_triggered\": true,                                              |
|                                                                      |
| \"evidence\": \"As on 31st March 2024, 62.1% of\...\",               |
|                                                                      |
| \"page_number\": 127,                                                |
|                                                                      |
| \"metric_value\": 62.1,                                              |
|                                                                      |
| \"threshold_value\": 50.0,                                           |
|                                                                      |
| \"yoy_change\": 4.2                                                  |
|                                                                      |
| },                                                                   |
|                                                                      |
| \...                                                                 |
|                                                                      |
| \]                                                                   |
|                                                                      |
| }                                                                    |
|                                                                      |
| }                                                                    |
|                                                                      |
| }                                                                    |
+----------------------------------------------------------------------+

+----------------------------------------------------------------------+
| **GET** /api/v1/reports/{analysis_id}/flags                          |
|                                                                      |
| Get red flags only                                                   |
+----------------------------------------------------------------------+
| **GET** /api/v1/reports/{analysis_id}/flags/{flag_id}                |
|                                                                      |
| Get single flag detail                                               |
+----------------------------------------------------------------------+

+----------------------------------------------------------------------+
| **GET** /api/v1/reports/{analysis_id}/trends                         |
|                                                                      |
| Get multi-year trend data                                            |
+----------------------------------------------------------------------+

+----------------------------------------------------------------------+
| // Response (Pro+ only)                                              |
|                                                                      |
| {                                                                    |
|                                                                      |
| \"success\": true,                                                   |
|                                                                      |
| \"data\": {                                                          |
|                                                                      |
| \"years\": \[\"FY2020\", \"FY2021\", \"FY2022\", \"FY2023\",         |
| \"FY2024\"\],                                                        |
|                                                                      |
| \"risk_scores\": \[28, 35, 48, 58, 67\],                             |
|                                                                      |
| \"events\": \[                                                       |
|                                                                      |
| { \"year\": \"FY2021\", \"event\": \"Auditor changed\", \"type\":    |
| \"auditor\" },                                                       |
|                                                                      |
| { \"year\": \"FY2022\", \"event\": \"CFO resigned\", \"type\":       |
| \"governance\" },                                                    |
|                                                                      |
| \...                                                                 |
|                                                                      |
| \],                                                                  |
|                                                                      |
| \"metrics\": {                                                       |
|                                                                      |
| \"promoter_pledge\": \[32, 38, 45, 58, 62\],                         |
|                                                                      |
| \"cfo_pat_ratio\": \[0.95, 0.72, 0.58, 0.35, 0.25\],                 |
|                                                                      |
| \"receivable_days\": \[68, 72, 80, 92, 98\],                         |
|                                                                      |
| \"debt_equity\": \[0.9, 1.0, 1.2, 1.4, 1.5\]                         |
|                                                                      |
| }                                                                    |
|                                                                      |
| }                                                                    |
|                                                                      |
| }                                                                    |
+----------------------------------------------------------------------+

+----------------------------------------------------------------------+
| **GET** /api/v1/reports/{analysis_id}/spiderweb                      |
|                                                                      |
| Get related party spiderweb data                                     |
+----------------------------------------------------------------------+

+----------------------------------------------------------------------+
| // Response                                                          |
|                                                                      |
| {                                                                    |
|                                                                      |
| \"success\": true,                                                   |
|                                                                      |
| \"data\": {                                                          |
|                                                                      |
| \"nodes\": \[                                                        |
|                                                                      |
| { \"id\": \"main\", \"name\": \"Zee Entertainment\", \"type\":       |
| \"company\", \"size\": 100 },                                        |
|                                                                      |
| { \"id\": \"rp1\", \"name\": \"Essel Infraprojects\", \"type\":      |
| \"promoter_group\", \"size\": 45 },                                  |
|                                                                      |
| { \"id\": \"rp2\", \"name\": \"Dish TV\", \"type\": \"subsidiary\",  |
| \"size\": 30 },                                                      |
|                                                                      |
| \...                                                                 |
|                                                                      |
| \],                                                                  |
|                                                                      |
| \"links\": \[                                                        |
|                                                                      |
| { \"source\": \"main\", \"target\": \"rp1\", \"value\": 847,         |
| \"type\": \"loan\", \"risk\": \"high\" },                            |
|                                                                      |
| { \"source\": \"main\", \"target\": \"rp2\", \"value\": 567,         |
| \"type\": \"sales\", \"risk\": \"medium\" },                         |
|                                                                      |
| \...                                                                 |
|                                                                      |
| \],                                                                  |
|                                                                      |
| \"total_rpt_value\": 2847,                                           |
|                                                                      |
| \"rpt_percent_of_revenue\": 14.2                                     |
|                                                                      |
| }                                                                    |
|                                                                      |
| }                                                                    |
+----------------------------------------------------------------------+

**12. User Endpoints**

+----------------------------------------------------------------------+
| **GET** /api/v1/user/me                                              |
|                                                                      |
| Get current user profile                                             |
+----------------------------------------------------------------------+

+----------------------------------------------------------------------+
| // Response                                                          |
|                                                                      |
| {                                                                    |
|                                                                      |
| \"success\": true,                                                   |
|                                                                      |
| \"data\": {                                                          |
|                                                                      |
| \"user\": {                                                          |
|                                                                      |
| \"id\": \"usr_abc123\",                                              |
|                                                                      |
| \"email\": \"manthan@example.com\",                                  |
|                                                                      |
| \"name\": \"Manthan Patel\",                                         |
|                                                                      |
| \"avatar_url\": \"https://\...\",                                    |
|                                                                      |
| \"subscription_tier\": \"pro\",                                      |
|                                                                      |
| \"subscription_expires_at\": \"2026-03-03T00:00:00Z\"                |
|                                                                      |
| },                                                                   |
|                                                                      |
| \"usage\": {                                                         |
|                                                                      |
| \"reports_used\": 7,                                                 |
|                                                                      |
| \"reports_limit\": 15,                                               |
|                                                                      |
| \"reports_reset_at\": \"2026-03-01T00:00:00Z\"                       |
|                                                                      |
| }                                                                    |
|                                                                      |
| }                                                                    |
|                                                                      |
| }                                                                    |
+----------------------------------------------------------------------+

+----------------------------------------------------------------------+
| **PUT** /api/v1/user/me                                              |
|                                                                      |
| Update user profile                                                  |
+----------------------------------------------------------------------+
| **PUT** /api/v1/user/me/password                                     |
|                                                                      |
| Change password                                                      |
+----------------------------------------------------------------------+
| **GET** /api/v1/user/me/reports                                      |
|                                                                      |
| Get user\'s recent reports                                           |
+----------------------------------------------------------------------+

+----------------------------------------------------------------------+
| // Response                                                          |
|                                                                      |
| {                                                                    |
|                                                                      |
| \"success\": true,                                                   |
|                                                                      |
| \"data\": {                                                          |
|                                                                      |
| \"reports\": \[                                                      |
|                                                                      |
| {                                                                    |
|                                                                      |
| \"analysis_id\": \"an_xyz789\",                                      |
|                                                                      |
| \"company_name\": \"Zee Entertainment\",                             |
|                                                                      |
| \"fiscal_year\": \"FY2024\",                                         |
|                                                                      |
| \"risk_score\": 67,                                                  |
|                                                                      |
| \"risk_level\": \"elevated\",                                        |
|                                                                      |
| \"accessed_at\": \"2026-02-03T10:35:00Z\"                            |
|                                                                      |
| },                                                                   |
|                                                                      |
| \...                                                                 |
|                                                                      |
| \]                                                                   |
|                                                                      |
| }                                                                    |
|                                                                      |
| }                                                                    |
+----------------------------------------------------------------------+

+----------------------------------------------------------------------+
| **GET** /api/v1/user/me/alerts                                       |
|                                                                      |
| Get user\'s alerts                                                   |
+----------------------------------------------------------------------+
| **PUT** /api/v1/user/me/alerts/{id}/read                             |
|                                                                      |
| Mark alert as read                                                   |
+----------------------------------------------------------------------+
| **DELETE** /api/v1/user/me/alerts/{id}                               |
|                                                                      |
| Dismiss alert                                                        |
+----------------------------------------------------------------------+

**13. Watchlist Endpoints**

+----------------------------------------------------------------------+
| **GET** /api/v1/watchlist                                            |
|                                                                      |
| Get user\'s watchlist                                                |
+----------------------------------------------------------------------+

+----------------------------------------------------------------------+
| // Response                                                          |
|                                                                      |
| {                                                                    |
|                                                                      |
| \"success\": true,                                                   |
|                                                                      |
| \"data\": {                                                          |
|                                                                      |
| \"watchlist\": \[                                                    |
|                                                                      |
| {                                                                    |
|                                                                      |
| \"id\": \"watch_abc123\",                                            |
|                                                                      |
| \"company\": {                                                       |
|                                                                      |
| \"id\": \"comp_xyz789\",                                             |
|                                                                      |
| \"name\": \"Zee Entertainment\",                                     |
|                                                                      |
| \"bse_code\": \"505537\"                                             |
|                                                                      |
| },                                                                   |
|                                                                      |
| \"latest_risk_score\": 67,                                           |
|                                                                      |
| \"score_change\": 9,                                                 |
|                                                                      |
| \"last_analyzed_at\": \"2026-02-03T10:31:00Z\",                      |
|                                                                      |
| \"alert_config\": {                                                  |
|                                                                      |
| \"on_new_ar\": true,                                                 |
|                                                                      |
| \"on_score_change\": 10,                                             |
|                                                                      |
| \"on_critical_flag\": true                                           |
|                                                                      |
| }                                                                    |
|                                                                      |
| },                                                                   |
|                                                                      |
| \...                                                                 |
|                                                                      |
| \],                                                                  |
|                                                                      |
| \"count\": 8,                                                        |
|                                                                      |
| \"limit\": 10 // Based on subscription tier                          |
|                                                                      |
| }                                                                    |
|                                                                      |
| }                                                                    |
+----------------------------------------------------------------------+

+----------------------------------------------------------------------+
| **POST** /api/v1/watchlist                                           |
|                                                                      |
| Add company to watchlist                                             |
+----------------------------------------------------------------------+

+----------------------------------------------------------------------+
| // Request                                                           |
|                                                                      |
| {                                                                    |
|                                                                      |
| \"company_id\": \"comp_xyz789\",                                     |
|                                                                      |
| \"alert_config\": {                                                  |
|                                                                      |
| \"on_new_ar\": true,                                                 |
|                                                                      |
| \"on_score_change\": 10,                                             |
|                                                                      |
| \"on_critical_flag\": true,                                          |
|                                                                      |
| \"on_pledge_threshold\": 50                                          |
|                                                                      |
| }                                                                    |
|                                                                      |
| }                                                                    |
+----------------------------------------------------------------------+

+----------------------------------------------------------------------+
| **PUT** /api/v1/watchlist/{id}                                       |
|                                                                      |
| Update watchlist item settings                                       |
+----------------------------------------------------------------------+
| **DELETE** /api/v1/watchlist/{id}                                    |
|                                                                      |
| Remove from watchlist                                                |
+----------------------------------------------------------------------+

**14. Portfolio Endpoints**

+----------------------------------------------------------------------+
| **GET** /api/v1/portfolio                                            |
|                                                                      |
| Get user\'s portfolio holdings                                       |
+----------------------------------------------------------------------+

+----------------------------------------------------------------------+
| // Response                                                          |
|                                                                      |
| {                                                                    |
|                                                                      |
| \"success\": true,                                                   |
|                                                                      |
| \"data\": {                                                          |
|                                                                      |
| \"summary\": {                                                       |
|                                                                      |
| \"total_holdings\": 15,                                              |
|                                                                      |
| \"total_value\": 2450000,                                            |
|                                                                      |
| \"risk_distribution\": {                                             |
|                                                                      |
| \"low\": 9,                                                          |
|                                                                      |
| \"medium\": 4,                                                       |
|                                                                      |
| \"high\": 2                                                          |
|                                                                      |
| }                                                                    |
|                                                                      |
| },                                                                   |
|                                                                      |
| \"holdings\": \[                                                     |
|                                                                      |
| {                                                                    |
|                                                                      |
| \"id\": \"hold_abc123\",                                             |
|                                                                      |
| \"company\": { \"id\": \"comp_xyz\", \"name\": \"HDFC Bank\" },      |
|                                                                      |
| \"quantity\": 100,                                                   |
|                                                                      |
| \"avg_price\": 1650.50,                                              |
|                                                                      |
| \"current_value\": 168000,                                           |
|                                                                      |
| \"risk_score\": 22,                                                  |
|                                                                      |
| \"risk_level\": \"low\"                                              |
|                                                                      |
| },                                                                   |
|                                                                      |
| \...                                                                 |
|                                                                      |
| \]                                                                   |
|                                                                      |
| }                                                                    |
|                                                                      |
| }                                                                    |
+----------------------------------------------------------------------+

+----------------------------------------------------------------------+
| **POST** /api/v1/portfolio/import                                    |
|                                                                      |
| Import holdings from CSV                                             |
+----------------------------------------------------------------------+

+----------------------------------------------------------------------+
| // Request - multipart/form-data                                     |
|                                                                      |
| {                                                                    |
|                                                                      |
| \"file\": \<csv_file\>,                                              |
|                                                                      |
| \"broker\": \"zerodha\" //                                           |
| \'zerodha\'\|\'groww\'\|\'upstox\'\|\'angel\'                        |
|                                                                      |
| }                                                                    |
|                                                                      |
| // Response                                                          |
|                                                                      |
| {                                                                    |
|                                                                      |
| \"success\": true,                                                   |
|                                                                      |
| \"data\": {                                                          |
|                                                                      |
| \"imported\": 12,                                                    |
|                                                                      |
| \"skipped\": 3,                                                      |
|                                                                      |
| \"skipped_reasons\": \[                                              |
|                                                                      |
| { \"symbol\": \"UNKNOWN\", \"reason\": \"Company not found\" }       |
|                                                                      |
| \]                                                                   |
|                                                                      |
| }                                                                    |
|                                                                      |
| }                                                                    |
+----------------------------------------------------------------------+

+----------------------------------------------------------------------+
| **POST** /api/v1/portfolio/scan                                      |
|                                                                      |
| Scan all portfolio holdings                                          |
+----------------------------------------------------------------------+

+----------------------------------------------------------------------+
| // Response (async - returns job ID)                                 |
|                                                                      |
| {                                                                    |
|                                                                      |
| \"success\": true,                                                   |
|                                                                      |
| \"data\": {                                                          |
|                                                                      |
| \"job_id\": \"job_scan123\",                                         |
|                                                                      |
| \"holdings_to_scan\": 15,                                            |
|                                                                      |
| \"cached\": 12,                                                      |
|                                                                      |
| \"fresh_required\": 3,                                               |
|                                                                      |
| \"estimated_time_seconds\": 180                                      |
|                                                                      |
| }                                                                    |
|                                                                      |
| }                                                                    |
+----------------------------------------------------------------------+

+----------------------------------------------------------------------+
| **POST** /api/v1/portfolio/holdings                                  |
|                                                                      |
| Add single holding manually                                          |
+----------------------------------------------------------------------+
| **PUT** /api/v1/portfolio/holdings/{id}                              |
|                                                                      |
| Update holding                                                       |
+----------------------------------------------------------------------+
| **DELETE** /api/v1/portfolio/holdings/{id}                           |
|                                                                      |
| Remove holding                                                       |
+----------------------------------------------------------------------+
| **DELETE** /api/v1/portfolio                                         |
|                                                                      |
| Clear entire portfolio                                               |
+----------------------------------------------------------------------+

**16. Error Codes & Rate Limiting**

**16.1 HTTP Status Codes**

  ----------------------- ----------------------- -----------------------
  **Code**                **Meaning**             **When Used**

  200                     OK                      Successful request

  201                     Created                 Resource created
                                                  (signup, new analysis)

  400                     Bad Request             Invalid request body or
                                                  parameters

  401                     Unauthorized            Missing or invalid auth
                                                  token

  403                     Forbidden               Valid token but
                                                  insufficient
                                                  permissions

  404                     Not Found               Resource doesn\'t exist

  409                     Conflict                Resource already exists
                                                  (duplicate email)

  422                     Unprocessable           Validation error

  429                     Too Many Requests       Rate limit exceeded

  500                     Server Error            Internal error
  ----------------------- ----------------------- -----------------------

**16.2 Error Codes**

  ----------------------------------- -----------------------------------
  **Code**                            **Message**

  AUTH_INVALID_CREDENTIALS            Invalid email or password

  AUTH_TOKEN_EXPIRED                  Token has expired, please login
                                      again

  AUTH_TOKEN_INVALID                  Invalid authentication token

  USER_NOT_FOUND                      User not found

  USER_EMAIL_EXISTS                   Email already registered

  COMPANY_NOT_FOUND                   Company not found

  ANALYSIS_NOT_FOUND                  Analysis not found

  SUBSCRIPTION_REQUIRED               This feature requires Pro/Premium
                                      subscription

  USAGE_LIMIT_EXCEEDED                Monthly report limit exceeded

  RATE_LIMIT_EXCEEDED                 Too many requests, please slow down

  FILE_TOO_LARGE                      PDF file exceeds 100MB limit

  FILE_INVALID_TYPE                   Only PDF files are accepted

  PROCESSING_FAILED                   Analysis processing failed
  ----------------------------------- -----------------------------------

**16.3 Rate Limit Headers**

+----------------------------------------------------------------------+
| // Response headers                                                  |
|                                                                      |
| X-RateLimit-Limit: 60                                                |
|                                                                      |
| X-RateLimit-Remaining: 45                                            |
|                                                                      |
| X-RateLimit-Reset: 1709856060 // Unix timestamp                      |
|                                                                      |
| // When rate limited (429 response)                                  |
|                                                                      |
| Retry-After: 60 // Seconds until reset                               |
+----------------------------------------------------------------------+

**Technical Documentation Complete**

**PART D: TECH STACK & COSTS**

**7. Complete Tech Stack**

  -----------------------------------------------------------------------
  **Layer**               **Technology**          **Cost/Month**
  ----------------------- ----------------------- -----------------------
  Frontend                Next.js 14 + Tailwind + Free
                          shadcn/ui               

  Charts                  Recharts + D3.js        Free

  Backend                 Python FastAPI + Celery Free

  Database                PostgreSQL (Supabase)   Rs.0-2000

  Cache                   Redis (Upstash)         Rs.0-500

  Storage                 Cloudflare R2           Rs.0-500

  PDF Native              PyMuPDF                 Free

  PDF OCR                 Surya OCR + Google      Rs.0.12/pg
                          Vision                  

  LLM Primary             Claude 3.5 Haiku        Rs.8/1M tokens

  LLM Budget              Gemini 1.5 Flash        Rs.6/1M tokens

  Hosting FE              Vercel                  Rs.0-1500

  Hosting BE              Railway                 Rs.500-3000

  GPU                     Modal/RunPod (OCR)      Rs.500-3000

  Payments                Razorpay                2% per txn

  Email                   SendGrid                Rs.0-1500

  Auth                    Supabase Auth           Included
  -----------------------------------------------------------------------

**8. Cost Per Analysis**

**Single Annual Report**

  -----------------------------------------------------------------------
  **Component**           **Calculation**         **Cost**
  ----------------------- ----------------------- -----------------------
  Text Extraction (native PyMuPDF                 Rs.0
  60%)                                            

  OCR (scanned 40%)       280 pages x Rs.0.005    Rs.1.40

  OCR Fallback (10%)      28 pages x Rs.0.12      Rs.3.36

  Section Detection       30K tokens LLM          Rs.0.24

  Boundary Refinement     60K tokens LLM          Rs.0.48

  Rule-based Flags (48)   Pure Python             Rs.0

  LLM Flags (6)           70K tokens              Rs.0.56

  Executive Summary       10K tokens              Rs.0.08

  TOTAL                                           Rs.6-8
  -----------------------------------------------------------------------

+----------------------------------------------------------------------+
| **With Caching**                                                     |
|                                                                      |
| NIFTY 500 pre-computed (one-time Rs.3,500) = 85% of requests served  |
| at Rs.0. Average cost per user request: Rs.2-3.                      |
+======================================================================+

**Monthly Infrastructure**

  -----------------------------------------------------------------------
  **Service**                         **Cost**
  ----------------------------------- -----------------------------------
  Vercel (Frontend)                   Rs.1,500

  Railway (Backend)                   Rs.2,500

  Supabase (DB)                       Rs.2,000

  Upstash (Redis)                     Rs.500

  R2 (Storage)                        Rs.500

  SendGrid (Email)                    Rs.1,500

  GPU (OCR)                           Rs.2,000

  TOTAL                               Rs.10,500
  -----------------------------------------------------------------------

**9. Subscription Model**

  -----------------------------------------------------------------------
  **Feature**       **Free (Rs.0)**   **Pro (Rs.599)**  **Premium
                                                        (Rs.1499)**
  ----------------- ----------------- ----------------- -----------------
  Reports/month     3                 15                50

  Companies         NIFTY 500         Any               Any

  Red Flag Details  Count only        Full              Full + history

  Page References   No                Yes               Yes

  Trends            No                2 years           5 years

  Peers             No                3 peers           10 peers

  Spiderweb         No                Yes               Interactive

  Portfolio Scan    No                No                Yes

  Watchlist         No                10                50

  Alerts            No                Weekly            Real-time

  API               No                No                Yes
  -----------------------------------------------------------------------

**Unit Economics**

  ----------------------------------------------------------------------------
  **User**    **Reports**   **Fresh %** **Cost**    **Revenue**   **Margin**
  ----------- ------------- ----------- ----------- ------------- ------------
  Free        2             0%          Rs.0        Rs.0          \-

  Pro         10            30%         Rs.21       Rs.599        96%

  Premium     30            40%         Rs.84       Rs.1499       94%
  ----------------------------------------------------------------------------

**10. Development Roadmap**

**Phase 1: MVP (Weeks 1-8)**

- Week 1-2: PDF pipeline (PyMuPDF + Surya + Vision)

- Week 3-4: LLM section detection

- Week 5-6: Red flag engine (25 flags)

- Week 7-8: Frontend + Deploy

**Phase 2: Visual Excellence (Weeks 9-14)**

- Risk gauge, spider chart, red flag cards

- Related Party Spiderweb (D3.js)

- Trends, peers, subscriptions

**Phase 3: Scale (Weeks 15-24)**

- Pre-compute NIFTY 500 cache

- Portfolio scanner, watchlist, alerts

- Fraud database (50 cases)

- Mobile PWA, API

**Complete Specification Ready**

This document contains:

8 Features with Implementation Details

12 App Pages with Visual Wireframes

LLM-Based PDF Pipeline (No Regex)

Complete Tech Stack

Detailed Cost Analysis

*\-\-- End of Document \-\--*
