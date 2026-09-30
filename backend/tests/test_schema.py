"""
Tests for Database Schema, Pandera Validation, Demo Users, and SQL Views.
"""

import os
import pytest
import bcrypt
import pandas as pd
from sqlalchemy import text
from backend.app.db.session import engine, SessionLocal
from backend.app.db.models import (
    User, Project, ProjectSnapshot, ProjectOutcome, ProjectExtra,
    Ministry, Sector, State, Agency, AlertRule, InterventionsPlaybook
)
from backend.app.core.data_quality import (
    projects_schema, snapshots_schema, outcomes_schema, extras_schema,
    generate_data_quality_report
)

def test_demo_user_credentials():
    """Verifies that demo users exist and passwords verify with bcrypt."""
    db = SessionLocal()
    try:
        viewer = db.query(User).filter(User.email == "viewer@demo").first()
        assert viewer is not None
        assert viewer.role == "viewer"
        assert bcrypt.checkpw(b"demo123", viewer.hashed_password.encode("utf-8"))

        admin = db.query(User).filter(User.email == "admin@demo").first()
        assert admin is not None
        assert admin.role == "admin"
        assert bcrypt.checkpw(b"demo123", admin.hashed_password.encode("utf-8"))
    finally:
        db.close()

def test_master_data_catalogs():
    """Verifies 17 ministries, 22 sectors, and 36 states."""
    db = SessionLocal()
    try:
        assert db.query(Ministry).count() == 17
        assert db.query(Sector).count() == 22
        assert db.query(State).count() == 36
        assert db.query(Agency).count() >= 50
    finally:
        db.close()

def test_sql_views_executable():
    """Verifies that read-only analytical views exist and execute without errors."""
    with engine.connect() as conn:
        res_latest = conn.execute(text("SELECT COUNT(*) FROM vw_project_latest")).scalar()
        assert res_latest is not None

        res_sector = conn.execute(text("SELECT COUNT(*) FROM vw_sector_summary")).scalar()
        assert res_sector is not None

        res_state = conn.execute(text("SELECT COUNT(*) FROM vw_state_summary")).scalar()
        assert res_state is not None

def test_pandera_schema_validation():
    """Verifies Pandera schema validation and quality report generation."""
    synth_dir = os.path.join(os.path.dirname(__file__), "../../data/synthetic")
    p_path = os.path.join(synth_dir, "projects.csv")
    s_path = os.path.join(synth_dir, "project_snapshots.csv")
    o_path = os.path.join(synth_dir, "project_outcomes.csv")
    e_path = os.path.join(synth_dir, "project_extras.csv")

    if all(os.path.exists(p) for p in [p_path, s_path, o_path, e_path]):
        df_p = pd.read_csv(p_path)
        df_s = pd.read_csv(s_path)
        df_o = pd.read_csv(o_path)
        df_e = pd.read_csv(e_path)

        report = generate_data_quality_report(df_p, df_s, df_o, df_e)
        assert report["overall_status"] == "passed"
        assert report["tables"]["projects"]["is_schema_valid"] is True
        assert report["tables"]["project_outcomes"]["high_risk_ratio"] > 0.0
