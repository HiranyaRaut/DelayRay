"""
DelayRay Live Demo Simulation & Model Artifacts API Tests
Tests advance-month monthly simulation, SSE status, and model research endpoints.
"""

import pytest
from fastapi.testclient import TestClient
from backend.app.main import app

client = TestClient(app)

def test_demo_status():
    """Demo status endpoint returns demo configuration."""
    res = client.get("/api/v1/demo/status")
    assert res.status_code == 200
    data = res.json()
    assert data["demo_mode"] is True
    assert data["synthetic_data_badge"] is True

def test_advance_month_simulation():
    """Advance month simulation produces new snapshots, rescores, and raises alerts."""
    res = client.post("/api/v1/demo/advance-month")
    assert res.status_code == 200
    data = res.json()
    assert "simulated_month" in data
    assert data["new_snapshots_count"] > 0
    assert "rescore_count" in data
    assert "new_alerts_raised" in data

def test_models_leaderboard_endpoint():
    """Leaderboard returns hold-out test set model rankings."""
    res = client.get("/api/v1/models/leaderboard")
    assert res.status_code == 200
    data = res.json()
    assert isinstance(data, list)
    assert any("Stacked ML Ensemble" in m.get("model_name", "") for m in data)

def test_models_verdict_endpoint():
    """Verdict returns significance metrics and text."""
    res = client.get("/api/v1/models/verdict")
    assert res.status_code == 200
    data = res.json()
    assert "verdict_status" in data
    assert "verdict_text" in data
    assert "p_value" in data

def test_models_ablation_endpoint():
    """Ablation returns feature group experiments, CUF attribution, and candidate fields."""
    res = client.get("/api/v1/models/ablation")
    assert res.status_code == 200
    data = res.json()
    assert "ablation_experiments" in data
    assert "cuf_attribution" in data
    assert "ranked_candidates" in data

def test_data_quality_endpoint():
    """Data quality returns schema validation and missingness metrics."""
    res = client.get("/api/v1/data/quality")
    assert res.status_code == 200
    data = res.json()
    assert "overall_status" in data
    assert "tables" in data
