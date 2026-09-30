import React, { useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";
import {
  LayoutDashboard,
  FolderKanban,
  AlertTriangle,
  Flame,
  Brain,
  Scale,
  MessageSquare,
  Shield,
  Palette,
  FastForward,
  Sun,
  Moon,
  Languages,
  DollarSign,
  Search,
  X,
} from "lucide-react";
import { useAppStore } from "../../stores/appStore";
import { useAdvanceMonthMutation } from "../../hooks/useApi";
import { cn } from "../../lib/utils";

interface CommandItem {
  id: string;
  category: "Navigation" | "Simulation" | "Settings";
  title: string;
  subtitle?: string;
  icon: React.ReactNode;
  action: () => void;
}

export function CommandPalette() {
  const navigate = useNavigate();
  const open = useAppStore((s) => s.commandPaletteOpen);
  const setOpen = useAppStore((s) => s.setCommandPaletteOpen);
  const { toggleTheme, theme, language, setLanguage, toggleCurrencyFormat } = useAppStore();
  const advanceMonthMutation = useAdvanceMonthMutation();

  const [query, setQuery] = useState("");
  const [selectedIndex, setSelectedIndex] = useState(0);

  // Keyboard shortcut listener
  useEffect(() => {
    const onKeyDown = (e: KeyboardEvent) => {
      if ((e.ctrlKey || e.metaKey) && e.key.toLowerCase() === "k") {
        e.preventDefault();
        setOpen(!open);
      }
      if (e.key === "Escape" && open) {
        setOpen(false);
      }
    };
    window.addEventListener("keydown", onKeyDown);
    return () => window.removeEventListener("keydown", onKeyDown);
  }, [open, setOpen]);

  if (!open) return null;

  const items: CommandItem[] = [
    // Navigation
    {
      id: "nav-home",
      category: "Navigation",
      title: "Command Center",
      subtitle: "Executive infrastructure portfolio dashboard",
      icon: <LayoutDashboard className="w-4 h-4 text-cyan-400" />,
      action: () => {
        navigate("/");
        setOpen(false);
      },
    },
    {
      id: "nav-projects",
      category: "Navigation",
      title: "Projects Explorer",
      subtitle: "Search, filter & inspect 1,981 central sector projects",
      icon: <FolderKanban className="w-4 h-4 text-emerald-400" />,
      action: () => {
        navigate("/projects");
        setOpen(false);
      },
    },
    {
      id: "nav-alerts",
      category: "Navigation",
      title: "Early Warning Center",
      subtitle: "Active alerts feed & managed lifecycle",
      icon: <Flame className="w-4 h-4 text-red-400" />,
      action: () => {
        navigate("/alerts");
        setOpen(false);
      },
    },
    {
      id: "nav-models",
      category: "Navigation",
      title: "Model Arena",
      subtitle: "Leaderboard & statistical significance verdict",
      icon: <Brain className="w-4 h-4 text-purple-400" />,
      action: () => {
        navigate("/models");
        setOpen(false);
      },
    },
    {
      id: "nav-ablation",
      category: "Navigation",
      title: "Ablation Lab",
      subtitle: "CUF attribution % & ranked field recommendations",
      icon: <Scale className="w-4 h-4 text-amber-400" />,
      action: () => {
        navigate("/ablation");
        setOpen(false);
      },
    },
    {
      id: "nav-dev",
      category: "Navigation",
      title: "Component Library",
      subtitle: "Reusable UI components design showcase",
      icon: <Palette className="w-4 h-4 text-pink-400" />,
      action: () => {
        navigate("/dev/components");
        setOpen(false);
      },
    },

    // Simulation
    {
      id: "act-advance",
      category: "Simulation",
      title: "Advance Monitoring Month",
      subtitle: "Simulate next month, generate snapshots & trigger alerts",
      icon: <FastForward className="w-4 h-4 text-cyan-400 animate-pulse" />,
      action: () => {
        advanceMonthMutation.mutate();
        setOpen(false);
      },
    },

    // Settings
    {
      id: "set-theme",
      category: "Settings",
      title: `Toggle Theme (${theme === "dark" ? "Switch to Light" : "Switch to Dark"})`,
      icon: theme === "dark" ? <Sun className="w-4 h-4 text-yellow-400" /> : <Moon className="w-4 h-4 text-indigo-400" />,
      action: () => {
        toggleTheme();
        setOpen(false);
      },
    },
    {
      id: "set-lang",
      category: "Settings",
      title: `Switch Language (${language === "en" ? "हिन्दी (Hindi)" : "English"})`,
      icon: <Languages className="w-4 h-4 text-teal-400" />,
      action: () => {
        setLanguage(language === "en" ? "hi" : "en");
        setOpen(false);
      },
    },
    {
      id: "set-currency",
      category: "Settings",
      title: "Toggle Currency Notation (₹ Crore vs Plain)",
      icon: <DollarSign className="w-4 h-4 text-emerald-400" />,
      action: () => {
        toggleCurrencyFormat();
        setOpen(false);
      },
    },
  ];

  const filtered = items.filter(
    (item) =>
      item.title.toLowerCase().includes(query.toLowerCase()) ||
      item.category.toLowerCase().includes(query.toLowerCase()) ||
      (item.subtitle && item.subtitle.toLowerCase().includes(query.toLowerCase()))
  );

  return (
    <div className="fixed inset-0 z-50 flex items-start justify-center pt-24 px-4 bg-black/60 backdrop-blur-sm">
      <div
        className="w-full max-w-xl bg-surface border border-border rounded-xl shadow-2xl overflow-hidden animate-in fade-in zoom-in-95 duration-150"
        onClick={(e) => e.stopPropagation()}
      >
        {/* Input bar */}
        <div className="flex items-center px-4 py-3.5 border-b border-border bg-raised/50">
          <Search className="w-4 h-4 text-muted mr-3 shrink-0" />
          <input
            type="text"
            placeholder="Type a command or jump to page... (ESC to close)"
            value={query}
            onChange={(e) => {
              setQuery(e.target.value);
              setSelectedIndex(0);
            }}
            autoFocus
            className="w-full bg-transparent text-sm text-text placeholder:text-muted focus:outline-none"
          />
          <button
            onClick={() => setOpen(false)}
            className="p-1 rounded text-muted hover:text-text transition-colors"
          >
            <X className="w-4 h-4" />
          </button>
        </div>

        {/* Results List */}
        <div className="max-h-80 overflow-y-auto p-2 space-y-1">
          {filtered.length === 0 ? (
            <div className="py-8 text-center text-xs text-muted">
              No matching commands or destinations found.
            </div>
          ) : (
            filtered.map((item, idx) => (
              <div
                key={item.id}
                onClick={item.action}
                onMouseEnter={() => setSelectedIndex(idx)}
                className={cn(
                  "flex items-center justify-between p-3 rounded-lg text-xs cursor-pointer transition-colors",
                  idx === selectedIndex ? "bg-accent/15 text-accent" : "hover:bg-raised/70 text-text"
                )}
              >
                <div className="flex items-center gap-3">
                  <div className="p-1.5 rounded-md bg-raised border border-border/50">
                    {item.icon}
                  </div>
                  <div>
                    <p className="font-semibold text-text">{item.title}</p>
                    {item.subtitle && <p className="text-[11px] text-muted">{item.subtitle}</p>}
                  </div>
                </div>
                <span className="text-[10px] uppercase font-mono px-2 py-0.5 rounded bg-raised border border-border text-muted">
                  {item.category}
                </span>
              </div>
            ))
          )}
        </div>

        {/* Footer */}
        <div className="px-4 py-2 border-t border-border bg-raised/30 flex items-center justify-between text-[11px] text-muted">
          <span>Use <b>↑</b> <b>↓</b> to navigate, <b>Enter</b> to select</span>
          <span className="font-mono">DelayRay v1.0</span>
        </div>
      </div>
    </div>
  );
}
