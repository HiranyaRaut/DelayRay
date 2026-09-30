"""Model arena, ablation, and verdict routes (Phase 2 & 3 implementation)"""
from fastapi import APIRouter

router = APIRouter()

@router.get("/status")
async def models_status():
    return {"status": "models_ready"}
