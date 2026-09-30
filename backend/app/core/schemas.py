"""
DelayRay Core Pydantic Schemas
Strictly typed, validated schemas for all Phase 3 endpoints.
"""

from typing import List, Optional, Dict, Any, Union
from pydantic import BaseModel, Field
from datetime import datetime

# ==============================================================================
# Authentication & User Schemas
# ==============================================================================

class UserBase(BaseModel):
    email: str
    role: str = "viewer"  # viewer, analyst, admin

class UserLogin(BaseModel):
    email: str
    password: str

class UserCreate(BaseModel):
    email: str
    password: str
    role: str = "viewer"

class UserProfile(BaseModel):
    id: int
    email: str
    role: str
    is_active: bool
    created_at: Optional[datetime] = None

class TokenResponse(BaseModel):
    access_token: str
    refresh_token: Optional[str] = None
    token_type: str = "bearer"
    role: str
    email: str

class RefreshTokenRequest(BaseModel):
    refresh_token: str

# ==============================================================================
# Portfolio Schemas
# ==============================================================================

class PortfolioSummary(BaseModel):
    total_projects: int
    ongoing_projects: int
    completed_projects: int
    total_original_cost_cr: float
    total_expenditure_to_date_cr: float
    total_predicted_overrun_cr: float
    total_value_at_risk_cr: float
    avg_portfolio_risk_score: float
    critical_risk_count: int
    high_risk_count: int
    moderate_risk_count: int
    low_risk_count: int
    active_alerts_count: int
    as_of_date: str
    synthetic_data_badge: bool = True
    advisory_notice: str = "Risk scores and predictions support human decisions and do not replace them."

class BreakdownItem(BaseModel):
    dimension_value: str
    project_count: int
    total_cost_cr: float
    avg_risk_score: float
    critical_count: int
    high_count: int
    value_at_risk_cr: float

class PortfolioBreakdownResponse(BaseModel):
    dimension: str
    items: List[BreakdownItem]

class TrendMonthItem(BaseModel):
    month: str
    avg_risk_score: float
    avg_spi: float
    avg_expenditure_cr: float
    avg_physical_progress_pct: float
    alerts_raised: int

class PortfolioTrendResponse(BaseModel):
    trends: List[TrendMonthItem]

class RiskRadarItem(BaseModel):
    project_id: str
    project_name: str
    sector: str
    ministry: str
    state: str
    time_elapsed_pct: float
    physical_progress_pct: float
    risk_score: float
    risk_band: str
    original_cost_cr: float
    value_at_risk_cr: float
    spi: float
    active_alerts: int

class RiskRadarResponse(BaseModel):
    projects: List[RiskRadarItem]
    count: int

# ==============================================================================
# Project Schemas
# ==============================================================================

class ProjectListItem(BaseModel):
    project_id: str
    project_name: str
    ministry: str
    sector: str
    primary_state: str
    implementing_agency: str
    original_cost_cr: float
    latest_cost_revised_cr: Optional[float] = None
    sanction_date: str
    original_completion_date: str
    anticipated_completion_date: Optional[str] = None
    status: str
    time_elapsed_pct: float
    physical_progress_pct: float
    expenditure_pct: float
    risk_score: float
    risk_band: str
    predicted_cost_overrun_pct: float
    predicted_delay_months: float
    value_at_risk_cr: float
    spi: float
    cost_efficiency: float
    active_alerts_count: int

class PaginatedProjectsResponse(BaseModel):
    items: List[ProjectListItem]
    total: int
    page: int
    page_size: int
    total_pages: int

class ProjectDetail(BaseModel):
    project_id: str
    project_name: str
    ministry: str
    sector: str
    sub_sector: Optional[str] = None
    primary_state: str
    secondary_states: Optional[str] = None
    implementing_agency: str
    agency_type: str
    sanction_date: str
    start_date: str
    original_cost_cr: float
    original_completion_date: str
    planned_duration_months: int
    funding_mode: str
    status: str
    data_source: str
    
    # Latest snapshot metrics
    latest_snapshot_month: Optional[str] = None
    latest_expenditure_cr: float
    latest_physical_progress_pct: float
    latest_planned_progress_pct: float
    latest_anticipated_date: Optional[str] = None
    latest_cost_revised_cr: Optional[float] = None
    revision_count: int
    spi: float
    cost_efficiency: float
    time_elapsed_pct: float

    # Prediction & Risk
    risk_score: float
    risk_band: str
    risk_probability: float
    cost_overrun_p10: Optional[float] = None
    cost_overrun_p50: float
    cost_overrun_p90: Optional[float] = None
    delay_p10: Optional[float] = None
    delay_p50: float
    delay_p90: Optional[float] = None
    expected_overrun_cr: float
    value_at_risk_cr: float

    # Extras
    land_acquisition_pct: Optional[float] = None
    env_clearance_status: Optional[str] = None
    contractor_score: Optional[float] = None
    terrain_class: Optional[str] = None

class TimelinePoint(BaseModel):
    month: str
    cumulative_expenditure_cr: float
    physical_progress_pct: float
    planned_progress_pct: float
    spi: float
    cost_efficiency: float
    cost_revised_cr: Optional[float] = None
    remarks: Optional[str] = None

class SCurvePoint(BaseModel):
    month: str
    planned_progress_pct: float
    actual_progress_pct: Optional[float] = None
    forecast_progress_p10: Optional[float] = None
    forecast_progress_p50: Optional[float] = None
    forecast_progress_p90: Optional[float] = None

class SCurveResponse(BaseModel):
    project_id: str
    points: List[SCurvePoint]
    sanction_date: str
    original_completion_date: str
    anticipated_completion_date: Optional[str] = None

class DriverExplanation(BaseModel):
    feature: str
    display_name: str
    group: str
    shap_value: float
    direction: str  # increases_risk / decreases_risk
    rank: int
    sentence: str

class ProjectExplainResponse(BaseModel):
    project_id: str
    risk_score: float
    risk_band: str
    base_value: float
    drivers: List[DriverExplanation]
    recommended_playbook_actions: List[Dict[str, Any]]

class PeerBenchmarkResponse(BaseModel):
    project_id: str
    sector: str
    cost_band: str
    peer_count: int
    project_risk_score: float
    peer_median_risk_score: float
    risk_percentile: float
    project_spi: float
    peer_median_spi: float
    spi_percentile: float
    project_cost_overrun_pct: float
    peer_median_cost_overrun_pct: float
    project_delay_months: float
    peer_median_delay_months: float
    radar_dimensions: Dict[str, float]
    peer_radar_dimensions: Dict[str, float]

class RemarkItem(BaseModel):
    id: int
    month: str
    remark_text: str
    extracted_tags: Optional[List[str]] = None
    tag_confidence: float

# ==============================================================================
# What-If Simulator Schemas
# ==============================================================================

class WhatIfRequest(BaseModel):
    land_handover_pct: Optional[float] = Field(None, ge=0.0, le=100.0)
    statutory_clearance_delay_months: Optional[float] = Field(None, ge=0.0, le=60.0)
    contractor_rating: Optional[float] = Field(None, ge=0.0, le=100.0)
    expenditure_acceleration_pct: Optional[float] = Field(None, ge=-50.0, le=100.0)

class WhatIfResponse(BaseModel):
    project_id: str
    original_risk_score: float
    simulated_risk_score: float
    delta_risk_score: float
    original_risk_band: str
    simulated_risk_band: str
    original_value_at_risk_cr: float
    simulated_value_at_risk_cr: float
    delta_value_at_risk_cr: float
    original_predicted_delay_months: float
    simulated_predicted_delay_months: float
    caveat: str = "Model-based association, not a guaranteed causal effect. What-if projections assume other exogenous variables remain fixed."

# ==============================================================================
# Early Warning System (Alerts) Schemas
# ==============================================================================

class AlertResponse(BaseModel):
    id: str
    project_id: str
    project_name: Optional[str] = None
    sector: Optional[str] = None
    ministry: Optional[str] = None
    rule_id: str
    severity: str  # Watch, Warning, Critical
    title: str
    detail: Optional[Dict[str, Any]] = None
    status: str  # new, acknowledged, assigned, resolved, dismissed
    created_at: datetime
    acknowledged_by: Optional[str] = None
    assigned_to: Optional[str] = None
    resolved_at: Optional[datetime] = None
    resolution_note: Optional[str] = None
    cooldown_until: Optional[datetime] = None

class PaginatedAlertsResponse(BaseModel):
    items: List[AlertResponse]
    total: int
    page: int
    page_size: int
    total_pages: int
    counts_by_severity: Dict[str, int]
    counts_by_status: Dict[str, int]

class AlertUpdate(BaseModel):
    status: Optional[str] = None
    assigned_to: Optional[str] = None
    resolution_note: Optional[str] = None

class AlertRuleResponse(BaseModel):
    id: str
    name: str
    severity: str
    description: str
    params: Dict[str, Any]
    enabled: bool

class AlertRuleUpdate(BaseModel):
    params: Optional[Dict[str, Any]] = None
    enabled: Optional[bool] = None

# ==============================================================================
# Models & Reports Schemas
# ==============================================================================

class RetrainRequest(BaseModel):
    retrain_baselines: bool = False
    optuna_trials: int = 20

class JobResponse(BaseModel):
    id: str
    job_type: str
    status: str
    progress: float
    result: Optional[Dict[str, Any]] = None
    error_message: Optional[str] = None
    created_at: datetime
    updated_at: datetime

# ==============================================================================
# Data & Admin Schemas
# ==============================================================================

class UploadResponse(BaseModel):
    filename: str
    row_count: int
    columns: List[str]
    message: str

class ValidationResult(BaseModel):
    passed: bool
    summary: Dict[str, Any]
    errors: List[str]

class AuditLogItem(BaseModel):
    id: int
    user_email: str
    action: str
    entity_type: str
    entity_id: Optional[str] = None
    detail: Optional[Dict[str, Any]] = None
    created_at: datetime

class SettingItem(BaseModel):
    key: str
    value: Any
    updated_at: datetime

# ==============================================================================
# Demo Simulation Schemas
# ==============================================================================

class AdvanceMonthResponse(BaseModel):
    simulated_month: str
    new_snapshots_count: int
    rescore_count: int
    new_alerts_raised: int
    alerts: List[AlertResponse]
    summary_impact: Dict[str, Any]
    message: str
