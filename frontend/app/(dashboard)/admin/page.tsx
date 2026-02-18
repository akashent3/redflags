'use client';

/**
 * Admin Dashboard
 *
 * System statistics and overview for administrators
 */

import { useEffect, useState } from 'react';
import { useRouter } from 'next/navigation';
import { api } from '@/lib/api/client';
import {
  Users,
  FileText,
  AlertTriangle,
  Building2,
  TrendingUp,
  Shield,
  Loader2,
  Eye,
  Briefcase,
} from 'lucide-react';

interface SystemStats {
  users: {
    total: number;
    active: number;
    verified: number;
    free: number;
    pro: number;
    premium: number;
  };
  analyses: {
    total: number;
    clean: number;
    low: number;
    medium: number;
    high: number;
    critical: number;
  };
  companies: {
    total: number;
    nifty_50: number;
    nifty_500: number;
  };
  fraud_cases: {
    total: number;
  };
  watchlist_items: {
    total: number;
  };
  portfolios: {
    total: number;
  };
}

export default function AdminDashboard() {
  const router = useRouter();
  const [stats, setStats] = useState<SystemStats | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    fetchStats();
  }, []);

  const fetchStats = async () => {
    try {
      setLoading(true);
      setError(null);
      const response = await api.get<SystemStats>('/admin/stats');
      setStats(response.data);
    } catch (err: any) {
      console.error('Failed to fetch admin stats:', err);
      if (err.response?.status === 403) {
        setError('Access denied. Admin privileges required.');
        setTimeout(() => router.push('/dashboard'), 2000);
      } else {
        setError(err.response?.data?.detail || 'Failed to load statistics');
      }
    } finally {
      setLoading(false);
    }
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center min-h-[60vh]">
        <div className="text-center">
          <Loader2 className="h-8 w-8 animate-spin text-blue-600 mx-auto" />
          <p className="mt-4 text-sm text-gray-600">Loading admin dashboard...</p>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="flex items-center justify-center min-h-[60vh]">
        <div className="text-center">
          <Shield className="h-12 w-12 text-red-600 mx-auto mb-4" />
          <p className="text-lg text-gray-900 font-semibold mb-2">Error</p>
          <p className="text-sm text-gray-600">{error}</p>
        </div>
      </div>
    );
  }

  if (!stats) return null;

  const StatCard = ({
    title,
    value,
    icon: Icon,
    color,
    subtitle
  }: {
    title: string;
    value: number;
    icon: any;
    color: string;
    subtitle?: string;
  }) => (
    <div className="bg-white rounded-lg shadow border border-gray-200 p-6">
      <div className="flex items-center justify-between mb-4">
        <div className={`p-3 rounded-lg bg-${color}-100`}>
          <Icon className={`h-6 w-6 text-${color}-600`} />
        </div>
        <div className="text-right">
          <div className="text-2xl font-bold text-gray-900">{value.toLocaleString()}</div>
          <div className="text-sm text-gray-600">{title}</div>
        </div>
      </div>
      {subtitle && (
        <div className="text-xs text-gray-500 mt-2">{subtitle}</div>
      )}
    </div>
  );

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold text-gray-900 flex items-center gap-3">
            <Shield className="h-8 w-8 text-blue-600" />
            Admin Dashboard
          </h1>
          <p className="text-gray-600 mt-2">System statistics and management</p>
        </div>
        <div className="flex gap-3">
          <button
            onClick={() => router.push('/admin/users')}
            className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors"
          >
            Manage Users
          </button>
          <button
            onClick={fetchStats}
            className="px-4 py-2 border border-gray-300 rounded-lg hover:bg-gray-50 transition-colors"
          >
            Refresh
          </button>
        </div>
      </div>

      {/* Quick Stats */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
        <StatCard
          title="Total Users"
          value={stats.users.total}
          icon={Users}
          color="blue"
          subtitle={`${stats.users.active} active, ${stats.users.verified} verified`}
        />
        <StatCard
          title="Total Analyses"
          value={stats.analyses.total}
          icon={FileText}
          color="green"
          subtitle={`${stats.analyses.critical} critical, ${stats.analyses.high} high risk`}
        />
        <StatCard
          title="Companies"
          value={stats.companies.total}
          icon={Building2}
          color="purple"
          subtitle={`${stats.companies.nifty_50} Nifty 50, ${stats.companies.nifty_500} Nifty 500`}
        />
        <StatCard
          title="Fraud Cases"
          value={stats.fraud_cases.total}
          icon={AlertTriangle}
          color="red"
        />
      </div>

      {/* User Breakdown */}
      <div className="bg-white rounded-lg shadow border border-gray-200 p-6">
        <h2 className="text-xl font-bold text-gray-900 mb-4 flex items-center gap-2">
          <Users className="h-6 w-6 text-blue-600" />
          User Statistics
        </h2>
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          <div className="p-4 bg-green-50 rounded-lg border border-green-200">
            <div className="text-sm text-gray-600">Free Users</div>
            <div className="text-2xl font-bold text-green-700">{stats.users.free}</div>
            <div className="text-xs text-gray-500 mt-1">
              {((stats.users.free / stats.users.total) * 100).toFixed(1)}% of total
            </div>
          </div>
          <div className="p-4 bg-blue-50 rounded-lg border border-blue-200">
            <div className="text-sm text-gray-600">Pro Users</div>
            <div className="text-2xl font-bold text-blue-700">{stats.users.pro}</div>
            <div className="text-xs text-gray-500 mt-1">
              {((stats.users.pro / stats.users.total) * 100).toFixed(1)}% of total
            </div>
          </div>
          <div className="p-4 bg-purple-50 rounded-lg border border-purple-200">
            <div className="text-sm text-gray-600">Premium Users</div>
            <div className="text-2xl font-bold text-purple-700">{stats.users.premium}</div>
            <div className="text-xs text-gray-500 mt-1">
              {((stats.users.premium / stats.users.total) * 100).toFixed(1)}% of total
            </div>
          </div>
        </div>
      </div>

      {/* Analysis Risk Distribution */}
      <div className="bg-white rounded-lg shadow border border-gray-200 p-6">
        <h2 className="text-xl font-bold text-gray-900 mb-4 flex items-center gap-2">
          <AlertTriangle className="h-6 w-6 text-orange-600" />
          Analysis Risk Distribution
        </h2>
        <div className="grid grid-cols-2 md:grid-cols-5 gap-4">
          <div className="p-4 bg-green-50 rounded-lg border border-green-200">
            <div className="text-sm text-gray-600">Clean</div>
            <div className="text-2xl font-bold text-green-700">{stats.analyses.clean}</div>
          </div>
          <div className="p-4 bg-blue-50 rounded-lg border border-blue-200">
            <div className="text-sm text-gray-600">Low</div>
            <div className="text-2xl font-bold text-blue-700">{stats.analyses.low}</div>
          </div>
          <div className="p-4 bg-yellow-50 rounded-lg border border-yellow-200">
            <div className="text-sm text-gray-600">Medium</div>
            <div className="text-2xl font-bold text-yellow-700">{stats.analyses.medium}</div>
          </div>
          <div className="p-4 bg-orange-50 rounded-lg border border-orange-200">
            <div className="text-sm text-gray-600">High</div>
            <div className="text-2xl font-bold text-orange-700">{stats.analyses.high}</div>
          </div>
          <div className="p-4 bg-red-50 rounded-lg border border-red-200">
            <div className="text-sm text-gray-600">Critical</div>
            <div className="text-2xl font-bold text-red-700">{stats.analyses.critical}</div>
          </div>
        </div>
      </div>

      {/* Additional Metrics */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        <div className="bg-white rounded-lg shadow border border-gray-200 p-6">
          <h3 className="text-lg font-bold text-gray-900 mb-4 flex items-center gap-2">
            <Eye className="h-5 w-5 text-blue-600" />
            Watchlist Activity
          </h3>
          <div className="text-3xl font-bold text-blue-700">{stats.watchlist_items.total}</div>
          <div className="text-sm text-gray-600 mt-1">Total watchlist items across all users</div>
        </div>

        <div className="bg-white rounded-lg shadow border border-gray-200 p-6">
          <h3 className="text-lg font-bold text-gray-900 mb-4 flex items-center gap-2">
            <Briefcase className="h-5 w-5 text-purple-600" />
            Portfolio Activity
          </h3>
          <div className="text-3xl font-bold text-purple-700">{stats.portfolios.total}</div>
          <div className="text-sm text-gray-600 mt-1">Total portfolios created</div>
        </div>
      </div>

      {/* Quick Links */}
      <div className="bg-gradient-to-br from-blue-50 to-purple-50 rounded-lg border border-blue-200 p-6">
        <h2 className="text-xl font-bold text-gray-900 mb-4">Quick Actions</h2>
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          <button
            onClick={() => router.push('/admin/users')}
            className="p-4 bg-white rounded-lg border border-gray-200 hover:shadow-md transition-shadow text-left"
          >
            <Users className="h-6 w-6 text-blue-600 mb-2" />
            <div className="font-semibold text-gray-900">Manage Users</div>
            <div className="text-sm text-gray-600">View, edit, and delete users</div>
          </button>
          <button
            onClick={() => router.push('/admin/analyses')}
            className="p-4 bg-white rounded-lg border border-gray-200 hover:shadow-md transition-shadow text-left"
          >
            <FileText className="h-6 w-6 text-green-600 mb-2" />
            <div className="font-semibold text-gray-900">Manage Analyses</div>
            <div className="text-sm text-gray-600">View and delete analysis results</div>
          </button>
          <button
            onClick={() => router.push('/admin/fraud-cases')}
            className="p-4 bg-white rounded-lg border border-gray-200 hover:shadow-md transition-shadow text-left"
          >
            <AlertTriangle className="h-6 w-6 text-red-600 mb-2" />
            <div className="font-semibold text-gray-900">Manage Fraud Cases</div>
            <div className="text-sm text-gray-600">Add and delete fraud cases</div>
          </button>
        </div>
      </div>
    </div>
  );
}
