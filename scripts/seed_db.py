"""
DelayRay Database Seeder Script
Initializes SQLite / PostgreSQL schema, read-only SQL views, demo users,
master data catalogs, alert rules, playbook, and ingests synthetic datasets.
Adheres strictly to docs/BUILD_SPEC.md Section 5.
"""

import os
import sys
import json
import yaml
import bcrypt
import pandas as pd
from datetime import datetime, timezone
from sqlalchemy import text
from sqlalchemy.orm import Session

# Add repository root to python path
ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT_DIR)

from backend.app.config import settings
from backend.app.db.session import engine, SessionLocal, Base
from backend.app.db.master_data import MINISTRIES, SECTORS, STATES, AGENCIES
from backend.app.db.models import (
    Ministry, Sector, State, Agency, User, AlertRule, InterventionsPlaybook,
    Project, ProjectSnapshot, ProjectOutcome, ProjectExtra, ExternalIndicator,
    ProjectRemark, Milestone
)
from scripts.generate_data import generate_synthetic_dataset

DEMO_USERS = [
    {"email": "viewer@demo", "role": "viewer", "password": "demo123"},
    {"email": "analyst@demo", "role": "analyst", "password": "demo123"},
    {"email": "admin@demo", "role": "admin", "password": "demo123"}
]

def hash_password(password: str) -> str:
    """Hashes password with bcrypt."""
    salt = bcrypt.gensalt()
    return bcrypt.hashpw(password.encode("utf-8"), salt).decode("utf-8")

def init_schema_and_views():
    """Creates all database tables and analytical views."""
    print("Creating database tables...")
    Base.metadata.create_all(bind=engine)

    views_path = os.path.join(ROOT_DIR, "backend", "app", "db", "views.sql")
    if os.path.exists(views_path):
        print("Executing read-only SQL views from views.sql...")
        with open(views_path, "r", encoding="utf-8") as f:
            sql_script = f.read()

        # Split statements by semicolon and execute
        with engine.connect() as conn:
            for statement in sql_script.split(";"):
                stmt = statement.strip()
                if stmt:
                    conn.execute(text(stmt))
            conn.commit()
    print("Database tables and views successfully established.")

def seed_master_data(db: Session):
    """Populates Ministries, Sectors, States, and Agencies."""
    print("Seeding master catalogs...")
    # Ministries
    if db.query(Ministry).count() == 0:
        for m in MINISTRIES:
            db.add(Ministry(code=m["code"], name=m["name"]))
        db.commit()

    # Sectors
    if db.query(Sector).count() == 0:
        ministry_id_map = {m.code: m.id for m in db.query(Ministry).all()}
        for s in SECTORS:
            min_id = ministry_id_map.get(s["ministry_code"])
            db.add(Sector(code=s["code"], name=s["name"], ministry_id=min_id))
        db.commit()

    # States
    if db.query(State).count() == 0:
        for st in STATES:
            db.add(State(code=st["code"], name=st["name"], region=st["region"]))
        db.commit()

    # Agencies
    if db.query(Agency).count() == 0:
        for ag in AGENCIES:
            db.add(Agency(code=ag["code"], name=ag["name"], agency_type=ag["agency_type"]))
        db.commit()
    print("Master catalogs seeded successfully.")

def seed_users(db: Session):
    """Seeds default demo users (viewer, analyst, admin)."""
    print("Seeding demo users...")
    for u in DEMO_USERS:
        existing = db.query(User).filter(User.email == u["email"]).first()
        if not existing:
            hashed_pw = hash_password(u["password"])
            db.add(User(
                email=u["email"],
                hashed_password=hashed_pw,
                role=u["role"],
                is_active=True
            ))
    db.commit()
    print("Demo users seeded: viewer@demo, analyst@demo, admin@demo (Password: demo123).")

def seed_alert_rules_and_playbook(db: Session):
    """Loads default alert rules and intervention playbook."""
    print("Seeding alert rules and playbook...")
    # Alert rules
    rules_path = os.path.join(ROOT_DIR, "backend", "app", "ews", "rules.yaml")
    if os.path.exists(rules_path) and db.query(AlertRule).count() == 0:
        with open(rules_path, "r", encoding="utf-8") as f:
            data = yaml.safe_load(f)
            for r in data.get("rules", []):
                db.add(AlertRule(
                    id=r["id"],
                    name=r["name"],
                    severity=r["severity"],
                    description=r["description"],
                    params=r["parameters"],
                    enabled=r.get("enabled", True)
                ))
        db.commit()

    # Intervention playbook
    playbook_path = os.path.join(ROOT_DIR, "backend", "app", "ews", "playbook.yaml")
    if os.path.exists(playbook_path) and db.query(InterventionsPlaybook).count() == 0:
        with open(playbook_path, "r", encoding="utf-8") as f:
            data = yaml.safe_load(f)
            for p in data.get("playbook", []):
                db.add(InterventionsPlaybook(
                    driver_tag=p["driver_tag"],
                    action=p["action"],
                    owner_level=p["owner_level"],
                    expected_effect=p["expected_effect"],
                    evidence_note=p["evidence_note"]
                ))
        db.commit()
    print("Alert rules and playbook seeded.")

def seed_synthetic_data(db: Session):
    """Ingests synthetic data CSVs into database."""
    synth_dir = os.path.join(ROOT_DIR, "data", "synthetic")
    projects_csv = os.path.join(synth_dir, "projects.csv")

    if not os.path.exists(projects_csv):
        print("Synthetic CSV files not found. Generating fresh synthetic dataset...")
        generate_synthetic_dataset(n_completed=7500, n_ongoing=1981, seed=42)

    if db.query(Project).count() > 0:
        print(f"Database already contains {db.query(Project).count()} projects. Skipping CSV bulk insert.")
        return

    print("Bulk-inserting synthetic datasets into database...")
    
    # 1. Projects
    print("  -> Inserting projects...")
    df_p = pd.read_csv(os.path.join(synth_dir, "projects.csv"))
    # Handle NaN in optional columns
    df_p = df_p.where(pd.notnull(df_p), None)
    p_records = df_p.to_dict(orient="records")
    for r in p_records:
        if isinstance(r.get("secondary_states"), str):
            try:
                r["secondary_states"] = json.loads(r["secondary_states"].replace("'", '"'))
            except Exception:
                r["secondary_states"] = None
    db.bulk_insert_mappings(Project, p_records)
    db.commit()

    # 2. Project Outcomes
    print("  -> Inserting outcomes...")
    df_o = pd.read_csv(os.path.join(synth_dir, "project_outcomes.csv"))
    df_o = df_o.where(pd.notnull(df_o), None)
    o_records = df_o.to_dict(orient="records")
    db.bulk_insert_mappings(ProjectOutcome, o_records)
    db.commit()

    # 3. Project Extras
    print("  -> Inserting project extras...")
    df_e = pd.read_csv(os.path.join(synth_dir, "project_extras.csv"))
    df_e = df_e.where(pd.notnull(df_e), None)
    e_records = df_e.to_dict(orient="records")
    db.bulk_insert_mappings(ProjectExtra, e_records)
    db.commit()

    # 4. Snapshots (Chunked insertion for performance)
    print("  -> Inserting project snapshots...")
    df_s = pd.read_csv(os.path.join(synth_dir, "project_snapshots.csv"))
    df_s = df_s.where(pd.notnull(df_s), None)
    s_records = df_s.to_dict(orient="records")
    chunk_size = 5000
    for i in range(0, len(s_records), chunk_size):
        db.bulk_insert_mappings(ProjectSnapshot, s_records[i:i+chunk_size])
        db.commit()

    # 5. Remarks
    print("  -> Inserting remarks...")
    df_r = pd.read_csv(os.path.join(synth_dir, "project_remarks.csv"))
    df_r = df_r.where(pd.notnull(df_r), None)
    r_records = df_r.to_dict(orient="records")
    for r in r_records:
        if isinstance(r.get("extracted_tags"), str):
            try:
                r["extracted_tags"] = json.loads(r["extracted_tags"].replace("'", '"'))
            except Exception:
                r["extracted_tags"] = []
    for i in range(0, len(r_records), chunk_size):
        db.bulk_insert_mappings(ProjectRemark, r_records[i:i+chunk_size])
        db.commit()

    # 6. Milestones
    print("  -> Inserting milestones...")
    df_m = pd.read_csv(os.path.join(synth_dir, "milestones.csv"))
    df_m = df_m.where(pd.notnull(df_m), None)
    m_records = df_m.to_dict(orient="records")
    for i in range(0, len(m_records), chunk_size):
        db.bulk_insert_mappings(Milestone, m_records[i:i+chunk_size])
        db.commit()

    # 7. External Indicators
    print("  -> Inserting external indicators...")
    df_ext = pd.read_csv(os.path.join(synth_dir, "external_indicators.csv"))
    ext_records = df_ext.to_dict(orient="records")
    for i in range(0, len(ext_records), chunk_size):
        db.bulk_insert_mappings(ExternalIndicator, ext_records[i:i+chunk_size])
        db.commit()

    print("All synthetic datasets successfully loaded into database.")

def main():
    print("==================================================")
    print("   DelayRay Database Seeder (Phase 1)")
    print("==================================================")
    init_schema_and_views()
    
    db: Session = SessionLocal()
    try:
        seed_master_data(db)
        seed_users(db)
        seed_alert_rules_and_playbook(db)
        seed_synthetic_data(db)
        
        # Verify counts
        print("\n--- Database Verification Counts ---")
        print(f"Projects:            {db.query(Project).count()}")
        print(f"  - Completed:       {db.query(Project).filter(Project.status == 'completed').count()}")
        print(f"  - Ongoing:         {db.query(Project).filter(Project.status == 'ongoing').count()}")
        print(f"Snapshots:           {db.query(ProjectSnapshot).count()}")
        print(f"Project Outcomes:    {db.query(ProjectOutcome).count()}")
        print(f"Project Extras:      {db.query(ProjectExtra).count()}")
        print(f"Remarks:             {db.query(ProjectRemark).count()}")
        print(f"Milestones:          {db.query(Milestone).count()}")
        print(f"External Indicators: {db.query(ExternalIndicator).count()}")
        print(f"Users:               {db.query(User).count()}")
        print("==================================================")
    finally:
        db.close()

if __name__ == "__main__":
    main()
