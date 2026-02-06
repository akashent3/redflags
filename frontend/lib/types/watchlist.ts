/**
 * Watchlist Types
 */

export interface WatchlistItem {
  watchlist_id: string;
  company_id: string;
  symbol: string;
  company_name: string;
  industry: string;
  sector: string;
  current_risk_score: number;
  current_risk_level: 'LOW' | 'MEDIUM' | 'HIGH' | 'CRITICAL';
  previous_risk_score?: number;
  score_change?: number;
  last_analysis_date: string;
  added_date: string;
  alert_enabled: boolean;
}

export interface WatchlistAlert {
  alert_id: string;
  company_id: string;
  symbol: string;
  company_name: string;
  alert_type: 'SCORE_CHANGE' | 'NEW_FLAGS' | 'NEW_REPORT';
  severity: 'INFO' | 'WARNING' | 'CRITICAL';
  message: string;
  created_at: string;
  is_read: boolean;
}

export interface Watchlist {
  user_id: string;
  items: WatchlistItem[];
  total_watched: number;
  alert_preferences: {
    email_enabled: boolean;
    push_enabled: boolean;
    frequency: 'real_time' | 'daily' | 'weekly' | 'none';
  };
  recent_alerts: WatchlistAlert[];
}

// Helper functions
export function getAlertSeverityColor(severity: WatchlistAlert['severity']): string {
  const colors = {
    INFO: '#3b82f6',
    WARNING: '#f59e0b',
    CRITICAL: '#ef4444',
  };
  return colors[severity];
}

export function getAlertIcon(alertType: WatchlistAlert['alert_type']): string {
  const icons = {
    SCORE_CHANGE: 'TrendingUp',
    NEW_FLAGS: 'AlertTriangle',
    NEW_REPORT: 'FileText',
  };
  return icons[alertType];
}

export function formatScoreChange(change: number): string {
  const sign = change > 0 ? '+' : '';
  return `${sign}${change.toFixed(1)}`;
}
