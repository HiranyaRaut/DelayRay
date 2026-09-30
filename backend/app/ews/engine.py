"""
DelayRay Early Warning System (EWS) Evaluation Engine
Evaluates project status against rules R1-R8 with de-duplication, cooldown, and auto-resolution.
Adheres to docs/BUILD_SPEC.md Section 7.
"""

import os
import uuid
import yaml
import numpy as np
from datetime import datetime, timezone, timedelta
from typing import Dict, Any, List, Optional
from sqlalchemy.orm import Session
from sqlalchemy import desc

from backend.app.db.models import (
    Project, ProjectSnapshot, Prediction, Alert, AlertRule,
    Milestone, ProjectRemark, AuditLog
)
from backend.app.ews.rules import (
    evaluate_r1_schedule_slippage,
    evaluate_r2_spend_divergence,
    evaluate_r3_high_model_risk,
    evaluate_r4_forecast_slip,
    evaluate_r5_stalled_progress,
    evaluate_r6_milestone_misses,
    evaluate_r7_anomaly,
    evaluate_r8_critical_challenge
)
from backend.app.ews.lifecycle import is_in_cooldown

RULE_DEFAULTS = {
    "R1": {"name": "Schedule slippage", "severity": "Warning", "title": "Chronic Schedule Slippage (SPI < 0.85)"},
    "R2": {"name": "Spend-progress divergence", "severity": "Warning", "title": "Spend Ahead of Physical Progress (> 10%)"},
    "R3": {"name": "High model risk", "severity": "Critical", "title": "Elevated Portfolio Risk Flag (Score >= 75 or Surge)"},
    "R4": {"name": "Forecast slip", "severity": "Warning", "title": "Projected Completion Slip (> 6 Months Delay)"},
    "R5": {"name": "Stalled progress", "severity": "Critical", "title": "Severe Execution Stall (Zero Progress over 3 Months)"},
    "R6": {"name": "Milestone misses", "severity": "Warning", "title": "Consecutive Critical Milestones Missed"},
    "R7": {"name": "Anomaly", "severity": "Watch", "title": "Trajectory Anomaly Detected (Unusual Spend Velocity)"},
    "R8": {"name": "Critical challenge", "severity": "Critical", "title": "Critical Latent Bottleneck Identified in Remarks"}
}

class EWSEngine:
    def __init__(self, db: Session):
        self.db = db
        self.rules_config = self._load_rules()

    def _load_rules(self) -> Dict[str, Dict[str, Any]]:
        """Loads enabled rules and params from database or fallback YAML."""
        rules = {}
        try:
            db_rules = self.db.query(AlertRule).all()
            for r in db_rules:
                rules[r.id] = {
                    "name": r.name,
                    "severity": r.severity,
                    "enabled": r.enabled,
                    "params": r.params or {}
                }
        except Exception:
            pass

        # If DB had no rules, seed from YAML defaults
        if not rules:
            yaml_path = os.path.join(os.path.dirname(__file__), "rules.yaml")
            if os.path.exists(yaml_path):
                with open(yaml_path, "r", encoding="utf-8") as f:
                    data = yaml.safe_load(f)
                    for r in data.get("rules", []):
                        rules[r["id"]] = {
                            "name": r["name"],
                            "severity": r["severity"],
                            "enabled": r.get("enabled", True),
                            "params": r.get("parameters", {})
                        }
        return rules

    def evaluate_project(self, project_id: str) -> List[Alert]:
        """
        Evaluates all enabled rules for a specific project based on latest snapshots,
        predictions, remarks, and milestones.
        """
        project = self.db.query(Project).filter(Project.project_id == project_id).first()
        if not project:
            return []

        # Fetch recent snapshots ordered chronologically
        snapshots = (
            self.db.query(ProjectSnapshot)
            .filter(ProjectSnapshot.project_id == project_id)
            .order_by(ProjectSnapshot.month.asc())
            .all()
        )
        if not snapshots:
            return []

        latest_snap = snapshots[-1]
        latest_pred = (
            self.db.query(Prediction)
            .filter(Prediction.project_id == project_id)
            .order_by(Prediction.id.desc())
            .first()
        )

        # Historical series
        spi_hist = []
        progress_hist = []
        for s in snapshots:
            if s.planned_progress_pct and s.planned_progress_pct > 0:
                spi = s.physical_progress_pct / s.planned_progress_pct
            else:
                spi = 1.0
            spi_hist.append(spi)
            progress_hist.append(s.physical_progress_pct)

        # Remarks & tags
        recent_remark = (
            self.db.query(ProjectRemark)
            .filter(ProjectRemark.project_id == project_id)
            .order_by(ProjectRemark.month.desc())
            .first()
        )
        remark_tags = recent_remark.extracted_tags if recent_remark and recent_remark.extracted_tags else []
        remark_conf = recent_remark.tag_confidence if recent_remark else 0.0

        # Milestones
        milestones = (
            self.db.query(Milestone)
            .filter(Milestone.project_id == project_id)
            .order_by(Milestone.planned_date.asc())
            .all()
        )
        milestone_statuses = [m.status for m in milestones]

        created_alerts: List[Alert] = []

        # ==============================================================
        # Evaluate Each Rule
        # ==============================================================
        eval_results: Dict[str, Dict[str, Any]] = {}

        # R1: Schedule slippage
        r1_cfg = self.rules_config.get("R1", {})
        if r1_cfg.get("enabled", True):
            p = r1_cfg.get("params", {})
            eval_results["R1"] = evaluate_r1_schedule_slippage(
                spi_hist,
                threshold=p.get("spi_threshold", 0.85),
                consecutive_months=p.get("consecutive_months", 3)
            )

        # R2: Spend-progress divergence
        r2_cfg = self.rules_config.get("R2", {})
        if r2_cfg.get("enabled", True):
            p = r2_cfg.get("params", {})
            exp_pct = (latest_snap.cumulative_expenditure_cr / project.original_cost_cr * 100.0) if project.original_cost_cr > 0 else 0.0
            eval_results["R2"] = evaluate_r2_spend_divergence(
                expenditure_pct=exp_pct,
                physical_progress_pct=latest_snap.physical_progress_pct,
                divergence_threshold=p.get("divergence_pct", 10.0)
            )

        # R3: High model risk
        r3_cfg = self.rules_config.get("R3", {})
        if r3_cfg.get("enabled", True) and latest_pred:
            p = r3_cfg.get("params", {})
            # Look up previous month prediction if available
            prev_pred = None
            if len(snapshots) > 1:
                prev_month = snapshots[-2].month
                prev_pred_obj = (
                    self.db.query(Prediction)
                    .filter(Prediction.project_id == project_id, Prediction.snapshot_month == prev_month)
                    .first()
                )
                if prev_pred_obj:
                    prev_pred = prev_pred_obj.risk_score

            eval_results["R3"] = evaluate_r3_high_model_risk(
                current_risk_score=latest_pred.risk_score,
                previous_risk_score=prev_pred,
                score_threshold=p.get("score_threshold", 75.0),
                monthly_delta_threshold=p.get("monthly_delta_threshold", 15.0)
            )

        # R4: Forecast slip
        r4_cfg = self.rules_config.get("R4", {})
        if r4_cfg.get("enabled", True) and latest_pred:
            p = r4_cfg.get("params", {})
            eval_results["R4"] = evaluate_r4_forecast_slip(
                predicted_delay_months=latest_pred.delay_p50,
                delay_threshold_months=p.get("delay_months_threshold", 6.0)
            )

        # R5: Stalled progress
        r5_cfg = self.rules_config.get("R5", {})
        if r5_cfg.get("enabled", True):
            p = r5_cfg.get("params", {})
            eval_results["R5"] = evaluate_r5_stalled_progress(
                progress_hist,
                consecutive_stall_months=p.get("consecutive_stall_months", 3)
            )

        # R6: Milestone misses
        r6_cfg = self.rules_config.get("R6", {})
        if r6_cfg.get("enabled", True):
            p = r6_cfg.get("params", {})
            eval_results["R6"] = evaluate_r6_milestone_misses(
                milestone_statuses,
                consecutive_misses=p.get("missed_milestones", 2)
            )

        # R7: Anomaly
        r7_cfg = self.rules_config.get("R7", {})
        if r7_cfg.get("enabled", True):
            # Compute heuristic velocity irregularity for anomaly
            vel = np.diff(progress_hist[-3:]) if len(progress_hist) >= 3 else [1.0]
            score = -0.2 if (np.std(vel) > 8.0 and spi_hist[-1] < 0.8) else 0.1
            eval_results["R7"] = evaluate_r7_anomaly(anomaly_score=score)

        # R8: Critical challenge
        r8_cfg = self.rules_config.get("R8", {})
        if r8_cfg.get("enabled", True):
            p = r8_cfg.get("params", {})
            eval_results["R8"] = evaluate_r8_critical_challenge(
                remark_tags=remark_tags,
                confidence=remark_conf,
                critical_tags=p.get("tags", ["land", "clearance", "funds"]),
                confidence_threshold=p.get("confidence_threshold", 0.75)
            )

        # ==============================================================
        # Process Triggers, De-duplication, Cooldown, and Auto-Resolve
        # ==============================================================
        for rule_id, res in eval_results.items():
            is_triggered = res.get("triggered", False)
            rule_meta = RULE_DEFAULTS.get(rule_id, {})
            severity = self.rules_config.get(rule_id, {}).get("severity", rule_meta.get("severity", "Warning"))
            title = rule_meta.get("title", f"Rule {rule_id} Alert")

            # Check existing alerts for this project & rule
            existing_alerts = (
                self.db.query(Alert)
                .filter(Alert.project_id == project_id, Alert.rule_id == rule_id)
                .order_by(Alert.created_at.desc())
                .all()
            )
            active_alert = next((a for a in existing_alerts if a.status in ("new", "acknowledged", "assigned")), None)
            latest_resolved = next((a for a in existing_alerts if a.status in ("resolved", "dismissed")), None)

            if is_triggered:
                # If already active, do not duplicate
                if active_alert:
                    continue
                # If recently resolved and still in cooldown, suppress flapping
                if latest_resolved and is_in_cooldown(latest_resolved):
                    continue

                # Raise new alert
                alert_id = f"ALT-{datetime.now().strftime('%Y%m')}-{uuid.uuid4().hex[:6].upper()}"
                alert = Alert(
                    id=alert_id,
                    project_id=project_id,
                    rule_id=rule_id,
                    severity=severity,
                    title=title,
                    detail=res.get("detail", {}),
                    status="new",
                    created_at=datetime.now(timezone.utc)
                )
                self.db.add(alert)
                created_alerts.append(alert)

            else:
                # If condition cleared and there is an active alert, auto-resolve it
                if active_alert:
                    active_alert.status = "resolved"
                    active_alert.resolved_at = datetime.now(timezone.utc)
                    active_alert.resolution_note = "Auto-resolved: condition cleared in current monitoring cycle."
                    active_alert.cooldown_until = datetime.now(timezone.utc) + timedelta(days=14)

        if created_alerts:
            self.db.commit()
            for al in created_alerts:
                self.db.refresh(al)

        return created_alerts

    def evaluate_portfolio(self, limit: Optional[int] = None) -> List[Alert]:
        """Runs EWS evaluation over all ongoing projects."""
        query = self.db.query(Project.project_id).filter(Project.status == "ongoing")
        if limit:
            query = query.limit(limit)
        project_ids = [row[0] for row in query.all()]
        all_new_alerts = []
        for pid in project_ids:
            alerts = self.evaluate_project(pid)
            all_new_alerts.extend(alerts)
        return all_new_alerts
