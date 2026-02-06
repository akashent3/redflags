'use client';

/**
 * CategoryBreakdown Component
 *
 * Displays horizontal bars showing risk scores by category
 */

import { AlertTriangle, TrendingUp, Users, Shield, FileText, DollarSign, MessageSquare, Search } from 'lucide-react';

export interface CategoryData {
  name: string;
  score: number; // 0-100
  flagsCount: number;
  weight: number; // Percentage weight in overall score
}

interface CategoryBreakdownProps {
  categories: CategoryData[];
  compact?: boolean;
}

// Category icons mapping
const categoryIcons: Record<string, any> = {
  'Auditor': Search,
  'Cash Flow': TrendingUp,
  'Related Party': Users,
  'Promoter': Shield,
  'Governance': FileText,
  'Balance Sheet': DollarSign,
  'Revenue': TrendingUp,
  'Textual': MessageSquare,
};

export default function CategoryBreakdown({ categories, compact = false }: CategoryBreakdownProps) {
  const getColor = (score: number) => {
    if (score >= 70) return {
      bg: 'bg-red-500',
      light: 'bg-red-100',
      text: 'text-red-600',
      border: 'border-red-200',
    };
    if (score >= 40) return {
      bg: 'bg-yellow-500',
      light: 'bg-yellow-100',
      text: 'text-yellow-600',
      border: 'border-yellow-200',
    };
    return {
      bg: 'bg-green-500',
      light: 'bg-green-100',
      text: 'text-green-600',
      border: 'border-green-200',
    };
  };

  return (
    <div className="space-y-4">
      {categories.map((category) => {
        const color = getColor(category.score);
        const Icon = categoryIcons[category.name] || AlertTriangle;

        return (
          <div key={category.name} className={compact ? 'space-y-2' : 'space-y-3'}>
            {/* Category Header */}
            <div className="flex items-center justify-between">
              <div className="flex items-center gap-3">
                <div className={`p-2 rounded-lg ${color.light}`}>
                  <Icon className={`h-4 w-4 ${color.text}`} />
                </div>
                <div>
                  <h4 className="font-medium text-gray-900">{category.name}</h4>
                  {!compact && (
                    <p className="text-xs text-gray-500">
                      {category.flagsCount} flag{category.flagsCount !== 1 ? 's' : ''} detected • {category.weight}% weight
                    </p>
                  )}
                </div>
              </div>
              <div className="flex items-center gap-3">
                {compact && (
                  <span className="text-xs text-gray-500">
                    {category.flagsCount} flags
                  </span>
                )}
                <span className={`text-lg font-bold ${color.text}`}>
                  {category.score}
                </span>
              </div>
            </div>

            {/* Progress Bar */}
            <div className="relative">
              <div className={`w-full h-3 rounded-full ${color.light}`}>
                <div
                  className={`h-3 rounded-full ${color.bg} transition-all duration-500 ease-out`}
                  style={{ width: `${category.score}%` }}
                />
              </div>
              {/* Score markers */}
              {!compact && (
                <div className="flex justify-between mt-1">
                  <span className="text-xs text-gray-400">0</span>
                  <span className="text-xs text-gray-400">25</span>
                  <span className="text-xs text-gray-400">50</span>
                  <span className="text-xs text-gray-400">75</span>
                  <span className="text-xs text-gray-400">100</span>
                </div>
              )}
            </div>
          </div>
        );
      })}
    </div>
  );
}
