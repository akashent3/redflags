'use client';

/**
 * Dashboard Page
 *
 * Main dashboard for authenticated users - fetches real data from API
 */

import { useEffect, useState } from 'react';
import { useRouter } from 'next/navigation';
import { useAuth } from '@/lib/hooks/useAuth';
import { api } from '@/lib/api/client';
import { Button } from '@/components/ui/button';
import {
  FileText,
  TrendingUp,
  AlertTriangle,
  Clock,
  Upload,
  Search,
  BarChart3,
  Loader2,
} from 'lucide-react';

interface DashboardStats {
  total_reports: number;
  avg_risk_score: number;
  total_red_flags: number;
  last_analysis_date: string | null;
  recent_analyses: RecentAnalysis[];
}

interface RecentAnalysis {
  analysis_id: string;
  company_name: string;
  symbol: string;
  fiscal_year: string;
  risk_score: number;
  risk_level: string;
  flags_triggered: number;
  analyzed_at: string;
}

export default function DashboardPage() {
  const { user } = useAuth();
  const router = useRouter();
  const [stats, setStats] = useState<DashboardStats | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    fetchDashboardStats();
  }, []);

  const fetchDashboardStats = async () => {
    try {
      setLoading(true);
      setError(null);
      const response = await api.get<DashboardStats>('/dashboard/stats');
      setStats(response.data);
    } catch (err: any) {
      console.error('Failed to fetch dashboard stats:', err);
      setError(err.response?.data?.detail || 'Failed to load dashboard data');
    } finally {
      setLoading(false);
    }
  };

  const getRiskColor = (level: string) => {
    switch (level) {
      case 'CLEAN':
        return 'text-green-600 bg-green-100';
      case 'LOW':
        return 'text-blue-600 bg-blue-100';
      case 'MEDIUM':
        return 'text-yellow-600 bg-yellow-100';
      case 'HIGH':
        return 'text-orange-600 bg-orange-100';
      case 'CRITICAL':
        return 'text-red-600 bg-red-100';
      default:
        return 'text-gray-600 bg-gray-100';
    }
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center min-h-[60vh]">
        <div className="text-center">
          <Loader2 className="h-8 w-8 animate-spin text-blue-600 mx-auto" />
          <p className="mt-4 text-sm text-gray-600">Loading dashboard...</p>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="p-8">
        <div className="bg-red-50 border border-red-200 text-red-800 px-4 py-3 rounded-md">
          <p className="font-medium">Error loading dashboard</p>
          <p className="text-sm mt-1">{error}</p>
        </div>
      </div>
    );
  }

  return (
    <div className="space-y-8">
      {/* Header */}
      <div>
        <h1 className="text-3xl font-bold text-gray-900">Dashboard</h1>
        <p className="mt-2 text-gray-600">
          Welcome back, {user?.full_name || 'User'}!
        </p>
      </div>

      {/* Stats Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        {/* Total Reports */}
        <div className="bg-white p-6 rounded-lg shadow border border-gray-200">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm font-medium text-gray-600">Total Reports</p>
              <p className="mt-2 text-3xl font-bold text-gray-900">
                {stats?.total_reports || 0}
              </p>
            </div>
            <div className="bg-blue-100 p-3 rounded-full">
              <FileText className="h-6 w-6 text-blue-600" />
            </div>
          </div>
          <p className="mt-4 text-xs text-gray-500">
            {stats?.total_reports === 0 ? 'No reports analyzed yet' : 'Completed analyses'}
          </p>
        </div>

        {/* Avg Risk Score */}
        <div className="bg-white p-6 rounded-lg shadow border border-gray-200">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm font-medium text-gray-600">Avg Risk Score</p>
              <p className="mt-2 text-3xl font-bold text-gray-900">
                {stats?.avg_risk_score !== undefined ? stats.avg_risk_score : '-'}
              </p>
            </div>
            <div className="bg-green-100 p-3 rounded-full">
              <TrendingUp className="h-6 w-6 text-green-600" />
            </div>
          </div>
          <p className="mt-4 text-xs text-gray-500">
            {stats?.total_reports === 0 ? 'Upload reports to see analytics' : 'Out of 100'}
          </p>
        </div>

        {/* Red Flags */}
        <div className="bg-white p-6 rounded-lg shadow border border-gray-200">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm font-medium text-gray-600">Red Flags</p>
              <p className="mt-2 text-3xl font-bold text-gray-900">
                {stats?.total_red_flags || 0}
              </p>
            </div>
            <div className="bg-red-100 p-3 rounded-full">
              <AlertTriangle className="h-6 w-6 text-red-600" />
            </div>
          </div>
          <p className="mt-4 text-xs text-gray-500">
            {stats?.total_red_flags === 0 ? 'No flags detected' : 'Flags triggered'}
          </p>
        </div>

        {/* Last Analysis */}
        <div className="bg-white p-6 rounded-lg shadow border border-gray-200">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm font-medium text-gray-600">Last Analysis</p>
              <p className="mt-2 text-3xl font-bold text-gray-900">
                {stats?.last_analysis_date
                  ? new Date(stats.last_analysis_date).toLocaleDateString('en-US', {
                      month: 'short',
                      day: 'numeric',
                    })
                  : '-'}
              </p>
            </div>
            <div className="bg-purple-100 p-3 rounded-full">
              <Clock className="h-6 w-6 text-purple-600" />
            </div>
          </div>
          <p className="mt-4 text-xs text-gray-500">
            {stats?.last_analysis_date ? 'Most recent activity' : 'No recent activity'}
          </p>
        </div>
      </div>

      {/* Welcome Card - Show when no data */}
      {stats?.total_reports === 0 && (
        <div className="bg-gradient-to-r from-blue-600 to-blue-700 rounded-lg shadow-lg p-8 text-white">
          <h2 className="text-2xl font-bold mb-4">🎉 Welcome to RedFlag AI!</h2>
          <p className="text-blue-100 mb-6 max-w-2xl">
            You're all set! RedFlag AI helps you analyze corporate annual reports to detect financial
            red flags using advanced AI. Get started by uploading your first annual report or searching
            for a company.
          </p>
          <div className="flex gap-4">
            <Button variant="secondary" onClick={() => router.push('/analyze')}>
              <FileText className="mr-2 h-4 w-4" />
              Analyze Report
            </Button>
            <Button
              variant="outline"
              className="bg-transparent border-white text-white hover:bg-blue-500"
              onClick={() => router.push('/analyze')}
            >
              Browse Companies
            </Button>
          </div>
        </div>
      )}

      {/* Quick Actions */}
      <div className="bg-white rounded-lg shadow border border-gray-200 p-6">
        <h3 className="text-lg font-semibold text-gray-900 mb-4">Quick Actions</h3>
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          <button
            className="text-left p-4 border border-gray-200 rounded-lg hover:border-blue-500 hover:shadow-md transition-all"
            onClick={() => router.push('/analyze')}
          >
            <Upload className="h-8 w-8 text-blue-600 mb-2" />
            <h4 className="font-medium text-gray-900">Upload Report</h4>
            <p className="text-sm text-gray-500 mt-1">Upload a PDF annual report for analysis</p>
          </button>

          <button
            className="text-left p-4 border border-gray-200 rounded-lg hover:border-blue-500 hover:shadow-md transition-all"
            onClick={() => router.push('/analyze')}
          >
            <Search className="h-8 w-8 text-green-600 mb-2" />
            <h4 className="font-medium text-gray-900">Search Company</h4>
            <p className="text-sm text-gray-500 mt-1">Search NIFTY 500 companies by name or code</p>
          </button>

          <button
            className="text-left p-4 border border-gray-200 rounded-lg hover:border-blue-500 hover:shadow-md transition-all"
            onClick={() => router.push('/portfolio')}
          >
            <BarChart3 className="h-8 w-8 text-purple-600 mb-2" />
            <h4 className="font-medium text-gray-900">Portfolio Scanner</h4>
            <p className="text-sm text-gray-500 mt-1">Upload your portfolio CSV for bulk analysis</p>
          </button>
        </div>
      </div>

      {/* Recent Analyses Table */}
      {stats?.recent_analyses && stats.recent_analyses.length > 0 && (
        <div className="bg-white rounded-lg shadow border border-gray-200 p-6">
          <div className="flex items-center justify-between mb-4">
            <h3 className="text-lg font-semibold text-gray-900">Recent Analyses</h3>
          </div>

          <div className="overflow-x-auto">
            <table className="w-full">
              <thead>
                <tr className="border-b border-gray-200">
                  <th className="text-left py-3 px-4 text-sm font-medium text-gray-700">Company</th>
                  <th className="text-left py-3 px-4 text-sm font-medium text-gray-700">
                    Fiscal Year
                  </th>
                  <th className="text-left py-3 px-4 text-sm font-medium text-gray-700">
                    Risk Score
                  </th>
                  <th className="text-left py-3 px-4 text-sm font-medium text-gray-700">
                    Red Flags
                  </th>
                  <th className="text-right py-3 px-4 text-sm font-medium text-gray-700">Action</th>
                </tr>
              </thead>
              <tbody>
                {stats.recent_analyses.map((analysis) => (
                  <tr key={analysis.analysis_id} className="border-b border-gray-100 hover:bg-gray-50">
                    <td className="py-3 px-4 text-sm text-gray-900">
                      <div>
                        <p className="font-medium">{analysis.company_name}</p>
                        <p className="text-xs text-gray-500">{analysis.symbol}</p>
                      </div>
                    </td>
                    <td className="py-3 px-4 text-sm text-gray-600">{analysis.fiscal_year}</td>
                    <td className="py-3 px-4">
                      <span
                        className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium ${getRiskColor(
                          analysis.risk_level
                        )}`}
                      >
                        {analysis.risk_score} / 100
                      </span>
                    </td>
                    <td className="py-3 px-4 text-sm text-gray-600">
                      <div className="flex items-center gap-1">
                        <AlertTriangle className="h-4 w-4 text-yellow-600" />
                        {analysis.flags_triggered}
                      </div>
                    </td>
                    <td className="py-3 px-4 text-right">
                      <Button
                        variant="ghost"
                        size="sm"
                        onClick={() => router.push(`/report/${analysis.analysis_id}`)}
                      >
                        View Report
                      </Button>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      )}
    </div>
  );
}