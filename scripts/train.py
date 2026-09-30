"""
DelayRay Master Machine Learning Training & Evaluation Orchestrator
Executes Section 6 of docs/BUILD_SPEC.md:
- Leak-free dataset splits (Train <= 2016, Val 2017-2018, Test >= 2019)
- Statistical baselines (B0 Sector-median, B1 Ridge, B2 Logistic, B4 Earned-Value)
- ML models (LightGBM, XGBoost, Random Forest, Stacked Ensembles)
- Isotonic calibration (0-100 Risk Score) & Split Conformal Intervals (P10-P90)
- Paired bootstrap significance testing & Auto-Verdict generation
- Anomaly & Drift monitoring (IsolationForest & PSI)
- SHAP explanations & Model Registry tracking
- Populates database predictions & explanations
"""

import os
import sys
import json
import numpy as np
import pandas as pd
from datetime import datetime, timezone
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

# Add repository root to python path
ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT_DIR)

from backend.app.ml.datasets import load_and_build_split_datasets
from backend.app.ml.features import ALL_FEATURE_COLS
from backend.app.ml.baselines import SectorMedianBaseline, EarnedValueBaseline, build_linear_baseline
from backend.app.ml.models import (
    build_preprocessor, build_lgb_regressor, build_xgb_regressor,
    build_rf_regressor, build_lgb_classifier, build_xgb_classifier,
    StackedEnsembleRegressor
)
from backend.app.ml.calibrate import RiskScoreCalibrator
from backend.app.ml.conformal import ConformalIntervalPredictor
from backend.app.ml.survival import SurvivalAnalysisSuite
from backend.app.ml.significance import compute_significance_verdict
from backend.app.ml.explain import ExplainabilitySuite
from backend.app.ml.drift import evaluate_portfolio_drift
from backend.app.ml.anomaly import TrajectoryAnomalyDetector
from backend.app.ml.registry import ModelArtifactManager
from backend.app.ml.evaluate import (
    evaluate_regression_metrics, evaluate_classification_metrics,
    evaluate_slice_performance, compute_lead_time_distribution
)
from backend.app.db.session import SessionLocal
from backend.app.db.models import Prediction, Explanation

def main():
    print("==================================================================")
    print("   DelayRay Master Machine Learning Pipeline (Phase 2)")
    print("==================================================================")

    # 1. Dataset Construction with strict temporal splits
    data_dict = load_and_build_split_datasets("data/synthetic")
    df_train = data_dict["df_train"]
    df_val = data_dict["df_val"]
    df_test = data_dict["df_test"]
    df_ongoing = data_dict["df_ongoing"]

    # Target arrays
    y_train_cost = df_train["cost_overrun_pct"].values
    y_val_cost = df_val["cost_overrun_pct"].values
    y_test_cost = df_test["cost_overrun_pct"].values

    y_train_delay = df_train["time_overrun_months"].values
    y_val_delay = df_val["time_overrun_months"].values
    y_test_delay = df_test["time_overrun_months"].values

    y_train_risk = df_train["high_risk_flag"].astype(int).values
    y_val_risk = df_val["high_risk_flag"].astype(int).values
    y_test_risk = df_test["high_risk_flag"].astype(int).values

    w_train = df_train["sample_weight"].values

    # 2. Preprocessor Fitting (Train set only)
    feature_cols = [c for c in ALL_FEATURE_COLS if c in df_train.columns]
    preprocessor, transformed_feature_names = build_preprocessor(feature_cols)

    X_train_trans = preprocessor.fit_transform(df_train[feature_cols])
    X_val_trans = preprocessor.transform(df_val[feature_cols])
    X_test_trans = preprocessor.transform(df_test[feature_cols])
    X_ongoing_trans = preprocessor.transform(df_ongoing[feature_cols])

    # 3. Train Conventional & Statistical Baselines
    print("\n--- Training Statistical Baselines (B0, B1, B2, B4 EVM) ---")
    # B0 Sector Median
    b0_model = SectorMedianBaseline().fit(df_train, df_train["cost_overrun_pct"], df_train["time_overrun_months"])
    b0_test_cost = b0_model.predict_cost(df_test)
    b0_test_delay = b0_model.predict_delay(df_test)
    b0_cost_mae = float(np.mean(np.abs(y_test_cost - b0_test_cost)))

    # B4 Earned Value Management Forecast
    b4_model = EarnedValueBaseline()
    b4_test_cost = b4_model.predict_cost(df_test)
    b4_test_delay = b4_model.predict_delay(df_test)

    # B1 Ridge Regressors
    b1_cost_model = build_linear_baseline(task="regression", alpha=10.0)
    b1_cost_model.fit(X_train_trans, y_train_cost)
    b1_test_cost = b1_cost_model.predict(X_test_trans)

    b1_delay_model = build_linear_baseline(task="regression", alpha=10.0)
    b1_delay_model.fit(X_train_trans, y_train_delay)
    b1_test_delay = b1_delay_model.predict(X_test_trans)

    # B2 Logistic Classifier
    b2_risk_model = build_linear_baseline(task="classification", alpha=1.0)
    b2_risk_model.fit(X_train_trans, y_train_risk)
    b2_test_prob = b2_risk_model.predict_proba(X_test_trans)[:, 1]

    # 4. Train ML Models
    print("\n--- Training Machine Learning Models (LightGBM, XGBoost, Random Forest) ---")
    # T1 Cost Overrun %
    lgb_cost = build_lgb_regressor(feature_names=transformed_feature_names)
    lgb_cost.fit(X_train_trans, y_train_cost, sample_weight=w_train)

    xgb_cost = build_xgb_regressor()
    xgb_cost.fit(X_train_trans, y_train_cost, sample_weight=w_train)

    rf_cost = build_rf_regressor()
    rf_cost.fit(X_train_trans, y_train_cost, sample_weight=w_train)

    stacked_cost = StackedEnsembleRegressor(lgb_cost, xgb_cost, rf_cost)
    ml_test_cost = stacked_cost.predict(X_test_trans)

    # T2 Delay Months
    lgb_delay = build_lgb_regressor(feature_names=transformed_feature_names)
    lgb_delay.fit(X_train_trans, y_train_delay, sample_weight=w_train)

    xgb_delay = build_xgb_regressor()
    xgb_delay.fit(X_train_trans, y_train_delay, sample_weight=w_train)

    rf_delay = build_rf_regressor()
    rf_delay.fit(X_train_trans, y_train_delay, sample_weight=w_train)

    stacked_delay = StackedEnsembleRegressor(lgb_delay, xgb_delay, rf_delay)
    ml_test_delay = stacked_delay.predict(X_test_trans)

    # T3 High Risk Classification
    lgb_risk = build_lgb_classifier()
    lgb_risk.fit(X_train_trans, y_train_risk, sample_weight=w_train)

    xgb_risk = build_xgb_classifier()
    xgb_risk.fit(X_train_trans, y_train_risk, sample_weight=w_train)

    val_raw_prob = 0.55 * lgb_risk.predict_proba(X_val_trans)[:, 1] + 0.45 * xgb_risk.predict_proba(X_val_trans)[:, 1]
    test_raw_prob = 0.55 * lgb_risk.predict_proba(X_test_trans)[:, 1] + 0.45 * xgb_risk.predict_proba(X_test_trans)[:, 1]

    # 5. Isotonic Probability Calibration
    print("\n--- Fitting Isotonic Probability Calibrator ---")
    calibrator = RiskScoreCalibrator().fit(y_val_risk, val_raw_prob)
    test_calibrated_prob = calibrator.calibrate(test_raw_prob)

    # 6. Split Conformal Intervals (P10, P50, P90)
    print("\n--- Fitting Split Conformal Interval Regressor ---")
    conformal_cost = ConformalIntervalPredictor(alpha=0.20)
    conformal_cost.fit(X_train_trans, y_train_cost, X_val_trans, y_val_cost)
    cost_coverage = conformal_cost.evaluate_coverage(X_test_trans, y_test_cost)

    conformal_delay = ConformalIntervalPredictor(alpha=0.20)
    conformal_delay.fit(X_train_trans, y_train_delay, X_val_trans, y_val_delay)
    delay_coverage = conformal_delay.evaluate_coverage(X_test_trans, y_test_delay)

    # 7. Survival Analytics (Task T4)
    print("\n--- Fitting Survival Models (Cox PH & Kaplan-Meier) ---")
    survival_suite = SurvivalAnalysisSuite()
    survival_metrics = survival_suite.fit(df_train)

    # 8. Model Evaluation & Leaderboard
    print("\n--- Compiling Performance Leaderboard on Hold-Out Test Set ---")
    leaderboard = [
        {"model_name": "B0 Sector Median", "task": "Cost Overrun %", "type": "Statistical Baseline", **evaluate_regression_metrics(y_test_cost, b0_test_cost, b0_cost_mae)},
        {"model_name": "B4 EVM Forecast (EAC)", "task": "Cost Overrun %", "type": "Statistical Baseline", **evaluate_regression_metrics(y_test_cost, b4_test_cost, b0_cost_mae)},
        {"model_name": "B1 Ridge Regression", "task": "Cost Overrun %", "type": "Linear Baseline", **evaluate_regression_metrics(y_test_cost, b1_test_cost, b0_cost_mae)},
        {"model_name": "LightGBM Regressor", "task": "Cost Overrun %", "type": "Machine Learning", **evaluate_regression_metrics(y_test_cost, lgb_cost.predict(X_test_trans), b0_cost_mae)},
        {"model_name": "XGBoost Regressor", "task": "Cost Overrun %", "type": "Machine Learning", **evaluate_regression_metrics(y_test_cost, xgb_cost.predict(X_test_trans), b0_cost_mae)},
        {"model_name": "Stacked ML Ensemble", "task": "Cost Overrun %", "type": "Champion ML", **evaluate_regression_metrics(y_test_cost, ml_test_cost, b0_cost_mae)},

        {"model_name": "B0 Sector Median", "task": "Delay Months", "type": "Statistical Baseline", **evaluate_regression_metrics(y_test_delay, b0_test_delay)},
        {"model_name": "B4 EVM Schedule (SPI)", "task": "Delay Months", "type": "Statistical Baseline", **evaluate_regression_metrics(y_test_delay, b4_test_delay)},
        {"model_name": "B1 Ridge Regression", "task": "Delay Months", "type": "Linear Baseline", **evaluate_regression_metrics(y_test_delay, b1_test_delay)},
        {"model_name": "LightGBM Regressor", "task": "Delay Months", "type": "Machine Learning", **evaluate_regression_metrics(y_test_delay, lgb_delay.predict(X_test_trans))},
        {"model_name": "Stacked ML Ensemble", "task": "Delay Months", "type": "Champion ML", **evaluate_regression_metrics(y_test_delay, ml_test_delay)},

        {"model_name": "B2 Logistic Regression", "task": "High-Risk Flag", "type": "Statistical Baseline", **evaluate_classification_metrics(y_test_risk, b2_test_prob)},
        {"model_name": "LightGBM Classifier", "task": "High-Risk Flag", "type": "Machine Learning", **evaluate_classification_metrics(y_test_risk, lgb_risk.predict_proba(X_test_trans)[:, 1])},
        {"model_name": "Calibrated ML Classifier", "task": "High-Risk Flag", "type": "Champion ML", **evaluate_classification_metrics(y_test_risk, test_calibrated_prob)}
    ]

    # 9. Statistical Significance Testing & Verdict Card (Question a)
    print("\n--- Running Paired Cluster Bootstrap Significance Test (1,000 resamples) ---")
    verdict = compute_significance_verdict(
        y_true=y_test_cost,
        preds_ml=ml_test_cost,
        preds_baseline=b1_test_cost,
        project_ids=df_test["project_id"].values,
        task="Cost Overrun %",
        n_bootstrap=1000,
        practical_threshold_pct=5.0
    )

    # 10. Drift & Anomaly Evaluation
    print("\n--- Monitoring Distribution Drift (PSI) & Trajectory Anomalies ---")
    drift_report = evaluate_portfolio_drift(df_train, df_ongoing)
    anomaly_detector = TrajectoryAnomalyDetector().fit(df_train)
    df_ongoing_scored = anomaly_detector.score_anomalies(df_ongoing)

    # 11. Lead-Time Metric
    df_test_scored = df_test.copy()
    df_test_scored["risk_score"] = test_calibrated_prob * 100.0
    lead_time_stats = compute_lead_time_distribution(df_test_scored, threshold=50.0)

    # 12. SHAP Explanations Setup
    print("\n--- Initializing SHAP TreeExplainer ---")
    shap_suite = ExplainabilitySuite(lgb_cost, transformed_feature_names)

    # 13. Save Artifacts & Reports
    reports_dir = os.path.join(ROOT_DIR, "ml_artifacts", "reports")
    os.makedirs(reports_dir, exist_ok=True)

    df_lb = pd.DataFrame(leaderboard)
    df_lb.to_csv(os.path.join(reports_dir, "leaderboard.csv"), index=False)
    with open(os.path.join(reports_dir, "leaderboard.json"), "w", encoding="utf-8") as f:
        json.dump(leaderboard, f, indent=2)

    with open(os.path.join(reports_dir, "verdict.json"), "w", encoding="utf-8") as f:
        json.dump(verdict, f, indent=2)

    with open(os.path.join(reports_dir, "conformal.json"), "w", encoding="utf-8") as f:
        json.dump({"cost_intervals": cost_coverage, "delay_intervals": delay_coverage}, f, indent=2)

    with open(os.path.join(reports_dir, "calibration.json"), "w", encoding="utf-8") as f:
        json.dump({
            "brier_score": calibrator.brier_score,
            "ece_score": calibrator.ece_score,
            "curve": calibrator.calibration_curve_data
        }, f, indent=2)

    with open(os.path.join(reports_dir, "lead_time.json"), "w", encoding="utf-8") as f:
        json.dump(lead_time_stats, f, indent=2)

    with open(os.path.join(reports_dir, "drift.json"), "w", encoding="utf-8") as f:
        json.dump(drift_report, f, indent=2)

    with open(os.path.join(reports_dir, "survival.json"), "w", encoding="utf-8") as f:
        json.dump(survival_metrics, f, indent=2)

    # Save Model Artifacts
    artifact_mgr = ModelArtifactManager()
    db = SessionLocal()
    try:
        artifact_mgr.save_model("stacked_cost_regressor", "cost_overrun", "v1.0", stacked_cost, feature_cols, {"ensemble": "lgb+xgb+rf"}, {"test_mae": float(df_lb.loc[df_lb['model_name']=='Stacked ML Ensemble', 'mae'].iloc[0])}, is_champion=True, db=db)
        artifact_mgr.save_model("stacked_delay_regressor", "time_overrun", "v1.0", stacked_delay, feature_cols, {"ensemble": "lgb+xgb+rf"}, {"test_mae": float(df_lb.loc[(df_lb['model_name']=='Stacked ML Ensemble') & (df_lb['task']=='Delay Months'), 'mae'].iloc[0])}, is_champion=True, db=db)
        artifact_mgr.save_model("calibrated_risk_classifier", "high_risk", "v1.0", calibrator, feature_cols, {"type": "isotonic"}, {"test_auc": float(df_lb.loc[df_lb['model_name']=='Calibrated ML Classifier', 'roc_auc'].iloc[0])}, is_champion=True, db=db)

        # 14. Batch Score Ongoing Projects and Populate Database
        print("\n--- Scoring Ongoing Projects & Inserting Predictions/Explanations into Database ---")
        # Score latest snapshot for ongoing projects
        latest_ongoing = df_ongoing_scored.sort_values(["project_id", "month"]).groupby("project_id").last().reset_index()
        X_latest_trans = preprocessor.transform(latest_ongoing[feature_cols])

        cost_p10, cost_p50, cost_p90 = conformal_cost.predict(X_latest_trans)
        delay_p10, delay_p50, delay_p90 = conformal_delay.predict(X_latest_trans)
        raw_prob_ongoing = 0.55 * lgb_risk.predict_proba(X_latest_trans)[:, 1] + 0.45 * xgb_risk.predict_proba(X_latest_trans)[:, 1]
        cal_prob_ongoing = calibrator.calibrate(raw_prob_ongoing)

        # Clear existing predictions/explanations
        db.query(Explanation).delete()
        db.query(Prediction).delete()
        db.commit()

        predictions_to_add = []
        explanations_to_add = []

        print(f"Generating predictions and SHAP explanations for {len(latest_ongoing)} ongoing projects...")
        for idx, row in latest_ongoing.iterrows():
            orig_cost = float(row["original_cost_cr"])
            p_cost = float(cost_p50[idx])
            p_delay = float(delay_p50[idx])
            prob = float(cal_prob_ongoing[idx])

            risk_dict = RiskScoreCalibrator.compute_risk_metrics(prob, p_cost, orig_cost)

            pred = Prediction(
                project_id=row["project_id"],
                snapshot_month=row["month"],
                cost_overrun_p10=float(cost_p10[idx]),
                cost_overrun_p50=p_cost,
                cost_overrun_p90=float(cost_p90[idx]),
                delay_p10=float(delay_p10[idx]),
                delay_p50=p_delay,
                delay_p90=float(delay_p90[idx]),
                risk_probability=risk_dict["risk_probability"],
                risk_score=risk_dict["risk_score"],
                risk_band=risk_dict["risk_band"],
                expected_overrun_cr=risk_dict["expected_overrun_cr"],
                value_at_risk_cr=risk_dict["value_at_risk_cr"]
            )
            predictions_to_add.append(pred)

        # Batch insert predictions
        db.add_all(predictions_to_add)
        db.commit()

        # Generate top SHAP explanations for a sample of high/critical projects
        print("Extracting SHAP causal drivers for priority projects...")
        sample_indices = np.where(cal_prob_ongoing >= 0.40)[0][:300]  # Top 300 flagged projects
        for idx in sample_indices:
            pred_obj = predictions_to_add[idx]
            raw_vals = latest_ongoing.iloc[idx].to_dict()
            drivers = shap_suite.explain_instance(X_latest_trans[idx], raw_vals, top_k=6)
            for d in drivers:
                explanations_to_add.append(Explanation(
                    prediction_id=pred_obj.id,
                    feature=d["feature"],
                    feature_group=d["feature_group"],
                    shap_value=d["shap_value"],
                    direction=d["direction"],
                    rank=d["rank"]
                ))

        if explanations_to_add:
            db.bulk_save_objects(explanations_to_add)
            db.commit()

    finally:
        db.close()

    print("\n--- Training Pipeline Execution Summary ---")
    print(f"Leaderboard exported:   {os.path.join(reports_dir, 'leaderboard.csv')}")
    print(f"Verdict Status:         {verdict['verdict_status']}")
    print(f"Verdict Text:           {verdict['verdict_text']}")
    print(f"Predictions Ingested:   {len(predictions_to_add)}")
    print("Training pipeline completed successfully.")

if __name__ == "__main__":
    main()
