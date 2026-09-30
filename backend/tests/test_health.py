"""
DelayRay Health & Smoke Test Suite
"""

import pytest
from fastapi.testclient import TestClient
from backend.app.main import app

@pytest.fixture
def client():
    return TestClient(app)

def test_root_health_endpoint(client):
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert data["service"] == "DelayRay Backend API"
    assert "timestamp" in data
    assert data["synthetic_data_badge"] is True

def test_api_v1_health_endpoint(client):
    response = client.get("/api/v1/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert data["version"] == "1.0.0"
    assert "sqlite" in data["database"].lower()
    assert "advisory_notice" in data

def test_api_v1_auth_status(client):
    response = client.get("/api/v1/auth/status")
    assert response.status_code == 200
    assert response.json()["status"] == "auth_ready"

def test_api_v1_portfolio_status(client):
    response = client.get("/api/v1/portfolio/status")
    assert response.status_code == 200
    assert response.json()["status"] == "portfolio_ready"
