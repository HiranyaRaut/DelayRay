import React from "react";
import { getRiskBand, getRiskColor, cn } from "../../lib/utils";

interface RiskGaugeProps {
  score: number; // 0 - 100
  size?: number; // width/height in px
  showLabel?: boolean;
  className?: string;
}

export function RiskGauge({
  score,
  size = 180,
  showLabel = true,
  className,
}: RiskGaugeProps) {
  const clamped = Math.max(0, Math.min(100, score || 0));
  const band = getRiskBand(clamped);
  const colors = getRiskColor(band);

  // SVG parameters for half-circle arc
  const strokeWidth = 14;
  const radius = (size - strokeWidth * 2) / 2;
  const center = size / 2;
  const circumference = Math.PI * radius;
  const progressOffset = circumference - (clamped / 100) * circumference;

  return (
    <div
      className={cn("flex flex-col items-center justify-center select-none", className)}
      style={{ width: size }}
    >
      <div className="relative" style={{ width: size, height: size / 2 + 18 }}>
        <svg
          width={size}
          height={size / 2 + 10}
          viewBox={`0 0 ${size} ${size / 2 + 10}`}
          className="overflow-visible"
        >
          {/* Background Arc */}
          <path
            d={`M ${strokeWidth} ${center} A ${radius} ${radius} 0 0 1 ${size - strokeWidth} ${center}`}
            fill="none"
            stroke="currentColor"
            strokeWidth={strokeWidth}
            strokeLinecap="round"
            className="text-raised"
          />

          {/* Color Progress Arc */}
          <path
            d={`M ${strokeWidth} ${center} A ${radius} ${radius} 0 0 1 ${size - strokeWidth} ${center}`}
            fill="none"
            stroke={colors.hex}
            strokeWidth={strokeWidth}
            strokeDasharray={circumference}
            strokeDashoffset={progressOffset}
            strokeLinecap="round"
            className="transition-all duration-700 ease-out"
          />
        </svg>

        {/* Center Text Indicator */}
        <div
          className="absolute inset-x-0 bottom-0 flex flex-col items-center justify-center"
          style={{ height: size / 2 }}
        >
          <span className="text-3xl font-extrabold font-mono text-text tracking-tighter">
            {clamped.toFixed(1)}
          </span>
          <span className="text-[11px] font-semibold tracking-wider text-muted uppercase">
            / 100
          </span>
        </div>
      </div>

      {showLabel && (
        <div className="mt-1 flex items-center gap-1.5">
          <span
            className="w-2.5 h-2.5 rounded-full"
            style={{ backgroundColor: colors.hex }}
          ></span>
          <span
            className="text-xs font-bold tracking-wide uppercase"
            style={{ color: colors.hex }}
          >
            {band} Risk
          </span>
        </div>
      )}
    </div>
  );
}
