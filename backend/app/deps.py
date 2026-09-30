"""
DelayRay FastApi Dependency Injection Module
"""

from typing import Generator, Optional
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from backend.app.config import settings

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/login", auto_error=False)

def get_current_user_optional(token: Optional[str] = Depends(oauth2_scheme)) -> Optional[dict]:
    """
    Optional user dependency for public / demo endpoints.
    """
    if not token:
        return None
    from backend.app.security import decode_access_token
    payload = decode_access_token(token)
    return payload
