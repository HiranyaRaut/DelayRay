"""
DelayRay FastAPI Application Entrypoint
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from datetime import datetime, timezone
import os

from backend.app.config import settings
from backend.app.api.routes import api_router

app = FastAPI(
    title="DelayRay API",
    description="AI-Powered Predictive Analytics & Early Warning System for Central Sector Infrastructure Projects",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/api/v1/openapi.json"
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origin_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(api_router)

@app.get("/health", tags=["System"])
async def root_health():
    """
    Root health check endpoint.
    """
    return {
        "status": "healthy",
        "service": "DelayRay Backend API",
        "environment": settings.ENVIRONMENT,
        "demo_mode": settings.DEMO_MODE,
        "synthetic_data_badge": settings.SHOW_SYNTHETIC_BADGE,
        "timestamp": datetime.now(timezone.utc).isoformat()
    }

@app.get("/api/v1/health", tags=["System"])
async def api_health():
    """
    API v1 health status endpoint.
    """
    return {
        "status": "healthy",
        "version": "1.0.0",
        "database": "connected (sqlite WAL mode)",
        "llm_backend": f"Ollama ({settings.CHAT_MODEL})",
        "llm_fallback_ready": True,
        "demo_mode": settings.DEMO_MODE,
        "advisory_notice": "Risk scores and predictions support human decisions and do not replace them.",
        "timestamp": datetime.now(timezone.utc).isoformat()
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("backend.app.main:app", host=settings.HOST, port=settings.PORT, reload=True)
