import React from "react";
import { Routes, Route, Navigate } from "react-router-dom";
import { Layout } from "./components/layout/Layout";
import { Login } from "./pages/Login";
import { Dashboard } from "./pages/Dashboard";
import { ComponentShowcase } from "./pages/ComponentShowcase";
import { PlaceholderPage } from "./pages/PlaceholderPage";
import { useAuthStore } from "./stores/authStore";

export function AppRoutes() {
  const isAuthenticated = useAuthStore((s) => s.isAuthenticated);

  return (
    <Routes>
      <Route path="/login" element={<Login />} />

      {/* Main Protected / Demo Application Shell */}
      <Route path="/" element={<Layout />}>
        <Route index element={<Dashboard />} />
        <Route
          path="projects"
          element={
            <PlaceholderPage
              title="Projects Catalogue & Analytics"
              phase="Phase 5"
              description="Virtualized table over 1,981 central sector projects with faceted search, S-curves, and drawer quick-peek."
            />
          }
        />
        <Route
          path="alerts"
          element={
            <PlaceholderPage
              title="Early Warning Center"
              phase="Phase 6"
              description="Active alerts feed, lifecycle board (new / acknowledged / assigned / resolved), and trigger rules administration."
            />
          }
        />
        <Route
          path="models"
          element={
            <PlaceholderPage
              title="Model Arena & Research Leaderboard"
              phase="Phase 6"
              description="Empirical benchmark comparing statistical baselines vs ML models, paired bootstrap significance verdict, and calibration curves."
            />
          }
        />
        <Route
          path="ablation"
          element={
            <PlaceholderPage
              title="Econometric Ablation Lab"
              phase="Phase 6"
              description="CUF attribution percentage (66.0%), feature group progression (G1-G6), and ranked candidate fields."
            />
          }
        />
        <Route
          path="benchmark"
          element={
            <PlaceholderPage
              title="Peer Benchmarking Cohorts"
              phase="Phase 6"
              description="Multi-dimensional radar comparisons and percentile distributions against similar sector assets."
            />
          }
        />
        <Route
          path="assistant"
          element={
            <PlaceholderPage
              title="Local LLM Infrastructure Assistant"
              phase="Phase 7"
              description="Conversational intent router, guarded text-to-SQL, and local RAG citations over monthly contractor remarks."
            />
          }
        />
        <Route
          path="admin"
          element={
            <PlaceholderPage
              title="Data & Governance Administration"
              phase="Phase 5/6"
              description="Pandera schema validation reports, audit logging, system settings, and batch scoring job controls."
            />
          }
        />
        <Route path="dev/components" element={<ComponentShowcase />} />
      </Route>

      {/* Fallback to home */}
      <Route path="*" element={<Navigate to="/" replace />} />
    </Routes>
  );
}
