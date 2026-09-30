"""
DelayRay Early Warning System (Alerts) Routes
Alert management feed, lifecycle transitions, and editable rule definitions.
Adheres strictly to docs/BUILD_SPEC.md Sections 7 and 9.
"""

from typing import List, Optional, Dict, Any
from fastapi import APIRouter, Depends, Query, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import desc, func

from backend.app.deps import get_db, get_current_user, require_analyst, require_admin
from backend.app.db.models import Alert, AlertRule, Project, User
from backend.app.core.schemas import (
    AlertResponse, PaginatedAlertsResponse, AlertUpdate,
    AlertRuleResponse, AlertRuleUpdate
)
from backend.app.ews.lifecycle import transition_alert

router = APIRouter()

@router.get("", response_model=PaginatedAlertsResponse, tags=["Alerts"])
def list_alerts(
    status_filter: Optional[str] = Query(None, alias="status"),
    severity: Optional[str] = None,
    rule_id: Optional[str] = None,
    project_id: Optional[str] = None,
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db)
):
    """
    Returns filtered and paginated early warning alerts feed.
    """
    query = (
        db.query(Alert, Project.project_name, Project.sector, Project.ministry)
        .outerjoin(Project, Project.project_id == Alert.project_id)
    )

    if status_filter:
        query = query.filter(Alert.status == status_filter)
    if severity:
        query = query.filter(Alert.severity == severity)
    if rule_id:
        query = query.filter(Alert.rule_id == rule_id)
    if project_id:
        query = query.filter(Alert.project_id == project_id)

    query = query.order_by(desc(Alert.created_at))

    total = query.count()
    total_pages = (total + page_size - 1) // page_size
    records = query.offset((page - 1) * page_size).limit(page_size).all()

    items = []
    for alert, p_name, p_sector, p_ministry in records:
        items.append(AlertResponse(
            id=alert.id,
            project_id=alert.project_id,
            project_name=p_name,
            sector=p_sector,
            ministry=p_ministry,
            rule_id=alert.rule_id,
            severity=alert.severity,
            title=alert.title,
            detail=alert.detail,
            status=alert.status,
            created_at=alert.created_at,
            acknowledged_by=alert.acknowledged_by,
            assigned_to=alert.assigned_to,
            resolved_at=alert.resolved_at,
            resolution_note=alert.resolution_note,
            cooldown_until=alert.cooldown_until
        ))

    # Aggregated counts
    sev_counts = dict(db.query(Alert.severity, func.count(Alert.id)).group_by(Alert.severity).all())
    stat_counts = dict(db.query(Alert.status, func.count(Alert.id)).group_by(Alert.status).all())

    return PaginatedAlertsResponse(
        items=items,
        total=total,
        page=page,
        page_size=page_size,
        total_pages=total_pages,
        counts_by_severity=sev_counts,
        counts_by_status=stat_counts
    )

@router.patch("/{alert_id}", response_model=AlertResponse, tags=["Alerts"])
def update_alert_status(
    alert_id: str,
    update: AlertUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_analyst)
):
    """
    Updates alert status along the lifecycle: new -> acknowledged -> assigned -> resolved / dismissed.
    Requires 'analyst' or 'admin' role.
    """
    alert = db.query(Alert).filter(Alert.id == alert_id).first()
    if not alert:
        raise HTTPException(status_code=404, detail=f"Alert '{alert_id}' not found")

    if update.status:
        success, msg = transition_alert(
            alert=alert,
            new_status=update.status,
            user_email=current_user.email,
            db=db,
            resolution_note=update.resolution_note,
            assigned_to=update.assigned_to
        )
        if not success:
            raise HTTPException(status_code=400, detail=msg)
    else:
        if update.assigned_to:
            alert.assigned_to = update.assigned_to
        if update.resolution_note:
            alert.resolution_note = update.resolution_note
        db.commit()
        db.refresh(alert)

    proj = db.query(Project).filter(Project.project_id == alert.project_id).first()

    return AlertResponse(
        id=alert.id,
        project_id=alert.project_id,
        project_name=proj.project_name if proj else None,
        sector=proj.sector if proj else None,
        ministry=proj.ministry if proj else None,
        rule_id=alert.rule_id,
        severity=alert.severity,
        title=alert.title,
        detail=alert.detail,
        status=alert.status,
        created_at=alert.created_at,
        acknowledged_by=alert.acknowledged_by,
        assigned_to=alert.assigned_to,
        resolved_at=alert.resolved_at,
        resolution_note=alert.resolution_note,
        cooldown_until=alert.cooldown_until
    )

@router.get("/rules", response_model=List[AlertRuleResponse], tags=["Alerts"])
def get_alert_rules(db: Session = Depends(get_db)):
    """
    Returns configured early warning trigger rules and thresholds.
    """
    rules = db.query(AlertRule).all()
    return [
        AlertRuleResponse(
            id=r.id,
            name=r.name,
            severity=r.severity,
            description=r.description,
            params=r.params,
            enabled=r.enabled
        )
        for r in rules
    ]

@router.put("/rules/{rule_id}", response_model=AlertRuleResponse, tags=["Alerts"])
def update_alert_rule(
    rule_id: str,
    update: AlertRuleUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin)
):
    """
    Updates rule parameters or enabled status. Requires 'admin' role.
    """
    rule = db.query(AlertRule).filter(AlertRule.id == rule_id).first()
    if not rule:
        raise HTTPException(status_code=404, detail=f"Alert rule '{rule_id}' not found")

    if update.params is not None:
        rule.params = update.params
    if update.enabled is not None:
        rule.enabled = update.enabled

    db.commit()
    db.refresh(rule)

    return AlertRuleResponse(
        id=rule.id,
        name=rule.name,
        severity=rule.severity,
        description=rule.description,
        params=rule.params,
        enabled=rule.enabled
    )
