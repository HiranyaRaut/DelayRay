"""
DelayRay Early Warning Rule Definitions (R1 - R8)
Adheres strictly to docs/BUILD_SPEC.md Section 7.
"""

from typing import Dict, Any, List, Optional
import numpy as np

def evaluate_r1_schedule_slippage(
    spi_history: List[float],
    threshold: float = 0.85,
    consecutive_months: int = 3
) -> Dict[str, Any]:
    """
    R1 Schedule slippage: SPI < threshold for consecutive_months.
    """
    if len(spi_history) < consecutive_months:
        return {"triggered": False}
    recent = spi_history[-consecutive_months:]
    triggered = all(s is not None and s < threshold for s in recent)
    return {
        "triggered": triggered,
        "detail": {
            "spi_history": recent,
            "threshold": threshold,
            "consecutive_months": consecutive_months
        }
    }

def evaluate_r2_spend_divergence(
    expenditure_pct: float,
    physical_progress_pct: float,
    divergence_threshold: float = 10.0
) -> Dict[str, Any]:
    """
    R2 Spend-progress divergence: expenditure % - physical % > threshold.
    """
    diff = expenditure_pct - physical_progress_pct
    triggered = diff > divergence_threshold
    return {
        "triggered": triggered,
        "detail": {
            "expenditure_pct": round(expenditure_pct, 2),
            "physical_progress_pct": round(physical_progress_pct, 2),
            "divergence_pct": round(diff, 2),
            "threshold": divergence_threshold
        }
    }

def evaluate_r3_high_model_risk(
    current_risk_score: float,
    previous_risk_score: Optional[float],
    score_threshold: float = 75.0,
    monthly_delta_threshold: float = 15.0
) -> Dict[str, Any]:
    """
    R3 High model risk: risk score >= 75 or rise >= 15 points in one month.
    """
    is_absolute_high = current_risk_score >= score_threshold
    delta = (current_risk_score - previous_risk_score) if previous_risk_score is not None else 0.0
    is_spike = delta >= monthly_delta_threshold
    triggered = is_absolute_high or is_spike
    return {
        "triggered": triggered,
        "detail": {
            "risk_score": round(current_risk_score, 1),
            "previous_risk_score": round(previous_risk_score, 1) if previous_risk_score is not None else None,
            "monthly_delta": round(delta, 1),
            "reason": "absolute_high" if is_absolute_high else ("spike" if is_spike else "none")
        }
    }

def evaluate_r4_forecast_slip(
    predicted_delay_months: float,
    delay_threshold_months: float = 6.0
) -> Dict[str, Any]:
    """
    R4 Forecast slip: predicted completion > 6 months beyond approved date.
    """
    triggered = predicted_delay_months > delay_threshold_months
    return {
        "triggered": triggered,
        "detail": {
            "predicted_delay_months": round(predicted_delay_months, 1),
            "threshold_months": delay_threshold_months
        }
    }

def evaluate_r5_stalled_progress(
    progress_history: List[float],
    consecutive_stall_months: int = 3,
    epsilon: float = 0.01
) -> Dict[str, Any]:
    """
    R5 Stalled progress: no physical progress change for consecutive_stall_months while time elapses.
    """
    if len(progress_history) < consecutive_stall_months:
        return {"triggered": False}
    recent = progress_history[-consecutive_stall_months:]
    # Check if delta between max and min in recent months is under epsilon
    stall = (max(recent) - min(recent)) <= epsilon and recent[-1] < 98.0
    return {
        "triggered": stall,
        "detail": {
            "progress_history": [round(p, 2) for p in recent],
            "stall_months": consecutive_stall_months
        }
    }

def evaluate_r6_milestone_misses(
    milestone_statuses: List[str],
    consecutive_misses: int = 2
) -> Dict[str, Any]:
    """
    R6 Milestone misses: consecutive missed milestones.
    """
    miss_count = 0
    for st in reversed(milestone_statuses):
        if st == "missed":
            miss_count += 1
            if miss_count >= consecutive_misses:
                break
        elif st == "achieved":
            break
    triggered = miss_count >= consecutive_misses
    return {
        "triggered": triggered,
        "detail": {
            "consecutive_missed": miss_count,
            "threshold": consecutive_misses
        }
    }

def evaluate_r7_anomaly(
    anomaly_score: float,
    threshold_percentile: float = 0.02
) -> Dict[str, Any]:
    """
    R7 Anomaly: isolation forest trajectory anomaly score in top 2%.
    """
    # Lower isolation forest score indicates higher anomalous behavior
    triggered = anomaly_score < -0.15  # Scaled threshold matching top 2%
    return {
        "triggered": triggered,
        "detail": {
            "anomaly_score": round(anomaly_score, 3),
            "is_outlier": triggered
        }
    }

def evaluate_r8_critical_challenge(
    remark_tags: List[str],
    confidence: float,
    critical_tags: Optional[List[str]] = None,
    confidence_threshold: float = 0.75
) -> Dict[str, Any]:
    """
    R8 Critical challenge: remark tags include land, clearance, or funds with high confidence.
    """
    if critical_tags is None:
        critical_tags = ["land", "clearance", "funds"]
    matched = [t for t in remark_tags if any(c in t.lower() for c in critical_tags)]
    triggered = bool(matched) and (confidence >= confidence_threshold)
    return {
        "triggered": triggered,
        "detail": {
            "matched_tags": matched,
            "confidence": round(confidence, 2),
            "confidence_threshold": confidence_threshold
        }
    }
