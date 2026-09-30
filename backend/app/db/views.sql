-- ==============================================================================
-- DelayRay Read-Only SQL Views for Guarded Analytics & Assistant Access
-- Adheres strictly to docs/BUILD_SPEC.md Section 5
-- ==============================================================================

-- Drop existing views if they exist to allow clean migration and re-creation
DROP VIEW IF EXISTS vw_project_latest;
DROP VIEW IF EXISTS vw_open_alerts;
DROP VIEW IF EXISTS vw_sector_summary;
DROP VIEW IF EXISTS vw_state_summary;
DROP VIEW IF EXISTS vw_model_leaderboard;

-- 1. Latest Project Snapshot & Risk View
CREATE VIEW vw_project_latest AS
WITH ranked_snapshots AS (
    SELECT 
        ps.*,
        ROW_NUMBER() OVER(PARTITION BY ps.project_id ORDER BY ps.month DESC) as rn
    FROM project_snapshots ps
),
ranked_predictions AS (
    SELECT 
        pr.*,
        ROW_NUMBER() OVER(PARTITION BY pr.project_id ORDER BY pr.snapshot_month DESC) as pr_rn
    FROM predictions pr
)
SELECT 
    p.project_id,
    p.project_name,
    p.ministry,
    p.sector,
    p.sub_sector,
    p.primary_state,
    p.implementing_agency,
    p.agency_type,
    p.sanction_date,
    p.start_date,
    p.original_cost_cr,
    p.original_completion_date,
    p.planned_duration_months,
    p.funding_mode,
    p.status,
    p.data_source,
    s.month AS latest_month,
    COALESCE(s.cumulative_expenditure_cr, 0.0) AS cumulative_expenditure_cr,
    COALESCE(s.physical_progress_pct, 0.0) AS physical_progress_pct,
    COALESCE(s.planned_progress_pct, 0.0) AS planned_progress_pct,
    ROUND(CASE 
        WHEN s.planned_progress_pct > 0 THEN s.physical_progress_pct / s.planned_progress_pct 
        ELSE 1.0 
    END, 3) AS spi,
    ROUND(CASE 
        WHEN s.cumulative_expenditure_cr > 0 AND p.original_cost_cr > 0 
        THEN s.physical_progress_pct / ((s.cumulative_expenditure_cr / p.original_cost_cr) * 100.0)
        ELSE 1.0 
    END, 3) AS cost_efficiency,
    s.reporting_lag_days,
    s.remarks AS latest_remarks,
    pred.risk_score,
    pred.risk_band,
    pred.risk_probability,
    pred.cost_overrun_p50,
    pred.delay_p50,
    pred.expected_overrun_cr,
    pred.value_at_risk_cr
FROM projects p
LEFT JOIN ranked_snapshots s ON p.project_id = s.project_id AND s.rn = 1
LEFT JOIN ranked_predictions pred ON p.project_id = pred.project_id AND pred.pr_rn = 1;

-- 2. Open Alerts View
CREATE VIEW vw_open_alerts AS
SELECT 
    a.id AS alert_id,
    a.project_id,
    p.project_name,
    p.sector,
    p.primary_state,
    a.rule_id,
    a.severity,
    a.title,
    a.status,
    a.created_at,
    a.assigned_to
FROM alerts a
JOIN projects p ON a.project_id = p.project_id
WHERE a.status IN ('new', 'acknowledged', 'assigned');

-- 3. Sector Aggregation Summary View
CREATE VIEW vw_sector_summary AS
SELECT 
    p.sector,
    p.ministry,
    COUNT(DISTINCT p.project_id) AS total_projects,
    SUM(p.original_cost_cr) AS total_sanctioned_cr,
    ROUND(AVG(COALESCE(s.physical_progress_pct, 0.0)), 2) AS avg_physical_progress_pct,
    ROUND(AVG(COALESCE(pred.risk_score, 0.0)), 1) AS avg_risk_score,
    SUM(CASE WHEN pred.risk_band IN ('High', 'Critical') THEN 1 ELSE 0 END) AS high_critical_count,
    ROUND(SUM(COALESCE(pred.value_at_risk_cr, 0.0)), 2) AS total_value_at_risk_cr
FROM projects p
LEFT JOIN (
    SELECT project_id, physical_progress_pct,
           ROW_NUMBER() OVER(PARTITION BY project_id ORDER BY month DESC) as rn
    FROM project_snapshots
) s ON p.project_id = s.project_id AND s.rn = 1
LEFT JOIN (
    SELECT project_id, risk_score, risk_band, value_at_risk_cr,
           ROW_NUMBER() OVER(PARTITION BY project_id ORDER BY snapshot_month DESC) as pr_rn
    FROM predictions
) pred ON p.project_id = pred.project_id AND pred.pr_rn = 1
GROUP BY p.sector, p.ministry;

-- 4. State Aggregation Summary View
CREATE VIEW vw_state_summary AS
SELECT 
    p.primary_state AS state_name,
    COUNT(DISTINCT p.project_id) AS project_count,
    SUM(p.original_cost_cr) AS total_sanctioned_cr,
    ROUND(AVG(COALESCE(pred.risk_score, 0.0)), 1) AS avg_risk_score,
    ROUND(SUM(COALESCE(pred.value_at_risk_cr, 0.0)), 2) AS total_value_at_risk_cr,
    SUM(CASE WHEN pred.risk_band IN ('High', 'Critical') THEN 1 ELSE 0 END) AS high_critical_count
FROM projects p
LEFT JOIN (
    SELECT project_id, risk_score, risk_band, value_at_risk_cr,
           ROW_NUMBER() OVER(PARTITION BY project_id ORDER BY snapshot_month DESC) as pr_rn
    FROM predictions
) pred ON p.project_id = pred.project_id AND pred.pr_rn = 1
GROUP BY p.primary_state;

-- 5. Model Leaderboard View
CREATE VIEW vw_model_leaderboard AS
SELECT 
    m.name AS model_name,
    m.task,
    m.version,
    m.is_champion,
    MAX(CASE WHEN mm.metric = 'mae' AND mm.split = 'test' THEN mm.value END) AS test_mae,
    MAX(CASE WHEN mm.metric = 'rmse' AND mm.split = 'test' THEN mm.value END) AS test_rmse,
    MAX(CASE WHEN mm.metric = 'r2' AND mm.split = 'test' THEN mm.value END) AS test_r2,
    MAX(CASE WHEN mm.metric = 'auc' AND mm.split = 'test' THEN mm.value END) AS test_auc,
    MAX(CASE WHEN mm.metric = 'brier' AND mm.split = 'test' THEN mm.value END) AS test_brier,
    m.created_at
FROM model_registry m
LEFT JOIN model_metrics mm ON m.id = mm.model_id
GROUP BY m.id, m.name, m.task, m.version, m.is_champion, m.created_at;
