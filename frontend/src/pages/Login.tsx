import React, { useState } from "react";
import { useNavigate } from "react-router-dom";
import { Radio, Lock, Mail, ArrowRight, ShieldCheck, AlertCircle } from "lucide-react";
import { api } from "../lib/api";
import { useAuthStore } from "../stores/authStore";
import { useAppStore } from "../stores/appStore";

export function Login() {
  const navigate = useNavigate();
  const setAuth = useAuthStore((s) => s.setAuth);
  const addToast = useAppStore((s) => s.addToast);

  const [email, setEmail] = useState("analyst@demo");
  const [password, setPassword] = useState("demo123");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const handleLogin = async (e?: React.FormEvent) => {
    if (e) e.preventDefault();
    setLoading(true);
    setError(null);

    try {
      const tokens = await api.login({ email, password });
      setAuth(tokens);
      addToast({
        type: "success",
        title: "Authenticated Successfully",
        message: `Welcome back, logged in as ${tokens.role.toUpperCase()}.`,
      });
      navigate("/");
    } catch (err: any) {
      setError(err?.message || "Invalid credentials. Please verify your email and password.");
    } finally {
      setLoading(false);
    }
  };

  const handleQuickDemoUser = (userEmail: string) => {
    setEmail(userEmail);
    setPassword("demo123");
  };

  return (
    <div className="min-h-screen w-screen bg-background flex flex-col justify-center items-center p-6 relative overflow-hidden select-none">
      {/* Background Glow */}
      <div className="absolute top-1/4 -left-20 w-96 h-96 bg-accent/10 rounded-full blur-3xl pointer-events-none" />
      <div className="absolute bottom-1/4 -right-20 w-96 h-96 bg-accent/10 rounded-full blur-3xl pointer-events-none" />

      {/* Main Card */}
      <div className="w-full max-w-md bg-surface border border-border rounded-2xl shadow-2xl p-8 z-10">
        {/* Brand Header */}
        <div className="flex flex-col items-center text-center mb-8">
          <div className="w-12 h-12 rounded-xl bg-accent/15 border border-accent/40 flex items-center justify-center text-accent mb-3 shadow-[0_0_20px_rgba(34,211,238,0.25)]">
            <Radio className="w-6 h-6 animate-pulse" />
          </div>
          <h1 className="text-2xl font-black tracking-tight text-text">DelayRay</h1>
          <p className="text-xs text-muted mt-1 max-w-xs leading-relaxed">
            AI-Powered Early Warning System for Central Sector Infrastructure Projects
          </p>
        </div>

        {/* Demo Credentials Chips */}
        <div className="mb-6 p-3 bg-raised/50 border border-border rounded-xl">
          <p className="text-[11px] font-semibold text-muted uppercase tracking-wider mb-2">
            One-Click Demo Credentials:
          </p>
          <div className="flex flex-wrap gap-2">
            {[
              { email: "viewer@demo", label: "Viewer", desc: "Read-only" },
              { email: "analyst@demo", label: "Analyst", desc: "Operational" },
              { email: "admin@demo", label: "Admin", desc: "Full Governance" },
            ].map((d) => (
              <button
                key={d.email}
                type="button"
                onClick={() => handleQuickDemoUser(d.email)}
                className={`flex-1 text-left px-2.5 py-1.5 rounded-lg border text-xs transition-all ${
                  email === d.email
                    ? "bg-accent/15 border-accent text-accent font-semibold"
                    : "bg-surface border-border text-text hover:bg-raised"
                }`}
              >
                <div className="font-semibold">{d.label}</div>
                <div className="text-[10px] text-muted">{d.email}</div>
              </button>
            ))}
          </div>
        </div>

        {/* Form */}
        <form onSubmit={handleLogin} className="space-y-4">
          {error && (
            <div className="flex items-center gap-2 p-3 text-xs text-red-400 bg-red-500/10 border border-red-500/30 rounded-lg">
              <AlertCircle className="w-4 h-4 shrink-0" />
              <span>{error}</span>
            </div>
          )}

          <div>
            <label className="block text-xs font-semibold text-text mb-1.5">Official Email</label>
            <div className="relative">
              <Mail className="absolute left-3 top-2.5 w-4 h-4 text-muted" />
              <input
                type="email"
                required
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                className="w-full pl-9 pr-3 py-2 text-xs bg-raised border border-border rounded-lg text-text focus:outline-none focus:border-accent transition-colors"
                placeholder="analyst@demo"
              />
            </div>
          </div>

          <div>
            <label className="block text-xs font-semibold text-text mb-1.5">Password</label>
            <div className="relative">
              <Lock className="absolute left-3 top-2.5 w-4 h-4 text-muted" />
              <input
                type="password"
                required
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                className="w-full pl-9 pr-3 py-2 text-xs bg-raised border border-border rounded-lg text-text focus:outline-none focus:border-accent transition-colors"
                placeholder="••••••••"
              />
            </div>
          </div>

          <button
            type="submit"
            disabled={loading}
            className="w-full mt-2 py-2.5 px-4 bg-accent hover:bg-accent/90 text-background font-bold text-xs rounded-lg shadow-lg shadow-accent/20 transition-all flex items-center justify-center gap-2 active:scale-95 disabled:opacity-50"
          >
            {loading ? (
              <span className="inline-block w-4 h-4 border-2 border-background border-t-transparent rounded-full animate-spin" />
            ) : (
              <>
                <span>Sign In to Mission Control</span>
                <ArrowRight className="w-4 h-4" />
              </>
            )}
          </button>
        </form>

        {/* Footer Note */}
        <div className="mt-6 pt-4 border-t border-border/60 text-center text-[11px] text-muted flex items-center justify-center gap-1.5">
          <ShieldCheck className="w-3.5 h-3.5 text-accent" />
          <span>Role-Based Access Protected | Offline-First</span>
        </div>
      </div>
    </div>
  );
}
