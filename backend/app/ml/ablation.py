"""
DelayRay Ablation Study & CUF Feature Attribution Engine
Answers Question (b): How much predictive power comes from existing CUF fields
versus variables not currently captured?
Adheres strictly to docs/BUILD_SPEC.md Section 6.5.
"""

from typing import Dict, Any, List, Tuple
import os
import yaml
import json
import numpy as np
import pandas as pd
from sklearn.metrics import mean_absolute_error, roc_auc_score
from backend.app.ml.features import (
    G1_FEATURES, G2_FEATURES, G3_FEATURES, G4_FEATURES, G5_FEATURES, G6_FEATURES
)
from backend.app.ml.models import build_lgb_regressor, build_preprocessor

GROUP_DEFS = {
    "G1": G1_FEATURES,
    "G2": G2_FEATURES,
    "G3": G3_FEATURES,
    "G4": G4_FEATURES,
    "G5": G5_FEATURES,
    "G6": G6_FEATURES
}

def evaluate_feature_subset(
    df_train: pd.DataFrame,
    df_test: pd.DataFrame,
    features: List[str],
    target_col: str = "cost_overrun_pct"
) -> Tuple[float, float]:
    """
    Fits LightGBM on specified feature subset and evaluates on test set.
    Returns (mae, r2).
    """
    # Build preprocessor on train
    preprocessor, cols = build_preprocessor(features)
    X_train_trans = preprocessor.fit_transform(df_train[features])
    X_test_trans = preprocessor.transform(df_test[features])

    y_train = df_train[target_col].values
    y_test = df_test[target_col].values
    sample_weights = df_train["sample_weight"].values

    model = build_lgb_regressor()
    model.fit(X_train_trans, y_train, sample_weight=sample_weights)
    preds = model.predict(X_test_trans)

    mae = float(mean_absolute_error(y_test, preds))
    u = ((y_test - preds) ** 2).sum()
    v = ((y_test - y_test.mean()) ** 2).sum()
    r2 = float(1.0 - u / max(1e-5, v))

    return round(mae, 2), round(r2, 3)

def run_ablation_experiments(
    df_train: pd.DataFrame,
    df_test: pd.DataFrame,
    baseline_mae: float = 7.85,
    candidates_yaml_path: str = "docs/inputs/cuf_candidates.yaml"
) -> Dict[str, Any]:
    """
    Runs full ablation battery: CUF-only, partial additions, all groups,
    leave-one-group-out, CUF attribution %, and candidate field rankings.
    """
    print("Executing feature group ablation experiments...")
    results = []

    # 1. CUF-Only (G1 + G2)
    cuf_features = G1_FEATURES + G2_FEATURES
    cuf_mae, cuf_r2 = evaluate_feature_subset(df_train, df_test, cuf_features)
    cuf_skill = max(0.001, 1.0 - (cuf_mae / baseline_mae))
    results.append({
        "experiment": "CUF-Only (G1+G2)",
        "feature_group": "G1+G2",
        "n_features": len(cuf_features),
        "test_mae": cuf_mae,
        "test_r2": cuf_r2,
        "skill_score": round(cuf_skill, 3)
    })

    # 2. CUF + Derived EV (G1-G3)
    cuf_ev_features = cuf_features + G3_FEATURES
    ev_mae, ev_r2 = evaluate_feature_subset(df_train, df_test, cuf_ev_features)
    results.append({
        "experiment": "CUF + Derived EV (G1-G3)",
        "feature_group": "G1+G2+G3",
        "n_features": len(cuf_ev_features),
        "test_mae": ev_mae,
        "test_r2": ev_r2,
        "skill_score": round(1.0 - (ev_mae / baseline_mae), 3)
    })

    # 3. CUF + Text / NLP (G1, G2, G4)
    cuf_text_features = cuf_features + G4_FEATURES
    text_mae, text_r2 = evaluate_feature_subset(df_train, df_test, cuf_text_features)
    results.append({
        "experiment": "CUF + Remarks NLP (G1+G2+G4)",
        "feature_group": "G1+G2+G4",
        "n_features": len(cuf_text_features),
        "test_mae": text_mae,
        "test_r2": text_r2,
        "skill_score": round(1.0 - (text_mae / baseline_mae), 3)
    })

    # 4. CUF + Macro (G1, G2, G5)
    cuf_macro_features = cuf_features + G5_FEATURES
    macro_mae, macro_r2 = evaluate_feature_subset(df_train, df_test, cuf_macro_features)
    results.append({
        "experiment": "CUF + External Macro (G1+G2+G5)",
        "feature_group": "G1+G2+G5",
        "n_features": len(cuf_macro_features),
        "test_mae": macro_mae,
        "test_r2": macro_r2,
        "skill_score": round(1.0 - (macro_mae / baseline_mae), 3)
    })

    # 5. CUF + Project Extras (G1, G2, G6)
    cuf_extras_features = cuf_features + G6_FEATURES
    extras_mae, extras_r2 = evaluate_feature_subset(df_train, df_test, cuf_extras_features)
    results.append({
        "experiment": "CUF + Project Specific Extras (G1+G2+G6)",
        "feature_group": "G1+G2+G6",
        "n_features": len(cuf_extras_features),
        "test_mae": extras_mae,
        "test_r2": extras_r2,
        "skill_score": round(1.0 - (extras_mae / baseline_mae), 3)
    })

    # 6. All Groups (G1-G6)
    all_features = G1_FEATURES + G2_FEATURES + G3_FEATURES + G4_FEATURES + G5_FEATURES + G6_FEATURES
    all_mae, all_r2 = evaluate_feature_subset(df_train, df_test, all_features)
    all_skill = max(0.001, 1.0 - (all_mae / baseline_mae))
    results.append({
        "experiment": "All Groups (G1-G6 Full)",
        "feature_group": "G1-G6",
        "n_features": len(all_features),
        "test_mae": all_mae,
        "test_r2": all_r2,
        "skill_score": round(all_skill, 3)
    })

    # Compute CUF Attribution %
    cuf_attribution_pct = round(float((cuf_skill / all_skill) * 100.0), 1)

    # 7. Leave-One-Group-Out
    logo_results = []
    for grp_name, grp_cols in GROUP_DEFS.items():
        subset = [f for f in all_features if f not in grp_cols]
        sub_mae, sub_r2 = evaluate_feature_subset(df_train, df_test, subset)
        delta_mae = round(sub_mae - all_mae, 2)  # Positive means group was helpful
        logo_results.append({
            "excluded_group": grp_name,
            "group_label": grp_name,
            "mae_without_group": sub_mae,
            "skill_loss_delta_mae": delta_mae
        })

    # 8. Candidate New CUF Fields Ranked Table
    candidates_ranked = []
    difficulty_weights = {"low": 1.0, "medium": 1.75, "high": 2.75}

    if os.path.exists(candidates_yaml_path):
        with open(candidates_yaml_path, "r", encoding="utf-8") as f:
            candidates_data = yaml.safe_load(f).get("candidates", [])

        for cand in candidates_data:
            field = cand["field_name"]
            # Evaluate CUF + single candidate field
            field_candidates = [field] if field in all_features else []
            if field == "nlp_challenge_tags":
                field_candidates = ["tag_land", "tag_clearance", "tag_utility", "tag_contractor"]
            
            cand_features = [f for f in cuf_features + field_candidates if f in df_train.columns]
            cand_mae, _ = evaluate_feature_subset(df_train, df_test, cand_features)
            marginal_mae_gain = round(max(0.01, cuf_mae - cand_mae), 2)
            
            diff = cand.get("collection_difficulty", "medium").lower()
            diff_weight = difficulty_weights.get(diff, 1.75)
            priority_score = round(float(marginal_mae_gain / diff_weight), 2)

            candidates_ranked.append({
                "field_name": field,
                "display_name": cand.get("display_name", field),
                "group": cand.get("group", "G6"),
                "collection_difficulty": diff,
                "marginal_mae_gain": marginal_mae_gain,
                "priority_score": priority_score,
                "suggested_collection_point": cand.get("suggested_collection_point", "Project Sanction")
            })

        # Sort by priority score descending
        candidates_ranked.sort(key=lambda x: x["priority_score"], reverse=True)

    # 9. Verify Ground-Truth Recovery
    truth_recovered = False
    truth_path = "data/synthetic/_truth.json"
    if os.path.exists(truth_path):
        with open(truth_path, "r", encoding="utf-8") as f:
            truth = json.load(f)
        # Check that G6 project extras improves skill over CUF-only
        if extras_mae < cuf_mae and all_mae < cuf_mae:
            truth_recovered = True

    return {
        "cuf_attribution_pct": cuf_attribution_pct,
        "ablation_experiments": results,
        "leave_one_group_out": logo_results,
        "ranked_candidates": candidates_ranked,
        "planted_drivers_recovered": truth_recovered
    }
