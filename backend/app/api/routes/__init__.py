"""
DelayRay API v1 Routers Aggregator
"""

from fastapi import APIRouter
from backend.app.api.routes import (
    auth, portfolio, projects, alerts, models, data, assistant, admin, demo
)

api_router = APIRouter(prefix="/api/v1")
api_router.include_router(auth.router, prefix="/auth", tags=["Authentication"])
api_router.include_router(portfolio.router, prefix="/portfolio", tags=["Portfolio"])
api_router.include_router(projects.router, prefix="/projects", tags=["Projects"])
api_router.include_router(alerts.router, prefix="/alerts", tags=["Alerts & EWS"])
api_router.include_router(models.router, prefix="/models", tags=["Model Arena & Ablation"])
api_router.include_router(data.router, prefix="/data", tags=["Data Administration"])
api_router.include_router(assistant.router, prefix="/assistant", tags=["Assistant"])
api_router.include_router(admin.router, prefix="/admin", tags=["Admin & Audit"])
api_router.include_router(demo.router, prefix="/demo", tags=["Demo Simulation"])
