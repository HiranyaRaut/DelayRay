"""
DelayRay Core Services
"""

from typing import Dict, Any

class PortfolioService:
    @staticmethod
    def get_summary_stub() -> Dict[str, Any]:
        return {
            "projects_tracked": 1981,
            "portfolio_cost_cr": 2685000.0,
            "cumulative_expenditure_cr": 1142000.0,
            "predicted_overrun_cr": 482000.0,
            "value_at_risk_cr": 312000.0,
            "high_critical_count": 487,
            "open_alerts": 142
        }
