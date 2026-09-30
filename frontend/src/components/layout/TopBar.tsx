import React from "react";
import {
  Search,
  FastForward,
  Sun,
  Moon,
  Languages,
  DollarSign,
  Maximize2,
  Minimize2,
  Bell,
  RefreshCw,
} from "lucide-react";
import { SyntheticBadge } from "../SyntheticBadge";
import { useAppStore } from "../../stores/appStore";
import { useAdvanceMonthMutation } from "../../hooks/useApi";
import { cn } from "../../lib/utils";

export function TopBar() {
  const {
    theme,
    toggleTheme,
    currencyFormat,
    toggleCurrencyFormat,
    language,
    setLanguage,
    presentationMode,
    togglePresentationMode,
    setCommandPaletteOpen,
  } = useAppStore();

  const advanceMonthMutation = useAdvanceMonthMutation();

  return (
    <header className="h-16 px-6 bg-surface border-b border-border flex items-center justify-between gap-4 select-none shrink-0 transition-colors">
      {/* Left: Global Search triggering Command Palette */}
      <div className="flex items-center gap-4 flex-1 max-w-md">
        <button
          onClick={() => setCommandPaletteOpen(true)}
          className="w-full flex items-center justify-between px-3.5 py-1.5 rounded-lg bg-raised border border-border text-xs text-muted hover:border-accent/50 hover:text-text transition-all group"
        >
          <div className="flex items-center gap-2.5">
            <Search className="w-3.5 h-3.5 text-muted group-hover:text-accent transition-colors" />
            <span>Search portfolio, projects, rules...</span>
          </div>
          <kbd className="hidden sm:inline-flex items-center gap-1 font-mono text-[10px] px-1.5 py-0.5 rounded bg-surface border border-border text-muted">
            <span className="text-xs">⌘</span>K
          </kbd>
        </button>
      </div>

      {/* Center: Persistent Non-Dismissible Synthetic Demo Data Badge */}
      <div className="hidden lg:flex items-center">
        <SyntheticBadge />
      </div>

      {/* Right: Controls & Simulation Actions */}
      <div className="flex items-center gap-2">
        {/* Advance Month Demo Button */}
        <button
          onClick={() => advanceMonthMutation.mutate()}
          disabled={advanceMonthMutation.isPending}
          title="Simulate Next Monthly Cycle (Ingest progress, rescore & trigger alerts)"
          className={cn(
            "inline-flex items-center gap-2 px-3 py-1.5 text-xs font-semibold rounded-lg bg-accent text-background shadow-md hover:bg-accent/90 active:scale-95 transition-all disabled:opacity-50",
            advanceMonthMutation.isPending && "animate-pulse"
          )}
        >
          {advanceMonthMutation.isPending ? (
            <RefreshCw className="w-3.5 h-3.5 animate-spin" />
          ) : (
            <FastForward className="w-3.5 h-3.5" />
          )}
          <span className="hidden sm:inline">Advance Month</span>
        </button>

        {/* Currency Notation Toggle */}
        <button
          onClick={toggleCurrencyFormat}
          title={`Currency format: ${currencyFormat === "in" ? "Indian (₹ Cr / ₹ L)" : "Plain numbers"}`}
          className="p-2 rounded-lg bg-raised border border-border text-muted hover:text-text hover:bg-raised/80 transition-colors"
        >
          <span className="font-mono font-bold text-xs">
            {currencyFormat === "in" ? "₹ Cr" : "#"}
          </span>
        </button>

        {/* Language Toggle */}
        <button
          onClick={() => setLanguage(language === "en" ? "hi" : "en")}
          title={`Switch language (${language === "en" ? "हिन्दी" : "English"})`}
          className="p-2 rounded-lg bg-raised border border-border text-muted hover:text-text hover:bg-raised/80 transition-colors"
        >
          <span className="text-xs font-bold font-mono">
            {language === "en" ? "EN" : "हि"}
          </span>
        </button>

        {/* Presentation Mode Toggle */}
        <button
          onClick={togglePresentationMode}
          title={presentationMode ? "Exit Presentation Mode" : "Enter Presentation Mode"}
          className="p-2 rounded-lg bg-raised border border-border text-muted hover:text-text hover:bg-raised/80 transition-colors"
        >
          {presentationMode ? <Minimize2 className="w-4 h-4" /> : <Maximize2 className="w-4 h-4" />}
        </button>

        {/* Dark / Light Theme Toggle */}
        <button
          onClick={toggleTheme}
          title={`Switch to ${theme === "dark" ? "Light" : "Dark"} mode`}
          className="p-2 rounded-lg bg-raised border border-border text-muted hover:text-text hover:bg-raised/80 transition-colors"
        >
          {theme === "dark" ? (
            <Sun className="w-4 h-4 text-yellow-400" />
          ) : (
            <Moon className="w-4 h-4 text-indigo-400" />
          )}
        </button>
      </div>
    </header>
  );
}
