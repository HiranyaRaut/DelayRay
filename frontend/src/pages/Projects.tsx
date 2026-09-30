import React, { useState, useMemo } from "react";
import { Link, useNavigate, useSearchParams } from "react-router-dom";
import ReactECharts from "echarts-for-react";
import {
  Search,
  Filter,
  Download,
  Eye,
  ArrowRight,
  SlidersHorizontal,
  ChevronLeft,
  ChevronRight,
  ChevronsLeft,
  ChevronsRight,
  RefreshCw,
  FolderKanban,
  Check,
} from "lucide-react";
import { RiskBadge } from "../components/ui/RiskBadge";
import { Drawer } from "../components/ui/Drawer";
import {
  useProjects,
  usePortfolioBreakdown,
  useProjectDetail,
  useProjectSCurve,
} from "../hooks/useApi";
import { formatCurrency, getRiskColor } from "../lib/utils";
import { useAppStore } from "../stores/appStore";

export function Projects() {
  const navigate = useNavigate();
  const [searchParams, setSearchParams] = useSearchParams();
  const theme = useAppStore((s) => s.theme);
  const isDark = theme === "dark";

  // State from URL params or defaults
  const search = searchParams.get("search") || "";
  const sector = searchParams.get("sector") || "";
  const ministry = searchParams.get("ministry") || "";
  const state = searchParams.get("state") || "";
  const riskBand = searchParams.get("risk_band") || "";
  const sortBy = searchParams.get("sort_by") || "risk_score";
  const sortDir = searchParams.get("sort_dir") || "desc";
  const page = parseInt(searchParams.get("page") || "1", 10);
  const pageSize = 20;

  // Local drawer state
  const [peekProjectId, setPeekProjectId] = useState<string | null>(null);

  // Column visibility state
  const [visibleColumns, setVisibleColumns] = useState<Record<string, boolean>>({
    id: true,
    name: true,
    sector: true,
    ministry: true,
    state: true,
    cost: true,
    risk: true,
    var: true,
    delay: true,
    spi: true,
    actions: true,
  });
  const [showColChooser, setShowColChooser] = useState(false);

  // Queries
  const { data: projectsData, isLoading, refetch } = useProjects({
    search: search || undefined,
    sector: sector || undefined,
    ministry: ministry || undefined,
    state: state || undefined,
    risk_band: riskBand || undefined,
    sort_by: sortBy,
    sort_dir: sortDir,
    page,
    page_size: pageSize,
  });

  const { data: sectorOptions } = usePortfolioBreakdown("sector");
  const { data: ministryOptions } = usePortfolioBreakdown("ministry");
  const { data: stateOptions } = usePortfolioBreakdown("state");

  // Quick peek query
  const { data: peekProject } = useProjectDetail(peekProjectId || undefined);
  const { data: peekSCurve } = useProjectSCurve(peekProjectId || undefined);

  // Handlers to update URL
  const updateFilter = (key: string, value: string) => {
    const next = new URLSearchParams(searchParams);
    if (value) {
      next.set(key, value);
    } else {
      next.delete(key);
    }
    next.set("page", "1"); // Reset to page 1 on filter change
    setSearchParams(next);
  };

  const handleSort = (column: string) => {
    const next = new URLSearchParams(searchParams);
    if (sortBy === column) {
      next.set("sort_dir", sortDir === "asc" ? "desc" : "asc");
    } else {
      next.set("sort_by", column);
      next.set("sort_dir", "desc");
    }
    setSearchParams(next);
  };

  // CSV Export handler
  const handleExportCsv = () => {
    if (!projectsData?.items) return;
    const headers = ["Project ID", "Project Name", "Sector", "Ministry", "State", "Sanction Cost (Cr)", "Risk Score", "Risk Band", "VaR (Cr)", "Delay P50 (mo)", "SPI"];
    const rows = projectsData.items.map((p) => [
      `"${p.project_id}"`,
      `"${p.project_name.replace(/"/g, '""')}"`,
      `"${p.sector}"`,
      `"${p.ministry}"`,
      `"${p.primary_state}"`,
      p.original_cost_cr,
      p.risk_score,
      p.risk_band,
      p.value_at_risk_cr,
      p.predicted_delay_months,
      p.spi,
    ]);

    const csvContent = "data:text/csv;charset=utf-8," + [headers.join(","), ...rows.map((e) => e.join(","))].join("\n");
    const encodedUri = encodeURI(csvContent);
    const link = document.createElement("a");
    link.setAttribute("href", encodedUri);
    link.setAttribute("download", `delayray_projects_${new Date().toISOString().slice(0, 10)}.csv`);
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
  };

  // Drawer Mini S-curve
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
      {/* Header */}
      <div className="flex flex-wrap items-center justify-between gap-4 p-6 bg-surface border border-border rounded-xl">
        <div>
          <div className="flex items-center gap-2.5">
            <h1 className="text-2xl font-black text-text tracking-tight">Projects Catalogue</h1>
            <span className="text-[11px] font-mono px-2 py-0.5 rounded bg-raised border border-border text-muted">
              {projectsData?.total ? `${projectsData.total.toLocaleString()} Ongoing` : "1,981 Ongoing"}
            </span>
          </div>
          <p className="text-xs text-muted mt-1">
            Faceted search, calibrated risk scores, cost overruns, and schedule performance across central sector infrastructure.
          </p>
        </div>
        <div className="flex items-center gap-3">
          {/* Column Chooser Button */}
          <div className="relative">
            <button
              onClick={() => setShowColChooser(!showColChooser)}
              className="inline-flex items-center gap-1.5 px-3 py-2 rounded-lg bg-raised hover:bg-raised/80 border border-border text-xs font-semibold text-text transition-colors"
            >
              <SlidersHorizontal className="w-3.5 h-3.5 text-muted" />
              <span>Columns</span>
            </button>
            {showColChooser && (
              <div className="absolute right-0 mt-2 w-48 bg-surface border border-border rounded-xl shadow-xl p-3 z-50 space-y-2 text-xs">
                <div className="font-bold text-text mb-1 pb-1 border-b border-border">Visible Columns</div>
                {Object.entries(visibleColumns).map(([col, val]) => (
                  <label key={col} className="flex items-center gap-2 cursor-pointer hover:text-accent">
                    <input
                      type="checkbox"
                      checked={val}
                      onChange={(e) => setVisibleColumns({ ...visibleColumns, [col]: e.target.checked })}
                      className="rounded border-border text-accent focus:ring-accent"
                    />
                    <span className="capitalize">{col}</span>
                  </label>
                ))}
              </div>
            )}
          </div>

          {/* Export CSV */}
          <button
            onClick={handleExportCsv}
            className="inline-flex items-center gap-1.5 px-3.5 py-2 rounded-lg bg-raised hover:bg-raised/80 border border-border text-xs font-semibold text-text transition-colors"
          >
            <Download className="w-3.5 h-3.5 text-accent" />
            <span>Export CSV</span>
          </button>

          <button
            onClick={() => refetch()}
            className="p-2 rounded-lg bg-raised hover:bg-raised/80 border border-border text-muted hover:text-text"
            title="Refresh Data"
          >
            <RefreshCw className="w-4 h-4" />
          </button>
        </div>
      </div>

      {/* Filter Toolbar */}
      <div className="bg-surface border border-border rounded-xl p-4 space-y-3">
        <div className="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-5 gap-3">
          {/* Search Input */}
          <div className="md:col-span-2 relative">
            <Search className="w-4 h-4 absolute left-3 top-3 text-muted" />
            <input
              type="text"
              placeholder="Search by project name, ID, or agency..."
              value={search}
              onChange={(e) => updateFilter("search", e.target.value)}
              className="w-full pl-9 pr-3 py-2 bg-raised/50 border border-border rounded-lg text-xs text-text placeholder-muted focus:outline-none focus:border-accent"
            />
          </div>

          {/* Sector Filter */}
          <div>
            <select
              value={sector}
              onChange={(e) => updateFilter("sector", e.target.value)}
              className="w-full px-3 py-2 bg-raised/50 border border-border rounded-lg text-xs text-text focus:outline-none focus:border-accent"
            >
              <option value="">All Sectors (22)</option>
              {sectorOptions?.items?.map((s) => (
                <option key={s.dimension_value} value={s.dimension_value}>
                  {s.dimension_value}
                </option>
              ))}
            </select>
          </div>

          {/* Risk Band Filter */}
          <div>
            <select
              value={riskBand}
              onChange={(e) => updateFilter("risk_band", e.target.value)}
              className="w-full px-3 py-2 bg-raised/50 border border-border rounded-lg text-xs text-text focus:outline-none focus:border-accent"
            >
              <option value="">All Risk Bands</option>
              <option value="Critical">Critical (75-100)</option>
              <option value="High">High (50-74)</option>
              <option value="Moderate">Moderate (25-49)</option>
              <option value="Low">Low (0-24)</option>
            </select>
          </div>

          {/* State Filter */}
          <div>
            <select
              value={state}
              onChange={(e) => updateFilter("state", e.target.value)}
              className="w-full px-3 py-2 bg-raised/50 border border-border rounded-lg text-xs text-text focus:outline-none focus:border-accent"
            >
              <option value="">All States / UTs</option>
              {stateOptions?.items?.map((st) => (
                <option key={st.dimension_value} value={st.dimension_value}>
                  {st.dimension_value}
                </option>
              ))}
            </select>
          </div>
        </div>

        {/* Active Filter Chips */}
        {(search || sector || riskBand || state) && (
          <div className="flex items-center gap-2 pt-2 border-t border-border/40 text-xs">
            <span className="text-muted text-[11px] font-semibold">Active filters:</span>
            {search && (
              <span className="px-2 py-0.5 rounded bg-accent/10 border border-accent/30 text-accent flex items-center gap-1">
                Search: {search}
                <button onClick={() => updateFilter("search", "")} className="hover:text-text">×</button>
              </span>
            )}
            {sector && (
              <span className="px-2 py-0.5 rounded bg-accent/10 border border-accent/30 text-accent flex items-center gap-1">
                Sector: {sector}
                <button onClick={() => updateFilter("sector", "")} className="hover:text-text">×</button>
              </span>
            )}
            {riskBand && (
              <span className="px-2 py-0.5 rounded bg-accent/10 border border-accent/30 text-accent flex items-center gap-1">
                Band: {riskBand}
                <button onClick={() => updateFilter("risk_band", "")} className="hover:text-text">×</button>
              </span>
            )}
            {state && (
              <span className="px-2 py-0.5 rounded bg-accent/10 border border-accent/30 text-accent flex items-center gap-1">
                State: {state}
                <button onClick={() => updateFilter("state", "")} className="hover:text-text">×</button>
              </span>
            )}
            <button
              onClick={() => setSearchParams(new URLSearchParams())}
              className="text-[11px] text-muted hover:text-text underline ml-auto"
            >
              Reset All Filters
            </button>
          </div>
        )}
      </div>

      {/* Projects Table */}
      <div className="bg-surface border border-border rounded-xl overflow-hidden">
        <div className="overflow-x-auto">
          <table className="w-full text-left text-xs">
            <thead className="bg-raised/60 border-b border-border text-muted font-bold tracking-wider uppercase text-[10px]">
              <tr>
                {visibleColumns.id && <th className="p-3.5">ID</th>}
                {visibleColumns.name && (
                  <th
                    className="p-3.5 cursor-pointer hover:text-text"
                    onClick={() => handleSort("project_name")}
                  >
                    Project Name {sortBy === "project_name" && (sortDir === "asc" ? "▲" : "▼")}
                  </th>
                )}
                {visibleColumns.sector && <th className="p-3.5">Sector</th>}
                {visibleColumns.state && <th className="p-3.5">State</th>}
                {visibleColumns.cost && (
                  <th
                    className="p-3.5 text-right cursor-pointer hover:text-text"
                    onClick={() => handleSort("original_cost_cr")}
                  >
                    Sanctioned {sortBy === "original_cost_cr" && (sortDir === "asc" ? "▲" : "▼")}
                  </th>
                )}
                {visibleColumns.risk && (
                  <th
                    className="p-3.5 text-center cursor-pointer hover:text-text"
                    onClick={() => handleSort("risk_score")}
                  >
                    Risk Score {sortBy === "risk_score" && (sortDir === "asc" ? "▲" : "▼")}
                  </th>
                )}
                {visibleColumns.var && (
                  <th
                    className="p-3.5 text-right cursor-pointer hover:text-text"
                    onClick={() => handleSort("value_at_risk_cr")}
                  >
                    Value at Risk {sortBy === "value_at_risk_cr" && (sortDir === "asc" ? "▲" : "▼")}
                  </th>
                )}
                {visibleColumns.delay && <th className="p-3.5 text-center">Delay (P50)</th>}
                {visibleColumns.spi && <th className="p-3.5 text-center">SPI</th>}
                {visibleColumns.actions && <th className="p-3.5 text-center">Actions</th>}
              </tr>
            </thead>
            <tbody className="divide-y divide-border/60">
              {isLoading ? (
                Array.from({ length: 8 }).map((_, i) => (
                  <tr key={i} className="animate-pulse">
                    <td colSpan={10} className="p-4 bg-raised/20"></td>
                  </tr>
                ))
              ) : projectsData?.items?.length ? (
                projectsData.items.map((p) => (
                  <tr
                    key={p.project_id}
                    className="hover:bg-raised/40 transition-colors cursor-pointer group"
                    onClick={() => setPeekProjectId(p.project_id)}
                  >
                    {visibleColumns.id && (
                      <td className="p-3.5 font-mono text-[11px] text-muted">{p.project_id}</td>
                    )}
                    {visibleColumns.name && (
                      <td className="p-3.5 font-semibold text-text max-w-[280px]">
                        <div className="truncate group-hover:text-accent transition-colors" title={p.project_name}>
                          {p.project_name}
                        </div>
                        <div className="text-[10px] text-muted truncate">{p.implementing_agency}</div>
                      </td>
                    )}
                    {visibleColumns.sector && (
                      <td className="p-3.5 text-muted truncate max-w-[140px]">{p.sector}</td>
                    )}
                    {visibleColumns.state && (
                      <td className="p-3.5 text-muted truncate max-w-[100px]">{p.primary_state}</td>
                    )}
                    {visibleColumns.cost && (
                      <td className="p-3.5 text-right font-mono font-medium">
                        ₹{p.original_cost_cr.toLocaleString()} Cr
                      </td>
                    )}
                    {visibleColumns.risk && (
                      <td className="p-3.5 text-center">
                        <RiskBadge band={p.risk_band as any} score={p.risk_score} size="sm" />
                      </td>
                    )}
                    {visibleColumns.var && (
                      <td className="p-3.5 text-right font-mono font-bold text-critical">
                        ₹{p.value_at_risk_cr.toLocaleString()} Cr
                      </td>
                    )}
                    {visibleColumns.delay && (
                      <td className="p-3.5 text-center font-mono">
                        +{p.predicted_delay_months || 0}m
                      </td>
                    )}
                    {visibleColumns.spi && (
                      <td className="p-3.5 text-center font-mono">
                        <span className={p.spi < 0.85 ? "text-critical" : "text-text"}>
                          {p.spi?.toFixed(2) || "1.00"}
                        </span>
                      </td>
                    )}
                    {visibleColumns.actions && (
                      <td className="p-3.5 text-center" onClick={(e) => e.stopPropagation()}>
                        <div className="flex items-center justify-center gap-1">
                          <button
                            onClick={() => setPeekProjectId(p.project_id)}
                            className="p-1 rounded hover:bg-raised text-muted hover:text-accent"
                            title="Quick Peek Drawer"
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
                    )}
                  </tr>
                ))
              ) : (
                <tr>
                  <td colSpan={10} className="p-8 text-center text-muted">
                    No infrastructure projects found matching your query criteria.
                  </td>
                </tr>
              )}
            </tbody>
          </table>
        </div>

        {/* Pagination Footer */}
        {projectsData && (
          <div className="p-4 border-t border-border bg-raised/30 flex flex-wrap items-center justify-between gap-4 text-xs text-muted">
            <div>
              Showing{" "}
              <strong className="text-text font-mono">
                {Math.min(projectsData.total, (page - 1) * pageSize + 1)}-
                {Math.min(projectsData.total, page * pageSize)}
              </strong>{" "}
              of <strong className="text-text font-mono">{projectsData.total.toLocaleString()}</strong> projects
            </div>

            <div className="flex items-center gap-1.5">
              <button
                disabled={page <= 1}
                onClick={() => updateFilter("page", "1")}
                className="p-1.5 rounded border border-border bg-surface hover:bg-raised disabled:opacity-40"
                title="First Page"
              >
                <ChevronsLeft className="w-3.5 h-3.5" />
              </button>
              <button
                disabled={page <= 1}
                onClick={() => updateFilter("page", String(page - 1))}
                className="p-1.5 rounded border border-border bg-surface hover:bg-raised disabled:opacity-40"
                title="Previous Page"
              >
                <ChevronLeft className="w-3.5 h-3.5" />
              </button>
              <span className="px-3 py-1 font-mono text-text">
                Page {page} of {projectsData.total_pages || 1}
              </span>
              <button
                disabled={page >= (projectsData.total_pages || 1)}
                onClick={() => updateFilter("page", String(page + 1))}
                className="p-1.5 rounded border border-border bg-surface hover:bg-raised disabled:opacity-40"
                title="Next Page"
              >
                <ChevronRight className="w-3.5 h-3.5" />
              </button>
              <button
                disabled={page >= (projectsData.total_pages || 1)}
                onClick={() => updateFilter("page", String(projectsData.total_pages || 1))}
                className="p-1.5 rounded border border-border bg-surface hover:bg-raised disabled:opacity-40"
                title="Last Page"
              >
                <ChevronsRight className="w-3.5 h-3.5" />
              </button>
            </div>
          </div>
        )}
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
                <span className="text-muted">Expected Overrun (P50)</span>
                <div className="text-base font-bold font-mono text-warning mt-1">
                  +₹{peekProject.expected_overrun_cr?.toLocaleString() || "1,200"} Cr
                </div>
              </div>
            </div>

            <div>
              <h4 className="text-xs font-bold text-text mb-2">Historical Progress Trajectory</h4>
              <div className="h-44 w-full bg-surface border border-border rounded-lg p-2">
                <ReactECharts option={miniSCurveOption} style={{ height: "100%", width: "100%" }} />
              </div>
            </div>

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
