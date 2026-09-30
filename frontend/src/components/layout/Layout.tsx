import React from "react";
import { Outlet } from "react-router-dom";
import { Sidebar } from "./Sidebar";
import { TopBar } from "./TopBar";
import { CommandPalette } from "../ui/CommandPalette";
import { ToastContainer } from "../ui/ToastContainer";
import { ErrorBoundary } from "../ui/ErrorBoundary";

export function Layout() {
  return (
    <div className="flex h-screen w-screen overflow-hidden bg-background text-text">
      {/* Left Navigation Sidebar */}
      <Sidebar />

      {/* Main Content Area */}
      <div className="flex flex-col flex-1 min-w-0 overflow-hidden">
        {/* Global Top Bar */}
        <TopBar />

        {/* Scrollable Workspace Pages */}
        <main className="flex-1 overflow-y-auto p-6 md:p-8 bg-background">
          <ErrorBoundary>
            <Outlet />
          </ErrorBoundary>
        </main>
      </div>

      {/* Global Interactive Overlays */}
      <CommandPalette />
      <ToastContainer />
    </div>
  );
}
