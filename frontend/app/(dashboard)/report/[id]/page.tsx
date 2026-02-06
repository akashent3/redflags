'use client';

/**
 * Report Results Page
 *
 * Displays full analysis results with risk gauge, spider chart, and red flags
 */

import { use, useState } from 'react';
import { useRouter } from 'next/navigation';
import { Button } from '@/components/ui/button';
import RiskGauge from '@/components/analysis/RiskGauge';
import SpiderChart, { CategoryScore } from '@/components/analysis/SpiderChart';
import CategoryBreakdown, { CategoryData } from '@/components/analysis/CategoryBreakdown';
import RedFlagsList from '@/components/analysis/RedFlagsList';
import { RedFlag } from '@/components/analysis/RedFlagCard';
import RelatedPartyNetwork from '@/components/analysis/RelatedPartyNetwork';
import { transformRPTToNetwork } from '@/lib/utils/networkTransformer';
import {
  Download,
  Share2,
  FileText,
  AlertTriangle,
  TrendingUp,
  Calendar,
  Building2,
  ArrowLeft,
  Network,
} from 'lucide-react';

interface ReportPageProps {
  params: Promise<{ id: string }>;
}

// Sample data - will be replaced with real API calls
const sampleReport = {
  id: 1,
  company: 'Reliance Industries Ltd',
  reportDate: '2026-02-05',
  financialYear: 'FY 2023-24',
  riskScore: 42,
  categories: [
    { category: 'Auditor', score: 35, fullMark: 100 },
    { category: 'Cash Flow', score: 65, fullMark: 100 },
    { category: 'Related Party', score: 28, fullMark: 100 },
    { category: 'Promoter', score: 40, fullMark: 100 },
    { category: 'Governance', score: 32, fullMark: 100 },
    { category: 'Balance Sheet', score: 45, fullMark: 100 },
    { category: 'Revenue', score: 38, fullMark: 100 },
    { category: 'Textual', score: 30, fullMark: 100 },
  ] as CategoryScore[],
  categoryDetails: [
    { name: 'Cash Flow', score: 65, flagsCount: 3, weight: 18 },
    { name: 'Balance Sheet', score: 45, flagsCount: 2, weight: 10 },
    { name: 'Promoter', score: 40, flagsCount: 2, weight: 15 },
    { name: 'Revenue', score: 38, flagsCount: 1, weight: 5 },
    { name: 'Auditor', score: 35, flagsCount: 1, weight: 20 },
    { name: 'Governance', score: 32, flagsCount: 2, weight: 12 },
    { name: 'Textual', score: 30, flagsCount: 1, weight: 5 },
    { name: 'Related Party', score: 28, flagsCount: 1, weight: 15 },
  ] as CategoryData[],
  flags: [
    {
      id: 1,
      flag_id: 'CF001',
      name: 'Profit growing but CFO flat/declining',
      severity: 'CRITICAL' as const,
      category: 'Cash Flow',
      description: 'Profit After Tax (PAT) is increasing while Cash Flow from Operations (CFO) is stagnant or declining, suggesting potential earnings manipulation through aggressive revenue recognition or working capital management.',
      evidence: 'FY24: PAT increased 15% to ₹8,500 Cr, but CFO decreased 5% to ₹6,200 Cr. CFO/PAT ratio dropped from 0.92 to 0.73.',
      triggered: true,
    },
    {
      id: 2,
      flag_id: 'CF002',
      name: 'Working capital buildup',
      severity: 'HIGH' as const,
      category: 'Cash Flow',
      description: 'Significant increase in working capital (inventory + receivables - payables) relative to revenue growth, which can indicate quality of earnings issues or potential overstatement of assets.',
      evidence: 'Working capital increased 28% while revenue grew only 12%. Days Sales Outstanding (DSO) increased from 45 to 62 days.',
      triggered: true,
    },
    {
      id: 3,
      flag_id: 'BS001',
      name: 'Debt levels increasing',
      severity: 'HIGH' as const,
      category: 'Balance Sheet',
      description: 'Total debt has increased significantly, raising concerns about financial leverage and ability to service debt obligations.',
      evidence: 'Total debt increased from ₹1.2 Lakh Cr to ₹1.8 Lakh Cr (50% increase). Debt-to-Equity ratio increased from 0.8 to 1.2.',
      triggered: true,
    },
    {
      id: 4,
      flag_id: 'PR001',
      name: 'High promoter pledging',
      severity: 'MEDIUM' as const,
      category: 'Promoter',
      description: 'Significant portion of promoter shareholding is pledged as collateral, which may indicate financial stress or liquidity constraints.',
      evidence: '42% of promoter holding is pledged (up from 28% last year). Pledged shares worth approximately ₹18,000 Cr.',
      triggered: true,
    },
    {
      id: 5,
      flag_id: 'AU001',
      name: 'Auditor changed recently',
      severity: 'MEDIUM' as const,
      category: 'Auditor',
      description: 'Change in auditor, especially if frequent or without clear explanation, can be a red flag warranting investigation.',
      evidence: 'Auditor changed from Deloitte to EY in FY24. This is the second change in 3 years.',
      triggered: true,
    },
    {
      id: 6,
      flag_id: 'GV001',
      name: 'Related party transactions high',
      severity: 'MEDIUM' as const,
      category: 'Governance',
      description: 'High volume of related party transactions which may not be at arm\'s length pricing.',
      evidence: 'Related party transactions totaled ₹12,500 Cr (18% of revenue). Sales to subsidiaries increased 35%.',
      triggered: true,
    },
    {
      id: 7,
      flag_id: 'CF003',
      name: 'Negative free cash flow',
      severity: 'MEDIUM' as const,
      category: 'Cash Flow',
      description: 'Free Cash Flow (CFO - CapEx) is negative, indicating the company is consuming more cash than it generates from operations.',
      evidence: 'FCF = ₹6,200 Cr (CFO) - ₹8,500 Cr (CapEx) = -₹2,300 Cr. Second consecutive year of negative FCF.',
      triggered: true,
    },
    {
      id: 8,
      flag_id: 'REV001',
      name: 'Revenue recognition timing',
      severity: 'LOW' as const,
      category: 'Revenue',
      description: 'Potential issues with revenue recognition timing, with large portion of revenue recognized in Q4.',
      evidence: 'Q4 revenue was 38% of annual revenue (vs 25% expected). Deferred revenue decreased 15%.',
      triggered: true,
    },
  ] as RedFlag[],
  // Sample RPT data - will be replaced with real API data
  rptData: {
    subsidiaries: [
      {
        name: 'Jio Platforms Ltd',
        sales: 450000, // in lakhs
        purchases: 120000,
        loans_given: 50000,
        investments: 200000,
      },
      {
        name: 'Reliance Retail Ltd',
        sales: 380000,
        purchases: 95000,
        advances: 30000,
      },
      {
        name: 'Reliance Jio Infocomm',
        sales: 280000,
        purchases: 75000,
        guarantees: 100000,
      },
    ],
    associates: [
      {
        name: 'Network18 Media',
        sales: 15000,
        purchases: 8000,
        loans_given: 12000,
      },
      {
        name: 'TV18 Broadcast',
        sales: 12000,
        purchases: 5000,
      },
    ],
    joint_ventures: [
      {
        name: 'IndianOil-Panipat Power',
        investments: 45000,
        loans_given: 20000,
      },
    ],
  },
};

export default function ReportPage({ params }: ReportPageProps) {
  const resolvedParams = use(params);
  const router = useRouter();
  const [activeTab, setActiveTab] = useState<'overview' | 'flags' | 'network' | 'details'>('overview');

  // In real implementation, fetch data based on resolvedParams.id
  const report = sampleReport;

  const handleDownload = () => {
    // TODO: Implement PDF download
    alert('Download functionality coming soon!');
  };

  const handleShare = () => {
    // TODO: Implement share functionality
    alert('Share functionality coming soon!');
  };

  return (
    <div className="space-y-6">
      {/* Header */}
      <div>
        <button
          onClick={() => router.push('/dashboard')}
          className="flex items-center gap-2 text-sm text-gray-600 hover:text-gray-900 mb-4"
        >
          <ArrowLeft className="h-4 w-4" />
          Back to Dashboard
        </button>

        <div className="flex items-start justify-between">
          <div>
            <h1 className="text-3xl font-bold text-gray-900 flex items-center gap-3">
              <Building2 className="h-8 w-8 text-blue-600" />
              {report.company}
            </h1>
            <div className="flex items-center gap-4 mt-2 text-sm text-gray-600">
              <span className="flex items-center gap-1">
                <Calendar className="h-4 w-4" />
                {report.financialYear}
              </span>
              <span className="flex items-center gap-1">
                <FileText className="h-4 w-4" />
                Analyzed {new Date(report.reportDate).toLocaleDateString()}
              </span>
              <span className="flex items-center gap-1">
                <AlertTriangle className="h-4 w-4" />
                {report.flags.length} red flags detected
              </span>
            </div>
          </div>

          <div className="flex items-center gap-3">
            <Button onClick={handleShare} variant="outline" size="sm">
              <Share2 className="mr-2 h-4 w-4" />
              Share
            </Button>
            <Button onClick={handleDownload} size="sm">
              <Download className="mr-2 h-4 w-4" />
              Download PDF
            </Button>
          </div>
        </div>
      </div>

      {/* Tabs */}
      <div className="border-b border-gray-200">
        <div className="flex gap-8">
          <button
            onClick={() => setActiveTab('overview')}
            className={`pb-4 px-1 border-b-2 font-medium text-sm transition-colors ${
              activeTab === 'overview'
                ? 'border-blue-600 text-blue-600'
                : 'border-transparent text-gray-600 hover:text-gray-900 hover:border-gray-300'
            }`}
          >
            Overview
          </button>
          <button
            onClick={() => setActiveTab('flags')}
            className={`pb-4 px-1 border-b-2 font-medium text-sm transition-colors ${
              activeTab === 'flags'
                ? 'border-blue-600 text-blue-600'
                : 'border-transparent text-gray-600 hover:text-gray-900 hover:border-gray-300'
            }`}
          >
            Red Flags ({report.flags.length})
          </button>
          <button
            onClick={() => setActiveTab('network')}
            className={`pb-4 px-1 border-b-2 font-medium text-sm transition-colors flex items-center gap-2 ${
              activeTab === 'network'
                ? 'border-blue-600 text-blue-600'
                : 'border-transparent text-gray-600 hover:text-gray-900 hover:border-gray-300'
            }`}
          >
            <Network className="h-4 w-4" />
            Related Party Network
          </button>
          <button
            onClick={() => setActiveTab('details')}
            className={`pb-4 px-1 border-b-2 font-medium text-sm transition-colors ${
              activeTab === 'details'
                ? 'border-blue-600 text-blue-600'
                : 'border-transparent text-gray-600 hover:text-gray-900 hover:border-gray-300'
            }`}
          >
            Category Details
          </button>
        </div>
      </div>

      {/* Overview Tab */}
      {activeTab === 'overview' && (
        <div className="space-y-8">
          {/* Risk Score Section */}
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
            {/* Risk Gauge */}
            <div className="bg-white rounded-lg shadow border border-gray-200 p-8">
              <h2 className="text-xl font-bold text-gray-900 mb-6">
                Overall Risk Assessment
              </h2>
              <RiskGauge score={report.riskScore} size="large" />
            </div>

            {/* Key Highlights */}
            <div className="bg-white rounded-lg shadow border border-gray-200 p-8">
              <h2 className="text-xl font-bold text-gray-900 mb-6">
                Key Highlights
              </h2>
              <div className="space-y-4">
                <div className="flex items-start gap-3">
                  <div className="bg-red-100 p-2 rounded-lg">
                    <AlertTriangle className="h-5 w-5 text-red-600" />
                  </div>
                  <div>
                    <h3 className="font-semibold text-gray-900">
                      {report.flags.filter((f) => f.severity === 'CRITICAL').length} Critical Issues
                    </h3>
                    <p className="text-sm text-gray-600 mt-1">
                      Require immediate attention and investigation
                    </p>
                  </div>
                </div>

                <div className="flex items-start gap-3">
                  <div className="bg-orange-100 p-2 rounded-lg">
                    <TrendingUp className="h-5 w-5 text-orange-600" />
                  </div>
                  <div>
                    <h3 className="font-semibold text-gray-900">
                      Highest Risk: {report.categoryDetails[0].name}
                    </h3>
                    <p className="text-sm text-gray-600 mt-1">
                      Score: {report.categoryDetails[0].score}/100 with {report.categoryDetails[0].flagsCount} flags
                    </p>
                  </div>
                </div>

                <div className="flex items-start gap-3">
                  <div className="bg-blue-100 p-2 rounded-lg">
                    <FileText className="h-5 w-5 text-blue-600" />
                  </div>
                  <div>
                    <h3 className="font-semibold text-gray-900">
                      {report.flags.length} Total Red Flags
                    </h3>
                    <p className="text-sm text-gray-600 mt-1">
                      Across {report.categories.length} categories analyzed
                    </p>
                  </div>
                </div>
              </div>

              <div className="mt-6 p-4 bg-blue-50 border border-blue-200 rounded-lg">
                <p className="text-sm text-blue-800">
                  <strong>Recommendation:</strong> This company shows medium risk with several concerns in cash flow and balance sheet management. Further due diligence recommended before investment.
                </p>
              </div>
            </div>
          </div>

          {/* Spider Chart */}
          <div className="bg-white rounded-lg shadow border border-gray-200 p-8">
            <h2 className="text-xl font-bold text-gray-900 mb-6">
              Risk Breakdown by Category
            </h2>
            <SpiderChart categories={report.categories} size="large" />
          </div>

          {/* Top Red Flags Preview */}
          <div className="bg-white rounded-lg shadow border border-gray-200 p-8">
            <div className="flex items-center justify-between mb-6">
              <h2 className="text-xl font-bold text-gray-900">
                Top Red Flags
              </h2>
              <Button
                onClick={() => setActiveTab('flags')}
                variant="outline"
                size="sm"
              >
                View All {report.flags.length} Flags
              </Button>
            </div>
            <RedFlagsList
              flags={report.flags.slice(0, 3)}
              showFilters={false}
            />
          </div>
        </div>
      )}

      {/* Red Flags Tab */}
      {activeTab === 'flags' && (
        <div className="bg-white rounded-lg shadow border border-gray-200 p-8">
          <h2 className="text-xl font-bold text-gray-900 mb-6">
            All Red Flags
          </h2>
          <RedFlagsList flags={report.flags} showFilters={true} />
        </div>
      )}

      {/* Related Party Network Tab */}
      {activeTab === 'network' && (
        <div className="bg-white rounded-lg shadow border border-gray-200 p-8">
          <RelatedPartyNetwork
            data={transformRPTToNetwork(
              report.rptData,
              report.company,
              report.financialYear
            )}
          />
        </div>
      )}

      {/* Category Details Tab */}
      {activeTab === 'details' && (
        <div className="bg-white rounded-lg shadow border border-gray-200 p-8">
          <h2 className="text-xl font-bold text-gray-900 mb-6">
            Detailed Category Breakdown
          </h2>
          <CategoryBreakdown categories={report.categoryDetails} compact={false} />
        </div>
      )}
    </div>
  );
}
