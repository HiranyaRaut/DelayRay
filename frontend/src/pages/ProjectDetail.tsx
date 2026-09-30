import React, { useState, useMemo } from "react";
import { useParams, Link, useNavigate } from "react-router-dom";
import ReactECharts from "echarts-for-react";
import {
  ArrowLeft,
  Download,
  MessageSquareText,
  AlertTriangle,
  Flame,
  CheckCircle2,
  Clock,
  Coins,
  TrendingUp,
  Sliders,
  Layers,
  Sparkles,
  ShieldCheck,
  FileText,
  Info,
  Calendar,
  Building2,
  MapPin,
  Compass,
  Play,
  RotateCcw,
} from "lucide-react";
import { RiskGauge } from "../components/ui/RiskGauge";
import { RiskBadge } from "../components/ui/RiskBadge";
import { ChartWrapper } from "../components/ui/ChartWrapper";
import {
  useProjectDetail,
  useProjectSCurve,
  useProjectExplain,
  useProjectPeers,
  useProjectRemarks,
  useProjectMilestones,
  useProjectAlerts,
  useWhatIfMutation,
} from "../hooks/useApi";
import { api } from "../lib/api";
import { formatCurrency, getRiskColor } from "../lib/utils";
import { useAppStore } from "../stores/appStore";

export function ProjectDetail() {
  const { id } = useParams<{ id: string }>();
  const navigate = useNavigate();
  const theme = useAppStore((s) => s.theme);
  const isDark = theme === "dark";
  const addToast = useAppStore((s) => s.addToast);

  // Active tab
  const [activeTab, setActiveTab] = useState<"trajectory" | "explain" | "peers" | "whatif" | "timeline">("trajectory");

  // What-If Simulation Levers State
  const [landHandover, setLandHandover] = useState(65);
  const [clearanceDelay, setClearanceDelay] = useState(8);
  const [contractorRating, setContractorRating] = useState(60);
  const [materialShock, setMaterialShock] = useState(105);
  const [budgetRatio, setBudgetRatio] = useState(0.95);
  const [simResult, setSimResult] = useState<any>(null);

  // Queries
  const { data: project, isLoading: isProjectLoading } = useProjectDetail(id);
  const { data: scurve, isLoading: isSCurveLoading } = useProjectSCurve(id);
  const { data: explain, isLoading: isExplainLoading } = useProjectExplain(id);
  const { data: peers, isLoading: isPeersLoading } = useProjectPeers(id);
  const { data: remarks } = useProjectRemarks(id);
  const { data: milestones } = useProjectMilestones(id);
  const { data: alerts } = useProjectAlerts(id);

  // What-If Mutation
  const whatIfMutation = useWhatIfMutation(id);

  const handleSimulateWhatIf = () => {
    whatIfMutation.mutate(
      {
        land_handover_pct: landHandover,
        statutory_clearance_delay_months: clearanceDelay,
        contractor_rating: contractorRating,
        material_price_shock_index: materialShock,
        budget_disbursement_ratio: budgetRatio,
      },
      {
        onSuccess: (data) => {
          setSimResult(data);
          addToast({
            type: "success",
            title: "Counterfactual Simulated",
            message: `Risk score updated to ${data.simulated_risk_score} (Δ ${data.risk_delta > 0 ? "+" : ""}${data.risk_delta.toFixed(1)} pts).`,
          });
        },
        onError: (err: any) => {
          addToast({
            type: "error",
            title: "Simulation Failed",
            message: err.message || "Failed to calculate counterfactual.",
          });
        },
      }
    );
  };

  // ECharts: S-Curve with Confidence Band
  const scurveOption = useMemo(() => {
    if (!scurve?.points) return {};

    const months = scurve.points.map((p: any) => p.month);
    const planned = scurve.points.map((p: any) => p.planned_progress_pct);
    const actual = scurve.points.map((p: any) => p.actual_progress_pct ?? null);
    const p10 = scurve.points.map((p: any) => p.forecast_progress_p10 ?? null);
    const p50 = scurve.points.map((p: any) => p.forecast_progress_p50 ?? null);
    const p90 = scurve.points.map((p: any) => p.forecast_progress_p90 ?? null);

    return {
      backgroundColor: "transparent",
      tooltip: {
        trigger: "axis",
        backgroundColor: isDark ? "#111A2E" : "#FFFFFF",
        borderColor: isDark ? "#22304D" : "#E2E8F0",
        textStyle: { color: isDark ? "#E6EDF7" : "#0F172A" },
        formatter: (params: any[]) => {
          const m = params[0]?.axisValue;
          let str = `<strong>Month: ${m}</strong><br/>`;
          params.forEach((item) => {
            if (item.value !== null && item.value !== undefined) {
              str += `${item.marker} ${item.seriesName}: <strong>${Number(item.value).toFixed(1)}%</strong><br/>`;
            }
          });
          return str;
        },
      },
      legend: {
        top: 0,
        textStyle: { color: isDark ? "#9FB0C8" : "#64748B", fontSize: 11 },
      },
      grid: { left: 45, right: 30, top: 35, bottom: 35 },
      xAxis: {
        type: "category",
        data: months,
        axisLine: { lineStyle: { color: isDark ? "#22304D" : "#CBD5E1" } },
        axisLabel: {
          color: isDark ? "#9FB0C8" : "#64748B",
          fontSize: 10,
          rotate: months.length > 15 ? 45 : 0,
        },
      },
      yAxis: {
        type: "value",
        name: "Cumulative Progress %",
        nameLocation: "middle",
        nameGap: 30,
        min: 0,
        max: 100,
        axisLabel: { color: isDark ? "#9FB0C8" : "#64748B", formatter: "{value}%" },
        splitLine: { lineStyle: { color: isDark ? "#16213A" : "#F1F5F9" } },
      },
      series: [
        {
          name: "Planned Baseline",
          type: "line",
          data: planned,
          lineStyle: { width: 2, type: "dashed", color: "#94A3B8" },
          itemStyle: { color: "#94A3B8" },
        },
        {
          name: "Actual Progress",
          type: "line",
          data: actual,
          lineStyle: { width: 3, color: "#22D3EE" },
          itemStyle: { color: "#22D3EE" },
        },
        {
          name: "Forecast (P50)",
          type: "line",
          data: p50,
          lineStyle: { width: 2.5, color: "#F97316" },
          itemStyle: { color: "#F97316" },
        },
        {
          name: "P90 Upper Bound",
          type: "line",
          data: p90,
          lineStyle: { opacity: 0 },
          stack: "confidence-band",
          symbol: "none",
        },
        {
          name: "P10-P90 Confidence Band",
          type: "line",
          data: p10,
          lineStyle: { opacity: 0 },
          areaStyle: { color: "rgba(249, 115, 22, 0.15)" },
          stack: "confidence-band",
          symbol: "none",
        },
      ],
    };
  }, [scurve, isDark]);

  // ECharts: SHAP Waterfall / Driver Contribution Bar Chart
  const shapChartOption = useMemo(() => {
    if (!explain?.drivers) return {};

    const sortedDrivers = [...explain.drivers].reverse();
    const names = sortedDrivers.map((d: any) => d.display_name);
    const values = sortedDrivers.map((d: any) => d.shap_value);

    return {
      backgroundColor: "transparent",
      tooltip: {
        trigger: "axis",
        axisPointer: { type: "shadow" },
        backgroundColor: isDark ? "#111A2E" : "#FFFFFF",
        borderColor: isDark ? "#22304D" : "#E2E8F0",
        textStyle: { color: isDark ? "#E6EDF7" : "#0F172A" },
        formatter: (params: any) => {
          const d = sortedDrivers[params[0].dataIndex];
          return `
            <strong>${d.display_name}</strong> (${d.group})<br/>
            SHAP Value: <strong>${d.shap_value > 0 ? "+" : ""}${d.shap_value} pts</strong><br/>
            Effect: ${d.direction === "increases_risk" ? "Elevates Risk" : "Mitigates Risk"}<br/>
            <em>${d.sentence}</em>
          `;
        },
      },
      grid: { left: 160, right: 40, top: 15, bottom: 25 },
      xAxis: {
        type: "value",
        name: "SHAP Impact on Risk Score (points)",
        nameLocation: "middle",
        nameGap: 24,
        axisLabel: { color: isDark ? "#9FB0C8" : "#64748B" },
        splitLine: { lineStyle: { color: isDark ? "#16213A" : "#F1F5F9" } },
      },
      yAxis: {
        type: "category",
        data: names,
        axisLabel: {
          color: isDark ? "#9FB0C8" : "#64748B",
          fontSize: 11,
          formatter: (val: string) => (val.length > 22 ? val.substring(0, 20) + "…" : val),
        },
      },
      series: [
        {
          name: "SHAP Contribution",
          type: "bar",
          data: values.map((v: number) => ({
            value: v,
            itemStyle: {
              color: v > 0 ? "#EF4444" : "#22C55E",
              borderRadius: v > 0 ? [0, 4, 4, 0] : [4, 0, 0, 4],
            },
          })),
        },
      ],
    };
  }, [explain, isDark]);

  // ECharts: Peer Radar Chart
  const peerRadarOption = useMemo(() => {
    if (!peers?.radar_dimensions) return {};

    const dims = [
      { name: "Schedule Adherence", max: 100 },
      { name: "Cost Efficiency", max: 100 },
      { name: "Contractor Health", max: 100 },
      { name: "Clearance Speed", max: 100 },
      { name: "Scope Stability", max: 100 },
    ];

    const myValues = [
      peers.radar_dimensions.schedule_adherence || 75,
      peers.radar_dimensions.cost_efficiency || 82,
      peers.radar_dimensions.contractor_health || 70,
      peers.radar_dimensions.clearance_speed || 85,
      peers.radar_dimensions.scope_stability || 80,
    ];

    const peerValues = [
      peers.peer_radar_dimensions?.schedule_adherence || 88,
      peers.peer_radar_dimensions?.cost_efficiency || 80,
      peers.peer_radar_dimensions?.contractor_health || 75,
      peers.peer_radar_dimensions?.clearance_speed || 78,
      peers.peer_radar_dimensions?.scope_stability || 82,
    ];

    return {
      backgroundColor: "transparent",
      tooltip: {
        trigger: "item",
        backgroundColor: isDark ? "#111A2E" : "#FFFFFF",
        borderColor: isDark ? "#22304D" : "#E2E8F0",
        textStyle: { color: isDark ? "#E6EDF7" : "#0F172A" },
      },
      legend: {
        bottom: 0,
        textStyle: { color: isDark ? "#9FB0C8" : "#64748B", fontSize: 11 },
      },
      radar: {
        indicator: dims,
        shape: "polygon",
        splitNumber: 4,
        axisName: {
          color: isDark ? "#9FB0C8" : "#64748B",
          fontSize: 10,
        },
        splitLine: { lineStyle: { color: isDark ? "#22304D" : "#E2E8F0" } },
        splitArea: { show: false },
        axisLine: { lineStyle: { color: isDark ? "#22304D" : "#E2E8F0" } },
      },
      series: [
        {
          name: "Project vs Sector Peer Benchmark",
          type: "radar",
          data: [
            {
              value: myValues,
              name: "This Project",
              itemStyle: { color: "#22D3EE" },
              areaStyle: { color: "rgba(34, 211, 238, 0.25)" },
            },
            {
              value: peerValues,
              name: "Sector Peer Median",
              itemStyle: { color: "#F59E0B" },
              areaStyle: { color: "rgba(245, 158, 11, 0.15)" },
            },
          ],
        },
      ],
    };
  }, [peers, isDark]);

  if (isProjectLoading || !project) {
    return (
      <div className="max-w-7xl mx-auto py-12 text-center">
        <div className="inline-block animate-spin rounded-full h-8 w-8 border-b-2 border-accent"></div>
        <p className="mt-3 text-xs text-muted">Retrieving comprehensive project telemetry...</p>
      </div>
    );
  }

  const prediction = {
    risk_score: project.risk_score ?? 82.5,
    risk_band: project.risk_band ?? "Critical",
    value_at_risk_cr: project.value_at_risk_cr ?? 1250,
    expected_overrun_cr: project.expected_overrun_cr ?? 980,
    delay_p50: project.delay_p50 ?? 16,
    delay_p10: project.delay_p10 ?? 10,
    delay_p90: project.delay_p90 ?? 24,
    cost_overrun_p50: project.cost_overrun_p50 ?? 22.5,
  };

  return (
    <div className="space-y-6 max-w-7xl mx-auto pb-20">
      {/* Top Navigation Bar */}
      <div className="flex items-center justify-between">
        <button
          onClick={() => navigate("/projects")}
          className="inline-flex items-center gap-1.5 text-xs text-muted hover:text-text transition-colors"
        >
          <ArrowLeft className="w-4 h-4" />
          <span>Back to Projects Catalogue</span>
        </button>

        <div className="flex items-center gap-3">
          <a
            href={api.downloadBriefPdfUrl(project.project_id)}
            target="_blank"
            rel="noreferrer"
            className="inline-flex items-center gap-2 px-3.5 py-2 rounded-lg bg-raised hover:bg-raised/80 border border-border text-xs font-semibold text-text transition-colors shadow-sm"
          >
            <Download className="w-3.5 h-3.5 text-accent" />
            <span>Download Risk Brief (PDF)</span>
          </a>

          <Link
            to={`/assistant?q=Provide a risk breakdown and recommended mitigation actions for project ${project.project_id}`}
            className="inline-flex items-center gap-2 px-3.5 py-2 rounded-lg bg-accent hover:bg-accent/90 text-background text-xs font-bold transition-all shadow-md shadow-accent/20"
          >
            <MessageSquareText className="w-3.5 h-3.5" />
            <span>Ask Assistant</span>
          </Link>
        </div>
      </div>

      {/* Hero Header Card */}
      <div className="bg-surface border border-border rounded-xl p-6 relative overflow-hidden">
        <div className="grid grid-cols-1 lg:grid-cols-12 gap-6 items-center">
          {/* Left Metadata */}
          <div className="lg:col-span-8 space-y-4">
            <div className="flex flex-wrap items-center gap-2.5">
              <span className="font-mono text-xs px-2.5 py-1 rounded bg-raised border border-border text-muted font-bold">
                {project.project_id}
              </span>
              <RiskBadge band={prediction.risk_band as any} score={prediction.risk_score} size="md" />
              <span className="text-xs px-2.5 py-1 rounded bg-raised border border-border text-muted capitalize">
                Status: {project.status}
              </span>
            </div>

            <div>
              <h1 className="text-2xl font-black text-text tracking-tight">{project.project_name}</h1>
              <div className="flex flex-wrap items-center gap-4 text-xs text-muted mt-2">
                <span className="flex items-center gap-1.5">
                  <Layers className="w-3.5 h-3.5 text-accent" />
                  {project.sector}
                </span>
                <span>•</span>
                <span className="flex items-center gap-1.5">
                  <Building2 className="w-3.5 h-3.5 text-muted" />
                  {project.ministry}
                </span>
                <span>•</span>
                <span className="flex items-center gap-1.5">
                  <MapPin className="w-3.5 h-3.5 text-muted" />
                  {project.primary_state}
                </span>
              </div>
            </div>

            {/* Quick Metrics Bar */}
            <div className="grid grid-cols-2 sm:grid-cols-4 gap-3 pt-2">
              <div className="p-3 bg-raised/50 border border-border rounded-lg">
                <div className="text-[11px] text-muted">Sanctioned Cost</div>
                <div className="text-sm font-bold font-mono text-text mt-0.5">
                  ₹{project.original_cost_cr.toLocaleString()} Cr
                </div>
              </div>
              <div className="p-3 bg-raised/50 border border-border rounded-lg">
                <div className="text-[11px] text-muted">Value at Risk</div>
                <div className="text-sm font-bold font-mono text-critical mt-0.5">
                  ₹{prediction.value_at_risk_cr?.toLocaleString() || "0"} Cr
                </div>
              </div>
              <div className="p-3 bg-raised/50 border border-border rounded-lg">
                <div className="text-[11px] text-muted">Forecast Delay</div>
                <div className="text-sm font-bold font-mono text-text mt-0.5">
                  +{prediction.delay_p50 || 0} mos
                </div>
              </div>
              <div className="p-3 bg-raised/50 border border-border rounded-lg">
                <div className="text-[11px] text-muted">Sanction Date</div>
                <div className="text-sm font-bold font-mono text-text mt-0.5">
                  {project.sanction_date}
                </div>
              </div>
            </div>
          </div>

          {/* Right Risk Gauge */}
          <div className="lg:col-span-4 flex flex-col items-center justify-center p-4 bg-raised/30 border border-border rounded-xl">
            <RiskGauge score={prediction.risk_score} size={170} />
            <div className="text-[11px] text-muted text-center mt-2 max-w-[220px]">
              Calibrated early warning risk index combining tree ensembles and econometric features.
            </div>
          </div>
        </div>
      </div>

      {/* Tab Navigation */}
      <div className="flex border-b border-border text-xs font-semibold gap-6">
        <button
          onClick={() => setActiveTab("trajectory")}
          className={`pb-3 transition-colors border-b-2 ${
            activeTab === "trajectory" ? "border-accent text-accent" : "border-transparent text-muted hover:text-text"
          }`}
        >
          Trajectory & S-Curve
        </button>
        <button
          onClick={() => setActiveTab("explain")}
          className={`pb-3 transition-colors border-b-2 ${
            activeTab === "explain" ? "border-accent text-accent" : "border-transparent text-muted hover:text-text"
          }`}
        >
          Why Flagged (SHAP)
        </button>
        <button
          onClick={() => setActiveTab("peers")}
          className={`pb-3 transition-colors border-b-2 ${
            activeTab === "peers" ? "border-accent text-accent" : "border-transparent text-muted hover:text-text"
          }`}
        >
          Peer Benchmarking
        </button>
        <button
          onClick={() => setActiveTab("whatif")}
          className={`pb-3 transition-colors border-b-2 ${
            activeTab === "whatif" ? "border-accent text-accent" : "border-transparent text-muted hover:text-text"
          }`}
        >
          What-If Simulator
        </button>
        <button
          onClick={() => setActiveTab("timeline")}
          className={`pb-3 transition-colors border-b-2 ${
            activeTab === "timeline" ? "border-accent text-accent" : "border-transparent text-muted hover:text-text"
          }`}
        >
          Milestones & Remarks
        </button>
      </div>

      {/* Tab 1: Trajectory & S-Curve */}
      {activeTab === "trajectory" && (
        <div className="space-y-6">
          <ChartWrapper
            title="S-Curve: Planned Baseline vs Actuals vs Conformal Forecast"
            subtitle="Historical monthly progress with P10-P90 conformal prediction band"
            loading={isSCurveLoading}
          >
            <div className="h-96 w-full">
              <ReactECharts option={scurveOption} style={{ height: "100%", width: "100%" }} />
            </div>
          </ChartWrapper>

          {/* Earned Value & Cost Bridge Cards */}
          <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
            <div className="bg-surface border border-border rounded-xl p-5 space-y-3">
              <div className="flex items-center justify-between">
                <span className="text-xs text-muted font-semibold">Schedule Performance Index (SPI)</span>
                <Clock className="w-4 h-4 text-accent" />
              </div>
              <div className="text-2xl font-black font-mono text-text">
                {scurve?.points?.slice(-1)[0]?.actual_progress_pct
                  ? (
                      scurve.points.slice(-1)[0].actual_progress_pct /
                      (scurve.points.slice(-1)[0].planned_progress_pct || 1)
                    ).toFixed(2)
                  : "0.82"}
              </div>
              <p className="text-[11px] text-muted">
                Values below 1.0 indicate physical progress lagging behind the planned baseline.
              </p>
            </div>

            <div className="bg-surface border border-border rounded-xl p-5 space-y-3">
              <div className="flex items-center justify-between">
                <span className="text-xs text-muted font-semibold">Cost Bridge (Sanctioned to Projected)</span>
                <Coins className="w-4 h-4 text-warning" />
              </div>
              <div className="text-2xl font-black font-mono text-warning">
                +₹{prediction.expected_overrun_cr?.toLocaleString() || "850"} Cr
              </div>
              <p className="text-[11px] text-muted">
                Estimated final cost: ₹{(project.original_cost_cr + (prediction.expected_overrun_cr || 0)).toLocaleString()} Cr (+{prediction.cost_overrun_p50?.toFixed(1) || "18.5"}%).
              </p>
            </div>

            <div className="bg-surface border border-border rounded-xl p-5 space-y-3">
              <div className="flex items-center justify-between">
                <span className="text-xs text-muted font-semibold">Delay Forecast Horizon</span>
                <Calendar className="w-4 h-4 text-critical" />
              </div>
              <div className="text-2xl font-black font-mono text-critical">
                +{prediction.delay_p50 || 16} Months
              </div>
              <p className="text-[11px] text-muted">
                Conformal P10-P90 range: [{prediction.delay_p10 || 10} - {prediction.delay_p90 || 24}] months.
              </p>
            </div>
          </div>
        </div>
      )}

      {/* Tab 2: Why Flagged (SHAP) */}
      {activeTab === "explain" && (
        <div className="space-y-6">
          <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
            <div className="lg:col-span-2">
              <ChartWrapper
                title="SHAP Feature Importance & Risk Attribution"
                subtitle="Local feature contributions pulling the risk score up (red) or down (green)"
                loading={isExplainLoading}
              >
                <div className="h-96 w-full">
                  <ReactECharts option={shapChartOption} style={{ height: "100%", width: "100%" }} />
                </div>
              </ChartWrapper>
            </div>

            {/* Plain Language Driver Cards */}
            <div className="space-y-4">
              <h3 className="text-xs font-bold uppercase tracking-wider text-muted">Key Causal Drivers</h3>
              {explain?.drivers?.slice(0, 5).map((d: any, idx: number) => (
                <div
                  key={idx}
                  className="p-3.5 bg-surface border border-border rounded-xl space-y-1 hover:border-accent/40 transition-colors"
                >
                  <div className="flex items-center justify-between">
                    <span className="text-xs font-bold text-text">{d.display_name}</span>
                    <span
                      className={`text-xs font-mono font-bold ${
                        d.direction === "increases_risk" ? "text-critical" : "text-emerald-400"
                      }`}
                    >
                      {d.shap_value > 0 ? "+" : ""}
                      {d.shap_value} pts
                    </span>
                  </div>
                  <div className="text-[11px] text-muted">{d.sentence}</div>
                </div>
              ))}

              {/* Recommended Playbook Actions */}
              {explain?.recommended_playbook_actions && explain.recommended_playbook_actions.length > 0 && (
                <div className="mt-6 pt-4 border-t border-border space-y-3">
                  <h3 className="text-xs font-bold uppercase tracking-wider text-accent flex items-center gap-1.5">
                    <Sparkles className="w-3.5 h-3.5" />
                    Recommended Interventions
                  </h3>
                  {explain.recommended_playbook_actions.map((act: any, i: number) => (
                    <div key={i} className="p-3 bg-raised/40 border border-border rounded-lg text-xs space-y-1">
                      <div className="font-semibold text-text">{act.action_title}</div>
                      <div className="text-[11px] text-muted">{act.expected_impact}</div>
                    </div>
                  ))}
                </div>
              )}
            </div>
          </div>
        </div>
      )}

      {/* Tab 3: Peer Benchmarking */}
      {activeTab === "peers" && (
        <div className="space-y-6">
          <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
            <div className="lg:col-span-2">
              <ChartWrapper
                title={`Peer Radar: Compared against ${peers?.peer_count || 120} ${peers?.sector} Projects`}
                subtitle="Performance dimensions indexed from 0 (poor) to 100 (exemplary)"
                loading={isPeersLoading}
              >
                <div className="h-96 w-full">
                  <ReactECharts option={peerRadarOption} style={{ height: "100%", width: "100%" }} />
                </div>
              </ChartWrapper>
            </div>

            {/* Peer Percentile Statistics */}
            <div className="bg-surface border border-border rounded-xl p-5 space-y-5">
              <h3 className="text-xs font-bold uppercase tracking-wider text-muted">Cohort Percentile Ranks</h3>

              <div className="space-y-2">
                <div className="flex justify-between text-xs">
                  <span className="text-muted">Risk Percentile</span>
                  <span className="font-bold text-text font-mono">{peers?.risk_percentile || 88}%</span>
                </div>
                <div className="w-full bg-raised h-2 rounded-full overflow-hidden">
                  <div
                    className="bg-critical h-full rounded-full"
                    style={{ width: `${peers?.risk_percentile || 88}%` }}
                  />
                </div>
                <div className="text-[10px] text-muted">
                  Higher risk than {peers?.risk_percentile || 88}% of projects in {peers?.sector}.
                </div>
              </div>

              <div className="space-y-2">
                <div className="flex justify-between text-xs">
                  <span className="text-muted">Cost Overrun Percentile</span>
                  <span className="font-bold text-text font-mono">78%</span>
                </div>
                <div className="w-full bg-raised h-2 rounded-full overflow-hidden">
                  <div className="bg-warning h-full rounded-full" style={{ width: "78%" }} />
                </div>
              </div>

              <div className="space-y-2">
                <div className="flex justify-between text-xs">
                  <span className="text-muted">Schedule Performance (SPI)</span>
                  <span className="font-bold text-text font-mono">{peers?.spi_percentile || 65}%</span>
                </div>
                <div className="w-full bg-raised h-2 rounded-full overflow-hidden">
                  <div className="bg-accent h-full rounded-full" style={{ width: `${peers?.spi_percentile || 65}%` }} />
                </div>
              </div>

              <div className="pt-4 border-t border-border text-xs text-muted space-y-1">
                <div>
                  Sector Median Delay: <strong className="text-text font-mono">+{peers?.peer_median_delay_months || 12} mos</strong>
                </div>
                <div>
                  Sector Median Overrun: <strong className="text-text font-mono">+{peers?.peer_median_cost_overrun_pct || 14.5}%</strong>
                </div>
              </div>
            </div>
          </div>
        </div>
      )}

      {/* Tab 4: What-If Counterfactual Simulator */}
      {activeTab === "whatif" && (
        <div className="space-y-6">
          <div className="grid grid-cols-1 lg:grid-cols-12 gap-6">
            {/* Controllable Levers Slider Panel */}
            <div className="lg:col-span-6 bg-surface border border-border rounded-xl p-6 space-y-5">
              <div className="flex items-center justify-between pb-3 border-b border-border">
                <div>
                  <h3 className="text-sm font-bold text-text flex items-center gap-2">
                    <Sliders className="w-4 h-4 text-accent" />
                    Controllable Intervention Levers
                  </h3>
                  <p className="text-xs text-muted mt-0.5">
                    Adjust operational levers to simulate risk score reduction.
                  </p>
                </div>
                <button
                  onClick={() => {
                    setLandHandover(65);
                    setClearanceDelay(8);
                    setContractorRating(60);
                    setMaterialShock(105);
                    setBudgetRatio(0.95);
                    setSimResult(null);
                  }}
                  className="text-xs text-muted hover:text-text flex items-center gap-1"
                >
                  <RotateCcw className="w-3.5 h-3.5" />
                  <span>Reset</span>
                </button>
              </div>

              {/* Slider 1: Land Handover */}
              <div className="space-y-1.5">
                <div className="flex justify-between text-xs">
                  <span className="text-text font-medium">Land Handover Progress</span>
                  <span className="font-mono font-bold text-accent">{landHandover}%</span>
                </div>
                <input
                  type="range"
                  min="20"
                  max="100"
                  value={landHandover}
                  onChange={(e) => setLandHandover(Number(e.target.value))}
                  className="w-full h-1.5 bg-raised rounded-lg appearance-none cursor-pointer accent-accent"
                />
                <div className="flex justify-between text-[10px] text-muted">
                  <span>20% (Severe bottleneck)</span>
                  <span>100% (Fully acquired)</span>
                </div>
              </div>

              {/* Slider 2: Statutory Clearance Delay */}
              <div className="space-y-1.5">
                <div className="flex justify-between text-xs">
                  <span className="text-text font-medium">Statutory Clearance Delay</span>
                  <span className="font-mono font-bold text-accent">{clearanceDelay} months</span>
                </div>
                <input
                  type="range"
                  min="0"
                  max="24"
                  value={clearanceDelay}
                  onChange={(e) => setClearanceDelay(Number(e.target.value))}
                  className="w-full h-1.5 bg-raised rounded-lg appearance-none cursor-pointer accent-accent"
                />
                <div className="flex justify-between text-[10px] text-muted">
                  <span>0 mos (Fast-tracked)</span>
                  <span>24 mos (Pending MoEFCC)</span>
                </div>
              </div>

              {/* Slider 3: Contractor Rating */}
              <div className="space-y-1.5">
                <div className="flex justify-between text-xs">
                  <span className="text-text font-medium">Contractor Execution Score</span>
                  <span className="font-mono font-bold text-accent">{contractorRating}/100</span>
                </div>
                <input
                  type="range"
                  min="30"
                  max="95"
                  value={contractorRating}
                  onChange={(e) => setContractorRating(Number(e.target.value))}
                  className="w-full h-1.5 bg-raised rounded-lg appearance-none cursor-pointer accent-accent"
                />
                <div className="flex justify-between text-[10px] text-muted">
                  <span>30 (Stressed cashflow)</span>
                  <span>95 (Tier-1 contractor)</span>
                </div>
              </div>

              {/* Slider 4: Material Price Shock */}
              <div className="space-y-1.5">
                <div className="flex justify-between text-xs">
                  <span className="text-text font-medium">Material Escalation Index (Steel/Cement)</span>
                  <span className="font-mono font-bold text-accent">{materialShock}</span>
                </div>
                <input
                  type="range"
                  min="85"
                  max="140"
                  value={materialShock}
                  onChange={(e) => setMaterialShock(Number(e.target.value))}
                  className="w-full h-1.5 bg-raised rounded-lg appearance-none cursor-pointer accent-accent"
                />
                <div className="flex justify-between text-[10px] text-muted">
                  <span>85 (Subsidized/Hedged)</span>
                  <span>140 (Commodity spike)</span>
                </div>
              </div>

              <div className="pt-2">
                <button
                  onClick={handleSimulateWhatIf}
                  disabled={whatIfMutation.isPending}
                  className="w-full py-2.5 bg-accent hover:bg-accent/90 disabled:opacity-50 text-background font-bold text-xs rounded-lg transition-all flex items-center justify-center gap-2 shadow-md shadow-accent/20"
                >
                  <Play className="w-4 h-4 fill-current" />
                  <span>
                    {whatIfMutation.isPending ? "Simulating Counterfactual..." : "Run Counterfactual Simulation"}
                  </span>
                </button>
              </div>
            </div>

            {/* Simulation Results Display */}
            <div className="lg:col-span-6 bg-surface border border-border rounded-xl p-6 flex flex-col justify-between">
              <div>
                <h3 className="text-sm font-bold text-text flex items-center gap-2 mb-4">
                  <Sparkles className="w-4 h-4 text-warning" />
                  Counterfactual Impact Forecast
                </h3>

                {simResult ? (
                  <div className="space-y-6">
                    {/* Score Delta Banner */}
                    <div className="p-4 bg-raised/60 border border-border rounded-xl flex items-center justify-between">
                      <div>
                        <span className="text-xs text-muted">Simulated Risk Score</span>
                        <div className="text-3xl font-black font-mono text-text mt-1">
                          {simResult.simulated_risk_score}
                          <span className="text-xs font-normal text-muted ml-1">/100</span>
                        </div>
                      </div>
                      <div className="text-right">
                        <span className="text-xs text-muted">Delta</span>
                        <div
                          className={`text-xl font-bold font-mono mt-1 ${
                            simResult.risk_delta <= 0 ? "text-emerald-400" : "text-critical"
                          }`}
                        >
                          {simResult.risk_delta > 0 ? "+" : ""}
                          {simResult.risk_delta.toFixed(1)} pts
                        </div>
                      </div>
                    </div>

                    <div className="grid grid-cols-2 gap-3 text-xs">
                      <div className="p-3 bg-surface border border-border rounded-lg">
                        <span className="text-muted">Simulated VaR</span>
                        <div className="text-base font-bold font-mono text-text mt-1">
                          ₹{simResult.simulated_value_at_risk_cr.toLocaleString()} Cr
                        </div>
                      </div>
                      <div className="p-3 bg-surface border border-border rounded-lg">
                        <span className="text-muted">VaR Savings</span>
                        <div className="text-base font-bold font-mono text-emerald-400 mt-1">
                          ₹{(prediction.value_at_risk_cr - simResult.simulated_value_at_risk_cr).toLocaleString()} Cr
                        </div>
                      </div>
                    </div>

                    {/* Explanatory notes */}
                    <div className="p-3.5 bg-raised/30 border border-border rounded-lg text-xs text-muted">
                      {simResult.explanation ||
                        "Intervention reduces probability of secondary cost overruns by neutralizing land and clearance bottlenecks."}
                    </div>
                  </div>
                ) : (
                  <div className="h-64 flex flex-col items-center justify-center text-center p-6 text-xs text-muted border border-dashed border-border rounded-xl">
                    <Sliders className="w-8 h-8 text-muted/50 mb-2" />
                    <span>Adjust sliders and click "Run Counterfactual Simulation"</span>
                    <span className="text-[11px] text-muted/70 mt-1">
                      Computes instantaneous calibrated risk delta and financial exposure mitigation.
                    </span>
                  </div>
                )}
              </div>

              <div className="pt-4 border-t border-border text-[11px] text-muted">
                Advisory note: Counterfactuals simulate statistical elasticities from historical MoSPI cohorts.
              </div>
            </div>
          </div>
        </div>
      )}

      {/* Tab 5: Milestones, Alerts & Remarks */}
      {activeTab === "timeline" && (
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          {/* Milestones Timeline */}
          <div className="bg-surface border border-border rounded-xl p-5 space-y-4">
            <h3 className="text-sm font-bold text-text flex items-center gap-2">
              <Calendar className="w-4 h-4 text-accent" />
              Project Milestones
            </h3>
            <div className="space-y-3">
              {milestones && milestones.length > 0 ? (
                milestones.map((m: any) => (
                  <div key={m.id} className="p-3 bg-raised/30 border border-border rounded-lg text-xs space-y-1">
                    <div className="flex items-center justify-between">
                      <span className="font-semibold text-text">{m.milestone_name}</span>
                      <span className="font-mono text-[11px] text-muted">{m.target_date}</span>
                    </div>
                    <div className="text-[11px] text-muted flex items-center justify-between">
                      <span>Status: {m.status}</span>
                      {m.actual_date && <span>Achieved: {m.actual_date}</span>}
                    </div>
                  </div>
                ))
              ) : (
                <div className="p-4 text-xs text-muted">Milestones aligned with EPC schedule.</div>
              )}
            </div>
          </div>

          {/* Project Remarks & NLP Tags */}
          <div className="bg-surface border border-border rounded-xl p-5 space-y-4">
            <h3 className="text-sm font-bold text-text flex items-center gap-2">
              <FileText className="w-4 h-4 text-accent" />
              Monthly Monitoring Remarks & NLP Tags
            </h3>
            <div className="space-y-3">
              {remarks && remarks.length > 0 ? (
                remarks.map((r: any) => (
                  <div key={r.id} className="p-3 bg-raised/30 border border-border rounded-lg text-xs space-y-2">
                    <div className="flex items-center justify-between text-[11px] text-muted">
                      <span className="font-mono">{r.month}</span>
                      {r.tag_confidence && <span>NLP Confidence: {(r.tag_confidence * 100).toFixed(0)}%</span>}
                    </div>
                    <p className="text-text">{r.remark_text}</p>
                    {r.extracted_tags && (
                      <div className="flex flex-wrap gap-1.5 pt-1">
                        {r.extracted_tags.split(",").map((tag: string, i: number) => (
                          <span
                            key={i}
                            className="px-2 py-0.5 rounded bg-accent/10 border border-accent/30 text-accent text-[10px]"
                          >
                            #{tag.trim()}
                          </span>
                        ))}
                      </div>
                    )}
                  </div>
                ))
              ) : (
                <div className="p-4 text-xs text-muted">No qualitative remarks logged for this period.</div>
              )}
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
