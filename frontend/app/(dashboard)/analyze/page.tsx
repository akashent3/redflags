'use client';

/**
 * Analysis Page
 *
 * Debounced autocomplete search via FinEdge API → one-click Analyze.
 * Same search source as Watchlist and Portfolio add-stock.
 */

import { useState, useRef, useCallback, useEffect } from 'react';
import { useRouter } from 'next/navigation';
import { Button } from '@/components/ui/button';
import { Search, Loader2, AlertCircle, Building2, X } from 'lucide-react';
import { api } from '@/lib/api/client';

// Shape returned by /companies/finedge/search
interface FinEdgeResult {
  symbol: string;
  name: string;
  nse_code: string;
  bse_code: string;
  exchange: string;
  isin: string;
}

export default function AnalyzePage() {
  const router = useRouter();

  // Search state
  const [searchQuery, setSearchQuery]         = useState('');
  const [suggestions, setSuggestions]         = useState<FinEdgeResult[]>([]);
  const [searchLoading, setSearchLoading]     = useState(false);
  const [showDropdown, setShowDropdown]       = useState(false);
  const [selectedCompany, setSelectedCompany] = useState<FinEdgeResult | null>(null);

  // Analysis state
  const [isAnalyzing, setIsAnalyzing] = useState(false);
  const [error, setError]             = useState<string | null>(null);

  const searchRef   = useRef<HTMLDivElement>(null);
  const debounceRef = useRef<ReturnType<typeof setTimeout> | null>(null);

  // Close dropdown on outside click
  useEffect(() => {
    const handler = (e: MouseEvent) => {
      if (searchRef.current && !searchRef.current.contains(e.target as Node)) {
        setShowDropdown(false);
      }
    };
    document.addEventListener('mousedown', handler);
    return () => document.removeEventListener('mousedown', handler);
  }, []);

  // Debounced autocomplete — calls FinEdge search (same source as Watchlist & Portfolio)
  const handleSearchInput = useCallback((value: string) => {
    setSearchQuery(value);
    setSelectedCompany(null);
    setError(null);
    if (debounceRef.current) clearTimeout(debounceRef.current);
    if (!value.trim()) {
      setSuggestions([]);
      setShowDropdown(false);
      return;
    }
    debounceRef.current = setTimeout(async () => {
      try {
        setSearchLoading(true);
        const res = await api.get(
          `/companies/finedge/search?q=${encodeURIComponent(value)}&limit=10`
        );
        const results: FinEdgeResult[] = res.data.results || [];
        setSuggestions(results);
        setShowDropdown(results.length > 0);
      } catch {
        setSuggestions([]);
        setShowDropdown(false);
      } finally {
        setSearchLoading(false);
      }
    }, 300);
  }, []);

  const handleSelectCompany = (company: FinEdgeResult) => {
    setSelectedCompany(company);
    // Display whichever code is available
    const code = company.nse_code || company.symbol;
    setSearchQuery(`${code} — ${company.name}`);
    setShowDropdown(false);
    setSuggestions([]);
  };

  const clearSearch = () => {
    setSearchQuery('');
    setSelectedCompany(null);
    setSuggestions([]);
    setShowDropdown(false);
    setError(null);
  };

  // ── Analysis ────────────────────────────────────────────────────────────────

  const pollTaskStatus = async (taskId: string): Promise<any> => {
    const maxAttempts = 120; // 10 minutes
    let attempts = 0;
    while (attempts < maxAttempts) {
      const response = await api.get(`/analysis/task/${taskId}`);
      const status = response.data.status;
      if (status === 'SUCCESS') return response.data;
      if (status === 'FAILURE') throw new Error(response.data.error || 'Analysis failed');
      await new Promise(resolve => setTimeout(resolve, 5000));
      attempts++;
    }
    throw new Error('Analysis timed out');
  };

  const handleAnalyze = async () => {
    if (!selectedCompany) return;
    setIsAnalyzing(true);
    setError(null);

    try {
      // Use nse_code if available, fall back to symbol
      const symbol = selectedCompany.nse_code || selectedCompany.symbol;
      const response = await api.post(`/analysis/analyze-symbol/${symbol}`);

      // Already completed — redirect immediately
      if (response.data.status === 'COMPLETED') {
        const analysisId = response.data.analysis_id;
        if (!analysisId) throw new Error('No analysis ID returned');
        router.push(`/report/${analysisId}`);
        return;
      }

      // New analysis — poll for completion
      const taskId = response.data.task_id;
      if (!taskId) throw new Error('No task ID returned from server');

      const result = await pollTaskStatus(taskId);
      const analysisId =
        result.analysis_id ||
        result.result?.analysis_id ||
        result.data?.analysis_id;

      if (!analysisId) throw new Error('No analysis ID in result');
      router.push(`/report/${analysisId}`);

    } catch (err: any) {
      setError(
        err.response?.data?.detail || err.message || 'Analysis failed. Please try again.'
      );
      setIsAnalyzing(false);
    }
  };

  // ── Render ──────────────────────────────────────────────────────────────────

  return (
    <div className="space-y-8">
      {/* Page header */}
      <div>
        <h1 className="text-3xl font-bold text-gray-900">Analyze Report</h1>
        <p className="mt-2 text-gray-600">
          Search any NSE / BSE listed company and run a red-flag analysis
        </p>
      </div>

      <div className="max-w-4xl">
        <div className="bg-white rounded-lg shadow border border-gray-200 p-8">

          {/* Error */}
          {error && (
            <div className="bg-red-50 border border-red-200 text-red-800 px-4 py-3 rounded-md flex items-start gap-3 mb-6">
              <AlertCircle className="h-5 w-5 mt-0.5 flex-shrink-0" />
              <div className="flex-1">
                <p className="text-sm font-medium">Error</p>
                <p className="text-sm mt-1">{error}</p>
              </div>
              <button onClick={() => setError(null)} className="text-red-600 hover:text-red-800">×</button>
            </div>
          )}

          {/* Analyzing status */}
          {isAnalyzing && selectedCompany && (
            <div className="bg-blue-50 border border-blue-200 text-blue-800 px-4 py-3 rounded-md flex items-start gap-3 mb-6">
              <Loader2 className="h-5 w-5 mt-0.5 flex-shrink-0 animate-spin" />
              <div className="flex-1">
                <p className="text-sm font-medium">
                  Analyzing {selectedCompany.nse_code || selectedCompany.symbol}
                </p>
                <p className="text-sm mt-1">
                  Checking for existing analysis or fetching the latest annual report from NSE India…
                </p>
              </div>
            </div>
          )}

          {/* Autocomplete search + Analyze button */}
          <div className="mb-6">
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Search Company
            </label>
            <div className="flex gap-3 items-start">

              {/* Input + dropdown */}
              <div className="flex-1 relative" ref={searchRef}>
                <div className="relative">
                  <Search className="absolute left-3 top-1/2 -translate-y-1/2 h-5 w-5 text-gray-400 pointer-events-none" />
                  <input
                    type="text"
                    placeholder="Type company name or NSE symbol (e.g. Reliance, TCS, INFY)…"
                    value={searchQuery}
                    onChange={e => handleSearchInput(e.target.value)}
                    onFocus={() => suggestions.length > 0 && setShowDropdown(true)}
                    disabled={isAnalyzing}
                    className="w-full pl-10 pr-10 py-3 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500 disabled:bg-gray-100 disabled:cursor-not-allowed"
                  />
                  {searchQuery && !isAnalyzing && (
                    <button
                      onClick={clearSearch}
                      className="absolute right-3 top-1/2 -translate-y-1/2 text-gray-400 hover:text-gray-600"
                    >
                      <X className="h-4 w-4" />
                    </button>
                  )}
                  {searchLoading && (
                    <Loader2 className="absolute right-3 top-1/2 -translate-y-1/2 h-4 w-4 animate-spin text-blue-500" />
                  )}
                </div>

                {/* Dropdown results */}
                {showDropdown && suggestions.length > 0 && (
                  <div className="absolute z-50 w-full mt-1 bg-white border border-gray-200 rounded-lg shadow-lg max-h-72 overflow-y-auto">
                    {suggestions.map((company, idx) => {
                      const code = company.nse_code || company.symbol;
                      return (
                        <button
                          key={`${company.symbol}-${idx}`}
                          onClick={() => handleSelectCompany(company)}
                          className="w-full text-left px-4 py-3 hover:bg-blue-50 border-b border-gray-100 last:border-0 transition-colors"
                        >
                          <div className="flex items-center justify-between">
                            <div className="flex items-center gap-2 min-w-0">
                              <Building2 className="h-4 w-4 text-gray-400 flex-shrink-0" />
                              <span className="font-semibold text-blue-700 text-sm flex-shrink-0">{code}</span>
                              <span className="text-gray-700 text-sm truncate">{company.name}</span>
                            </div>
                            {company.exchange && (
                              <span className="text-xs text-gray-400 ml-2 flex-shrink-0">{company.exchange}</span>
                            )}
                          </div>
                          {company.bse_code && company.nse_code && (
                            <p className="text-xs text-gray-400 mt-0.5 ml-6">
                              BSE: {company.bse_code}
                            </p>
                          )}
                        </button>
                      );
                    })}
                  </div>
                )}

                {/* No results */}
                {showDropdown && suggestions.length === 0 && !searchLoading && searchQuery.length >= 2 && (
                  <div className="absolute z-50 w-full mt-1 bg-white border border-gray-200 rounded-lg shadow-lg">
                    <div className="px-4 py-3 text-sm text-gray-500 text-center">
                      No companies found for &quot;{searchQuery}&quot;
                    </div>
                  </div>
                )}
              </div>

              {/* Analyze button — enabled only after selection */}
              <Button
                onClick={handleAnalyze}
                disabled={!selectedCompany || isAnalyzing}
                className="py-3 px-6 flex-shrink-0"
              >
                {isAnalyzing ? (
                  <><Loader2 className="mr-2 h-4 w-4 animate-spin" />Analyzing…</>
                ) : (
                  'Analyze'
                )}
              </Button>
            </div>

            {/* Selected company chip */}
            {selectedCompany && !isAnalyzing && (
              <div className="mt-3 flex items-center gap-2 text-sm text-green-700 bg-green-50 border border-green-200 px-3 py-2 rounded-lg">
                <Building2 className="h-4 w-4 flex-shrink-0" />
                <span className="font-semibold">{selectedCompany.nse_code || selectedCompany.symbol}</span>
                <span>—</span>
                <span>{selectedCompany.name}</span>
                {selectedCompany.exchange && (
                  <span className="text-gray-500 text-xs ml-auto">{selectedCompany.exchange}</span>
                )}
              </div>
            )}

            <p className="text-sm text-gray-500 mt-3">
              💡 Start typing to search, select a company from the dropdown, then click <strong>Analyze</strong>
            </p>
          </div>

          {/* Empty state */}
          {!selectedCompany && !searchQuery && (
            <div className="text-center py-10 border-t border-gray-100">
              <Search className="h-12 w-12 text-gray-300 mx-auto mb-3" />
              <p className="text-gray-500 font-medium">Search NSE / BSE Listed Companies</p>
              <p className="text-sm text-gray-400 mt-1">
                Enter a company name or stock symbol above to get started
              </p>
            </div>
          )}
        </div>

        {/* How it works */}
        <div className="mt-6 bg-blue-50 border border-blue-200 rounded-lg p-4">
          <p className="text-sm text-blue-800">
            <strong>How it works:</strong> Search any NSE / BSE listed company. If an analysis already
            exists you&apos;ll be redirected instantly (&lt; 1 second). Otherwise we fetch the latest
            annual report from NSE India, extract financials via FinEdge API, and analyse red flags
            using AI. New analyses typically take 1–2 minutes.
          </p>
        </div>
      </div>
    </div>
  );
}
