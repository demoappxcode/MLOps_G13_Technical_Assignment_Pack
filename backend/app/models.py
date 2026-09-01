from datetime import datetime

from sqlalchemy import Boolean, Column, DateTime, ForeignKey, Integer, String, Text
from sqlalchemy.orm import relationship

from .database import Base


class ModelRecord(Base):
    __tablename__ = "models"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), unique=True, index=True, nullable=False)
    framework = Column(String(128), nullable=False)
    algorithm = Column(String(128), nullable=False)
    owner = Column(String(128), nullable=False)
    description = Column(Text, nullable=True)
    lifecycle_stage = Column(String(64), default="DRAFT", nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    versions = relationship("ModelVersion", back_populates="model", cascade="all, delete-orphan")
    deployments = relationship("Deployment", back_populates="model", cascade="all, delete-orphan")


class ModelVersion(Base):
    __tablename__ = "model_versions"

    id = Column(Integer, primary_key=True, index=True)
    model_id = Column(Integer, ForeignKey("models.id"), nullable=False)
    version = Column(String(64), nullable=False)
    artifact_uri = Column(String(255), nullable=False)
    training_data_ref = Column(String(255), nullable=False)
    framework = Column(String(128), nullable=False)
    algorithm = Column(String(128), nullable=False)
    version_metadata = Column(Text, default="{}")
    approved = Column(Boolean, default=False, nullable=False)
    lifecycle_stage = Column(String(64), default="DRAFT", nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    model = relationship("ModelRecord", back_populates="versions")
    deployments = relationship("Deployment", back_populates="version", cascade="all, delete-orphan")


class Deployment(Base):
    __tablename__ = "deployments"

    id = Column(Integer, primary_key=True, index=True)
    model_id = Column(Integer, ForeignKey("models.id"), nullable=False)
    version_id = Column(Integer, ForeignKey("model_versions.id"), nullable=False)
    environment = Column(String(64), nullable=False)
    status = Column(String(64), default="REQUESTED", nullable=False)
    requested_by = Column(String(128), nullable=False)
    error_message = Column(Text, nullable=True)
    retry_count = Column(Integer, default=0, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    model = relationship("ModelRecord", back_populates="deployments")
    version = relationship("ModelVersion", back_populates="deployments")
