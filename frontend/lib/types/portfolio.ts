/**
 * Portfolio Types
 */

export interface Holding {
  symbol: string;
  company_name: string;
  quantity: number;
  avg_price: number;
  current_price?: number;
  investment_value: number;
  current_value?: number;
  pnl?: number;
  pnl_percent?: number;
  risk_score?: number;
  risk_level?: 'LOW' | 'MEDIUM' | 'HIGH' | 'CRITICAL';
  flags_count?: number;
  last_analyzed?: string;
}

export interface Portfolio {
  portfolio_id: string;
  user_id: string;
  name: string;
  holdings: Holding[];
  total_investment: number;
  total_current_value?: number;
  total_pnl?: number;
  average_risk_score: number;
  high_risk_count: number;
  created_at: string;
  updated_at: string;
}

export interface PortfolioUploadResult {
  success: boolean;
  holdings_parsed: number;
  holdings_analyzed: number;
  portfolio_id: string;
  errors?: string[];
}

export type BrokerFormat = 'zerodha' | 'groww' | 'upstox' | 'generic';

export function getRiskColor(score?: number): string {
  if (!score) return '#9ca3af';
  if (score < 30) return '#10b981';
  if (score < 60) return '#f59e0b';
  if (score < 80) return '#f97316';
  return '#ef4444';
}

export function getRiskLevel(score?: number): string {
  if (!score) return 'UNKNOWN';
  if (score < 30) return 'LOW';
  if (score < 60) return 'MEDIUM';
  if (score < 80) return 'HIGH';
  return 'CRITICAL';
}
