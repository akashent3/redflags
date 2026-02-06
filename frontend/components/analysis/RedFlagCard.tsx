'use client';

/**
 * RedFlagCard Component
 *
 * Displays a single red flag with severity, category, description, and evidence
 */

import { AlertTriangle, AlertCircle, Info, XCircle, ExternalLink } from 'lucide-react';
import { useState } from 'react';
import { useRouter, useParams } from 'next/navigation';
import { hasEducationalContent } from '@/lib/utils/flagHelpers';

export interface RedFlag {
  id: number;
  flag_id: string;
  name: string;
  severity: 'CRITICAL' | 'HIGH' | 'MEDIUM' | 'LOW';
  category: string;
  description: string;
  evidence: string;
  triggered: boolean;
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
      className={`border rounded-lg overflow-hidden transition-all ${
        isExpanded ? `${config.border} shadow-lg` : 'border-gray-200 hover:border-gray-300 hover:shadow-md'
      }`}
    >
      {/* Header - Always Visible */}
      <button
        onClick={() => setIsExpanded(!isExpanded)}
        className={`w-full text-left p-4 ${config.bg} hover:opacity-90 transition-opacity`}
      >
        <div className="flex items-start gap-3">
          <Icon className={`h-5 w-5 ${config.color} flex-shrink-0 mt-0.5`} />
          <div className="flex-1 min-w-0">
            <div className="flex items-start justify-between gap-3 mb-2">
              <h3 className="font-semibold text-gray-900 text-sm md:text-base">
                {flag.name}
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
            <p className="text-sm text-gray-700 line-clamp-2">
              {flag.description}
            </p>
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
        <div className="p-4 bg-white border-t border-gray-200">
          {/* Description */}
          <div className="mb-4">
            <h4 className="text-sm font-semibold text-gray-900 mb-2">
              What This Means
            </h4>
            <p className="text-sm text-gray-700 leading-relaxed">
              {flag.description}
            </p>
          </div>

          {/* Evidence */}
          <div className="mb-4">
            <h4 className="text-sm font-semibold text-gray-900 mb-2">
              Evidence
            </h4>
            <div className="bg-gray-50 border border-gray-200 rounded-lg p-3">
              <p className="text-sm text-gray-700 leading-relaxed whitespace-pre-wrap">
                {flag.evidence || 'No specific evidence provided.'}
              </p>
            </div>
          </div>

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

          {/* Action Buttons */}
          <div className="mt-4 flex items-center gap-3">
            {hasEducationalContent(flag.id) ? (
              <button
                onClick={(e) => {
                  e.stopPropagation();
                  router.push(`/report/${reportId}/flag/${flag.id}`);
                }}
                className="inline-flex items-center gap-2 px-4 py-2 bg-blue-600 text-white text-sm font-medium rounded-lg hover:bg-blue-700 transition-colors"
              >
                View Full Details
                <ExternalLink className="h-4 w-4" />
              </button>
            ) : (
              <span className="text-sm text-gray-500 italic">
                Detailed educational content coming soon for this flag
              </span>
            )}
          </div>
        </div>
      )}
    </div>
  );
}
