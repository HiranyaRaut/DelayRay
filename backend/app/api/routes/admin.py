"""
DelayRay Administration & Governance Routes
User management, audit logging, system settings, and health diagnostics.
Adheres strictly to docs/BUILD_SPEC.md Section 9.
"""

from typing import List, Dict, Any, Optional
from datetime import datetime, timezone
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session
from sqlalchemy import desc

from backend.app.deps import get_db, require_admin
from backend.app.db.models import User, AuditLog, Setting
from backend.app.security import get_password_hash
from backend.app.core.schemas import UserProfile, UserCreate, AuditLogItem, SettingItem

router = APIRouter()

@router.get("/users", response_model=List[UserProfile], tags=["Admin"])
def list_users(db: Session = Depends(get_db), current_user: User = Depends(require_admin)):
    """
    Returns list of system users. Requires 'admin' role.
    """
    users = db.query(User).all()
    return [
        UserProfile(
            id=u.id,
            email=u.email,
            role=u.role,
            is_active=u.is_active,
            created_at=u.created_at
        )
        for u in users
    ]

@router.post("/users", response_model=UserProfile, tags=["Admin"])
def create_user(
    user_in: UserCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin)
):
    """
    Creates a new user account. Requires 'admin' role.
    """
    existing = db.query(User).filter(User.email == user_in.email).first()
    if existing:
        raise HTTPException(status_code=400, detail="User with this email already exists")

    new_user = User(
        email=user_in.email,
        hashed_password=get_password_hash(user_in.password),
        role=user_in.role,
        is_active=True,
        created_at=datetime.now(timezone.utc)
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    db.add(AuditLog(
        user_email=current_user.email,
        action="CREATE_USER",
        entity_type="User",
        entity_id=str(new_user.id),
        detail={"created_email": new_user.email, "role": new_user.role}
    ))
    db.commit()

    return UserProfile(
        id=new_user.id,
        email=new_user.email,
        role=new_user.role,
        is_active=new_user.is_active,
        created_at=new_user.created_at
    )

@router.get("/audit-log", response_model=List[AuditLogItem], tags=["Admin"])
def list_audit_logs(
    limit: int = Query(50, le=200),
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin)
):
    """
    Returns chronological security audit trail. Requires 'admin' role.
    """
    logs = db.query(AuditLog).order_by(desc(AuditLog.created_at)).limit(limit).all()
    return [
        AuditLogItem(
            id=l.id,
            user_email=l.user_email,
            action=l.action,
            entity_type=l.entity_type,
            entity_id=l.entity_id,
            detail=l.detail,
            created_at=l.created_at
        )
        for l in logs
    ]

@router.get("/settings", response_model=List[SettingItem], tags=["Admin"])
def get_settings(db: Session = Depends(get_db)):
    """
    Returns application configuration settings.
    """
    settings_records = db.query(Setting).all()
    if not settings_records:
        # Defaults
        return [
            SettingItem(key="risk_critical_threshold", value=75.0, updated_at=datetime.now(timezone.utc)),
            SettingItem(key="risk_high_threshold", value=50.0, updated_at=datetime.now(timezone.utc)),
            SettingItem(key="spi_warning_threshold", value=0.85, updated_at=datetime.now(timezone.utc)),
            SettingItem(key="presentation_mode_default", value=False, updated_at=datetime.now(timezone.utc))
        ]
    return [
        SettingItem(key=s.key, value=s.value, updated_at=s.updated_at)
        for s in settings_records
    ]

@router.put("/settings/{key}", response_model=SettingItem, tags=["Admin"])
def update_setting(
    key: str,
    val_body: Dict[str, Any],
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin)
):
    """
    Updates system setting. Requires 'admin' role.
    """
    setting = db.query(Setting).filter(Setting.key == key).first()
    now = datetime.now(timezone.utc)
    if not setting:
        setting = Setting(key=key, value=val_body.get("value"), updated_at=now)
        db.add(setting)
    else:
        setting.value = val_body.get("value")
        setting.updated_at = now

    db.commit()
    db.refresh(setting)

    db.add(AuditLog(
        user_email=current_user.email,
        action="UPDATE_SETTING",
        entity_type="Setting",
        entity_id=key,
        detail={"new_value": setting.value}
    ))
    db.commit()

    return SettingItem(key=setting.key, value=setting.value, updated_at=setting.updated_at)

@router.get("/health", tags=["Admin"])
def get_admin_health(db: Session = Depends(get_db)):
    """
    Provides comprehensive runtime system health diagnostics.
    """
    from backend.app.db.models import Project, Prediction, Alert, User
    return {
        "status": "operational",
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "database_connected": True,
        "counts": {
            "projects_total": db.query(Project).count(),
            "predictions_total": db.query(Prediction).count(),
            "alerts_total": db.query(Alert).count(),
            "users_total": db.query(User).count()
        }
    }
