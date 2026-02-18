'use client';

/**
 * Learning Page - Fraud Database & Pattern Matching
 *
 * Historical fraud cases with timeline, red flags, and lessons
 */

import { useState, useEffect } from 'react';
import { Button } from '@/components/ui/button';
import {
  BookOpen,
  AlertTriangle,
  TrendingDown,
  Search,
  Filter,
  ChevronRight,
  Calendar,
  CheckCircle2,
  XCircle,
  Loader2,
  Scale,
} from 'lucide-react';
import { api } from '@/lib/api/client';

interface RedFlag {
  flag_number: number;
  flag_name: string;
  category: string;
  severity: string;
  evidence: string;
  triggered?: boolean;
}

interface TimelineEvent {
  date: string;
  event: string;
  type: string;
}

interface FraudCase {
  id: string;
  case_id: string;
  company_name: string;
  year: number;
  sector: string;
  industry?: string;
  fraud_type: string;
  detection_difficulty?: string;
  stock_decline_percent: number;
  market_cap_lost_cr: number;
  primary_flags?: string[];
  red_flags_detected: RedFlag[];
  timeline?: TimelineEvent[];
  what_investors_missed?: string[];
  lessons_learned?: string[];
  outcome?: string;
  regulatory_action?: string;
  created_at: string;
}

interface FraudCaseListResponse {
  total: number;
  cases: FraudCase[];
}

const getSectorColor = (sector: string): string => {
  const colors: Record<string, string> = {
    'IT Services': '#3b82f6',
    'Banking': '#10b981',
    'Finance': '#f59e0b',
    'Aviation': '#8b5cf6',
    'Real Estate': '#ef4444',
    'Infrastructure': '#6366f1',
    'Telecom': '#ec4899',
    'NBFC': '#f97316',
    'Pharmaceuticals': '#06b6d4',
    'Manufacturing': '#84cc16',
  };
  return colors[sector] || '#6b7280';
};

const getSeverityColor = (severity: string): string => {
  const colors: Record<string, string> = {
    'CRITICAL': 'bg-red-100 text-red-800 border-red-300',
    'HIGH': 'bg-orange-100 text-orange-800 border-orange-300',
    'MEDIUM': 'bg-yellow-100 text-yellow-800 border-yellow-300',
    'LOW': 'bg-blue-100 text-blue-800 border-blue-300',
  };
  return colors[severity] || 'bg-gray-100 text-gray-800 border-gray-300';
};

interface MyCompany {
  id: string;
  name: string;
  nse_symbol: string | null;
}

export default function LearnPage() {
  const [fraudCases, setFraudCases] = useState<FraudCase[]>([]);
  const [loading, setLoading] = useState(true);
  const [selectedCase, setSelectedCase] = useState<FraudCase | null>(null);
  const [sectorFilter, setSectorFilter] = useState<string>('All');
  const [searchQuery, setSearchQuery] = useState('');
  const [error, setError] = useState<string | null>(null);
  const [showPatternMatch, setShowPatternMatch] = useState(false);

  // Pattern match autocomplete
  const [patternQuery, setPatternQuery] = useState('');
  const [selectedCompany, setSelectedCompany] = useState<MyCompany | null>(null);
  const [myCompanies, setMyCompanies] = useState<MyCompany[]>([]);
  const [showSuggestions, setShowSuggestions] = useState(false);

  // Pattern match results
  const [patternResult, setPatternResult] = useState<any>(null);
  const [patternLoading, setPatternLoading] = useState(false);
  const [patternError, setPatternError] = useState<string | null>(null);

  useEffect(() => {
    fetchFraudCases();
    fetchMyCompanies();
  }, []);

  const fetchMyCompanies = async () => {
    try {
      const response = await api.get<{ companies: MyCompany[]; total: number }>('/analysis/my-companies');
      setMyCompanies(response.data.companies || []);
    } catch {
      // Silently fail — autocomplete is non-critical
    }
  };

  const handlePatternMatch = async () => {
    if (!selectedCompany) {
      setPatternError('Please select a company from the suggestions first.');
      return;
    }
    setPatternLoading(true);
    setPatternError(null);
    setPatternResult(null);
    try {
      // Step 1: Get latest analysis ID for selected company
      const analysisRes = await api.get<{ analysis_id: string | null }>(`/companies/${selectedCompany.id}/latest-analysis`);
      const analysisId = analysisRes.data.analysis_id;
      if (!analysisId) {
        setPatternError(`No analysis report found for ${selectedCompany.name}. Please run an analysis first.`);
        return;
      }
      // Step 2: Run pattern match
      const matchRes = await api.post<any>(`/fraud-cases/pattern-match/${analysisId}`, {});
      setPatternResult(matchRes.data);
    } catch (err: any) {
      setPatternError(err.response?.data?.detail || 'Failed to run pattern match. Please try again.');
    } finally {
      setPatternLoading(false);
    }
  };

  const filteredSuggestions = patternQuery.length > 0
    ? myCompanies.filter(c =>
        c.name.toLowerCase().includes(patternQuery.toLowerCase()) ||
        (c.nse_symbol && c.nse_symbol.toLowerCase().includes(patternQuery.toLowerCase()))
      )
    : myCompanies;

  const fetchFraudCases = async () => {
    try {
      setLoading(true);
      setError(null);
      const response = await api.get<FraudCaseListResponse>('/fraud-cases/');
      // API returns { total: number, cases: FraudCase[] }
      const cases = Array.isArray(response.data.cases) ? response.data.cases : [];
      setFraudCases(cases);
    } catch (err: any) {
      console.error('Failed to fetch fraud cases:', err);
      setError('Failed to load fraud cases. Please try again later.');
      setFraudCases([]);
    } finally {
      setLoading(false);
    }
  };

  const sectors = ['All', ...Array.from(new Set(fraudCases.map(c => c.sector).filter(Boolean)))];

  const filteredCases = fraudCases.filter(fraudCase => {
    const matchesSector = sectorFilter === 'All' || fraudCase.sector === sectorFilter;
    const matchesSearch =
      fraudCase.company_name.toLowerCase().includes(searchQuery.toLowerCase()) ||
      (fraudCase.sector && fraudCase.sector.toLowerCase().includes(searchQuery.toLowerCase())) ||
      (fraudCase.fraud_type && fraudCase.fraud_type.toLowerCase().includes(searchQuery.toLowerCase()));
    return matchesSector && matchesSearch;
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
          <p className="text-lg text-gray-900 font-semibold mb-2">Error Loading Fraud Cases</p>
          <p className="text-sm text-gray-600 mb-4">{error}</p>
          <Button onClick={fetchFraudCases}>Retry</Button>
        </div>
      </div>
    );
  }

  if (fraudCases.length === 0) {
    return (
      <div className="flex items-center justify-center min-h-[60vh]">
        <div className="text-center">
          <BookOpen className="h-12 w-12 text-gray-400 mx-auto mb-4" />
          <p className="text-lg text-gray-900 font-semibold mb-2">No Fraud Cases Yet</p>
          <p className="text-sm text-gray-600">
            Fraud cases will appear here once they are added by administrators.
          </p>
        </div>
      </div>
    );
  }

  // --- Detail View ---
  if (selectedCase) {
    const triggeredFlags = selectedCase.red_flags_detected?.filter(f => f.triggered !== false) || selectedCase.red_flags_detected || [];

    return (
      <div className="space-y-6">
        {/* Back Navigation */}
        <button
          onClick={() => setSelectedCase(null)}
          className="flex items-center gap-2 text-sm text-gray-600 hover:text-gray-900"
        >
          <ChevronRight className="h-4 w-4 rotate-180" />
          Back to All Cases
        </button>

        {/* Case Header */}
        <div className="bg-white rounded-lg shadow border border-gray-200 p-6">
          <div className="flex items-start justify-between mb-4">
            <div>
              <h1 className="text-3xl font-bold text-gray-900">{selectedCase.company_name}</h1>
              <div className="flex items-center gap-4 mt-2 text-sm text-gray-600">
                <span className="flex items-center gap-1">
                  <Calendar className="h-4 w-4" />
                  {selectedCase.year}
                </span>
                {selectedCase.sector && (
                  <>
                    <span>•</span>
                    <span
                      className="px-2 py-1 rounded text-xs font-semibold"
                      style={{ backgroundColor: `${getSectorColor(selectedCase.sector)}20`, color: getSectorColor(selectedCase.sector) }}
                    >
                      {selectedCase.sector}
                    </span>
                  </>
                )}
                {selectedCase.detection_difficulty && (
                  <>
                    <span>•</span>
                    <span className="text-xs text-gray-500">Difficulty: {selectedCase.detection_difficulty}</span>
                  </>
                )}
              </div>
            </div>
            <div className="text-right">
              <div className="text-3xl font-bold text-red-600">{selectedCase.stock_decline_percent}%</div>
              <div className="text-sm text-gray-600">Stock Decline</div>
              <div className="text-lg font-semibold text-gray-900 mt-2">
                ₹{selectedCase.market_cap_lost_cr?.toLocaleString()} Cr
              </div>
              <div className="text-xs text-gray-600">Market Cap Lost</div>
            </div>
          </div>

          {/* Fraud Type & Flag Count */}
          <div className="flex gap-3 mt-4 flex-wrap">
            <span className="px-3 py-1 bg-red-100 text-red-800 rounded-full text-sm font-semibold">
              {selectedCase.fraud_type}
            </span>
            <span className="px-3 py-1 bg-orange-100 text-orange-800 rounded-full text-sm font-semibold">
              {triggeredFlags.length} Red Flags Triggered
            </span>
          </div>
        </div>

        {/* Timeline */}
        {selectedCase.timeline && selectedCase.timeline.length > 0 && (
          <div className="bg-white rounded-lg shadow border border-gray-200 p-6">
            <h2 className="text-xl font-bold text-gray-900 mb-4 flex items-center gap-2">
              <Calendar className="h-6 w-6 text-blue-600" />
              Timeline
            </h2>
            <div className="space-y-4">
              {selectedCase.timeline.map((event, idx) => (
                <div key={idx} className="flex gap-4">
                  <div className="flex flex-col items-center">
                    <div
                      className={`w-3 h-3 rounded-full flex-shrink-0 ${
                        event.type === 'red_flag' ? 'bg-orange-500' :
                        event.type === 'investigation' ? 'bg-blue-500' :
                        event.type === 'collapse' ? 'bg-red-600' :
                        'bg-gray-500'
                      }`}
                    />
                    {idx < selectedCase.timeline!.length - 1 && (
                      <div className="w-0.5 h-full bg-gray-300 mt-1" style={{ minHeight: '30px' }} />
                    )}
                  </div>
                  <div className="flex-1 pb-4">
                    <div className="text-sm font-semibold text-gray-900">{event.date}</div>
                    <div className="text-sm text-gray-700 mt-1">{event.event}</div>
                  </div>
                </div>
              ))}
            </div>
          </div>
        )}

        {/* Red Flags Detected */}
        {triggeredFlags.length > 0 && (
          <div className="bg-white rounded-lg shadow border border-gray-200 p-6">
            <h2 className="text-xl font-bold text-gray-900 mb-4 flex items-center gap-2">
              <AlertTriangle className="h-6 w-6 text-orange-500" />
              Red Flags Detected ({triggeredFlags.length})
            </h2>
            <div className="space-y-4">
              {triggeredFlags.map((flag, idx) => (
                <div key={idx} className={`border rounded-lg p-4 ${getSeverityColor(flag.severity)}`}>
                  <div className="flex items-start gap-3">
                    <div className="w-8 h-8 rounded-full bg-orange-500 text-white flex items-center justify-center text-sm font-bold flex-shrink-0">
                      {flag.flag_number || idx + 1}
                    </div>
                    <div className="flex-1">
                      <div className="flex items-center gap-2 flex-wrap">
                        <h3 className="font-semibold text-gray-900">{flag.flag_name || 'Red Flag'}</h3>
                        {flag.severity && (
                          <span className="text-xs font-bold px-2 py-0.5 rounded-full bg-white/60">
                            {flag.severity}
                          </span>
                        )}
                        {flag.category && (
                          <span className="text-xs text-gray-600 bg-white/60 px-2 py-0.5 rounded-full">
                            {flag.category}
                          </span>
                        )}
                      </div>
                      {flag.evidence && (
                        <p className="text-sm text-gray-700 mt-1">{flag.evidence}</p>
                      )}
                    </div>
                  </div>
                </div>
              ))}
            </div>
          </div>
        )}

        {/* What Investors Missed */}
        {selectedCase.what_investors_missed && selectedCase.what_investors_missed.length > 0 && (
          <div className="bg-white rounded-lg shadow border border-gray-200 p-6">
            <h2 className="text-xl font-bold text-gray-900 mb-4 flex items-center gap-2">
              <XCircle className="h-6 w-6 text-red-600" />
              What Investors Missed
            </h2>
            <ul className="space-y-2">
              {selectedCase.what_investors_missed.map((item, idx) => (
                <li key={idx} className="flex items-start gap-2">
                  <XCircle className="h-5 w-5 text-red-500 flex-shrink-0 mt-0.5" />
                  <span className="text-gray-700">{item}</span>
                </li>
              ))}
            </ul>
          </div>
        )}

        {/* Outcome & Regulatory Action */}
        {(selectedCase.outcome || selectedCase.regulatory_action) && (
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            {selectedCase.outcome && (
              <div className="bg-white rounded-lg shadow border border-gray-200 p-6">
                <h2 className="text-lg font-bold text-gray-900 mb-3 flex items-center gap-2">
                  <TrendingDown className="h-5 w-5 text-red-600" />
                  Outcome
                </h2>
                <p className="text-gray-700 text-sm">{selectedCase.outcome}</p>
              </div>
            )}
            {selectedCase.regulatory_action && (
              <div className="bg-white rounded-lg shadow border border-gray-200 p-6">
                <h2 className="text-lg font-bold text-gray-900 mb-3 flex items-center gap-2">
                  <Scale className="h-5 w-5 text-blue-600" />
                  Regulatory Action
                </h2>
                <p className="text-gray-700 text-sm">{selectedCase.regulatory_action}</p>
              </div>
            )}
          </div>
        )}

        {/* Lessons Learned */}
        {selectedCase.lessons_learned && selectedCase.lessons_learned.length > 0 && (
          <div className="bg-gradient-to-br from-blue-50 to-green-50 rounded-lg border border-blue-200 p-6">
            <h2 className="text-xl font-bold text-gray-900 mb-4 flex items-center gap-2">
              <CheckCircle2 className="h-6 w-6 text-green-600" />
              Lessons Learned
            </h2>
            <ul className="space-y-2">
              {selectedCase.lessons_learned.map((lesson, idx) => (
                <li key={idx} className="flex items-start gap-2">
                  <CheckCircle2 className="h-5 w-5 text-green-600 flex-shrink-0 mt-0.5" />
                  <span className="text-gray-800 font-medium">{lesson}</span>
                </li>
              ))}
            </ul>
          </div>
        )}
      </div>
    );
  }

  // --- List View ---
  return (
    <div className="space-y-6">
      {/* Header */}
      <div>
        <h1 className="text-3xl font-bold text-gray-900 flex items-center gap-3">
          <BookOpen className="h-8 w-8 text-blue-600" />
          Fraud Database
        </h1>
        <p className="text-gray-600 mt-2">
          Learn from {fraudCases.length} historical fraud cases. Understand red flags and protect your investments.
        </p>
      </div>

      {/* Pattern Matching Banner */}
      <div className="bg-gradient-to-r from-purple-600 to-blue-600 rounded-lg p-6 text-white">
        <div className="flex items-center justify-between">
          <div>
            <h2 className="text-xl font-bold mb-2">Check Your Stock for Fraud Patterns</h2>
            <p className="text-blue-100">
              Enter a company name to see if it matches patterns from historical frauds
            </p>
          </div>
          <Button
            onClick={() => setShowPatternMatch(!showPatternMatch)}
            className="bg-white text-purple-600 hover:bg-blue-50"
          >
            {showPatternMatch ? 'Hide' : 'Try Now'}
          </Button>
        </div>
      </div>

      {/* Pattern Match Section */}
      {showPatternMatch && (
        <div className="bg-white rounded-lg shadow border border-gray-200 p-6">
          <div className="flex gap-3">
            <div className="relative flex-1">
              <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 h-5 w-5 text-gray-400" />
              <input
                type="text"
                value={patternQuery}
                onChange={(e) => { setPatternQuery(e.target.value); setShowSuggestions(true); setSelectedCompany(null); setPatternResult(null); setPatternError(null); }}
                onFocus={() => setShowSuggestions(true)}
                onBlur={() => setTimeout(() => setShowSuggestions(false), 150)}
                placeholder="Enter company name or symbol..."
                className="w-full pl-10 pr-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                autoComplete="off"
              />
              {/* Autocomplete dropdown */}
              {showSuggestions && filteredSuggestions.length > 0 && (
                <div className="absolute z-10 w-full mt-1 bg-white border border-gray-200 rounded-lg shadow-lg max-h-56 overflow-y-auto">
                  {filteredSuggestions.map((company) => (
                    <button
                      key={company.id}
                      className="w-full text-left px-4 py-2.5 hover:bg-blue-50 flex items-center justify-between"
                      onMouseDown={() => {
                        setPatternQuery(company.name);
                        setSelectedCompany(company);
                        setPatternResult(null);
                        setPatternError(null);
                        setShowSuggestions(false);
                      }}
                    >
                      <span className="text-sm font-medium text-gray-900">{company.name}</span>
                      {company.nse_symbol && (
                        <span className="text-xs text-gray-500 bg-gray-100 px-2 py-0.5 rounded">{company.nse_symbol}</span>
                      )}
                    </button>
                  ))}
                </div>
              )}
            </div>
            <Button onClick={handlePatternMatch} disabled={patternLoading || !patternQuery.trim()}>
              {patternLoading ? (
                <><Loader2 className="mr-2 h-4 w-4 animate-spin" />Analyzing...</>
              ) : 'Analyze Patterns'}
            </Button>
          </div>
          <p className="text-xs text-gray-500 mt-3 flex items-start gap-1.5">
            <span className="text-blue-500 mt-0.5">ℹ</span>
            Only companies whose reports have been generated — via Analyze, Watchlist, or Portfolio — are shown in suggestions.
          </p>

          {/* Error */}
          {patternError && (
            <div className="mt-4 p-3 bg-red-50 border border-red-200 rounded-lg text-sm text-red-700">
              {patternError}
            </div>
          )}

          {/* Pattern Match Results */}
          {patternResult && (
            <div className="mt-6 space-y-4">
              {/* Summary */}
              <div className={`p-4 rounded-lg border-2 ${
                patternResult.risk_level === 'CRITICAL' ? 'bg-red-50 border-red-400' :
                patternResult.risk_level === 'HIGH' ? 'bg-orange-50 border-orange-400' :
                patternResult.risk_level === 'MEDIUM' ? 'bg-yellow-50 border-yellow-400' :
                'bg-green-50 border-green-400'
              }`}>
                <div className="flex items-center justify-between mb-1">
                  <h3 className="font-bold text-gray-900">{patternResult.company_name}</h3>
                  <span className={`px-3 py-1 rounded-full text-sm font-bold ${
                    patternResult.risk_level === 'CRITICAL' ? 'bg-red-100 text-red-800' :
                    patternResult.risk_level === 'HIGH' ? 'bg-orange-100 text-orange-800' :
                    patternResult.risk_level === 'MEDIUM' ? 'bg-yellow-100 text-yellow-800' :
                    'bg-green-100 text-green-800'
                  }`}>{patternResult.risk_level}</span>
                </div>
                <p className="text-sm text-gray-700">{patternResult.message}</p>
                <div className="flex gap-4 mt-2 text-xs text-gray-600">
                  <span>{patternResult.triggered_flags_count} flags triggered</span>
                  <span>{patternResult.total_matches} fraud case matches</span>
                </div>
              </div>

              {/* Matches */}
              {patternResult.matches && patternResult.matches.length > 0 && (
                <div className="space-y-3">
                  <h4 className="font-semibold text-gray-900">Top Matching Fraud Cases:</h4>
                  {patternResult.matches.map((match: any, idx: number) => (
                    <div key={idx} className="bg-gray-50 border border-gray-200 rounded-lg p-4">
                      <div className="flex items-center justify-between mb-2">
                        <span className="font-semibold text-gray-900">{match.company_name}</span>
                        <span className={`text-sm font-bold px-2 py-0.5 rounded ${
                          match.similarity_score >= 70 ? 'bg-red-100 text-red-700' :
                          match.similarity_score >= 50 ? 'bg-orange-100 text-orange-700' :
                          'bg-yellow-100 text-yellow-700'
                        }`}>{match.similarity_score?.toFixed(0)}% match</span>
                      </div>
                      {match.matching_flags && match.matching_flags.length > 0 && (
                        <div className="flex flex-wrap gap-1 mt-1">
                          {match.matching_flags.map((flag: any, fidx: number) => (
                            <span key={fidx} className="text-xs bg-orange-100 text-orange-800 px-2 py-0.5 rounded">
                              {flag.flag_name || `Flag #${flag.flag_number}`}
                            </span>
                          ))}
                        </div>
                      )}
                    </div>
                  ))}
                </div>
              )}
            </div>
          )}
        </div>
      )}

      {/* Search & Filter */}
      <div className="bg-white rounded-lg shadow border border-gray-200 p-4">
        <div className="flex flex-col md:flex-row gap-4">
          <div className="relative flex-1">
            <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 h-5 w-5 text-gray-400" />
            <input
              type="text"
              placeholder="Search companies, fraud type..."
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              className="w-full pl-10 pr-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
            />
          </div>
          <div className="flex items-center gap-2">
            <Filter className="h-5 w-5 text-gray-600" />
            <select
              value={sectorFilter}
              onChange={(e) => setSectorFilter(e.target.value)}
              className="px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
            >
              {sectors.map(sector => (
                <option key={sector} value={sector}>{sector}</option>
              ))}
            </select>
          </div>
        </div>
      </div>

      {/* Cases Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        {filteredCases.map((fraudCase) => (
          <div
            key={fraudCase.case_id}
            onClick={() => setSelectedCase(fraudCase)}
            className="bg-white rounded-lg shadow border border-gray-200 p-6 hover:border-blue-300 hover:shadow-lg transition-all cursor-pointer"
          >
            <div className="flex items-start justify-between mb-3">
              <div>
                <h3 className="text-xl font-bold text-gray-900">{fraudCase.company_name}</h3>
                <div className="flex items-center gap-2 mt-1 text-sm text-gray-600">
                  <span>{fraudCase.year}</span>
                  <span>•</span>
                  <span>{fraudCase.industry || fraudCase.sector}</span>
                </div>
              </div>
              <span
                className="px-2 py-1 rounded text-xs font-semibold"
                style={{ backgroundColor: `${getSectorColor(fraudCase.sector)}20`, color: getSectorColor(fraudCase.sector) }}
              >
                {fraudCase.sector}
              </span>
            </div>

            <div className="grid grid-cols-2 gap-4 mb-4">
              <div>
                <div className="text-2xl font-bold text-red-600">{fraudCase.stock_decline_percent}%</div>
                <div className="text-xs text-gray-600">Stock Decline</div>
              </div>
              <div>
                <div className="text-lg font-semibold text-gray-900">
                  ₹{fraudCase.market_cap_lost_cr?.toLocaleString()} Cr
                </div>
                <div className="text-xs text-gray-600">Market Cap Lost</div>
              </div>
            </div>

            {/* Primary Flags */}
            {fraudCase.primary_flags && fraudCase.primary_flags.length > 0 && (
              <div className="space-y-2 mb-4">
                <div className="text-sm font-semibold text-gray-700">Primary Red Flags:</div>
                <div className="flex flex-wrap gap-2">
                  {fraudCase.primary_flags.slice(0, 3).map((flag, idx) => (
                    <span key={idx} className="px-2 py-1 bg-orange-100 text-orange-800 rounded text-xs">
                      {flag}
                    </span>
                  ))}
                </div>
              </div>
            )}

            <div className="flex items-center justify-between pt-3 border-t border-gray-200">
              <span className="text-sm text-gray-600">{fraudCase.fraud_type}</span>
              <div className="flex items-center gap-2">
                <span className="text-xs text-orange-600 font-semibold">
                  {fraudCase.red_flags_detected?.length || 0} flags
                </span>
                <ChevronRight className="h-5 w-5 text-blue-600" />
              </div>
            </div>
          </div>
        ))}
      </div>

      {filteredCases.length === 0 && (
        <div className="text-center py-12 text-gray-500">
          No fraud cases found matching your search criteria
        </div>
      )}
    </div>
  );
}
