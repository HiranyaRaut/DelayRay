"""
DelayRay Statistical & Conventional Baselines (B0, B1, B2, B4 EVM)
Adheres strictly to docs/BUILD_SPEC.md Section 6.3.
"""

from typing import Dict, Any, Union
import numpy as np
import pandas as pd
from sklearn.linear_model import Ridge, ElasticNet, LogisticRegression
from sklearn.preprocessing import StandardScaler
from sklearn.pipeline import Pipeline
from sklearn.impute import SimpleImputer

class SectorMedianBaseline:
    """B0: Sector-median reference class forecasting."""
    def __init__(self):
        self.sector_cost_medians: Dict[str, float] = {}
        self.sector_delay_medians: Dict[str, float] = {}
        self.global_cost_median: float = 0.0
        self.global_delay_median: float = 0.0

    def fit(self, X: pd.DataFrame, y_cost: pd.Series, y_delay: pd.Series):
        df = pd.DataFrame({
            "sector": X["sector"],
            "cost_overrun": y_cost,
            "delay": y_delay
        })
        self.global_cost_median = float(y_cost.median())
        self.global_delay_median = float(y_delay.median())
        self.sector_cost_medians = df.groupby("sector")["cost_overrun"].median().to_dict()
        self.sector_delay_medians = df.groupby("sector")["delay"].median().to_dict()
        return self

    def predict_cost(self, X: pd.DataFrame) -> np.ndarray:
        return np.array([self.sector_cost_medians.get(s, self.global_cost_median) for s in X["sector"]])

    def predict_delay(self, X: pd.DataFrame) -> np.ndarray:
        return np.array([self.sector_delay_medians.get(s, self.global_delay_median) for s in X["sector"]])

class EarnedValueBaseline:
    """B4: Classical Earned Value Management (EVM) schedule and cost forecasts."""
    def predict_cost(self, X: pd.DataFrame) -> np.ndarray:
        # Cost Efficiency = physical_progress / spend_pct
        ce = X["cost_efficiency"].clip(lower=0.15, upper=2.0)
        # EAC = original_cost / CE
        # Cost overrun % = (EAC - original_cost) / original_cost * 100 = (1/CE - 1) * 100
        cost_overrun = np.maximum(0.0, (1.0 / ce - 1.0) * 100.0)
        return cost_overrun.values

    def predict_delay(self, X: pd.DataFrame) -> np.ndarray:
        # SPI = physical_progress / planned_progress
        spi = X["spi"].clip(lower=0.15, upper=2.0)
        # Forecast duration = planned_duration / SPI
        # Delay months = Forecast duration - planned_duration = planned_duration * (1/SPI - 1)
        delay_months = np.maximum(0.0, X["planned_duration_months"] * (1.0 / spi - 1.0))
        return delay_months.values

def build_linear_baseline(task: str = "regression", alpha: float = 1.0) -> Pipeline:
    """B1 / B2: Penalized linear regression or logistic regression pipeline."""
    if task == "classification":
        model = LogisticRegression(C=1.0 / max(0.001, alpha), max_iter=1000, random_state=42)
    else:
        model = Ridge(alpha=alpha, random_state=42)

    return Pipeline([
        ("imputer", SimpleImputer(strategy="median")),
        ("scaler", StandardScaler()),
        ("model", model)
    ])
