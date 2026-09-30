"""
DelayRay Pandera Data Validation & Quality Reporting Engine
Enforces schema contracts and produces data quality diagnostics.
Adheres to docs/BUILD_SPEC.md Section 4.7 & 5.
"""

from typing import Dict, Any, Tuple, List
import os
import pandas as pd
import warnings

# Suppress Pandera import warning
os.environ["DISABLE_PANDERA_IMPORT_WARNING"] = "True"
try:
    import pandera.pandas as pa
    from pandera.pandas import Column, Check, DataFrameSchema
except ImportError:
    import pandera as pa
    from pandera import Column, Check, DataFrameSchema

# ------------------------------------------------------------------------------
# Pandera Schemas
# ------------------------------------------------------------------------------

projects_schema = DataFrameSchema({
    "project_id": Column(str, nullable=False, unique=True),
    "project_name": Column(str, nullable=False),
    "ministry": Column(str, nullable=False),
    "sector": Column(str, nullable=False),
    "sub_sector": Column(str, nullable=True),
    "primary_state": Column(str, nullable=False),
    "implementing_agency": Column(str, nullable=False),
    "agency_type": Column(str, nullable=False),
    "sanction_date": Column(str, Check.str_matches(r"^\d{4}-\d{2}-\d{2}$")),
    "start_date": Column(str, Check.str_matches(r"^\d{4}-\d{2}-\d{2}$")),
    "original_cost_cr": Column(float, Check.greater_than_or_equal_to(150.0)),
    "original_completion_date": Column(str, Check.str_matches(r"^\d{4}-\d{2}-\d{2}$")),
    "planned_duration_months": Column(float, Check.greater_than(0.0)),
    "funding_mode": Column(str, nullable=False),
    "status": Column(str, Check.isin(["ongoing", "completed"])),
    "data_source": Column(str, Check.isin(["synthetic", "real"]))
}, coerce=True)

snapshots_schema = DataFrameSchema({
    "project_id": Column(str, nullable=False),
    "month": Column(str, Check.str_matches(r"^\d{4}-\d{2}$")),
    "cumulative_expenditure_cr": Column(float, Check.greater_than_or_equal_to(0.0)),
    "physical_progress_pct": Column(float, [Check.greater_than_or_equal_to(0.0), Check.less_than_or_equal_to(100.0)]),
    "planned_progress_pct": Column(float, [Check.greater_than_or_equal_to(0.0), Check.less_than_or_equal_to(100.0)]),
    "milestones_planned_to_date": Column(int, Check.greater_than_or_equal_to(0)),
    "milestones_achieved_to_date": Column(int, Check.greater_than_or_equal_to(0)),
    "anticipated_completion_date": Column(str, nullable=True),
    "cost_revised_to_date_cr": Column(float, nullable=True),
    "revision_count_to_date": Column(int, Check.greater_than_or_equal_to(0)),
    "reporting_lag_days": Column(int, Check.greater_than_or_equal_to(0)),
    "remarks": Column(str, nullable=True)
}, coerce=True)

outcomes_schema = DataFrameSchema({
    "project_id": Column(str, nullable=False, unique=True),
    "final_cost_cr": Column(float, Check.greater_than_or_equal_to(150.0)),
    "actual_completion_date": Column(str, Check.str_matches(r"^\d{4}-\d{2}-\d{2}$")),
    "cost_overrun_pct": Column(float, Check.greater_than_or_equal_to(0.0)),
    "time_overrun_months": Column(float, Check.greater_than_or_equal_to(0.0)),
    "high_risk_flag": Column(bool, nullable=False)
}, coerce=True)

extras_schema = DataFrameSchema({
    "project_id": Column(str, nullable=False, unique=True),
    "land_acquisition_pct_at_start": Column(float, [Check.greater_than_or_equal_to(0.0), Check.less_than_or_equal_to(100.0)]),
    "env_forest_clearance_status": Column(str, Check.isin(["cleared", "pending", "delayed"])),
    "env_forest_clearance_delay_months": Column(float, Check.greater_than_or_equal_to(0.0)),
    "utility_shifting_complexity": Column(str, Check.isin(["low", "medium", "high", "critical"])),
    "utility_shifting_count": Column(int, Check.greater_than_or_equal_to(0)),
    "terrain_class": Column(str, Check.isin(["plain", "hilly", "coastal", "urban_dense"])),
    "contractor_id": Column(str, nullable=False),
    "contractor_performance_score": Column(float, [Check.greater_than_or_equal_to(0.0), Check.less_than_or_equal_to(100.0)]),
    "contractor_concurrent_projects": Column(int, Check.greater_than_or_equal_to(1)),
    "geotechnical_uncertainty_score": Column(float, [Check.greater_than_or_equal_to(0.0), Check.less_than_or_equal_to(100.0)]),
    "design_changes_count": Column(int, Check.greater_than_or_equal_to(0)),
    "local_law_order_index": Column(float, [Check.greater_than_or_equal_to(0.0), Check.less_than_or_equal_to(100.0)])
}, coerce=True)

# ------------------------------------------------------------------------------
# Validation & Quality Report Generator
# ------------------------------------------------------------------------------

def validate_dataframe(df: pd.DataFrame, schema: DataFrameSchema) -> Tuple[bool, List[str]]:
    """
    Validates a DataFrame against a Pandera schema and returns (is_valid, error_list).
    """
    try:
        schema.validate(df, lazy=True)
        return True, []
    except pa.errors.SchemaErrors as err:
        errors = [f"{e.get('column', 'Schema')}: {e.get('check', 'Error')}" for e in err.failure_cases.to_dict('records')[:10]]
        return False, errors

def generate_data_quality_report(
    df_projects: pd.DataFrame,
    df_snapshots: pd.DataFrame,
    df_outcomes: pd.DataFrame,
    df_extras: pd.DataFrame
) -> Dict[str, Any]:
    """
    Produces a detailed data quality audit report including missingness, ranges, and anomalies.
    """
    p_valid, p_errs = validate_dataframe(df_projects, projects_schema)
    s_valid, s_errs = validate_dataframe(df_snapshots, snapshots_schema)
    o_valid, o_errs = validate_dataframe(df_outcomes, outcomes_schema)
    e_valid, e_errs = validate_dataframe(df_extras, extras_schema)

    def col_missingness(df: pd.DataFrame) -> Dict[str, Dict[str, Any]]:
        res = {}
        for col in df.columns:
            n_null = int(df[col].isna().sum())
            res[col] = {
                "null_count": n_null,
                "null_pct": round(float(n_null / len(df) * 100), 2)
            }
        return res

    report = {
        "overall_status": "passed" if (p_valid and s_valid and o_valid and e_valid) else "validation_warnings",
        "tables": {
            "projects": {
                "row_count": len(df_projects),
                "is_schema_valid": p_valid,
                "errors": p_errs,
                "missingness": col_missingness(df_projects)
            },
            "project_snapshots": {
                "row_count": len(df_snapshots),
                "is_schema_valid": s_valid,
                "errors": s_errs,
                "missingness": col_missingness(df_snapshots),
                "reporting_lag_p95_days": float(df_snapshots["reporting_lag_days"].quantile(0.95))
            },
            "project_outcomes": {
                "row_count": len(df_outcomes),
                "is_schema_valid": o_valid,
                "errors": o_errs,
                "high_risk_ratio": round(float(df_outcomes["high_risk_flag"].mean()), 3)
            },
            "project_extras": {
                "row_count": len(df_extras),
                "is_schema_valid": e_valid,
                "errors": e_errs
            }
        },
        "anomalies_detected": {
            "negative_progress_count": int((df_snapshots["physical_progress_pct"] < 0).sum()),
            "extreme_reporting_lag_gt60d": int((df_snapshots["reporting_lag_days"] > 60).sum()),
            "extreme_cost_overrun_gt100pct": int((df_outcomes["cost_overrun_pct"] > 100).sum())
        }
    }
    return report
