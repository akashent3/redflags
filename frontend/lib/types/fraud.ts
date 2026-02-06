/**
 * Fraud Database Types
 */

export interface FraudCase {
  case_id: string;
  company_name: string;
  year: number;
  sector: string;
  industry: string;
  stock_decline_percent: number;
  market_cap_lost_cr: number;
  primary_flags: string[];
  fraud_type: 'Accounting Fraud' | 'Promoter Misconduct' | 'Auditor Failure' | 'Governance Issues' | 'Related Party Transactions';
  timeline: FraudTimeline[];
  red_flags_detected: {
    flag_number: number;
    flag_name: string;
    evidence: string;
    when_visible: string; // Years before collapse
  }[];
  what_investors_missed: string[];
  outcome: string;
  regulatory_action: string;
  lessons_learned: string[];
  detection_difficulty: 'Easy' | 'Medium' | 'Hard';
  image_url?: string;
}

export interface FraudTimeline {
  date: string;
  event: string;
  type: 'red_flag' | 'investigation' | 'collapse' | 'outcome';
}

export interface FraudPattern {
  pattern_id: string;
  pattern_name: string;
  description: string;
  common_flags: number[];
  historical_cases: string[]; // case_ids
  detection_rate: number;
  severity: 'HIGH' | 'CRITICAL';
}

export interface PatternMatch {
  company_name: string;
  similarity_score: number; // 0-100
  matched_patterns: {
    pattern_name: string;
    confidence: number;
    matching_flags: number[];
  }[];
  risk_assessment: 'LOW' | 'MEDIUM' | 'HIGH' | 'CRITICAL';
  recommendation: string;
}

// Helper functions
export function getSectorColor(sector: string): string {
  const colors: Record<string, string> = {
    'Banking': '#3b82f6',
    'Financial Services': '#8b5cf6',
    'Infrastructure': '#f59e0b',
    'Real Estate': '#10b981',
    'Manufacturing': '#6366f1',
    'Technology': '#06b6d4',
    'Retail': '#ec4899',
    'Media': '#f97316',
    'Default': '#64748b',
  };
  return colors[sector] || colors.Default;
}

export function getDifficultyColor(difficulty: FraudCase['detection_difficulty']): string {
  const colors = {
    'Easy': '#22c55e',
    'Medium': '#eab308',
    'Hard': '#ef4444',
  };
  return colors[difficulty];
}
