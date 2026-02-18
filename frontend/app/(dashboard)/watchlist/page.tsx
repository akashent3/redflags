'use client';

/**
 * Watchlist Page
 *
 * Manage watchlist with real-time prices and auto-analysis
 */

import { useEffect, useState, useRef, useCallback } from 'react';
import { useRouter } from 'next/navigation';
import { api } from '@/lib/api/client';
import { Button } from '@/components/ui/button';
import {
  Plus,
  Trash2,
  TrendingUp,
  TrendingDown,
  Loader2,
  AlertCircle,
  FileText,
  Search,
  Eye,
  X,
} from 'lucide-react';

// Shape returned by /companies/finedge/search
interface CompanySearchResult {
  symbol: string;
  name: string;
  nse_code: string;
  bse_code: string;
  exchange: string;
  isin: string;
}

interface WatchlistItem {
  watchlist_id: string;
  symbol: string;
  company_name: string;
  added_date: string;
  current_price: number | null;
  price_change: number | null;
  price_change_percent: number | null;
  high: number | null;
  low: number | null;
  volume: number | null;
  current_risk_score: number | null;
  current_risk_level: string | null;
  last_analysis_date: string | null;
  latest_analysis_id: string | null;
}

interface WatchlistResponse {
  user_id: string;
  items: WatchlistItem[];
  alerts: any[];
}

/** Extract a human-readable string from a FastAPI/Pydantic error response. */
function parseApiError(err: any, fallback: string): string {
  const detail = err?.response?.data?.detail;
  if (!detail) return fallback;
  if (Array.isArray(detail)) {
    return detail.map((d: any) => d?.msg || JSON.stringify(d)).join(', ');
  }
  if (typeof detail === 'string') return detail;
  return fallback;
}

export default function WatchlistPage() {
  const router = useRouter();
  const [watchlist, setWatchlist] = useState<WatchlistItem[]>([]);
  // isLoading: only true on the very first mount — shows full-page spinner once
  const [isLoading, setIsLoading] = useState(true);
  const [addingSymbol, setAddingSymbol] = useState(false);
  const [error, setError] = useState<string | null>(null);
  // Tracks which symbols just got their score (for green-flash animation)
  const [justScored, setJustScored] = useState<Set<string>>(new Set());

  // Autocomplete search state
  const [searchQuery, setSearchQuery] = useState('');
  const [suggestions, setSuggestions] = useState<CompanySearchResult[]>([]);
  const [searchLoading, setSearchLoading] = useState(false);
  const [showDropdown, setShowDropdown] = useState(false);
  const [selectedCompany, setSelectedCompany] = useState<CompanySearchResult | null>(null);
  const searchRef = useRef<HTMLDivElement>(null);
  const debounceRef = useRef<ReturnType<typeof setTimeout> | null>(null);
  const pollingRef = useRef<ReturnType<typeof setInterval> | null>(null);
  // Keep a ref to current watchlist so the silent poll closure always sees fresh data
  const watchlistRef = useRef<WatchlistItem[]>([]);

  useEffect(() => {
    // Initial load — show spinner
    fetchWatchlist(true);
    return () => {
      if (pollingRef.current) clearInterval(pollingRef.current);
    };
  }, []);

  // Start/stop silent background polling whenever pending items change
  useEffect(() => {
    watchlistRef.current = watchlist;
    const hasPending = watchlist.some(item => item.current_risk_score === null);
    if (hasPending) {
      if (!pollingRef.current) {
        pollingRef.current = setInterval(() => {
          fetchWatchlist(false); // silent — no spinner, no page flash
        }, 10000);
      }
    } else {
      if (pollingRef.current) {
        clearInterval(pollingRef.current);
        pollingRef.current = null;
      }
    }
  }, [watchlist]);

  // Close dropdown when clicking outside
  useEffect(() => {
    const handleClickOutside = (e: MouseEvent) => {
      if (searchRef.current && !searchRef.current.contains(e.target as Node)) {
        setShowDropdown(false);
      }
    };
    document.addEventListener('mousedown', handleClickOutside);
    return () => document.removeEventListener('mousedown', handleClickOutside);
  }, []);

  // Debounced search — calls FinEdge search (all NSE/BSE companies)
  const handleSearchInput = useCallback((value: string) => {
    setSearchQuery(value);
    setSelectedCompany(null);
    if (debounceRef.current) clearTimeout(debounceRef.current);
    if (!value.trim()) {
      setSuggestions([]);
      setShowDropdown(false);
      return;
    }
    debounceRef.current = setTimeout(async () => {
      try {
        setSearchLoading(true);
        const response = await api.get(`/companies/finedge/search?q=${encodeURIComponent(value)}&limit=10`);
        const results: CompanySearchResult[] = response.data.results || [];
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

  const handleSelectCompany = (company: CompanySearchResult) => {
    setSelectedCompany(company);
    const code = company.nse_code || company.symbol;
    setSearchQuery(`${code} — ${company.name}`);
    setShowDropdown(false);
    setSuggestions([]);
  };

  /**
   * Fetch watchlist data.
   * @param showSpinner - true only on the very first load; false for background polls.
   */
  const fetchWatchlist = async (showSpinner: boolean) => {
    try {
      if (showSpinner) setIsLoading(true);

      const response = await api.get<WatchlistResponse>('/watchlist/');
      const newItems: WatchlistItem[] = response.data.items || [];

      setWatchlist(prev => {
        // Find which items just received a score for the first time
        const newlyScored = new Set<string>();
        newItems.forEach(newItem => {
          const old = prev.find(p => p.watchlist_id === newItem.watchlist_id);
          if (old && old.current_risk_score === null && newItem.current_risk_score !== null) {
            newlyScored.add(newItem.watchlist_id);
          }
        });

        if (newlyScored.size > 0) {
          setJustScored(prev => {
            const next = new Set(prev);
            newlyScored.forEach(id => next.add(id));
            return next;
          });
          // Remove flash class after 1.5 s
          setTimeout(() => {
            setJustScored(prev => {
              const next = new Set(prev);
              newlyScored.forEach(id => next.delete(id));
              return next;
            });
          }, 1500);
        }

        return newItems;
      });
    } catch (err: any) {
      // Only show error banner on explicit (non-silent) loads
      if (showSpinner) {
        setError(parseApiError(err, 'Failed to load watchlist'));
      }
    } finally {
      if (showSpinner) setIsLoading(false);
    }
  };

  const handleAddSymbol = async () => {
    if (!selectedCompany) return;
    try {
      setAddingSymbol(true);
      setError(null);

      // Step 1: Ensure company exists in local DB (creates it if new) — returns UUID
      const ensureRes = await api.post('/companies/ensure-by-symbol', {
        symbol: selectedCompany.nse_code || selectedCompany.symbol,
        name: selectedCompany.name,
      });
      const companyId = ensureRes.data.company_id;

      // Step 2: Add to watchlist using the UUID (existing flow — unchanged)
      await api.post('/watchlist/', {
        company_id: companyId,
        alert_enabled: true,
      });

      setSearchQuery('');
      setSelectedCompany(null);
      setSuggestions([]);
      await fetchWatchlist(false);
    } catch (err: any) {
      setError(parseApiError(err, 'Failed to add company to watchlist'));
    } finally {
      setAddingSymbol(false);
    }
  };

  const handleRemoveSymbol = async (watchlistId: string, symbol: string) => {
    if (!confirm(`Remove ${symbol} from watchlist?`)) return;
    try {
      await api.delete(`/watchlist/${watchlistId}`);
      // Optimistically remove from state — no full reload needed
      setWatchlist(prev => prev.filter(item => item.watchlist_id !== watchlistId));
    } catch (err: any) {
      setError(parseApiError(err, 'Failed to remove from watchlist'));
    }
  };

  const getRiskColor = (level: string | null) => {
    if (!level) return 'text-gray-600 bg-gray-100';
    switch (level) {
      case 'CLEAN':   return 'text-green-600 bg-green-100';
      case 'LOW':     return 'text-blue-600 bg-blue-100';
      case 'MEDIUM':  return 'text-yellow-600 bg-yellow-100';
      case 'HIGH':    return 'text-orange-600 bg-orange-100';
      case 'CRITICAL':return 'text-red-600 bg-red-100';
      default:        return 'text-gray-600 bg-gray-100';
    }
  };

  if (isLoading) {
    return (
      <div className="flex items-center justify-center min-h-[60vh]">
        <div className="text-center">
          <Loader2 className="h-8 w-8 animate-spin text-blue-600 mx-auto" />
          <p className="mt-4 text-sm text-gray-600">Loading watchlist...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="space-y-8">
      {/* Flash animation style */}
      <style>{`
        @keyframes rowFlash {
          0%   { background-color: #d1fae5; }
          100% { background-color: transparent; }
        }
        .row-flash { animation: rowFlash 1.5s ease-out forwards; }
      `}</style>

      {/* Header */}
      <div>
        <h1 className="text-3xl font-bold text-gray-900">Watchlist</h1>
        <p className="mt-2 text-gray-600">
          Track stocks with real-time prices and automatic analysis
        </p>
      </div>

      {/* Error Alert */}
      {error && (
        <div className="bg-red-50 border border-red-200 text-red-800 px-4 py-3 rounded-md flex items-start gap-3">
          <AlertCircle className="h-5 w-5 mt-0.5 flex-shrink-0" />
          <div className="flex-1">
            <p className="text-sm font-medium">Error</p>
            <p className="text-sm mt-1">{error}</p>
          </div>
          <button onClick={() => setError(null)} className="text-red-600 hover:text-red-800">×</button>
        </div>
      )}

      {/* Add Symbol — Autocomplete Search */}
      <div className="bg-white rounded-lg shadow border border-gray-200 p-6">
        <h3 className="text-lg font-semibold text-gray-900 mb-4">Add to Watchlist</h3>
        <div className="flex gap-4 items-start">
          <div className="flex-1 relative" ref={searchRef}>
            <div className="relative">
              <Search className="absolute left-3 top-1/2 -translate-y-1/2 h-5 w-5 text-gray-400 pointer-events-none" />
              <input
                type="text"
                placeholder="Search by company name or NSE symbol (e.g. RELIANCE, TCS)"
                value={searchQuery}
                onChange={(e) => handleSearchInput(e.target.value)}
                onFocus={() => suggestions.length > 0 && setShowDropdown(true)}
                disabled={addingSymbol}
                className="w-full pl-10 pr-10 py-3 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500 disabled:bg-gray-100"
              />
              {searchQuery && !addingSymbol && (
                <button
                  onClick={() => { setSearchQuery(''); setSelectedCompany(null); setSuggestions([]); setShowDropdown(false); }}
                  className="absolute right-3 top-1/2 -translate-y-1/2 text-gray-400 hover:text-gray-600"
                >
                  <X className="h-4 w-4" />
                </button>
              )}
              {searchLoading && (
                <Loader2 className="absolute right-3 top-1/2 -translate-y-1/2 h-4 w-4 animate-spin text-blue-500" />
              )}
            </div>

            {/* Autocomplete Dropdown */}
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
                          <span className="font-semibold text-blue-700 text-sm flex-shrink-0">{code}</span>
                          <span className="text-gray-700 text-sm truncate">{company.name}</span>
                        </div>
                        {company.exchange && (
                          <span className="text-xs text-gray-400 ml-2 flex-shrink-0">{company.exchange}</span>
                        )}
                      </div>
                      {company.bse_code && company.nse_code && (
                        <p className="text-xs text-gray-400 mt-0.5">BSE: {company.bse_code}</p>
                      )}
                    </button>
                  );
                })}
              </div>
            )}

            {showDropdown && suggestions.length === 0 && !searchLoading && searchQuery.length >= 2 && (
              <div className="absolute z-50 w-full mt-1 bg-white border border-gray-200 rounded-lg shadow-lg">
                <div className="px-4 py-3 text-sm text-gray-500 text-center">
                  No companies found for &quot;{searchQuery}&quot;
                </div>
              </div>
            )}
          </div>

          <Button onClick={handleAddSymbol} disabled={addingSymbol || !selectedCompany}>
            {addingSymbol ? (
              <Loader2 className="mr-2 h-4 w-4 animate-spin" />
            ) : (
              <Plus className="mr-2 h-4 w-4" />
            )}
            Add
          </Button>
        </div>

        {selectedCompany && (
          <div className="mt-3 flex items-center gap-2 text-sm text-green-700 bg-green-50 border border-green-200 px-3 py-2 rounded-lg">
            <span className="font-semibold">{selectedCompany.nse_code || selectedCompany.symbol}</span>
            <span>—</span>
            <span>{selectedCompany.name}</span>
            {selectedCompany.exchange && (
              <span className="text-gray-500 ml-auto text-xs">{selectedCompany.exchange}</span>
            )}
          </div>
        )}

        <p className="text-sm text-gray-500 mt-3">
          💡 Start typing a company name or NSE symbol to search, then select and click Add
        </p>
      </div>

      {/* Watchlist Table */}
      <div className="bg-white rounded-lg shadow border border-gray-200 p-6">
        <div className="flex items-center justify-between mb-4">
          <h3 className="text-lg font-semibold text-gray-900">
            Your Watchlist ({watchlist.length})
          </h3>
        </div>

        {watchlist.length === 0 ? (
          <div className="text-center py-12">
            <Eye className="h-12 w-12 text-gray-400 mx-auto mb-3" />
            <p className="text-gray-600 mb-2">Your watchlist is empty</p>
            <p className="text-sm text-gray-500">Add stocks to track their prices and analysis</p>
          </div>
        ) : (
          <div className="overflow-x-auto">
            <table className="w-full">
              <thead>
                <tr className="border-b border-gray-200">
                  <th className="text-left py-3 px-4 text-sm font-medium text-gray-700">Symbol</th>
                  <th className="text-right py-3 px-4 text-sm font-medium text-gray-700">Price</th>
                  <th className="text-right py-3 px-4 text-sm font-medium text-gray-700">Change</th>
                  <th className="text-right py-3 px-4 text-sm font-medium text-gray-700">52Wk High</th>
                  <th className="text-right py-3 px-4 text-sm font-medium text-gray-700">52Wk Low</th>
                  <th className="text-center py-3 px-4 text-sm font-medium text-gray-700">Analysis</th>
                  <th className="text-right py-3 px-4 text-sm font-medium text-gray-700">Actions</th>
                </tr>
              </thead>
              <tbody>
                {watchlist.map((item) => (
                  <tr
                    key={item.watchlist_id}
                    className={`border-b border-gray-100 hover:bg-gray-50 transition-colors ${
                      justScored.has(item.watchlist_id) ? 'row-flash' : ''
                    }`}
                  >
                    <td className="py-3 px-4">
                      <div className="font-medium text-gray-900">{item.symbol}</div>
                      <div className="text-xs text-gray-500">
                        Added {new Date(item.added_date).toLocaleDateString()}
                      </div>
                    </td>
                    <td className="py-3 px-4 text-right text-sm text-gray-900 font-medium">
                      {item.current_price !== null ? `₹${item.current_price.toFixed(2)}` : <span className="text-gray-400">-</span>}
                    </td>
                    <td className="py-3 px-4 text-right">
                      {item.price_change_percent !== null ? (
                        <div className={`flex items-center justify-end gap-1 ${
                          item.price_change_percent >= 0 ? 'text-green-600' : 'text-red-600'
                        }`}>
                          {item.price_change_percent >= 0 ? (
                            <TrendingUp className="h-4 w-4" />
                          ) : (
                            <TrendingDown className="h-4 w-4" />
                          )}
                          <span className="text-sm font-medium">
                            {item.price_change_percent >= 0 ? '+' : ''}{item.price_change_percent.toFixed(2)}%
                          </span>
                        </div>
                      ) : (
                        <span className="text-sm text-gray-400">-</span>
                      )}
                    </td>
                    <td className="py-3 px-4 text-right text-sm text-gray-600">
                      {item.high !== null ? `₹${item.high.toFixed(2)}` : <span className="text-gray-400">-</span>}
                    </td>
                    <td className="py-3 px-4 text-right text-sm text-gray-600">
                      {item.low !== null ? `₹${item.low.toFixed(2)}` : <span className="text-gray-400">-</span>}
                    </td>
                    <td className="py-3 px-4 text-center">
                      {item.current_risk_score ? (
                        <span className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium ${getRiskColor(item.current_risk_level)}`}>
                          {item.current_risk_score} / 100
                        </span>
                      ) : (
                        <span className="inline-flex items-center gap-1 text-xs text-gray-500">
                          <Loader2 className="h-3 w-3 animate-spin" />
                          Analyzing...
                        </span>
                      )}
                    </td>
                    <td className="py-3 px-4 text-right">
                      <div className="flex items-center justify-end gap-2">
                        {item.current_risk_score && item.latest_analysis_id && (
                          <Button
                            variant="ghost"
                            size="sm"
                            onClick={() => router.push(`/report/${item.latest_analysis_id}`)}
                            title="View full analysis report"
                          >
                            <FileText className="h-4 w-4" />
                          </Button>
                        )}
                        <Button
                          variant="ghost"
                          size="sm"
                          onClick={() => handleRemoveSymbol(item.watchlist_id, item.symbol)}
                          className="text-red-600 hover:text-red-700 hover:bg-red-50"
                        >
                          <Trash2 className="h-4 w-4" />
                        </Button>
                      </div>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </div>

      {/* Info */}
      <div className="bg-blue-50 border border-blue-200 rounded-lg p-4">
        <p className="text-sm text-blue-800">
          <strong>Real-time Data:</strong> Prices are fetched live from FinEdge API.
          When you add a new symbol, we automatically trigger analysis if it doesn&apos;t exist yet.
        </p>
      </div>
    </div>
  );
}
