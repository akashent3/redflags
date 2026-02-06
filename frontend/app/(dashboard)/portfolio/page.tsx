'use client';

/**
 * Portfolio Scanner Page (Premium Feature)
 *
 * Upload broker CSV and analyze entire portfolio risk
 */

import { useState } from 'react';
import { Button } from '@/components/ui/button';
import {
  Upload,
  FileSpreadsheet,
  AlertTriangle,
  TrendingUp,
  Crown,
  CheckCircle2,
  XCircle,
} from 'lucide-react';
import { Holding, Portfolio, getRiskColor, getRiskLevel } from '@/lib/types/portfolio';

// Sample portfolio data
const samplePortfolio: Holding[] = [
  { symbol: 'HDFCBANK', company_name: 'HDFC Bank', quantity: 50, avg_price: 1500, investment_value: 75000, risk_score: 22, flags_count: 1 },
  { symbol: 'INFY', company_name: 'Infosys', quantity: 100, avg_price: 1400, investment_value: 140000, risk_score: 18, flags_count: 0 },
  { symbol: 'TCS', company_name: 'TCS', quantity: 80, avg_price: 3200, investment_value: 256000, risk_score: 25, flags_count: 2 },
  { symbol: 'RELIANCE', company_name: 'Reliance Industries', quantity: 30, avg_price: 2400, investment_value: 72000, risk_score: 42, flags_count: 8 },
  { symbol: 'ICICIBANK', company_name: 'ICICI Bank', quantity: 60, avg_price: 900, investment_value: 54000, risk_score: 24, flags_count: 2 },
  { symbol: 'AXISBANK', company_name: 'Axis Bank', quantity: 70, avg_price: 800, investment_value: 56000, risk_score: 35, flags_count: 4 },
  { symbol: 'SBIN', company_name: 'SBI', quantity: 90, avg_price: 550, investment_value: 49500, risk_score: 21, flags_count: 1 },
  { symbol: 'ZEEL', company_name: 'Zee Entertainment', quantity: 40, avg_price: 250, investment_value: 10000, risk_score: 67, flags_count: 12 },
];

export default function PortfolioPage() {
  const [isPremiumUser] = useState(false); // TODO: Replace with auth check
  const [isUploading, setIsUploading] = useState(false);
  const [portfolio, setPortfolio] = useState<Holding[] | null>(null);

  const handleFileUpload = (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (!file) return;

    setIsUploading(true);
    // Simulate upload and analysis
    setTimeout(() => {
      setPortfolio(samplePortfolio);
      setIsUploading(false);
    }, 2000);
  };

  const totalInvestment = portfolio?.reduce((sum, h) => sum + h.investment_value, 0) || 0;
  const avgRisk = portfolio?.reduce((sum, h) => sum + (h.risk_score || 0), 0) / (portfolio?.length || 1) || 0;
  const highRiskCount = portfolio?.filter(h => (h.risk_score || 0) >= 60).length || 0;

  if (!isPremiumUser) {
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

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-3xl font-bold text-gray-900 flex items-center gap-3">
          <FileSpreadsheet className="h-8 w-8 text-blue-600" />
          Portfolio Scanner
          <Crown className="h-6 w-6 text-yellow-500" />
        </h1>
        <p className="text-gray-600 mt-2">Upload your broker CSV to analyze all holdings at once</p>
      </div>

      {!portfolio && (
        <div className="bg-white rounded-lg shadow border border-gray-200 p-8">
          <div className="max-w-2xl mx-auto text-center">
            <Upload className="h-16 w-16 text-gray-400 mx-auto mb-4" />
            <h2 className="text-xl font-bold text-gray-900 mb-2">Upload Portfolio CSV</h2>
            <p className="text-gray-600 mb-6">
              Supported formats: Zerodha, Groww, Upstox, or generic CSV with Symbol, Quantity, Avg Price
            </p>

            <label className="inline-block">
              <input
                type="file"
                accept=".csv"
                onChange={handleFileUpload}
                className="hidden"
                disabled={isUploading}
              />
              <Button disabled={isUploading} className="cursor-pointer">
                {isUploading ? 'Analyzing...' : 'Choose CSV File'}
              </Button>
            </label>

            <div className="mt-8 text-left bg-gray-50 p-4 rounded-lg">
              <h3 className="font-semibold text-gray-900 mb-2">CSV Format Example:</h3>
              <pre className="text-xs text-gray-600 overflow-x-auto">
{`Symbol,Quantity,Avg Price
HDFCBANK,50,1500
INFY,100,1400
TCS,80,3200`}
              </pre>
            </div>
          </div>
        </div>
      )}

      {portfolio && (
        <>
          {/* Summary Cards */}
          <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
            <div className="bg-white rounded-lg shadow border border-gray-200 p-4">
              <div className="text-sm text-gray-600">Total Holdings</div>
              <div className="text-2xl font-bold text-gray-900">{portfolio.length}</div>
            </div>
            <div className="bg-white rounded-lg shadow border border-gray-200 p-4">
              <div className="text-sm text-gray-600">Total Investment</div>
              <div className="text-2xl font-bold text-gray-900">₹{(totalInvestment/100000).toFixed(2)}L</div>
            </div>
            <div className="bg-white rounded-lg shadow border border-gray-200 p-4">
              <div className="text-sm text-gray-600">Avg Risk Score</div>
              <div className="text-2xl font-bold" style={{ color: getRiskColor(avgRisk) }}>
                {avgRisk.toFixed(1)}
              </div>
            </div>
            <div className="bg-white rounded-lg shadow border border-gray-200 p-4">
              <div className="text-sm text-gray-600">High Risk Stocks</div>
              <div className="text-2xl font-bold text-red-600">{highRiskCount}</div>
            </div>
          </div>

          {/* Risk Heatmap */}
          <div className="bg-white rounded-lg shadow border border-gray-200 p-6">
            <h2 className="text-xl font-bold text-gray-900 mb-4">Risk Heatmap</h2>
            <div className="grid grid-cols-2 md:grid-cols-4 gap-3">
              {portfolio.map((holding) => (
                <div
                  key={holding.symbol}
                  className="p-4 rounded-lg border-2 transition-transform hover:scale-105 cursor-pointer"
                  style={{
                    backgroundColor: `${getRiskColor(holding.risk_score)}20`,
                    borderColor: getRiskColor(holding.risk_score),
                  }}
                >
                  <div className="font-bold text-gray-900">{holding.symbol}</div>
                  <div className="text-2xl font-bold mt-1" style={{ color: getRiskColor(holding.risk_score) }}>
                    {holding.risk_score}
                  </div>
                  <div className="text-xs text-gray-600 mt-1">{holding.flags_count} flags</div>
                </div>
              ))}
            </div>
          </div>

          {/* Holdings Table */}
          <div className="bg-white rounded-lg shadow border border-gray-200 p-6">
            <h2 className="text-xl font-bold text-gray-900 mb-4">Detailed Holdings</h2>
            <div className="overflow-x-auto">
              <table className="w-full">
                <thead>
                  <tr className="border-b border-gray-200">
                    <th className="text-left py-3 px-4 text-sm font-semibold text-gray-900">Symbol</th>
                    <th className="text-left py-3 px-4 text-sm font-semibold text-gray-900">Company</th>
                    <th className="text-right py-3 px-4 text-sm font-semibold text-gray-900">Qty</th>
                    <th className="text-right py-3 px-4 text-sm font-semibold text-gray-900">Avg Price</th>
                    <th className="text-right py-3 px-4 text-sm font-semibold text-gray-900">Investment</th>
                    <th className="text-center py-3 px-4 text-sm font-semibold text-gray-900">Risk</th>
                    <th className="text-center py-3 px-4 text-sm font-semibold text-gray-900">Flags</th>
                    <th className="text-center py-3 px-4 text-sm font-semibold text-gray-900">Status</th>
                  </tr>
                </thead>
                <tbody>
                  {portfolio.map((holding) => (
                    <tr key={holding.symbol} className="border-b border-gray-100 hover:bg-gray-50">
                      <td className="py-3 px-4 font-semibold text-gray-900">{holding.symbol}</td>
                      <td className="py-3 px-4 text-gray-700">{holding.company_name}</td>
                      <td className="py-3 px-4 text-right text-gray-700">{holding.quantity}</td>
                      <td className="py-3 px-4 text-right text-gray-700">₹{holding.avg_price}</td>
                      <td className="py-3 px-4 text-right text-gray-700">₹{(holding.investment_value/1000).toFixed(0)}k</td>
                      <td className="py-3 px-4 text-center">
                        <span
                          className="px-3 py-1 rounded-full text-sm font-bold"
                          style={{
                            backgroundColor: `${getRiskColor(holding.risk_score)}20`,
                            color: getRiskColor(holding.risk_score),
                          }}
                        >
                          {holding.risk_score}
                        </span>
                      </td>
                      <td className="py-3 px-4 text-center">
                        <span className="text-sm text-gray-600">{holding.flags_count}</span>
                      </td>
                      <td className="py-3 px-4 text-center">
                        {(holding.risk_score || 0) >= 60 ? (
                          <XCircle className="h-5 w-5 text-red-500 mx-auto" />
                        ) : (
                          <CheckCircle2 className="h-5 w-5 text-green-500 mx-auto" />
                        )}
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </div>

          {/* Alerts */}
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

          <Button variant="outline" onClick={() => setPortfolio(null)}>
            Upload New Portfolio
          </Button>
        </>
      )}
    </div>
  );
}
