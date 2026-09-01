from __future__ import annotations

import json
from datetime import datetime

from fastapi import Depends, FastAPI, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import select
from sqlalchemy.orm import Session

from .database import Base, SessionLocal, engine
from .models import Deployment, ModelRecord, ModelVersion
from .schemas import (
    DeploymentCreate,
    DeploymentList,
    DeploymentRead,
    MetricsRead,
    ModelCreate,
    ModelList,
    ModelRead,
    ModelVersionCreate,
    ModelVersionRead,
    VersionList,
)

Base.metadata.create_all(bind=engine)

app = FastAPI(title="MLOps Platform API", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:4200", "http://127.0.0.1:4200"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


def get_db() -> Session:
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def serialize_model_version(version: ModelVersion) -> dict:
    metadata = version.version_metadata or "{}"
    if isinstance(metadata, str):
        try:
            metadata = json.loads(metadata)
        except json.JSONDecodeError:
            metadata = {}

    return {
        "id": version.id,
        "model_id": version.model_id,
        "version": version.version,
        "artifact_uri": version.artifact_uri,
        "training_data_ref": version.training_data_ref,
        "framework": version.framework,
        "algorithm": version.algorithm,
        "metadata": metadata,
        "approved": version.approved,
        "lifecycle_stage": version.lifecycle_stage,
        "created_at": version.created_at,
        "updated_at": version.updated_at,
    }


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok", "timestamp": datetime.utcnow().isoformat()}


@app.post("/models", status_code=status.HTTP_201_CREATED, response_model=ModelRead)
def create_model(payload: ModelCreate, db: Session = Depends(get_db)):
    existing = db.execute(select(ModelRecord).where(ModelRecord.name == payload.name)).scalar_one_or_none()
    if existing:
        raise HTTPException(status_code=400, detail="Model already exists")

    model = ModelRecord(
        name=payload.name,
        framework=payload.framework,
        algorithm=payload.algorithm,
        owner=payload.owner,
        description=payload.description,
        lifecycle_stage="DRAFT",
    )
    db.add(model)
    db.commit()
    db.refresh(model)
    return model


@app.get("/models", response_model=ModelList)
def list_models(db: Session = Depends(get_db)):
    records = db.execute(select(ModelRecord).order_by(ModelRecord.created_at.desc())).scalars().all()
    return {"items": records, "total": len(records)}


@app.get("/models/{model_id}", response_model=ModelRead)
def get_model(model_id: int, db: Session = Depends(get_db)):
    model = db.execute(select(ModelRecord).where(ModelRecord.id == model_id)).scalar_one_or_none()
    if not model:
        raise HTTPException(status_code=404, detail="Model not found")
    return model


@app.post(
    "/models/{model_id}/versions",
    status_code=status.HTTP_201_CREATED,
    response_model=ModelVersionRead,
)
def create_model_version(model_id: int, payload: ModelVersionCreate, db: Session = Depends(get_db)):
    model = db.execute(select(ModelRecord).where(ModelRecord.id == model_id)).scalar_one_or_none()
    if not model:
        raise HTTPException(status_code=404, detail="Model not found")

    duplicate = db.execute(
        select(ModelVersion).where(ModelVersion.model_id == model_id, ModelVersion.version == payload.version)
    ).scalar_one_or_none()
    if duplicate:
        raise HTTPException(status_code=409, detail="Version already exists for this model")

    version = ModelVersion(
        model_id=model_id,
        version=payload.version,
        artifact_uri=payload.artifact_uri,
        training_data_ref=payload.training_data_ref,
        framework=payload.framework,
        algorithm=payload.algorithm,
        version_metadata=str(payload.metadata),
        approved=False,
        lifecycle_stage="DRAFT",
    )
    db.add(version)
    db.commit()
    db.refresh(version)
    if model.lifecycle_stage == "DRAFT":
        model.lifecycle_stage = "VALIDATED"
        db.commit()
    return serialize_model_version(version)


@app.get("/models/{model_id}/versions", response_model=VersionList)
def list_model_versions(model_id: int, db: Session = Depends(get_db)):
    model = db.execute(select(ModelRecord).where(ModelRecord.id == model_id)).scalar_one_or_none()
    if not model:
        raise HTTPException(status_code=404, detail="Model not found")

    versions = db.execute(select(ModelVersion).where(ModelVersion.model_id == model_id).order_by(ModelVersion.created_at.desc())).scalars().all()
    return {"items": [serialize_model_version(version) for version in versions], "total": len(versions)}


@app.post("/models/{model_id}/versions/{version_id}/approve", response_model=ModelVersionRead)
def approve_version(model_id: int, version_id: int, payload: dict, db: Session = Depends(get_db)):
    version = db.execute(
        select(ModelVersion).where(ModelVersion.id == version_id, ModelVersion.model_id == model_id)
    ).scalar_one_or_none()
    if not version:
        raise HTTPException(status_code=404, detail="Version not found")

    version.approved = bool(payload.get("approved", True))
    version.lifecycle_stage = "APPROVED" if version.approved else "DRAFT"
    db.commit()
    db.refresh(version)
    return serialize_model_version(version)


@app.post("/deployments", status_code=status.HTTP_201_CREATED, response_model=DeploymentRead)
def create_deployment(payload: DeploymentCreate, db: Session = Depends(get_db)):
    model = db.execute(select(ModelRecord).where(ModelRecord.id == payload.model_id)).scalar_one_or_none()
    if not model:
        raise HTTPException(status_code=404, detail="Model not found")

    version = db.execute(
        select(ModelVersion).where(ModelVersion.id == payload.version_id, ModelVersion.model_id == payload.model_id)
    ).scalar_one_or_none()
    if not version:
        raise HTTPException(status_code=404, detail="Model version not found")

    duplicate = db.execute(
        select(Deployment).where(
            Deployment.model_id == payload.model_id,
            Deployment.version_id == payload.version_id,
            Deployment.environment == payload.environment,
            Deployment.status.notin_(["ROLLED_BACK", "SUCCEEDED"]),
        )
    ).scalar_one_or_none()
    if duplicate:
        raise HTTPException(status_code=409, detail="Duplicate deployment request detected")

    if payload.environment.lower() == "production" and not version.approved:
        raise HTTPException(status_code=400, detail="Version must be approved before production deployment")

    deployment = Deployment(
        model_id=payload.model_id,
        version_id=payload.version_id,
        environment=payload.environment,
        status="REQUESTED",
        requested_by=payload.requested_by,
        retry_count=0,
    )
    db.add(deployment)
    db.commit()
    db.refresh(deployment)
    return DeploymentRead(
        id=deployment.id,
        model_id=deployment.model_id,
        version_id=deployment.version_id,
        environment=deployment.environment,
        status=deployment.status,
        requested_by=deployment.requested_by,
        error_message=deployment.error_message,
        retry_count=deployment.retry_count,
        created_at=deployment.created_at,
        updated_at=deployment.updated_at,
    )


@app.get("/deployments", response_model=DeploymentList)
def list_deployments(db: Session = Depends(get_db)):
    records = db.execute(select(Deployment).order_by(Deployment.created_at.desc())).scalars().all()
    items = [
        DeploymentRead(
            id=item.id,
            model_id=item.model_id,
            version_id=item.version_id,
            environment=item.environment,
            status=item.status,
            requested_by=item.requested_by,
            error_message=item.error_message,
            retry_count=item.retry_count,
            created_at=item.created_at,
            updated_at=item.updated_at,
        )
        for item in records
    ]
    return {"items": items, "total": len(items)}


@app.get("/deployments/{deployment_id}", response_model=DeploymentRead)
def get_deployment(deployment_id: int, db: Session = Depends(get_db)):
    deployment = db.execute(select(Deployment).where(Deployment.id == deployment_id)).scalar_one_or_none()
    if not deployment:
        raise HTTPException(status_code=404, detail="Deployment not found")
    return DeploymentRead(
        id=deployment.id,
        model_id=deployment.model_id,
        version_id=deployment.version_id,
        environment=deployment.environment,
        status=deployment.status,
        requested_by=deployment.requested_by,
        error_message=deployment.error_message,
        retry_count=deployment.retry_count,
        created_at=deployment.created_at,
        updated_at=deployment.updated_at,
    )


@app.post("/deployments/{deployment_id}/retry", response_model=DeploymentRead)
def retry_deployment(deployment_id: int, db: Session = Depends(get_db)):
    deployment = db.execute(select(Deployment).where(Deployment.id == deployment_id)).scalar_one_or_none()
    if not deployment:
        raise HTTPException(status_code=404, detail="Deployment not found")

    deployment.retry_count += 1
    deployment.status = "REQUESTED"
    deployment.error_message = None
    db.commit()
    db.refresh(deployment)
    return DeploymentRead(
        id=deployment.id,
        model_id=deployment.model_id,
        version_id=deployment.version_id,
        environment=deployment.environment,
        status=deployment.status,
        requested_by=deployment.requested_by,
        error_message=deployment.error_message,
        retry_count=deployment.retry_count,
        created_at=deployment.created_at,
        updated_at=deployment.updated_at,
    )


@app.post("/deployments/{deployment_id}/rollback", response_model=DeploymentRead)
def rollback_deployment(deployment_id: int, db: Session = Depends(get_db)):
    deployment = db.execute(select(Deployment).where(Deployment.id == deployment_id)).scalar_one_or_none()
    if not deployment:
        raise HTTPException(status_code=404, detail="Deployment not found")

    deployment.status = "ROLLED_BACK"
    deployment.error_message = "Production rollback executed"
    db.commit()
    db.refresh(deployment)
    return DeploymentRead(
        id=deployment.id,
        model_id=deployment.model_id,
        version_id=deployment.version_id,
        environment=deployment.environment,
        status=deployment.status,
        requested_by=deployment.requested_by,
        error_message=deployment.error_message,
        retry_count=deployment.retry_count,
        created_at=deployment.created_at,
        updated_at=deployment.updated_at,
    )


@app.get("/models/{model_id}/metrics", response_model=MetricsRead)
def get_model_metrics(model_id: int, db: Session = Depends(get_db)):
    model = db.execute(select(ModelRecord).where(ModelRecord.id == model_id)).scalar_one_or_none()
    if not model:
        raise HTTPException(status_code=404, detail="Model not found")

    metrics = {
        "prediction_latency_ms": 93,
        "throughput_rps": 870,
        "error_rate": 0.012,
        "quality_score": 0.91,
        "drift_score": 0.07,
        "availability": 0.998,
        "last_successful_inference": datetime.utcnow().isoformat(),
        "monitoring_status": "healthy",
    }
    return {"model_id": model.id, "model_name": model.name, "metrics": metrics}
