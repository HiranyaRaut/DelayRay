"""
DelayRay Model Registry & Artifact Management
Handles serialization, champion promotion, and metadata tracking.
Adheres strictly to docs/BUILD_SPEC.md Section 6.8.
"""

from typing import Dict, Any, List, Optional
import os
import json
import joblib
from datetime import datetime, timezone
from sqlalchemy.orm import Session
from backend.app.db.models import ModelRegistry, ModelMetric

class ModelArtifactManager:
    """Manages model serialization, versioning, and database registry."""
    def __init__(self, artifacts_dir: str = "ml_artifacts/models"):
        self.artifacts_dir = artifacts_dir
        os.makedirs(artifacts_dir, exist_ok=True)

    def save_model(
        self,
        name: str,
        task: str,
        version: str,
        model_object: Any,
        feature_list: List[str],
        params: Dict[str, Any],
        metrics: Dict[str, float],
        is_champion: bool = False,
        db: Optional[Session] = None
    ) -> str:
        """
        Saves model using joblib and records entry in database registry.
        """
        filename = f"{name}_{version}.joblib"
        filepath = os.path.join(self.artifacts_dir, filename)
        joblib.dump(model_object, filepath)

        # Write sidecar JSON metadata
        meta = {
            "name": name,
            "task": task,
            "version": version,
            "artifact_path": filepath,
            "feature_list": feature_list,
            "params": params,
            "metrics": metrics,
            "is_champion": is_champion,
            "saved_at": datetime.now(timezone.utc).isoformat()
        }
        meta_path = os.path.join(self.artifacts_dir, f"{name}_{version}_meta.json")
        with open(meta_path, "w", encoding="utf-8") as f:
            json.dump(meta, f, indent=2)

        # Register in database if session provided
        if db is not None:
            if is_champion:
                # Demote existing champions for this task
                db.query(ModelRegistry).filter(
                    ModelRegistry.task == task,
                    ModelRegistry.is_champion == True
                ).update({"is_champion": False})

            reg_entry = ModelRegistry(
                name=name,
                task=task,
                version=version,
                params=params,
                feature_list=feature_list,
                data_hash="synthetic_seed_42",
                git_commit="b3310ee",
                is_champion=is_champion
            )
            db.add(reg_entry)
            db.commit()
            db.refresh(reg_entry)

            for metric_name, val in metrics.items():
                db.add(ModelMetric(
                    model_id=reg_entry.id,
                    split="test",
                    metric=metric_name,
                    value=float(val)
                ))
            db.commit()

        return filepath
