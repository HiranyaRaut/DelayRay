"""
DelayRay Machine Learning Models Suite
Implements LightGBM, XGBoost, Random Forest, and Stacked Ensembles
with domain monotonic constraints.
Adheres strictly to docs/BUILD_SPEC.md Section 6.3.
"""

from typing import Dict, Any, List, Tuple
import numpy as np
import pandas as pd
from sklearn.base import BaseEstimator, RegressorMixin, ClassifierMixin
from sklearn.ensemble import RandomForestRegressor, RandomForestClassifier, ExtraTreesRegressor
from sklearn.preprocessing import OrdinalEncoder, StandardScaler
from sklearn.compose import ColumnTransformer
from sklearn.pipeline import Pipeline
from sklearn.impute import SimpleImputer
import lightgbm as lgb
import xgboost as xgb

CATEGORICAL_COLS = [
    "sector", "ministry", "primary_state", "agency_type", "funding_mode",
    "terrain_class", "env_forest_clearance_status", "utility_shifting_complexity"
]

def build_preprocessor(feature_cols: List[str]) -> Tuple[ColumnTransformer, List[str]]:
    """
    Builds a leak-free ColumnTransformer handling numeric imputation/scaling
    and categorical ordinal encoding.
    """
    cat_cols = [c for c in feature_cols if c in CATEGORICAL_COLS]
    num_cols = [c for c in feature_cols if c not in cat_cols]

    numeric_transformer = Pipeline([
        ("imputer", SimpleImputer(strategy="median", add_indicator=True)),
        ("scaler", StandardScaler())
    ])

    categorical_transformer = Pipeline([
        ("imputer", SimpleImputer(strategy="most_frequent")),
        ("encoder", OrdinalEncoder(handle_unknown="use_encoded_value", unknown_value=-1))
    ])

    preprocessor = ColumnTransformer(
        transformers=[
            ("num", numeric_transformer, num_cols),
            ("cat", categorical_transformer, cat_cols)
        ],
        remainder="drop"
    )
    return preprocessor, num_cols + cat_cols

def build_lgb_regressor(params: Dict[str, Any] = None, feature_names: List[str] = None) -> lgb.LGBMRegressor:
    """Builds LightGBM Regressor with domain monotonic constraints where applicable."""
    default_params = {
        "n_estimators": 180,
        "learning_rate": 0.04,
        "num_leaves": 31,
        "max_depth": 6,
        "subsample": 0.85,
        "colsample_bytree": 0.85,
        "random_state": 42,
        "verbose": -1,
        "n_jobs": -1
    }
    if params:
        default_params.update(params)

    # Monotonic constraint: higher SPI (-1) or higher physical progress (-1) decreases delay/cost
    if feature_names and "monotone_constraints" not in default_params:
        constraints = []
        for f in feature_names:
            if f in ("spi", "physical_progress_pct", "cost_efficiency", "land_acquisition_pct_at_start"):
                constraints.append(-1)
            elif f in ("clearance_delay_months", "utility_shifting_count", "design_changes_count"):
                constraints.append(1)
            else:
                constraints.append(0)
        default_params["monotone_constraints"] = constraints

    return lgb.LGBMRegressor(**default_params)

def build_xgb_regressor(params: Dict[str, Any] = None) -> xgb.XGBRegressor:
    """Builds XGBoost Regressor."""
    default_params = {
        "n_estimators": 160,
        "learning_rate": 0.05,
        "max_depth": 5,
        "subsample": 0.85,
        "colsample_bytree": 0.85,
        "random_state": 42,
        "n_jobs": -1
    }
    if params:
        default_params.update(params)
    return xgb.XGBRegressor(**default_params)

def build_rf_regressor(n_estimators: int = 150) -> RandomForestRegressor:
    """Builds Random Forest Regressor."""
    return RandomForestRegressor(
        n_estimators=n_estimators,
        max_depth=12,
        min_samples_split=6,
        random_state=42,
        n_jobs=-1
    )

def build_lgb_classifier(params: Dict[str, Any] = None) -> lgb.LGBMClassifier:
    """Builds LightGBM Classifier for high-risk classification (Task T3)."""
    default_params = {
        "n_estimators": 180,
        "learning_rate": 0.04,
        "num_leaves": 31,
        "max_depth": 6,
        "subsample": 0.85,
        "colsample_bytree": 0.85,
        "random_state": 42,
        "verbose": -1,
        "n_jobs": -1
    }
    if params:
        default_params.update(params)
    return lgb.LGBMClassifier(**default_params)

def build_xgb_classifier(params: Dict[str, Any] = None) -> xgb.XGBClassifier:
    """Builds XGBoost Classifier for high-risk classification (Task T3)."""
    default_params = {
        "n_estimators": 160,
        "learning_rate": 0.05,
        "max_depth": 5,
        "subsample": 0.85,
        "colsample_bytree": 0.85,
        "random_state": 42,
        "n_jobs": -1
    }
    if params:
        default_params.update(params)
    return xgb.XGBClassifier(**default_params)

class StackedEnsembleRegressor(BaseEstimator, RegressorMixin):
    """Stacked ensemble averaging LightGBM, XGBoost, and Random Forest."""
    def __init__(self, lgb_model, xgb_model, rf_model):
        self.lgb_model = lgb_model
        self.xgb_model = xgb_model
        self.rf_model = rf_model

    def fit(self, X, y, sample_weight=None):
        self.lgb_model.fit(X, y, sample_weight=sample_weight)
        self.xgb_model.fit(X, y, sample_weight=sample_weight)
        self.rf_model.fit(X, y, sample_weight=sample_weight)
        return self

    def predict(self, X) -> np.ndarray:
        p_lgb = self.lgb_model.predict(X)
        p_xgb = self.xgb_model.predict(X)
        p_rf = self.rf_model.predict(X)
        return 0.45 * p_lgb + 0.35 * p_xgb + 0.20 * p_rf
