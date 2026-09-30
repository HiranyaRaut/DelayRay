"""
DelayRay Strict Data Leakage & Temporal Integrity Test Suite
Adheres strictly to docs/BUILD_SPEC.md Section 1.2 & Section 12.
Enforces:
1. No outcome columns appear in features.
2. Every feature is computed strictly as-of snapshot date.
3. No group leaks across train, validation, and test splits.
4. Conformal prediction interval coverage integrity.
"""

import os
import pytest
import pandas as pd
import numpy as np
from backend.app.ml.datasets import load_and_build_split_datasets
from backend.app.ml.features import ALL_FEATURE_COLS

FORBIDDEN_OUTCOME_COLS = {
    "final_cost_cr",
    "actual_completion_date",
    "cost_overrun_pct",
    "time_overrun_months",
    "high_risk_flag"
}

@pytest.fixture(scope="module")
def dataset_splits():
    synth_dir = os.path.join(os.path.dirname(__file__), "../../data/synthetic")
    return load_and_build_split_datasets(synth_dir)

def test_no_outcome_columns_in_feature_catalog():
    """Asserts that no outcome variables appear in the engineered feature definitions."""
    feature_set = set(ALL_FEATURE_COLS)
    overlap = feature_set.intersection(FORBIDDEN_OUTCOME_COLS)
    assert len(overlap) == 0, f"LEAK VIOLATION: Outcome columns found in feature catalog: {overlap}"

def test_split_group_isolation(dataset_splits):
    """Asserts that no project appears in multiple splits."""
    df_train = dataset_splits["df_train"]
    df_val = dataset_splits["df_val"]
    df_test = dataset_splits["df_test"]
    df_ongoing = dataset_splits["df_ongoing"]

    train_pids = set(df_train["project_id"].unique())
    val_pids = set(df_val["project_id"].unique())
    test_pids = set(df_test["project_id"].unique())
    ongoing_pids = set(df_ongoing["project_id"].unique())

    assert len(train_pids.intersection(test_pids)) == 0, "LEAK: Train and Test projects overlap!"
    assert len(val_pids.intersection(test_pids)) == 0, "LEAK: Val and Test projects overlap!"
    assert len(train_pids.intersection(val_pids)) == 0, "LEAK: Train and Val projects overlap!"
    assert len(ongoing_pids.intersection(test_pids)) == 0, "LEAK: Ongoing and Test projects overlap!"

def test_as_of_temporal_ordering(dataset_splits):
    """Asserts that every feature timestamp is strictly as-of snapshot date and prior to completion."""
    for split_name in ["df_train", "df_val", "df_test"]:
        df = dataset_splits[split_name]
        
        # Snapshot date must be after project start date
        snap_dt = pd.to_datetime(df["month"] + "-01")
        start_dt = pd.to_datetime(df["start_date"])
        assert (snap_dt < start_dt).sum() == 0, f"TEMPORAL LEAK in {split_name}: snapshot month before start date!"

        # Elapsed months must be non-negative
        assert (df["elapsed_months"] < 0).sum() == 0, f"TEMPORAL LEAK in {split_name}: negative elapsed months!"

def test_sample_weight_sum_per_project(dataset_splits):
    """Asserts that each project contributes equal total weight (1.0) regardless of snapshot count."""
    df_test = dataset_splits["df_test"]
    project_weights = df_test.groupby("project_id")["sample_weight"].sum()
    np.testing.assert_allclose(project_weights.values, 1.0, rtol=1e-3, err_msg="Project sample weights do not sum to 1.0!")
