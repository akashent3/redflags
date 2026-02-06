'use client';

/**
 * Company Profile Page - Historical Performance Analysis
 *
 * Shows company risk trends vs own historical averages
 */

import { use } from 'react';
import { useRouter } from 'next/navigation';
import { Button } from '@/components/ui/button';
import {
  LineChart,
  Line,
  BarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
  ResponsiveContainer,
  ReferenceLine,
} from 'recharts';
import {
  ArrowLeft,
  Building2,
  Calendar,
  TrendingUp,
  TrendingDown,
  BarChart3,
  AlertTriangle,
  FileText,
} from 'lucide-react';
import { CompanyProfile, getRiskLevelColorClasses } from '@/lib/types/company';

interface CompanyProfilePageProps {
  params: Promise<{ id: string }>;
}

// Sample company profile data
const sampleProfile: CompanyProfile = {
  company_id: '1',
  company_name: 'Reliance Industries Ltd',
  display_code: 'RELIANCE',
  industry: 'Conglomerate',
  sector: 'Diversified',
  market_cap_cr: 1750000,
  total_reports: 5,
  latest_report_year: 'FY 2023-24',
  earliest_report_year: 'FY 2019-20',
  analysis_span_years: 5,
  historical_risk: [
    { fiscal_year: 'FY 2019-20', risk_score: 38, risk_level: 'MEDIUM', flags_triggered: 5 },
    { fiscal_year: 'FY 2020-21', risk_score: 42, risk_level: 'MEDIUM', flags_triggered: 7 },
    { fiscal_year: 'FY 2021-22', risk_score: 45, risk_level: 'MEDIUM', flags_triggered: 8 },
    { fiscal_year: 'FY 2022-23', risk_score: 40, risk_level: 'MEDIUM', flags_triggered: 6 },
    { fiscal_year: 'FY 2023-24', risk_score: 42, risk_level: 'MEDIUM', flags_triggered: 8 },
  ],
  current_risk_score: 42,
  current_risk_level: 'MEDIUM',
  average_risk_score: 41.4,
  best_risk_score: 38,
  best_year: 'FY 2019-20',
  worst_risk_score: 45,
  worst_year: 'FY 2021-22',
  category_comparison: [
    { category: 'Cash Flow', current: 65, historical_avg: 60, difference: 5 },
    { category: 'Balance Sheet', current: 45, historical_avg: 42, difference: 3 },
    { category: 'Promoter', current: 40, historical_avg: 38, difference: 2 },
    { category: 'Revenue', current: 38, historical_avg: 35, difference: 3 },
    { category: 'Auditor', current: 35, historical_avg: 32, difference: 3 },
    { category: 'Governance', current: 32, historical_avg: 30, difference: 2 },
    { category: 'Textual', current: 30, historical_avg: 28, difference: 2 },
    { category: 'Related Party', current: 28, historical_avg: 27, difference: 1 },
  ],
  common_flags: [
    { flag_number: 1, flag_name: 'Profit growing but CFO flat/declining', category: 'Cash Flow', frequency: 4 },
    { flag_number: 2, flag_name: 'Working capital buildup', category: 'Cash Flow', frequency: 3 },
    { flag_number: 3, flag_name: 'Debt levels increasing', category: 'Balance Sheet', frequency: 3 },
    { flag_number: 4, flag_name: 'High promoter pledging', category: 'Promoter', frequency: 2 },
    { flag_number: 7, flag_name: 'Negative free cash flow', category: 'Cash Flow', frequency: 2 },
  ],
  recent_reports: [
    { analysis_id: 'a5', fiscal_year: 'FY 2023-24', risk_score: 42, flags_count: 8 },
    { analysis_id: 'a4', fiscal_year: 'FY 2022-23', risk_score: 40, flags_count: 6 },
    { analysis_id: 'a3', fiscal_year: 'FY 2021-22', risk_score: 45, flags_count: 8 },
  ],
};

export default function CompanyProfilePage({ params }: CompanyProfilePageProps) {
  const resolvedParams = use(params);
  const router = useRouter();
  const profile = sampleProfile;

  const currentColor = getRiskLevelColorClasses(profile.current_risk_level);

  return (
    <div className="space-y-6">
      {/* Back Navigation */}
      <button
        onClick={() => router.back()}
        className="flex items-center gap-2 text-sm text-gray-600 hover:text-gray-900"
      >
        <ArrowLeft className="h-4 w-4" />
        Back
      </button>

      {/* Header */}
      <div className="bg-white rounded-lg shadow border border-gray-200 p-6">
        <div className="flex items-start justify-between">
          <div className="flex items-start gap-4">
            <Building2 className="h-12 w-12 text-blue-600" />
            <div>
              <h1 className="text-3xl font-bold text-gray-900">{profile.company_name}</h1>
              <div className="flex items-center gap-4 mt-2 text-sm text-gray-600">
                <span>{profile.display_code}</span>
                <span>•</span>
                <span>{profile.industry}</span>
                <span>•</span>
                <span>{profile.sector}</span>
                {profile.market_cap_cr && (
                  <>
                    <span>•</span>
                    <span>MCap: ₹{(profile.market_cap_cr / 100000).toFixed(2)}L Cr</span>
                  </>
                )}
              </div>
            </div>
          </div>
          <div className={`px-4 py-2 rounded-lg ${currentColor.bg} ${currentColor.border} border`}>
            <div className="text-center">
              <div className={`text-2xl font-bold ${currentColor.text}`}>
                {profile.current_risk_score}
              </div>
              <div className={`text-xs ${currentColor.text}`}>Current Risk</div>
            </div>
          </div>
        </div>

        <div className="grid grid-cols-4 gap-4 mt-6">
          <div className="bg-gray-50 p-4 rounded-lg">
            <Calendar className="h-5 w-5 text-gray-600 mb-2" />
            <div className="text-2xl font-bold text-gray-900">{profile.total_reports}</div>
            <div className="text-sm text-gray-600">Analyses</div>
          </div>
          <div className="bg-gray-50 p-4 rounded-lg">
            <BarChart3 className="h-5 w-5 text-gray-600 mb-2" />
            <div className="text-2xl font-bold text-gray-900">{profile.average_risk_score.toFixed(1)}</div>
            <div className="text-sm text-gray-600">Avg Risk</div>
          </div>
          <div className="bg-green-50 p-4 rounded-lg">
            <TrendingDown className="h-5 w-5 text-green-600 mb-2" />
            <div className="text-2xl font-bold text-green-800">{profile.best_risk_score}</div>
            <div className="text-sm text-gray-600">Best ({profile.best_year})</div>
          </div>
          <div className="bg-red-50 p-4 rounded-lg">
            <TrendingUp className="h-5 w-5 text-red-600 mb-2" />
            <div className="text-2xl font-bold text-red-800">{profile.worst_risk_score}</div>
            <div className="text-sm text-gray-600">Worst ({profile.worst_year})</div>
          </div>
        </div>
      </div>

      {/* Historical Risk Profile */}
      <div className="bg-white rounded-lg shadow border border-gray-200 p-6">
        <h2 className="text-xl font-bold text-gray-900 mb-6">Historical Risk Profile</h2>
        <ResponsiveContainer width="100%" height={300}>
          <LineChart data={profile.historical_risk}>
            <CartesianGrid strokeDasharray="3 3" />
            <XAxis dataKey="fiscal_year" />
            <YAxis domain={[0, 100]} />
            <Tooltip />
            <Legend />
            <ReferenceLine
              y={profile.average_risk_score}
              stroke="#9ca3af"
              strokeDasharray="5 5"
              label="Company Average"
            />
            <Line
              type="monotone"
              dataKey="risk_score"
              stroke="#3b82f6"
              strokeWidth={3}
              dot={{ r: 5 }}
              name="Risk Score"
            />
          </LineChart>
        </ResponsiveContainer>
      </div>

      {/* Category Performance */}
      <div className="bg-white rounded-lg shadow border border-gray-200 p-6">
        <h2 className="text-xl font-bold text-gray-900 mb-6">
          Category Performance: Current vs Historical Average
        </h2>
        <ResponsiveContainer width="100%" height={350}>
          <BarChart data={profile.category_comparison}>
            <CartesianGrid strokeDasharray="3 3" />
            <XAxis dataKey="category" angle={-45} textAnchor="end" height={100} />
            <YAxis domain={[0, 100]} />
            <Tooltip />
            <Legend />
            <Bar dataKey="current" fill="#3b82f6" name="Current" />
            <Bar dataKey="historical_avg" fill="#9ca3af" name="Historical Avg" />
          </BarChart>
        </ResponsiveContainer>
      </div>

      {/* Common Flags */}
      <div className="bg-white rounded-lg shadow border border-gray-200 p-6">
        <h2 className="text-xl font-bold text-gray-900 mb-6">Most Frequent Red Flags</h2>
        <div className="space-y-3">
          {profile.common_flags.map((flag) => (
            <div
              key={flag.flag_number}
              className="flex items-center justify-between p-4 border border-gray-200 rounded-lg hover:bg-gray-50"
            >
              <div className="flex items-start gap-3">
                <AlertTriangle className="h-5 w-5 text-orange-500 mt-0.5" />
                <div>
                  <h3 className="font-semibold text-gray-900">{flag.flag_name}</h3>
                  <p className="text-sm text-gray-600">{flag.category}</p>
                </div>
              </div>
              <div className="text-right">
                <div className="text-lg font-bold text-gray-900">{flag.frequency}</div>
                <div className="text-xs text-gray-600">
                  {((flag.frequency / profile.total_reports) * 100).toFixed(0)}% of reports
                </div>
              </div>
            </div>
          ))}
        </div>
      </div>

      {/* Recent Reports */}
      <div className="bg-white rounded-lg shadow border border-gray-200 p-6">
        <h2 className="text-xl font-bold text-gray-900 mb-6">Recent Analysis Reports</h2>
        <div className="space-y-3">
          {profile.recent_reports.map((report) => (
            <button
              key={report.analysis_id}
              onClick={() => router.push(`/report/${report.analysis_id}`)}
              className="w-full flex items-center justify-between p-4 border border-gray-200 rounded-lg hover:bg-gray-50 hover:border-blue-300 transition-colors text-left"
            >
              <div className="flex items-center gap-3">
                <FileText className="h-5 w-5 text-gray-600" />
                <div>
                  <div className="font-semibold text-gray-900">{report.fiscal_year}</div>
                  <div className="text-sm text-gray-600">{report.flags_count} flags detected</div>
                </div>
              </div>
              <div className="text-right">
                <div className="text-lg font-bold text-gray-900">{report.risk_score}</div>
                <div className="text-xs text-gray-600">Risk Score</div>
              </div>
            </button>
          ))}
        </div>
      </div>
    </div>
  );
}
