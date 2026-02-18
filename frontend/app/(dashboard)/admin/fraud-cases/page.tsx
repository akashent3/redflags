'use client';

/**
 * Admin - Fraud Case Management
 *
 * View and delete fraud cases
 */

import { useEffect, useState } from 'react';
import { useRouter } from 'next/navigation';
import { api } from '@/lib/api/client';
import { Button } from '@/components/ui/button';
import {
  AlertTriangle,
  Search,
  Trash2,
  Loader2,
  ChevronLeft,
  BookOpen,
  TrendingDown,
} from 'lucide-react';

interface FraudCase {
  case_id: string;
  company_name: string;
  year: number;
  sector: string;
  fraud_type: string;
  stock_decline_percent: number;
  market_cap_lost_cr: number;
  red_flags_detected: any[];
  created_at?: string;
}

export default function FraudCaseManagementPage() {
  const router = useRouter();
  const [fraudCases, setFraudCases] = useState<FraudCase[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [searchQuery, setSearchQuery] = useState('');

  useEffect(() => {
    fetchFraudCases();
  }, []);

  const fetchFraudCases = async () => {
    try {
      setLoading(true);
      setError(null);
      // API returns { total: number, cases: FraudCase[] }
      const response = await api.get<{ total: number; cases: FraudCase[] }>('/fraud-cases/');
      const cases = Array.isArray(response.data.cases) ? response.data.cases : [];
      setFraudCases(cases);
    } catch (err: any) {
      console.error('Failed to fetch fraud cases:', err);
      setError(err.response?.data?.detail || 'Failed to load fraud cases');
      setFraudCases([]);
    } finally {
      setLoading(false);
    }
  };

  const handleDeleteFraudCase = async (caseId: string, companyName: string) => {
    if (!confirm(`Delete fraud case for ${companyName}? This action cannot be undone!`)) return;

    try {
      await api.delete(`/admin/fraud-cases/${caseId}`);
      await fetchFraudCases();
    } catch (err: any) {
      console.error('Failed to delete fraud case:', err);
      if (err.response?.status === 403) {
        alert('Access denied. Admin privileges required.');
      } else {
        alert(err.response?.data?.detail || 'Failed to delete fraud case');
      }
    }
  };

  const filteredCases = fraudCases.filter(fraudCase => {
    const matchesSearch =
      fraudCase.company_name.toLowerCase().includes(searchQuery.toLowerCase()) ||
      fraudCase.fraud_type.toLowerCase().includes(searchQuery.toLowerCase()) ||
      fraudCase.sector.toLowerCase().includes(searchQuery.toLowerCase());
    return matchesSearch;
  });

  if (loading) {
    return (
      <div className="flex items-center justify-center min-h-[60vh]">
        <div className="text-center">
          <Loader2 className="h-8 w-8 animate-spin text-blue-600 mx-auto" />
          <p className="mt-4 text-sm text-gray-600">Loading fraud cases...</p>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="flex items-center justify-center min-h-[60vh]">
        <div className="text-center">
          <AlertTriangle className="h-12 w-12 text-red-600 mx-auto mb-4" />
          <p className="text-lg text-gray-900 font-semibold mb-2">Error</p>
          <p className="text-sm text-gray-600">{error}</p>
        </div>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div>
        <button
          onClick={() => router.push('/admin')}
          className="flex items-center gap-2 text-sm text-gray-600 hover:text-gray-900 mb-4"
        >
          <ChevronLeft className="h-4 w-4" />
          Back to Admin Dashboard
        </button>

        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-3xl font-bold text-gray-900 flex items-center gap-3">
              <AlertTriangle className="h-8 w-8 text-red-600" />
              Fraud Case Management
            </h1>
            <p className="text-gray-600 mt-2">
              {filteredCases.length} of {fraudCases.length} fraud cases
            </p>
          </div>
          <div className="flex gap-3">
            <Button onClick={fetchFraudCases}>Refresh</Button>
          </div>
        </div>
      </div>

      {/* Info Box */}
      <div className="bg-blue-50 border border-blue-200 rounded-lg p-4">
        <div className="flex items-start gap-3">
          <BookOpen className="h-5 w-5 text-blue-600 flex-shrink-0 mt-0.5" />
          <div>
            <p className="text-sm text-blue-900 font-semibold mb-1">How to Add Fraud Cases</p>
            <p className="text-sm text-blue-800">
              Use the admin script: <code className="bg-blue-100 px-1 py-0.5 rounded">python scripts/analyze_fraud_case.py</code>
            </p>
            <p className="text-xs text-blue-700 mt-1">
              Required: --symbol, --pdf, --year, --fraud-type, --stock-decline, --market-cap-lost
            </p>
          </div>
        </div>
      </div>

      {/* Search */}
      <div className="bg-white rounded-lg shadow border border-gray-200 p-4">
        <div className="relative">
          <Search className="absolute left-3 top-1/2 -translate-y-1/2 h-5 w-5 text-gray-400" />
          <input
            type="text"
            placeholder="Search by company name, fraud type, or sector..."
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            className="w-full pl-10 pr-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
          />
        </div>
      </div>

      {/* Fraud Cases Grid */}
      {filteredCases.length > 0 ? (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
          {filteredCases.map((fraudCase) => (
            <div
              key={fraudCase.case_id}
              className="bg-white rounded-lg shadow border border-gray-200 p-5 hover:shadow-lg transition-shadow"
            >
              <div className="flex items-start justify-between mb-3">
                <div className="flex-1">
                  <h3 className="font-bold text-gray-900 mb-1">{fraudCase.company_name}</h3>
                  <div className="flex items-center gap-2 text-sm text-gray-600">
                    <span>{fraudCase.year}</span>
                    <span>•</span>
                    <span>{fraudCase.sector}</span>
                  </div>
                </div>
                <Button
                  variant="ghost"
                  size="sm"
                  onClick={() => handleDeleteFraudCase(fraudCase.case_id, fraudCase.company_name)}
                  className="text-red-600 hover:text-red-700 hover:bg-red-50 -mt-2 -mr-2"
                >
                  <Trash2 className="h-4 w-4" />
                </Button>
              </div>

              <div className="space-y-2 mb-4">
                <div className="flex items-center gap-2 text-sm">
                  <span className="px-2 py-1 bg-red-100 text-red-800 rounded text-xs font-semibold">
                    {fraudCase.fraud_type}
                  </span>
                </div>

                <div className="grid grid-cols-2 gap-2">
                  <div className="bg-red-50 rounded p-2">
                    <div className="flex items-center gap-1 text-red-700 mb-1">
                      <TrendingDown className="h-3 w-3" />
                      <span className="text-xs font-semibold">Stock Decline</span>
                    </div>
                    <div className="text-lg font-bold text-red-800">
                      {fraudCase.stock_decline_percent}%
                    </div>
                  </div>

                  <div className="bg-orange-50 rounded p-2">
                    <div className="text-xs font-semibold text-orange-700 mb-1">
                      Market Cap Lost
                    </div>
                    <div className="text-lg font-bold text-orange-800">
                      ₹{fraudCase.market_cap_lost_cr}Cr
                    </div>
                  </div>
                </div>
              </div>

              <div className="pt-3 border-t border-gray-200">
                <div className="flex items-center justify-between text-sm">
                  <span className="text-gray-600">Red Flags Detected:</span>
                  <span className="font-bold text-orange-700">
                    {fraudCase.red_flags_detected.length}
                  </span>
                </div>
              </div>
            </div>
          ))}
        </div>
      ) : (
        <div className="text-center py-12 bg-white rounded-lg border border-gray-200">
          <AlertTriangle className="h-12 w-12 text-gray-400 mx-auto mb-3" />
          <p className="text-gray-600 mb-2">
            {fraudCases.length === 0
              ? 'No fraud cases in database yet'
              : 'No fraud cases found matching your search'}
          </p>
          {fraudCases.length === 0 && (
            <p className="text-sm text-gray-500">
              Add fraud cases using the admin script from the backend
            </p>
          )}
        </div>
      )}
    </div>
  );
}
