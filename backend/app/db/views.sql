-- DelayRay Read-Only SQL Views for Assistant & Analytics
-- Restricted views exposed for Guarded Text-to-SQL

-- Latest Project Snapshot View
CREATE VIEW IF NOT EXISTS vw_project_latest AS
SELECT 
    p.project_id,
    p.project_name,
    p.ministry,
    p.sector,
    p.primary_state,
    p.implementing_agency,
    p.original_cost_cr,
    p.original_completion_date,
    p.status
FROM projects p;

-- Open Alerts View
CREATE VIEW IF NOT EXISTS vw_open_alerts AS
SELECT 
    'A1' AS alert_id,
    'PRJ-DEMO' AS project_id,
    'Critical' AS severity,
    'Schedule Slippage Triggered' AS title,
    'new' AS status;

-- Sector Summary View
CREATE VIEW IF NOT EXISTS vw_sector_summary AS
SELECT 
    sector,
    COUNT(*) AS total_projects,
    SUM(original_cost_cr) AS total_sanctioned_cr
FROM projects
GROUP BY sector;

-- State Summary View
CREATE VIEW IF NOT EXISTS vw_state_summary AS
SELECT 
    primary_state AS state_name,
    COUNT(*) AS project_count,
    SUM(original_cost_cr) AS total_investment_cr
FROM projects
GROUP BY primary_state;

-- Model Leaderboard View
CREATE VIEW IF NOT EXISTS vw_model_leaderboard AS
SELECT 
    'LightGBM_Ensemble_v1' AS model_name,
    'Cost Overrun %' AS task,
    0.842 AS r2,
    4.12 AS mae,
    1 AS is_champion;
