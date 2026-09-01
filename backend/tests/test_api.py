import uuid

import pytest
from fastapi.testclient import TestClient

from app.database import SessionLocal
from app.main import app
from app.models import Deployment, ModelRecord, ModelVersion

client = TestClient(app)


@pytest.fixture(autouse=True)
def clean_db():
    db = SessionLocal()
    db.query(Deployment).delete()
    db.query(ModelVersion).delete()
    db.query(ModelRecord).delete()
    db.commit()
    yield
    db.query(Deployment).delete()
    db.query(ModelVersion).delete()
    db.query(ModelRecord).delete()
    db.commit()
    db.close()


def unique_name(prefix: str) -> str:
    return f"{prefix}-{uuid.uuid4().hex[:8]}"


def test_model_and_version_registration_flow():
    create_response = client.post(
        "/models",
        json={
            "name": unique_name("price-forecast"),
            "framework": "scikit-learn",
            "algorithm": "random_forest",
            "owner": "pricing-team",
            "description": "Predicts next-week prices",
        },
    )
    assert create_response.status_code == 201, create_response.text
    model = create_response.json()
    assert model["name"].startswith("price-forecast-")

    version_response = client.post(
        f"/models/{model['id']}/versions",
        json={
            "version": "v1.0.0",
            "artifact_uri": "s3://bucket/models/price-forecast/v1.0.0",
            "training_data_ref": "warehouse:training:2024-05",
            "framework": "scikit-learn",
            "algorithm": "random_forest",
            "metadata": {"accuracy": 0.91},
        },
    )
    assert version_response.status_code == 201, version_response.text
    version = version_response.json()
    assert version["version"] == "v1.0.0"

    list_response = client.get(f"/models/{model['id']}/versions")
    assert list_response.status_code == 200
    assert len(list_response.json()["items"]) >= 1


def test_deployment_requires_approved_version():
    model_response = client.post(
        "/models",
        json={
            "name": unique_name("quality-score"),
            "framework": "xgboost",
            "algorithm": "gradient_boosting",
            "owner": "ml-ops",
            "description": "Model for quality scoring",
        },
    )
    model = model_response.json()

    version_response = client.post(
        f"/models/{model['id']}/versions",
        json={
            "version": "v2.0.0",
            "artifact_uri": "s3://bucket/models/quality-score/v2.0.0",
            "training_data_ref": "warehouse:training:2024-06",
            "framework": "xgboost",
            "algorithm": "gradient_boosting",
            "metadata": {"accuracy": 0.85},
        },
    )
    version = version_response.json()

    deploy_response = client.post(
        "/deployments",
        json={
            "model_id": model["id"],
            "version_id": version["id"],
            "environment": "production",
            "requested_by": "g13-reviewer",
        },
    )
    assert deploy_response.status_code == 400
    assert "approved" in deploy_response.json()["detail"].lower()


def test_retry_and_rollback_workflow():
    model_response = client.post(
        "/models",
        json={
            "name": unique_name("drift-detector"),
            "framework": "pytorch",
            "algorithm": "cnn",
            "owner": "vision-team",
            "description": "Drift detector",
        },
    )
    model = model_response.json()

    version_response = client.post(
        f"/models/{model['id']}/versions",
        json={
            "version": "v3.0.0",
            "artifact_uri": "s3://bucket/models/drift-detector/v3.0.0",
            "training_data_ref": "warehouse:training:2024-07",
            "framework": "pytorch",
            "algorithm": "cnn",
            "metadata": {"accuracy": 0.92},
        },
    )
    version = version_response.json()

    approve_response = client.post(
        f"/models/{model['id']}/versions/{version['id']}/approve",
        json={"approved": True},
    )
    assert approve_response.status_code == 200

    deploy_response = client.post(
        "/deployments",
        json={
            "model_id": model["id"],
            "version_id": version["id"],
            "environment": "staging",
            "requested_by": "g13-reviewer",
        },
    )
    assert deploy_response.status_code == 201
    deployment = deploy_response.json()

    retry_response = client.post(f"/deployments/{deployment['id']}/retry")
    assert retry_response.status_code == 200

    rollback_response = client.post(f"/deployments/{deployment['id']}/rollback")
    assert rollback_response.status_code == 200


def test_health_endpoint():
    response = client.get("/health")
    assert response.status_code == 200
    payload = response.json()
    assert payload["status"] == "ok"
