"""
DelayRay Core Pydantic Schemas
"""

from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field
from datetime import datetime

class HealthResponse(BaseModel):
    status: str
    service: str
    environment: str
    demo_mode: bool
    synthetic_data_badge: bool
    timestamp: str

class UserBase(BaseModel):
    email: str
    role: str = "viewer"  # viewer, analyst, admin

class UserLogin(BaseModel):
    email: str
    password: str

class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    role: str
    email: str
