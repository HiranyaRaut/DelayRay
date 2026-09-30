"""
DelayRay Alert Lifecycle Management:
new -> acknowledged -> assigned -> resolved / dismissed
"""

from typing import Optional, Dict, Any

VALID_TRANSITIONS = {
    "new": ["acknowledged", "dismissed"],
    "acknowledged": ["assigned", "resolved", "dismissed"],
    "assigned": ["resolved", "dismissed"],
    "resolved": [],
    "dismissed": []
}

def transition_alert(current_status: str, new_status: str) -> bool:
    return new_status in VALID_TRANSITIONS.get(current_status, [])
