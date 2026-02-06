'use client';

/**
 * Watchlist Page
 *
 * Track companies and receive alerts on risk score changes
 */

import { useState } from 'react';
import { Button } from '@/components/ui/button';
import {
  Bell,
  Plus,
  Trash2,
  TrendingUp,
  TrendingDown,
  AlertTriangle,
  FileText,
  Search,
  CheckCircle2,
  Mail,
  Smartphone,
  Clock,
} from 'lucide-react';
import { WatchlistItem, WatchlistAlert, getAlertSeverityColor, formatScoreChange } from '@/lib/types/watchlist';
import { getRiskColor, getRiskLevel } from '@/lib/types/portfolio';

// Sample watchlist data
const sampleWatchlist: WatchlistItem[] = [
  {
    watchlist_id: 'w1',
    company_id: 'c1',
    symbol: 'RELIANCE',
    company_name: 'Reliance Industries',
    industry: 'Conglomerate',
    sector: 'Diversified',
    current_risk_score: 42,
    current_risk_level: 'MEDIUM',
    previous_risk_score: 38,
    score_change: 4,
    last_analysis_date: '2024-01-15',
    added_date: '2023-12-01',
    alert_enabled: true,
  },
  {
    watchlist_id: 'w2',
    company_id: 'c2',
    symbol: 'ZEEL',
    company_name: 'Zee Entertainment',
    industry: 'Media',
    sector: 'Entertainment',
    current_risk_score: 67,
    current_risk_level: 'CRITICAL',
    previous_risk_score: 58,
    score_change: 9,
    last_analysis_date: '2024-01-10',
    added_date: '2023-11-15',
    alert_enabled: true,
  },
  {
    watchlist_id: 'w3',
    company_id: 'c3',
    symbol: 'HDFCBANK',
    company_name: 'HDFC Bank',
    industry: 'Banking',
    sector: 'Financial Services',
    current_risk_score: 22,
    current_risk_level: 'LOW',
    previous_risk_score: 25,
    score_change: -3,
    last_analysis_date: '2024-01-12',
    added_date: '2023-10-20',
    alert_enabled: true,
  },
];

const sampleAlerts: WatchlistAlert[] = [
  {
    alert_id: 'a1',
    company_id: 'c2',
    symbol: 'ZEEL',
    company_name: 'Zee Entertainment',
    alert_type: 'SCORE_CHANGE',
    severity: 'CRITICAL',
    message: 'Risk score increased by 9 points (58 → 67). Now in CRITICAL range.',
    created_at: '2024-01-10T10:30:00Z',
    is_read: false,
  },
  {
    alert_id: 'a2',
    company_id: 'c1',
    symbol: 'RELIANCE',
    company_name: 'Reliance Industries',
    alert_type: 'NEW_REPORT',
    severity: 'INFO',
    message: 'New annual report available for FY 2023-24.',
    created_at: '2024-01-15T08:00:00Z',
    is_read: false,
  },
  {
    alert_id: 'a3',
    company_id: 'c3',
    symbol: 'HDFCBANK',
    company_name: 'HDFC Bank',
    alert_type: 'SCORE_CHANGE',
    severity: 'INFO',
    message: 'Risk score improved by 3 points (25 → 22). Maintaining LOW risk level.',
    created_at: '2024-01-12T14:20:00Z',
    is_read: true,
  },
];

export default function WatchlistPage() {
  const [subscriptionTier] = useState<'free' | 'pro' | 'premium'>('free'); // TODO: Replace with auth check
  const [watchlist, setWatchlist] = useState<WatchlistItem[]>(sampleWatchlist);
  const [alerts, setAlerts] = useState<WatchlistAlert[]>(sampleAlerts);
  const [showAddModal, setShowAddModal] = useState(false);
  const [searchQuery, setSearchQuery] = useState('');

  const unreadAlertCount = alerts.filter(a => !a.is_read).length;

  const handleRemoveFromWatchlist = (watchlistId: string) => {
    setWatchlist(watchlist.filter(item => item.watchlist_id !== watchlistId));
  };

  const handleMarkAlertRead = (alertId: string) => {
    setAlerts(alerts.map(a => a.alert_id === alertId ? { ...a, is_read: true } : a));
  };

  const getAlertIcon = (alertType: WatchlistAlert['alert_type']) => {
    switch (alertType) {
      case 'SCORE_CHANGE': return TrendingUp;
      case 'NEW_FLAGS': return AlertTriangle;
      case 'NEW_REPORT': return FileText;
      default: return Bell;
    }
  };

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold text-gray-900 flex items-center gap-3">
            <Bell className="h-8 w-8 text-blue-600" />
            Watchlist
          </h1>
          <p className="text-gray-600 mt-2">Track companies and receive alerts on risk changes</p>
        </div>
        <Button onClick={() => setShowAddModal(true)}>
          <Plus className="mr-2 h-5 w-5" />
          Add Company
        </Button>
      </div>

      {/* Alert Preferences Banner */}
      <div className="bg-white rounded-lg shadow border border-gray-200 p-6">
        <div className="flex items-start justify-between">
          <div>
            <h2 className="text-lg font-bold text-gray-900 mb-2">Alert Preferences</h2>
            <div className="flex items-center gap-6 text-sm text-gray-600">
              {subscriptionTier === 'free' && (
                <>
                  <div className="flex items-center gap-2">
                    <Mail className="h-4 w-4 text-gray-400" />
                    <span>Email: Disabled</span>
                  </div>
                  <div className="flex items-center gap-2">
                    <Smartphone className="h-4 w-4 text-gray-400" />
                    <span>Push: Disabled</span>
                  </div>
                  <div className="flex items-center gap-2">
                    <Clock className="h-4 w-4 text-gray-400" />
                    <span>Frequency: None</span>
                  </div>
                </>
              )}
              {subscriptionTier === 'pro' && (
                <>
                  <div className="flex items-center gap-2">
                    <Mail className="h-4 w-4 text-blue-600" />
                    <span>Email: Weekly Digest</span>
                  </div>
                  <div className="flex items-center gap-2">
                    <Smartphone className="h-4 w-4 text-gray-400" />
                    <span>Push: Disabled</span>
                  </div>
                </>
              )}
              {subscriptionTier === 'premium' && (
                <>
                  <div className="flex items-center gap-2">
                    <Mail className="h-4 w-4 text-green-600" />
                    <span>Email: Real-time</span>
                  </div>
                  <div className="flex items-center gap-2">
                    <Smartphone className="h-4 w-4 text-green-600" />
                    <span>Push: Enabled</span>
                  </div>
                </>
              )}
            </div>
          </div>
          {subscriptionTier === 'free' && (
            <Button variant="outline" className="border-blue-600 text-blue-600">
              Upgrade for Alerts
            </Button>
          )}
        </div>
        {subscriptionTier === 'free' && (
          <div className="mt-4 p-4 bg-blue-50 border border-blue-200 rounded-lg">
            <p className="text-sm text-blue-800">
              <strong>Pro:</strong> Weekly email digest • <strong>Premium:</strong> Real-time email + push notifications
            </p>
          </div>
        )}
      </div>

      {/* Recent Alerts */}
      {alerts.length > 0 && (
        <div className="bg-white rounded-lg shadow border border-gray-200 p-6">
          <div className="flex items-center justify-between mb-4">
            <h2 className="text-xl font-bold text-gray-900">
              Recent Alerts
              {unreadAlertCount > 0 && (
                <span className="ml-2 px-2 py-1 text-xs font-bold bg-red-100 text-red-800 rounded-full">
                  {unreadAlertCount} new
                </span>
              )}
            </h2>
          </div>
          <div className="space-y-3">
            {alerts.map((alert) => {
              const IconComponent = getAlertIcon(alert.alert_type);
              const severityColor = getAlertSeverityColor(alert.severity);
              return (
                <div
                  key={alert.alert_id}
                  className={`p-4 border rounded-lg ${alert.is_read ? 'bg-gray-50 border-gray-200' : 'bg-white border-blue-300'}`}
                >
                  <div className="flex items-start gap-3">
                    <IconComponent className="h-5 w-5 mt-0.5" style={{ color: severityColor }} />
                    <div className="flex-1">
                      <div className="flex items-center gap-2 mb-1">
                        <h3 className="font-semibold text-gray-900">{alert.symbol}</h3>
                        <span className="text-sm text-gray-600">{alert.company_name}</span>
                      </div>
                      <p className="text-sm text-gray-700">{alert.message}</p>
                      <p className="text-xs text-gray-500 mt-1">
                        {new Date(alert.created_at).toLocaleString()}
                      </p>
                    </div>
                    {!alert.is_read && (
                      <Button
                        variant="outline"
                        size="sm"
                        onClick={() => handleMarkAlertRead(alert.alert_id)}
                      >
                        Mark Read
                      </Button>
                    )}
                  </div>
                </div>
              );
            })}
          </div>
        </div>
      )}

      {/* Watched Companies */}
      <div className="bg-white rounded-lg shadow border border-gray-200 p-6">
        <h2 className="text-xl font-bold text-gray-900 mb-4">
          Watched Companies ({watchlist.length})
        </h2>
        {watchlist.length === 0 ? (
          <div className="text-center py-12">
            <Bell className="h-16 w-16 text-gray-400 mx-auto mb-4" />
            <h3 className="text-lg font-semibold text-gray-900 mb-2">No companies in watchlist</h3>
            <p className="text-gray-600 mb-6">Add companies to track their risk scores and receive alerts</p>
            <Button onClick={() => setShowAddModal(true)}>
              <Plus className="mr-2 h-5 w-5" />
              Add First Company
            </Button>
          </div>
        ) : (
          <div className="space-y-3">
            {watchlist.map((item) => (
              <div
                key={item.watchlist_id}
                className="p-4 border border-gray-200 rounded-lg hover:bg-gray-50 transition-colors"
              >
                <div className="flex items-center justify-between">
                  <div className="flex items-center gap-4">
                    <div>
                      <div className="flex items-center gap-2 mb-1">
                        <h3 className="font-bold text-gray-900 text-lg">{item.symbol}</h3>
                        <span className="text-sm text-gray-600">{item.company_name}</span>
                      </div>
                      <div className="flex items-center gap-3 text-sm text-gray-600">
                        <span>{item.industry}</span>
                        <span>•</span>
                        <span>{item.sector}</span>
                      </div>
                    </div>
                  </div>

                  <div className="flex items-center gap-6">
                    {/* Risk Score */}
                    <div className="text-center">
                      <div
                        className="text-2xl font-bold"
                        style={{ color: getRiskColor(item.current_risk_score) }}
                      >
                        {item.current_risk_score}
                      </div>
                      <div className="text-xs text-gray-600">Current Risk</div>
                    </div>

                    {/* Score Change */}
                    {item.score_change !== undefined && item.score_change !== 0 && (
                      <div className="text-center">
                        <div className={`flex items-center gap-1 text-sm font-bold ${item.score_change > 0 ? 'text-red-600' : 'text-green-600'}`}>
                          {item.score_change > 0 ? (
                            <TrendingUp className="h-4 w-4" />
                          ) : (
                            <TrendingDown className="h-4 w-4" />
                          )}
                          <span>{formatScoreChange(item.score_change)}</span>
                        </div>
                        <div className="text-xs text-gray-600">Change</div>
                      </div>
                    )}

                    {/* Last Updated */}
                    <div className="text-right">
                      <div className="text-sm text-gray-900">
                        {new Date(item.last_analysis_date).toLocaleDateString()}
                      </div>
                      <div className="text-xs text-gray-600">Last Updated</div>
                    </div>

                    {/* Actions */}
                    <Button
                      variant="outline"
                      size="sm"
                      onClick={() => handleRemoveFromWatchlist(item.watchlist_id)}
                      className="text-red-600 hover:bg-red-50"
                    >
                      <Trash2 className="h-4 w-4" />
                    </Button>
                  </div>
                </div>
              </div>
            ))}
          </div>
        )}
      </div>

      {/* Add Company Modal (Simple version - TODO: Implement full modal) */}
      {showAddModal && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
          <div className="bg-white rounded-lg shadow-xl p-6 max-w-md w-full">
            <h2 className="text-xl font-bold text-gray-900 mb-4">Add Company to Watchlist</h2>
            <div className="mb-4">
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Search Company
              </label>
              <div className="relative">
                <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 h-5 w-5 text-gray-400" />
                <input
                  type="text"
                  placeholder="Enter company name or symbol..."
                  value={searchQuery}
                  onChange={(e) => setSearchQuery(e.target.value)}
                  className="w-full pl-10 pr-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                />
              </div>
            </div>
            <div className="flex gap-3">
              <Button variant="outline" onClick={() => setShowAddModal(false)} className="flex-1">
                Cancel
              </Button>
              <Button onClick={() => setShowAddModal(false)} className="flex-1">
                Add to Watchlist
              </Button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
