"""
DelayRay Split Conformal Prediction Intervals Engine (P10, P50, P90)
Quantile Gradient Boosting with split conformal calibration for coverage guarantees.
Adheres strictly to docs/BUILD_SPEC.md Section 6.3.
"""

from typing import Dict, Any, Tuple
import numpy as np
import lightgbm as lgb

class ConformalIntervalPredictor:
    """Provides calibrated P10, P50, P90 prediction intervals with formal coverage."""
    def __init__(self, alpha: float = 0.20):  # 80% nominal coverage
        self.alpha = alpha
        self.q10_model = lgb.LGBMRegressor(objective="quantile", alpha=0.10, n_estimators=120, random_state=42, verbose=-1, n_jobs=-1)
        self.q50_model = lgb.LGBMRegressor(objective="quantile", alpha=0.50, n_estimators=120, random_state=42, verbose=-1, n_jobs=-1)
        self.q90_model = lgb.LGBMRegressor(objective="quantile", alpha=0.90, n_estimators=120, random_state=42, verbose=-1, n_jobs=-1)
        self.conformal_q: float = 0.0

    def fit(self, X_train: np.ndarray, y_train: np.ndarray, X_val: np.ndarray, y_val: np.ndarray):
        # 1. Fit quantile models on train
        self.q10_model.fit(X_train, y_train)
        self.q50_model.fit(X_train, y_train)
        self.q90_model.fit(X_train, y_train)

        # 2. Compute non-conformity scores on validation set
        val_p10 = self.q10_model.predict(X_val)
        val_p90 = self.q90_model.predict(X_val)
        
        # Non-conformity score: distance outside [p10, p90]
        residuals = np.maximum(y_val - val_p90, val_p10 - y_val)
        
        # Conformal correction quantile
        n = len(y_val)
        level = min(1.0, np.ceil((n + 1) * (1.0 - self.alpha)) / n)
        self.conformal_q = float(np.quantile(residuals, level))
        return self

    def predict(self, X: np.ndarray) -> Tuple[np.ndarray, np.ndarray, np.ndarray]:
        """Returns calibrated (p10, p50, p90) intervals."""
        p10 = np.maximum(0.0, self.q10_model.predict(X) - self.conformal_q)
        p50 = np.maximum(0.0, self.q50_model.predict(X))
        p90 = np.maximum(p50, self.q90_model.predict(X) + self.conformal_q)
        return p10, p50, p90

    def evaluate_coverage(self, X_test: np.ndarray, y_test: np.ndarray) -> Dict[str, float]:
        """Calculates empirical coverage and mean interval width on test set."""
        p10, p50, p90 = self.predict(X_test)
        covered = (y_test >= p10) & (y_test <= p90)
        empirical_coverage = round(float(np.mean(covered) * 100.0), 2)
        mean_width = round(float(np.mean(p90 - p10)), 2)

        return {
            "nominal_coverage_pct": (1.0 - self.alpha) * 100.0,
            "empirical_coverage_pct": empirical_coverage,
            "mean_interval_width": mean_width,
            "conformal_adjustment": round(self.conformal_q, 2)
        }
