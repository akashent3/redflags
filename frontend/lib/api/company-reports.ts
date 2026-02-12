/**
 * Companies API Service - Extended
 *
 * Additional API functions for company reports
 */

import { api } from './client';

export interface AnnualReport {
    id: string;
    company_id: string;
    fiscal_year: string;
    file_url: string;
    file_size_mb: number;
    page_count: number;
    is_processed: string;
    uploaded_at: string;
}

export interface ReportListResponse {
    total: number;
    reports: AnnualReport[];
}

/**
 * Get company's annual reports
 * Backend endpoint: GET /api/v1/companies/{company_id}/reports
 */
export const getCompanyReports = async (companyId: string): Promise<ReportListResponse> => {
    const response = await api.get<ReportListResponse>(`/companies/${companyId}/reports`);
    return response.data;
};
