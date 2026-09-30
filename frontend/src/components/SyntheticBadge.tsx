import React from "react";
import { AlertCircle } from "lucide-react";

export const SyntheticBadge: React.FC = () => {
  return (
    <div
      role="status"
      aria-label="Synthetic demo data disclosure"
      className="inline-flex items-center gap-1.5 px-2.5 py-1 rounded-full text-xs font-medium bg-amber-500/10 text-amber-400 border border-amber-500/30 tracking-wide select-none"
    >
      <AlertCircle className="w-3.5 h-3.5 animate-pulse text-amber-400" />
      <span>Synthetic demo data</span>
    </div>
  );
};
