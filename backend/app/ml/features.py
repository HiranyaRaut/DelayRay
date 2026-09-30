"""
DelayRay Feature Engineering & Feature Group Taxonomy (G1 - G6)
Adheres strictly to docs/BUILD_SPEC.md Section 6.2.
"""

from typing import List, Dict, Any, Tuple
import numpy as np
import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.decomposition import TruncatedSVD

FEATURE_GROUPS = {
    "G1": "CUF Static",
    "G2": "CUF Progress",
    "G3": "Derived Earned-Value",
    "G4": "Text & NLP Challenge Tags",
    "G5": "External Macroeconomic",
    "G6": "External Project-Specific"
}

G1_FEATURES = [
    "original_cost_cr",
    "planned_duration_months",
    "sector",
    "ministry",
    "primary_state",
    "agency_type",
    "funding_mode"
]

G2_FEATURES = [
    "elapsed_months",
    "elapsed_ratio",
    "physical_progress_pct",
    "planned_progress_pct",
    "spend_pct",
    "revision_count_to_date",
    "cost_revised_pct"
]

G3_FEATURES = [
    "spi",
    "cost_efficiency",
    "progress_gap",
    "spend_gap",
    "progress_velocity_3m",
    "acceleration",
    "months_since_progress",
    "milestone_slip_ratio"
]

G4_TAGS = [
    "tag_land",
    "tag_clearance",
    "tag_utility",
    "tag_contractor",
    "tag_funds",
    "tag_weather",
    "tag_design"
]

G4_FEATURES = G4_TAGS + ["remarks_svd_0", "remarks_svd_1", "remarks_svd_2"]

G5_FEATURES = [
    "rainfall_anomaly_pct",
    "steel_price_index",
    "cement_price_index",
    "crude_oil_price_index"
]

G6_FEATURES = [
    "land_acquisition_pct_at_start",
    "env_forest_clearance_delay_months",
    "utility_shifting_count",
    "contractor_performance_score",
    "contractor_concurrent_projects",
    "geotechnical_uncertainty_score",
    "design_changes_count",
    "local_law_order_index",
    "terrain_class",
    "env_forest_clearance_status",
    "utility_shifting_complexity"
]

ALL_FEATURE_COLS = G1_FEATURES + G2_FEATURES + G3_FEATURES + G4_FEATURES + G5_FEATURES + G6_FEATURES

def extract_snapshot_features(
    df_projects: pd.DataFrame,
    df_snapshots: pd.DataFrame,
    df_extras: pd.DataFrame,
    df_external: pd.DataFrame,
    df_remarks: pd.DataFrame = None,
    tfidf_model: TfidfVectorizer = None,
    svd_model: TruncatedSVD = None
) -> Tuple[pd.DataFrame, TfidfVectorizer, TruncatedSVD]:
    """
    Computes all features strictly as-of each snapshot date.
    Zero leakage: Outcome columns are never accessed.
    """
    # Merge project static fields (G1)
    df = df_snapshots.merge(
        df_projects[[
            "project_id", "project_name", "ministry", "sector", "primary_state",
            "implementing_agency", "agency_type", "sanction_date", "start_date",
            "original_cost_cr", "original_completion_date", "planned_duration_months",
            "funding_mode", "status"
        ]],
        on="project_id",
        how="inner"
    )

    # Merge project extras (G6)
    if df_extras is not None:
        df = df.merge(df_extras, on="project_id", how="left")

    # Merge external indicators by (month, state) (G5)
    if df_external is not None:
        df = df.merge(
            df_external[[
                "month", "state", "rainfall_anomaly_pct", "steel_price_index",
                "cement_price_index", "crude_oil_price_index"
            ]],
            left_on=["month", "primary_state"],
            right_on=["month", "state"],
            how="left"
        )
        if "state" in df.columns:
            df.drop(columns=["state"], inplace=True)

    # --------------------------------------------------------------------------
    # G2 CUF Progress Derivations
    # --------------------------------------------------------------------------
    start_dt = pd.to_datetime(df["start_date"])
    snap_dt = pd.to_datetime(df["month"] + "-01")
    df["elapsed_months"] = ((snap_dt.dt.year - start_dt.dt.year) * 12 + (snap_dt.dt.month - start_dt.dt.month)).clip(lower=1)
    df["elapsed_ratio"] = (df["elapsed_months"] / df["planned_duration_months"].clip(lower=1.0)).clip(lower=0.0, upper=3.0)

    # Spend % of original cost
    df["spend_pct"] = ((df["cumulative_expenditure_cr"] / df["original_cost_cr"].clip(lower=1.0)) * 100.0).clip(lower=0.0, upper=300.0)

    # Revised cost %
    raw_revised = np.where(
        df["cost_revised_to_date_cr"].notna() & (df["original_cost_cr"] > 0),
        ((df["cost_revised_to_date_cr"] - df["original_cost_cr"]) / df["original_cost_cr"]) * 100.0,
        0.0
    )
    df["cost_revised_pct"] = np.clip(raw_revised, 0.0, None)

    # --------------------------------------------------------------------------
    # G3 Derived Earned-Value Metrics
    # --------------------------------------------------------------------------
    # SPI = Physical % / Planned % (clamped for stability)
    df["spi"] = (df["physical_progress_pct"] / df["planned_progress_pct"].clip(lower=1.0)).clip(lower=0.05, upper=2.5)

    # Cost Efficiency = Physical % / Spend %
    df["cost_efficiency"] = (df["physical_progress_pct"] / df["spend_pct"].clip(lower=1.0)).clip(lower=0.05, upper=2.5)

    df["progress_gap"] = df["planned_progress_pct"] - df["physical_progress_pct"]
    df["spend_gap"] = df["spend_pct"] - df["physical_progress_pct"]

    # Trajectory Slopes (sort by project and month)
    df = df.sort_values(["project_id", "month"]).reset_index(drop=True)
    df["prev_prog_1"] = df.groupby("project_id")["physical_progress_pct"].shift(1).fillna(0.0)
    df["prev_prog_3"] = df.groupby("project_id")["physical_progress_pct"].shift(3).fillna(0.0)
    
    # 3-month velocity slope (% per month)
    df["progress_velocity_3m"] = ((df["physical_progress_pct"] - df["prev_prog_3"]) / 3.0).clip(lower=-5.0, upper=30.0)
    
    # Acceleration = current 1m delta - prev 1m delta
    df["delta_prog_curr"] = df["physical_progress_pct"] - df["prev_prog_1"]
    df["delta_prog_prev"] = df.groupby("project_id")["delta_prog_curr"].shift(1).fillna(0.0)
    df["acceleration"] = (df["delta_prog_curr"] - df["delta_prog_prev"]).clip(lower=-20.0, upper=20.0)

    # Months since progress stall
    stalled = (df["delta_prog_curr"] <= 0.05).astype(int)
    # Cumulative consecutive stall months
    df["months_since_progress"] = stalled.groupby((~stalled.astype(bool)).cumsum()).cumsum()

    # Milestone slip ratio
    planned_ms = df["milestones_planned_to_date"].clip(lower=1)
    achieved_ms = df["milestones_achieved_to_date"]
    slip_calc = np.where(
        df["milestones_planned_to_date"] > 0,
        (planned_ms - achieved_ms).clip(lower=0) / planned_ms,
        0.0
    )
    df["milestone_slip_ratio"] = np.clip(slip_calc, 0.0, 1.0)

    # --------------------------------------------------------------------------
    # G4 Unstructured Text / NLP Features
    # --------------------------------------------------------------------------
    remarks_text = df["remarks"].fillna("").astype(str).str.lower()
    
    # Keyword/tag indicator matching
    df["tag_land"] = remarks_text.str.contains("land|row|possession|village|dispute").astype(float)
    df["tag_clearance"] = remarks_text.str.contains("clearance|forest|tree|environment|crz").astype(float)
    df["tag_utility"] = remarks_text.str.contains("utility|electric|pipeline|sewer|water").astype(float)
    df["tag_contractor"] = remarks_text.str.contains("contractor|machinery|mobiliz|manpower|slow").astype(float)
    df["tag_funds"] = remarks_text.str.contains("fund|grant|disburs|budget|payment").astype(float)
    df["tag_weather"] = remarks_text.str.contains("rain|monsoon|flood|inundat|weather").astype(float)
    df["tag_design"] = remarks_text.str.contains("design|drawing|geotech|consultant|scope").astype(float)

    # TF-IDF + SVD reduction
    if tfidf_model is None:
        tfidf_model = TfidfVectorizer(max_features=250, stop_words="english")
        tfidf_matrix = tfidf_model.fit_transform(remarks_text)
        svd_model = TruncatedSVD(n_components=3, random_state=42)
        svd_matrix = svd_model.fit_transform(tfidf_matrix)
    else:
        tfidf_matrix = tfidf_model.transform(remarks_text)
        svd_matrix = svd_model.transform(tfidf_matrix)

    df["remarks_svd_0"] = svd_matrix[:, 0]
    df["remarks_svd_1"] = svd_matrix[:, 1]
    df["remarks_svd_2"] = svd_matrix[:, 2]

    # Fill any remaining NaNs in G5/G6
    for col in G5_FEATURES:
        if col in df.columns:
            df[col] = df[col].fillna(df[col].median() if len(df[col].dropna()) > 0 else 0.0)

    for col in G6_FEATURES:
        if col in df.columns and df[col].dtype in (np.float64, np.int64, float, int):
            df[col] = df[col].fillna(df[col].median() if len(df[col].dropna()) > 0 else 0.0)

    return df, tfidf_model, svd_model
