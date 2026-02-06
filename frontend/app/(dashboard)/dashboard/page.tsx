'use client';

/**
 * Dashboard Page
 *
 * Main dashboard for authenticated users
 */

import { useAuth } from '@/lib/hooks/useAuth';
import { Button } from '@/components/ui/button';
import { useRouter } from 'next/navigation';
import {
  FileText,
  TrendingUp,
  AlertTriangle,
  Clock,
  Upload,
  Search,
  Calendar,
  BarChart3,
} from 'lucide-react';

// Sample data - will be replaced with real API calls
const recentAnalyses = [
  {
    id: 1,
    company: 'Reliance Industries Ltd',
    date: '2026-02-05',
    riskScore: 42,
    status: 'completed',
    flagsCount: 8,
  },
  {
    id: 2,
    company: 'Tata Consultancy Services',
    date: '2026-02-04',
    riskScore: 28,
    status: 'completed',
    flagsCount: 4,
  },
  {
    id: 3,
    company: 'HDFC Bank Ltd',
    date: '2026-02-03',
    riskScore: 35,
    status: 'completed',
    flagsCount: 6,
  },
];

const recentActivity = [
  {
    id: 1,
    action: 'Analyzed report',
    company: 'Reliance Industries Ltd',
    time: '2 hours ago',
    type: 'analysis',
  },
  {
    id: 2,
    action: 'Added to watchlist',
    company: 'Infosys Ltd',
    time: '5 hours ago',
    type: 'watchlist',
  },
  {
    id: 3,
    action: 'Uploaded report',
    company: 'HDFC Bank Ltd',
    time: '1 day ago',
    type: 'upload',
  },
];

export default function DashboardPage() {
  const { user } = useAuth();
  const router = useRouter();

  const getRiskColor = (score: number) => {
    if (score >= 70) return 'text-red-600 bg-red-100';
    if (score >= 40) return 'text-yellow-600 bg-yellow-100';
    return 'text-green-600 bg-green-100';
  };

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
        <div className="bg-white p-6 rounded-lg shadow border border-gray-200">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm font-medium text-gray-600">
                Total Reports
              </p>
              <p className="mt-2 text-3xl font-bold text-gray-900">0</p>
            </div>
            <div className="bg-blue-100 p-3 rounded-full">
              <FileText className="h-6 w-6 text-blue-600" />
            </div>
          </div>
          <p className="mt-4 text-xs text-gray-500">
            No reports analyzed yet
          </p>
        </div>

        <div className="bg-white p-6 rounded-lg shadow border border-gray-200">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm font-medium text-gray-600">
                Avg Risk Score
              </p>
              <p className="mt-2 text-3xl font-bold text-gray-900">-</p>
            </div>
            <div className="bg-green-100 p-3 rounded-full">
              <TrendingUp className="h-6 w-6 text-green-600" />
            </div>
          </div>
          <p className="mt-4 text-xs text-gray-500">
            Upload reports to see analytics
          </p>
        </div>

        <div className="bg-white p-6 rounded-lg shadow border border-gray-200">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm font-medium text-gray-600">
                Red Flags
              </p>
              <p className="mt-2 text-3xl font-bold text-gray-900">0</p>
            </div>
            <div className="bg-red-100 p-3 rounded-full">
              <AlertTriangle className="h-6 w-6 text-red-600" />
            </div>
          </div>
          <p className="mt-4 text-xs text-gray-500">
            No flags detected
          </p>
        </div>

        <div className="bg-white p-6 rounded-lg shadow border border-gray-200">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm font-medium text-gray-600">
                Last Analysis
              </p>
              <p className="mt-2 text-3xl font-bold text-gray-900">-</p>
            </div>
            <div className="bg-purple-100 p-3 rounded-full">
              <Clock className="h-6 w-6 text-purple-600" />
            </div>
          </div>
          <p className="mt-4 text-xs text-gray-500">
            No recent activity
          </p>
        </div>
      </div>

      {/* Welcome Card */}
      <div className="bg-gradient-to-r from-blue-600 to-blue-700 rounded-lg shadow-lg p-8 text-white">
        <h2 className="text-2xl font-bold mb-4">
          🎉 Welcome to RedFlag AI!
        </h2>
        <p className="text-blue-100 mb-6 max-w-2xl">
          You're all set! RedFlag AI helps you analyze corporate annual reports
          to detect financial red flags using advanced AI. Get started by
          uploading your first annual report or searching for a company.
        </p>
        <div className="flex gap-4">
          <Button
            variant="secondary"
            onClick={() => router.push('/analyze')}
          >
            <FileText className="mr-2 h-4 w-4" />
            Analyze Report
          </Button>
          <Button
            variant="outline"
            className="bg-transparent border-white text-white hover:bg-blue-500"
          >
            Browse Companies
          </Button>
        </div>
      </div>

      {/* Quick Actions */}
      <div className="bg-white rounded-lg shadow border border-gray-200 p-6">
        <h3 className="text-lg font-semibold text-gray-900 mb-4">
          Quick Actions
        </h3>
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          <button
            className="text-left p-4 border border-gray-200 rounded-lg hover:border-blue-500 hover:shadow-md transition-all"
            onClick={() => router.push('/analyze')}
          >
            <Upload className="h-8 w-8 text-blue-600 mb-2" />
            <h4 className="font-medium text-gray-900">Upload Report</h4>
            <p className="text-sm text-gray-500 mt-1">
              Upload a PDF annual report for analysis
            </p>
          </button>

          <button
            className="text-left p-4 border border-gray-200 rounded-lg hover:border-blue-500 hover:shadow-md transition-all"
            onClick={() => router.push('/analyze')}
          >
            <Search className="h-8 w-8 text-green-600 mb-2" />
            <h4 className="font-medium text-gray-900">Search Company</h4>
            <p className="text-sm text-gray-500 mt-1">
              Search NIFTY 500 companies by name or code
            </p>
          </button>

          <button
            className="text-left p-4 border border-gray-200 rounded-lg hover:border-blue-500 hover:shadow-md transition-all"
            onClick={() => router.push('/portfolio')}
          >
            <BarChart3 className="h-8 w-8 text-purple-600 mb-2" />
            <h4 className="font-medium text-gray-900">Portfolio Scanner</h4>
            <p className="text-sm text-gray-500 mt-1">
              Upload your portfolio CSV for bulk analysis
            </p>
          </button>
        </div>
      </div>

      {/* Recent Analyses Table */}
      <div className="bg-white rounded-lg shadow border border-gray-200 p-6">
        <div className="flex items-center justify-between mb-4">
          <h3 className="text-lg font-semibold text-gray-900">
            Recent Analyses
          </h3>
          <Button
            variant="ghost"
            size="sm"
            onClick={() => router.push('/analyze')}
          >
            View All
          </Button>
        </div>

        {recentAnalyses.length === 0 ? (
          <div className="text-center py-12">
            <FileText className="h-12 w-12 text-gray-400 mx-auto mb-3" />
            <p className="text-gray-600 mb-4">No analyses yet</p>
            <Button onClick={() => router.push('/analyze')}>
              Analyze Your First Report
            </Button>
          </div>
        ) : (
          <div className="overflow-x-auto">
            <table className="w-full">
              <thead>
                <tr className="border-b border-gray-200">
                  <th className="text-left py-3 px-4 text-sm font-medium text-gray-700">
                    Company
                  </th>
                  <th className="text-left py-3 px-4 text-sm font-medium text-gray-700">
                    Date
                  </th>
                  <th className="text-left py-3 px-4 text-sm font-medium text-gray-700">
                    Risk Score
                  </th>
                  <th className="text-left py-3 px-4 text-sm font-medium text-gray-700">
                    Red Flags
                  </th>
                  <th className="text-left py-3 px-4 text-sm font-medium text-gray-700">
                    Status
                  </th>
                  <th className="text-right py-3 px-4 text-sm font-medium text-gray-700">
                    Action
                  </th>
                </tr>
              </thead>
              <tbody>
                {recentAnalyses.map((analysis) => (
                  <tr
                    key={analysis.id}
                    className="border-b border-gray-100 hover:bg-gray-50"
                  >
                    <td className="py-3 px-4 text-sm text-gray-900">
                      {analysis.company}
                    </td>
                    <td className="py-3 px-4 text-sm text-gray-600">
                      <div className="flex items-center gap-2">
                        <Calendar className="h-4 w-4" />
                        {new Date(analysis.date).toLocaleDateString()}
                      </div>
                    </td>
                    <td className="py-3 px-4">
                      <span
                        className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium ${getRiskColor(
                          analysis.riskScore
                        )}`}
                      >
                        {analysis.riskScore}
                      </span>
                    </td>
                    <td className="py-3 px-4 text-sm text-gray-600">
                      <div className="flex items-center gap-1">
                        <AlertTriangle className="h-4 w-4 text-yellow-600" />
                        {analysis.flagsCount}
                      </div>
                    </td>
                    <td className="py-3 px-4">
                      <span className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-green-100 text-green-800">
                        Completed
                      </span>
                    </td>
                    <td className="py-3 px-4 text-right">
                      <Button
                        variant="ghost"
                        size="sm"
                        onClick={() =>
                          router.push(`/report/${analysis.id}`)
                        }
                      >
                        View Report
                      </Button>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
        {/* Activity Timeline */}
        <div className="bg-white rounded-lg shadow border border-gray-200 p-6">
          <h3 className="text-lg font-semibold text-gray-900 mb-4">
            Recent Activity
          </h3>
          <div className="space-y-4">
            {recentActivity.map((activity) => (
              <div
                key={activity.id}
                className="flex items-start gap-3 pb-4 border-b border-gray-100 last:border-b-0 last:pb-0"
              >
                <div className="bg-blue-100 p-2 rounded-lg">
                  {activity.type === 'analysis' && (
                    <FileText className="h-4 w-4 text-blue-600" />
                  )}
                  {activity.type === 'watchlist' && (
                    <AlertTriangle className="h-4 w-4 text-blue-600" />
                  )}
                  {activity.type === 'upload' && (
                    <Upload className="h-4 w-4 text-blue-600" />
                  )}
                </div>
                <div className="flex-1">
                  <p className="text-sm text-gray-900">
                    {activity.action}{' '}
                    <span className="font-medium">{activity.company}</span>
                  </p>
                  <p className="text-xs text-gray-500 mt-1">
                    <Clock className="h-3 w-3 inline mr-1" />
                    {activity.time}
                  </p>
                </div>
              </div>
            ))}
          </div>
        </div>

        {/* Recommendations */}
        <div className="bg-gradient-to-br from-blue-50 to-blue-100 rounded-lg shadow border border-blue-200 p-6">
          <h3 className="text-lg font-semibold text-blue-900 mb-4">
            💡 Recommendations
          </h3>
          <div className="space-y-4">
            <div className="bg-white rounded-lg p-4">
              <h4 className="font-medium text-gray-900 mb-1">
                Complete your first analysis
              </h4>
              <p className="text-sm text-gray-600 mb-3">
                Upload an annual report or search for a NIFTY 500 company to get started
              </p>
              <Button
                size="sm"
                onClick={() => router.push('/analyze')}
              >
                Get Started
              </Button>
            </div>

            <div className="bg-white rounded-lg p-4">
              <h4 className="font-medium text-gray-900 mb-1">
                Learn about red flags
              </h4>
              <p className="text-sm text-gray-600 mb-3">
                Explore our fraud database with 50+ real-world case studies
              </p>
              <Button
                size="sm"
                variant="outline"
                onClick={() => router.push('/learn')}
              >
                Explore Cases
              </Button>
            </div>

            <div className="bg-white rounded-lg p-4">
              <h4 className="font-medium text-gray-900 mb-1">
                Set up watchlist
              </h4>
              <p className="text-sm text-gray-600 mb-3">
                Track companies and get alerts when new reports are available
              </p>
              <Button
                size="sm"
                variant="outline"
                onClick={() => router.push('/watchlist')}
              >
                Add Companies
              </Button>
            </div>
          </div>
        </div>
      </div>

    </div>
  );
}
