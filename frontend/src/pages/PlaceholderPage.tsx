import React from "react";
import { Link } from "react-router-dom";
import { Construction, ArrowLeft, Palette } from "lucide-react";

interface PlaceholderProps {
  title: string;
  phase: string;
  description: string;
}

export function PlaceholderPage({ title, phase, description }: PlaceholderProps) {
  return (
    <div className="min-h-[500px] flex flex-col items-center justify-center p-8 bg-surface border border-border rounded-2xl text-center select-none">
      <div className="w-14 h-14 rounded-2xl bg-accent/15 border border-accent/40 flex items-center justify-center text-accent mb-4 shadow-[0_0_20px_rgba(34,211,238,0.2)]">
        <Construction className="w-7 h-7" />
      </div>
      <div className="inline-flex items-center gap-1.5 px-3 py-1 rounded-full text-xs font-semibold bg-raised border border-border text-muted mb-2">
        <span>Target Phase: {phase}</span>
      </div>
      <h1 className="text-xl font-black text-text tracking-tight mb-2">{title}</h1>
      <p className="text-xs text-muted max-w-md mb-6 leading-relaxed">{description}</p>
      <div className="flex items-center gap-3">
        <Link
          to="/"
          className="inline-flex items-center gap-2 px-4 py-2 rounded-lg bg-raised hover:bg-raised/80 border border-border text-xs font-medium text-text transition-colors"
        >
          <ArrowLeft className="w-4 h-4" />
          <span>Back to Command Center</span>
        </Link>
        <Link
          to="/dev/components"
          className="inline-flex items-center gap-2 px-4 py-2 rounded-lg bg-accent text-background text-xs font-bold transition-all shadow-md shadow-accent/20"
        >
          <Palette className="w-4 h-4" />
          <span>Component Library Showcase</span>
        </Link>
      </div>
    </div>
  );
}
