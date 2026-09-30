import React, { Component, ErrorInfo, ReactNode } from "react";
import { AlertOctagon, RotateCcw } from "lucide-react";

interface Props {
  children: ReactNode;
  fallback?: ReactNode;
}

interface State {
  hasError: boolean;
  error: Error | null;
}

export class ErrorBoundary extends Component<Props, State> {
  public state: State = {
    hasError: false,
    error: null,
  };

  public static getDerivedStateFromError(error: Error): State {
    return { hasError: true, error };
  }

  public componentDidCatch(error: Error, errorInfo: ErrorInfo) {
    console.error("Uncaught React exception in ErrorBoundary:", error, errorInfo);
  }

  private handleReset = () => {
    this.setState({ hasError: false, error: null });
    window.location.reload();
  };

  public render() {
    if (this.state.hasError) {
      if (this.props.fallback) {
        return this.props.fallback;
      }

      return (
        <div className="min-h-[400px] w-full flex flex-col items-center justify-center p-8 bg-surface border border-red-500/20 rounded-xl text-center">
          <div className="w-12 h-12 rounded-full bg-red-500/10 border border-red-500/30 flex items-center justify-center text-red-500 mb-4 shadow-[0_0_20px_rgba(239,68,68,0.2)]">
            <AlertOctagon className="w-6 h-6" />
          </div>
          <h2 className="text-base font-bold text-text mb-1">Application Layout Exception</h2>
          <p className="text-xs text-muted max-w-md mb-4 leading-relaxed">
            An unexpected error occurred while rendering this interface module. Our diagnostic state has captured the event.
          </p>
          <div className="text-[11px] font-mono text-red-400 bg-raised px-4 py-2 rounded-lg border border-border mb-5 max-w-lg overflow-x-auto text-left">
            {this.state.error?.message || "Unknown error"}
          </div>
          <button
            onClick={this.handleReset}
            className="inline-flex items-center gap-2 px-4 py-2 bg-accent text-background font-semibold text-xs rounded-lg shadow-md hover:bg-accent/90 transition-all active:scale-95"
          >
            <RotateCcw className="w-4 h-4" />
            Reload Workspace
          </button>
        </div>
      );
    }

    return this.props.children;
  }
}
