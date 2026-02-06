/**
 * Company Types - Profile and Historical Analysis
 */

export interface CompanyProfile {
  company_id: string;
  company_name: string;
  display_code: string;
  industry: string;
  sector: string;
  market_cap_cr?: number;
  total_reports: number;
  latest_report_year: string;
  earliest_report_year: string;
  analysis_span_years: number;
  historical_risk: Array<{
    fiscal_year: string;
    risk_score: number;
    risk_level: string;
    flags_triggered: number;
  }>;
  current_risk_score: number;
  current_risk_level: string;
  average_risk_score: number;
  best_risk_score: number;
  best_year: string;
  worst_risk_score: number;
  worst_year: string;
  category_comparison: Array<{
    category: string;
    current: number;
    historical_avg: number;
    difference: number;
  }>;
  common_flags: Array<{
    flag_number: number;
    flag_name: string;
    category: string;
    frequency: number;
  }>;
  recent_reports: Array<{
    analysis_id: string;
    fiscal_year: string;
    risk_score: number;
    flags_count: number;
  }>;
}

export function getRiskLevelColorClasses(level: string): {
  bg: string;
  text: string;
  border: string;
} {
  const colors: Record<string, { bg: string; text: string; border: string }> = {
    LOW: { bg: 'bg-green-100', text: 'text-green-800', border: 'border-green-300' },
    MEDIUM: { bg: 'bg-yellow-100', text: 'text-yellow-800', border: 'border-yellow-300' },
    HIGH: { bg: 'bg-orange-100', text: 'text-orange-800', border: 'border-orange-300' },
    CRITICAL: { bg: 'bg-red-100', text: 'text-red-800', border: 'border-red-300' },
  };
  return colors[level] || colors.MEDIUM;
}
