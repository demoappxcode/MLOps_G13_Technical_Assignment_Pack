from __future__ import annotations

from datetime import datetime
from typing import Any

from pydantic import BaseModel, Field


class ModelCreate(BaseModel):
    name: str
    framework: str
    algorithm: str
    owner: str
    description: str | None = None


class ModelRead(ModelCreate):
    id: int
    lifecycle_stage: str
    created_at: datetime
    updated_at: datetime


class ModelList(BaseModel):
    items: list[ModelRead]
    total: int


class ModelVersionCreate(BaseModel):
    version: str
    artifact_uri: str
    training_data_ref: str
    framework: str
    algorithm: str
    metadata: dict[str, Any] = Field(default_factory=dict)


class ModelVersionRead(ModelVersionCreate):
    id: int
    model_id: int
    approved: bool
    lifecycle_stage: str
    created_at: datetime
    updated_at: datetime


class VersionList(BaseModel):
    items: list[ModelVersionRead]
    total: int


class DeploymentCreate(BaseModel):
    model_id: int
    version_id: int
    environment: str
    requested_by: str


class DeploymentRead(BaseModel):
    id: int
    model_id: int
    version_id: int
    environment: str
    status: str
    requested_by: str
    error_message: str | None = None
    retry_count: int
    created_at: datetime
    updated_at: datetime


class DeploymentList(BaseModel):
    items: list[DeploymentRead]
    total: int


class MetricsRead(BaseModel):
    model_id: int
    model_name: str
    metrics: dict[str, Any]
