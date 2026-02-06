'use client';

/**
 * RiskGauge Component
 *
 * Displays a radial gauge showing risk score from 0-100
 * Color-coded: Green (0-39), Yellow (40-69), Red (70-100)
 */

import { useEffect, useState } from 'react';

interface RiskGaugeProps {
  score: number; // 0-100
  size?: 'small' | 'medium' | 'large';
  showLabel?: boolean;
  animated?: boolean;
}

export default function RiskGauge({
  score,
  size = 'large',
  showLabel = true,
  animated = true,
}: RiskGaugeProps) {
  const [displayScore, setDisplayScore] = useState(animated ? 0 : score);

  // Animate score on mount
  useEffect(() => {
    if (animated) {
      const duration = 1500; // 1.5 seconds
      const steps = 60;
      const increment = score / steps;
      let current = 0;

      const timer = setInterval(() => {
        current += increment;
        if (current >= score) {
          setDisplayScore(score);
          clearInterval(timer);
        } else {
          setDisplayScore(Math.round(current));
        }
      }, duration / steps);

      return () => clearInterval(timer);
    }
  }, [score, animated]);

  // Determine color based on score
  const getColor = (value: number) => {
    if (value >= 70) return { main: '#dc2626', light: '#fecaca', text: 'text-red-600' }; // Red
    if (value >= 40) return { main: '#eab308', light: '#fef08a', text: 'text-yellow-600' }; // Yellow
    return { main: '#16a34a', light: '#bbf7d0', text: 'text-green-600' }; // Green
  };

  // Get risk label
  const getRiskLabel = (value: number) => {
    if (value >= 70) return 'High Risk';
    if (value >= 40) return 'Medium Risk';
    return 'Low Risk';
  };

  const color = getColor(displayScore);
  const riskLabel = getRiskLabel(displayScore);

  // Size configurations
  const sizeConfig = {
    small: { width: 120, height: 120, strokeWidth: 8, fontSize: 'text-2xl' },
    medium: { width: 180, height: 180, strokeWidth: 12, fontSize: 'text-4xl' },
    large: { width: 240, height: 240, strokeWidth: 16, fontSize: 'text-5xl' },
  };

  const config = sizeConfig[size];
  const radius = (config.width - config.strokeWidth) / 2;
  const circumference = 2 * Math.PI * radius;
  const strokeDashoffset = circumference - (displayScore / 100) * circumference;

  return (
    <div className="flex flex-col items-center">
      <div className="relative" style={{ width: config.width, height: config.height }}>
        {/* Background Circle */}
        <svg
          width={config.width}
          height={config.height}
          className="transform -rotate-90"
        >
          <circle
            cx={config.width / 2}
            cy={config.height / 2}
            r={radius}
            stroke={color.light}
            strokeWidth={config.strokeWidth}
            fill="none"
          />
          {/* Progress Circle */}
          <circle
            cx={config.width / 2}
            cy={config.height / 2}
            r={radius}
            stroke={color.main}
            strokeWidth={config.strokeWidth}
            fill="none"
            strokeDasharray={circumference}
            strokeDashoffset={strokeDashoffset}
            strokeLinecap="round"
            className="transition-all duration-300 ease-out"
          />
        </svg>

        {/* Center Score */}
        <div className="absolute inset-0 flex flex-col items-center justify-center">
          <div className={`${config.fontSize} font-bold ${color.text}`}>
            {displayScore}
          </div>
          <div className="text-xs text-gray-500 mt-1">Risk Score</div>
        </div>
      </div>

      {/* Label */}
      {showLabel && (
        <div className="mt-4 text-center">
          <div className={`text-lg font-semibold ${color.text}`}>
            {riskLabel}
          </div>
          <div className="text-sm text-gray-500 mt-1">
            {displayScore < 40
              ? 'Company shows healthy financial indicators'
              : displayScore < 70
              ? 'Some concerns detected, requires attention'
              : 'Multiple red flags detected, high caution advised'}
          </div>
        </div>
      )}
    </div>
  );
}
