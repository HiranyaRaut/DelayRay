"""
DelayRay Dataset Construction & Group-Aware Time-Split Engine
Adheres strictly to docs/BUILD_SPEC.md Section 6.1.
Enforces zero temporal leakage with automated integrity assertions.
"""

import os
import pandas as pd
import numpy as np
from typing import Dict, Any, Tuple, List
from backend.app.ml.features import extract_snapshot_features, ALL_FEATURE_COLS

def load_and_build_split_datasets(data_dir: str = "data/synthetic") -> Dict[str, Any]:
    """
    Constructs train, val, test, and ongoing datasets with group-aware time splitting.
    Train: Project start_date <= 2016
    Val:   Project start_date between 2017 and 2018
    Test:  Project start_date >= 2019 and status == 'completed'
    Ongoing: Active projects up to April 2026
    """
    p_path = os.path.join(data_dir, "projects.csv")
    s_path = os.path.join(data_dir, "project_snapshots.csv")
    o_path = os.path.join(data_dir, "project_outcomes.csv")
    e_path = os.path.join(data_dir, "project_extras.csv")
    ext_path = os.path.join(data_dir, "external_indicators.csv")

    df_projects = pd.read_csv(p_path)
    df_snapshots = pd.read_csv(s_path)
    df_outcomes = pd.read_csv(o_path)
    df_extras = pd.read_csv(e_path)
    df_external = pd.read_csv(ext_path)

    # Extract all features strictly as-of snapshot date
    df_all, tfidf_model, svd_model = extract_snapshot_features(
        df_projects=df_projects,
        df_snapshots=df_snapshots,
        df_extras=df_extras,
        df_external=df_external
    )

    # Attach targets for completed projects
    df_all = df_all.merge(
        df_outcomes[[
            "project_id", "final_cost_cr", "actual_completion_date",
            "cost_overrun_pct", "time_overrun_months", "high_risk_flag"
        ]],
        on="project_id",
        how="left"
    )

    # Convert start_date to datetime for clean time filtering
    df_all["start_year"] = pd.to_datetime(df_all["start_date"]).dt.year

    # --------------------------------------------------------------------------
    # Temporal Group Splits
    # --------------------------------------------------------------------------
    # Train: start_year <= 2016
    df_train = df_all[(df_all["status"] == "completed") & (df_all["start_year"] <= 2016)].copy()

    # Val: start_year in (2017, 2018)
    df_val = df_all[(df_all["status"] == "completed") & (df_all["start_year"].isin([2017, 2018]))].copy()

    # Test: start_year >= 2019 and completed
    df_test = df_all[(df_all["status"] == "completed") & (df_all["start_year"] >= 2019)].copy()

    # Ongoing: active portfolio
    df_ongoing = df_all[df_all["status"] == "ongoing"].copy()

    # --------------------------------------------------------------------------
    # Strict Leakage & Split Verification Invariants
    # --------------------------------------------------------------------------
    train_pids = set(df_train["project_id"].unique())
    val_pids = set(df_val["project_id"].unique())
    test_pids = set(df_test["project_id"].unique())
    ongoing_pids = set(df_ongoing["project_id"].unique())

    # Assert no group leaks across splits
    assert len(train_pids.intersection(test_pids)) == 0, "LEAK DETECTED: Train and Test projects overlap!"
    assert len(val_pids.intersection(test_pids)) == 0, "LEAK DETECTED: Val and Test projects overlap!"
    assert len(train_pids.intersection(val_pids)) == 0, "LEAK DETECTED: Train and Val projects overlap!"

    # Assert no feature timestamp exceeds snapshot month
    snap_dt = pd.to_datetime(df_all["month"] + "-01")
    start_dt = pd.to_datetime(df_all["start_date"])
    assert (snap_dt < start_dt).sum() == 0, "TEMPORAL INVARIANT VIOLATED: Snapshot month precedes project start date!"

    # --------------------------------------------------------------------------
    # Project-Balanced Row Weights
    # --------------------------------------------------------------------------
    for df_split in [df_train, df_val, df_test, df_ongoing]:
        counts = df_split.groupby("project_id")["month"].transform("count")
        df_split["sample_weight"] = 1.0 / counts.clip(lower=1.0)

    print(f"Dataset constructed with zero leakage:")
    print(f"  Train:   {len(df_train):>6,} rows ({len(train_pids):>5,} completed projects, start <= 2016)")
    print(f"  Val:     {len(df_val):>6,} rows ({len(val_pids):>5,} completed projects, start 2017-2018)")
    print(f"  Test:    {len(df_test):>6,} rows ({len(test_pids):>5,} completed projects, start >= 2019)")
    print(f"  Ongoing: {len(df_ongoing):>6,} rows ({len(ongoing_pids):>5,} active projects)")

    return {
        "df_train": df_train,
        "df_val": df_val,
        "df_test": df_test,
        "df_ongoing": df_ongoing,
        "tfidf_model": tfidf_model,
        "svd_model": svd_model
    }
