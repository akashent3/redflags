'use client';

/**
 * Analysis Page
 *
 * Upload PDF or search for company to analyze
 */

import { useState } from 'react';
import { useRouter } from 'next/navigation';
import { Button } from '@/components/ui/button';
import {
  Upload,
  Search,
  FileText,
  X,
  Loader2,
  AlertCircle,
  CheckCircle,
  Building2,
} from 'lucide-react';
import { api } from '@/lib/api/client';

interface CompanySearchResult {
  symbol: string;
  name: string;
  nse_code: string;
  bse_code: string;
  exchange: string;
  isin: string;
}

export default function AnalyzePage() {
  const router = useRouter();
  const [activeTab, setActiveTab] = useState<'upload' | 'search'>('search');
  const [selectedFile, setSelectedFile] = useState<File | null>(null);
  const [isDragging, setIsDragging] = useState(false);
  const [isUploading, setIsUploading] = useState(false);
  const [uploadProgress, setUploadProgress] = useState(0);
  const [searchQuery, setSearchQuery] = useState('');
  const [searchResults, setSearchResults] = useState<CompanySearchResult[]>([]);
  const [isSearching, setIsSearching] = useState(false);
  const [isAnalyzing, setIsAnalyzing] = useState(false);
  const [analyzingSymbol, setAnalyzingSymbol] = useState<string | null>(null);
  const [error, setError] = useState<string | null>(null);

  const handleDragEnter = (e: React.DragEvent) => {
    e.preventDefault();
    e.stopPropagation();
    setIsDragging(true);
  };

  const handleDragLeave = (e: React.DragEvent) => {
    e.preventDefault();
    e.stopPropagation();
    setIsDragging(false);
  };

  const handleDragOver = (e: React.DragEvent) => {
    e.preventDefault();
    e.stopPropagation();
  };

  const handleDrop = (e: React.DragEvent) => {
    e.preventDefault();
    e.stopPropagation();
    setIsDragging(false);

    const files = e.dataTransfer.files;
    if (files && files.length > 0) {
      const file = files[0];
      validateAndSetFile(file);
    }
  };

  const handleFileSelect = (e: React.ChangeEvent<HTMLInputElement>) => {
    const files = e.target.files;
    if (files && files.length > 0) {
      validateAndSetFile(files[0]);
    }
  };

  const validateAndSetFile = (file: File) => {
    setError(null);

    // Check file type
    if (file.type !== 'application/pdf') {
      setError('Please upload a PDF file');
      return;
    }

    // Check file size (max 50MB)
    const maxSize = 50 * 1024 * 1024; // 50MB
    if (file.size > maxSize) {
      setError('File size must be less than 50MB');
      return;
    }

    setSelectedFile(file);
  };

  const handleRemoveFile = () => {
    setSelectedFile(null);
    setError(null);
  };

  const handleUpload = async () => {
    if (!selectedFile) return;

    setIsUploading(true);
    setError(null);
    setUploadProgress(0);

    try {
      // Upload PDF to /reports/upload
      setUploadProgress(20);
      const response = await api.upload('/reports/upload', selectedFile);
      setUploadProgress(100);

      // Redirect to report page
      setTimeout(() => {
        const reportId = response.data.report_id;
        router.push(`/report/${reportId}`);
      }, 500);
    } catch (err: any) {
      console.error('Upload failed:', err);
      setError(err.response?.data?.detail || 'Upload failed. Please try again.');
      setIsUploading(false);
      setUploadProgress(0);
    }
  };

  const handleSearch = async () => {
    if (!searchQuery.trim()) return;

    setIsSearching(true);
    setError(null);

    try {
      const response = await api.get<{
        total: number;
        returned: number;
        results: CompanySearchResult[];
      }>('/companies/finedge/search', {
        params: {
          q: searchQuery,
          limit: 20,
        },
      });

      setSearchResults(response.data.results);
    } catch (err: any) {
      console.error('Search failed:', err);
      setError(err.response?.data?.detail || 'Search failed. Please try again.');
    } finally {
      setIsSearching(false);
    }
  };

  const pollTaskStatus = async (taskId: string): Promise<any> => {
    const maxAttempts = 120; // 10 minutes max
    let attempts = 0;

    while (attempts < maxAttempts) {
      try {
        const response = await api.get(`/analysis/task/${taskId}`);
        const status = response.data.status;

        if (status === 'SUCCESS') {
          return response.data;
        } else if (status === 'FAILURE') {
          throw new Error(response.data.error || 'Analysis failed');
        }

        // Still pending/progress - wait and retry
        await new Promise((resolve) => setTimeout(resolve, 5000)); // Wait 5 seconds
        attempts++;
      } catch (err) {
        throw err;
      }
    }

    throw new Error('Analysis timed out');
  };

  const handleAnalyzeCompany = async (company: CompanySearchResult) => {
    setIsAnalyzing(true);
    setAnalyzingSymbol(company.symbol);
    setError(null);

    try {
      // Trigger analysis via /analysis/analyze-symbol/{symbol}
      const response = await api.post(`/analysis/analyze-symbol/${company.symbol}`);
      
      // ✅ NEW: Check if analysis already exists (instant completion)
      if (response.data.status === 'COMPLETED') {
        console.log('✓ Analysis already exists! Redirecting immediately...');
        
        // Get report_id from response
        const reportId = response.data.report_id;
        
        if (!reportId) {
          throw new Error('No report ID returned from completed analysis');
        }
        
        // Redirect immediately to report page (< 1 second)
        router.push(`/report/${reportId}`);
        return;
      }

      // ✅ NEW: Validate task_id exists for new analysis
      const taskId = response.data.task_id;
      
      if (!taskId) {
        throw new Error('No task ID returned from server');
      }

      console.log('⏳ New analysis started. Polling for completion...');

      // Poll for status (new analysis)
      const result = await pollTaskStatus(taskId);

      // Redirect to report page when complete
      const reportId = result.report_id;
      
      if (!reportId) {
        throw new Error('No report ID returned from analysis result');
      }
      
      router.push(`/report/${reportId}`);
    } catch (err: any) {
      console.error('Analysis failed:', err);
      setError(
        err.response?.data?.detail ||
          err.message ||
          'Analysis failed. Please try again.'
      );
      setIsAnalyzing(false);
      setAnalyzingSymbol(null);
    }
  };

  return (
    <div className="space-y-8">
      {/* Header */}
      <div>
        <h1 className="text-3xl font-bold text-gray-900">Analyze Report</h1>
        <p className="mt-2 text-gray-600">
          Search for any NSE/BSE company or upload an annual report PDF
        </p>
      </div>

      {/* Tabs */}
      <div className="border-b border-gray-200">
        <div className="flex gap-8">
          <button
            onClick={() => setActiveTab('search')}
            className={`pb-4 px-1 border-b-2 font-medium text-sm transition-colors ${
              activeTab === 'search'
                ? 'border-blue-600 text-blue-600'
                : 'border-transparent text-gray-600 hover:text-gray-900 hover:border-gray-300'
            }`}
          >
            <Search className="h-4 w-4 inline mr-2" />
            Search Company
          </button>
          <button
            onClick={() => setActiveTab('upload')}
            className={`pb-4 px-1 border-b-2 font-medium text-sm transition-colors ${
              activeTab === 'upload'
                ? 'border-blue-600 text-blue-600'
                : 'border-transparent text-gray-600 hover:text-gray-900 hover:border-gray-300'
            }`}
          >
            <Upload className="h-4 w-4 inline mr-2" />
            Upload PDF
          </button>
        </div>
      </div>

      {/* Upload Tab */}
      {activeTab === 'upload' && (
        <div className="max-w-2xl">
          <div className="bg-white rounded-lg shadow border border-gray-200 p-8">
            {/* Error Alert */}
            {error && (
              <div className="bg-red-50 border border-red-200 text-red-800 px-4 py-3 rounded-md flex items-start gap-3 mb-6">
                <AlertCircle className="h-5 w-5 mt-0.5 flex-shrink-0" />
                <div className="flex-1">
                  <p className="text-sm font-medium">Error</p>
                  <p className="text-sm mt-1">{error}</p>
                </div>
              </div>
            )}

            {!selectedFile ? (
              <>
                {/* Dropzone */}
                <div
                  onDragEnter={handleDragEnter}
                  onDragOver={handleDragOver}
                  onDragLeave={handleDragLeave}
                  onDrop={handleDrop}
                  className={`border-2 border-dashed rounded-lg p-12 text-center transition-colors ${
                    isDragging
                      ? 'border-blue-500 bg-blue-50'
                      : 'border-gray-300 hover:border-gray-400'
                  }`}
                >
                  <Upload className="h-12 w-12 text-gray-400 mx-auto mb-4" />
                  <p className="text-lg font-medium text-gray-900 mb-2">
                    Drop your PDF here, or click to browse
                  </p>
                  <p className="text-sm text-gray-600 mb-6">
                    Maximum file size: 50MB
                  </p>
                  <input
                    type="file"
                    accept=".pdf"
                    onChange={handleFileSelect}
                    className="hidden"
                    id="file-upload"
                  />
                  <label htmlFor="file-upload">
                    <Button asChild>
                      <span>Choose File</span>
                    </Button>
                  </label>
                </div>

                {/* Supported formats */}
                <div className="mt-6 text-sm text-gray-600">
                  <p className="font-medium mb-2">Supported formats:</p>
                  <ul className="list-disc list-inside space-y-1">
                    <li>PDF files up to 50MB</li>
                    <li>Annual reports with financial statements</li>
                    <li>Both text-based and scanned PDFs</li>
                  </ul>
                </div>
              </>
            ) : (
              <>
                {/* Selected File */}
                <div className="bg-gray-50 rounded-lg p-6 mb-6">
                  <div className="flex items-start gap-4">
                    <div className="bg-blue-100 p-3 rounded-lg">
                      <FileText className="h-6 w-6 text-blue-600" />
                    </div>
                    <div className="flex-1">
                      <h3 className="font-medium text-gray-900 mb-1">
                        {selectedFile.name}
                      </h3>
                      <p className="text-sm text-gray-600">
                        {(selectedFile.size / (1024 * 1024)).toFixed(2)} MB
                      </p>
                    </div>
                    {!isUploading && (
                      <button
                        onClick={handleRemoveFile}
                        className="text-gray-400 hover:text-gray-600"
                      >
                        <X className="h-5 w-5" />
                      </button>
                    )}
                  </div>

                  {/* Upload Progress */}
                  {isUploading && (
                    <div className="mt-4">
                      <div className="flex items-center justify-between text-sm text-gray-600 mb-2">
                        <span>Uploading...</span>
                        <span>{uploadProgress}%</span>
                      </div>
                      <div className="w-full bg-gray-200 rounded-full h-2">
                        <div
                          className="bg-blue-600 h-2 rounded-full transition-all duration-300"
                          style={{ width: `${uploadProgress}%` }}
                        />
                      </div>
                    </div>
                  )}
                </div>

                {/* Action Buttons */}
                <div className="flex items-center gap-4">
                  <Button
                    onClick={handleUpload}
                    disabled={isUploading}
                    className="flex-1"
                  >
                    {isUploading ? (
                      <>
                        <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                        Analyzing...
                      </>
                    ) : (
                      <>
                        <CheckCircle className="mr-2 h-4 w-4" />
                        Analyze Report
                      </>
                    )}
                  </Button>
                  {!isUploading && (
                    <Button onClick={handleRemoveFile} variant="outline">
                      Cancel
                    </Button>
                  )}
                </div>

                {/* Info */}
                {!isUploading && (
                  <div className="mt-6 bg-blue-50 border border-blue-200 rounded-lg p-4">
                    <p className="text-sm text-blue-800">
                      <strong>What happens next?</strong> We'll analyze the PDF using
                      Gemini AI and check 44+ red flags. This usually takes 1-2 minutes.
                    </p>
                  </div>
                )}
              </>
            )}
          </div>
        </div>
      )}

      {/* Search Tab */}
      {activeTab === 'search' && (
        <div className="max-w-4xl">
          <div className="bg-white rounded-lg shadow border border-gray-200 p-8">
            {/* Error Alert */}
            {error && (
              <div className="bg-red-50 border border-red-200 text-red-800 px-4 py-3 rounded-md flex items-start gap-3 mb-6">
                <AlertCircle className="h-5 w-5 mt-0.5 flex-shrink-0" />
                <div className="flex-1">
                  <p className="text-sm font-medium">Error</p>
                  <p className="text-sm mt-1">{error}</p>
                </div>
              </div>
            )}

            {/* Analyzing Alert */}
            {isAnalyzing && analyzingSymbol && (
              <div className="bg-blue-50 border border-blue-200 text-blue-800 px-4 py-3 rounded-md flex items-start gap-3 mb-6">
                <Loader2 className="h-5 w-5 mt-0.5 flex-shrink-0 animate-spin" />
                <div className="flex-1">
                  <p className="text-sm font-medium">Analyzing {analyzingSymbol}</p>
                  <p className="text-sm mt-1">
                    Checking for existing analysis or fetching latest annual report from NSE India...
                  </p>
                </div>
              </div>
            )}

            {/* Search Bar */}
            <div className="flex gap-4 mb-6">
              <div className="flex-1 relative">
                <Search className="absolute left-3 top-1/2 -translate-y-1/2 h-5 w-5 text-gray-400" />
                <input
                  type="text"
                  placeholder="Search by company name or stock code (e.g., Reliance, TCS, INFY)"
                  value={searchQuery}
                  onChange={(e) => setSearchQuery(e.target.value)}
                  onKeyPress={(e) => e.key === 'Enter' && handleSearch()}
                  disabled={isAnalyzing}
                  className="w-full pl-10 pr-4 py-3 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500 disabled:bg-gray-100 disabled:cursor-not-allowed"
                />
              </div>
              <Button onClick={handleSearch} disabled={isSearching || !searchQuery.trim() || isAnalyzing}>
                {isSearching ? (
                  <Loader2 className="h-4 w-4 animate-spin" />
                ) : (
                  'Search'
                )}
              </Button>
            </div>

            {/* Search Results */}
            {searchResults.length > 0 ? (
              <div className="space-y-3">
                <h3 className="text-sm font-medium text-gray-700 mb-3">
                  Search Results ({searchResults.length})
                </h3>
                {searchResults.map((company) => (
                  <div
                    key={company.symbol}
                    className="flex items-center justify-between p-4 border border-gray-200 rounded-lg hover:border-blue-500 hover:shadow-md transition-all"
                  >
                    <div className="flex-1">
                      <h4 className="font-medium text-gray-900 flex items-center gap-2">
                        <Building2 className="h-4 w-4 text-gray-400" />
                        {company.name}
                      </h4>
                      <div className="flex items-center gap-4 mt-1">
                        <span className="text-sm text-gray-600">
                          NSE: <span className="font-medium">{company.nse_code || company.symbol}</span>
                        </span>
                        {company.bse_code && (
                          <span className="text-sm text-gray-600">
                            BSE: <span className="font-medium">{company.bse_code}</span>
                          </span>
                        )}
                        <span className="text-sm text-gray-600">
                          {company.exchange}
                        </span>
                      </div>
                    </div>
                    <Button
                      onClick={() => handleAnalyzeCompany(company)}
                      disabled={isAnalyzing}
                      variant="outline"
                    >
                      {isAnalyzing && analyzingSymbol === company.symbol ? (
                        <>
                          <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                          Analyzing...
                        </>
                      ) : (
                        'Analyze'
                      )}
                    </Button>
                  </div>
                ))}
              </div>
            ) : searchQuery && !isSearching ? (
              <div className="text-center py-12">
                <Search className="h-12 w-12 text-gray-400 mx-auto mb-3" />
                <p className="text-gray-600">No companies found</p>
                <p className="text-sm text-gray-500 mt-1">
                  Try searching with a different name or stock code
                </p>
              </div>
            ) : (
              <div className="text-center py-12">
                <Search className="h-12 w-12 text-gray-400 mx-auto mb-3" />
                <p className="text-gray-600 mb-2">Search NSE/BSE Listed Companies</p>
                <p className="text-sm text-gray-500">
                  Enter a company name or stock code to get started
                </p>
              </div>
            )}
          </div>

          {/* Info */}
          <div className="mt-6 bg-blue-50 border border-blue-200 rounded-lg p-4">
            <p className="text-sm text-blue-800">
              <strong>How it works:</strong> Search for any NSE/BSE company. If analysis already exists, 
              you'll be redirected instantly (&lt; 1 second)! Otherwise, we'll automatically fetch the latest 
              annual report from NSE India, extract financial data from FinEdge API, and analyze 44+ red flags 
              using AI. New analysis typically takes 1-2 minutes.
            </p>
          </div>
        </div>
      )}
    </div>
  );
}