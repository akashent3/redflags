'use client';

/**
 * RedFlagsList Component
 *
 * Displays a list of red flags with filtering by severity and category
 */

import { useState } from 'react';
import RedFlagCard, { RedFlag } from './RedFlagCard';
import { Filter } from 'lucide-react';

interface RedFlagsListProps {
  flags: RedFlag[];
  showFilters?: boolean;
}

export default function RedFlagsList({ flags, showFilters = true }: RedFlagsListProps) {
  const [selectedSeverity, setSelectedSeverity] = useState<string>('all');
  const [selectedCategory, setSelectedCategory] = useState<string>('all');

  // Get unique categories
  const categories = Array.from(new Set(flags.map((f) => f.category)));

  // Filter flags
  const filteredFlags = flags.filter((flag) => {
    const severityMatch =
      selectedSeverity === 'all' || flag.severity === selectedSeverity;
    const categoryMatch =
      selectedCategory === 'all' || flag.category === selectedCategory;
    return severityMatch && categoryMatch;
  });

  // Count by severity
  const severityCounts = {
    all: flags.length,
    CRITICAL: flags.filter((f) => f.severity === 'CRITICAL').length,
    HIGH: flags.filter((f) => f.severity === 'HIGH').length,
    MEDIUM: flags.filter((f) => f.severity === 'MEDIUM').length,
    LOW: flags.filter((f) => f.severity === 'LOW').length,
  };

  return (
    <div className="space-y-6">
      {/* Filters */}
      {showFilters && (
        <div className="bg-white rounded-lg shadow border border-gray-200 p-4">
          <div className="flex items-center gap-2 mb-4">
            <Filter className="h-4 w-4 text-gray-600" />
            <h3 className="font-semibold text-gray-900">Filters</h3>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            {/* Severity Filter */}
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Severity
              </label>
              <div className="flex flex-wrap gap-2">
                <button
                  onClick={() => setSelectedSeverity('all')}
                  className={`px-3 py-1.5 rounded-lg text-xs font-medium transition-colors ${
                    selectedSeverity === 'all'
                      ? 'bg-gray-900 text-white'
                      : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
                  }`}
                >
                  All ({severityCounts.all})
                </button>
                <button
                  onClick={() => setSelectedSeverity('CRITICAL')}
                  className={`px-3 py-1.5 rounded-lg text-xs font-medium transition-colors ${
                    selectedSeverity === 'CRITICAL'
                      ? 'bg-red-600 text-white'
                      : 'bg-red-100 text-red-700 hover:bg-red-200'
                  }`}
                >
                  Critical ({severityCounts.CRITICAL})
                </button>
                <button
                  onClick={() => setSelectedSeverity('HIGH')}
                  className={`px-3 py-1.5 rounded-lg text-xs font-medium transition-colors ${
                    selectedSeverity === 'HIGH'
                      ? 'bg-orange-600 text-white'
                      : 'bg-orange-100 text-orange-700 hover:bg-orange-200'
                  }`}
                >
                  High ({severityCounts.HIGH})
                </button>
                <button
                  onClick={() => setSelectedSeverity('MEDIUM')}
                  className={`px-3 py-1.5 rounded-lg text-xs font-medium transition-colors ${
                    selectedSeverity === 'MEDIUM'
                      ? 'bg-yellow-600 text-white'
                      : 'bg-yellow-100 text-yellow-700 hover:bg-yellow-200'
                  }`}
                >
                  Medium ({severityCounts.MEDIUM})
                </button>
                <button
                  onClick={() => setSelectedSeverity('LOW')}
                  className={`px-3 py-1.5 rounded-lg text-xs font-medium transition-colors ${
                    selectedSeverity === 'LOW'
                      ? 'bg-blue-600 text-white'
                      : 'bg-blue-100 text-blue-700 hover:bg-blue-200'
                  }`}
                >
                  Low ({severityCounts.LOW})
                </button>
              </div>
            </div>

            {/* Category Filter */}
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Category
              </label>
              <select
                value={selectedCategory}
                onChange={(e) => setSelectedCategory(e.target.value)}
                className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500 text-sm"
              >
                <option value="all">All Categories</option>
                {categories.map((cat) => (
                  <option key={cat} value={cat}>
                    {cat}
                  </option>
                ))}
              </select>
            </div>
          </div>

          {/* Active Filters Count */}
          {(selectedSeverity !== 'all' || selectedCategory !== 'all') && (
            <div className="mt-3 flex items-center justify-between">
              <p className="text-sm text-gray-600">
                Showing {filteredFlags.length} of {flags.length} flags
              </p>
              <button
                onClick={() => {
                  setSelectedSeverity('all');
                  setSelectedCategory('all');
                }}
                className="text-sm text-blue-600 hover:text-blue-700 font-medium"
              >
                Clear Filters
              </button>
            </div>
          )}
        </div>
      )}

      {/* Results Count */}
      <div className="flex items-center justify-between">
        <h3 className="text-lg font-semibold text-gray-900">
          {filteredFlags.length} Red Flag{filteredFlags.length !== 1 ? 's' : ''} Detected
        </h3>
        {filteredFlags.length > 0 && (
          <p className="text-sm text-gray-600">
            Click any flag to expand details
          </p>
        )}
      </div>

      {/* Flags List */}
      {filteredFlags.length === 0 ? (
        <div className="bg-white rounded-lg shadow border border-gray-200 p-12 text-center">
          <div className="text-gray-400 mb-4">
            <svg
              className="h-16 w-16 mx-auto"
              fill="none"
              stroke="currentColor"
              viewBox="0 0 24 24"
            >
              <path
                strokeLinecap="round"
                strokeLinejoin="round"
                strokeWidth={2}
                d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z"
              />
            </svg>
          </div>
          <p className="text-gray-600 font-medium">No flags match your filters</p>
          <p className="text-sm text-gray-500 mt-1">
            Try adjusting your filter criteria
          </p>
        </div>
      ) : (
        <div className="space-y-3">
          {filteredFlags.map((flag) => (
            <RedFlagCard key={flag.id} flag={flag} />
          ))}
        </div>
      )}
    </div>
  );
}
