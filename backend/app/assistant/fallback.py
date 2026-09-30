"""
DelayRay Deterministic Fallback Assistant
Provides deterministic templated responses when Ollama service is unreachable.
"""

from typing import Dict, Any

FALLBACK_TEMPLATES = {
    "top_risk": "Based on current portfolio scoring, the top risk projects are identified via Value-at-Risk criteria in the Command Center.",
    "model_status": "The champion model is a calibrated LightGBM ensemble evaluated on test projects starting 2019 and later.",
    "general": "Local LLM service is offline. Showing deterministic summary data from local database views."
}

def get_deterministic_response(intent: str, data: Dict[str, Any]) -> str:
    return FALLBACK_TEMPLATES.get(intent, FALLBACK_TEMPLATES["general"])
