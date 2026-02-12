/**
 * Companies API Service
 *
 * API functions for searching and retrieving company information
 */

import { api } from './client';

export interface Company {
    id: string;
    name: string;
    display_code: string;
    sector: string | null;
    industry: string | null;
    market_cap: number | null;
}

export interface CompanySearchResponse {
    total: number;
    results: Company[];
}

/**
 * Search for companies by name or code
 */
export const searchCompanies = async (query: string, limit: number = 20): Promise<CompanySearchResponse> => {
    const response = await api.get<CompanySearchResponse>(`/companies/search?q=${encodeURIComponent(query)}&limit=${limit}`);
    return response.data;
};

/**
 * Get company details by ID
 */
export const getCompanyById = async (companyId: string): Promise<Company> => {
    const response = await api.get<Company>(`/companies/${companyId}`);
    return response.data;
};
