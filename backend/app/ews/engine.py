"""
DelayRay Early Warning Rule Evaluation Engine
"""

from typing import Dict, Any, List

class EWSEngine:
    """Evaluates project snapshots against rules R1-R8."""
    def __init__(self, rules_config_path: str = "backend/app/ews/rules.yaml"):
        self.rules_config_path = rules_config_path

    def evaluate_project(self, project_data: Dict[str, Any]) -> List[Dict[str, Any]]:
        return []
