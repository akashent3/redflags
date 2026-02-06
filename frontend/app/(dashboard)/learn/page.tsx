'use client';

/**
 * Learning Page - Fraud Database & Pattern Matching
 *
 * Historical fraud cases with timeline, red flags, and lessons
 */

import { useState } from 'react';
import { Button } from '@/components/ui/button';
import {
  BookOpen,
  AlertTriangle,
  TrendingDown,
  Search,
  Filter,
  ChevronRight,
  Calendar,
  Building2,
  DollarSign,
  Scale,
  CheckCircle2,
  XCircle,
} from 'lucide-react';
import { FRAUD_CASES, FRAUD_PATTERNS } from '@/lib/data/fraudCases';
import { FraudCase, getSectorColor, getDifficultyColor } from '@/lib/types/fraud';

export default function LearnPage() {
  const [selectedCase, setSelectedCase] = useState<FraudCase | null>(null);
  const [sectorFilter, setSectorFilter] = useState<string>('All');
  const [searchQuery, setSearchQuery] = useState('');
  const [showPatternMatch, setShowPatternMatch] = useState(false);

  const sectors = ['All', ...Array.from(new Set(FRAUD_CASES.map(c => c.sector)))];

  const filteredCases = FRAUD_CASES.filter(fraudCase => {
    const matchesSector = sectorFilter === 'All' || fraudCase.sector === sectorFilter;
    const matchesSearch = fraudCase.company_name.toLowerCase().includes(searchQuery.toLowerCase()) ||
                         fraudCase.industry.toLowerCase().includes(searchQuery.toLowerCase());
    return matchesSector && matchesSearch;
  });

  if (selectedCase) {
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
                <span>•</span>
                <span className="flex items-center gap-1">
                  <Building2 className="h-4 w-4" />
                  {selectedCase.industry}
                </span>
                <span>•</span>
                <span
                  className="px-2 py-1 rounded text-xs font-semibold"
                  style={{ backgroundColor: `${getSectorColor(selectedCase.sector)}20`, color: getSectorColor(selectedCase.sector) }}
                >
                  {selectedCase.sector}
                </span>
              </div>
            </div>
            <div className="text-right">
              <div className="text-3xl font-bold text-red-600">{selectedCase.stock_decline_percent}%</div>
              <div className="text-sm text-gray-600">Stock Decline</div>
              <div className="text-lg font-semibold text-gray-900 mt-2">₹{selectedCase.market_cap_lost_cr.toLocaleString()} Cr</div>
              <div className="text-xs text-gray-600">Market Cap Lost</div>
            </div>
          </div>

          {/* Fraud Type & Detection */}
          <div className="flex gap-3 mt-4">
            <span className="px-3 py-1 bg-red-100 text-red-800 rounded-full text-sm font-semibold">
              {selectedCase.fraud_type}
            </span>
            <span
              className="px-3 py-1 rounded-full text-sm font-semibold"
              style={{
                backgroundColor: `${getDifficultyColor(selectedCase.detection_difficulty)}20`,
                color: getDifficultyColor(selectedCase.detection_difficulty),
              }}
            >
              Detection: {selectedCase.detection_difficulty}
            </span>
          </div>
        </div>

        {/* Timeline */}
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
                    className={`w-3 h-3 rounded-full ${
                      event.type === 'red_flag' ? 'bg-orange-500' :
                      event.type === 'investigation' ? 'bg-blue-500' :
                      event.type === 'collapse' ? 'bg-red-600' :
                      'bg-gray-500'
                    }`}
                  />
                  {idx < selectedCase.timeline.length - 1 && (
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

        {/* Red Flags Detected */}
        <div className="bg-white rounded-lg shadow border border-gray-200 p-6">
          <h2 className="text-xl font-bold text-gray-900 mb-4 flex items-center gap-2">
            <AlertTriangle className="h-6 w-6 text-orange-500" />
            Red Flags Detected
          </h2>
          <div className="space-y-4">
            {selectedCase.red_flags_detected.map((flag, idx) => (
              <div key={idx} className="border border-orange-200 bg-orange-50 rounded-lg p-4">
                <div className="flex items-start gap-3">
                  <div className="w-8 h-8 rounded-full bg-orange-500 text-white flex items-center justify-center text-sm font-bold flex-shrink-0">
                    {flag.flag_number}
                  </div>
                  <div className="flex-1">
                    <h3 className="font-semibold text-gray-900">{flag.flag_name}</h3>
                    <p className="text-sm text-gray-700 mt-1">{flag.evidence}</p>
                    <div className="text-xs text-orange-700 mt-2 font-semibold">
                      Visible {flag.when_visible} collapse
                    </div>
                  </div>
                </div>
              </div>
            ))}
          </div>
        </div>

        {/* What Investors Missed */}
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

        {/* Outcome & Regulatory Action */}
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          <div className="bg-white rounded-lg shadow border border-gray-200 p-6">
            <h2 className="text-lg font-bold text-gray-900 mb-3 flex items-center gap-2">
              <TrendingDown className="h-5 w-5 text-red-600" />
              Outcome
            </h2>
            <p className="text-gray-700 text-sm">{selectedCase.outcome}</p>
          </div>
          <div className="bg-white rounded-lg shadow border border-gray-200 p-6">
            <h2 className="text-lg font-bold text-gray-900 mb-3 flex items-center gap-2">
              <Scale className="h-5 w-5 text-blue-600" />
              Regulatory Action
            </h2>
            <p className="text-gray-700 text-sm">{selectedCase.regulatory_action}</p>
          </div>
        </div>

        {/* Lessons Learned */}
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
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div>
        <h1 className="text-3xl font-bold text-gray-900 flex items-center gap-3">
          <BookOpen className="h-8 w-8 text-blue-600" />
          Fraud Database
        </h1>
        <p className="text-gray-600 mt-2">
          Learn from {FRAUD_CASES.length} historical fraud cases. Understand red flags and protect your investments.
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
                placeholder="Enter company name or symbol..."
                className="w-full pl-10 pr-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
              />
            </div>
            <Button>Analyze Patterns</Button>
          </div>
          <p className="text-sm text-gray-600 mt-3">
            This feature will compare your stock's red flags with {FRAUD_PATTERNS.length} fraud patterns from history
          </p>
        </div>
      )}

      {/* Search & Filter */}
      <div className="bg-white rounded-lg shadow border border-gray-200 p-4">
        <div className="flex flex-col md:flex-row gap-4">
          <div className="relative flex-1">
            <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 h-5 w-5 text-gray-400" />
            <input
              type="text"
              placeholder="Search companies..."
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
                  <span>{fraudCase.industry}</span>
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
                <div className="text-lg font-semibold text-gray-900">₹{fraudCase.market_cap_lost_cr.toLocaleString()} Cr</div>
                <div className="text-xs text-gray-600">Market Cap Lost</div>
              </div>
            </div>

            <div className="space-y-2 mb-4">
              <div className="text-sm font-semibold text-gray-700">Primary Red Flags:</div>
              <div className="flex flex-wrap gap-2">
                {fraudCase.primary_flags.map((flag, idx) => (
                  <span key={idx} className="px-2 py-1 bg-orange-100 text-orange-800 rounded text-xs">
                    {flag}
                  </span>
                ))}
              </div>
            </div>

            <div className="flex items-center justify-between pt-3 border-t border-gray-200">
              <span className="text-sm text-gray-600">{fraudCase.fraud_type}</span>
              <ChevronRight className="h-5 w-5 text-blue-600" />
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
