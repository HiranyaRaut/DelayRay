"""
DelayRay Authentication & Role-Based Access Control Tests
Tests JWT token creation, password verification, profile lookup, and role boundaries.
"""

import pytest
from fastapi.testclient import TestClient
from backend.app.main import app

client = TestClient(app)

def test_login_success_viewer():
    """Viewer can login and obtain JWT access token."""
    response = client.post("/api/v1/auth/login", json={"email": "viewer@demo", "password": "demo123"})
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert data["role"] == "viewer"
    assert data["email"] == "viewer@demo"

def test_login_success_analyst():
    """Analyst can login and obtain JWT access token."""
    response = client.post("/api/v1/auth/login", json={"email": "analyst@demo", "password": "demo123"})
    assert response.status_code == 200
    data = response.json()
    assert data["role"] == "analyst"

def test_login_success_admin():
    """Admin can login and obtain JWT access token."""
    response = client.post("/api/v1/auth/login", json={"email": "admin@demo", "password": "demo123"})
    assert response.status_code == 200
    data = response.json()
    assert data["role"] == "admin"

def test_login_failure_bad_password():
    """Invalid credentials return 401 Unauthorized."""
    response = client.post("/api/v1/auth/login", json={"email": "admin@demo", "password": "wrongpassword"})
    assert response.status_code == 401
    assert "Incorrect email or password" in response.json()["detail"]

def test_auth_me_endpoint():
    """Protected profile endpoint requires valid bearer token."""
    # 1. Unauthenticated request rejected
    res_unauth = client.get("/api/v1/auth/me")
    assert res_unauth.status_code == 401

    # 2. Authenticated request succeeds
    login_res = client.post("/api/v1/auth/login", json={"email": "analyst@demo", "password": "demo123"})
    token = login_res.json()["access_token"]
    res_auth = client.get("/api/v1/auth/me", headers={"Authorization": f"Bearer {token}"})
    assert res_auth.status_code == 200
    data = res_auth.json()
    assert data["email"] == "analyst@demo"
    assert data["role"] == "analyst"
    assert data["is_active"] is True

def test_token_refresh():
    """Can exchange refresh token for a fresh access token."""
    login_res = client.post("/api/v1/auth/login", json={"email": "viewer@demo", "password": "demo123"})
    ref_token = login_res.json()["refresh_token"]

    res = client.post("/api/v1/auth/refresh", json={"refresh_token": ref_token})
    assert res.status_code == 200
    assert "access_token" in res.json()
