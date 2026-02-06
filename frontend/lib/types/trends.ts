/**
 * Trends Types for Multi-Year Analysis
 *
 * Type definitions for historical risk trend analysis across multiple years
 */

export type TrendDirection = 'Improving' | 'Deteriorating' | 'Stable';
export type RiskLevel = 'LOW' | 'MEDIUM' | 'HIGH' | 'CRITICAL';

export interface YearlyRiskScore {
  fiscal_year: string;
  risk_score: number;
  risk_level: RiskLevel;
  flags_triggered: number;
}

export interface CategoryTrendData {
  fiscal_year: string;
  auditor: number;
  cash_flow: number;
  related_party: number;
  promoter: number;
  governance: number;
  balance_sheet: number;
  revenue: number;
  textual: number;
}

export interface FlagCountByYear {
  fiscal_year: string;
  critical: number;
  high: number;
  medium: number;
  low: number;
  total: number;
}

export interface TrendsData {
  company_id: string;
  company_name: string;
  display_code?: string;

  /** Overall risk trend over years */
  overall_trend: YearlyRiskScore[];

  /** Category-wise trends over years */
  category_trends: CategoryTrendData[];

  /** Flag count trends by severity */
  flag_count_trend: FlagCountByYear[];

  /** Year-over-year change percentage */
  yoy_change: number;

  /** 3-5 year trend direction */
  five_year_trend: TrendDirection;

  /** AI-generated insights about the trends */
  insights: string[];

  /** Analysis metadata */
  earliest_year: string;
  latest_year: string;
  total_analyses: number;
}

/**
 * Recharts expects specific data format for line charts
 */
export interface OverallTrendChartData {
  year: string;
  score: number;
  level: string;
}

export interface CategoryTrendChartData {
  year: string;
  [category: string]: string | number;
}

export interface FlagCountChartData {
  year: string;
  Critical: number;
  High: number;
  Medium: number;
  Low: number;
}

/**
 * Helper function to get risk level color
 */
export function getRiskLevelColor(level: RiskLevel): string {
  const colors: Record<RiskLevel, string> = {
    LOW: '#10b981',      // green-500
    MEDIUM: '#f59e0b',   // yellow-500
    HIGH: '#f97316',     // orange-500
    CRITICAL: '#ef4444', // red-500
  };
  return colors[level];
}

/**
 * Helper function to get trend direction color
 */
export function getTrendDirectionColor(direction: TrendDirection): {
  bg: string;
  text: string;
  icon: string;
} {
  const colors: Record<TrendDirection, { bg: string; text: string; icon: string }> = {
    Improving: {
      bg: 'bg-green-100',
      text: 'text-green-800',
      icon: 'text-green-600',
    },
    Deteriorating: {
      bg: 'bg-red-100',
      text: 'text-red-800',
      icon: 'text-red-600',
    },
    Stable: {
      bg: 'bg-gray-100',
      text: 'text-gray-800',
      icon: 'text-gray-600',
    },
  };
  return colors[direction];
}

/**
 * Transform TrendsData to chart-compatible format
 */
export function transformToOverallTrendChart(
  data: YearlyRiskScore[]
): OverallTrendChartData[] {
  return data.map((item) => ({
    year: item.fiscal_year,
    score: item.risk_score,
    level: item.risk_level,
  }));
}

export function transformToCategoryTrendChart(
  data: CategoryTrendData[]
): CategoryTrendChartData[] {
  return data.map((item) => ({
    year: item.fiscal_year,
    Auditor: item.auditor,
    'Cash Flow': item.cash_flow,
    'Related Party': item.related_party,
    Promoter: item.promoter,
    Governance: item.governance,
    'Balance Sheet': item.balance_sheet,
    Revenue: item.revenue,
    Textual: item.textual,
  }));
}

export function transformToFlagCountChart(
  data: FlagCountByYear[]
): FlagCountChartData[] {
  return data.map((item) => ({
    year: item.fiscal_year,
    Critical: item.critical,
    High: item.high,
    Medium: item.medium,
    Low: item.low,
  }));
}
