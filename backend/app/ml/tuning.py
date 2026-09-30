"""
DelayRay Optuna Hyperparameter Optimization Engine
Adheres strictly to docs/BUILD_SPEC.md Section 6.3.
"""

from typing import Dict, Any, List
import optuna
import numpy as np
import pandas as pd
from sklearn.metrics import mean_absolute_error, roc_auc_score
from sklearn.model_selection import GroupKFold
import lightgbm as lgb

# Disable noisy Optuna logging during production runs
optuna.logging.set_verbosity(optuna.logging.WARNING)

def tune_lgb_regressor(
    X_train: pd.DataFrame,
    y_train: pd.Series,
    groups: pd.Series,
    n_trials: int = 40
) -> Dict[str, Any]:
    """
    Tunes LightGBM regressor using GroupKFold to preserve project integrity.
    """
    def objective(trial):
        params = {
            "n_estimators": trial.suggest_int("n_estimators", 80, 250),
            "learning_rate": trial.suggest_float("learning_rate", 0.01, 0.12, log=True),
            "num_leaves": trial.suggest_int("num_leaves", 15, 63),
            "max_depth": trial.suggest_int("max_depth", 4, 8),
            "subsample": trial.suggest_float("subsample", 0.65, 0.95),
            "colsample_bytree": trial.suggest_float("colsample_bytree", 0.65, 0.95),
            "min_child_samples": trial.suggest_int("min_child_samples", 10, 40),
            "random_state": 42,
            "verbose": -1,
            "n_jobs": -1
        }
        
        gkf = GroupKFold(n_splits=3)
        scores = []
        for tr_idx, val_idx in gkf.split(X_train, y_train, groups=groups):
            X_tr, y_tr = X_train.iloc[tr_idx], y_train.iloc[tr_idx]
            X_va, y_val = X_train.iloc[val_idx], y_train.iloc[val_idx]
            
            model = lgb.LGBMRegressor(**params)
            model.fit(X_tr, y_tr)
            preds = model.predict(X_va)
            scores.append(mean_absolute_error(y_val, preds))
            
        return float(np.mean(scores))

    study = optuna.create_study(direction="minimize")
    study.optimize(objective, n_trials=n_trials)
    return study.best_params
