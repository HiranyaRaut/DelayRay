import React, { useState } from "react";
import {
  TrendingUp,
  AlertTriangle,
  FolderKanban,
  Flame,
  ShieldCheck,
  Clock,
  Sparkles,
  BarChart3,
  ExternalLink,
} from "lucide-react";
import { KpiTile } from "../components/ui/KpiTile";
import { RiskBadge } from "../components/ui/RiskBadge";
import { RiskGauge } from "../components/ui/RiskGauge";
import { ChartWrapper } from "../components/ui/ChartWrapper";
import { DataTable, ColumnDef } from "../components/ui/DataTable";
import { Drawer } from "../components/ui/Drawer";
import { FacetedFilters } from "../components/ui/FacetedFilters";
import { useAppStore } from "../stores/appStore";

export function ComponentShowcase() {
  const addToast = useAppStore((s) => s.addToast);
  const [drawerOpen, setDrawerOpen] = useState(false);
  const [search, setSearch] = useState("");
  const [sector, setSector] = useState("");
  const [band, setBand] = useState("");

  // Sample data for DataTable demo
  const sampleProjects = [
    {
      id: "PRJ-RAIL-00102",
      name: "Dedicated Freight Corridor (Western Alignment) Pkg 4",
      sector: "Railways",
      cost_cr: 12450.0,
      risk_score: 88.5,
      risk_band: "Critical",
      spi: 0.72,
    },
    {
      id: "PRJ-ROAD-00451",
      name: "Six-Laning Greenfield Expressway Package 2",
      sector: "Road Transport & Highways",
      cost_cr: 3420.5,
      risk_score: 64.2,
      risk_band: "High",
      spi: 0.81,
    },
    {
      id: "PRJ-POWER-00812",
      name: "765kV Inter-Regional Power Transmission Link",
      sector: "Power Transmission",
      cost_cr: 1850.0,
      risk_score: 38.0,
      risk_band: "Moderate",
      spi: 0.94,
    },
    {
      id: "PRJ-SOLAR-00301",
      name: "Ultra Mega Solar Park Grid Evacuation Line",
      sector: "Renewable Energy (Solar/Wind)",
      cost_cr: 920.0,
      risk_score: 18.5,
      risk_band: "Low",
      spi: 1.05,
    },
  ];

  const columns: ColumnDef<any>[] = [
    {
      header: "Project ID",
      accessorKey: "id",
      className: "font-mono font-semibold text-accent",
    },
    {
      header: "Infrastructure Asset Name",
      accessorKey: "name",
      className: "max-w-xs truncate font-medium",
    },
    {
      header: "Sector",
      accessorKey: "sector",
    },
    {
      header: "Sanctioned Cost",
      cell: (row) => <span className="font-mono tabular-nums">₹{row.cost_cr.toLocaleString()} Cr</span>,
      align: "right",
    },
    {
      header: "Risk Tier",
      cell: (row) => <RiskBadge band={row.risk_band} score={row.risk_score} size="sm" />,
      align: "center",
    },
    {
      header: "SPI",
      cell: (row) => (
        <span className={`font-mono font-bold ${row.spi < 0.85 ? "text-red-400" : "text-emerald-400"}`}>
          {row.spi.toFixed(2)}
        </span>
      ),
      align: "right",
    },
  ];

  return (
    <div className="space-y-10 max-w-7xl mx-auto pb-12 select-none">
      {/* Title Header */}
      <div>
        <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full text-xs font-semibold bg-accent/15 text-accent border border-accent/30 mb-2">
          <Sparkles className="w-3.5 h-3.5" />
          <span>Design System & Reusable Component Library</span>
        </div>
        <h1 className="text-2xl font-black text-text tracking-tight">Component Showcase (/dev/components)</h1>
        <p className="text-xs text-muted mt-1 max-w-2xl leading-relaxed">
          Comprehensive catalog of all foundational design tokens, color-blind safe risk indicators,
          analytical gauges, and structured layouts adhering to docs/BUILD_SPEC.md Section 10.1.
        </p>
      </div>

      {/* 1. Risk Badges (Colour-blind safe combinations) */}
      <section className="space-y-3">
        <h2 className="text-sm font-bold text-text uppercase tracking-wider text-muted">
          1. Risk Badges (Color + Icon + Label)
        </h2>
        <div className="flex flex-wrap items-center gap-4 p-5 bg-surface border border-border rounded-xl">
          <RiskBadge band="Low" score={14.2} size="lg" />
          <RiskBadge band="Moderate" score={38.5} size="lg" />
          <RiskBadge band="High" score={64.0} size="lg" />
          <RiskBadge band="Critical" score={89.5} size="lg" />
          <div className="h-6 w-px bg-border mx-2" />
          <RiskBadge band="Low" size="md" />
          <RiskBadge band="Moderate" size="md" />
          <RiskBadge band="High" size="md" />
          <RiskBadge band="Critical" size="md" />
          <div className="h-6 w-px bg-border mx-2" />
          <RiskBadge band="Critical" size="sm" />
        </div>
      </section>

      {/* 2. KPI Tiles */}
      <section className="space-y-3">
        <h2 className="text-sm font-bold text-text uppercase tracking-wider text-muted">
          2. Executive KPI Tiles
        </h2>
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
          <KpiTile
            title="Projects Tracked"
            value="1,981"
            subtitle="Central sector ongoing"
            icon={FolderKanban}
            trend={{ value: "+12", direction: "neutral" }}
          />
          <KpiTile
            title="Portfolio Cost"
            value="₹86.58 Lk Cr"
            subtitle="Sanctioned budget"
            icon={TrendingUp}
            variant="accent"
            trend={{ value: "+4.2%", direction: "up" }}
          />
          <KpiTile
            title="Value at Risk (VaR)"
            value="₹12.64 Lk Cr"
            subtitle="At-risk capital exposure"
            icon={AlertTriangle}
            variant="warning"
            trend={{ value: "+2.1%", direction: "up" }}
          />
          <KpiTile
            title="Critical Risk Assets"
            value="1,699"
            subtitle="Score ≥ 75.0"
            icon={Flame}
            variant="critical"
            trend={{ value: "+18", direction: "up" }}
          />
        </div>

        {/* Loading State Sample */}
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4 pt-2">
          <KpiTile title="" value="" loading={true} />
          <KpiTile title="" value="" loading={true} />
        </div>
      </section>

      {/* 3. Risk Gauge (Calibrated 0-100 Probabilities) */}
      <section className="space-y-3">
        <h2 className="text-sm font-bold text-text uppercase tracking-wider text-muted">
          3. Calibrated Risk Score Gauges
        </h2>
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4 p-6 bg-surface border border-border rounded-xl">
          <div className="flex flex-col items-center">
            <span className="text-xs text-muted mb-2 font-medium">Low Band (0 - 25)</span>
            <RiskGauge score={18.2} />
          </div>
          <div className="flex flex-col items-center">
            <span className="text-xs text-muted mb-2 font-medium">Moderate Band (25 - 50)</span>
            <RiskGauge score={42.0} />
          </div>
          <div className="flex flex-col items-center">
            <span className="text-xs text-muted mb-2 font-medium">High Band (50 - 75)</span>
            <RiskGauge score={68.5} />
          </div>
          <div className="flex flex-col items-center">
            <span className="text-xs text-muted mb-2 font-medium">Critical Band (≥ 75)</span>
            <RiskGauge score={91.4} />
          </div>
        </div>
      </section>

      {/* 4. Chart Wrapper in All States */}
      <section className="space-y-3">
        <h2 className="text-sm font-bold text-text uppercase tracking-wider text-muted">
          4. Chart Container States (Normal, Loading, Empty, Error)
        </h2>
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          <ChartWrapper
            title="Normal State (Mock Chart)"
            subtitle="Renders charts smoothly with full interactive tooltips"
            height={200}
          >
            <div className="w-full h-full flex items-center justify-center bg-raised/30 rounded-lg border border-border/50">
              <span className="text-xs text-accent font-mono">[Interactive ECharts Visualization Container]</span>
            </div>
          </ChartWrapper>

          <ChartWrapper
            title="Loading Skeleton State"
            subtitle="Demonstrates graceful data acquisition placeholder"
            loading={true}
            height={200}
          >
            <div />
          </ChartWrapper>

          <ChartWrapper
            title="Empty Data State"
            subtitle="Appears when query filters match zero observations"
            empty={true}
            emptyMessage="No project snapshots found for the selected time horizon."
            height={200}
          >
            <div />
          </ChartWrapper>

          <ChartWrapper
            title="Error State with Retry Action"
            subtitle="Handles network interruptions and query timeouts"
            error="Connection timeout while fetching vector similarity weights."
            onRetry={() => addToast({ type: "info", title: "Retrying", message: "Connecting to API backend..." })}
            height={200}
          >
            <div />
          </ChartWrapper>
        </div>
      </section>

      {/* 5. Faceted Filter Bar */}
      <section className="space-y-3">
        <h2 className="text-sm font-bold text-text uppercase tracking-wider text-muted">
          5. Faceted Filter Bar & Search
        </h2>
        <FacetedFilters
          search={search}
          onSearchChange={setSearch}
          selectedSector={sector}
          onSectorChange={setSector}
          selectedBand={band}
          onBandChange={setBand}
          sectors={["Railways", "Road Transport & Highways", "Thermal Power", "Metro Rail Transit", "Atomic Energy"]}
          onReset={() => {
            setSearch("");
            setSector("");
            setBand("");
          }}
        />
      </section>

      {/* 6. DataTable & Drawer Demonstration */}
      <section className="space-y-3">
        <div className="flex items-center justify-between">
          <h2 className="text-sm font-bold text-text uppercase tracking-wider text-muted">
            6. Interactive Data Table (Click row to trigger Quick-Peek Drawer)
          </h2>
          <button
            onClick={() => setDrawerOpen(true)}
            className="text-xs font-semibold text-accent hover:underline flex items-center gap-1"
          >
            Open Drawer Demo <ExternalLink className="w-3.5 h-3.5" />
          </button>
        </div>
        <DataTable
          columns={columns}
          data={sampleProjects}
          onRowClick={(row) => setDrawerOpen(true)}
          pagination={{
            page: 1,
            pageSize: 4,
            total: 1981,
            totalPages: 496,
            onPageChange: (p) => addToast({ type: "info", title: `Navigating to page ${p}` }),
          }}
        />
      </section>

      {/* 7. Interactive Toast Triggers */}
      <section className="space-y-3">
        <h2 className="text-sm font-bold text-text uppercase tracking-wider text-muted">
          7. Notification Toasts
        </h2>
        <div className="flex flex-wrap gap-3 p-5 bg-surface border border-border rounded-xl">
          <button
            onClick={() => addToast({ type: "success", title: "Operation Completed", message: "Dataset validated successfully." })}
            className="px-3.5 py-1.5 text-xs font-semibold rounded-lg bg-emerald-500/15 text-emerald-400 border border-emerald-500/30 hover:bg-emerald-500/25"
          >
            Trigger Success Toast
          </button>
          <button
            onClick={() => addToast({ type: "warning", title: "Monitoring Warning", message: "Rule R1: SPI dropped below 0.85 threshold." })}
            className="px-3.5 py-1.5 text-xs font-semibold rounded-lg bg-yellow-500/15 text-yellow-400 border border-yellow-500/30 hover:bg-yellow-500/25"
          >
            Trigger Warning Toast
          </button>
          <button
            onClick={() => addToast({ type: "critical", title: "CRITICAL ALERT", message: "Rule R3: High model risk surge on PRJ-RAIL-00102." })}
            className="px-3.5 py-1.5 text-xs font-semibold rounded-lg bg-red-500/15 text-red-400 border border-red-500/30 hover:bg-red-500/25"
          >
            Trigger Critical Toast
          </button>
          <button
            onClick={() => addToast({ type: "info", title: "Monthly Cycle Advance", message: "Simulating next cycle." })}
            className="px-3.5 py-1.5 text-xs font-semibold rounded-lg bg-cyan-500/15 text-cyan-400 border border-cyan-500/30 hover:bg-cyan-500/25"
          >
            Trigger Info Toast
          </button>
        </div>
      </section>

      {/* Quick-Peek Drawer Instance */}
      <Drawer
        open={drawerOpen}
        onClose={() => setDrawerOpen(false)}
        title="Project Quick-Peek: PRJ-RAIL-00102"
        subtitle="Dedicated Freight Corridor Western Alignment"
      >
        <div className="space-y-6">
          <div className="flex items-center justify-between p-4 bg-raised rounded-xl border border-border">
            <div>
              <span className="text-xs text-muted">Current Calibrated Risk</span>
              <div className="text-2xl font-black font-mono text-red-400">88.5 / 100</div>
            </div>
            <RiskBadge band="Critical" score={88.5} size="lg" />
          </div>

          <div className="space-y-2">
            <h4 className="text-xs font-semibold text-text uppercase tracking-wider text-muted">Key Asset Attributes</h4>
            <div className="grid grid-cols-2 gap-3 text-xs">
              <div className="p-3 bg-surface border border-border rounded-lg">
                <span className="text-muted block text-[10px]">Ministry</span>
                <span className="font-semibold text-text">Ministry of Railways</span>
              </div>
              <div className="p-3 bg-surface border border-border rounded-lg">
                <span className="text-muted block text-[10px]">Original Sanction</span>
                <span className="font-semibold text-text">₹12,450 Cr</span>
              </div>
              <div className="p-3 bg-surface border border-border rounded-lg">
                <span className="text-muted block text-[10px]">Physical Progress</span>
                <span className="font-semibold text-text">54.2%</span>
              </div>
              <div className="p-3 bg-surface border border-border rounded-lg">
                <span className="text-muted block text-[10px]">Active Warnings</span>
                <span className="font-semibold text-red-400">3 Open Alerts</span>
              </div>
            </div>
          </div>

          <div className="p-4 bg-amber-500/10 border border-amber-500/30 rounded-xl">
            <h4 className="text-xs font-bold text-amber-400 mb-1">Active Causal Bottlenecks</h4>
            <p className="text-xs text-muted leading-relaxed">
              Land acquisition delays in 3 river bridge approach corridors and contractor cashflow distress on Package C.
            </p>
          </div>
        </div>
      </Drawer>
    </div>
  );
}
