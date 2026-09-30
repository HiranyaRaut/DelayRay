import React from "react";
import { AlertCircle, RefreshCw, BarChart3 } from "lucide-react";
import { cn } from "../../lib/utils";

interface ChartWrapperProps {
  title: string;
  subtitle?: string;
  actions?: React.ReactNode;
  loading?: boolean;
  empty?: boolean;
  emptyMessage?: string;
  error?: string | null;
  onRetry?: () => void;
  children: React.ReactNode;
  className?: string;
  height?: string | number;
}

export function ChartWrapper({
  title,
  subtitle,
  actions,
  loading = false,
  empty = false,
  emptyMessage = "No data available for the selected filters.",
  error = null,
  onRetry,
  children,
  className,
  height = 320,
}: ChartWrapperProps) {
  return (
    <div
      className={cn(
        "bg-surface border border-border rounded-lg p-5 flex flex-col justify-between transition-colors",
        className
      )}
    >
      <div className="flex flex-wrap items-center justify-between gap-3 mb-4">
        <div>
          <h3 className="text-sm font-semibold text-text tracking-tight">{title}</h3>
          {subtitle && <p className="text-xs text-muted mt-0.5">{subtitle}</p>}
        </div>
        {actions && <div className="flex items-center gap-2">{actions}</div>}
      </div>

      <div
        className="relative w-full flex items-center justify-center overflow-hidden"
        style={{ height }}
      >
        {loading ? (
          <div className="w-full h-full flex flex-col items-center justify-center gap-3 animate-pulse bg-raised/40 rounded-lg">
            <div className="w-10 h-10 rounded-full border-2 border-accent border-t-transparent animate-spin" />
            <span className="text-xs text-muted">Rendering chart intelligence...</span>
          </div>
        ) : error ? (
          <div className="w-full h-full flex flex-col items-center justify-center p-6 text-center bg-red-500/5 rounded-lg border border-red-500/20">
            <AlertCircle className="w-8 h-8 text-red-500 mb-2" />
            <p className="text-xs font-semibold text-red-400 mb-1">Failed to load chart</p>
            <p className="text-xs text-muted max-w-sm mb-3">{error}</p>
            {onRetry && (
              <button
                onClick={onRetry}
                className="inline-flex items-center gap-1.5 px-3 py-1.5 text-xs font-medium text-text bg-raised hover:bg-raised/80 rounded-md border border-border transition-colors"
              >
                <RefreshCw className="w-3.5 h-3.5" />
                Retry
              </button>
            )}
          </div>
        ) : empty ? (
          <div className="w-full h-full flex flex-col items-center justify-center p-6 text-center bg-raised/30 rounded-lg">
            <BarChart3 className="w-8 h-8 text-muted mb-2 opacity-50" />
            <p className="text-xs font-medium text-muted">{emptyMessage}</p>
          </div>
        ) : (
          <div className="w-full h-full">{children}</div>
        )}
      </div>
    </div>
  );
}
