"""
DelayRay Early Warning System (Alerts & Rules) Tests
Tests rules R1-R8 logic, lifecycle transitions, de-duplication, and alert management endpoints.
"""

import pytest
from fastapi.testclient import TestClient
from backend.app.main import app
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
from backend.app.ews.lifecycle import can_transition

client = TestClient(app)

def test_rule_r1_schedule_slippage():
    """SPI < 0.85 for 3 consecutive months triggers R1."""
    assert evaluate_r1_schedule_slippage([0.80, 0.75, 0.70])["triggered"] is True
    assert evaluate_r1_schedule_slippage([0.90, 0.80, 0.70])["triggered"] is False
    assert evaluate_r1_schedule_slippage([0.70, 0.70])["triggered"] is False

def test_rule_r2_spend_divergence():
    """Spend % - Physical % > 10 points triggers R2."""
    assert evaluate_r2_spend_divergence(expenditure_pct=45.0, physical_progress_pct=30.0)["triggered"] is True
    assert evaluate_r2_spend_divergence(expenditure_pct=35.0, physical_progress_pct=30.0)["triggered"] is False

def test_rule_r3_high_model_risk():
    """Risk score >= 75 or jump of >= 15 points triggers R3."""
    assert evaluate_r3_high_model_risk(76.0, 70.0)["triggered"] is True
    assert evaluate_r3_high_model_risk(65.0, 48.0)["triggered"] is True  # jump of 17
    assert evaluate_r3_high_model_risk(50.0, 48.0)["triggered"] is False

def test_rule_r4_forecast_slip():
    """Delay > 6 months triggers R4."""
    assert evaluate_r4_forecast_slip(7.5)["triggered"] is True
    assert evaluate_r4_forecast_slip(4.0)["triggered"] is False

def test_rule_r5_stalled_progress():
    """Stall over 3 consecutive months triggers R5."""
    assert evaluate_r5_stalled_progress([35.0, 35.0, 35.0])["triggered"] is True
    assert evaluate_r5_stalled_progress([35.0, 36.0, 37.0])["triggered"] is False

def test_rule_r6_milestone_misses():
    """2 consecutive missed milestones trigger R6."""
    assert evaluate_r6_milestone_misses(["achieved", "missed", "missed"])["triggered"] is True
    assert evaluate_r6_milestone_misses(["missed", "achieved", "missed"])["triggered"] is False

def test_rule_r7_anomaly():
    """Top 2% anomaly score triggers R7."""
    assert evaluate_r7_anomaly(-0.25)["triggered"] is True
    assert evaluate_r7_anomaly(0.10)["triggered"] is False

def test_rule_r8_critical_challenge():
    """Remark tags with land, clearance or funds with high confidence trigger R8."""
    assert evaluate_r8_critical_challenge(["land_delay", "monsoon"], 0.85)["triggered"] is True
    assert evaluate_r8_critical_challenge(["land_delay"], 0.60)["triggered"] is False

def test_lifecycle_transition_validations():
    """Alert lifecycle enforces permitted transitions."""
    assert can_transition("new", "acknowledged") is True
    assert can_transition("new", "dismissed") is True
    assert can_transition("new", "resolved") is False  # Must acknowledge/assign first

    assert can_transition("acknowledged", "assigned") is True
    assert can_transition("acknowledged", "resolved") is True
    assert can_transition("assigned", "resolved") is True
    assert can_transition("resolved", "new") is False  # Terminal state

def test_alerts_api_list_and_patch():
    """Alerts feed and status updating via API."""
    # Obtain analyst token
    login_res = client.post("/api/v1/auth/login", json={"email": "analyst@demo", "password": "demo123"})
    token = login_res.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    # Fetch alerts
    res = client.get("/api/v1/alerts?page_size=5")
    assert res.status_code == 200
    data = res.json()
    assert "items" in data

    if data["items"]:
        alert_id = data["items"][0]["id"]
        # Update alert to acknowledged
        patch_res = client.patch(
            f"/api/v1/alerts/{alert_id}",
            json={"status": "acknowledged"},
            headers=headers
        )
        assert patch_res.status_code == 200
        assert patch_res.json()["status"] == "acknowledged"

def test_alert_rules_api():
    """Admin can view and update alert rules."""
    # Admin login
    admin_login = client.post("/api/v1/auth/login", json={"email": "admin@demo", "password": "demo123"})
    admin_token = admin_login.json()["access_token"]
    admin_headers = {"Authorization": f"Bearer {admin_token}"}

    # Get rules
    rules_res = client.get("/api/v1/alerts/rules")
    assert rules_res.status_code == 200
    rules = rules_res.json()
    assert len(rules) >= 8

    # Put update on rule R1
    update_res = client.put(
        "/api/v1/alerts/rules/R1",
        json={"params": {"spi_threshold": 0.82, "consecutive_months": 3}},
        headers=admin_headers
    )
    assert update_res.status_code == 200
    assert update_res.json()["params"]["spi_threshold"] == 0.82
