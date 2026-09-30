import React from "react";
import { LucideIcon, ArrowUpRight, ArrowDownRight, Minus } from "lucide-react";
import { cn } from "../../lib/utils";

interface KpiTileProps {
  title: string;
  value: string | number;
  subtitle?: string;
  icon?: LucideIcon;
  trend?: {
    value: string | number;
    direction: "up" | "down" | "neutral";
    label?: string;
  };
  variant?: "default" | "critical" | "warning" | "accent";
  loading?: boolean;
  className?: string;
  onClick?: () => void;
}

export function KpiTile({
  title,
  value,
  subtitle,
  icon: Icon,
  trend,
  variant = "default",
  loading = false,
  className,
  onClick,
}: KpiTileProps) {
  if (loading) {
    return (
      <div
        className={cn(
          "bg-surface border border-border rounded-lg p-5 flex flex-col justify-between animate-pulse",
          className
        )}
      >
        <div className="flex justify-between items-start">
          <div className="h-4 bg-muted/20 rounded w-24 mb-3"></div>
          <div className="h-8 w-8 bg-muted/20 rounded-lg"></div>
        </div>
        <div className="h-8 bg-muted/20 rounded w-32 mb-2"></div>
        <div className="h-3 bg-muted/20 rounded w-40"></div>
      </div>
    );
  }

  const borderVariant = {
    default: "border-border hover:border-accent/40",
    critical: "border-red-500/40 shadow-[0_0_15px_rgba(239,68,68,0.15)]",
    warning: "border-yellow-500/40",
    accent: "border-accent/50 shadow-[0_0_15px_rgba(34,211,238,0.15)]",
  }[variant];

  return (
    <div
      onClick={onClick}
      className={cn(
        "bg-surface border rounded-lg p-5 flex flex-col justify-between transition-all duration-200",
        borderVariant,
        onClick && "cursor-pointer hover:bg-raised/70 active:scale-[0.99]",
        className
      )}
    >
      <div className="flex justify-between items-start mb-2">
        <span className="text-xs font-medium text-muted uppercase tracking-wider">
          {title}
        </span>
        {Icon && (
          <div className="p-2 rounded-lg bg-raised border border-border/50 text-accent">
            <Icon className="w-4 h-4" />
          </div>
        )}
      </div>

      <div className="my-1">
        <div className="text-2xl font-bold font-mono tracking-tight text-text tabular-nums">
          {value}
        </div>
      </div>

      <div className="flex items-center justify-between text-xs text-muted mt-2 pt-2 border-t border-border/40">
        <span>{subtitle}</span>
        {trend && (
          <span
            className={cn(
              "inline-flex items-center gap-0.5 font-medium",
              trend.direction === "up" && "text-red-400",
              trend.direction === "down" && "text-emerald-400",
              trend.direction === "neutral" && "text-muted"
            )}
          >
            {trend.direction === "up" && <ArrowUpRight className="w-3.5 h-3.5" />}
            {trend.direction === "down" && <ArrowDownRight className="w-3.5 h-3.5" />}
            {trend.direction === "neutral" && <Minus className="w-3.5 h-3.5" />}
            {trend.value}
          </span>
        )}
      </div>
    </div>
  );
}
