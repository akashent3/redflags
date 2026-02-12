/**
 * Reports API Service
 *
 * API functions for viewing analysis reports
 */

import { api } from './client';

export interface AnalysisResult {
    id: string;
    report_id: string;
    risk_score: number;
    risk_level: string;
    flags_triggered_count: number;
    analyzed_at: string;
}

/**
 * Get analysis result by ID
 * Backend endpoint: GET /api/v1/reports/{analysis_id}
 */
export const getAnalysisById = async (analysisId: string): Promise<AnalysisResult> => {
    const response = await api.get<AnalysisResult>(`/reports/${analysisId}`);
    return response.data;
};
