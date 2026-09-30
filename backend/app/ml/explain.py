"""
DelayRay SHAP Explainability Engine
Generates top-8 causal drivers per prediction and natural-language explanations.
Adheres strictly to docs/BUILD_SPEC.md Section 6.6.
"""

from typing import Dict, Any, List
import numpy as np
import pandas as pd
import shap
from backend.app.ml.features import (
    G1_FEATURES, G2_FEATURES, G3_FEATURES, G4_FEATURES, G5_FEATURES, G6_FEATURES
)

def map_feature_to_group(feature_name: str) -> str:
    if feature_name in G1_FEATURES:
        return "G1 (CUF Static)"
    elif feature_name in G2_FEATURES:
        return "G2 (CUF Progress)"
    elif feature_name in G3_FEATURES:
        return "G3 (Derived EV)"
    elif feature_name in G4_FEATURES:
        return "G4 (Remarks NLP)"
    elif feature_name in G5_FEATURES:
        return "G5 (External Macro)"
    elif feature_name in G6_FEATURES:
        return "G6 (Project Extras)"
    return "Other"

def generate_driver_sentence(feature: str, val: Any, shap_val: float) -> str:
    """Generates natural language explanation from templates with empirical values."""
    direction = "increased" if shap_val > 0 else "reduced"
    impact = abs(shap_val)

    if isinstance(val, (int, float, np.number)):
        if feature == "spi":
            return f"Schedule Performance Index (SPI) of {val:.2f} {direction} risk score by {impact:.1f} points."
        elif feature == "cost_efficiency":
            return f"Cost efficiency factor of {val:.2f} {direction} risk score by {impact:.1f} points."
        elif feature == "land_acquisition_pct_at_start":
            return f"Land handover of {val:.1f}% at sanction {direction} risk score by {impact:.1f} points."
        elif feature == "contractor_concurrent_projects":
            return f"Contractor concurrent load of {int(val)} active packages {direction} delivery risk by {impact:.1f} points."
        elif feature == "env_forest_clearance_delay_months":
            return f"Statutory clearance delay of {val:.1f} months {direction} timeline risk by {impact:.1f} points."
        elif feature == "progress_gap":
            return f"Physical progress deficit of {val:.1f}% behind S-curve target {direction} risk by {impact:.1f} points."
        elif feature == "design_changes_count":
            return f"{int(val)} approved major design variations {direction} cost overrun risk by {impact:.1f} points."
        else:
            clean_name = feature.replace("_", " ").title()
            return f"{clean_name} ({val:.2f}) {direction} prediction by {impact:.1f} points."
    else:
        clean_name = feature.replace("_", " ").title()
        return f"{clean_name} '{val}' {direction} prediction by {impact:.1f} points."

class ExplainabilitySuite:
    """SHAP Explainer for tree models."""
    def __init__(self, model, feature_names: List[str]):
        self.model = model
        self.feature_names = feature_names
        self.explainer = shap.TreeExplainer(model)

    def explain_instance(
        self,
        X_row: np.ndarray,
        raw_feature_values: Dict[str, Any],
        top_k: int = 8
    ) -> List[Dict[str, Any]]:
        """
        Extracts top-8 drivers for an individual prediction.
        """
        shap_values = self.explainer.shap_values(X_row.reshape(1, -1))
        if isinstance(shap_values, list):  # Classification multi-class/binary
            shap_vec = shap_values[1][0] if len(shap_values) > 1 else shap_values[0][0]
        elif len(shap_values.shape) > 1:
            shap_vec = shap_values[0]
        else:
            shap_vec = shap_values

        driver_indices = np.argsort(np.abs(shap_vec))[::-1][:top_k]

        explanations = []
        for rank, idx in enumerate(driver_indices, start=1):
            fname = self.feature_names[idx] if idx < len(self.feature_names) else f"feature_{idx}"
            s_val = float(shap_vec[idx])
            raw_val = raw_feature_values.get(fname, X_row[idx])
            
            explanations.append({
                "feature": fname,
                "feature_group": map_feature_to_group(fname),
                "shap_value": round(s_val, 3),
                "raw_value": str(raw_val) if not isinstance(raw_val, (int, float, np.number)) else round(float(raw_val), 2),
                "direction": "increases_risk" if s_val > 0 else "decreases_risk",
                "rank": rank,
                "narrative": generate_driver_sentence(fname, raw_val, s_val)
            })

        return explanations
