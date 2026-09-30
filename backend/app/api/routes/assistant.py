"""Assistant chat & suggestions routes (Phase 7 implementation)"""
from fastapi import APIRouter

router = APIRouter()

@router.get("/status")
async def assistant_status():
    return {"status": "assistant_ready"}
