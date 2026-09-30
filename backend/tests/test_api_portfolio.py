"""
DelayRay Portfolio Analytics API Contract Tests
Tests portfolio KPI aggregates, dimension breakdowns, trends, and risk radar.
"""

import pytest
from fastapi.testclient import TestClient
from backend.app.main import app

client = TestClient(app)

def test_portfolio_summary():
    """Summary returns correct ongoing count, costs, risk scores, and synthetic badge."""
    response = client.get("/api/v1/portfolio/summary")
    assert response.status_code == 200
    data = response.json()
    assert data["ongoing_projects"] == 1981
    assert data["total_original_cost_cr"] > 100000.0
    assert 0.0 <= data["avg_portfolio_risk_score"] <= 100.0
    assert data["synthetic_data_badge"] is True
    assert "advisory_notice" in data

def test_portfolio_breakdown_by_sector():
    """Breakdown by sector aggregates projects correctly."""
    response = client.get("/api/v1/portfolio/breakdown?dim=sector")
    assert response.status_code == 200
    data = response.json()
    assert data["dimension"] == "sector"
    assert len(data["items"]) > 0
    first = data["items"][0]
    assert "dimension_value" in first
    assert first["project_count"] > 0
    assert first["total_cost_cr"] > 0

def test_portfolio_breakdown_by_ministry():
    """Breakdown by ministry aggregates projects correctly."""
    response = client.get("/api/v1/portfolio/breakdown?dim=ministry")
    assert response.status_code == 200
    data = response.json()
    assert data["dimension"] == "ministry"
    assert len(data["items"]) > 0

def test_portfolio_trend():
    """Trend endpoint returns monthly performance metrics array."""
    response = client.get("/api/v1/portfolio/trend")
    assert response.status_code == 200
    data = response.json()
    assert "trends" in data
    assert len(data["trends"]) > 0
    item = data["trends"][0]
    assert "month" in item
    assert "avg_risk_score" in item

def test_portfolio_value_at_risk():
    """VaR returns top project exposures."""
    response = client.get("/api/v1/portfolio/value-at-risk")
    assert response.status_code == 200
    data = response.json()
    assert "top_exposures" in data
    assert len(data["top_exposures"]) <= 10
    assert data["top_10_var_total_cr"] > 0

def test_portfolio_risk_radar():
    """Risk radar returns scatter points with X=time_elapsed, Y=risk_score, Size=cost."""
    response = client.get("/api/v1/portfolio/risk-radar?limit=50")
    assert response.status_code == 200
    data = response.json()
    assert "projects" in data
    assert len(data["projects"]) <= 50
    if data["projects"]:
        p = data["projects"][0]
        assert "time_elapsed_pct" in p
        assert "risk_score" in p
        assert "original_cost_cr" in p
        assert "value_at_risk_cr" in p
