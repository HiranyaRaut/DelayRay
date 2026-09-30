"""
DelayRay Probability Calibration & Risk Scoring Engine
Calibrates binary classification probabilities via Isotonic Regression,
computes Brier score and ECE, and derives 0-100 Risk Scores and Value at Risk.
Adheres strictly to docs/BUILD_SPEC.md Section 6.3.
"""

from typing import Dict, Any, Tuple
import numpy as np
import pandas as pd
from sklearn.isotonic import IsotonicRegression
from sklearn.metrics import brier_score_loss
from sklearn.calibration import calibration_curve

class RiskScoreCalibrator:
    """Isotonic probability calibrator mapping raw model outputs to calibrated 0-100 scores."""
    def __init__(self):
        self.calibrator = IsotonicRegression(out_of_bounds="clip")
        self.brier_score: float = 0.0
        self.ece_score: float = 0.0
        self.calibration_curve_data: Dict[str, list] = {}

    def fit(self, y_true_val: np.ndarray, y_raw_prob_val: np.ndarray):
        self.calibrator.fit(y_raw_prob_val, y_true_val)
        y_cal_val = self.calibrator.predict(y_raw_prob_val)
        self.brier_score = round(float(brier_score_loss(y_true_val, y_cal_val)), 4)
        
        # Compute ECE across 10 bins
        prob_true, prob_pred = calibration_curve(y_true_val, y_cal_val, n_bins=10, strategy="uniform")
        self.ece_score = round(float(np.mean(np.abs(prob_true - prob_pred))), 4)
        self.calibration_curve_data = {
            "fraction_of_positives": [round(float(x), 4) for x in prob_true],
            "mean_predicted_value": [round(float(x), 4) for x in prob_pred]
        }
        return self

    def calibrate(self, y_raw_prob: np.ndarray) -> np.ndarray:
        return np.clip(self.calibrator.predict(y_raw_prob), 0.001, 0.999)

    @staticmethod
    def assign_risk_band(score: float) -> str:
        """Assigns risk category: Low (< 25), Moderate (25-50), High (50-75), Critical (>= 75)."""
        if score >= 75.0:
            return "Critical"
        elif score >= 50.0:
            return "High"
        elif score >= 25.0:
            return "Moderate"
        else:
            return "Low"

    @classmethod
    def compute_risk_metrics(
        cls,
        calibrated_prob: float,
        predicted_cost_overrun_pct: float,
        original_cost_cr: float
    ) -> Dict[str, Any]:
        """
        Computes 0-100 risk score, risk band, Expected Overrun (₹ Cr), and Value at Risk (₹ Cr).
        """
        risk_score = round(float(calibrated_prob * 100.0), 1)
        risk_band = cls.assign_risk_band(risk_score)
        
        expected_overrun_cr = round(float((max(0.0, predicted_cost_overrun_pct) / 100.0) * original_cost_cr), 2)
        value_at_risk_cr = round(float(calibrated_prob * expected_overrun_cr), 2)

        return {
            "risk_score": risk_score,
            "risk_band": risk_band,
            "risk_probability": round(float(calibrated_prob), 4),
            "expected_overrun_cr": expected_overrun_cr,
            "value_at_risk_cr": value_at_risk_cr
        }
