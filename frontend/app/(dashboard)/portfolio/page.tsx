'use client';

/**
 * Portfolio Scanner Page (Premium Feature)
 *
 * Upload broker CSV and analyze entire portfolio risk.
 * Also supports manually adding / removing individual holdings.
 */

import { useState, useEffect, useRef, useCallback } from 'react';
import { useRouter } from 'next/navigation';
import { Button } from '@/components/ui/button';
import {
  Upload,
  FileSpreadsheet,
  AlertTriangle,
  TrendingUp,
  Crown,
  CheckCircle2,
  XCircle,
  Loader2,
  FileText,
  Plus,
  Trash2,
  Search,
  X,
  AlertCircle,
} from 'lucide-react';
import { Holding, Portfolio, getRiskColor, getRiskLevel } from '@/lib/types/portfolio';
import { api } from '@/lib/api/client';
import { User } from '@/lib/types/api';

// ─── Types ───────────────────────────────────────────────────────────────────

// Shape returned by /companies/finedge/search
interface CompanySearchResult {
  symbol: string;
  name: string;
  nse_code: string;
  bse_code: string;
  exchange: string;
  isin: string;
}

// ─── Helpers ─────────────────────────────────────────────────────────────────

function parseApiError(err: any, fallback: string): string {
  const detail = err?.response?.data?.detail;
  if (!detail) return fallback;
  if (Array.isArray(detail)) return detail.map((d: any) => d?.msg || JSON.stringify(d)).join(', ');
  if (typeof detail === 'string') return detail;
  return fallback;
}

// ─── Component ───────────────────────────────────────────────────────────────

export default function PortfolioPage() {
  const router = useRouter();

  // User
  const [currentUser, setCurrentUser] = useState<User | null>(null);

  // Portfolio state
  const [portfolios, setPortfolios] = useState<Portfolio[]>([]);
  const [currentPortfolio, setCurrentPortfolio] = useState<Portfolio | null>(null);

  // Loading states — isLoading only blocks on first mount, never during polling
  const [isLoading, setIsLoading] = useState(false);
  const [isUploading, setIsUploading] = useState(false);
  const [uploadError, setUploadError] = useState<string | null>(null);
  const [globalError, setGlobalError] = useState<string | null>(null);

  // Silent polling — tracks which holding_ids just received their score
  const [justScored, setJustScored] = useState<Set<string>>(new Set());
  const pollingRef = useRef<ReturnType<typeof setInterval> | null>(null);

  // File input ref
  const fileInputRef = useRef<HTMLInputElement>(null);

  // ── Add-stock panel ──
  const [showAddPanel, setShowAddPanel] = useState(false);
  const [addSearchQuery, setAddSearchQuery] = useState('');
  const [addSuggestions, setAddSuggestions] = useState<CompanySearchResult[]>([]);
  const [addSearchLoading, setAddSearchLoading] = useState(false);
  const [addShowDropdown, setAddShowDropdown] = useState(false);
  const [addSelectedCompany, setAddSelectedCompany] = useState<CompanySearchResult | null>(null);
  const [addQty, setAddQty] = useState('');
  const [addAvgPrice, setAddAvgPrice] = useState('');
  const [isAddingHolding, setIsAddingHolding] = useState(false);
  const [addError, setAddError] = useState<string | null>(null);
  const addSearchRef = useRef<HTMLDivElement>(null);
  const addDebounceRef = useRef<ReturnType<typeof setTimeout> | null>(null);

  // ── Inline remove confirm — maps holding_id → true when awaiting confirm ──
  const [pendingRemove, setPendingRemove] = useState<Record<string, boolean>>({});
  const [removingId, setRemovingId] = useState<string | null>(null);

  // ─── Init ───────────────────────────────────────────────────────────────────

  useEffect(() => {
    const userStr = localStorage.getItem('user');
    if (userStr) { try { setCurrentUser(JSON.parse(userStr)); } catch {} }
    fetchPortfolios(true);
    return () => { if (pollingRef.current) clearInterval(pollingRef.current); };
  }, []);

  // Start / stop silent background polling whenever currentPortfolio changes
  useEffect(() => {
    const hasPending = currentPortfolio?.holdings?.some(
      h => h.risk_score === null || h.risk_score === undefined
    );
    if (hasPending) {
      if (!pollingRef.current) {
        pollingRef.current = setInterval(() => fetchPortfolios(false), 10000);
      }
    } else {
      if (pollingRef.current) { clearInterval(pollingRef.current); pollingRef.current = null; }
    }
  }, [currentPortfolio]);

  // Close add-stock dropdown when clicking outside
  useEffect(() => {
    const handler = (e: MouseEvent) => {
      if (addSearchRef.current && !addSearchRef.current.contains(e.target as Node)) {
        setAddShowDropdown(false);
      }
    };
    document.addEventListener('mousedown', handler);
    return () => document.removeEventListener('mousedown', handler);
  }, []);

  // ─── Auth ───────────────────────────────────────────────────────────────────

  const isPremiumUser = currentUser?.is_admin || currentUser?.subscription_tier === 'premium';

  // ─── Fetch portfolios ───────────────────────────────────────────────────────

  /**
   * @param showSpinner – true only on the very first load
   */
  const fetchPortfolios = async (showSpinner: boolean) => {
    try {
      if (showSpinner) setIsLoading(true);

      const response = await api.get<{ portfolios: Portfolio[]; total: number }>('/portfolio/');
      const portfolioList: Portfolio[] = response.data.portfolios || [];

      setPortfolios(portfolioList);

      // Update currentPortfolio in-place: detect newly scored holdings for flash
      setCurrentPortfolio(prev => {
        const first = portfolioList[0] ?? null;
        if (!first) return null;

        // Match by portfolio_id if already viewing one
        const updated = prev
          ? portfolioList.find(p => p.portfolio_id === prev.portfolio_id) ?? first
          : first;

        // Detect which holding_ids just got their first score
        if (prev) {
          const newlyScored = new Set<string>();
          updated.holdings.forEach(newH => {
            const old = prev.holdings.find(o => o.holding_id === newH.holding_id);
            if (old && !old.risk_score && newH.risk_score) {
              newlyScored.add(newH.holding_id);
            }
          });
          if (newlyScored.size > 0) {
            setJustScored(s => { const n = new Set(s); newlyScored.forEach(id => n.add(id)); return n; });
            setTimeout(() => {
              setJustScored(s => { const n = new Set(s); newlyScored.forEach(id => n.delete(id)); return n; });
            }, 1500);
          }
        }

        return updated;
      });
    } catch (err: any) {
      if (showSpinner) setGlobalError(parseApiError(err, 'Failed to load portfolios'));
    } finally {
      if (showSpinner) setIsLoading(false);
    }
  };

  // ─── CSV Upload ─────────────────────────────────────────────────────────────

  const handleFileUpload = async (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (!file) return;
    setIsUploading(true);
    setUploadError(null);
    try {
      const response = await api.upload<{
        portfolio_id: string;
        total_holdings: number;
        matched_companies: number;
        unmatched_symbols: string[];
        total_investment: number;
      }>('/portfolio/upload', file, {
        portfolio_name: `Portfolio ${new Date().toLocaleDateString()}`,
      });
      if (response.data.unmatched_symbols?.length > 0) {
        setUploadError(
          `Warning: ${response.data.unmatched_symbols.length} symbol(s) could not be matched: ${response.data.unmatched_symbols.join(', ')}`
        );
      }
      await fetchPortfolios(false);
    } catch (err: any) {
      setUploadError(parseApiError(err, 'Failed to upload portfolio. Please try again.'));
    } finally {
      setIsUploading(false);
    }
  };

  // ─── Add-stock search ───────────────────────────────────────────────────────

  const handleAddSearchInput = useCallback((value: string) => {
    setAddSearchQuery(value);
    setAddSelectedCompany(null);
    if (addDebounceRef.current) clearTimeout(addDebounceRef.current);
    if (!value.trim()) { setAddSuggestions([]); setAddShowDropdown(false); return; }
    addDebounceRef.current = setTimeout(async () => {
      try {
        setAddSearchLoading(true);
        // FinEdge search — all NSE/BSE companies (same source as Analyze & Watchlist)
        const res = await api.get(`/companies/finedge/search?q=${encodeURIComponent(value)}&limit=10`);
        const results: CompanySearchResult[] = res.data.results || [];
        setAddSuggestions(results);
        setAddShowDropdown(results.length > 0);
      } catch {
        setAddSuggestions([]); setAddShowDropdown(false);
      } finally {
        setAddSearchLoading(false);
      }
    }, 300);
  }, []);

  const handleAddSelectCompany = (c: CompanySearchResult) => {
    setAddSelectedCompany(c);
    const code = c.nse_code || c.symbol;
    setAddSearchQuery(`${code} — ${c.name}`);
    setAddShowDropdown(false);
    setAddSuggestions([]);
  };

  const handleAddHolding = async () => {
    if (!addSelectedCompany || !currentPortfolio) return;
    const qty = parseInt(addQty, 10);
    const price = parseFloat(addAvgPrice);
    if (!qty || qty <= 0 || !price || price <= 0) {
      setAddError('Please enter valid quantity and average price.');
      return;
    }
    setIsAddingHolding(true);
    setAddError(null);
    try {
      const symbol = addSelectedCompany.nse_code || addSelectedCompany.symbol;

      // Step 1: Ensure company exists in local DB (creates it if new) — returns UUID
      const ensureRes = await api.post('/companies/ensure-by-symbol', {
        symbol,
        name: addSelectedCompany.name,
      });
      const companyId = ensureRes.data.company_id;

      // Step 2: Add holding using the UUID (existing flow — unchanged)
      await api.post(`/portfolio/${currentPortfolio.portfolio_id}/holdings`, {
        company_id: companyId,
        symbol,
        quantity: qty,
        avg_price: price,
      });

      // Reset panel
      setAddSearchQuery('');
      setAddSelectedCompany(null);
      setAddSuggestions([]);
      setAddQty('');
      setAddAvgPrice('');
      setShowAddPanel(false);
      await fetchPortfolios(false);
    } catch (err: any) {
      setAddError(parseApiError(err, 'Failed to add stock.'));
    } finally {
      setIsAddingHolding(false);
    }
  };

  // ─── Remove holding ─────────────────────────────────────────────────────────

  const requestRemove = (holdingId: string) => {
    setPendingRemove(prev => ({ ...prev, [holdingId]: true }));
  };

  const cancelRemove = (holdingId: string) => {
    setPendingRemove(prev => { const n = { ...prev }; delete n[holdingId]; return n; });
  };

  const confirmRemove = async (holdingId: string) => {
    if (!currentPortfolio) return;
    setRemovingId(holdingId);
    try {
      await api.delete(`/portfolio/${currentPortfolio.portfolio_id}/holdings/${holdingId}`);
      // Optimistically remove the row from state
      setCurrentPortfolio(prev => {
        if (!prev) return prev;
        const updated = { ...prev, holdings: prev.holdings.filter(h => h.holding_id !== holdingId) };
        return updated;
      });
    } catch (err: any) {
      setGlobalError(parseApiError(err, 'Failed to remove holding.'));
    } finally {
      setRemovingId(null);
      setPendingRemove(prev => { const n = { ...prev }; delete n[holdingId]; return n; });
    }
  };

  // ─── Derived values ─────────────────────────────────────────────────────────

  const holdings = currentPortfolio?.holdings || [];
  const totalInvestment = currentPortfolio?.total_investment || 0;
  const totalCurrentValue = holdings.reduce((s, h) => s + (h.current_value || h.investment_value), 0);
  const totalPnL = totalCurrentValue - totalInvestment;
  const totalPnLPercent = totalInvestment > 0 ? (totalPnL / totalInvestment) * 100 : 0;
  const avgRisk = currentPortfolio?.average_risk_score || 0;
  const highRiskCount = currentPortfolio?.high_risk_count || 0;

  // ─── Premium gate ───────────────────────────────────────────────────────────

  if (!isPremiumUser && !isLoading) {
    return (
      <div className="space-y-6">
        <div className="bg-gradient-to-br from-purple-600 to-blue-600 rounded-lg p-8 text-white">
          <div className="flex items-center gap-3 mb-4">
            <Crown className="h-10 w-10 text-yellow-300" />
            <h1 className="text-3xl font-bold">Portfolio Scanner</h1>
          </div>
          <p className="text-lg text-blue-100 mb-6">
            Analyze your entire portfolio at once. Upload your broker CSV and get instant risk assessment.
          </p>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4 mb-6">
            <div className="bg-white/20 p-4 rounded-lg">
              <FileSpreadsheet className="h-6 w-6 mb-2" />
              <h3 className="font-semibold mb-1">Multi-Broker Support</h3>
              <p className="text-sm text-blue-100">Zerodha, Groww, Upstox formats</p>
            </div>
            <div className="bg-white/20 p-4 rounded-lg">
              <TrendingUp className="h-6 w-6 mb-2" />
              <h3 className="font-semibold mb-1">Risk Heatmap</h3>
              <p className="text-sm text-blue-100">Visual portfolio risk overview</p>
            </div>
          </div>
          <Button size="lg" className="bg-yellow-400 text-gray-900 hover:bg-yellow-300">
            <Crown className="mr-2 h-5 w-5" />
            Upgrade to Premium - ₹1,999/month
          </Button>
        </div>
      </div>
    );
  }

  // ─── Render ─────────────────────────────────────────────────────────────────

  return (
    <div className="space-y-6">
      {/* Flash animation */}
      <style>{`
        @keyframes rowFlash {
          0%   { background-color: #d1fae5; }
          100% { background-color: transparent; }
        }
        .row-flash { animation: rowFlash 1.5s ease-out forwards; }
      `}</style>

      {/* Page header */}
      <div>
        <h1 className="text-3xl font-bold text-gray-900 flex items-center gap-3">
          <FileSpreadsheet className="h-8 w-8 text-blue-600" />
          Portfolio Scanner
          <Crown className="h-6 w-6 text-yellow-500" />
        </h1>
        <p className="text-gray-600 mt-2">Upload your broker CSV or manually add stocks to analyse portfolio risk</p>
      </div>

      {/* Global error */}
      {globalError && (
        <div className="bg-red-50 border border-red-200 text-red-800 px-4 py-3 rounded-md flex items-start gap-3">
          <AlertCircle className="h-5 w-5 mt-0.5 flex-shrink-0" />
          <div className="flex-1"><p className="text-sm">{globalError}</p></div>
          <button onClick={() => setGlobalError(null)} className="text-red-600 hover:text-red-800">×</button>
        </div>
      )}

      {/* Initial spinner */}
      {isLoading ? (
        <div className="flex items-center justify-center py-12">
          <Loader2 className="h-8 w-8 animate-spin text-blue-600" />
          <span className="ml-3 text-gray-600">Loading portfolios...</span>
        </div>
      ) : !currentPortfolio ? (
        /* ── CSV Upload panel (shown when no portfolio exists) ── */
        <div className="bg-white rounded-lg shadow border border-gray-200 p-8">
          <div className="max-w-2xl mx-auto text-center">
            <Upload className="h-16 w-16 text-gray-400 mx-auto mb-4" />
            <h2 className="text-xl font-bold text-gray-900 mb-2">Upload Portfolio CSV</h2>
            <p className="text-gray-600 mb-6">
              Supported formats: Zerodha, Groww, Upstox, or generic CSV with Symbol, Quantity, Avg Price
            </p>

            {uploadError && (
              <div className={`mb-4 p-4 rounded-lg text-sm ${
                uploadError.startsWith('Warning')
                  ? 'bg-yellow-50 border border-yellow-200 text-yellow-800'
                  : 'bg-red-50 border border-red-200 text-red-800'
              }`}>
                {uploadError}
              </div>
            )}

            <input
              ref={fileInputRef}
              type="file"
              accept=".csv"
              onChange={handleFileUpload}
              className="hidden"
              disabled={isUploading}
            />
            <Button disabled={isUploading} onClick={() => fileInputRef.current?.click()}>
              {isUploading ? (
                <><Loader2 className="mr-2 h-4 w-4 animate-spin" />Uploading & Analyzing...</>
              ) : (
                <><Upload className="mr-2 h-4 w-4" />Choose CSV File</>
              )}
            </Button>

            <div className="mt-8 text-left bg-gray-50 p-4 rounded-lg">
              <h3 className="font-semibold text-gray-900 mb-2">CSV Format Example:</h3>
              <pre className="text-xs text-gray-600 overflow-x-auto">{`Symbol,Quantity,Avg Price\nHDFCBANK,50,1500\nINFY,100,1400\nTCS,80,3200`}</pre>
            </div>
          </div>
        </div>
      ) : null}

      {/* ── Portfolio content (shown when portfolio exists) ── */}
      {currentPortfolio && (
        <>
          {/* Summary cards */}
          <div className="grid grid-cols-1 md:grid-cols-5 gap-4">
            {[
              { label: 'Total Holdings',    value: holdings.length,                                 cls: 'text-gray-900' },
              { label: 'Total Investment',  value: `₹${(totalInvestment/100000).toFixed(2)}L`,     cls: 'text-gray-900' },
              { label: 'Current Value',     value: `₹${(totalCurrentValue/100000).toFixed(2)}L`,  cls: 'text-gray-900' },
              {
                label: 'Total P&L',
                value: `${totalPnL >= 0 ? '+' : ''}₹${(totalPnL/1000).toFixed(1)}k (${totalPnLPercent >= 0 ? '+' : ''}${totalPnLPercent.toFixed(1)}%)`,
                cls: totalPnL >= 0 ? 'text-green-600' : 'text-red-600',
              },
              { label: 'High Risk Stocks',  value: highRiskCount,                                   cls: 'text-red-600' },
            ].map(card => (
              <div key={card.label} className="bg-white rounded-lg shadow border border-gray-200 p-4">
                <div className="text-sm text-gray-600">{card.label}</div>
                <div className={`text-2xl font-bold ${card.cls}`}>{card.value}</div>
              </div>
            ))}
          </div>

          {/* Risk Heatmap */}
          <div className="bg-white rounded-lg shadow border border-gray-200 p-6">
            <h2 className="text-xl font-bold text-gray-900 mb-4">Risk Heatmap</h2>
            <div className="grid grid-cols-2 md:grid-cols-4 gap-3">
              {holdings.map((holding) => (
                <div
                  key={holding.holding_id}
                  className={`p-4 rounded-lg border-2 transition-transform hover:scale-105 cursor-pointer ${
                    justScored.has(holding.holding_id) ? 'row-flash' : ''
                  }`}
                  style={{
                    backgroundColor: `${getRiskColor(holding.risk_score)}20`,
                    borderColor: getRiskColor(holding.risk_score),
                  }}
                >
                  <div className="font-bold text-gray-900">{holding.symbol}</div>
                  <div className="text-2xl font-bold mt-1" style={{ color: getRiskColor(holding.risk_score) }}>
                    {holding.risk_score ?? (
                      <span className="inline-flex items-center gap-1 text-sm text-gray-400">
                        <Loader2 className="h-4 w-4 animate-spin" />
                      </span>
                    )}
                  </div>
                  <div className="text-xs text-gray-600 mt-1">{holding.flags_count || 0} flags</div>
                  {holding.pnl_percent !== undefined && (
                    <div className={`text-xs font-semibold mt-1 ${holding.pnl_percent >= 0 ? 'text-green-600' : 'text-red-600'}`}>
                      {holding.pnl_percent >= 0 ? '+' : ''}{holding.pnl_percent.toFixed(1)}%
                    </div>
                  )}
                </div>
              ))}
            </div>
          </div>

          {/* Holdings Table */}
          <div className="bg-white rounded-lg shadow border border-gray-200 p-6">
            <div className="flex items-center justify-between mb-4">
              <h2 className="text-xl font-bold text-gray-900">Detailed Holdings</h2>
              <Button
                size="sm"
                variant="outline"
                onClick={() => { setShowAddPanel(v => !v); setAddError(null); }}
                className="flex items-center gap-1.5"
              >
                {showAddPanel ? <X className="h-4 w-4" /> : <Plus className="h-4 w-4" />}
                {showAddPanel ? 'Cancel' : 'Add Stock'}
              </Button>
            </div>

            {/* ── Add-stock inline panel ── */}
            {showAddPanel && (
              <div className="mb-6 p-4 bg-blue-50 border border-blue-200 rounded-lg">
                <h3 className="text-sm font-semibold text-blue-900 mb-3">Add a stock to this portfolio</h3>

                {addError && (
                  <div className="mb-3 text-xs text-red-700 bg-red-50 border border-red-200 px-3 py-2 rounded">
                    {addError}
                  </div>
                )}

                <div className="flex flex-wrap gap-3 items-end">
                  {/* Company search */}
                  <div className="flex-1 min-w-[200px] relative" ref={addSearchRef}>
                    <label className="block text-xs font-medium text-gray-700 mb-1">Company</label>
                    <div className="relative">
                      <Search className="absolute left-2.5 top-1/2 -translate-y-1/2 h-4 w-4 text-gray-400 pointer-events-none" />
                      <input
                        type="text"
                        placeholder="Search symbol or name…"
                        value={addSearchQuery}
                        onChange={e => handleAddSearchInput(e.target.value)}
                        onFocus={() => addSuggestions.length > 0 && setAddShowDropdown(true)}
                        disabled={isAddingHolding}
                        className="w-full pl-8 pr-8 py-2 text-sm border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                      />
                      {addSearchQuery && !isAddingHolding && (
                        <button
                          onClick={() => { setAddSearchQuery(''); setAddSelectedCompany(null); setAddSuggestions([]); setAddShowDropdown(false); }}
                          className="absolute right-2 top-1/2 -translate-y-1/2 text-gray-400 hover:text-gray-600"
                        ><X className="h-3.5 w-3.5" /></button>
                      )}
                      {addSearchLoading && (
                        <Loader2 className="absolute right-2 top-1/2 -translate-y-1/2 h-3.5 w-3.5 animate-spin text-blue-500" />
                      )}
                    </div>

                    {/* Dropdown */}
                    {addShowDropdown && addSuggestions.length > 0 && (
                      <div className="absolute z-50 w-full mt-1 bg-white border border-gray-200 rounded-lg shadow-lg max-h-56 overflow-y-auto">
                        {addSuggestions.map((c, idx) => {
                          const code = c.nse_code || c.symbol;
                          return (
                            <button
                              key={`${c.symbol}-${idx}`}
                              onClick={() => handleAddSelectCompany(c)}
                              className="w-full text-left px-3 py-2.5 hover:bg-blue-50 border-b border-gray-100 last:border-0 transition-colors"
                            >
                              <span className="font-semibold text-blue-700 text-sm">{code}</span>
                              <span className="text-gray-600 text-xs ml-2">{c.name}</span>
                              {c.exchange && <span className="text-gray-400 text-xs ml-2">· {c.exchange}</span>}
                            </button>
                          );
                        })}
                      </div>
                    )}
                    {addShowDropdown && addSuggestions.length === 0 && !addSearchLoading && addSearchQuery.length >= 2 && (
                      <div className="absolute z-50 w-full mt-1 bg-white border border-gray-200 rounded-lg shadow-lg px-3 py-2 text-sm text-gray-500">
                        No companies found
                      </div>
                    )}
                  </div>

                  {/* Quantity */}
                  <div className="w-28">
                    <label className="block text-xs font-medium text-gray-700 mb-1">Quantity *</label>
                    <input
                      type="number"
                      min={1}
                      placeholder="e.g. 50"
                      value={addQty}
                      onChange={e => setAddQty(e.target.value)}
                      disabled={isAddingHolding}
                      className="w-full px-3 py-2 text-sm border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                    />
                  </div>

                  {/* Avg Price */}
                  <div className="w-36">
                    <label className="block text-xs font-medium text-gray-700 mb-1">Avg Price (₹) *</label>
                    <input
                      type="number"
                      min={0.01}
                      step={0.01}
                      placeholder="e.g. 1500.00"
                      value={addAvgPrice}
                      onChange={e => setAddAvgPrice(e.target.value)}
                      disabled={isAddingHolding}
                      className="w-full px-3 py-2 text-sm border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                    />
                  </div>

                  {/* Add button */}
                  <Button
                    size="sm"
                    onClick={handleAddHolding}
                    disabled={isAddingHolding || !addSelectedCompany || !addQty || !addAvgPrice}
                  >
                    {isAddingHolding
                      ? <><Loader2 className="mr-1.5 h-3.5 w-3.5 animate-spin" />Adding…</>
                      : <><Plus className="mr-1.5 h-3.5 w-3.5" />Add</>
                    }
                  </Button>
                </div>

                {addSelectedCompany && (
                  <p className="mt-2 text-xs text-blue-700">
                    Selected: <strong>{addSelectedCompany.nse_code || addSelectedCompany.symbol}</strong> — {addSelectedCompany.name}
                  </p>
                )}
              </div>
            )}

            {/* Table */}
            <div className="overflow-x-auto">
              <table className="w-full">
                <thead>
                  <tr className="border-b border-gray-200">
                    <th className="text-left py-3 px-4 text-sm font-semibold text-gray-900">Symbol</th>
                    <th className="text-left py-3 px-4 text-sm font-semibold text-gray-900">Company</th>
                    <th className="text-right py-3 px-4 text-sm font-semibold text-gray-900">Qty</th>
                    <th className="text-right py-3 px-4 text-sm font-semibold text-gray-900">Avg Price</th>
                    <th className="text-right py-3 px-4 text-sm font-semibold text-gray-900">Current Price</th>
                    <th className="text-right py-3 px-4 text-sm font-semibold text-gray-900">Investment</th>
                    <th className="text-right py-3 px-4 text-sm font-semibold text-gray-900">Current Value</th>
                    <th className="text-right py-3 px-4 text-sm font-semibold text-gray-900">P&L</th>
                    <th className="text-center py-3 px-4 text-sm font-semibold text-gray-900">Risk</th>
                    <th className="text-center py-3 px-4 text-sm font-semibold text-gray-900">Status</th>
                    <th className="text-center py-3 px-4 text-sm font-semibold text-gray-900">Report</th>
                    <th className="text-center py-3 px-4 text-sm font-semibold text-gray-900">Remove</th>
                  </tr>
                </thead>
                <tbody>
                  {holdings.map((holding) => {
                    const isFlashing  = justScored.has(holding.holding_id);
                    const awaitingConfirm = !!pendingRemove[holding.holding_id];
                    const isRemoving  = removingId === holding.holding_id;

                    return (
                      <tr
                        key={holding.holding_id}
                        className={`border-b border-gray-100 hover:bg-gray-50 transition-colors ${isFlashing ? 'row-flash' : ''}`}
                      >
                        <td className="py-3 px-4 font-semibold text-gray-900">{holding.symbol}</td>
                        <td className="py-3 px-4 text-gray-700 max-w-[180px] truncate">{holding.company_name}</td>
                        <td className="py-3 px-4 text-right text-gray-700">{holding.quantity}</td>
                        <td className="py-3 px-4 text-right text-gray-700">₹{holding.avg_price.toFixed(2)}</td>
                        <td className="py-3 px-4 text-right text-gray-700">
                          {holding.current_price ? (
                            <div>
                              <div>₹{holding.current_price.toFixed(2)}</div>
                              {holding.price_change_percent !== undefined && (
                                <div className={`text-xs ${holding.price_change_percent >= 0 ? 'text-green-600' : 'text-red-600'}`}>
                                  {holding.price_change_percent >= 0 ? '+' : ''}{holding.price_change_percent.toFixed(2)}%
                                </div>
                              )}
                            </div>
                          ) : <span className="text-gray-400">N/A</span>}
                        </td>
                        <td className="py-3 px-4 text-right text-gray-700">₹{(holding.investment_value/1000).toFixed(1)}k</td>
                        <td className="py-3 px-4 text-right text-gray-700">
                          {holding.current_value ? `₹${(holding.current_value/1000).toFixed(1)}k` : <span className="text-gray-400">N/A</span>}
                        </td>
                        <td className="py-3 px-4 text-right">
                          {holding.pnl !== undefined && holding.pnl_percent !== undefined ? (
                            <div className={`font-semibold ${holding.pnl >= 0 ? 'text-green-600' : 'text-red-600'}`}>
                              <div>{holding.pnl >= 0 ? '+' : ''}₹{(holding.pnl/1000).toFixed(1)}k</div>
                              <div className="text-xs">({holding.pnl_percent >= 0 ? '+' : ''}{holding.pnl_percent.toFixed(1)}%)</div>
                            </div>
                          ) : <span className="text-gray-400">N/A</span>}
                        </td>
                        <td className="py-3 px-4 text-center">
                          {holding.risk_score ? (
                            <span
                              className="px-3 py-1 rounded-full text-sm font-bold"
                              style={{
                                backgroundColor: `${getRiskColor(holding.risk_score)}20`,
                                color: getRiskColor(holding.risk_score),
                              }}
                            >
                              {holding.risk_score}
                            </span>
                          ) : (
                            <span className="inline-flex items-center gap-1 text-xs text-gray-500">
                              <Loader2 className="h-3 w-3 animate-spin" />
                              Analyzing...
                            </span>
                          )}
                        </td>
                        <td className="py-3 px-4 text-center">
                          {(holding.risk_score || 0) >= 60 ? (
                            <XCircle className="h-5 w-5 text-red-500 mx-auto" />
                          ) : (
                            <CheckCircle2 className="h-5 w-5 text-green-500 mx-auto" />
                          )}
                        </td>
                        <td className="py-3 px-4 text-center">
                          {holding.latest_analysis_id ? (
                            <Button
                              variant="ghost"
                              size="sm"
                              onClick={() => router.push(`/report/${holding.latest_analysis_id}`)}
                              title="View full analysis report"
                              className="text-blue-600 hover:text-blue-800 hover:bg-blue-50"
                            >
                              <FileText className="h-4 w-4" />
                            </Button>
                          ) : <span className="text-gray-300 text-xs">—</span>}
                        </td>
                        <td className="py-3 px-4 text-center">
                          {isRemoving ? (
                            <Loader2 className="h-4 w-4 animate-spin text-gray-400 mx-auto" />
                          ) : awaitingConfirm ? (
                            /* Inline confirm */
                            <div className="flex items-center justify-center gap-1.5 text-xs">
                              <span className="text-gray-600 whitespace-nowrap">Sure?</span>
                              <button
                                onClick={() => confirmRemove(holding.holding_id)}
                                className="px-2 py-0.5 bg-red-500 text-white rounded hover:bg-red-600 font-medium transition-colors"
                              >Yes</button>
                              <button
                                onClick={() => cancelRemove(holding.holding_id)}
                                className="px-2 py-0.5 bg-gray-200 text-gray-700 rounded hover:bg-gray-300 font-medium transition-colors"
                              >No</button>
                            </div>
                          ) : (
                            <Button
                              variant="ghost"
                              size="sm"
                              onClick={() => requestRemove(holding.holding_id)}
                              className="text-red-500 hover:text-red-700 hover:bg-red-50 mx-auto"
                              title="Remove from portfolio"
                            >
                              <Trash2 className="h-4 w-4" />
                            </Button>
                          )}
                        </td>
                      </tr>
                    );
                  })}
                </tbody>
              </table>
            </div>
          </div>

          {/* High-risk alert */}
          {highRiskCount > 0 && (
            <div className="bg-red-50 border border-red-200 rounded-lg p-6">
              <div className="flex items-start gap-3">
                <AlertTriangle className="h-6 w-6 text-red-600 flex-shrink-0 mt-1" />
                <div>
                  <h3 className="font-bold text-red-900 mb-2">High Risk Alert</h3>
                  <p className="text-sm text-red-800">
                    {highRiskCount} stock{highRiskCount > 1 ? 's' : ''} in your portfolio {highRiskCount > 1 ? 'have' : 'has'} high risk scores (≥60).
                    Consider reviewing detailed reports and taking appropriate action.
                  </p>
                </div>
              </div>
            </div>
          )}

          {/* Portfolio actions */}
          <div className="flex flex-wrap gap-4 items-center">
            <Button
              variant="outline"
              onClick={() => fileInputRef.current?.click()}
              disabled={isUploading}
            >
              {isUploading
                ? <><Loader2 className="mr-2 h-4 w-4 animate-spin" />Uploading…</>
                : <><Upload className="mr-2 h-4 w-4" />Re-upload CSV</>
              }
            </Button>
            <input
              ref={fileInputRef}
              type="file"
              accept=".csv"
              onChange={handleFileUpload}
              className="hidden"
              disabled={isUploading}
            />

            {portfolios.length > 1 && (
              <select
                className="px-4 py-2 border border-gray-300 rounded-lg text-sm"
                value={currentPortfolio.portfolio_id}
                onChange={e => {
                  const sel = portfolios.find(p => p.portfolio_id === e.target.value);
                  if (sel) setCurrentPortfolio(sel);
                }}
              >
                {portfolios.map(p => (
                  <option key={p.portfolio_id} value={p.portfolio_id}>
                    {p.name} — {new Date(p.created_at).toLocaleDateString()}
                  </option>
                ))}
              </select>
            )}
          </div>
        </>
      )}
    </div>
  );
}
