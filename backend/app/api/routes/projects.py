"""Project registry & hero routes (Phase 3 implementation)"""
from fastapi import APIRouter

router = APIRouter()

@router.get("/status")
async def projects_status():
    return {"status": "projects_ready"}
