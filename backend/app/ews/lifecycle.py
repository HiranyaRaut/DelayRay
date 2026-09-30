"""
DelayRay Alert Lifecycle Management:
new -> acknowledged -> assigned -> resolved / dismissed
Handles state transitions, audit logging, de-duplication, and cooldowns.
"""

from datetime import datetime, timezone, timedelta
from typing import Optional, Dict, Any, Tuple
from sqlalchemy.orm import Session
from backend.app.db.models import Alert, AuditLog

VALID_TRANSITIONS = {
    "new": ["acknowledged", "dismissed"],
    "acknowledged": ["assigned", "resolved", "dismissed"],
    "assigned": ["resolved", "dismissed"],
    "resolved": [],
    "dismissed": []
}

def can_transition(current_status: str, new_status: str) -> bool:
    """Checks whether the requested state transition is valid."""
    return new_status in VALID_TRANSITIONS.get(current_status, [])

def transition_alert(
    alert: Alert,
    new_status: str,
    user_email: str,
    db: Session,
    resolution_note: Optional[str] = None,
    assigned_to: Optional[str] = None
) -> Tuple[bool, str]:
    """
    Executes a transition on an Alert instance, updates timestamps,
    and logs an audit event.
    """
    if not can_transition(alert.status, new_status):
        return False, f"Invalid transition from '{alert.status}' to '{new_status}'."

    old_status = alert.status
    alert.status = new_status
    now = datetime.now(timezone.utc)

    if new_status == "acknowledged":
        alert.acknowledged_by = user_email
    elif new_status == "assigned":
        if assigned_to:
            alert.assigned_to = assigned_to
    elif new_status in ("resolved", "dismissed"):
        alert.resolved_at = now
        if resolution_note:
            alert.resolution_note = resolution_note
        # 30-day cooldown window to prevent flapping
        alert.cooldown_until = now + timedelta(days=30)

    # Log to AuditLog
    audit_entry = AuditLog(
        user_email=user_email,
        action=f"ALERT_STATUS_CHANGE",
        entity_type="Alert",
        entity_id=alert.id,
        detail={
            "old_status": old_status,
            "new_status": new_status,
            "assigned_to": alert.assigned_to,
            "resolution_note": alert.resolution_note,
            "rule_id": alert.rule_id
        }
    )
    db.add(audit_entry)
    db.commit()
    db.refresh(alert)
    return True, f"Alert {alert.id} successfully moved to '{new_status}'."

def is_in_cooldown(alert: Alert) -> bool:
    """Checks if an alert is currently in a cooldown period."""
    if not alert.cooldown_until:
        return False
    now = datetime.now(timezone.utc)
    # Ensure timezone aware comparison
    cd = alert.cooldown_until
    if cd.tzinfo is None:
        cd = cd.replace(tzinfo=timezone.utc)
    return now < cd
