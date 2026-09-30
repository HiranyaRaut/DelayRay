import React, { useState } from "react";
import { Link } from "react-router-dom";
import {
  ShieldAlert,
  CheckCircle2,
  Clock,
  UserCheck,
  AlertCircle,
  Filter,
  Check,
  ArrowRight,
  RefreshCw,
  Search,
  ExternalLink,
} from "lucide-react";
import { RiskBadge } from "../components/ui/RiskBadge";
import { useAlerts } from "../hooks/useApi";
import { api } from "../lib/api";
import { useAppStore } from "../stores/appStore";

export function Alerts() {
  const addToast = useAppStore((s) => s.addToast);
  const [viewMode, setViewMode] = useState<"board" | "list">("board");
  const [severityFilter, setSeverityFilter] = useState<string>("");
  const [statusFilter, setStatusFilter] = useState<string>("");
  const [search, setSearch] = useState("");

  const { data: alertsData, isLoading, refetch } = useAlerts({
    severity: severityFilter || undefined,
    status: statusFilter || undefined,
    limit: 100,
  });

  const handleUpdateStatus = async (alertId: string, newStatus: string) => {
    try {
      await api.updateAlertStatus(alertId, newStatus, `Transitioned via Early Warning Center.`);
      addToast({
        type: "success",
        title: "Alert Updated",
        message: `Alert ${alertId} updated to ${newStatus}.`,
      });
      refetch();
    } catch (err: any) {
      addToast({
        type: "error",
        title: "Update Failed",
        message: err.message || "Failed to update alert status.",
      });
    }
  };

  const filteredItems = (alertsData?.items || []).filter((item) => {
    if (!search) return true;
    return (
      item.title.toLowerCase().includes(search.toLowerCase()) ||
      item.project_id.toLowerCase().includes(search.toLowerCase()) ||
      item.rule_id.toLowerCase().includes(search.toLowerCase())
    );
  });

  const columns = [
    { id: "new", title: "New Alerts", color: "border-critical/50 text-critical" },
    { id: "acknowledged", title: "Acknowledged", color: "border-warning/50 text-warning" },
    { id: "assigned", title: "Assigned for Action", color: "border-accent/50 text-accent" },
    { id: "resolved", title: "Resolved", color: "border-emerald-500/50 text-emerald-400" },
  ];

  return (
    <div className="space-y-6 max-w-7xl mx-auto pb-16">
      {/* Header */}
      <div className="flex flex-wrap items-center justify-between gap-4 p-6 bg-surface border border-border rounded-xl">
        <div>
          <div className="flex items-center gap-2.5">
            <h1 className="text-2xl font-black text-text tracking-tight">Early Warning Center</h1>
            <span className="text-[11px] font-mono px-2 py-0.5 rounded bg-raised border border-border text-critical font-bold">
              {alertsData?.total || 406} Active Triggers
            </span>
          </div>
          <p className="text-xs text-muted mt-1">
            Rules engine (R1–R8) monitoring physical velocity, expenditure anomalies, land bottlenecks, and contractor distress.
          </p>
        </div>

        <div className="flex items-center gap-3">
          <div className="flex items-center bg-raised rounded-lg p-1 border border-border text-xs">
            <button
              onClick={() => setViewMode("board")}
              className={`px-3 py-1.5 rounded-md font-semibold transition-colors ${
                viewMode === "board" ? "bg-accent text-background" : "text-muted hover:text-text"
              }`}
            >
              Lifecycle Board
            </button>
            <button
              onClick={() => setViewMode("list")}
              className={`px-3 py-1.5 rounded-md font-semibold transition-colors ${
                viewMode === "list" ? "bg-accent text-background" : "text-muted hover:text-text"
              }`}
            >
              Table Feed
            </button>
          </div>

          <button
            onClick={() => refetch()}
            className="p-2 rounded-lg bg-raised hover:bg-raised/80 border border-border text-muted hover:text-text"
            title="Refresh Alerts"
          >
            <RefreshCw className="w-4 h-4" />
          </button>
        </div>
      </div>

      {/* Filter Bar */}
      <div className="flex flex-wrap items-center gap-3 bg-surface border border-border rounded-xl p-3.5 text-xs">
        <div className="relative flex-1 min-w-[200px]">
          <Search className="w-3.5 h-3.5 absolute left-3 top-2.5 text-muted" />
          <input
            type="text"
            placeholder="Search alerts by project, title, or rule..."
            value={search}
            onChange={(e) => setSearch(e.target.value)}
            className="w-full pl-8 pr-3 py-1.5 bg-raised/50 border border-border rounded-lg text-text focus:outline-none focus:border-accent"
          />
        </div>

        <select
          value={severityFilter}
          onChange={(e) => setSeverityFilter(e.target.value)}
          className="px-3 py-1.5 bg-raised/50 border border-border rounded-lg text-text focus:outline-none focus:border-accent"
        >
          <option value="">All Severities</option>
          <option value="Critical">Critical</option>
          <option value="High">High</option>
          <option value="Moderate">Moderate</option>
          <option value="Low">Low</option>
        </select>

        {viewMode === "list" && (
          <select
            value={statusFilter}
            onChange={(e) => setStatusFilter(e.target.value)}
            className="px-3 py-1.5 bg-raised/50 border border-border rounded-lg text-text focus:outline-none focus:border-accent"
          >
            <option value="">All Lifecycle Statuses</option>
            <option value="new">New</option>
            <option value="acknowledged">Acknowledged</option>
            <option value="assigned">Assigned</option>
            <option value="resolved">Resolved</option>
          </select>
        )}
      </div>

      {/* Lifecycle Kanban Board View */}
      {viewMode === "board" ? (
        <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
          {columns.map((col) => {
            const items = filteredItems.filter((i) => i.status === col.id);
            return (
              <div key={col.id} className="bg-surface border border-border rounded-xl flex flex-col h-[700px] overflow-hidden">
                <div className={`p-3.5 border-b border-border bg-raised/40 flex items-center justify-between ${col.color}`}>
                  <span className="font-bold text-xs uppercase tracking-wider">{col.title}</span>
                  <span className="px-2 py-0.5 rounded-full bg-raised border border-border text-[11px] font-mono font-bold text-text">
                    {items.length}
                  </span>
                </div>

                <div className="flex-1 p-3 space-y-3 overflow-y-auto">
                  {isLoading ? (
                    <div className="text-center text-xs text-muted py-8">Loading alerts...</div>
                  ) : items.length === 0 ? (
                    <div className="text-center text-xs text-muted/60 py-12 border border-dashed border-border/60 rounded-lg">
                      No alerts in this stage
                    </div>
                  ) : (
                    items.map((item) => (
                      <div
                        key={item.id}
                        className="p-3 bg-raised/50 border border-border rounded-xl space-y-2 hover:border-accent/40 transition-colors"
                      >
                        <div className="flex items-center justify-between text-[11px]">
                          <RiskBadge band={item.severity as any} size="sm" />
                          <span className="font-mono text-muted">{item.rule_id}</span>
                        </div>

                        <div>
                          <div className="text-xs font-bold text-text line-clamp-2">{item.title}</div>
                          <Link
                            to={`/projects/${item.project_id}`}
                            className="text-[11px] font-mono text-accent hover:underline flex items-center gap-1 mt-0.5"
                          >
                            <span>{item.project_id}</span>
                            <ExternalLink className="w-2.5 h-2.5" />
                          </Link>
                        </div>

                        <p className="text-[11px] text-muted line-clamp-2">{item.description}</p>

                        {/* Action buttons to transition lifecycle */}
                        <div className="pt-2 border-t border-border/50 flex items-center justify-between text-[11px]">
                          {col.id === "new" && (
                            <button
                              onClick={() => handleUpdateStatus(item.id, "acknowledged")}
                              className="px-2.5 py-1 rounded bg-raised hover:bg-raised/80 border border-border text-text font-semibold flex items-center gap-1"
                            >
                              <Check className="w-3 h-3 text-warning" />
                              <span>Acknowledge</span>
                            </button>
                          )}
                          {col.id === "acknowledged" && (
                            <button
                              onClick={() => handleUpdateStatus(item.id, "assigned")}
                              className="px-2.5 py-1 rounded bg-raised hover:bg-raised/80 border border-border text-text font-semibold flex items-center gap-1"
                            >
                              <UserCheck className="w-3 h-3 text-accent" />
                              <span>Assign Action</span>
                            </button>
                          )}
                          {col.id === "assigned" && (
                            <button
                              onClick={() => handleUpdateStatus(item.id, "resolved")}
                              className="px-2.5 py-1 rounded bg-emerald-500/20 hover:bg-emerald-500/30 border border-emerald-500/40 text-emerald-400 font-semibold flex items-center gap-1"
                            >
                              <CheckCircle2 className="w-3 h-3" />
                              <span>Resolve</span>
                            </button>
                          )}
                          {col.id === "resolved" && (
                            <span className="text-emerald-400 font-semibold flex items-center gap-1">
                              <CheckCircle2 className="w-3 h-3" />
                              Resolved
                            </span>
                          )}

                          <Link
                            to={`/projects/${item.project_id}`}
                            className="text-muted hover:text-text p-1"
                            title="Drill into Project"
                          >
                            <ArrowRight className="w-3.5 h-3.5" />
                          </Link>
                        </div>
                      </div>
                    ))
                  )}
                </div>
              </div>
            );
          })}
        </div>
      ) : (
        /* Table Feed View */
        <div className="bg-surface border border-border rounded-xl overflow-hidden">
          <table className="w-full text-left text-xs">
            <thead className="bg-raised/60 border-b border-border text-muted font-bold text-[10px] uppercase">
              <tr>
                <th className="p-3.5">Severity</th>
                <th className="p-3.5">Alert Title</th>
                <th className="p-3.5">Rule</th>
                <th className="p-3.5">Project ID</th>
                <th className="p-3.5">Status</th>
                <th className="p-3.5 text-center">Lifecycle Action</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-border/60">
              {filteredItems.map((item) => (
                <tr key={item.id} className="hover:bg-raised/40 transition-colors">
                  <td className="p-3.5">
                    <RiskBadge band={item.severity as any} size="sm" />
                  </td>
                  <td className="p-3.5 font-semibold text-text max-w-sm">
                    <div>{item.title}</div>
                    <div className="text-[11px] text-muted font-normal truncate">{item.description}</div>
                  </td>
                  <td className="p-3.5 font-mono text-[11px] text-muted">{item.rule_id}</td>
                  <td className="p-3.5 font-mono text-[11px]">
                    <Link to={`/projects/${item.project_id}`} className="text-accent hover:underline">
                      {item.project_id}
                    </Link>
                  </td>
                  <td className="p-3.5">
                    <span className="capitalize px-2 py-0.5 rounded bg-raised border border-border text-[11px]">
                      {item.status}
                    </span>
                  </td>
                  <td className="p-3.5 text-center">
                    {item.status === "new" && (
                      <button
                        onClick={() => handleUpdateStatus(item.id, "acknowledged")}
                        className="px-2.5 py-1 rounded bg-raised border border-border text-xs font-semibold hover:bg-raised/80"
                      >
                        Acknowledge
                      </button>
                    )}
                    {item.status === "acknowledged" && (
                      <button
                        onClick={() => handleUpdateStatus(item.id, "assigned")}
                        className="px-2.5 py-1 rounded bg-raised border border-border text-xs font-semibold hover:bg-raised/80 text-accent"
                      >
                        Assign
                      </button>
                    )}
                    {item.status === "assigned" && (
                      <button
                        onClick={() => handleUpdateStatus(item.id, "resolved")}
                        className="px-2.5 py-1 rounded bg-emerald-500/20 border border-emerald-500/40 text-emerald-400 text-xs font-semibold"
                      >
                        Resolve
                      </button>
                    )}
                    {item.status === "resolved" && (
                      <span className="text-emerald-400 font-mono text-[11px]">Closed</span>
                    )}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
    </div>
  );
}
