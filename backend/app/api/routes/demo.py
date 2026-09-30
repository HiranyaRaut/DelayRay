"""
DelayRay Live Demo Simulation Routes
Provides the 'Advance Month' interactive simulation and Server-Sent Events (SSE) live push.
Adheres strictly to docs/BUILD_SPEC.md Sections 9 and 10.3.
"""

import asyncio
import json
import uuid
from typing import List, Dict, Any, AsyncGenerator
from datetime import datetime, timezone
from fastapi import APIRouter, Depends, HTTPException, Request, status
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session
from sqlalchemy import func

from backend.app.config import settings
from backend.app.deps import get_db
from backend.app.db.models import (
    Project, ProjectSnapshot, Prediction, Alert, Setting
)
from backend.app.core.schemas import AdvanceMonthResponse, AlertResponse
from backend.app.ews.engine import EWSEngine

router = APIRouter()

# Global list of subscriber queues for SSE
_event_subscribers: List[asyncio.Queue] = []

async def broadcast_demo_event(event_type: str, data: Dict[str, Any]):
    """Broadcasts event payload to all active SSE subscribers."""
    payload = json.dumps({"event": event_type, "data": data, "timestamp": datetime.now(timezone.utc).isoformat()})
    for q in list(_event_subscribers):
        try:
            await q.put(payload)
        except Exception:
            if q in _event_subscribers:
                _event_subscribers.remove(q)

@router.get("/status", tags=["Demo"])
def demo_status():
    """Returns demo mode status."""
    return {
        "demo_mode": settings.DEMO_MODE,
        "synthetic_data_badge": True,
        "active_sse_subscribers": len(_event_subscribers)
    }

@router.post("/advance-month", response_model=AdvanceMonthResponse, tags=["Demo"])
async def advance_month(db: Session = Depends(get_db)):
    """
    Simulates the next monthly monitoring cycle (2026-04 -> 2026-05):
    1. Generates new progress & expenditure snapshot for active projects
    2. Recalculates risk scores and VaR
    3. Triggers EWS rules R1-R8
    4. Pushes new live alerts through SSE stream
    """
    if not settings.DEMO_MODE:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Advance month simulation is only permitted when DEMO_MODE=true"
        )

    # 1. Determine current max snapshot month
    latest_month = db.query(func.max(ProjectSnapshot.month)).scalar() or "2026-04"
    y, m = map(int, latest_month.split("-"))
    next_m = 1 if m == 12 else m + 1
    next_y = y + 1 if m == 12 else y
    simulated_month = f"{next_y:04d}-{next_m:02d}"

    # 2. Select priority active ongoing projects to advance
    ongoing_projects = (
        db.query(Project)
        .filter(Project.status == "ongoing")
        .limit(150)
        .all()
    )

    new_snapshots = 0
    rescore_count = 0

    for proj in ongoing_projects:
        # Check if snapshot already exists
        exists = db.query(ProjectSnapshot).filter(
            ProjectSnapshot.project_id == proj.project_id,
            ProjectSnapshot.month == simulated_month
        ).first()
        if exists:
            continue

        prev_snap = (
            db.query(ProjectSnapshot)
            .filter(ProjectSnapshot.project_id == proj.project_id)
            .order_by(ProjectSnapshot.month.desc())
            .first()
        )
        prev_phys = prev_snap.physical_progress_pct if prev_snap else 30.0
        prev_exp = prev_snap.cumulative_expenditure_cr if prev_snap else 200.0

        # Simulate execution advance with realistic noise
        inc_phys = 1.2 if (proj.original_cost_cr < 1000) else 0.8
        inc_exp = proj.original_cost_cr * 0.012

        new_phys = min(99.0, prev_phys + inc_phys)
        new_exp = prev_exp + inc_exp

        # Planned progress
        new_plan = min(100.0, (prev_snap.planned_progress_pct + 1.5) if prev_snap else 35.0)

        snap = ProjectSnapshot(
            project_id=proj.project_id,
            month=simulated_month,
            cumulative_expenditure_cr=round(new_exp, 2),
            physical_progress_pct=round(new_phys, 1),
            planned_progress_pct=round(new_plan, 1),
            milestones_planned_to_date=(prev_snap.milestones_planned_to_date + 1) if prev_snap else 3,
            milestones_achieved_to_date=prev_snap.milestones_achieved_to_date if prev_snap else 2,
            anticipated_completion_date=prev_snap.anticipated_completion_date if prev_snap else proj.original_completion_date,
            cost_revised_to_date_cr=prev_snap.cost_revised_to_date_cr if prev_snap else None,
            revision_count_to_date=prev_snap.revision_count_to_date if prev_snap else 0,
            reporting_lag_days=7,
            remarks="Monthly status review completed. Execution ongoing on primary civil packages."
        )
        db.add(snap)
        new_snapshots += 1

        # Rescore prediction
        pred = (
            db.query(Prediction)
            .filter(Prediction.project_id == proj.project_id)
            .order_by(Prediction.id.desc())
            .first()
        )
        if pred:
            # Slight drift/update in risk score
            spi = new_phys / new_plan
            delta_risk = 2.5 if spi < 0.85 else -0.5
            updated_score = min(98.0, max(5.0, pred.risk_score + delta_risk))
            pred.risk_score = round(updated_score, 1)
            pred.snapshot_month = simulated_month
            if updated_score >= 75.0:
                pred.risk_band = "Critical"
            elif updated_score >= 50.0:
                pred.risk_band = "High"
            elif updated_score >= 25.0:
                pred.risk_band = "Moderate"
            else:
                pred.risk_band = "Low"
            pred.value_at_risk_cr = round(pred.expected_overrun_cr * (updated_score / 100.0), 2)
            rescore_count += 1

    db.commit()

    # 3. Run EWS rules on advanced projects
    engine = EWSEngine(db)
    new_alerts_list: List[Alert] = []
    for proj in ongoing_projects:
        created = engine.evaluate_project(proj.project_id)
        new_alerts_list.extend(created)

    alert_responses = [
        AlertResponse(
            id=a.id,
            project_id=a.project_id,
            rule_id=a.rule_id,
            severity=a.severity,
            title=a.title,
            detail=a.detail,
            status=a.status,
            created_at=a.created_at,
            acknowledged_by=a.acknowledged_by,
            assigned_to=a.assigned_to,
            resolved_at=a.resolved_at,
            resolution_note=a.resolution_note,
            cooldown_until=a.cooldown_until
        )
        for a in new_alerts_list
    ]

    # 4. Broadcast live notification to connected SSE clients
    await broadcast_demo_event("MONTH_ADVANCED", {
        "simulated_month": simulated_month,
        "new_snapshots": new_snapshots,
        "new_alerts_count": len(new_alerts_list),
        "alerts": [a.model_dump(mode="json") for a in alert_responses[:5]]
    })

    return AdvanceMonthResponse(
        simulated_month=simulated_month,
        new_snapshots_count=new_snapshots,
        rescore_count=rescore_count,
        new_alerts_raised=len(new_alerts_list),
        alerts=alert_responses,
        summary_impact={
            "cycle_transition": f"{latest_month} -> {simulated_month}",
            "rescore_scope": f"{rescore_count} assets updated",
            "active_alerts_generated": len(new_alerts_list)
        },
        message=f"Portfolio monitoring month advanced to {simulated_month}. Generated {len(new_alerts_list)} new early warning alerts."
    )

@router.get("/events", tags=["Demo"])
async def stream_demo_events(request: Request):
    """
    Server-Sent Events (SSE) streaming endpoint for live simulation broadcasts.
    """
    queue: asyncio.Queue = asyncio.Queue()
    _event_subscribers.append(queue)

    async def event_stream() -> AsyncGenerator[str, None]:
        try:
            # Send initial ping event
            yield f"data: {json.dumps({'event': 'CONNECTED', 'message': 'Subscribed to DelayRay Live Event Stream'})}\n\n"
            while True:
                # Disconnect check
                if await request.is_disconnected():
                    break
                try:
                    payload = await asyncio.wait_for(queue.get(), timeout=20.0)
                    yield f"data: {payload}\n\n"
                except asyncio.TimeoutError:
                    # Heartbeat comment to keep HTTP connection alive
                    yield ": ping\n\n"
        finally:
            if queue in _event_subscribers:
                _event_subscribers.remove(queue)

    return StreamingResponse(
        event_stream(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no"
        }
    )
