"""
DelayRay Authentication Routes
Provides JWT authentication, token refresh, and user profile endpoints.
"""

from datetime import timedelta
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session

from backend.app.config import settings
from backend.app.deps import get_db, get_current_user
from backend.app.db.models import User, AuditLog
from backend.app.security import (
    verify_password, create_access_token, decode_access_token
)
from backend.app.core.schemas import (
    UserLogin, TokenResponse, RefreshTokenRequest, UserProfile
)

router = APIRouter()

@router.get("/status", tags=["Auth"])
async def auth_status():
    """Service status check."""
    return {"status": "auth_ready", "modes": ["jwt_bearer"]}

@router.post("/login", response_model=TokenResponse, tags=["Auth"])
def login(login_data: UserLogin, db: Session = Depends(get_db)):
    """
    Authenticates a user via JSON body and issues access and refresh tokens.
    """
    user = db.query(User).filter(User.email == login_data.email).first()
    if not user or not user.is_active or not verify_password(login_data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"}
        )

    access_token = create_access_token(
        data={"sub": user.email, "role": user.role},
        expires_delta=timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    )
    refresh_token = create_access_token(
        data={"sub": user.email, "type": "refresh"},
        expires_delta=timedelta(days=7)
    )

    # Log successful login
    db.add(AuditLog(
        user_email=user.email,
        action="USER_LOGIN",
        entity_type="User",
        entity_id=str(user.id),
        detail={"role": user.role}
    ))
    db.commit()

    return TokenResponse(
        access_token=access_token,
        refresh_token=refresh_token,
        token_type="bearer",
        role=user.role,
        email=user.email
    )

@router.post("/refresh", response_model=TokenResponse, tags=["Auth"])
def refresh_token(req: RefreshTokenRequest, db: Session = Depends(get_db)):
    """
    Exchanges a valid refresh token for a fresh access token.
    """
    payload = decode_access_token(req.refresh_token)
    if not payload or payload.get("type") != "refresh":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired refresh token"
        )
    email = payload.get("sub")
    user = db.query(User).filter(User.email == email, User.is_active == True).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User account inactive or deleted"
        )

    new_access_token = create_access_token(
        data={"sub": user.email, "role": user.role},
        expires_delta=timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    )
    return TokenResponse(
        access_token=new_access_token,
        refresh_token=req.refresh_token,
        token_type="bearer",
        role=user.role,
        email=user.email
    )

@router.get("/me", response_model=UserProfile, tags=["Auth"])
def get_current_profile(current_user: User = Depends(get_current_user)):
    """
    Returns the currently authenticated user's profile and permissions.
    """
    return UserProfile(
        id=current_user.id,
        email=current_user.email,
        role=current_user.role,
        is_active=current_user.is_active,
        created_at=current_user.created_at
    )
