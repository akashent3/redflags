'use client';

/**
 * SpiderChart Component
 *
 * Displays an 8-category radar chart showing risk breakdown
 * Categories: Auditor, Cash Flow, Related Party, Promoter, Governance, Balance Sheet, Revenue, Textual
 */

import {
  Radar,
  RadarChart,
  PolarGrid,
  PolarAngleAxis,
  PolarRadiusAxis,
  ResponsiveContainer,
  Tooltip,
} from 'recharts';

export interface CategoryScore {
  category: string;
  score: number; // 0-100
  fullMark: number;
}

interface SpiderChartProps {
  categories: CategoryScore[];
  size?: 'small' | 'medium' | 'large';
}

export default function SpiderChart({ categories, size = 'large' }: SpiderChartProps) {
  // Size configurations
  const sizeConfig = {
    small: { height: 250 },
    medium: { height: 350 },
    large: { height: 450 },
  };

  const config = sizeConfig[size];

  // Custom tooltip
  const CustomTooltip = ({ active, payload }: any) => {
    if (active && payload && payload.length) {
      const data = payload[0].payload;
      const getColor = (score: number) => {
        if (score >= 70) return '#dc2626'; // Red
        if (score >= 40) return '#eab308'; // Yellow
        return '#16a34a'; // Green
      };

      return (
        <div className="bg-white border border-gray-200 shadow-lg rounded-lg p-3">
          <p className="font-semibold text-gray-900">{data.category}</p>
          <p className="text-sm text-gray-600 mt-1">
            Risk Score:{' '}
            <span
              className="font-bold"
              style={{ color: getColor(data.score) }}
            >
              {data.score}
            </span>
            /100
          </p>
        </div>
      );
    }
    return null;
  };

  return (
    <div className="w-full">
      <ResponsiveContainer width="100%" height={config.height}>
        <RadarChart data={categories}>
          <PolarGrid stroke="#e5e7eb" />
          <PolarAngleAxis
            dataKey="category"
            tick={{ fill: '#6b7280', fontSize: 12 }}
            tickLine={false}
          />
          <PolarRadiusAxis
            angle={90}
            domain={[0, 100]}
            tick={{ fill: '#9ca3af', fontSize: 10 }}
            tickCount={6}
          />
          <Radar
            name="Risk Score"
            dataKey="score"
            stroke="#2563eb"
            fill="#3b82f6"
            fillOpacity={0.3}
            strokeWidth={2}
          />
          <Tooltip content={<CustomTooltip />} />
        </RadarChart>
      </ResponsiveContainer>

      {/* Legend */}
      <div className="mt-6 grid grid-cols-2 md:grid-cols-4 gap-4">
        {categories.map((cat) => {
          const getColor = (score: number) => {
            if (score >= 70) return 'bg-red-100 text-red-800 border-red-200';
            if (score >= 40) return 'bg-yellow-100 text-yellow-800 border-yellow-200';
            return 'bg-green-100 text-green-800 border-green-200';
          };

          return (
            <div
              key={cat.category}
              className={`flex items-center justify-between px-3 py-2 rounded-lg border ${getColor(
                cat.score
              )}`}
            >
              <span className="text-xs font-medium truncate">{cat.category}</span>
              <span className="text-sm font-bold ml-2">{cat.score}</span>
            </div>
          );
        })}
      </div>
    </div>
  );
}
