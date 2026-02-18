'use client';

/**
 * Admin - Analysis Management
 *
 * View and manage analysis results
 */

import { useEffect, useState } from 'react';
import { useRouter } from 'next/navigation';
import { api } from '@/lib/api/client';
import { Button } from '@/components/ui/button';
import {
  FileText,
  Search,
  Trash2,
  Loader2,
  ChevronLeft,
  AlertTriangle,
} from 'lucide-react';

interface Analysis {
  id: string;
  company_id: string;
  fiscal_year: number;
  risk_score: number;
  risk_level: string;
  flags_triggered: number;
  created_at: string;
}

export default function AnalysisManagementPage() {
  const router = useRouter();
  const [analyses, setAnalyses] = useState<Analysis[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [searchQuery, setSearchQuery] = useState('');
  const [filterRisk, setFilterRisk] = useState<string>('all');

  useEffect(() => {
    fetchAnalyses();
  }, []);

  const fetchAnalyses = async () => {
    try {
      setLoading(true);
      setError(null);
      const response = await api.get<Analysis[]>('/admin/analyses?skip=0&limit=100');
      setAnalyses(response.data);
    } catch (err: any) {
      console.error('Failed to fetch analyses:', err);
      if (err.response?.status === 403) {
        setError('Access denied. Admin privileges required.');
        setTimeout(() => router.push('/dashboard'), 2000);
      } else {
        setError(err.response?.data?.detail || 'Failed to load analyses');
      }
    } finally {
      setLoading(false);
    }
  };

  const handleDeleteAnalysis = async (analysisId: string) => {
    if (!confirm('Delete this analysis? This action cannot be undone!')) return;

    try {
      await api.delete(`/admin/analyses/${analysisId}`);
      await fetchAnalyses();
    } catch (err: any) {
      console.error('Failed to delete analysis:', err);
      alert(err.response?.data?.detail || 'Failed to delete analysis');
    }
  };

  const filteredAnalyses = analyses.filter(analysis => {
    const matchesSearch = analysis.company_id.toLowerCase().includes(searchQuery.toLowerCase());
    const matchesRisk = filterRisk === 'all' || analysis.risk_level === filterRisk.toUpperCase();
    return matchesSearch && matchesRisk;
  });

  const getRiskColor = (level: string) => {
    const colors = {
      CLEAN: 'bg-green-100 text-green-800',
      LOW: 'bg-blue-100 text-blue-800',
      MEDIUM: 'bg-yellow-100 text-yellow-800',
      HIGH: 'bg-orange-100 text-orange-800',
      CRITICAL: 'bg-red-100 text-red-800',
    };
    return colors[level as keyof typeof colors] || 'bg-gray-100 text-gray-800';
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center min-h-[60vh]">
        <div className="text-center">
          <Loader2 className="h-8 w-8 animate-spin text-blue-600 mx-auto" />
          <p className="mt-4 text-sm text-gray-600">Loading analyses...</p>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="flex items-center justify-center min-h-[60vh]">
        <div className="text-center">
          <FileText className="h-12 w-12 text-red-600 mx-auto mb-4" />
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
              <FileText className="h-8 w-8 text-green-600" />
              Analysis Management
            </h1>
            <p className="text-gray-600 mt-2">
              {filteredAnalyses.length} of {analyses.length} analyses
            </p>
          </div>
          <Button onClick={fetchAnalyses}>Refresh</Button>
        </div>
      </div>

      {/* Filters */}
      <div className="bg-white rounded-lg shadow border border-gray-200 p-4">
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          {/* Search */}
          <div className="relative">
            <Search className="absolute left-3 top-1/2 -translate-y-1/2 h-5 w-5 text-gray-400" />
            <input
              type="text"
              placeholder="Search by company ID..."
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              className="w-full pl-10 pr-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
            />
          </div>

          {/* Risk Filter */}
          <select
            value={filterRisk}
            onChange={(e) => setFilterRisk(e.target.value)}
            className="px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
          >
            <option value="all">All Risk Levels</option>
            <option value="clean">Clean</option>
            <option value="low">Low</option>
            <option value="medium">Medium</option>
            <option value="high">High</option>
            <option value="critical">Critical</option>
          </select>
        </div>
      </div>

      {/* Analyses Table */}
      <div className="bg-white rounded-lg shadow border border-gray-200 overflow-hidden">
        <div className="overflow-x-auto">
          <table className="w-full">
            <thead className="bg-gray-50 border-b border-gray-200">
              <tr>
                <th className="text-left py-3 px-4 text-sm font-semibold text-gray-900">Company ID</th>
                <th className="text-center py-3 px-4 text-sm font-semibold text-gray-900">Fiscal Year</th>
                <th className="text-center py-3 px-4 text-sm font-semibold text-gray-900">Risk Score</th>
                <th className="text-center py-3 px-4 text-sm font-semibold text-gray-900">Risk Level</th>
                <th className="text-center py-3 px-4 text-sm font-semibold text-gray-900">Flags</th>
                <th className="text-left py-3 px-4 text-sm font-semibold text-gray-900">Created</th>
                <th className="text-right py-3 px-4 text-sm font-semibold text-gray-900">Actions</th>
              </tr>
            </thead>
            <tbody>
              {filteredAnalyses.map((analysis) => (
                <tr key={analysis.id} className="border-b border-gray-100 hover:bg-gray-50">
                  <td className="py-3 px-4">
                    <div className="font-mono text-sm text-gray-700">
                      {analysis.company_id.substring(0, 8)}...
                    </div>
                  </td>
                  <td className="py-3 px-4 text-center">
                    <div className="text-sm font-medium text-gray-900">{analysis.fiscal_year}</div>
                  </td>
                  <td className="py-3 px-4 text-center">
                    <div className="text-lg font-bold text-gray-900">{analysis.risk_score}</div>
                  </td>
                  <td className="py-3 px-4 text-center">
                    <span className={`px-2.5 py-0.5 rounded-full text-xs font-medium ${getRiskColor(analysis.risk_level)}`}>
                      {analysis.risk_level}
                    </span>
                  </td>
                  <td className="py-3 px-4 text-center">
                    <div className="flex items-center justify-center gap-1">
                      <AlertTriangle className="h-4 w-4 text-orange-600" />
                      <span className="text-sm font-medium">{analysis.flags_triggered}</span>
                    </div>
                  </td>
                  <td className="py-3 px-4 text-sm text-gray-600">
                    {new Date(analysis.created_at).toLocaleDateString()}
                  </td>
                  <td className="py-3 px-4 text-right">
                    <Button
                      variant="ghost"
                      size="sm"
                      onClick={() => handleDeleteAnalysis(analysis.id)}
                      className="text-red-600 hover:text-red-700 hover:bg-red-50"
                    >
                      <Trash2 className="h-4 w-4" />
                    </Button>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>

      {filteredAnalyses.length === 0 && (
        <div className="text-center py-12 bg-white rounded-lg border border-gray-200">
          <FileText className="h-12 w-12 text-gray-400 mx-auto mb-3" />
          <p className="text-gray-600">No analyses found matching your filters</p>
        </div>
      )}
    </div>
  );
}
