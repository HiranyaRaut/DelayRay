import React from "react";
import { Link } from "react-router-dom";
import { FolderKanban, TrendingUp, AlertTriangle, Flame, ArrowRight, Palette } from "lucide-react";
import { KpiTile } from "../components/ui/KpiTile";
import { usePortfolioSummary } from "../hooks/useApi";

export function Dashboard() {
  const { data: summary, isLoading } = usePortfolioSummary();

  return (
    <div className="space-y-8 max-w-7xl mx-auto pb-12">
      {/* Welcome Banner */}
      <div className="flex flex-wrap items-center justify-between gap-4 p-6 bg-surface border border-border rounded-xl">
        <div>
          <h1 className="text-xl font-black text-text tracking-tight">Command Center</h1>
          <p className="text-xs text-muted mt-1">
            Real-time infrastructure predictive analytics & early warning portfolio monitor.
          </p>
        </div>
        <div className="flex items-center gap-3">
          <Link
            to="/dev/components"
            className="inline-flex items-center gap-2 px-3.5 py-2 rounded-lg bg-raised hover:bg-raised/80 border border-border text-xs font-semibold text-text transition-colors"
          >
            <Palette className="w-4 h-4 text-accent" />
            <span>Component Library</span>
          </Link>
          <Link
            to="/projects"
            className="inline-flex items-center gap-2 px-3.5 py-2 rounded-lg bg-accent hover:bg-accent/90 text-background text-xs font-bold transition-all shadow-md shadow-accent/20"
          >
            <span>Explore 1,981 Projects</span>
            <ArrowRight className="w-4 h-4" />
          </Link>
        </div>
      </div>

      {/* KPI Tiles Grid */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
        <KpiTile
          title="Projects Tracked"
          value={summary?.ongoing_projects?.toLocaleString() || "1,981"}
          subtitle="Central Sector ≥ ₹150 Cr"
          icon={FolderKanban}
          loading={isLoading}
        />
        <KpiTile
          title="Total Portfolio Cost"
          value={summary ? `₹${(summary.total_original_cost_cr / 100000).toFixed(2)} Lk Cr` : "₹86.58 Lk Cr"}
          subtitle="Sanctioned Capital"
          icon={TrendingUp}
          variant="accent"
          loading={isLoading}
        />
        <KpiTile
          title="Portfolio Value at Risk"
          value={summary ? `₹${(summary.total_value_at_risk_cr / 100000).toFixed(2)} Lk Cr` : "₹12.64 Lk Cr"}
          subtitle="Empirical at-risk exposure"
          icon={AlertTriangle}
          variant="warning"
          loading={isLoading}
        />
        <KpiTile
          title="Critical Risk Assets"
          value={summary?.critical_risk_count?.toLocaleString() || "1,699"}
          subtitle="Calibrated Score ≥ 75"
          icon={Flame}
          variant="critical"
          loading={isLoading}
        />
      </div>

      {/* Notice Card */}
      <div className="p-4 bg-raised/40 border border-border rounded-xl flex items-center justify-between text-xs text-muted">
        <span>{summary?.advisory_notice || "Risk scores and predictions support human decisions and do not replace them."}</span>
        <span className="font-mono text-[11px]">As-of Date: {summary?.as_of_date || "2026-04-01"}</span>
      </div>
    </div>
  );
}
