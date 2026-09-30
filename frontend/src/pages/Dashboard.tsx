import React, { useState, useMemo } from "react";
import { Link, useNavigate } from "react-router-dom";
import ReactECharts from "echarts-for-react";
import {
  FolderKanban,
  TrendingUp,
  AlertTriangle,
  Flame,
  ArrowRight,
  ShieldAlert,
  Coins,
  Clock,
  Filter,
  Eye,
  RefreshCw,
  ExternalLink,
  ChevronRight,
  Zap,
} from "lucide-react";
import { KpiTile } from "../components/ui/KpiTile";
import { RiskBadge } from "../components/ui/RiskBadge";
import { ChartWrapper } from "../components/ui/ChartWrapper";
import { Drawer } from "../components/ui/Drawer";
import { RiskGauge } from "../components/ui/RiskGauge";
import {
  usePortfolioSummary,
  usePortfolioBreakdown,
  usePortfolioTrend,
  useRiskRadar,
  useAlerts,
  useProjectDetail,
  useProjectSCurve,
} from "../hooks/useApi";
import { formatCurrency, getRiskColor } from "../lib/utils";
import { useAppStore } from "../stores/appStore";

export function Dashboard() {
  const navigate = useNavigate();
  const theme = useAppStore((s) => s.theme);
  const isDark = theme === "dark";

  // State
  const [selectedSector, setSelectedSector] = useState<string | undefined>(undefined);
  const [brushedProjectIds, setBrushedProjectIds] = useState<string[]>([]);
  const [peekProjectId, setPeekProjectId] = useState<string | null>(null);

  // Queries
  const { data: summary, isLoading: isSummaryLoading, refetch: refetchSummary } = usePortfolioSummary();
  const { data: sectorBreakdown, isLoading: isSectorLoading } = usePortfolioBreakdown("sector");
  const { data: trendData, isLoading: isTrendLoading } = usePortfolioTrend();
  const { data: radarData, isLoading: isRadarLoading } = useRiskRadar(selectedSector);
  const { data: alertsData, isLoading: isAlertsLoading } = useAlerts({ limit: 5, status: "new" });

  // Quick peek data
  const { data: peekProject } = useProjectDetail(peekProjectId || undefined);
  const { data: peekSCurve } = useProjectSCurve(peekProjectId || undefined);

  // Watchlist computation: filter by brushed project IDs if any, else top 10 by VaR
  const watchlist = useMemo(() => {
    if (!radarData?.projects) return [];
    let list = [...radarData.projects];
    if (brushedProjectIds.length > 0) {
      list = list.filter((p) => brushedProjectIds.includes(p.project_id));
    }
    return list.sort((a, b) => b.value_at_risk_cr - a.value_at_risk_cr).slice(0, 10);
  }, [radarData, brushedProjectIds]);

  // Sector list for filter
  const sectors = useMemo(() => {
    if (!sectorBreakdown?.items) return [];
    return sectorBreakdown.items.map((i) => i.dimension_value);
  }, [sectorBreakdown]);

  // ECharts Risk Radar Config
  const radarChartOption = useMemo(() => {
    if (!radarData?.projects) return {};

    const sectorColors: Record<string, string> = {
      Railways: "#22D3EE",
      "Road Transport and Highways": "#F59E0B",
      Power: "#10B981",
      "Petroleum and Natural Gas": "#8B5CF6",
      "Coal and Lignite": "#EC4899",
      "Water Resources": "#3B82F6",
      Default: "#94A3B8",
    };

    const seriesData = radarData.projects.map((p) => [
      p.time_elapsed_pct,
      p.risk_score,
      p.original_cost_cr,
      p.project_name,
      p.sector,
      p.project_id,
      p.risk_band,
      p.value_at_risk_cr,
    ]);

    return {
      backgroundColor: "transparent",
      tooltip: {
        trigger: "item",
        backgroundColor: isDark ? "#111A2E" : "#FFFFFF",
        borderColor: isDark ? "#22304D" : "#E2E8F0",
        textStyle: { color: isDark ? "#E6EDF7" : "#0F172A", fontSize: 12 },
        formatter: (params: any) => {
          const [timeElapsed, score, cost, name, sector, id, band, vAr] = params.data;
          return `
            <div style="font-weight: 700; margin-bottom: 4px; max-width: 260px;">${name}</div>
            <div style="font-size: 11px; color: ${isDark ? '#9FB0C8' : '#64748B'}; margin-bottom: 6px;">
              ${sector} • <span style="font-family: monospace;">${id}</span>
            </div>
            <div style="display: flex; justify-content: space-between; gap: 12px; font-size: 12px;">
              <span>Risk Score:</span>
              <strong style="color: ${getRiskColor(score)}">${score} (${band})</strong>
            </div>
            <div style="display: flex; justify-content: space-between; gap: 12px; font-size: 12px;">
              <span>Time Elapsed:</span>
              <strong>${timeElapsed}%</strong>
            </div>
            <div style="display: flex; justify-content: space-between; gap: 12px; font-size: 12px;">
              <span>Sanctioned Cost:</span>
              <strong>₹${Number(cost).toLocaleString()} Cr</strong>
            </div>
            <div style="display: flex; justify-content: space-between; gap: 12px; font-size: 12px;">
              <span>Value at Risk:</span>
              <strong style="color: #EF4444">₹${Number(vAr).toLocaleString()} Cr</strong>
            </div>
            <div style="font-size: 10px; margin-top: 6px; color: #22D3EE;">Click point to quick-peek</div>
          `;
        },
      },
      grid: { left: 45, right: 30, top: 25, bottom: 45 },
      xAxis: {
        type: "value",
        name: "% Time Elapsed",
        nameLocation: "middle",
        nameGap: 28,
        min: 0,
        max: 100,
        axisLine: { lineStyle: { color: isDark ? "#22304D" : "#CBD5E1" } },
        axisLabel: { color: isDark ? "#9FB0C8" : "#64748B", formatter: "{value}%" },
        splitLine: { lineStyle: { color: isDark ? "#16213A" : "#F1F5F9" } },
      },
      yAxis: {
        type: "value",
        name: "Calibrated Risk Score (0-100)",
        nameLocation: "middle",
        nameGap: 30,
        min: 0,
        max: 100,
        axisLine: { lineStyle: { color: isDark ? "#22304D" : "#CBD5E1" } },
        axisLabel: { color: isDark ? "#9FB0C8" : "#64748B" },
        splitLine: { lineStyle: { color: isDark ? "#16213A" : "#F1F5F9" } },
      },
      brush: {
        toolbox: ["rect", "polygon", "clear"],
        xAxisIndex: 0,
        yAxisIndex: 0,
        brushStyle: {
          borderWidth: 1,
          color: "rgba(34, 211, 238, 0.15)",
          borderColor: "#22D3EE",
        },
      },
      series: [
        {
          name: "Projects",
          type: "scatter",
          data: seriesData,
          symbolSize: (data: any) => {
            const cost = data[2];
            return Math.min(32, Math.max(7, Math.sqrt(cost) * 0.25));
          },
          itemStyle: {
            color: (params: any) => sectorColors[params.data[4]] || sectorColors.Default,
            opacity: 0.85,
            borderColor: isDark ? "#0B1220" : "#FFFFFF",
            borderWidth: 1,
          },
        },
      ],
    };
  }, [radarData, isDark]);

  // ECharts Risk Distribution Donut
  const donutChartOption = useMemo(() => {
    if (!summary) return {};
    return {
      backgroundColor: "transparent",
      tooltip: {
        trigger: "item",
        formatter: "{b}: <strong>{c}</strong> ({d}%)",
        backgroundColor: isDark ? "#111A2E" : "#FFFFFF",
        borderColor: isDark ? "#22304D" : "#E2E8F0",
        textStyle: { color: isDark ? "#E6EDF7" : "#0F172A" },
      },
      legend: {
        bottom: 0,
        textStyle: { color: isDark ? "#9FB0C8" : "#64748B", fontSize: 11 },
        itemWidth: 10,
        itemHeight: 10,
      },
      series: [
        {
          name: "Risk Bands",
          type: "pie",
          radius: ["55%", "80%"],
          center: ["50%", "45%"],
          avoidLabelOverlap: false,
          itemStyle: {
            borderRadius: 6,
            borderColor: isDark ? "#111A2E" : "#FFFFFF",
            borderWidth: 2,
          },
          label: { show: false },
          emphasis: {
            label: {
              show: true,
              fontSize: 14,
              fontWeight: "bold",
              formatter: "{b}\n{c}",
              color: isDark ? "#E6EDF7" : "#0F172A",
            },
          },
          data: [
            { value: summary.critical_risk_count, name: "Critical", itemStyle: { color: "#EF4444" } },
            { value: summary.high_risk_count, name: "High", itemStyle: { color: "#F97316" } },
            { value: summary.moderate_risk_count, name: "Moderate", itemStyle: { color: "#EAB308" } },
            { value: summary.low_risk_count, name: "Low", itemStyle: { color: "#22C55E" } },
          ],
        },
      ],
    };
  }, [summary, isDark]);

  // ECharts Trend Option
  const trendChartOption = useMemo(() => {
    if (!trendData?.trends) return {};
    const months = trendData.trends.map((t) => t.month);
    const avgRisk = trendData.trends.map((t) => t.avg_risk_score);
    const spi = trendData.trends.map((t) => t.avg_spi);

    return {
      backgroundColor: "transparent",
      tooltip: {
        trigger: "axis",
        backgroundColor: isDark ? "#111A2E" : "#FFFFFF",
        borderColor: isDark ? "#22304D" : "#E2E8F0",
        textStyle: { color: isDark ? "#E6EDF7" : "#0F172A" },
      },
      legend: {
        top: 0,
        textStyle: { color: isDark ? "#9FB0C8" : "#64748B", fontSize: 11 },
      },
      grid: { left: 40, right: 40, top: 30, bottom: 25 },
      xAxis: {
        type: "category",
        data: months,
        axisLine: { lineStyle: { color: isDark ? "#22304D" : "#CBD5E1" } },
        axisLabel: { color: isDark ? "#9FB0C8" : "#64748B", fontSize: 10 },
      },
      yAxis: [
        {
          type: "value",
          name: "Risk",
          min: 0,
          max: 100,
          axisLabel: { color: isDark ? "#9FB0C8" : "#64748B" },
          splitLine: { lineStyle: { color: isDark ? "#16213A" : "#F1F5F9" } },
        },
        {
          type: "value",
          name: "SPI",
          min: 0.5,
          max: 1.2,
          axisLabel: { color: isDark ? "#9FB0C8" : "#64748B" },
          splitLine: { show: false },
        },
      ],
      series: [
        {
          name: "Avg Risk Score",
          type: "line",
          data: avgRisk,
          smooth: true,
          itemStyle: { color: "#F97316" },
          lineStyle: { width: 2.5 },
        },
        {
          name: "Avg SPI",
          type: "line",
          yAxisIndex: 1,
          data: spi,
          smooth: true,
          itemStyle: { color: "#22D3EE" },
          lineStyle: { width: 2, type: "dashed" },
        },
      ],
    };
  }, [trendData, isDark]);

  // Top Sectors Bar Option
  const sectorBarOption = useMemo(() => {
    if (!sectorBreakdown?.items) return {};
    const top7 = sectorBreakdown.items.slice(0, 7);
    return {
      backgroundColor: "transparent",
      tooltip: {
        trigger: "axis",
        axisPointer: { type: "shadow" },
        backgroundColor: isDark ? "#111A2E" : "#FFFFFF",
        borderColor: isDark ? "#22304D" : "#E2E8F0",
        textStyle: { color: isDark ? "#E6EDF7" : "#0F172A" },
        formatter: (params: any) => {
          const item = top7[params[0].dataIndex];
          return `
            <strong>${item.dimension_value}</strong><br/>
            Cost: ₹${item.total_cost_cr.toLocaleString()} Cr<br/>
            Avg Risk: ${item.avg_risk_score}<br/>
            Value at Risk: ₹${item.value_at_risk_cr.toLocaleString()} Cr<br/>
            Critical Projects: ${item.critical_count}
          `;
        },
      },
      grid: { left: 130, right: 30, top: 10, bottom: 25 },
      xAxis: {
        type: "value",
        axisLabel: { color: isDark ? "#9FB0C8" : "#64748B", formatter: "₹{value} Cr" },
        splitLine: { lineStyle: { color: isDark ? "#16213A" : "#F1F5F9" } },
      },
      yAxis: {
        type: "category",
        data: top7.map((i) => i.dimension_value).reverse(),
        axisLabel: {
          color: isDark ? "#9FB0C8" : "#64748B",
          fontSize: 10,
          formatter: (val: string) => (val.length > 18 ? val.substring(0, 16) + "…" : val),
        },
      },
      series: [
        {
          type: "bar",
          data: top7.map((i) => i.value_at_risk_cr).reverse(),
          itemStyle: {
            color: "#22D3EE",
            borderRadius: [0, 4, 4, 0],
          },
        },
      ],
    };
  }, [sectorBreakdown, isDark]);

  // Mini S-Curve for quick peek drawer
  const miniSCurveOption = useMemo(() => {
    if (!peekSCurve?.history) return {};
    const historyMonths = peekSCurve.history.map((h: any) => h.month);
    const planned = peekSCurve.history.map((h: any) => h.planned_progress_pct);
    const actual = peekSCurve.history.map((h: any) => h.physical_progress_pct);

    return {
      backgroundColor: "transparent",
      tooltip: { trigger: "axis" },
      grid: { left: 35, right: 15, top: 20, bottom: 25 },
      xAxis: {
        type: "category",
        data: historyMonths,
        axisLabel: { color: isDark ? "#9FB0C8" : "#64748B", fontSize: 9 },
      },
      yAxis: {
        type: "value",
        min: 0,
        max: 100,
        axisLabel: { color: isDark ? "#9FB0C8" : "#64748B", fontSize: 9, formatter: "{value}%" },
        splitLine: { lineStyle: { color: isDark ? "#16213A" : "#F1F5F9" } },
      },
      series: [
        {
          name: "Planned",
          type: "line",
          data: planned,
          lineStyle: { type: "dashed", color: "#94A3B8" },
        },
        {
          name: "Actual",
          type: "line",
          data: actual,
          lineStyle: { width: 2.5, color: "#22D3EE" },
        },
      ],
    };
  }, [peekSCurve, isDark]);

  return (
    <div className="space-y-6 max-w-7xl mx-auto pb-16">
      {/* Alert Ticker Bar */}
      {alertsData?.items && alertsData.items.length > 0 && (
        <div className="bg-raised/70 border border-critical/30 rounded-xl px-4 py-2.5 flex items-center justify-between gap-4 overflow-hidden">
          <div className="flex items-center gap-2 shrink-0">
            <span className="flex h-2 w-2 relative">
              <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-critical opacity-75"></span>
              <span className="relative inline-flex rounded-full h-2 w-2 bg-critical"></span>
            </span>
            <span className="text-xs font-bold uppercase tracking-wider text-critical flex items-center gap-1.5">
              <ShieldAlert className="w-3.5 h-3.5" />
              Live Alerts ({alertsData.total})
            </span>
          </div>
          <div className="flex-1 overflow-hidden">
            <div className="flex items-center gap-3 overflow-x-auto no-scrollbar text-xs">
              {alertsData.items.slice(0, 3).map((a) => (
                <div key={a.id} className="flex items-center gap-1.5 shrink-0 bg-surface/80 px-2.5 py-1 rounded-md border border-border">
                  <RiskBadge band={a.severity as any} size="sm" showIcon={false} />
                  <span className="font-semibold text-text truncate max-w-[240px]">{a.title}</span>
                  <span className="text-muted text-[10px]">{a.project_id}</span>
                </div>
              ))}
            </div>
          </div>
          <Link
            to="/alerts"
            className="shrink-0 text-xs font-semibold text-accent hover:underline flex items-center gap-1"
          >
            <span>Early Warning Center</span>
            <ChevronRight className="w-3.5 h-3.5" />
          </Link>
        </div>
      )}

      {/* Header Banner */}
      <div className="flex flex-wrap items-center justify-between gap-4 p-6 bg-surface border border-border rounded-xl">
        <div>
          <div className="flex items-center gap-2.5">
            <h1 className="text-2xl font-black text-text tracking-tight">Command Center</h1>
            <span className="text-[11px] font-mono px-2 py-0.5 rounded bg-raised border border-border text-muted">
              MoSPI PAIMANA Portfolio
            </span>
          </div>
          <p className="text-xs text-muted mt-1">
            Real-time predictive analytics, value-at-risk exposure, and early warning monitoring across 1,981 central sector projects.
          </p>
        </div>
        <div className="flex items-center gap-3">
          <button
            onClick={() => refetchSummary()}
            className="p-2 rounded-lg bg-raised hover:bg-raised/80 border border-border text-muted hover:text-text transition-colors"
            title="Refresh Portfolio Data"
          >
            <RefreshCw className="w-4 h-4" />
          </button>
          <Link
            to="/projects"
            className="inline-flex items-center gap-2 px-4 py-2 rounded-lg bg-accent hover:bg-accent/90 text-background text-xs font-bold transition-all shadow-md shadow-accent/20"
          >
            <span>View All Projects</span>
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
          loading={isSummaryLoading}
        />
        <KpiTile
          title="Sanctioned Capital"
          value={formatCurrency(summary?.total_original_cost_cr || 8658000)}
          subtitle={`Expenditure: ${formatCurrency(summary?.total_expenditure_to_date_cr || 3636000)}`}
          icon={Coins}
          variant="accent"
          loading={isSummaryLoading}
        />
        <KpiTile
          title="Portfolio Value at Risk"
          value={formatCurrency(summary?.total_value_at_risk_cr || 1264000)}
          subtitle={`Expected Overrun: ${formatCurrency(summary?.total_predicted_overrun_cr || 821000)}`}
          icon={AlertTriangle}
          variant="warning"
          loading={isSummaryLoading}
        />
        <KpiTile
          title="Critical & High Risk"
          value={`${summary?.critical_risk_count || 1699} / ${summary?.high_risk_count || 282}`}
          subtitle={`Avg Risk Score: ${summary?.avg_portfolio_risk_score || 88.5}/100`}
          icon={Flame}
          variant="critical"
          loading={isSummaryLoading}
        />
      </div>

      {/* Risk Radar Hero Section */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        <div className="lg:col-span-2">
          <ChartWrapper
            title="Risk Radar: Progress vs Risk Profile"
            subtitle="Scatter of projects: X = Time Elapsed %, Y = Calibrated Risk Score, Size = Project Cost. Use brush tool or click points."
            loading={isRadarLoading}
            actions={
              <div className="flex items-center gap-2">
                <Filter className="w-3.5 h-3.5 text-muted" />
                <select
                  value={selectedSector || ""}
                  onChange={(e) => setSelectedSector(e.target.value || undefined)}
                  className="bg-surface border border-border rounded text-xs px-2 py-1 text-text focus:outline-none focus:border-accent"
                >
                  <option value="">All 22 Sectors</option>
                  {sectors.map((s) => (
                    <option key={s} value={s}>
                      {s}
                    </option>
                  ))}
                </select>
              </div>
            }
          >
            <div className="h-96 w-full">
              <ReactECharts
                option={radarChartOption}
                style={{ height: "100%", width: "100%" }}
                onEvents={{
                  click: (params: any) => {
                    if (params.data && params.data[5]) {
                      setPeekProjectId(params.data[5]);
                    }
                  },
                  brushselected: (params: any) => {
                    const brushComponent = params.batch?.[0];
                    if (brushComponent?.selected?.[0]?.dataIndex) {
                      const indices = brushComponent.selected[0].dataIndex;
                      if (radarData?.projects) {
                        const selectedIds = indices.map((idx: number) => radarData.projects[idx]?.project_id);
                        setBrushedProjectIds(selectedIds);
                      }
                    } else {
                      setBrushedProjectIds([]);
                    }
                  },
                }}
              />
            </div>
            {brushedProjectIds.length > 0 && (
              <div className="mt-2 text-xs flex items-center justify-between bg-accent/10 border border-accent/30 px-3 py-1.5 rounded-lg text-accent">
                <span>Brushed selection: {brushedProjectIds.length} projects highlighted in Top Watchlist below</span>
                <button
                  onClick={() => setBrushedProjectIds([])}
                  className="underline hover:text-text text-[11px]"
                >
                  Clear Selection
                </button>
              </div>
            )}
          </ChartWrapper>
        </div>

        {/* Risk Distribution Donut & Month Trend */}
        <div className="space-y-6">
          <ChartWrapper
            title="Portfolio Risk Distribution"
            subtitle="Calibrated 0-100 score bands across 1,981 projects"
            loading={isSummaryLoading}
          >
            <div className="h-44 w-full">
              <ReactECharts option={donutChartOption} style={{ height: "100%", width: "100%" }} />
            </div>
          </ChartWrapper>

          <ChartWrapper
            title="Monthly Risk & SPI Trajectory"
            subtitle="12-month rolling average risk vs Schedule Performance"
            loading={isTrendLoading}
          >
            <div className="h-44 w-full">
              <ReactECharts option={trendChartOption} style={{ height: "100%", width: "100%" }} />
            </div>
          </ChartWrapper>
        </div>
      </div>

      {/* Sector VaR & Watchlist */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Sector Exposure */}
        <div className="lg:col-span-1">
          <ChartWrapper
            title="Value at Risk by Sector"
            subtitle="Top infrastructure sectors ranked by financial exposure"
            loading={isSectorLoading}
          >
            <div className="h-80 w-full">
              <ReactECharts option={sectorBarOption} style={{ height: "100%", width: "100%" }} />
            </div>
          </ChartWrapper>
        </div>

        {/* Top Watchlist Table */}
        <div className="lg:col-span-2">
          <div className="bg-surface border border-border rounded-xl p-5 flex flex-col justify-between h-full">
            <div>
              <div className="flex items-center justify-between mb-4">
                <div>
                  <h3 className="text-sm font-bold text-text">Top-10 Watchlist (Ranked by Value at Risk)</h3>
                  <p className="text-xs text-muted">
                    {brushedProjectIds.length > 0
                      ? `Filtered by radar selection (${brushedProjectIds.length} projects)`
                      : "Highest financial exposure requiring urgent intervention"}
                  </p>
                </div>
                <Link
                  to="/projects?sort_by=value_at_risk_cr&sort_dir=desc"
                  className="text-xs text-accent hover:underline flex items-center gap-1 font-semibold"
                >
                  <span>All Filtered</span>
                  <ExternalLink className="w-3 h-3" />
                </Link>
              </div>

              <div className="overflow-x-auto">
                <table className="w-full text-left text-xs">
                  <thead className="border-b border-border text-muted font-semibold">
                    <tr>
                      <th className="pb-2.5">Project</th>
                      <th className="pb-2.5">Sector</th>
                      <th className="pb-2.5 text-center">Risk Score</th>
                      <th className="pb-2.5 text-right">Cost (Cr)</th>
                      <th className="pb-2.5 text-right">Value at Risk</th>
                      <th className="pb-2.5 text-center">Actions</th>
                    </tr>
                  </thead>
                  <tbody className="divide-y divide-border/50">
                    {watchlist.map((p) => (
                      <tr key={p.project_id} className="hover:bg-raised/40 transition-colors group">
                        <td className="py-2.5 pr-2">
                          <div className="font-semibold text-text truncate max-w-[200px]" title={p.project_name}>
                            {p.project_name}
                          </div>
                          <div className="text-[10px] font-mono text-muted">{p.project_id}</div>
                        </td>
                        <td className="py-2.5 text-muted truncate max-w-[120px]">{p.sector}</td>
                        <td className="py-2.5 text-center">
                          <RiskBadge band={p.risk_band as any} score={p.risk_score} size="sm" />
                        </td>
                        <td className="py-2.5 text-right font-mono">₹{p.original_cost_cr.toLocaleString()}</td>
                        <td className="py-2.5 text-right font-mono font-bold text-critical">
                          ₹{p.value_at_risk_cr.toLocaleString()}
                        </td>
                        <td className="py-2.5 text-center">
                          <div className="flex items-center justify-center gap-1.5">
                            <button
                              onClick={() => setPeekProjectId(p.project_id)}
                              className="p-1 rounded hover:bg-raised text-muted hover:text-accent"
                              title="Quick Peek"
                            >
                              <Eye className="w-3.5 h-3.5" />
                            </button>
                            <Link
                              to={`/projects/${p.project_id}`}
                              className="p-1 rounded hover:bg-raised text-muted hover:text-text"
                              title="Open Project Hero"
                            >
                              <ArrowRight className="w-3.5 h-3.5" />
                            </Link>
                          </div>
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            </div>

            <div className="pt-3 border-t border-border/40 flex items-center justify-between text-[11px] text-muted">
              <span>Showing top {watchlist.length} projects</span>
              <span className="font-mono">As of 2026-04 snapshot</span>
            </div>
          </div>
        </div>
      </div>

      {/* Quick Peek Drawer */}
      <Drawer
        open={!!peekProjectId}
        onClose={() => setPeekProjectId(null)}
        title={peekProject?.project_name || "Project Quick Peek"}
        width="w-[500px]"
      >
        {peekProject ? (
          <div className="space-y-6">
            {/* Quick KPI Header */}
            <div className="flex items-center justify-between p-4 bg-raised/50 border border-border rounded-xl">
              <div>
                <span className="text-xs text-muted font-mono">{peekProject.project_id}</span>
                <div className="text-sm font-bold text-text mt-0.5">{peekProject.sector}</div>
                <div className="text-xs text-muted">{peekProject.ministry}</div>
              </div>
              <div className="flex flex-col items-end">
                <RiskBadge band={peekProject.risk_band} size="md" />
                <span className="text-xs font-mono font-bold mt-1 text-text">
                  Score: {peekProject.risk_score}/100
                </span>
              </div>
            </div>

            {/* Financial Metrics */}
            <div className="grid grid-cols-2 gap-3 text-xs">
              <div className="p-3 bg-surface border border-border rounded-lg">
                <span className="text-muted">Sanctioned Cost</span>
                <div className="text-base font-bold font-mono mt-1">
                  ₹{peekProject.original_cost_cr.toLocaleString()} Cr
                </div>
              </div>
              <div className="p-3 bg-surface border border-border rounded-lg">
                <span className="text-muted">Value at Risk</span>
                <div className="text-base font-bold font-mono text-critical mt-1">
                  ₹{peekProject.value_at_risk_cr.toLocaleString()} Cr
                </div>
              </div>
              <div className="p-3 bg-surface border border-border rounded-lg">
                <span className="text-muted">Expected Delay (P50)</span>
                <div className="text-base font-bold font-mono mt-1">
                  +{peekProject.delay_p50 || 18} months
                </div>
              </div>
              <div className="p-3 bg-surface border border-border rounded-lg">
                <span className="text-muted">Schedule Performance (SPI)</span>
                <div className="text-base font-bold font-mono text-accent mt-1">
                  {peekProject.spi?.toFixed(2) || "0.82"}
                </div>
              </div>
            </div>

            {/* Mini S-Curve Chart */}
            <div>
              <h4 className="text-xs font-bold text-text mb-2">Historical Progress Trajectory</h4>
              <div className="h-44 w-full bg-surface border border-border rounded-lg p-2">
                <ReactECharts option={miniSCurveOption} style={{ height: "100%", width: "100%" }} />
              </div>
            </div>

            {/* Action Button */}
            <div className="pt-2">
              <button
                onClick={() => {
                  const id = peekProjectId;
                  setPeekProjectId(null);
                  navigate(`/projects/${id}`);
                }}
                className="w-full py-2.5 bg-accent hover:bg-accent/90 text-background font-bold text-xs rounded-lg transition-all flex items-center justify-center gap-2"
              >
                <span>Open Full Project Hero Page</span>
                <ArrowRight className="w-4 h-4" />
              </button>
            </div>
          </div>
        ) : (
          <div className="p-8 text-center text-xs text-muted">Loading project telemetry...</div>
        )}
      </Drawer>
    </div>
  );
}
