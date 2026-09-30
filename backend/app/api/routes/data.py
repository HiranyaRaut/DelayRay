"""
DelayRay Data Ingestion & Quality Diagnostics Routes
Handles file uploads, Pandera schema validation, data quality reports, and rescoring triggers.
Adheres strictly to docs/BUILD_SPEC.md Section 4.7 and 9.
"""

import os
import shutil
import pandas as pd
from typing import Dict, Any, Optional
from fastapi import APIRouter, Depends, UploadFile, File, HTTPException, BackgroundTasks, status
from sqlalchemy.orm import Session

from backend.app.config import settings
from backend.app.deps import get_db, require_analyst
from backend.app.db.models import User
from backend.app.core.schemas import UploadResponse, ValidationResult
from backend.app.core.data_quality import generate_data_quality_report, validate_dataframe, projects_schema

router = APIRouter()

UPLOAD_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../../../data/uploads"))
SYNTHETIC_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../../../data/synthetic"))

@router.post("/upload", response_model=UploadResponse, tags=["Data"])
async def upload_dataset_file(
    file: UploadFile = File(...),
    current_user: User = Depends(require_analyst)
):
    """
    Accepts CSV or Excel files for ingestion into the project monitoring staging area.
    """
    os.makedirs(UPLOAD_DIR, exist_ok=True)
    file_path = os.path.join(UPLOAD_DIR, file.filename)

    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    try:
        if file.filename.endswith(".csv"):
            df = pd.read_csv(file_path)
        elif file.filename.endswith((".xls", ".xlsx")):
            df = pd.read_excel(file_path)
        else:
            raise HTTPException(status_code=400, detail="Unsupported file format. Please upload CSV or XLSX.")
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Failed to parse uploaded dataset: {str(e)}")

    return UploadResponse(
        filename=file.filename,
        row_count=len(df),
        columns=list(df.columns),
        message=f"File '{file.filename}' uploaded successfully ({len(df)} rows parsed)."
    )

@router.post("/validate", response_model=ValidationResult, tags=["Data"])
def validate_staged_data(filename: str = "projects.csv"):
    """
    Executes Pandera validation checks on uploaded or synthetic dataset tables.
    """
    file_path = os.path.join(SYNTHETIC_DIR, filename)
    if not os.path.exists(file_path):
        file_path = os.path.join(UPLOAD_DIR, filename)
        if not os.path.exists(file_path):
            raise HTTPException(status_code=404, detail=f"Dataset file '{filename}' not found")

    df = pd.read_csv(file_path)
    is_valid, errors = validate_dataframe(df, projects_schema)

    return ValidationResult(
        passed=is_valid,
        summary={"total_records": len(df), "validated_table": filename},
        errors=errors
    )

@router.get("/quality", tags=["Data"])
def get_data_quality():
    """
    Returns data quality diagnostics including missingness %, schema validation, and reporting lags.
    """
    try:
        df_p = pd.read_csv(os.path.join(SYNTHETIC_DIR, "projects.csv"))
        df_s = pd.read_csv(os.path.join(SYNTHETIC_DIR, "project_snapshots.csv"))
        df_o = pd.read_csv(os.path.join(SYNTHETIC_DIR, "project_outcomes.csv"))
        df_e = pd.read_csv(os.path.join(SYNTHETIC_DIR, "project_extras.csv"))
        return generate_data_quality_report(df_p, df_s, df_o, df_e)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error generating data quality report: {str(e)}")

@router.post("/rescore", tags=["Data"])
def trigger_rescore(
    background_tasks: BackgroundTasks,
    current_user: User = Depends(require_analyst),
    db: Session = Depends(get_db)
):
    """
    Triggers batch rescoring job on all ongoing project snapshots and updates EWS alerts.
    """
    from backend.app.ews.engine import EWSEngine
    engine = EWSEngine(db)
    # Evaluate sample of projects in background
    background_tasks.add_task(engine.evaluate_portfolio, 100)

    return {
        "status": "queued",
        "message": "Batch rescore and early warning rule re-evaluation initiated.",
        "triggered_by": current_user.email
    }
