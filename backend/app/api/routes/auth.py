"""Authentication routes (Phase 3 implementation)"""
from fastapi import APIRouter

router = APIRouter()

@router.get("/status")
async def auth_status():
    return {"status": "auth_ready", "modes": ["jwt_bearer"]}
