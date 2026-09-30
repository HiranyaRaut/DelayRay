import React from "react";
import { Search, Filter, X } from "lucide-react";
import { RiskBand } from "../../types";
import { cn } from "../../lib/utils";

interface FacetedFiltersProps {
  search: string;
  onSearchChange: (val: string) => void;
  selectedSector?: string;
  onSectorChange?: (val: string) => void;
  selectedBand?: string;
  onBandChange?: (val: string) => void;
  sectors?: string[];
  onReset?: () => void;
  className?: string;
}

const BANDS: RiskBand[] = ["Low", "Moderate", "High", "Critical"];

export function FacetedFilters({
  search,
  onSearchChange,
  selectedSector = "",
  onSectorChange,
  selectedBand = "",
  onBandChange,
  sectors = [],
  onReset,
  className,
}: FacetedFiltersProps) {
  const hasActiveFilters = Boolean(search || selectedSector || selectedBand);

  return (
    <div
      className={cn(
        "flex flex-wrap items-center justify-between gap-3 p-3 bg-surface border border-border rounded-lg",
        className
      )}
    >
      <div className="flex flex-wrap items-center gap-3 flex-1 min-w-[280px]">
        {/* Search Input */}
        <div className="relative flex-1 min-w-[200px] max-w-sm">
          <Search className="absolute left-3 top-2.5 w-4 h-4 text-muted" />
          <input
            type="text"
            placeholder="Search projects, agency, ID..."
            value={search}
            onChange={(e) => onSearchChange(e.target.value)}
            className="w-full pl-9 pr-3 py-1.5 text-xs bg-raised border border-border rounded-md text-text placeholder:text-muted focus:outline-none focus:border-accent transition-colors"
          />
          {search && (
            <button
              onClick={() => onSearchChange("")}
              className="absolute right-2.5 top-2.5 text-muted hover:text-text"
            >
              <X className="w-3.5 h-3.5" />
            </button>
          )}
        </div>

        {/* Sector Select */}
        {onSectorChange && sectors.length > 0 && (
          <select
            value={selectedSector}
            onChange={(e) => onSectorChange(e.target.value)}
            className="px-3 py-1.5 text-xs bg-raised border border-border rounded-md text-text focus:outline-none focus:border-accent transition-colors cursor-pointer"
          >
            <option value="">All Infrastructure Sectors</option>
            {sectors.map((s) => (
              <option key={s} value={s}>
                {s}
              </option>
            ))}
          </select>
        )}

        {/* Risk Band Filter Chips */}
        {onBandChange && (
          <div className="flex items-center gap-1.5">
            <span className="text-xs text-muted font-medium mr-1">Risk:</span>
            {BANDS.map((b) => {
              const active = selectedBand === b;
              return (
                <button
                  key={b}
                  onClick={() => onBandChange(active ? "" : b)}
                  className={cn(
                    "px-2.5 py-1 text-xs rounded-md border font-medium transition-all select-none",
                    active
                      ? "bg-accent/15 border-accent text-accent shadow-[0_0_8px_rgba(34,211,238,0.2)]"
                      : "bg-raised border-border text-muted hover:text-text hover:bg-raised/80"
                  )}
                >
                  {b}
                </button>
              );
            })}
          </div>
        )}
      </div>

      {hasActiveFilters && onReset && (
        <button
          onClick={onReset}
          className="inline-flex items-center gap-1 px-2.5 py-1.5 text-xs font-medium text-muted hover:text-text bg-raised hover:bg-raised/80 rounded-md border border-border transition-colors"
        >
          <X className="w-3.5 h-3.5" />
          Clear filters
        </button>
      )}
    </div>
  );
}
