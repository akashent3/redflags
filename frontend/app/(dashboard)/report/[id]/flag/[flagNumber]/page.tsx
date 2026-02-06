'use client';

/**
 * Flag Detail Page
 *
 * Deep-dive page for individual red flags with educational content,
 * similar fraud cases, and investor guidance
 */

import { use, useState } from 'react';
import { useRouter } from 'next/navigation';
import { Button } from '@/components/ui/button';
import {
  getEducationalContent,
  hasEducationalContent,
  getSeverityColor,
  getCategoryColor,
} from '@/lib/utils/flagHelpers';
import {
  ArrowLeft,
  AlertTriangle,
  Info,
  BookOpen,
  TrendingDown,
  CheckCircle2,
  FileText,
  Building2,
} from 'lucide-react';

interface FlagDetailPageProps {
  params: Promise<{
    id: string;
    flagNumber: string;
  }>;
}

export default function FlagDetailPage({ params }: FlagDetailPageProps) {
  const resolvedParams = use(params);
  const router = useRouter();
  const flagNumber = parseInt(resolvedParams.flagNumber, 10);

  // Get educational content
  const education = getEducationalContent(flagNumber);

  if (!education || !hasEducationalContent(flagNumber)) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-gray-50">
        <div className="text-center max-w-md">
          <AlertTriangle className="h-16 w-16 text-gray-400 mx-auto mb-4" />
          <h1 className="text-2xl font-bold text-gray-900 mb-2">
            Flag Details Not Available
          </h1>
          <p className="text-gray-600 mb-6">
            Detailed educational content for flag #{flagNumber} is not yet available.
            We're continuously adding content for all flags.
          </p>
          <Button onClick={() => router.back()} variant="outline">
            <ArrowLeft className="mr-2 h-4 w-4" />
            Go Back
          </Button>
        </div>
      </div>
    );
  }

  const severityColor = getSeverityColor(education.severity);
  const categoryColor = getCategoryColor(education.category);

  return (
    <div className="space-y-6">
      {/* Back Navigation */}
      <button
        onClick={() => router.back()}
        className="flex items-center gap-2 text-sm text-gray-600 hover:text-gray-900"
      >
        <ArrowLeft className="h-4 w-4" />
        Back to Report
      </button>

      {/* Header */}
      <div className="bg-white rounded-lg shadow border border-gray-200 p-6">
        <div className="flex items-start justify-between">
          <div>
            <div className="flex items-center gap-3 mb-2">
              <span className="text-sm font-medium text-gray-500">
                Flag #{education.flagNumber}
              </span>
              <span
                className={`px-3 py-1 rounded-full text-xs font-semibold ${severityColor.bg} ${severityColor.text}`}
              >
                {education.severity}
              </span>
              <span
                className={`px-3 py-1 rounded-full text-xs font-semibold ${categoryColor.bg} ${categoryColor.text}`}
              >
                {education.category}
              </span>
            </div>
            <h1 className="text-3xl font-bold text-gray-900">{education.title}</h1>
          </div>
          <AlertTriangle className="h-10 w-10 text-orange-500 flex-shrink-0" />
        </div>
      </div>

      {/* What It Means */}
      <div className="bg-white rounded-lg shadow border border-gray-200 p-6">
        <div className="flex items-start gap-3 mb-4">
          <Info className="h-6 w-6 text-blue-600 flex-shrink-0 mt-1" />
          <div>
            <h2 className="text-xl font-bold text-gray-900 mb-2">What This Means</h2>
            <p className="text-gray-700 leading-relaxed">{education.whatItMeans}</p>
          </div>
        </div>
      </div>

      {/* Why It Matters */}
      <div className="bg-white rounded-lg shadow border border-gray-200 p-6">
        <div className="flex items-start gap-3 mb-4">
          <BookOpen className="h-6 w-6 text-purple-600 flex-shrink-0 mt-1" />
          <div>
            <h2 className="text-xl font-bold text-gray-900 mb-2">Why It Matters</h2>
            <p className="text-gray-700 leading-relaxed">{education.whyItMatters}</p>
          </div>
        </div>
      </div>

      {/* Red Flags to Watch */}
      <div className="bg-white rounded-lg shadow border border-gray-200 p-6">
        <div className="flex items-start gap-3">
          <AlertTriangle className="h-6 w-6 text-red-600 flex-shrink-0 mt-1" />
          <div className="flex-1">
            <h2 className="text-xl font-bold text-gray-900 mb-4">
              Specific Red Flags to Watch For
            </h2>
            <ul className="space-y-2">
              {education.redFlagsToWatch.map((flag, index) => (
                <li key={index} className="flex items-start gap-3">
                  <span className="text-red-500 font-bold mt-1">•</span>
                  <span className="text-gray-700">{flag}</span>
                </li>
              ))}
            </ul>
          </div>
        </div>
      </div>

      {/* Similar Fraud Cases */}
      <div className="bg-white rounded-lg shadow border border-gray-200 p-6">
        <div className="flex items-start gap-3 mb-6">
          <Building2 className="h-6 w-6 text-gray-600 flex-shrink-0 mt-1" />
          <div className="flex-1">
            <h2 className="text-xl font-bold text-gray-900 mb-2">
              Similar Historical Cases
            </h2>
            <p className="text-sm text-gray-600">
              Real-world examples of companies that exhibited this red flag
            </p>
          </div>
        </div>

        <div className="space-y-6">
          {education.similarCases.map((case_, index) => (
            <div
              key={index}
              className="border-l-4 border-red-500 bg-red-50 p-4 rounded-r-lg"
            >
              <div className="flex items-start justify-between mb-3">
                <div>
                  <h3 className="font-bold text-gray-900 text-lg">{case_.company}</h3>
                  <span className="text-sm text-gray-600">{case_.year}</span>
                </div>
                <TrendingDown className="h-5 w-5 text-red-600" />
              </div>

              <div className="space-y-3">
                <div>
                  <h4 className="font-semibold text-sm text-gray-700 mb-1">
                    What Happened:
                  </h4>
                  <p className="text-sm text-gray-700">{case_.description}</p>
                </div>

                <div>
                  <h4 className="font-semibold text-sm text-gray-700 mb-1">Outcome:</h4>
                  <p className="text-sm text-gray-700">{case_.outcome}</p>
                </div>

                <div>
                  <h4 className="font-semibold text-sm text-gray-700 mb-1">Impact:</h4>
                  <p className="text-sm text-gray-700">{case_.impact}</p>
                </div>
              </div>
            </div>
          ))}
        </div>
      </div>

      {/* Investor Actions */}
      <div className="bg-white rounded-lg shadow border border-gray-200 p-6">
        <div className="flex items-start gap-3 mb-4">
          <CheckCircle2 className="h-6 w-6 text-green-600 flex-shrink-0 mt-1" />
          <div className="flex-1">
            <h2 className="text-xl font-bold text-gray-900 mb-2">
              Recommended Investor Actions
            </h2>
            <p className="text-sm text-gray-600 mb-4">
              Steps you should take when you encounter this red flag
            </p>

            <ol className="space-y-3">
              {education.investorActions.map((action, index) => (
                <li key={index} className="flex items-start gap-3">
                  <span className="flex-shrink-0 w-6 h-6 bg-green-100 text-green-800 rounded-full flex items-center justify-center text-xs font-bold">
                    {index + 1}
                  </span>
                  <span className="text-gray-700 flex-1">{action}</span>
                </li>
              ))}
            </ol>
          </div>
        </div>
      </div>

      {/* Detection Method */}
      <div className="bg-gray-50 border border-gray-200 rounded-lg p-6">
        <div className="flex items-start gap-3">
          <FileText className="h-6 w-6 text-gray-600 flex-shrink-0 mt-1" />
          <div>
            <h2 className="text-lg font-bold text-gray-900 mb-2">
              How This Flag Was Detected
            </h2>
            <p className="text-sm text-gray-700">{education.detectionMethod}</p>
          </div>
        </div>
      </div>

      {/* Disclaimer */}
      <div className="bg-blue-50 border border-blue-200 rounded-lg p-4">
        <p className="text-sm text-blue-800">
          <strong>Disclaimer:</strong> This educational content is for informational
          purposes only and should not be considered as investment advice. The presence
          of a red flag does not necessarily indicate fraud or wrongdoing. Always conduct
          thorough due diligence and consult with financial professionals before making
          investment decisions.
        </p>
      </div>
    </div>
  );
}
