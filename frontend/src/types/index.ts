/**
 * DelayRay Frontend Type Definitions
 * Directly mirrors backend Pydantic models.
 */

export type RiskBand = "Low" | "Moderate" | "High" | "Critical";
export type AlertSeverity = "Watch" | "Warning" | "Critical";
export type AlertStatus = "new" | "acknowledged" | "assigned" | "resolved" | "dismissed";
export type UserRole = "viewer" | "analyst" | "admin";

export interface User {
  id: number;
  email: string;
  role: UserRole;
  is_active: boolean;
  created_at?: string;
}

export interface AuthTokens {
  access_token: string;
  refresh_token?: string;
  token_type: string;
  role: UserRole;
  email: string;
}

export interface PortfolioSummary {
  total_projects: number;
  ongoing_projects: number;
  completed_projects: number;
  total_original_cost_cr: number;
  total_expenditure_to_date_cr: number;
  total_predicted_overrun_cr: number;
  total_value_at_risk_cr: number;
  avg_portfolio_risk_score: number;
  critical_risk_count: number;
  high_risk_count: number;
  moderate_risk_count: number;
  low_risk_count: number;
  active_alerts_count: number;
  as_of_date: string;
  synthetic_data_badge: boolean;
  advisory_notice: string;
}

export interface BreakdownItem {
  dimension_value: string;
  project_count: number;
  total_cost_cr: number;
  avg_risk_score: number;
  critical_count: number;
  high_count: number;
  value_at_risk_cr: number;
}

export interface TrendMonthItem {
  month: string;
  avg_risk_score: number;
  avg_spi: number;
  avg_expenditure_cr: number;
  avg_physical_progress_pct: number;
  alerts_raised: number;
}

export interface RiskRadarItem {
  project_id: string;
  project_name: string;
  sector: string;
  ministry: string;
  state: string;
  time_elapsed_pct: number;
  physical_progress_pct: number;
  risk_score: number;
  risk_band: RiskBand;
  original_cost_cr: number;
  value_at_risk_cr: number;
  spi: number;
  active_alerts: number;
}

export interface ProjectListItem {
  project_id: string;
  project_name: string;
  ministry: string;
  sector: string;
  primary_state: string;
  implementing_agency: string;
  original_cost_cr: number;
  latest_cost_revised_cr?: number | null;
  sanction_date: string;
  original_completion_date: string;
  anticipated_completion_date?: string | null;
  status: string;
  time_elapsed_pct: number;
  physical_progress_pct: number;
  expenditure_pct: number;
  risk_score: number;
  risk_band: RiskBand;
  predicted_cost_overrun_pct: number;
  predicted_delay_months: number;
  value_at_risk_cr: number;
  spi: number;
  cost_efficiency: number;
  active_alerts_count: number;
}

export interface ProjectDetail {
  project_id: string;
  project_name: string;
  ministry: string;
  sector: string;
  sub_sector?: string | null;
  primary_state: string;
  secondary_states?: string | null;
  implementing_agency: string;
  agency_type: string;
  sanction_date: string;
  start_date: string;
  original_cost_cr: number;
  original_completion_date: string;
  planned_duration_months: number;
  funding_mode: string;
  status: string;
  data_source: string;

  latest_snapshot_month?: string | null;
  latest_expenditure_cr: number;
  latest_physical_progress_pct: number;
  latest_planned_progress_pct: number;
  latest_anticipated_date?: string | null;
  latest_cost_revised_cr?: number | null;
  revision_count: number;
  spi: number;
  cost_efficiency: number;
  time_elapsed_pct: number;

  risk_score: number;
  risk_band: RiskBand;
  risk_probability: number;
  cost_overrun_p10?: number | null;
  cost_overrun_p50: number;
  cost_overrun_p90?: number | null;
  delay_p10?: number | null;
  delay_p50: number;
  delay_p90?: number | null;
  expected_overrun_cr: number;
  value_at_risk_cr: number;

  land_acquisition_pct?: number | null;
  env_clearance_status?: string | null;
  contractor_score?: number | null;
  terrain_class?: string | null;
}

export interface AlertItem {
  id: string;
  project_id: string;
  project_name?: string | null;
  sector?: string | null;
  ministry?: string | null;
  rule_id: string;
  severity: AlertSeverity;
  title: string;
  detail?: any;
  status: AlertStatus;
  created_at: string;
  acknowledged_by?: string | null;
  assigned_to?: string | null;
  resolved_at?: string | null;
  resolution_note?: string | null;
  cooldown_until?: string | null;
}

export interface PaginatedResponse<T> {
  items: T[];
  total: number;
  page: number;
  page_size: number;
  total_pages: number;
}
