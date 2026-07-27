import React from 'react';

interface ConversionGaugeProps {
  rate: number;
  chamber: 'house' | 'senate';
  size?: number;
}

export const ConversionGauge: React.FC<ConversionGaugeProps> = ({
  rate,
  chamber,
  size = 64
}) => {
  const isHouse = chamber === 'house';
  const strokeWidth = 6;
  const radius = (size - strokeWidth) / 2;
  const circumference = 2 * Math.PI * radius;
  const strokeDashoffset = circumference - (rate / 100) * circumference;

  const colorClass = isHouse ? 'text-emerald-500' : 'text-rose-500';
  const bgStrokeClass = isHouse ? 'text-emerald-950/20 dark:text-emerald-950/40' : 'text-rose-950/20 dark:text-rose-950/40';

  return (
    <div className="relative inline-flex items-center justify-center">
      <svg width={size} height={size} className="transform -rotate-90">
        {/* Track Background */}
        <circle
          cx={size / 2}
          cy={size / 2}
          r={radius}
          stroke="currentColor"
          strokeWidth={strokeWidth}
          fill="transparent"
          className={bgStrokeClass}
        />
        {/* Progress Arc */}
        <circle
          cx={size / 2}
          cy={size / 2}
          r={radius}
          stroke="currentColor"
          strokeWidth={strokeWidth}
          fill="transparent"
          strokeDasharray={circumference}
          strokeDashoffset={strokeDashoffset}
          strokeLinecap="round"
          className={`${colorClass} transition-all duration-700 ease-out`}
        />
      </svg>
      {/* Center Text */}
      <div className="absolute inset-0 flex flex-col items-center justify-center text-center">
        <span className="text-xs font-bold tracking-tighter text-slate-900 dark:text-white">
          {rate}%
        </span>
      </div>
    </div>
  );
};
