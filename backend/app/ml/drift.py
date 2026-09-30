"""
DelayRay Population Stability Index (PSI) & Concept Drift Engine
Monitors feature distribution shifts and rolling prediction error.
Adheres strictly to docs/BUILD_SPEC.md Section 6.7.
"""

from typing import Dict, Any, List
import numpy as np
import pandas as pd

def calculate_psi(
    expected: np.ndarray,
    actual: np.ndarray,
    num_buckets: int = 10
) -> float:
    """
    Computes Population Stability Index (PSI) between baseline and monitored batch.
    PSI = sum((Actual% - Expected%) * ln(Actual% / Expected%))
    """
    expected = expected[~np.isnan(expected)]
    actual = actual[~np.isnan(actual)]
    if len(expected) < 20 or len(actual) < 20:
        return 0.0

    # Quantile bins based on expected
    percentiles = np.linspace(0, 100, num_buckets + 1)
    bins = np.percentile(expected, percentiles)
    bins[0] = -np.inf
    bins[-1] = np.inf
    # Ensure strictly increasing bins
    bins = np.unique(bins)
    if len(bins) < 3:
        return 0.0

    exp_counts, _ = np.histogram(expected, bins=bins)
    act_counts, _ = np.histogram(actual, bins=bins)

    exp_pct = exp_counts / max(1, len(expected))
    act_pct = act_counts / max(1, len(actual))

    # Add small epsilon to avoid div by zero
    eps = 1e-4
    exp_pct = np.clip(exp_pct, eps, 1.0)
    act_pct = np.clip(act_pct, eps, 1.0)

    psi_val = np.sum((act_pct - exp_pct) * np.log(act_pct / exp_pct))
    return round(float(psi_val), 4)

def evaluate_portfolio_drift(
    df_train: pd.DataFrame,
    df_ongoing: pd.DataFrame,
    key_features: List[str] = None
) -> Dict[str, Any]:
    """
    Calculates monthly PSI across portfolio snapshots.
    """
    if key_features is None:
        key_features = ["spi", "cost_efficiency", "spend_pct", "steel_price_index", "rainfall_anomaly_pct"]

    reports = []
    retrain_recommended = False

    months = sorted(df_ongoing["month"].unique())
    for m in months[-12:]:  # Last 12 months
        m_slice = df_ongoing[df_ongoing["month"] == m]
        month_psis = {}
        for feat in key_features:
            if feat in df_train.columns and feat in m_slice.columns:
                psi = calculate_psi(df_train[feat].values, m_slice[feat].values)
                month_psis[feat] = psi
                if psi >= 0.25:
                    retrain_recommended = True

        avg_psi = round(float(np.mean(list(month_psis.values()))), 3) if month_psis else 0.0
        status = "action_required" if avg_psi >= 0.25 else ("warning" if avg_psi >= 0.10 else "stable")
        
        reports.append({
            "month": m,
            "avg_psi": avg_psi,
            "status": status,
            "feature_psis": month_psis
        })

    return {
        "retrain_recommended": retrain_recommended,
        "monthly_drift_reports": reports
    }
