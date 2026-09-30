"""
DelayRay / PAIMANA Starter Pipeline Reference
Demonstrates data structures, earned-value feature derivations, and baseline comparisons.
"""

from typing import Dict, Any, List
import numpy as np
import pandas as pd

def compute_earned_value_metrics(row: Dict[str, Any]) -> Dict[str, float]:
    """
    Computes SPI, Cost Efficiency, and Schedule/Cost gaps strictly as-of snapshot.
    """
    planned_progress = max(0.001, float(row.get("planned_progress_pct", 1.0)))
    physical_progress = float(row.get("physical_progress_pct", 0.0))
    cumulative_exp = float(row.get("cumulative_expenditure_cr", 0.0))
    original_cost = max(1.0, float(row.get("original_cost_cr", 1.0)))
    
    spend_pct = (cumulative_exp / original_cost) * 100.0
    
    # SPI = Earned Value / Planned Value = Physical Progress / Planned Progress
    spi = physical_progress / planned_progress
    
    # Cost Efficiency (CPI proxy) = Physical % / Spend %
    cost_efficiency = physical_progress / max(0.001, spend_pct)
    
    progress_gap = planned_progress - physical_progress
    spend_gap = spend_pct - physical_progress
    
    return {
        "spi": round(spi, 4),
        "cost_efficiency": round(cost_efficiency, 4),
        "progress_gap": round(progress_gap, 2),
        "spend_gap": round(spend_gap, 2),
    }

def earned_value_forecast(
    original_cost_cr: float,
    planned_duration_months: float,
    spi: float,
    cost_efficiency: float
) -> Dict[str, float]:
    """
    Standard EVM baseline forecast:
    - Estimate at Completion (EAC) = Budget / Cost Efficiency
    - Forecast Duration = Planned Duration / SPI
    """
    clipped_spi = max(0.2, min(spi, 2.0))
    clipped_ce = max(0.2, min(cost_efficiency, 2.0))
    
    eac_cr = original_cost_cr / clipped_ce
    cost_overrun_pct = max(0.0, ((eac_cr - original_cost_cr) / original_cost_cr) * 100.0)
    
    forecast_duration_months = planned_duration_months / clipped_spi
    time_overrun_months = max(0.0, forecast_duration_months - planned_duration_months)
    
    return {
        "eac_cr": round(eac_cr, 2),
        "cost_overrun_pct": round(cost_overrun_pct, 2),
        "time_overrun_months": round(time_overrun_months, 1)
    }

if __name__ == "__main__":
    sample_snapshot = {
        "original_cost_cr": 1250.0,
        "planned_duration_months": 36.0,
        "planned_progress_pct": 65.0,
        "physical_progress_pct": 48.0,
        "cumulative_expenditure_cr": 720.0
    }
    
    ev_metrics = compute_earned_value_metrics(sample_snapshot)
    print("Earned Value Metrics:", ev_metrics)
    
    forecast = earned_value_forecast(
        sample_snapshot["original_cost_cr"],
        sample_snapshot["planned_duration_months"],
        ev_metrics["spi"],
        ev_metrics["cost_efficiency"]
    )
    print("Baseline EVM Forecast:", forecast)
