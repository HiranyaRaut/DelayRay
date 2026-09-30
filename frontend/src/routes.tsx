import React from "react";
import { Routes, Route, Navigate } from "react-router-dom";
import { Layout } from "./components/layout/Layout";
import { Login } from "./pages/Login";
import { Dashboard } from "./pages/Dashboard";
import { ComponentShowcase } from "./pages/ComponentShowcase";
import { Projects } from "./pages/Projects";
import { ProjectDetail } from "./pages/ProjectDetail";
import { Alerts } from "./pages/Alerts";
import { ModelArena } from "./pages/ModelArena";
import { AblationLab } from "./pages/AblationLab";
import { Benchmarking } from "./pages/Benchmarking";
import { Assistant } from "./pages/Assistant";
import { Admin } from "./pages/Admin";
import { Methodology } from "./pages/Methodology";

export function AppRoutes() {
  return (
    <Routes>
      <Route path="/login" element={<Login />} />

      {/* Main Application Shell */}
      <Route path="/" element={<Layout />}>
        <Route index element={<Dashboard />} />
        <Route path="projects" element={<Projects />} />
        <Route path="projects/:id" element={<ProjectDetail />} />
        <Route path="alerts" element={<Alerts />} />
        <Route path="models" element={<ModelArena />} />
        <Route path="ablation" element={<AblationLab />} />
        <Route path="benchmark" element={<Benchmarking />} />
        <Route path="assistant" element={<Assistant />} />
        <Route path="admin" element={<Admin />} />
        <Route path="methodology" element={<Methodology />} />
        <Route path="dev/components" element={<ComponentShowcase />} />
      </Route>

      {/* Fallback to home */}
      <Route path="*" element={<Navigate to="/" replace />} />
    </Routes>
  );
}
