"""
DelayRay Trajectory Anomaly Detection Engine
Uses IsolationForest on dynamic execution features (SPI, Cost Efficiency, Velocity)
to detect anomalous projects (top 2%) for early-warning flagging (Rule R7).
Adheres strictly to docs/BUILD_SPEC.md Section 6.7.
"""

from typing import Dict, Any, List
import numpy as np
import pandas as pd
from sklearn.ensemble import IsolationForest
from sklearn.preprocessing import StandardScaler
from sklearn.impute import SimpleImputer
from sklearn.pipeline import Pipeline

ANOMALY_FEATURES = [
    "spi", "cost_efficiency", "progress_velocity_3m", "spend_gap", "progress_gap"
]

class TrajectoryAnomalyDetector:
    """Isolation Forest anomaly detector for project execution trajectories."""
    def __init__(self, contamination: float = 0.02):
        self.contamination = contamination
        self.pipeline = Pipeline([
            ("imputer", SimpleImputer(strategy="median")),
            ("scaler", StandardScaler()),
            ("model", IsolationForest(contamination=contamination, random_state=42, n_jobs=-1))
        ])

    def fit(self, df_train: pd.DataFrame):
        X = df_train[ANOMALY_FEATURES]
        self.pipeline.fit(X)
        return self

    def score_anomalies(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Returns anomaly scores (0-100, higher = more anomalous) and boolean is_anomaly flag.
        """
        df = df.copy()
        X = df[ANOMALY_FEATURES]
        
        # Decision function: lower values mean more anomalous
        raw_scores = self.pipeline.named_steps["model"].decision_function(
            self.pipeline.named_steps["scaler"].transform(
                self.pipeline.named_steps["imputer"].transform(X)
            )
        )
        
        # Map decision function to 0-100 anomaly percentile
        norm_scores = 100.0 * (1.0 - (raw_scores - raw_scores.min()) / max(1e-4, (raw_scores.max() - raw_scores.min())))
        preds = self.pipeline.named_steps["model"].predict(
            self.pipeline.named_steps["scaler"].transform(
                self.pipeline.named_steps["imputer"].transform(X)
            )
        )
        
        df["anomaly_score"] = np.round(norm_scores, 1)
        df["is_anomaly"] = (preds == -1)
        return df
