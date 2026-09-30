"""
DelayRay SQLAlchemy Database Models
Full schema detailed in docs/BUILD_SPEC.md Section 5.
"""

from sqlalchemy import Column, Integer, String, Float, Boolean, DateTime, Text, JSON, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime, timezone
from backend.app.db.session import Base

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String(255), unique=True, index=True, nullable=False)
    hashed_password = Column(String(255), nullable=False)
    role = Column(String(50), default="viewer", nullable=False)  # viewer, analyst, admin
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))

class Project(Base):
    __tablename__ = "projects"

    id = Column(Integer, primary_key=True, index=True)
    project_id = Column(String(100), unique=True, index=True, nullable=False)
    project_name = Column(String(255), nullable=False)
    ministry = Column(String(150), index=True, nullable=False)
    sector = Column(String(100), index=True, nullable=False)
    sub_sector = Column(String(100), nullable=True)
    primary_state = Column(String(100), index=True, nullable=False)
    secondary_states = Column(JSON, nullable=True)
    implementing_agency = Column(String(150), nullable=False)
    agency_type = Column(String(50), nullable=False)
    sanction_date = Column(String(20), nullable=False)
    start_date = Column(String(20), nullable=False)
    original_cost_cr = Column(Float, nullable=False)
    original_completion_date = Column(String(20), nullable=False)
    planned_duration_months = Column(Float, nullable=False)
    funding_mode = Column(String(50), nullable=False)
    status = Column(String(50), default="ongoing", index=True)  # ongoing / completed
    data_source = Column(String(50), default="synthetic")  # synthetic / real
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
