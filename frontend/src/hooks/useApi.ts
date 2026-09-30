import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { api } from "../lib/api";
import { useAppStore } from "../stores/appStore";

export function usePortfolioSummary() {
  return useQuery({
    queryKey: ["portfolioSummary"],
    queryFn: () => api.getPortfolioSummary(),
    staleTime: 60000,
  });
}

export function usePortfolioBreakdown(dim = "sector") {
  return useQuery({
    queryKey: ["portfolioBreakdown", dim],
    queryFn: () => api.getPortfolioBreakdown(dim),
    staleTime: 60000,
  });
}

export function usePortfolioTrend() {
  return useQuery({
    queryKey: ["portfolioTrend"],
    queryFn: () => api.getPortfolioTrend(),
    staleTime: 60000,
  });
}

export function useRiskRadar(sector?: string) {
  return useQuery({
    queryKey: ["riskRadar", sector],
    queryFn: () => api.getRiskRadar(sector),
    staleTime: 60000,
  });
}

export function useProjects(params: Record<string, any> = {}) {
  return useQuery({
    queryKey: ["projects", params],
    queryFn: () => api.getProjects(params),
    staleTime: 30000,
  });
}

export function useProjectDetail(id?: string) {
  return useQuery({
    queryKey: ["projectDetail", id],
    queryFn: () => (id ? api.getProjectDetail(id) : Promise.reject("No ID")),
    enabled: !!id,
  });
}

export function useProjectSCurve(id?: string) {
  return useQuery({
    queryKey: ["projectSCurve", id],
    queryFn: () => (id ? api.getProjectSCurve(id) : Promise.reject("No ID")),
    enabled: !!id,
    staleTime: 60000,
  });
}

export function useProjectExplain(id?: string) {
  return useQuery({
    queryKey: ["projectExplain", id],
    queryFn: () => (id ? api.getProjectExplain(id) : Promise.reject("No ID")),
    enabled: !!id,
    staleTime: 60000,
  });
}

export function useProjectPeers(id?: string) {
  return useQuery({
    queryKey: ["projectPeers", id],
    queryFn: () => (id ? api.getProjectPeers(id) : Promise.reject("No ID")),
    enabled: !!id,
    staleTime: 60000,
  });
}

export function useProjectMilestones(id?: string) {
  return useQuery({
    queryKey: ["projectMilestones", id],
    queryFn: () => (id ? api.getProjectMilestones(id) : Promise.reject("No ID")),
    enabled: !!id,
    staleTime: 60000,
  });
}

export function useProjectAlerts(id?: string) {
  return useQuery({
    queryKey: ["projectAlerts", id],
    queryFn: () => (id ? api.getProjectAlerts(id) : Promise.reject("No ID")),
    enabled: !!id,
    staleTime: 30000,
  });
}

export function useProjectRemarks(id?: string) {
  return useQuery({
    queryKey: ["projectRemarks", id],
    queryFn: () => (id ? api.getProjectRemarks(id) : Promise.reject("No ID")),
    enabled: !!id,
    staleTime: 60000,
  });
}

export function useWhatIfMutation(id?: string) {
  return useMutation({
    mutationFn: (levers: Record<string, any>) => {
      if (!id) throw new Error("No project ID for what-if simulation");
      return api.simulateWhatIf(id, levers);
    },
  });
}

export function useAlerts(params: Record<string, any> = {}) {
  return useQuery({
    queryKey: ["alerts", params],
    queryFn: () => api.getAlerts(params),
    staleTime: 15000,
  });
}

export function useLeaderboard() {
  return useQuery({
    queryKey: ["modelLeaderboard"],
    queryFn: () => api.getLeaderboard(),
    staleTime: 300000,
  });
}

export function useVerdict() {
  return useQuery({
    queryKey: ["modelVerdict"],
    queryFn: () => api.getVerdict(),
    staleTime: 300000,
  });
}

export function useAblation() {
  return useQuery({
    queryKey: ["modelAblation"],
    queryFn: () => api.getAblation(),
    staleTime: 300000,
  });
}

export function useAdvanceMonthMutation() {
  const queryClient = useQueryClient();
  const addToast = useAppStore((s) => s.addToast);

  return useMutation({
    mutationFn: () => api.advanceMonth(),
    onSuccess: (data) => {
      addToast({
        type: "success",
        title: "Monitoring Month Advanced",
        message: data.message || `Portfolio advanced to ${data.simulated_month}.`,
      });
      // Invalidate queries to refresh UI
      queryClient.invalidateQueries({ queryKey: ["portfolioSummary"] });
      queryClient.invalidateQueries({ queryKey: ["portfolioBreakdown"] });
      queryClient.invalidateQueries({ queryKey: ["portfolioTrend"] });
      queryClient.invalidateQueries({ queryKey: ["projects"] });
      queryClient.invalidateQueries({ queryKey: ["alerts"] });
    },
    onError: (err: any) => {
      addToast({
        type: "error",
        title: "Simulation Failed",
        message: err.message || "Failed to advance monitoring month.",
      });
    },
  });
}
