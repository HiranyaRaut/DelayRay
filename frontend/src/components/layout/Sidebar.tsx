import React from "react";
import { NavLink } from "react-router-dom";
import {
  LayoutDashboard,
  FolderKanban,
  Flame,
  Brain,
  Scale,
  BarChart2,
  MessageSquare,
  Shield,
  Palette,
  LogOut,
  Radio,
  ExternalLink,
} from "lucide-react";
import { useAuthStore } from "../../stores/authStore";
import { useAppStore } from "../../stores/appStore";
import { t } from "../../i18n";
import { cn } from "../../lib/utils";

interface NavItem {
  to: string;
  labelKey: any;
  fallback: string;
  icon: React.ReactNode;
  badge?: string;
}

export function Sidebar() {
  const language = useAppStore((s) => s.language);
  const presentationMode = useAppStore((s) => s.presentationMode);
  const user = useAuthStore((s) => s.user);
  const role = useAuthStore((s) => s.role);
  const logout = useAuthStore((s) => s.logout);

  if (presentationMode) return null;

  const navItems: NavItem[] = [
    {
      to: "/",
      labelKey: "nav_command_center",
      fallback: "Command Center",
      icon: <LayoutDashboard className="w-4 h-4" />,
    },
    {
      to: "/projects",
      labelKey: "nav_projects",
      fallback: "Projects",
      icon: <FolderKanban className="w-4 h-4" />,
    },
    {
      to: "/alerts",
      labelKey: "nav_alerts",
      fallback: "Early Warning Center",
      icon: <Flame className="w-4 h-4" />,
      badge: "406",
    },
    {
      to: "/models",
      labelKey: "nav_models",
      fallback: "Model Arena",
      icon: <Brain className="w-4 h-4" />,
    },
    {
      to: "/ablation",
      labelKey: "nav_ablation",
      fallback: "Ablation Lab",
      icon: <Scale className="w-4 h-4" />,
    },
    {
      to: "/benchmark",
      labelKey: "nav_benchmarking",
      fallback: "Benchmarking",
      icon: <BarChart2 className="w-4 h-4" />,
    },
    {
      to: "/assistant",
      labelKey: "nav_assistant",
      fallback: "Assistant",
      icon: <MessageSquare className="w-4 h-4" />,
    },
    {
      to: "/admin",
      labelKey: "nav_admin",
      fallback: "Data & Admin",
      icon: <Shield className="w-4 h-4" />,
    },
    {
      to: "/dev/components",
      labelKey: "nav_components",
      fallback: "Component Library",
      icon: <Palette className="w-4 h-4" />,
    },
  ];

  return (
    <aside className="w-64 bg-surface border-r border-border flex flex-col justify-between shrink-0 select-none transition-all">
      {/* Brand Header */}
      <div>
        <div className="h-16 px-5 border-b border-border flex items-center justify-between">
          <div className="flex items-center gap-2.5">
            <div className="w-8 h-8 rounded-lg bg-accent/15 border border-accent/40 flex items-center justify-center text-accent shadow-[0_0_12px_rgba(34,211,238,0.25)]">
              <Radio className="w-4 h-4 animate-pulse" />
            </div>
            <div>
              <div className="flex items-center gap-1.5">
                <span className="font-extrabold text-base tracking-tight text-text">DelayRay</span>
                <span className="text-[10px] font-mono px-1.5 py-0.2 rounded bg-raised text-accent border border-border">v1.0</span>
              </div>
              <p className="text-[10px] text-muted tracking-tight">MoSPI PAIMANA Early Warning</p>
            </div>
          </div>
        </div>

        {/* Navigation Links */}
        <nav className="p-3 space-y-1">
          {navItems.map((item) => (
            <NavLink
              key={item.to}
              to={item.to}
              className={({ isActive }) =>
                cn(
                  "flex items-center justify-between px-3.5 py-2.5 rounded-lg text-xs font-medium transition-all group",
                  isActive
                    ? "bg-accent/15 text-accent border border-accent/30 font-semibold shadow-[0_0_10px_rgba(34,211,238,0.15)]"
                    : "text-muted hover:text-text hover:bg-raised/70 border border-transparent"
                )
              }
            >
              <div className="flex items-center gap-3">
                <span className="transition-transform group-hover:scale-110">{item.icon}</span>
                <span>{t(item.labelKey, language)}</span>
              </div>
              {item.badge && (
                <span className="text-[10px] font-mono font-semibold px-2 py-0.5 rounded-full bg-red-500/15 text-red-400 border border-red-500/30">
                  {item.badge}
                </span>
              )}
            </NavLink>
          ))}
        </nav>
      </div>

      {/* User Footer Profile */}
      <div className="p-3 border-t border-border bg-raised/30">
        <div className="flex items-center justify-between p-2 rounded-lg bg-surface border border-border/60">
          <div className="flex items-center gap-2.5 min-w-0">
            <div className="w-8 h-8 rounded-full bg-accent/20 border border-accent/40 flex items-center justify-center font-bold text-accent text-xs">
              {user?.email?.charAt(0).toUpperCase() || "A"}
            </div>
            <div className="min-w-0 flex-1">
              <p className="text-xs font-semibold text-text truncate">{user?.email || "analyst@demo"}</p>
              <span className="text-[10px] uppercase font-mono px-1.5 py-0.2 rounded bg-raised text-muted border border-border">
                {role || "analyst"}
              </span>
            </div>
          </div>

          <button
            onClick={logout}
            title="Sign Out"
            className="p-1.5 rounded-lg text-muted hover:text-red-400 hover:bg-raised transition-colors"
          >
            <LogOut className="w-4 h-4" />
          </button>
        </div>
      </div>
    </aside>
  );
}
