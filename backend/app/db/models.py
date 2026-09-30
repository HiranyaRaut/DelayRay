"""
DelayRay Comprehensive SQLAlchemy Database Models
Adheres strictly to docs/BUILD_SPEC.md Section 5.
"""

from sqlalchemy import (
    Column, Integer, String, Float, Boolean, DateTime, Text, JSON, ForeignKey, Index, UniqueConstraint
)
from sqlalchemy.orm import relationship
from datetime import datetime, timezone
from backend.app.db.session import Base

# ==============================================================================
# Master Data Tables
# ==============================================================================

class Ministry(Base):
    __tablename__ = "ministries"

    id = Column(Integer, primary_key=True, index=True)
    code = Column(String(50), unique=True, index=True, nullable=False)
    name = Column(String(150), unique=True, nullable=False)

    sectors = relationship("Sector", back_populates="ministry")
    projects = relationship("Project", back_populates="ministry_rel")

class Sector(Base):
    __tablename__ = "sectors"

    id = Column(Integer, primary_key=True, index=True)
    code = Column(String(50), unique=True, index=True, nullable=False)
    name = Column(String(100), unique=True, nullable=False)
    ministry_id = Column(Integer, ForeignKey("ministries.id", ondelete="CASCADE"), nullable=False)

    ministry = relationship("Ministry", back_populates="sectors")
    projects = relationship("Project", back_populates="sector_rel")

class State(Base):
    __tablename__ = "states"

    id = Column(Integer, primary_key=True, index=True)
    code = Column(String(10), unique=True, index=True, nullable=False)
    name = Column(String(100), unique=True, nullable=False)
    region = Column(String(50), nullable=False)  # North, South, East, West, North-East, Central

class Agency(Base):
    __tablename__ = "agencies"

    id = Column(Integer, primary_key=True, index=True)
    code = Column(String(50), unique=True, index=True, nullable=False)
    name = Column(String(150), unique=True, nullable=False)
    agency_type = Column(String(50), nullable=False)  # central_psu, state_agency, private_epc, spv

# ==============================================================================
# Core Project & Operational Tables
# ==============================================================================

class Project(Base):
    __tablename__ = "projects"

    id = Column(Integer, primary_key=True, index=True)
    project_id = Column(String(100), unique=True, index=True, nullable=False)
    project_name = Column(String(255), nullable=False)
    ministry = Column(String(150), index=True, nullable=False)
    ministry_id = Column(Integer, ForeignKey("ministries.id"), nullable=True)
    sector = Column(String(100), index=True, nullable=False)
    sector_id = Column(Integer, ForeignKey("sectors.id"), nullable=True)
    sub_sector = Column(String(100), nullable=True)
    primary_state = Column(String(100), index=True, nullable=False)
    secondary_states = Column(JSON, nullable=True)
    implementing_agency = Column(String(150), index=True, nullable=False)
    agency_type = Column(String(50), nullable=False)
    sanction_date = Column(String(20), nullable=False)
    start_date = Column(String(20), nullable=False)
    original_cost_cr = Column(Float, nullable=False)
    original_completion_date = Column(String(20), nullable=False)
    planned_duration_months = Column(Float, nullable=False)
    funding_mode = Column(String(50), nullable=False)
    status = Column(String(50), default="ongoing", index=True, nullable=False)  # ongoing / completed
    data_source = Column(String(50), default="synthetic", nullable=False)      # synthetic / real
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))

    ministry_rel = relationship("Ministry", back_populates="projects")
    sector_rel = relationship("Sector", back_populates="projects")
    snapshots = relationship("ProjectSnapshot", back_populates="project", cascade="all, delete-orphan")
    outcome = relationship("ProjectOutcome", back_populates="project", uselist=False, cascade="all, delete-orphan")
    extras = relationship("ProjectExtra", back_populates="project", uselist=False, cascade="all, delete-orphan")
    remarks = relationship("ProjectRemark", back_populates="project", cascade="all, delete-orphan")
    milestones = relationship("Milestone", back_populates="project", cascade="all, delete-orphan")
    predictions = relationship("Prediction", back_populates="project", cascade="all, delete-orphan")
    alerts = relationship("Alert", back_populates="project", cascade="all, delete-orphan")

    __table_args__ = (
        Index("idx_projects_sector_status", "sector", "status"),
        Index("idx_projects_ministry_status", "ministry", "status"),
        Index("idx_projects_state", "primary_state"),
    )

class ProjectSnapshot(Base):
    __tablename__ = "project_snapshots"

    id = Column(Integer, primary_key=True, index=True)
    project_id = Column(String(100), ForeignKey("projects.project_id", ondelete="CASCADE"), index=True, nullable=False)
    month = Column(String(7), index=True, nullable=False)  # YYYY-MM
    cumulative_expenditure_cr = Column(Float, nullable=False)
    physical_progress_pct = Column(Float, nullable=False)
    planned_progress_pct = Column(Float, nullable=False)
    milestones_planned_to_date = Column(Integer, default=0, nullable=False)
    milestones_achieved_to_date = Column(Integer, default=0, nullable=False)
    anticipated_completion_date = Column(String(20), nullable=True)
    cost_revised_to_date_cr = Column(Float, nullable=True)
    revision_count_to_date = Column(Integer, default=0, nullable=False)
    reporting_lag_days = Column(Integer, default=0, nullable=False)
    remarks = Column(Text, nullable=True)

    project = relationship("Project", back_populates="snapshots")

    __table_args__ = (
        UniqueConstraint("project_id", "month", name="uq_project_snapshot_month"),
        Index("idx_snapshot_project_month", "project_id", "month"),
    )

class ProjectOutcome(Base):
    __tablename__ = "project_outcomes"

    id = Column(Integer, primary_key=True, index=True)
    project_id = Column(String(100), ForeignKey("projects.project_id", ondelete="CASCADE"), unique=True, index=True, nullable=False)
    final_cost_cr = Column(Float, nullable=False)
    actual_completion_date = Column(String(20), nullable=False)
    cost_overrun_pct = Column(Float, nullable=False)
    time_overrun_months = Column(Float, nullable=False)
    high_risk_flag = Column(Boolean, default=False, index=True, nullable=False)

    project = relationship("Project", back_populates="outcome")

class ProjectExtra(Base):
    __tablename__ = "project_extras"

    id = Column(Integer, primary_key=True, index=True)
    project_id = Column(String(100), ForeignKey("projects.project_id", ondelete="CASCADE"), unique=True, index=True, nullable=False)
    land_acquisition_pct_at_start = Column(Float, nullable=False)
    env_forest_clearance_status = Column(String(50), nullable=False)  # cleared, pending, delayed
    env_forest_clearance_delay_months = Column(Float, default=0.0, nullable=False)
    utility_shifting_complexity = Column(String(50), nullable=False)  # low, medium, high, critical
    utility_shifting_count = Column(Integer, default=0, nullable=False)
    terrain_class = Column(String(50), nullable=False)               # plain, hilly, coastal, urban_dense
    contractor_id = Column(String(100), index=True, nullable=False)
    contractor_performance_score = Column(Float, nullable=False)     # 0 - 100
    contractor_concurrent_projects = Column(Integer, default=1, nullable=False)
    geotechnical_uncertainty_score = Column(Float, nullable=False)   # 0 - 100
    design_changes_count = Column(Integer, default=0, nullable=False)
    local_law_order_index = Column(Float, nullable=False)            # 0 - 100 (higher = more stable)

    project = relationship("Project", back_populates="extras")

class ExternalIndicator(Base):
    __tablename__ = "external_indicators"

    id = Column(Integer, primary_key=True, index=True)
    month = Column(String(7), index=True, nullable=False)  # YYYY-MM
    state = Column(String(100), index=True, nullable=False)
    rainfall_anomaly_pct = Column(Float, default=0.0, nullable=False)
    steel_price_index = Column(Float, nullable=False)
    cement_price_index = Column(Float, nullable=False)
    crude_oil_price_index = Column(Float, nullable=False)

    __table_args__ = (
        UniqueConstraint("month", "state", name="uq_external_month_state"),
        Index("idx_external_month_state", "month", "state"),
    )

class ProjectRemark(Base):
    __tablename__ = "project_remarks"

    id = Column(Integer, primary_key=True, index=True)
    project_id = Column(String(100), ForeignKey("projects.project_id", ondelete="CASCADE"), index=True, nullable=False)
    month = Column(String(7), index=True, nullable=False)
    remark_text = Column(Text, nullable=False)
    extracted_tags = Column(JSON, nullable=True)        # e.g. ["land", "clearance"]
    tag_confidence = Column(Float, default=0.0, nullable=False)

    project = relationship("Project", back_populates="remarks")

class Milestone(Base):
    __tablename__ = "milestones"

    id = Column(Integer, primary_key=True, index=True)
    project_id = Column(String(100), ForeignKey("projects.project_id", ondelete="CASCADE"), index=True, nullable=False)
    milestone_name = Column(String(255), nullable=False)
    planned_date = Column(String(20), nullable=False)
    achieved_date = Column(String(20), nullable=True)
    status = Column(String(50), default="pending", nullable=False)  # pending, achieved, missed

    project = relationship("Project", back_populates="milestones")

# ==============================================================================
# Model Registry, Metrics, and Ablation
# ==============================================================================

class ModelRegistry(Base):
    __tablename__ = "model_registry"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), index=True, nullable=False)
    task = Column(String(50), index=True, nullable=False)  # cost_overrun, time_overrun, high_risk
    version = Column(String(50), nullable=False)
    params = Column(JSON, nullable=True)
    feature_list = Column(JSON, nullable=True)
    data_hash = Column(String(100), nullable=False)
    git_commit = Column(String(50), nullable=False)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    is_champion = Column(Boolean, default=False, index=True, nullable=False)

class ModelMetric(Base):
    __tablename__ = "model_metrics"

    id = Column(Integer, primary_key=True, index=True)
    model_id = Column(Integer, ForeignKey("model_registry.id", ondelete="CASCADE"), index=True, nullable=False)
    split = Column(String(50), nullable=False)  # train, val, test
    metric = Column(String(50), nullable=False)  # mae, rmse, r2, auc, brier, ece
    value = Column(Float, nullable=False)
    ci_low = Column(Float, nullable=True)
    ci_high = Column(Float, nullable=True)

class AblationResult(Base):
    __tablename__ = "ablation_results"

    id = Column(Integer, primary_key=True, index=True)
    experiment = Column(String(100), index=True, nullable=False)
    feature_group = Column(String(100), index=True, nullable=False)
    task = Column(String(50), nullable=False)
    metric = Column(String(50), nullable=False)
    value = Column(Float, nullable=False)
    ci_low = Column(Float, nullable=True)
    ci_high = Column(Float, nullable=True)

# ==============================================================================
# Predictions, Explanations, and Early Warning System
# ==============================================================================

class Prediction(Base):
    __tablename__ = "predictions"

    id = Column(Integer, primary_key=True, index=True)
    project_id = Column(String(100), ForeignKey("projects.project_id", ondelete="CASCADE"), index=True, nullable=False)
    snapshot_month = Column(String(7), index=True, nullable=False)
    model_id = Column(Integer, ForeignKey("model_registry.id"), nullable=True)
    cost_overrun_p10 = Column(Float, nullable=True)
    cost_overrun_p50 = Column(Float, nullable=False)
    cost_overrun_p90 = Column(Float, nullable=True)
    delay_p10 = Column(Float, nullable=True)
    delay_p50 = Column(Float, nullable=False)
    delay_p90 = Column(Float, nullable=True)
    risk_probability = Column(Float, nullable=False)  # Calibrated probability (0 - 1)
    risk_score = Column(Float, index=True, nullable=False)  # 0 - 100
    risk_band = Column(String(20), index=True, nullable=False)  # Low, Moderate, High, Critical
    expected_overrun_cr = Column(Float, nullable=False)
    value_at_risk_cr = Column(Float, index=True, nullable=False)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))

    project = relationship("Project", back_populates="predictions")
    explanations = relationship("Explanation", back_populates="prediction", cascade="all, delete-orphan")

    __table_args__ = (
        Index("idx_predictions_proj_month", "project_id", "snapshot_month"),
        Index("idx_predictions_band_var", "risk_band", "value_at_risk_cr"),
    )

class Explanation(Base):
    __tablename__ = "explanations"

    id = Column(Integer, primary_key=True, index=True)
    prediction_id = Column(Integer, ForeignKey("predictions.id", ondelete="CASCADE"), index=True, nullable=False)
    feature = Column(String(100), nullable=False)
    feature_group = Column(String(50), nullable=False)
    shap_value = Column(Float, nullable=False)
    direction = Column(String(20), nullable=False)  # increases_risk / decreases_risk
    rank = Column(Integer, nullable=False)

    prediction = relationship("Prediction", back_populates="explanations")

class Alert(Base):
    __tablename__ = "alerts"

    id = Column(String(100), primary_key=True, index=True)  # e.g. ALT-2026-0001
    project_id = Column(String(100), ForeignKey("projects.project_id", ondelete="CASCADE"), index=True, nullable=False)
    rule_id = Column(String(50), index=True, nullable=False)  # R1 to R8
    severity = Column(String(20), index=True, nullable=False)  # Watch, Warning, Critical
    title = Column(String(255), nullable=False)
    detail = Column(JSON, nullable=True)
    status = Column(String(50), default="new", index=True, nullable=False)  # new, acknowledged, assigned, resolved, dismissed
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), index=True)
    acknowledged_by = Column(String(100), nullable=True)
    assigned_to = Column(String(100), nullable=True)
    resolved_at = Column(DateTime, nullable=True)
    resolution_note = Column(Text, nullable=True)
    cooldown_until = Column(DateTime, nullable=True)

    project = relationship("Project", back_populates="alerts")

    __table_args__ = (
        Index("idx_alerts_proj_status", "project_id", "status"),
        Index("idx_alerts_severity_status", "severity", "status"),
    )

class AlertRule(Base):
    __tablename__ = "alert_rules"

    id = Column(String(50), primary_key=True)  # R1 to R8
    name = Column(String(150), nullable=False)
    severity = Column(String(20), nullable=False)
    description = Column(Text, nullable=False)
    params = Column(JSON, nullable=False)
    enabled = Column(Boolean, default=True, nullable=False)

class InterventionsPlaybook(Base):
    __tablename__ = "interventions_playbook"

    id = Column(Integer, primary_key=True, index=True)
    driver_tag = Column(String(100), index=True, nullable=False)
    action = Column(Text, nullable=False)
    owner_level = Column(String(50), nullable=False)  # project, ministry, state
    expected_effect = Column(Text, nullable=False)
    evidence_note = Column(Text, nullable=False)

# ==============================================================================
# Administrative, Caching, and Audit Logging
# ==============================================================================

class BenchmarkCache(Base):
    __tablename__ = "benchmark_cache"

    id = Column(Integer, primary_key=True, index=True)
    sector = Column(String(100), index=True, nullable=False)
    cost_band = Column(String(50), index=True, nullable=False)
    metrics = Column(JSON, nullable=False)
    updated_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))

class DriftReport(Base):
    __tablename__ = "drift_reports"

    id = Column(Integer, primary_key=True, index=True)
    batch_month = Column(String(7), index=True, nullable=False)
    feature_name = Column(String(100), nullable=False)
    psi_value = Column(Float, nullable=False)
    status = Column(String(50), nullable=False)  # stable, warning, action_required
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))

class Job(Base):
    __tablename__ = "jobs"

    id = Column(String(100), primary_key=True, index=True)
    job_type = Column(String(50), nullable=False)  # retrain, rescore, vector_index, monthly_sim
    status = Column(String(50), default="pending", nullable=False)  # pending, running, completed, failed
    progress = Column(Float, default=0.0, nullable=False)
    result = Column(JSON, nullable=True)
    error_message = Column(Text, nullable=True)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String(255), unique=True, index=True, nullable=False)
    hashed_password = Column(String(255), nullable=False)
    role = Column(String(50), default="viewer", nullable=False)  # viewer, analyst, admin
    is_active = Column(Boolean, default=True, nullable=False)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))

class AuditLog(Base):
    __tablename__ = "audit_log"

    id = Column(Integer, primary_key=True, index=True)
    user_email = Column(String(255), index=True, nullable=False)
    action = Column(String(100), nullable=False)
    entity_type = Column(String(100), nullable=False)
    entity_id = Column(String(100), nullable=True)
    detail = Column(JSON, nullable=True)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))

class Setting(Base):
    __tablename__ = "settings"

    key = Column(String(100), primary_key=True)
    value = Column(JSON, nullable=False)
    updated_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
