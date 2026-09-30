import React, { useMemo } from "react";
import ReactECharts from "echarts-for-react";
import {
  Scale,
  Layers,
  ArrowRight,
  TrendingUp,
  BarChart3,
  CheckCircle2,
  Filter,
} from "lucide-react";
import { ChartWrapper } from "../components/ui/ChartWrapper";
import { usePortfolioBreakdown } from "../hooks/useApi";
import { useAppStore } from "../stores/appStore";

export function Benchmarking() {
  const theme = useAppStore((s) => s.theme);
  const isDark = theme === "dark";
  const { data: sectorBreakdown, isLoading } = usePortfolioBreakdown("sector");

  // Sector Boxplot / Comparison ECharts
  const sectorComparisonOption = useMemo(() => {
    if (!sectorBreakdown?.items) return {};
    const items = sectorBreakdown.items.slice(0, 8);
    const sectors = items.map((i) => i.dimension_value);
    const avgRisks = items.map((i) => i.avg_risk_score);
    const critCounts = items.map((i) => i.critical_count);

    return {
      backgroundColor: "transparent",
      tooltip: { trigger: "axis" },
      legend: {
        bottom: 0,
        textStyle: { color: isDark ? "#9FB0C8" : "#64748B", fontSize: 11 },
      },
      grid: { left: 45, right: 35, top: 20, bottom: 50 },
      xAxis: {
        type: "category",
        data: sectors,
        axisLine: { lineStyle: { color: isDark ? "#22304D" : "#CBD5E1" } },
        axisLabel: {
          color: isDark ? "#9FB0C8" : "#64748B",
          fontSize: 10,
          rotate: 20,
          formatter: (v: string) => (v.length > 18 ? v.substring(0, 16) + "…" : v),
        },
      },
      yAxis: [
        {
          type: "value",
          name: "Average Risk Score",
          min: 0,
          max: 100,
          axisLabel: { color: isDark ? "#9FB0C8" : "#64748B" },
          splitLine: { lineStyle: { color: isDark ? "#16213A" : "#F1F5F9" } },
        },
        {
          type: "value",
          name: "Critical Projects Count",
          axisLabel: { color: isDark ? "#9FB0C8" : "#64748B" },
          splitLine: { show: false },
        },
      ],
      series: [
        {
          name: "Average Risk Score",
          type: "bar",
          data: avgRisks,
          itemStyle: { color: "#22D3EE", borderRadius: [4, 4, 0, 0] },
        },
        {
          name: "Critical Risk Projects",
          type: "line",
          yAxisIndex: 1,
          data: critCounts,
          lineStyle: { width: 2.5, color: "#EF4444" },
          itemStyle: { color: "#EF4444" },
        },
      ],
    };
  }, [sectorBreakdown, isDark]);

  return (
    <div className="space-y-6 max-w-7xl mx-auto pb-16">
      {/* Header */}
      <div className="p-6 bg-surface border border-border rounded-xl">
        <div className="flex items-center gap-2.5">
          <h1 className="text-2xl font-black text-text tracking-tight">Portfolio Cohort Benchmarking</h1>
          <span className="text-[11px] font-mono px-2 py-0.5 rounded bg-raised border border-border text-accent font-bold">
            Cross-Sector Analytics
          </span>
        </div>
        <p className="text-xs text-muted mt-1">
          Comparative risk baselines, delay distributions, and execution efficiency across infrastructure sector cohorts.
        </p>
      </div>

      {/* Sector Risk & Critical Count Benchmark */}
      <ChartWrapper
        title="Sector Risk & Critical Project Load Comparison"
        subtitle="Average calibrated risk index vs volume of critical infrastructure assets across top sectors"
        loading={isLoading}
      >
        <div className="h-80 w-full">
          <ReactECharts option={sectorComparisonOption} style={{ height: "100%", width: "100%" }} />
        </div>
      </ChartWrapper>

      {/* Sector Cohort Summary Table */}
      <div className="bg-surface border border-border rounded-xl overflow-hidden">
        <div className="p-4 border-b border-border bg-raised/30 flex items-center justify-between">
          <div className="flex items-center gap-2">
            <Layers className="w-4 h-4 text-accent" />
            <h3 className="text-sm font-bold text-text">Infrastructure Sector Cohorts</h3>
          </div>
          <span className="text-[11px] text-muted font-mono">Ranked by Total Capital Exposure</span>
        </div>

        <div className="overflow-x-auto">
          <table className="w-full text-left text-xs">
            <thead className="bg-raised/60 border-b border-border text-muted font-bold text-[10px] uppercase">
              <tr>
                <th className="p-3.5">Sector</th>
                <th className="p-3.5 text-center">Projects</th>
                <th className="p-3.5 text-right">Total Cost</th>
                <th className="p-3.5 text-right">Value at Risk</th>
                <th className="p-3.5 text-center">Avg Risk Score</th>
                <th className="p-3.5 text-center">Critical Assets</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-border/60">
              {sectorBreakdown?.items?.map((item, idx) => (
                <tr key={idx} className="hover:bg-raised/40 transition-colors">
                  <td className="p-3.5 font-semibold text-text">{item.dimension_value}</td>
                  <td className="p-3.5 text-center font-mono">{item.project_count}</td>
                  <td className="p-3.5 text-right font-mono">₹{item.total_cost_cr.toLocaleString()} Cr</td>
                  <td className="p-3.5 text-right font-mono font-bold text-critical">
                    ₹{item.value_at_risk_cr.toLocaleString()} Cr
                  </td>
                  <td className="p-3.5 text-center font-mono font-bold text-accent">
                    {item.avg_risk_score}
                  </td>
                  <td className="p-3.5 text-center font-mono">
                    <span className="px-2 py-0.5 rounded bg-critical/10 text-critical font-bold">
                      {item.critical_count}
                    </span>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
}
