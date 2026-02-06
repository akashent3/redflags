'use client';

/**
 * Trends Page - Multi-Year Risk Analysis
 *
 * Pro+ exclusive feature showing historical risk trends, category evolution,
 * and flag patterns over time. Free users see upgrade prompt with preview.
 */

import { use, useState } from 'react';
import { useRouter } from 'next/navigation';
import { Button } from '@/components/ui/button';
import {
  LineChart,
  Line,
  AreaChart,
  Area,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
  ResponsiveContainer,
} from 'recharts';
import {
  ArrowLeft,
  Crown,
  TrendingUp,
  TrendingDown,
  Minus,
  Calendar,
  BarChart3,
  Lock,
} from 'lucide-react';
import {
  TrendsData,
  transformToOverallTrendChart,
  transformToCategoryTrendChart,
  transformToFlagCountChart,
  getTrendDirectionColor,
} from '@/lib/types/trends';

interface TrendsPageProps {
  params: Promise<{ id: string }>;
}

// Sample trends data for demonstration
const sampleTrendsData: TrendsData = {
  company_id: '1',
  company_name: 'Reliance Industries Ltd',
  display_code: 'RELIANCE',
  overall_trend: [
    { fiscal_year: 'FY 2019-20', risk_score: 38, risk_level: 'MEDIUM', flags_triggered: 5 },
    { fiscal_year: 'FY 2020-21', risk_score: 42, risk_level: 'MEDIUM', flags_triggered: 7 },
    { fiscal_year: 'FY 2021-22', risk_score: 45, risk_level: 'MEDIUM', flags_triggered: 8 },
    { fiscal_year: 'FY 2022-23', risk_score: 40, risk_level: 'MEDIUM', flags_triggered: 6 },
    { fiscal_year: 'FY 2023-24', risk_score: 42, risk_level: 'MEDIUM', flags_triggered: 8 },
  ],
  category_trends: [
    {
      fiscal_year: 'FY 2019-20',
      auditor: 30,
      cash_flow: 55,
      related_party: 25,
      promoter: 35,
      governance: 28,
      balance_sheet: 40,
      revenue: 32,
      textual: 25,
    },
    {
      fiscal_year: 'FY 2020-21',
      auditor: 32,
      cash_flow: 60,
      related_party: 28,
      promoter: 38,
      governance: 30,
      balance_sheet: 42,
      revenue: 35,
      textual: 28,
    },
    {
      fiscal_year: 'FY 2021-22',
      auditor: 35,
      cash_flow: 62,
      related_party: 30,
      promoter: 40,
      governance: 32,
      balance_sheet: 44,
      revenue: 38,
      textual: 30,
    },
    {
      fiscal_year: 'FY 2022-23',
      auditor: 30,
      cash_flow: 58,
      related_party: 26,
      promoter: 36,
      governance: 30,
      balance_sheet: 41,
      revenue: 34,
      textual: 27,
    },
    {
      fiscal_year: 'FY 2023-24',
      auditor: 35,
      cash_flow: 65,
      related_party: 28,
      promoter: 40,
      governance: 32,
      balance_sheet: 45,
      revenue: 38,
      textual: 30,
    },
  ],
  flag_count_trend: [
    { fiscal_year: 'FY 2019-20', critical: 0, high: 2, medium: 2, low: 1, total: 5 },
    { fiscal_year: 'FY 2020-21', critical: 1, high: 2, medium: 3, low: 1, total: 7 },
    { fiscal_year: 'FY 2021-22', critical: 1, high: 3, medium: 3, low: 1, total: 8 },
    { fiscal_year: 'FY 2022-23', critical: 0, high: 2, medium: 3, low: 1, total: 6 },
    { fiscal_year: 'FY 2023-24', critical: 1, high: 2, medium: 4, low: 1, total: 8 },
  ],
  yoy_change: 5.0,
  five_year_trend: 'Deteriorating',
  insights: [
    'Cash Flow risk has increased by 18% over the past 5 years, indicating persistent concerns with cash generation relative to reported profits.',
    'The company triggered its first Critical flag in FY 2020-21, which has recurred in FY 2023-24.',
    'Promoter-related risks have shown a gradual upward trend, rising from 35 to 40 over the period.',
    'Despite fluctuations, the overall risk score has remained in the MEDIUM range, averaging 41.4 over 5 years.',
  ],
  earliest_year: 'FY 2019-20',
  latest_year: 'FY 2023-24',
  total_analyses: 5,
};

export default function TrendsPage({ params }: TrendsPageProps) {
  const resolvedParams = use(params);
  const router = useRouter();
  const [selectedCategory, setSelectedCategory] = useState<string>('all');

  // TODO: Replace with actual auth check from useAuth hook
  const isProPlusUser = false; // Set to false to show upgrade prompt

  const trendsData = sampleTrendsData;
  const trendColor = getTrendDirectionColor(trendsData.five_year_trend);

  // Transform data for charts
  const overallTrendData = transformToOverallTrendChart(trendsData.overall_trend);
  const categoryTrendData = transformToCategoryTrendChart(trendsData.category_trends);
  const flagCountData = transformToFlagCountChart(trendsData.flag_count_trend);

  // Category colors for legend
  const categoryColors: Record<string, string> = {
    Auditor: '#8b5cf6',
    'Cash Flow': '#10b981',
    'Related Party': '#ec4899',
    Promoter: '#6366f1',
    Governance: '#64748b',
    'Balance Sheet': '#3b82f6',
    Revenue: '#14b8a6',
    Textual: '#f59e0b',
  };

  if (!isProPlusUser) {
    return (
      <div className="space-y-6">
        {/* Back Navigation */}
        <button
          onClick={() => router.back()}
          className="flex items-center gap-2 text-sm text-gray-600 hover:text-gray-900"
        >
          <ArrowLeft className="h-4 w-4" />
          Back to Report
        </button>

        {/* Upgrade Prompt */}
        <div className="relative bg-gradient-to-br from-blue-600 to-purple-600 rounded-lg overflow-hidden">
          <div className="absolute inset-0 bg-black/10" />
          <div className="relative p-8 md:p-12">
            <div className="max-w-2xl">
              <div className="flex items-center gap-3 mb-4">
                <Crown className="h-10 w-10 text-yellow-300" />
                <h1 className="text-3xl font-bold text-white">
                  Unlock Historical Trends
                </h1>
              </div>
              <p className="text-blue-100 text-lg mb-6">
                Get Pro+ to access multi-year risk analysis and see how companies evolve over time
              </p>

              <div className="grid grid-cols-1 md:grid-cols-2 gap-4 mb-8">
                <div className="flex items-start gap-3">
                  <div className="bg-white/20 p-2 rounded-lg">
                    <TrendingUp className="h-5 w-5 text-white" />
                  </div>
                  <div>
                    <h3 className="font-semibold text-white mb-1">
                      5-Year Risk Trends
                    </h3>
                    <p className="text-sm text-blue-100">
                      Track overall risk scores and identify patterns
                    </p>
                  </div>
                </div>

                <div className="flex items-start gap-3">
                  <div className="bg-white/20 p-2 rounded-lg">
                    <BarChart3 className="h-5 w-5 text-white" />
                  </div>
                  <div>
                    <h3 className="font-semibold text-white mb-1">
                      Category Evolution
                    </h3>
                    <p className="text-sm text-blue-100">
                      See how each risk category changes over time
                    </p>
                  </div>
                </div>

                <div className="flex items-start gap-3">
                  <div className="bg-white/20 p-2 rounded-lg">
                    <Calendar className="h-5 w-5 text-white" />
                  </div>
                  <div>
                    <h3 className="font-semibold text-white mb-1">
                      Year-over-Year Comparisons
                    </h3>
                    <p className="text-sm text-blue-100">
                      Analyze YoY changes and improvement rates
                    </p>
                  </div>
                </div>

                <div className="flex items-start gap-3">
                  <div className="bg-white/20 p-2 rounded-lg">
                    <Lock className="h-5 w-5 text-white" />
                  </div>
                  <div>
                    <h3 className="font-semibold text-white mb-1">
                      AI-Powered Insights
                    </h3>
                    <p className="text-sm text-blue-100">
                      Get automated analysis of key trend drivers
                    </p>
                  </div>
                </div>
              </div>

              <Button
                onClick={() => router.push('/pricing')}
                size="lg"
                className="bg-yellow-400 text-gray-900 hover:bg-yellow-300 font-bold"
              >
                <Crown className="mr-2 h-5 w-5" />
                Upgrade to Pro+ - ₹999/month
              </Button>
            </div>
          </div>
        </div>

        {/* Blurred Preview */}
        <div className="relative">
          <div className="absolute inset-0 bg-white/80 backdrop-blur-sm z-10 flex items-center justify-center">
            <div className="bg-white rounded-lg shadow-lg p-6 max-w-md text-center">
              <Lock className="h-12 w-12 text-gray-400 mx-auto mb-3" />
              <h3 className="text-lg font-bold text-gray-900 mb-2">
                Pro+ Feature
              </h3>
              <p className="text-sm text-gray-600 mb-4">
                Upgrade to view detailed historical trends and insights
              </p>
              <Button onClick={() => router.push('/pricing')}>
                Unlock Now
              </Button>
            </div>
          </div>

          {/* Preview Charts (blurred) */}
          <div className="space-y-6 opacity-50">
            <div className="bg-white rounded-lg shadow border border-gray-200 p-6">
              <h2 className="text-xl font-bold text-gray-900 mb-4">
                Overall Risk Trend
              </h2>
              <div className="h-64 bg-gray-100 rounded" />
            </div>

            <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
              <div className="bg-white rounded-lg shadow border border-gray-200 p-6">
                <h3 className="font-bold text-gray-900 mb-4">
                  Category Trends
                </h3>
                <div className="h-48 bg-gray-100 rounded" />
              </div>
              <div className="bg-white rounded-lg shadow border border-gray-200 p-6">
                <h3 className="font-bold text-gray-900 mb-4">
                  Flag Count Evolution
                </h3>
                <div className="h-48 bg-gray-100 rounded" />
              </div>
            </div>
          </div>
        </div>
      </div>
    );
  }

  // Pro+ User View
  return (
    <div className="space-y-6">
      {/* Back Navigation */}
      <button
        onClick={() => router.back()}
        className="flex items-center gap-2 text-sm text-gray-600 hover:text-gray-900"
      >
        <ArrowLeft className="h-4 w-4" />
        Back to Report
      </button>

      {/* Header */}
      <div className="bg-white rounded-lg shadow border border-gray-200 p-6">
        <div className="flex items-start justify-between">
          <div>
            <div className="flex items-center gap-2 mb-2">
              <h1 className="text-3xl font-bold text-gray-900">
                Historical Risk Trends
              </h1>
              <Crown className="h-6 w-6 text-yellow-500" />
            </div>
            <p className="text-gray-600">
              {trendsData.company_name} • {trendsData.earliest_year} to{' '}
              {trendsData.latest_year} • {trendsData.total_analyses} analyses
            </p>
          </div>
          <div className={`px-4 py-2 rounded-lg ${trendColor.bg}`}>
            <div className="flex items-center gap-2">
              {trendsData.five_year_trend === 'Improving' && (
                <TrendingUp className={`h-5 w-5 ${trendColor.icon}`} />
              )}
              {trendsData.five_year_trend === 'Deteriorating' && (
                <TrendingDown className={`h-5 w-5 ${trendColor.icon}`} />
              )}
              {trendsData.five_year_trend === 'Stable' && (
                <Minus className={`h-5 w-5 ${trendColor.icon}`} />
              )}
              <span className={`font-semibold ${trendColor.text}`}>
                {trendsData.five_year_trend}
              </span>
            </div>
            <p className={`text-sm ${trendColor.text} mt-1`}>
              YoY: {trendsData.yoy_change > 0 ? '+' : ''}
              {trendsData.yoy_change}%
            </p>
          </div>
        </div>
      </div>

      {/* Overall Risk Trend Chart */}
      <div className="bg-white rounded-lg shadow border border-gray-200 p-6">
        <h2 className="text-xl font-bold text-gray-900 mb-6">
          Overall Risk Score Trend
        </h2>
        <ResponsiveContainer width="100%" height={300}>
          <AreaChart data={overallTrendData}>
            <defs>
              <linearGradient id="colorScore" x1="0" y1="0" x2="0" y2="1">
                <stop offset="5%" stopColor="#3b82f6" stopOpacity={0.8} />
                <stop offset="95%" stopColor="#3b82f6" stopOpacity={0} />
              </linearGradient>
            </defs>
            <CartesianGrid strokeDasharray="3 3" />
            <XAxis dataKey="year" />
            <YAxis domain={[0, 100]} />
            <Tooltip
              content={({ active, payload }) => {
                if (active && payload && payload.length) {
                  return (
                    <div className="bg-white border border-gray-200 rounded-lg p-3 shadow-lg">
                      <p className="font-semibold">{payload[0].payload.year}</p>
                      <p className="text-sm text-blue-600">
                        Score: {payload[0].value}
                      </p>
                      <p className="text-sm text-gray-600">
                        Level: {payload[0].payload.level}
                      </p>
                    </div>
                  );
                }
                return null;
              }}
            />
            <Area
              type="monotone"
              dataKey="score"
              stroke="#3b82f6"
              strokeWidth={2}
              fillOpacity={1}
              fill="url(#colorScore)"
            />
          </AreaChart>
        </ResponsiveContainer>
      </div>

      {/* Category Trends */}
      <div className="bg-white rounded-lg shadow border border-gray-200 p-6">
        <div className="flex items-center justify-between mb-6">
          <h2 className="text-xl font-bold text-gray-900">Category Risk Trends</h2>
          <select
            value={selectedCategory}
            onChange={(e) => setSelectedCategory(e.target.value)}
            className="px-3 py-2 border border-gray-300 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
          >
            <option value="all">All Categories</option>
            {Object.keys(categoryColors).map((cat) => (
              <option key={cat} value={cat}>
                {cat}
              </option>
            ))}
          </select>
        </div>
        <ResponsiveContainer width="100%" height={350}>
          <LineChart data={categoryTrendData}>
            <CartesianGrid strokeDasharray="3 3" />
            <XAxis dataKey="year" />
            <YAxis domain={[0, 100]} />
            <Tooltip />
            <Legend />
            {(selectedCategory === 'all'
              ? Object.keys(categoryColors)
              : [selectedCategory]
            ).map((cat) => (
              <Line
                key={cat}
                type="monotone"
                dataKey={cat}
                stroke={categoryColors[cat]}
                strokeWidth={2}
                dot={{ r: 4 }}
              />
            ))}
          </LineChart>
        </ResponsiveContainer>
      </div>

      {/* Flag Count Evolution */}
      <div className="bg-white rounded-lg shadow border border-gray-200 p-6">
        <h2 className="text-xl font-bold text-gray-900 mb-6">
          Flag Count Evolution by Severity
        </h2>
        <ResponsiveContainer width="100%" height={300}>
          <LineChart data={flagCountData}>
            <CartesianGrid strokeDasharray="3 3" />
            <XAxis dataKey="year" />
            <YAxis />
            <Tooltip />
            <Legend />
            <Line
              type="monotone"
              dataKey="Critical"
              stroke="#ef4444"
              strokeWidth={2}
              dot={{ r: 4 }}
            />
            <Line
              type="monotone"
              dataKey="High"
              stroke="#f97316"
              strokeWidth={2}
              dot={{ r: 4 }}
            />
            <Line
              type="monotone"
              dataKey="Medium"
              stroke="#f59e0b"
              strokeWidth={2}
              dot={{ r: 4 }}
            />
            <Line
              type="monotone"
              dataKey="Low"
              stroke="#3b82f6"
              strokeWidth={2}
              dot={{ r: 4 }}
            />
          </LineChart>
        </ResponsiveContainer>
      </div>

      {/* AI Insights */}
      <div className="bg-white rounded-lg shadow border border-gray-200 p-6">
        <h2 className="text-xl font-bold text-gray-900 mb-4">Key Insights</h2>
        <div className="space-y-3">
          {trendsData.insights.map((insight, index) => (
            <div key={index} className="flex items-start gap-3">
              <div className="bg-blue-100 p-2 rounded-lg flex-shrink-0">
                <TrendingUp className="h-4 w-4 text-blue-600" />
              </div>
              <p className="text-gray-700 text-sm leading-relaxed">{insight}</p>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}
