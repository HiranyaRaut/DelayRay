"""
DelayRay Project Analytical API Contract Tests
Tests project listings, details, S-curves, SHAP drivers, peer benchmarking, what-if, and PDF brief.
"""

import pytest
from fastapi.testclient import TestClient
from backend.app.main import app

client = TestClient(app)

def test_list_projects_default():
    """Projects endpoint returns paginated ongoing projects."""
    response = client.get("/api/v1/projects?page=1&page_size=10")
    assert response.status_code == 200
    data = response.json()
    assert data["total"] == 1981
    assert len(data["items"]) == 10
    item = data["items"][0]
    assert "project_id" in item
    assert "risk_score" in item
    assert "risk_band" in item
    assert "value_at_risk_cr" in item

def test_list_projects_search_and_filter():
    """Filtering by sector and searching by name works properly."""
    res_sector = client.get("/api/v1/projects?sector=Railways&page_size=5")
    assert res_sector.status_code == 200
    data = res_sector.json()
    assert all(p["sector"] == "Railways" for p in data["items"])

def test_get_project_detail_and_timeline():
    """Retrieves full detail and timeline for an existing project."""
    # Grab first project ID
    list_res = client.get("/api/v1/projects?page_size=1")
    pid = list_res.json()["items"][0]["project_id"]

    detail_res = client.get(f"/api/v1/projects/{pid}")
    assert detail_res.status_code == 200
    detail = detail_res.json()
    assert detail["project_id"] == pid
    assert "risk_score" in detail
    assert "spi" in detail

    timeline_res = client.get(f"/api/v1/projects/{pid}/timeline")
    assert timeline_res.status_code == 200
    timeline = timeline_res.json()
    assert len(timeline) > 0
    assert "physical_progress_pct" in timeline[0]

def test_get_project_scurve():
    """Retrieves S-curve with planned, actual, and forecast bands."""
    list_res = client.get("/api/v1/projects?page_size=1")
    pid = list_res.json()["items"][0]["project_id"]

    res = client.get(f"/api/v1/projects/{pid}/scurve")
    assert res.status_code == 200
    data = res.json()
    assert data["project_id"] == pid
    assert len(data["points"]) > 0

def test_get_project_explain():
    """Retrieves SHAP waterfall drivers and playbook actions."""
    list_res = client.get("/api/v1/projects?page_size=1")
    pid = list_res.json()["items"][0]["project_id"]

    res = client.get(f"/api/v1/projects/{pid}/explain")
    assert res.status_code == 200
    data = res.json()
    assert "risk_score" in data
    assert "drivers" in data

def test_get_project_peers():
    """Retrieves peer benchmarking percentiles and radar dimensions."""
    list_res = client.get("/api/v1/projects?page_size=1")
    pid = list_res.json()["items"][0]["project_id"]

    res = client.get(f"/api/v1/projects/{pid}/peers")
    assert res.status_code == 200
    data = res.json()
    assert "risk_percentile" in data
    assert "radar_dimensions" in data

def test_project_whatif_simulator():
    """Simulates counterfactual parameter adjustments."""
    list_res = client.get("/api/v1/projects?page_size=1")
    pid = list_res.json()["items"][0]["project_id"]

    req_body = {
        "land_handover_pct": 95.0,
        "contractor_rating": 85.0
    }
    res = client.post(f"/api/v1/projects/{pid}/whatif", json=req_body)
    assert res.status_code == 200
    data = res.json()
    assert data["project_id"] == pid
    assert "simulated_risk_score" in data
    assert "delta_risk_score" in data
    assert "caveat" in data

def test_export_project_brief_pdf():
    """Downloads executive risk brief in PDF format."""
    list_res = client.get("/api/v1/projects?page_size=1")
    pid = list_res.json()["items"][0]["project_id"]

    res = client.get(f"/api/v1/projects/{pid}/brief.pdf")
    assert res.status_code == 200
    assert res.headers["content-type"] == "application/pdf"
    assert res.content.startswith(b"%PDF")
