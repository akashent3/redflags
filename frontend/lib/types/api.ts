/**
 * TypeScript types for RedFlag AI API
 *
 * These types match the Pydantic schemas from the backend.
 */

// ============================================================================
// Auth Types
// ============================================================================

export interface SignupRequest {
  email: string;
  password: string;
  full_name: string;
}

export interface LoginRequest {
  username: string; // email
  password: string;
}

export interface TokenResponse {
  access_token: string;
  token_type: string;
}

export interface User {
  id: string;
  email: string;
  full_name: string;
  is_active: boolean;
  subscription_tier: string;
  created_at: string;
}

// ============================================================================
// Company Types
// ============================================================================

export interface CompanySearchResult {
  id: string;
  name: string;
  display_code: string;
  industry: string | null;
  sector: string | null;
  is_nifty_50: boolean;
  is_nifty_500: boolean;
  market_cap_cr: number | null;
}

export interface CompanySearchResponse {
  total: number;
  results: CompanySearchResult[];
}

export interface CompanyDetailResponse {
  id: string;
  name: string;
  bse_code: string | null;
  nse_symbol: string | null;
  isin: string | null;
  industry: string | null;
  sector: string | null;
  market_cap_cr: number | null;
  is_nifty_50: boolean;
  is_nifty_500: boolean;
  is_active: boolean;
  display_code: string;
  is_nifty: boolean;
  created_at: string;
  updated_at: string | null;
  total_reports: number;
  latest_report_year: number | null;
  earliest_report_year: number | null;
}

// ============================================================================
// Report Types
// ============================================================================

export interface ReportUploadRequest {
  company_name: string;
  fiscal_year: number;
}

export interface Report {
  id: string;
  company_id: string;
  fiscal_year: number;
  fiscal_year_display: string;
  pdf_url: string;
  file_size_mb: number;
  pages_count: number | null;
  is_processed: string; // 'pending' | 'processing' | 'completed' | 'failed'
  uploaded_at: string;
  processed_at: string | null;
}

export interface ReportListResponse {
  total: number;
  skip: number;
  limit: number;
  reports: Report[];
}

// ============================================================================
// Analysis Types
// ============================================================================

export interface TaskSubmitResponse {
  task_id: string;
  report_id: string;
  status: string;
  message: string;
}

export interface TaskStatusResponse {
  task_id: string;
  status: string; // 'PENDING' | 'STARTED' | 'PROGRESS' | 'SUCCESS' | 'FAILURE'
  current: number | null;
  total: number | null;
  percent: number | null;
  message: string | null;
  // Success fields
  analysis_id: string | null;
  risk_score: number | null;
  risk_level: string | null;
  flags_triggered: number | null;
  processing_time: number | null;
  // Error fields
  error: string | null;
}

export interface AnalysisResult {
  id: string;
  report_id: string;
  risk_score: number;
  risk_level: string; // 'LOW' | 'MEDIUM' | 'ELEVATED' | 'HIGH' | 'CRITICAL'
  risk_level_color: string;
  category_scores: Record<string, number>;
  flags_triggered_count: number;
  flags_critical_count: number;
  flags_high_count: number;
  flags_medium_count: number;
  flags_low_count: number;
  summary_text: string | null;
  key_concerns: string[];
  analyzed_at: string;
}

export interface RedFlag {
  id: string;
  flag_number: number;
  flag_name: string;
  category: string;
  severity: string; // 'CRITICAL' | 'HIGH' | 'MEDIUM' | 'LOW'
  is_triggered: boolean;
  confidence_score: number;
  evidence_text: string | null;
  page_references: number[] | null;
  detection_method: string | null;
}

export interface FlagListResponse {
  total: number;
  flags: RedFlag[];
}

// ============================================================================
// Error Types
// ============================================================================

export interface APIError {
  detail: string;
  error_code?: string;
  timestamp?: string;
}
