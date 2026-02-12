/**
 * Analysis API Service
 *
 * API functions for triggering analysis and checking status
 */

import { api } from './client';

export interface TaskSubmitResponse {
    task_id: string;
    report_id: string;
    status: string;
    message: string;
}

export interface TaskStatusResponse {
    task_id: string;
    status: 'PENDING' | 'PROCESSING' | 'SUCCESS' | 'FAILURE';
    progress: number;
    result?: {
        analysis_id: string;
    };
    error?: string;
}

export interface AnalyzeCompanyResponse {
    status: 'existing_analysis' | 'analysis_triggered' | 'reports_missing';
    message: string;
    analysis_id?: string;
    task_id?: string;
    reports_count?: number;
}

/**
 * Trigger analysis on a report
 * Backend endpoint: POST /api/v1/analysis/analyze/{report_id}
 */
export const analyzeReport = async (reportId: string): Promise<TaskSubmitResponse> => {
    const response = await api.post<TaskSubmitResponse>(`/analysis/analyze/${reportId}`);
    return response.data;
};

/**
 * Get analysis task status
 * Backend endpoint: GET /api/v1/analysis/task/{task_id}
 */
export const getTaskStatus = async (taskId: string): Promise<TaskStatusResponse> => {
    const response = await api.get<TaskStatusResponse>(`/analysis/task/${taskId}`);
    return response.data;
};

/**
 * Get analysis by report ID
 * Backend endpoint: GET /api/v1/analysis/report/{report_id}
 */
export const getAnalysisByReport = async (reportId: string) => {
    const response = await api.get(`/analysis/report/${reportId}`);
    return response.data;
};

/**
 * Smart company analysis endpoint
 * Backend endpoint: POST /api/v1/companies/{company_id}/analyze
 */
export const analyzeCompany = async (companyId: string): Promise<AnalyzeCompanyResponse> => {
    const response = await api.post<AnalyzeCompanyResponse>(`/companies/${companyId}/analyze`);
    return response.data;
};

/**
 * Poll task status until completion
 * Polls every 2 seconds until task is complete or fails
 */
export const pollTaskStatus = async (
    taskId: string,
    onProgress?: (progress: number, status: string) => void
): Promise<TaskStatusResponse> => {
    return new Promise((resolve, reject) => {
        const pollInterval = setInterval(async () => {
            try {
                const status = await getTaskStatus(taskId);

                if (onProgress) {
                    onProgress(status.progress, status.status);
                }

                if (status.status === 'SUCCESS') {
                    clearInterval(pollInterval);
                    resolve(status);
                } else if (status.status === 'FAILURE') {
                    clearInterval(pollInterval);
                    reject(new Error(status.error || 'Analysis failed'));
                }
            } catch (error) {
                clearInterval(pollInterval);
                reject(error);
            }
        }, 2000); // Poll every 2 seconds
    });
};
