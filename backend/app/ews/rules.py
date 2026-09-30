"""
DelayRay Early Warning Rule Definitions (R1 - R8)
"""

from typing import Dict, Any, List

def evaluate_rule_r1(spi_history: List[float]) -> bool:
    """R1: SPI < 0.85 for 3 consecutive months."""
    if len(spi_history) < 3:
        return False
    return all(s < 0.85 for s in spi_history[-3:])

def evaluate_rule_r2(spend_pct: float, physical_pct: float) -> bool:
    """R2: Spend % - Physical % > 10 points."""
    return (spend_pct - physical_pct) > 10.0
