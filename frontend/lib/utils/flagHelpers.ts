/**
 * Flag Helpers - Educational Content System
 *
 * Provides educational content, similar fraud cases, and investor guidance
 * for all 54 red flags in the system
 */

export type FlagSeverity = 'CRITICAL' | 'HIGH' | 'MEDIUM' | 'LOW';
export type FlagCategory =
  | 'Auditor'
  | 'Cash Flow'
  | 'Related Party'
  | 'Promoter'
  | 'Governance'
  | 'Balance Sheet'
  | 'Revenue'
  | 'Textual';

export interface SimilarCase {
  company: string;
  year: string;
  description: string;
  outcome: string;
  impact: string;
}

export interface FlagEducation {
  flagNumber: number;
  title: string;
  category: FlagCategory;
  severity: FlagSeverity;
  whatItMeans: string;
  whyItMatters: string;
  redFlagsToWatch: string[];
  similarCases: SimilarCase[];
  investorActions: string[];
  detectionMethod: string;
}

/**
 * Educational content for all red flags
 * Starting with top 10 critical/high severity flags
 */
export const FLAG_EDUCATION: Record<number, FlagEducation> = {
  // CRITICAL FLAGS - Cash Flow Category
  1: {
    flagNumber: 1,
    title: 'Profit Growing but CFO Flat/Declining',
    category: 'Cash Flow',
    severity: 'CRITICAL',
    whatItMeans:
      'This flag indicates that while the company is reporting increasing Profit After Tax (PAT), its Cash Flow from Operations (CFO) is either stagnant or declining. This divergence suggests that the reported profits may not be converting into actual cash, which could indicate aggressive accounting practices, revenue recognition issues, or earnings manipulation through accruals and working capital management.',
    whyItMatters:
      'Cash flow is the lifeblood of any business. A company can manipulate profits through accounting techniques, but cash flow is much harder to fabricate. When profits grow but cash flow does not, it raises serious questions about the quality and sustainability of earnings. This pattern was observed in several major accounting scandals where companies inflated profits while actual cash generation declined.',
    redFlagsToWatch: [
      'CFO/PAT ratio declining below 0.8 for two consecutive years',
      'Increasing gap between net income and operating cash flow',
      'Rising accounts receivable growing faster than revenue',
      'Inventory buildup without corresponding sales growth',
      'Unusual changes in working capital accounts',
    ],
    similarCases: [
      {
        company: 'Satyam Computer Services',
        year: '2009',
        description:
          'Satyam reported strong profits and revenue growth for years while its actual cash flows did not match. The company fabricated ₹5,040 crore in cash and bank balances on its balance sheet. The CFO-to-PAT ratio had declined significantly in the years leading up to the scandal.',
        outcome: 'Founder Ramalinga Raju confessed to ₹7,136 crore fraud',
        impact: 'Stock fell 78%, investors lost ₹14,000 crore, company sold to Tech Mahindra',
      },
      {
        company: 'Gitanjali Gems',
        year: '2018',
        description:
          'Despite reporting profits, the company\'s operating cash flows were consistently negative. Investigation revealed fraudulent letter of credit transactions worth ₹6,500 crore. The company was booking revenues without actual cash collections.',
        outcome: 'Founder Mehul Choksi fled the country, company defaulted on loans',
        impact: 'Banks suffered losses of over ₹5,000 crore, trading suspended',
      },
    ],
    investorActions: [
      'Immediately review the cash flow statement in detail',
      'Calculate CFO/PAT ratio for the last 3 years - flag if below 0.8',
      'Analyze working capital changes and their business justification',
      'Check Days Sales Outstanding (DSO) trend - rising DSO is concerning',
      'Review management\'s explanation in annual report',
      'Consider reducing position or avoiding the stock until clarified',
      'Monitor for further deterioration in subsequent quarters',
    ],
    detectionMethod:
      'Rule-based: Calculated by comparing PAT growth rate with CFO growth rate over current and previous year. Triggered when PAT grows by >10% but CFO is flat (±5%) or declining.',
  },

  // HIGH FLAGS - Cash Flow Category
  2: {
    flagNumber: 2,
    title: 'Working Capital Buildup',
    category: 'Cash Flow',
    severity: 'HIGH',
    whatItMeans:
      'Working capital (inventory + receivables - payables) is increasing significantly faster than revenue growth. This suggests the company is tying up more cash in operations, which could indicate slowing collections, inventory accumulation, or aggressive revenue recognition practices. It may also signal weakening business fundamentals or attempts to inflate current assets.',
    whyItMatters:
      'Excessive working capital buildup consumes cash that could otherwise be used for growth, dividends, or debt repayment. It often precedes write-offs of uncollectible receivables or obsolete inventory. A sudden spike in working capital relative to revenue is a classic early warning sign of earnings quality issues and potential overstatement of assets.',
    redFlagsToWatch: [
      'Working capital growing 2x faster than revenue',
      'Days Sales Outstanding (DSO) increasing beyond 60 days',
      'Inventory days increasing without operational justification',
      'Accounts payable days declining (indicating supplier concerns)',
      'Large provisions for doubtful debts in subsequent periods',
    ],
    similarCases: [
      {
        company: 'PC Jeweller',
        year: '2018',
        description:
          'The company showed massive inventory and receivables buildup that was disproportionate to its sales growth. Inventory increased to ₹6,170 crore while sales remained flat. Later investigations revealed the company had inflated inventory values and booked fake sales to related parties.',
        outcome: 'Stock fell 95%, auditors resigned citing misstatements',
        impact: 'Market cap eroded from ₹11,500 crore to ₹500 crore',
      },
      {
        company: 'Manpasand Beverages',
        year: '2019',
        description:
          'Working capital swelled to 120% of sales from 40% in just two years. The company was booking sales through distributors who were not actually selling the products. Inventory and receivables piled up, later written off as fraudulent.',
        outcome: 'Management arrested for ₹800 crore fraud, stock delisted',
        impact: 'Investors lost 99% of their investment',
      },
    ],
    investorActions: [
      'Calculate working capital as % of sales for last 3 years',
      'Compare DSO, DIO (Days Inventory Outstanding), and DPO trends',
      'Verify if inventory buildup is due to seasonal factors or new product launches',
      'Check for provisioning in subsequent quarters for bad debts',
      'Read management commentary on working capital in earnings calls',
      'Flag for further investigation if working capital >25% of annual sales',
      'Avoid companies with unexplained working capital spikes',
    ],
    detectionMethod:
      'Rule-based: Calculated by comparing working capital growth rate with revenue growth rate. Triggered when working capital increases by >20% while revenue grows by <10%.',
  },

  // HIGH FLAGS - Balance Sheet Category
  3: {
    flagNumber: 3,
    title: 'Debt Levels Increasing',
    category: 'Balance Sheet',
    severity: 'HIGH',
    whatItMeans:
      'Total debt (short-term + long-term borrowings) has increased significantly, often accompanied by rising debt-to-equity ratio. This indicates the company is taking on more leverage, which increases financial risk and interest burden. Rapid debt accumulation can signal that the business is not generating enough internal cash to fund operations or growth.',
    whyItMatters:
      'High debt levels make companies vulnerable to economic downturns, interest rate increases, and operational setbacks. Excessive leverage can lead to debt servicing difficulties, covenant breaches, and in extreme cases, bankruptcy. Investors need to assess whether the debt is being used productively for growth or simply to sustain operations.',
    redFlagsToWatch: [
      'Debt-to-equity ratio exceeding 2.0 or increasing rapidly',
      'Interest coverage ratio (EBIT/Interest) below 2.5',
      'Short-term debt exceeding current assets',
      'Debt used for working capital rather than capital expenditure',
      'Frequent refinancing or restructuring of debt',
    ],
    similarCases: [
      {
        company: 'IL&FS',
        year: '2018',
        description:
          'Infrastructure Leasing & Financial Services accumulated debt of ₹91,000 crore with poor asset-liability management. The company was using short-term debt to fund long-term projects. When the refinancing cycle broke, the company defaulted on obligations, triggering a systemic crisis.',
        outcome: 'Defaulted on debt, government superseded board, NCLT proceedings',
        impact: 'Contagion effect on NBFC sector, credit freeze in markets',
      },
      {
        company: 'Zee Entertainment (Essel Group)',
        year: '2019',
        description:
          'The promoter group took on debt of ₹7,000+ crore backed by pledged shares. As stock prices fell, lenders demanded margin calls. The group scrambled to repay debt, causing governance concerns and investor panic.',
        outcome: 'Promoter stake diluted, merger with Sony collapsed',
        impact: 'Stock fell 60%, investor wealth eroded significantly',
      },
    ],
    investorActions: [
      'Calculate debt-to-equity ratio and compare with industry average',
      'Assess interest coverage ratio - flag if below 3.0',
      'Check debt maturity profile for near-term repayment obligations',
      'Analyze cash flow adequacy for debt servicing',
      'Review credit ratings and any recent downgrades',
      'Understand the purpose of debt - capex is better than working capital',
      'Avoid companies with deteriorating debt metrics without clear plans',
    ],
    detectionMethod:
      'Rule-based: Monitors total debt levels and debt-to-equity ratio. Triggered when debt increases by >30% year-over-year or debt-to-equity ratio exceeds 1.5.',
  },

  // MEDIUM FLAGS - Promoter Category
  4: {
    flagNumber: 4,
    title: 'High Promoter Pledging',
    category: 'Promoter',
    severity: 'MEDIUM',
    whatItMeans:
      'A significant portion of promoter shareholding is pledged as collateral for loans. This indicates that promoters may be facing liquidity constraints or using their shares to raise funds for purposes outside the company. High pledging creates a risk of forced share sales if stock prices fall below certain levels, potentially triggering a downward spiral.',
    whyItMatters:
      'Promoter pledging reduces their skin in the game and creates conflict of interest. If the stock price falls, lenders can sell pledged shares, causing further price decline and loss of promoter control. It also signals that promoters may lack confidence in the business or are diverting funds to other ventures. Historical data shows many companies with high pledging have suffered governance crises.',
    redFlagsToWatch: [
      'Pledged shares exceeding 50% of promoter holding',
      'Increasing pledge levels over consecutive quarters',
      'Pledging by multiple promoter entities simultaneously',
      'Stock price volatility coinciding with pledge announcements',
      'Lack of disclosure about end-use of funds raised via pledging',
    ],
    similarCases: [
      {
        company: 'Yes Bank',
        year: '2020',
        description:
          'Founder Rana Kapoor had pledged nearly 100% of his stake. As the bank\'s asset quality deteriorated and stock fell, lenders invoked pledges, triggering a liquidity crisis. The promoter\'s loss of control exacerbated the crisis.',
        outcome: 'RBI moratorium, government bailout via SBI, founder arrested',
        impact: 'Depositors faced withdrawal limits, stock fell 95%',
      },
      {
        company: 'DHFL',
        year: '2019',
        description:
          'Promoters had pledged 79% of their shareholding. When the NBFC faced liquidity stress, pledge invocation fears caused stock to crash. The pledging indicated promoters were funding other group ventures rather than strengthening the core business.',
        outcome: 'Company went into bankruptcy, lenders took control',
        impact: 'Shareholders lost everything, creditors recovered partial dues',
      },
    ],
    investorActions: [
      'Check pledging percentage in quarterly shareholding patterns',
      'Monitor trends - increasing pledging is more concerning than stable levels',
      'Look for explanations in corporate announcements',
      'Assess promoter track record and business performance',
      'Consider reducing exposure if pledging exceeds 50%',
      'Check if company has strong fundamentals despite pledging',
      'Avoid companies with both high pledging and weak cash flows',
    ],
    detectionMethod:
      'Data extraction: Extracted from shareholding pattern disclosures in annual reports. Triggered when pledged shares exceed 40% of promoter holding.',
  },

  // MEDIUM FLAGS - Auditor Category
  5: {
    flagNumber: 5,
    title: 'Auditor Changed Recently',
    category: 'Auditor',
    severity: 'MEDIUM',
    whatItMeans:
      'The company has changed its statutory auditor, particularly if this is the second change within 3 years. While auditor rotation is sometimes mandatory, frequent changes or changes without clear explanation can be a red flag. It may indicate disagreements over accounting treatments, auditor resignation due to irregularities, or management\'s attempt to find more "agreeable" auditors.',
    whyItMatters:
      'Auditors are the gatekeepers of financial statement integrity. When they resign or are replaced frequently, it often signals underlying issues with financial reporting, internal controls, or management integrity. Many corporate frauds were preceded by auditor changes or qualifications that management tried to suppress by switching auditors.',
    redFlagsToWatch: [
      'Auditor resignation rather than completion of term',
      'Second or third auditor change within 5 years',
      'Change from Big 4 to smaller audit firm',
      'Lack of detailed explanation for the change',
      'Previous auditor\'s qualification or adverse opinion',
    ],
    similarCases: [
      {
        company: 'Satyam Computer Services',
        year: '2009',
        description:
          'PricewaterhouseCoopers (PwC) was the auditor throughout the fraud period but failed to detect the ₹7,136 crore scam. Post-fraud, there was intense scrutiny of auditor complicity. The case highlighted how even reputed auditors can miss or ignore red flags.',
        outcome: 'PwC India banned by SEBI for 2 years, fined ₹13 crore',
        impact: 'Loss of auditor credibility, regulatory reforms in auditing',
      },
      {
        company: 'PC Jeweller',
        year: '2018',
        description:
          'Auditors S.R. Batliboi & Associates (EY) resigned citing management\'s failure to provide information on certain transactions. This was a major red flag that led to stock crash and investigations that revealed massive accounting irregularities.',
        outcome: 'Stock fell 90%, company under investigation for fraud',
        impact: 'Auditor resignation validated investor concerns',
      },
    ],
    investorActions: [
      'Read auditor change announcements carefully',
      'Check if previous auditor resigned or was replaced',
      'Look for any qualifications in the last audit report',
      'Assess the reputation of the new auditor',
      'Review management explanation for the change',
      'Monitor for restatements or adjustments after auditor change',
      'Be cautious if change coincides with other red flags',
    ],
    detectionMethod:
      'Data extraction: Extracted from auditor details in annual report. Triggered when auditor name changes from previous year, especially if it\'s the second change in 3 years.',
  },

  // MEDIUM FLAGS - Governance Category
  6: {
    flagNumber: 6,
    title: 'Related Party Transactions High',
    category: 'Governance',
    severity: 'MEDIUM',
    whatItMeans:
      'The company is conducting a high volume of transactions with related parties (subsidiaries, associates, joint ventures, or promoter-controlled entities). While some related party transactions (RPTs) are legitimate, excessive RPTs can be used to transfer wealth from the company to related entities at non-market prices, eroding minority shareholder value.',
    whyItMatters:
      'RPTs are a common vehicle for fraud and tunneling. Promoters can siphon money through inflated purchase prices, suppressed sale prices, or unsecured loans that are never repaid. High RPT volume makes it difficult for auditors and investors to verify whether transactions are at arm\'s length. Many Indian corporate frauds involved significant undisclosed or mispriced RPTs.',
    redFlagsToWatch: [
      'RPTs exceeding 20% of annual revenue',
      'Sales to related parties at prices different from market rates',
      'Loans to related parties without adequate security',
      'Management holding positions in both entities',
      'Lack of disclosure on pricing methodology',
    ],
    similarCases: [
      {
        company: 'Rana Kapoor / Yes Bank',
        year: '2020',
        description:
          'Yes Bank provided loans to several entities that were connected to the promoter\'s family interests. These loans were often evergreened (refinanced repeatedly). When borrowers defaulted, it was revealed that many were controlled by the Kapoor family, creating massive NPAs.',
        outcome: 'Founder arrested for ₹4,355 crore fraud, bank nationalized',
        impact: 'Depositors faced crisis, bank required ₹10,000 crore bailout',
      },
      {
        company: 'DHFL',
        year: '2019',
        description:
          'The company had extended ₹14,046 crore in loans to shell companies controlled by promoters. These funds were siphoned off and not recoverable. The RPTs were disclosed but their true nature was hidden through complex structures.',
        outcome: 'Company went bankrupt, promoters arrested',
        impact: 'Creditors faced 90% haircut, lenders lost ₹90,000+ crore',
      },
    ],
    investorActions: [
      'Review RPT disclosures in annual report notes',
      'Calculate RPTs as % of total revenue and assets',
      'Check pricing methodology and whether it\'s at arm\'s length',
      'Look for unsecured loans to related parties',
      'Assess business rationale for the transactions',
      'Verify if RPTs are increasing or decreasing over time',
      'Flag companies with RPTs >15% of revenue without strong justification',
    ],
    detectionMethod:
      'Data extraction: Extracted from related party transaction disclosures. Triggered when total RPT value exceeds 15% of annual revenue or shows unusual patterns.',
  },

  // MEDIUM FLAGS - Cash Flow Category
  7: {
    flagNumber: 7,
    title: 'Negative Free Cash Flow',
    category: 'Cash Flow',
    severity: 'MEDIUM',
    whatItMeans:
      'Free Cash Flow (FCF = Operating Cash Flow - Capital Expenditure) is negative, meaning the company is spending more cash on capital investments than it generates from operations. While this can be acceptable for growth companies investing heavily in expansion, persistent negative FCF indicates the company is consuming cash and may need external funding to sustain operations.',
    whyItMatters:
      'Negative FCF means the company is not self-sustaining and will need to raise debt or equity to continue operating. This increases financial risk and dilution risk for shareholders. Companies with sustained negative FCF often face liquidity crises, especially during economic downturns when access to funding becomes difficult.',
    redFlagsToWatch: [
      'Negative FCF for two or more consecutive years',
      'Operating cash flow declining while capex remains high',
      'Capex not translating into revenue or profit growth',
      'Increasing reliance on debt or equity dilution',
      'Management guidance not matching cash flow reality',
    ],
    similarCases: [
      {
        company: 'Jet Airways',
        year: '2019',
        description:
          'The airline had negative free cash flows for years as high operating costs and debt servicing consumed all operating cash and more. Despite multiple equity infusions and debt restructuring, the company could not generate positive cash flows and eventually ran out of liquidity.',
        outcome: 'Grounded operations, entered insolvency, lenders took control',
        impact: 'Shareholders wiped out, 20,000+ employees lost jobs',
      },
      {
        company: 'Suzlon Energy',
        year: '2017-2019',
        description:
          'The wind energy company had negative FCF as revenues declined while it still had to service ₹10,000+ crore debt. Despite asset sales and restructuring, the company struggled with cash generation and defaulted on bonds.',
        outcome: 'Debt restructuring, stake dilution, stock fell 95%',
        impact: 'Bondholders suffered losses, stock delisted temporarily',
      },
    ],
    investorActions: [
      'Calculate FCF for the last 3 years',
      'Assess whether negative FCF is due to growth capex or operational weakness',
      'Check management explanation and future capex guidance',
      'Verify if capex is yielding returns in subsequent years',
      'Monitor debt levels and funding sources',
      'Evaluate if the company has sufficient liquidity runway',
      'Avoid companies with persistently negative FCF and no clear turnaround path',
    ],
    detectionMethod:
      'Rule-based: Calculated as Operating Cash Flow minus Capital Expenditure. Triggered when FCF is negative for the current year.',
  },

  // LOW FLAGS - Revenue Category
  8: {
    flagNumber: 8,
    title: 'Revenue Recognition Timing Issues',
    category: 'Revenue',
    severity: 'LOW',
    whatItMeans:
      'A disproportionately large portion of annual revenue is recognized in Q4 (typically >30%), or there are unusual fluctuations in quarterly revenue without operational justification. This pattern can indicate aggressive revenue recognition, channel stuffing, or manipulation to meet annual targets. Declining deferred revenue alongside rising reported revenue is also concerning.',
    whyItMatters:
      'Revenue timing manipulation is a common earnings management tactic. Companies may push sales into Q4 to meet guidance, offer unsustainable discounts, or recognize revenue before it\'s earned. This creates a "borrowed" revenue problem where future quarters suffer. It can also indicate underlying demand weakness that management is trying to mask.',
    redFlagsToWatch: [
      'Q4 revenue exceeding 35% of annual revenue',
      'Large sequential jump in Q4 revenue (>50% increase from Q3)',
      'Deferred revenue declining while reported revenue increases',
      'Unusual payment terms or extended credit periods in Q4',
      'High product returns in Q1 of following year',
    ],
    similarCases: [
      {
        company: 'Manpasand Beverages',
        year: '2019',
        description:
          'The company showed unusual spikes in quarterly sales that did not match actual distributor offtake. They were channel stuffing by forcing distributors to take excess inventory. Revenue was recognized prematurely before actual sales to end customers.',
        outcome: 'Fraud exposed, promoters arrested, stock delisted',
        impact: 'Investors lost 99%, auditors faced scrutiny',
      },
      {
        company: 'Vakrangee',
        year: '2018',
        description:
          'The company reported massive revenue and profit growth driven by aggressive revenue recognition from its franchise model. Auditors raised concerns about the sustainability and accounting treatment. Revenue had to be restated downward significantly.',
        outcome: 'Stock fell 95% from peak, investigations launched',
        impact: 'Massive wealth destruction for retail investors',
      },
    ],
    investorActions: [
      'Analyze quarterly revenue pattern for last 2-3 years',
      'Calculate Q4 revenue as % of annual revenue',
      'Review management commentary on seasonality',
      'Check for unusual provisions or adjustments in subsequent quarter',
      'Monitor deferred revenue trends',
      'Verify if Q4 spike is due to genuine business factors',
      'Be cautious if pattern repeats without operational justification',
    ],
    detectionMethod:
      'Rule-based: Analyzes quarterly revenue distribution. Triggered when Q4 revenue exceeds 35% of annual revenue or deferred revenue decreases by >15% while revenue grows.',
  },
};

/**
 * Get educational content for a specific flag
 */
export function getEducationalContent(flagNumber: number): FlagEducation | null {
  return FLAG_EDUCATION[flagNumber] || null;
}

/**
 * Get similar fraud cases for a specific flag
 */
export function getSimilarCases(flagNumber: number): SimilarCase[] {
  const education = FLAG_EDUCATION[flagNumber];
  return education?.similarCases || [];
}

/**
 * Get investor action items based on severity and category
 */
export function getInvestorActions(flagNumber: number): string[] {
  const education = FLAG_EDUCATION[flagNumber];
  return education?.investorActions || [];
}

/**
 * Get detection method explanation
 */
export function getDetectionExplanation(flagNumber: number): string {
  const education = FLAG_EDUCATION[flagNumber];
  return education?.detectionMethod || 'Detection method not available';
}

/**
 * Get severity badge color
 */
export function getSeverityColor(severity: FlagSeverity): {
  bg: string;
  text: string;
  border: string;
} {
  const colors = {
    CRITICAL: { bg: 'bg-red-100', text: 'text-red-800', border: 'border-red-300' },
    HIGH: { bg: 'bg-orange-100', text: 'text-orange-800', border: 'border-orange-300' },
    MEDIUM: { bg: 'bg-yellow-100', text: 'text-yellow-800', border: 'border-yellow-300' },
    LOW: { bg: 'bg-blue-100', text: 'text-blue-800', border: 'border-blue-300' },
  };
  return colors[severity];
}

/**
 * Get category badge color
 */
export function getCategoryColor(category: FlagCategory): {
  bg: string;
  text: string;
} {
  const colors = {
    Auditor: { bg: 'bg-purple-100', text: 'text-purple-800' },
    'Cash Flow': { bg: 'bg-green-100', text: 'text-green-800' },
    'Related Party': { bg: 'bg-pink-100', text: 'text-pink-800' },
    Promoter: { bg: 'bg-indigo-100', text: 'text-indigo-800' },
    Governance: { bg: 'bg-gray-100', text: 'text-gray-800' },
    'Balance Sheet': { bg: 'bg-blue-100', text: 'text-blue-800' },
    Revenue: { bg: 'bg-teal-100', text: 'text-teal-800' },
    Textual: { bg: 'bg-amber-100', text: 'text-amber-800' },
  };
  return colors[category];
}

/**
 * Check if educational content exists for a flag
 */
export function hasEducationalContent(flagNumber: number): boolean {
  return flagNumber in FLAG_EDUCATION;
}

/**
 * Get all available flag numbers with content
 */
export function getAvailableFlagNumbers(): number[] {
  return Object.keys(FLAG_EDUCATION).map(Number);
}
