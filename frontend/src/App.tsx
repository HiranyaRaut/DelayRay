import React, { useState, useEffect } from "react";
import { 
  Activity, 
  ShieldCheck, 
  Database, 
  Cpu, 
  Server, 
  RefreshCw, 
  CheckCircle2, 
  Moon, 
  Sun,
  Layers,
  Terminal,
  Clock,
  Sparkles
} from "lucide-react";
import { SyntheticBadge } from "./components/SyntheticBadge";
import { fetchHealth, fetchApiV1Health, HealthStatus } from "./lib/api";

export function App() {
  const [rootHealth, setRootHealth] = useState<HealthStatus | null>(null);
  const [apiHealth, setApiHealth] = useState<HealthStatus | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [isDark, setIsDark] = useState(true);

  const checkHealth = async () => {
    setLoading(true);
    setError(null);
    try {
      const [rootData, apiData] = await Promise.all([
        fetchHealth(),
        fetchApiV1Health()
      ]);
      setRootHealth(rootData);
      setApiHealth(apiData);
    } catch (err: any) {
      console.error("Health check error:", err);
      setError(err?.message || "Failed to connect to DelayRay API server.");
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    checkHealth();
    const interval = setInterval(checkHealth, 30000);
    return () => clearInterval(interval);
  }, []);

  const toggleTheme = () => {
    setIsDark(!isDark);
    if (isDark) {
      document.documentElement.classList.remove("dark");
    } else {
      document.documentElement.classList.add("dark");
    }
  };

  return (
    <div className="min-h-screen bg-background text-text flex flex-col font-sans transition-colors duration-200">
      {/* Top Navigation Bar */}
      <header className="sticky top-0 z-50 border-b border-border bg-surface/80 backdrop-blur-md px-6 py-3.5 flex items-center justify-between">
        <div className="flex items-center gap-3">
          <div className="h-9 w-9 rounded-lg bg-accent/15 border border-accent/40 flex items-center justify-center text-accent shadow-sm">
            <Activity className="h-5 w-5" />
          </div>
          <div>
            <div className="flex items-center gap-2">
              <span className="font-bold text-lg tracking-tight">DelayRay</span>
              <span className="text-xs px-2 py-0.5 rounded bg-surface border border-border text-muted font-mono">
                v1.0.0
              </span>
            </div>
            <p className="text-xs text-muted">
              AI Early Warning & Predictive Intelligence System
            </p>
          </div>
        </div>

        <div className="flex items-center gap-4">
          <SyntheticBadge />

          <button
            onClick={toggleTheme}
            aria-label="Toggle theme"
            className="p-2 rounded-lg border border-border bg-surface hover:bg-raised text-muted hover:text-text transition-colors"
          >
            {isDark ? <Sun className="w-4 h-4 text-amber-400" /> : <Moon className="w-4 h-4 text-cyan-600" />}
          </button>

          <button
            onClick={checkHealth}
            disabled={loading}
            className="flex items-center gap-1.5 px-3 py-1.5 text-xs font-medium rounded-lg border border-border bg-surface hover:bg-raised text-muted hover:text-text transition-colors disabled:opacity-50"
          >
            <RefreshCw className={`w-3.5 h-3.5 ${loading ? "animate-spin text-accent" : ""}`} />
            <span>Refresh</span>
          </button>
        </div>
      </header>

      {/* Main Content Area */}
      <main className="flex-1 max-w-7xl w-full mx-auto p-6 md:p-8 space-y-6">
        {/* Banner Alert if API is disconnected */}
        {error && (
          <div className="p-4 rounded-lg bg-red-500/10 border border-red-500/30 text-red-400 text-sm flex items-center justify-between">
            <div className="flex items-center gap-2">
              <span className="font-semibold">Backend Unreachable:</span>
              <span>{error}</span>
            </div>
            <button
              onClick={checkHealth}
              className="text-xs underline hover:no-underline font-mono"
            >
              Retry Connection
            </button>
          </div>
        )}

        {/* Hero System Status Card */}
        <section className="p-6 rounded-lg bg-surface border border-border relative overflow-hidden shadow-sm">
          <div className="absolute top-0 right-0 w-96 h-96 bg-accent/5 rounded-full blur-3xl pointer-events-none" />
          
          <div className="flex flex-col md:flex-row md:items-center justify-between gap-4 pb-6 border-b border-border/60">
            <div>
              <div className="flex items-center gap-2.5">
                <span className="relative flex h-3 w-3">
                  <span className={`animate-ping absolute inline-flex h-full w-full rounded-full ${rootHealth ? "bg-emerald-400" : "bg-red-400"} opacity-75`}></span>
                  <span className={`relative inline-flex rounded-full h-3 w-3 ${rootHealth ? "bg-emerald-500" : "bg-red-500"}`}></span>
                </span>
                <h1 className="text-xl font-bold tracking-tight">
                  {rootHealth ? "System Services Operational" : "Awaiting API Connection"}
                </h1>
              </div>
              <p className="text-sm text-muted mt-1">
                Scaffold Phase 0 initialized. FastAPI backend and Vite React dashboard communicating successfully.
              </p>
            </div>

            <div className="flex items-center gap-3">
              <div className="px-3 py-1.5 rounded-lg bg-raised border border-border text-xs">
                <span className="text-muted">Environment: </span>
                <span className="font-mono font-medium text-accent">
                  {rootHealth?.environment || "connecting..."}
                </span>
              </div>
              <div className="px-3 py-1.5 rounded-lg bg-raised border border-border text-xs">
                <span className="text-muted">Demo Mode: </span>
                <span className="font-mono font-medium text-emerald-400">
                  {rootHealth?.demo_mode ? "ACTIVE" : "INACTIVE"}
                </span>
              </div>
            </div>
          </div>

          {/* Service Diagnostic Grid */}
          <div className="grid grid-cols-1 md:grid-cols-4 gap-4 mt-6">
            <div className="p-4 rounded-lg bg-raised/50 border border-border flex flex-col justify-between">
              <div className="flex items-center justify-between text-muted text-xs">
                <span>FastAPI Service</span>
                <Server className="w-4 h-4 text-accent" />
              </div>
              <div className="mt-3">
                <div className="text-base font-semibold">
                  {rootHealth?.service || "FastAPI Core"}
                </div>
                <div className="text-xs text-muted font-mono mt-0.5">
                  Route: /health
                </div>
              </div>
              <div className="mt-4 pt-2 border-t border-border/40 flex items-center gap-1.5 text-xs text-emerald-400">
                <CheckCircle2 className="w-3.5 h-3.5" />
                <span>HTTP 200 OK</span>
              </div>
            </div>

            <div className="p-4 rounded-lg bg-raised/50 border border-border flex flex-col justify-between">
              <div className="flex items-center justify-between text-muted text-xs">
                <span>Database Engine</span>
                <Database className="w-4 h-4 text-cyan-400" />
              </div>
              <div className="mt-3">
                <div className="text-base font-semibold">
                  SQLite (WAL Mode)
                </div>
                <div className="text-xs text-muted font-mono mt-0.5">
                  {apiHealth?.database || "PostgreSQL Ready"}
                </div>
              </div>
              <div className="mt-4 pt-2 border-t border-border/40 flex items-center gap-1.5 text-xs text-emerald-400">
                <CheckCircle2 className="w-3.5 h-3.5" />
                <span>Session Active</span>
              </div>
            </div>

            <div className="p-4 rounded-lg bg-raised/50 border border-border flex flex-col justify-between">
              <div className="flex items-center justify-between text-muted text-xs">
                <span>Analytical LLM</span>
                <Cpu className="w-4 h-4 text-purple-400" />
              </div>
              <div className="mt-3">
                <div className="text-base font-semibold">
                  {apiHealth?.llm_backend || "Ollama (llama3.1:8b)"}
                </div>
                <div className="text-xs text-muted font-mono mt-0.5">
                  Fallback: Deterministic
                </div>
              </div>
              <div className="mt-4 pt-2 border-t border-border/40 flex items-center gap-1.5 text-xs text-emerald-400">
                <ShieldCheck className="w-3.5 h-3.5" />
                <span>Guarded SQL Ready</span>
              </div>
            </div>

            <div className="p-4 rounded-lg bg-raised/50 border border-border flex flex-col justify-between">
              <div className="flex items-center justify-between text-muted text-xs">
                <span>Last Telemetry</span>
                <Clock className="w-4 h-4 text-amber-400" />
              </div>
              <div className="mt-3">
                <div className="text-base font-semibold font-mono text-sm">
                  {rootHealth?.timestamp ? new Date(rootHealth.timestamp).toLocaleTimeString() : "--:--:--"}
                </div>
                <div className="text-xs text-muted font-mono mt-0.5">
                  Auto-refresh: 30s
                </div>
              </div>
              <div className="mt-4 pt-2 border-t border-border/40 flex items-center gap-1.5 text-xs text-emerald-400">
                <CheckCircle2 className="w-3.5 h-3.5" />
                <span>Synced</span>
              </div>
            </div>
          </div>
        </section>

        {/* Phase Roadmap Card */}
        <section className="p-6 rounded-lg bg-surface border border-border">
          <div className="flex items-center justify-between mb-4">
            <div className="flex items-center gap-2">
              <Layers className="w-5 h-5 text-accent" />
              <h2 className="text-base font-semibold">Build Phase Status</h2>
            </div>
            <span className="text-xs px-2.5 py-1 rounded bg-raised border border-border font-mono text-muted">
              Target: MoSPI PAIMANA (1,981 Projects)
            </span>
          </div>

          <div className="space-y-3">
            <div className="p-3.5 rounded-lg bg-raised border border-accent/40 flex items-center justify-between">
              <div className="flex items-center gap-3">
                <div className="h-6 w-6 rounded-full bg-accent/20 border border-accent text-accent flex items-center justify-center text-xs font-bold font-mono">
                  0
                </div>
                <div>
                  <div className="text-sm font-semibold flex items-center gap-2">
                    <span>Phase 0: Plan and Scaffold</span>
                    <span className="text-xs px-2 py-0.5 rounded bg-emerald-500/10 text-emerald-400 border border-emerald-500/30">
                      CURRENT
                    </span>
                  </div>
                  <div className="text-xs text-muted">
                    Implementation plan, repo skeleton, pinned dependencies, Docker skeleton, and live health ping.
                  </div>
                </div>
              </div>
              <CheckCircle2 className="w-5 h-5 text-emerald-400 shrink-0" />
            </div>

            <div className="p-3 rounded-lg bg-raised/30 border border-border/60 flex items-center justify-between opacity-80">
              <div className="flex items-center gap-3">
                <div className="h-6 w-6 rounded-full bg-surface border border-border text-muted flex items-center justify-center text-xs font-bold font-mono">
                  1
                </div>
                <div>
                  <div className="text-sm font-medium">Phase 1: Data and Database</div>
                  <div className="text-xs text-muted">
                    Synthetic data generator (7.5k completed + 1,981 ongoing), SQLAlchemy models, SQL views, seed script.
                  </div>
                </div>
              </div>
              <span className="text-xs text-muted font-mono">Next</span>
            </div>

            <div className="p-3 rounded-lg bg-raised/30 border border-border/60 flex items-center justify-between opacity-60">
              <div className="flex items-center gap-3">
                <div className="h-6 w-6 rounded-full bg-surface border border-border text-muted flex items-center justify-center text-xs font-bold font-mono">
                  2
                </div>
                <div>
                  <div className="text-sm font-medium">Phase 2: ML Pipeline, Evaluation and Ablation</div>
                  <div className="text-xs text-muted">
                    Leakage tests, statistical baselines, tree ensembles, Optuna, isotonic 0-100 scores, CUF attribution.
                  </div>
                </div>
              </div>
              <span className="text-xs text-muted font-mono">Pending</span>
            </div>

            <div className="p-3 rounded-lg bg-raised/30 border border-border/60 flex items-center justify-between opacity-40">
              <div className="flex items-center gap-3">
                <div className="h-6 w-6 rounded-full bg-surface border border-border text-muted flex items-center justify-center text-xs font-bold font-mono">
                  3-9
                </div>
                <div>
                  <div className="text-sm font-medium">Phases 3-9: EWS Engine, Frontend Pages, Assistant, Packaging</div>
                  <div className="text-xs text-muted">
                    REST API, Mission Control UI, S-Curves, Model Arena, Ablation Lab, Guarded Local LLM, Docker Demo.
                  </div>
                </div>
              </div>
              <span className="text-xs text-muted font-mono">Pending</span>
            </div>
          </div>
        </section>

        {/* Footer Advisory */}
        <footer className="pt-4 border-t border-border/60 flex flex-col md:flex-row items-center justify-between gap-3 text-xs text-muted">
          <div>
            <span>DelayRay © 2026. Built with Python, FastAPI, React, and Open-Source ML.</span>
          </div>
          <div className="flex items-center gap-4">
            <span className="font-mono">Advisory decision-support system</span>
            <a href="/docs" target="_blank" rel="noreferrer" className="text-accent hover:underline flex items-center gap-1">
              <Terminal className="w-3.5 h-3.5" />
              <span>API Docs (/docs)</span>
            </a>
          </div>
        </footer>
      </main>
    </div>
  );
}
export default App;
