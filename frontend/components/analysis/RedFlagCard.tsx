'use client';

/**
 * RedFlagCard Component
 *
 * Displays a single red flag with severity, category, description, and evidence
 */

import { AlertTriangle, AlertCircle, Info, XCircle, ExternalLink } from 'lucide-react';
import { useState } from 'react';
import { useRouter, useParams } from 'next/navigation';

// ADD THESE HELPER FUNCTIONS after the imports:

/**
 * Get background color based on trigger status and confidence
 * Light red for triggered flags, light green for non-triggered
 * Opacity varies with confidence (higher confidence = darker shade)
 */
const getBackgroundColor = (isTriggered: boolean, confidence: number): string => {
  // Normalize confidence to 0-1 range
  const normalizedConfidence = (confidence || 50) / 100;
  
  // Calculate opacity: 0.15 (very light) to 0.45 (darker)
  const opacity = 0.15 + (normalizedConfidence * 0.3);
  
  if (isTriggered) {
    // Light red with varying opacity - rgb(239, 68, 68) = Tailwind red-500
    return `rgba(239, 68, 68, ${opacity})`;
  } else {
    // Light green with varying opacity - rgb(34, 197, 94) = Tailwind green-500
    return `rgba(34, 197, 94, ${opacity})`;
  }
};

/**
 * Get border color based on trigger status
 */
const getBorderColor = (isTriggered: boolean): string => {
  return isTriggered ? 'border-red-300' : 'border-green-300';
};

/**
 * Get the symbol to display (✓ for pass, ✗ for fail)
 */
const getSymbol = (isTriggered: boolean): string => {
  return isTriggered ? '✗' : '✓';
};

/**
 * Get symbol color
 */
const getSymbolColor = (isTriggered: boolean): string => {
  return isTriggered ? 'text-red-700' : 'text-green-700';
};

export interface RedFlag {
  id: string;  // ✅ UUID from backend
  flag_number: number;
  flag_name: string;  // ✅ Matches backend
  flag_description?: string;  // ✅ Optional from backend
  severity: 'CRITICAL' | 'HIGH' | 'MEDIUM' | 'LOW';
  category: string;
  is_triggered: boolean;  // ✅ Matches backend
  confidence_score?: number;
  evidence_text?: string;  // ✅ Matches backend
  page_references?: number[];
  detection_method?: string;
}

interface RedFlagCardProps {
  flag: RedFlag;
  expanded?: boolean;
}

export default function RedFlagCard({ flag, expanded: initialExpanded = false }: RedFlagCardProps) {
  const [isExpanded, setIsExpanded] = useState(initialExpanded);
  const router = useRouter();
  const params = useParams();
  const reportId = params?.id as string;

  // Severity configuration
  const severityConfig = {
    CRITICAL: {
      icon: XCircle,
      color: 'text-red-600',
      bg: 'bg-red-50',
      border: 'border-red-200',
      badge: 'bg-red-600 text-white',
      label: 'Critical',
    },
    HIGH: {
      icon: AlertTriangle,
      color: 'text-orange-600',
      bg: 'bg-orange-50',
      border: 'border-orange-200',
      badge: 'bg-orange-600 text-white',
      label: 'High',
    },
    MEDIUM: {
      icon: AlertCircle,
      color: 'text-yellow-600',
      bg: 'bg-yellow-50',
      border: 'border-yellow-200',
      badge: 'bg-yellow-600 text-white',
      label: 'Medium',
    },
    LOW: {
      icon: Info,
      color: 'text-blue-600',
      bg: 'bg-blue-50',
      border: 'border-blue-200',
      badge: 'bg-blue-600 text-white',
      label: 'Low',
    },
  };

  const config = severityConfig[flag.severity];
  const Icon = config.icon;

  return (
    <div
      className={`border rounded-lg overflow-hidden transition-all ${getBorderColor(flag.is_triggered)} ${
        isExpanded ? 'shadow-lg' : 'hover:shadow-md'
      }`}
      style={{ 
        backgroundColor: getBackgroundColor(flag.is_triggered, flag.confidence_score || 50)
      }}
    >
      {/* Header - Always Visible */}
      <button
        onClick={() => setIsExpanded(!isExpanded)}
        className="w-full text-left p-4 hover:opacity-95 transition-opacity"
      >
        <div className="flex items-start gap-3">
          {/* Replace icon with ✓/✗ symbol */}
          <span className={`text-2xl font-bold ${getSymbolColor(flag.is_triggered)} flex-shrink-0 leading-none`}>
            {getSymbol(flag.is_triggered)}
          </span>
          <div className="flex-1 min-w-0">
            <div className="flex items-start justify-between gap-3 mb-2">
              <h3 className="font-semibold text-gray-900 text-sm md:text-base">
                #{flag.flag_number} - {flag.flag_name}
              </h3>
              <div className="flex items-center gap-2 flex-shrink-0">
                <span className={`px-2 py-1 rounded text-xs font-medium ${config.badge}`}>
                  {config.label}
                </span>
                <span className="px-2 py-1 rounded text-xs font-medium bg-gray-200 text-gray-700">
                  {flag.category}
                </span>
              </div>
            </div>
            {flag.flag_description && (
              <p className="text-sm text-gray-700 line-clamp-2">
                {flag.flag_description}
              </p>
            )}
          </div>
          <div className={`text-gray-400 flex-shrink-0 ml-2 transform transition-transform ${
            isExpanded ? 'rotate-180' : ''
          }`}>
            <svg className="h-5 w-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 9l-7 7-7-7" />
            </svg>
          </div>
        </div>
      </button>

      {/* Expanded Content */}
      {isExpanded && (
        <div 
          className="p-4 border-t border-gray-200"
          style={{ 
            backgroundColor: 'white'
          }}
        >
          {/* Description */}
          {flag.flag_description && (
            <div className="mb-4">
              <h4 className="text-sm font-semibold text-gray-900 mb-2">
                What This Means
              </h4>
              <p className="text-sm text-gray-700 leading-relaxed">
                {flag.flag_description}
              </p>
            </div>
          )}

          {/* Evidence */}
          <div className="mb-4">
            <h4 className="text-sm font-semibold text-gray-900 mb-2">
              Evidence
            </h4>
            <div className="bg-gray-50 border border-gray-200 rounded-lg p-3">
              <p className="text-sm text-gray-700 leading-relaxed whitespace-pre-wrap">
                {flag.evidence_text || 'No specific evidence provided.'}
              </p>
            </div>
          </div>

          {/* Confidence Score */}
          {flag.confidence_score !== undefined && (
            <div className="mb-4">
              <h4 className="text-sm font-semibold text-gray-900 mb-2">
                Confidence Score
              </h4>
              <div className="flex items-center gap-3">
                <div className="flex-1 bg-gray-200 rounded-full h-2">
                  <div
                    className="bg-blue-600 h-2 rounded-full"
                    style={{ width: `${flag.confidence_score}%` }}
                  />
                </div>
                <span className="text-sm font-medium text-gray-900">
                  {flag.confidence_score}%
                </span>
              </div>
            </div>
          )}

          {/* Page References */}
          {flag.page_references && flag.page_references.length > 0 && (
            <div className="mb-4">
              <h4 className="text-sm font-semibold text-gray-900 mb-2">
                Page References
              </h4>
              <p className="text-sm text-gray-600">
                Pages: {flag.page_references.join(', ')}
              </p>
            </div>
          )}

          {/* Impact Level */}
          <div className="flex items-start gap-2 bg-gray-50 rounded-lg p-3">
            <AlertTriangle className="h-4 w-4 text-gray-500 mt-0.5 flex-shrink-0" />
            <div className="text-xs text-gray-600">
              <span className="font-medium">Impact:</span>{' '}
              {flag.severity === 'CRITICAL' &&
                'This is a critical issue that requires immediate attention and investigation.'}
              {flag.severity === 'HIGH' &&
                'This issue significantly increases the risk profile and warrants careful review.'}
              {flag.severity === 'MEDIUM' &&
                'This concern should be monitored and may require further investigation.'}
              {flag.severity === 'LOW' &&
                'This is a minor concern that should be noted but may not require immediate action.'}
            </div>
          </div>

          {/* Detection Method */}
          {flag.detection_method && (
            <div className="mt-4 text-xs text-gray-500">
              Detection method: <span className="font-medium">{flag.detection_method}</span>
            </div>
          )}
        </div>
      )}
    </div>
  );
}