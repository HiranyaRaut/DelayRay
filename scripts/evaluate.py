"""
DelayRay Evaluation & Slice Performance Runner
Adheres strictly to docs/BUILD_SPEC.md Section 6.4.
"""

import os
import sys
import json
import joblib
import pandas as pd
import numpy as np

ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT_DIR)

from backend.app.ml.datasets import load_and_build_split_datasets
from backend.app.ml.features import ALL_FEATURE_COLS
from backend.app.ml.models import build_preprocessor
from backend.app.ml.evaluate import evaluate_slice_performance

def main():
    print("==================================================================")
    print("   DelayRay Evaluation & Performance Slicing")
    print("==================================================================")
    
    data_dict = load_and_build_split_datasets("data/synthetic")
    df_train = data_dict["df_train"]
    df_test = data_dict["df_test"]

    # Load model
    model_path = os.path.join(ROOT_DIR, "ml_artifacts", "models", "stacked_cost_regressor_v1.0.joblib")
    if not os.path.exists(model_path):
        print(f"Model not found at {model_path}. Skipping slice evaluation.")
        return

    model = joblib.load(model_path)
    feature_cols = [c for c in ALL_FEATURE_COLS if c in df_train.columns]
    preprocessor, _ = build_preprocessor(feature_cols)
    preprocessor.fit(df_train[feature_cols])

    X_test_trans = preprocessor.transform(df_test[feature_cols])
    df_test["pred_cost_overrun"] = model.predict(X_test_trans)

    # Cost bands
    df_test["cost_band"] = pd.cut(
        df_test["original_cost_cr"],
        bins=[0, 500, 2000, 5000, np.inf],
        labels=["₹150-500 Cr", "₹500-2000 Cr", "₹2000-5000 Cr", ">₹5000 Cr"]
    )

    # Duration stage
    df_test["duration_stage"] = pd.cut(
        df_test["elapsed_ratio"],
        bins=[-0.1, 0.35, 0.65, 3.0],
        labels=["25% Stage", "50% Stage", "75%+ Stage"]
    )

    sector_slices = evaluate_slice_performance(df_test, "cost_overrun_pct", "pred_cost_overrun", "sector")
    cost_slices = evaluate_slice_performance(df_test, "cost_overrun_pct", "pred_cost_overrun", "cost_band")
    stage_slices = evaluate_slice_performance(df_test, "cost_overrun_pct", "pred_cost_overrun", "duration_stage")

    reports_dir = os.path.join(ROOT_DIR, "ml_artifacts", "reports")
    with open(os.path.join(reports_dir, "slices.json"), "w", encoding="utf-8") as f:
        json.dump({
            "by_sector": sector_slices,
            "by_cost_band": cost_slices,
            "by_duration_stage": stage_slices
        }, f, indent=2)

    print("Slice performance evaluated and saved to ml_artifacts/reports/slices.json.")

if __name__ == "__main__":
    main()
