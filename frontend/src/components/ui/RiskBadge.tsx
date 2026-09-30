import React from "react";
import { ShieldCheck, AlertTriangle, AlertCircle, Flame } from "lucide-react";
import { RiskBand } from "../../types";
import { getRiskColor, cn } from "../../lib/utils";

interface RiskBadgeProps {
  band: RiskBand | string;
  score?: number;
  size?: "sm" | "md" | "lg";
  showIcon?: boolean;
  className?: string;
}

export function RiskBadge({
  band,
  score,
  size = "md",
  showIcon = true,
  className,
}: RiskBadgeProps) {
  const normalizedBand = (band || "Low").toString() as RiskBand;
  const colors = getRiskColor(normalizedBand);

  const getIcon = () => {
    switch (normalizedBand.toLowerCase()) {
      case "critical":
        return <Flame className={cn("shrink-0", size === "sm" ? "w-3 h-3" : "w-4 h-4")} />;
      case "high":
        return <AlertCircle className={cn("shrink-0", size === "sm" ? "w-3 h-3" : "w-4 h-4")} />;
      case "moderate":
        return <AlertTriangle className={cn("shrink-0", size === "sm" ? "w-3 h-3" : "w-4 h-4")} />;
      case "low":
      default:
        return <ShieldCheck className={cn("shrink-0", size === "sm" ? "w-3 h-3" : "w-4 h-4")} />;
    }
  };

  const sizeClasses = {
    sm: "px-2 py-0.5 text-xs gap-1 rounded-md",
    md: "px-2.5 py-1 text-xs font-medium gap-1.5 rounded-lg",
    lg: "px-3.5 py-1.5 text-sm font-semibold gap-2 rounded-lg",
  };

  const isCritical = normalizedBand.toLowerCase() === "critical";

  return (
    <span
      className={cn(
        "inline-flex items-center border font-medium transition-all select-none",
        colors.bg,
        colors.text,
        colors.border,
        sizeClasses[size],
        isCritical && "shadow-[0_0_10px_rgba(239,68,68,0.25)] animate-pulse",
        className
      )}
    >
      {showIcon && getIcon()}
      <span>{normalizedBand}</span>
      {score !== undefined && (
        <span className="opacity-80 font-mono font-normal">({score.toFixed(1)})</span>
      )}
    </span>
  );
}
