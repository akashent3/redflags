'use client';

/**
 * Report Results Page
 *
 * Displays full analysis results with risk gauge, spider chart, and red flags
 */

import { use, useEffect, useState } from 'react';
import { useRouter } from 'next/navigation';
import { api } from '@/lib/api/client';
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
  Loader2,
} from 'lucide-react';

interface ReportPageProps {
  params: Promise<{ id: string }>;
}

interface AnalysisData {
  id: string;
  report_id: string;
  risk_score: number;
  risk_level: string;
  category_scores: Record<string, number>;
  flags_triggered_count: number;
  analyzed_at: string;
  summary_text?: string;
  key_concerns?: string[];
}

interface ReportData {
  id: string;
  company_id: string;
  fiscal_year: string;
  filing_date?: string;
  is_processed: string;
}

interface CompanyData {
  id: string;
  name: string;
  nse_symbol: string;
  industry?: string;
  sector?: string;
}

export default function ReportPage({ params }: ReportPageProps) {
  const resolvedParams = use(params);
  const router = useRouter();
  const [activeTab, setActiveTab] = useState<'overview' | 'flags' | 'network' | 'details'>('overview');
  
  // State for real data
  const [analysis, setAnalysis] = useState<AnalysisData | null>(null);
  const [report, setReport] = useState<ReportData | null>(null);
  const [company, setCompany] = useState<CompanyData | null>(null);
  const [flags, setFlags] = useState<RedFlag[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    fetchReportData();
  }, [resolvedParams.id]);

  const fetchReportData = async () => {
    try {
      setLoading(true);
      setError(null);

      // The ID in the URL is report_id - fetch analysis by report_id
      const analysisResponse = await api.get<AnalysisData>(`/analysis/report/${resolvedParams.id}`);
      setAnalysis(analysisResponse.data);

      // Fetch report details
      const reportResponse = await api.get<ReportData>(`/reports/${resolvedParams.id}`);
      setReport(reportResponse.data);

      // Fetch company details
      const companyResponse = await api.get<CompanyData>(`/companies/${reportResponse.data.company_id}`);
      setCompany(companyResponse.data);

      // Fetch red flags (use analysis_id, not report_id)
      const flagsResponse = await api.get(`/analysis/${analysisResponse.data.id}/flags?triggered_only=true`);
      setFlags(flagsResponse.data.flags || []);

    } catch (err: any) {
      console.error('Failed to fetch report data:', err);
      setError(err.response?.data?.detail || 'Failed to load report data');
    } finally {
      setLoading(false);
    }
  };

  const handleDownload = () => {
    alert('Download functionality coming soon!');
  };

  const handleShare = () => {
    alert('Share functionality coming soon!');
  };

  // Transform category scores for spider chart
  const getCategoryScores = (): CategoryScore[] => {
    if (!analysis?.category_scores) return [];
    
    return Object.entries(analysis.category_scores).map(([category, score]) => ({
      category,
      score: score as number,
      fullMark: 100,
    }));
  };

  // Transform category scores for breakdown
  const getCategoryDetails = (): CategoryData[] => {
    if (!analysis?.category_scores || !flags) return [];

    return Object.entries(analysis.category_scores).map(([category, score]) => {
      const categoryFlags = flags.filter(f => f.category === category && f.triggered);
      return {
        name: category,
        score: score as number,
        flagsCount: categoryFlags.length,
        weight: 10, // Default weight
      };
    }).sort((a, b) => b.score - a.score);
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center min-h-screen">
        <div className="text-center">
          <Loader2 className="h-8 w-8 animate-spin text-blue-600 mx-auto" />
          <p className="mt-4 text-sm text-gray-600">Loading report...</p>
        </div>
      </div>
    );
  }

  if (error || !analysis || !report || !company) {
    return (
      <div className="p-8">
        <div className="bg-red-50 border border-red-200 text-red-800 px-4 py-3 rounded-md">
          <p className="font-medium">Error loading report</p>
          <p className="text-sm mt-1">{error || 'Report data not found'}</p>
          <Button
            onClick={() => router.push('/')}
            variant="outline"
            size="sm"
            className="mt-4"
          >
            <ArrowLeft className="mr-2 h-4 w-4" />
            Back to Dashboard
          </Button>
        </div>
      </div>
    );
  }

  const triggeredFlags = flags.filter(f => f.triggered);
  const criticalFlags = triggeredFlags.filter(f => f.severity === 'CRITICAL');
  const categoryScores = getCategoryScores();
  const categoryDetails = getCategoryDetails();

  return (
    <div className="space-y-6">
      {/* Header */}
      <div>
        <button
          onClick={() => router.push('/')}
          className="flex items-center gap-2 text-sm text-gray-600 hover:text-gray-900 mb-4"
        >
          <ArrowLeft className="h-4 w-4" />
          Back to Dashboard
        </button>

        <div className="flex items-start justify-between">
          <div>
            <h1 className="text-3xl font-bold text-gray-900 flex items-center gap-3">
              <Building2 className="h-8 w-8 text-blue-600" />
              {company.name}
            </h1>
            <div className="flex items-center gap-4 mt-2 text-sm text-gray-600">
              <span className="flex items-center gap-1">
                <Calendar className="h-4 w-4" />
                FY {report.fiscal_year}
              </span>
              <span className="flex items-center gap-1">
                <FileText className="h-4 w-4" />
                Analyzed {new Date(analysis.analyzed_at).toLocaleDateString()}
              </span>
              <span className="flex items-center gap-1">
                <AlertTriangle className="h-4 w-4" />
                {triggeredFlags.length} red flags detected
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
            Red Flags ({triggeredFlags.length})
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
              <RiskGauge score={analysis.risk_score} size="large" />
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
                      {criticalFlags.length} Critical Issues
                    </h3>
                    <p className="text-sm text-gray-600 mt-1">
                      {criticalFlags.length > 0 ? 'Require immediate attention and investigation' : 'No critical issues found'}
                    </p>
                  </div>
                </div>

                {categoryDetails.length > 0 && (
                  <div className="flex items-start gap-3">
                    <div className="bg-orange-100 p-2 rounded-lg">
                      <TrendingUp className="h-5 w-5 text-orange-600" />
                    </div>
                    <div>
                      <h3 className="font-semibold text-gray-900">
                        Highest Risk: {categoryDetails[0].name}
                      </h3>
                      <p className="text-sm text-gray-600 mt-1">
                        Score: {categoryDetails[0].score}/100 with {categoryDetails[0].flagsCount} flags
                      </p>
                    </div>
                  </div>
                )}

                <div className="flex items-start gap-3">
                  <div className="bg-blue-100 p-2 rounded-lg">
                    <FileText className="h-5 w-5 text-blue-600" />
                  </div>
                  <div>
                    <h3 className="font-semibold text-gray-900">
                      {triggeredFlags.length} Total Red Flags
                    </h3>
                    <p className="text-sm text-gray-600 mt-1">
                      Across {categoryScores.length} categories analyzed
                    </p>
                  </div>
                </div>
              </div>

              <div className="mt-6 p-4 bg-blue-50 border border-blue-200 rounded-lg">
                <p className="text-sm text-blue-800">
                  <strong>Risk Level:</strong> {analysis.risk_level}
                  <br />
                  <strong>Score:</strong> {analysis.risk_score}/100
                </p>
              </div>
            </div>
          </div>

          {/* Spider Chart */}
          {categoryScores.length > 0 && (
            <div className="bg-white rounded-lg shadow border border-gray-200 p-8">
              <h2 className="text-xl font-bold text-gray-900 mb-6">
                Risk Breakdown by Category
              </h2>
              <SpiderChart categories={categoryScores} size="large" />
            </div>
          )}

          {/* Top Red Flags Preview */}
          {triggeredFlags.length > 0 && (
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
                  View All {triggeredFlags.length} Flags
                </Button>
              </div>
              <RedFlagsList
                flags={triggeredFlags.slice(0, 3)}
                showFilters={false}
              />
            </div>
          )}
        </div>
      )}

      {/* Red Flags Tab */}
      {activeTab === 'flags' && (
        <div className="bg-white rounded-lg shadow border border-gray-200 p-8">
          <h2 className="text-xl font-bold text-gray-900 mb-6">
            All Red Flags ({triggeredFlags.length} triggered)
          </h2>
          <RedFlagsList flags={triggeredFlags} showFilters={true} />
        </div>
      )}

      {/* Category Details Tab */}
      {activeTab === 'details' && (
        <div className="bg-white rounded-lg shadow border border-gray-200 p-8">
          <h2 className="text-xl font-bold text-gray-900 mb-6">
            Detailed Category Breakdown
          </h2>
          {categoryDetails.length > 0 ? (
            <CategoryBreakdown categories={categoryDetails} compact={false} />
          ) : (
            <p className="text-gray-600">No category data available</p>
          )}
        </div>
      )}
    </div>
  );
}