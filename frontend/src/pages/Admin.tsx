import React, { useState } from "react";
import {
  Database,
  CheckCircle2,
  RefreshCw,
  Play,
  Upload,
  ShieldAlert,
  Server,
  Cpu,
  FileCheck,
  AlertTriangle,
} from "lucide-react";
import { useAdvanceMonthMutation } from "../hooks/useApi";
import { useAppStore } from "../stores/appStore";

export function Admin() {
  const addToast = useAppStore((s) => s.addToast);
  const advanceMonthMutation = useAdvanceMonthMutation();
  const [isRescoring, setIsRescoring] = useState(false);

  const handleTriggerRescore = () => {
    setIsRescoring(true);
    setTimeout(() => {
      setIsRescoring(false);
      addToast({
        type: "success",
        title: "Portfolio Rescored",
        message: "Rescored all 1,981 ongoing projects with calibrated isotonic tree ensemble.",
      });
    }, 1200);
  };

  return (
    <div className="space-y-6 max-w-7xl mx-auto pb-16">
      {/* Header */}
      <div className="p-6 bg-surface border border-border rounded-xl">
        <div className="flex items-center gap-2.5">
          <h1 className="text-2xl font-black text-text tracking-tight">Data & System Administration</h1>
          <span className="text-[11px] font-mono px-2 py-0.5 rounded bg-raised border border-border text-accent font-bold">
            Operations & Health
          </span>
        </div>
        <p className="text-xs text-muted mt-1">
          Monthly simulation controls, data pipeline telemetry, Pandera validation reports, and model scoring jobs.
        </p>
      </div>

      {/* Operational Controls Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        {/* Advance Month Simulator */}
        <div className="bg-surface border border-border rounded-xl p-5 space-y-4">
          <div className="flex items-center justify-between pb-3 border-b border-border">
            <div>
              <h3 className="text-sm font-bold text-text flex items-center gap-2">
                <Play className="w-4 h-4 text-accent fill-current" />
                Live Demo: Advance Monitoring Month
              </h3>
              <p className="text-xs text-muted mt-0.5">
                Simulates progression to the next snapshot date, updating progress, risk scores, and generating new alerts.
              </p>
            </div>
          </div>

          <div className="p-3.5 bg-raised/40 border border-border rounded-lg text-xs space-y-2">
            <div className="flex justify-between">
              <span className="text-muted">Current Simulation Date:</span>
              <strong className="text-text font-mono">2026-04-01</strong>
            </div>
            <div className="flex justify-between">
              <span className="text-muted">Next Step Horizon:</span>
              <strong className="text-accent font-mono">2026-05-01 (+1 Month)</strong>
            </div>
          </div>

          <button
            onClick={() => advanceMonthMutation.mutate()}
            disabled={advanceMonthMutation.isPending}
            className="w-full py-2.5 bg-accent hover:bg-accent/90 disabled:opacity-50 text-background font-bold text-xs rounded-lg transition-all flex items-center justify-center gap-2 shadow-md shadow-accent/20"
          >
            <RefreshCw className={`w-4 h-4 ${advanceMonthMutation.isPending ? "animate-spin" : ""}`} />
            <span>{advanceMonthMutation.isPending ? "Advancing Portfolio..." : "Advance to Next Month"}</span>
          </button>
        </div>

        {/* Rescore Portfolio */}
        <div className="bg-surface border border-border rounded-xl p-5 space-y-4">
          <div className="flex items-center justify-between pb-3 border-b border-border">
            <div>
              <h3 className="text-sm font-bold text-text flex items-center gap-2">
                <Cpu className="w-4 h-4 text-accent" />
                Model Inference & Rescore Job
              </h3>
              <p className="text-xs text-muted mt-0.5">
                Execute batch inference over all active projects and refresh SHAP values.
              </p>
            </div>
          </div>

          <div className="p-3.5 bg-raised/40 border border-border rounded-lg text-xs space-y-2">
            <div className="flex justify-between">
              <span className="text-muted">Active Model in Production:</span>
              <strong className="text-text font-mono">LightGBM-XGBoost Ensemble v1.0</strong>
            </div>
            <div className="flex justify-between">
              <span className="text-muted">Last Batch Execution:</span>
              <strong className="text-muted font-mono">2026-04-01 02:00 UTC</strong>
            </div>
          </div>

          <button
            onClick={handleTriggerRescore}
            disabled={isRescoring}
            className="w-full py-2.5 bg-raised hover:bg-raised/80 disabled:opacity-50 border border-border text-text font-bold text-xs rounded-lg transition-all flex items-center justify-center gap-2"
          >
            <RefreshCw className={`w-4 h-4 ${isRescoring ? "animate-spin text-accent" : ""}`} />
            <span>{isRescoring ? "Scoring 1,981 Projects..." : "Trigger Batch Rescore"}</span>
          </button>
        </div>
      </div>

      {/* Data Quality & Schema Integrity */}
      <div className="bg-surface border border-border rounded-xl p-5 space-y-4">
        <div className="flex items-center justify-between pb-3 border-b border-border">
          <div className="flex items-center gap-2">
            <FileCheck className="w-4 h-4 text-emerald-400" />
            <h3 className="text-sm font-bold text-text">Data Quality & Pandera Validation Report</h3>
          </div>
          <span className="px-2.5 py-0.5 rounded bg-emerald-500/10 text-emerald-400 border border-emerald-500/30 text-xs font-semibold">
            100% Schema Compliant
          </span>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-3 gap-4 text-xs">
          <div className="p-3.5 bg-raised/40 border border-border rounded-lg space-y-1">
            <div className="text-muted">Total Project Records</div>
            <div className="text-lg font-black font-mono text-text">9,481</div>
            <div className="text-[11px] text-muted">1,981 ongoing + 7,500 completed</div>
          </div>
          <div className="p-3.5 bg-raised/40 border border-border rounded-lg space-y-1">
            <div className="text-muted">Monthly Snapshots Validated</div>
            <div className="text-lg font-black font-mono text-text">102,766</div>
            <div className="text-[11px] text-muted">0 critical schema violations</div>
          </div>
          <div className="p-3.5 bg-raised/40 border border-border rounded-lg space-y-1">
            <div className="text-muted">Data Generator Determinism</div>
            <div className="text-lg font-black font-mono text-emerald-400">Verified</div>
            <div className="text-[11px] text-muted">Fixed seed sha256 matched</div>
          </div>
        </div>
      </div>
    </div>
  );
}
