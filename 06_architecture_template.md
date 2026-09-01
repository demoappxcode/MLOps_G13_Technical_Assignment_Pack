# Architecture Document

## Context
The solution implements a lightweight MLOps control plane for managing ML models, versions, and deployments. It must support the lifecycle of experimentation-to-production while remaining easy to run in a local assignment environment.

## Scope
- model registration and ownership metadata
- model version lifecycle tracking
- approval enforcement before production deployment
- deployment creation, retry, and rollback flow
- monitoring-oriented metrics readout
- API and UI validation for operational workflows

## Architecture Overview
The application follows a layered architecture:
- Angular frontend for model operations and deployment dashboard
- FastAPI backend for REST endpoints and business rules
- SQLAlchemy ORM layer for persistence and schema management
- worker/process layer for background tasks and extension points
- SQLite for local development with PostgreSQL compatibility for Docker deployment

## Components
### Frontend
The Angular app provides a control center for creating models, registering versions, approving releases, and tracking deployments.

### API Layer
The FastAPI service exposes endpoints for model lifecycle operations, deployment attempts, and health checks. It validates state transitions and returns structured errors.

### Domain Model
The platform centers on three persistent entities:
- ModelRecord
- ModelVersion
- Deployment

### Persistence
SQLAlchemy stores entity state in a relational database so version and deployment history are traceable across runs.

### Worker / Background Execution
The worker module is structured for extension toward asynchronous job execution or deployment orchestration.

## Domain Model
- ModelRecord: contains name, owner, framework, algorithm, lifecycle stage, and description.
- ModelVersion: tracks artifact URI, training reference, metadata, approved flag, and version state.
- Deployment: records environment, status, retry count, requested_by, and rollback behavior.

## Key Workflows
1. Register a model.
2. Register a version for the model.
3. Approve the version for production use.
4. Deploy to staging or production.
5. Retry after a failed deployment.
6. Roll back an earlier deployment state.
7. Read monitoring metrics for a model.

## Reliability
The backend prevents invalid transitions by checking model existence, version existence, duplicate requests, and approval prerequisites for production deployments. Test fixtures clean database state between API tests to keep results deterministic.

## Security
The app uses environment-based configuration and does not implement production auth or RBAC. This is intentional for the assignment scope and should be extended in a real production deployment.

## Observability
The API exposes `/health`, and deployment and version records provide traceable operational states. The frontend surfaces the deployment timeline and error banner to help operators understand state changes.

## Scaling
The current design is suitable for a single-service assignment workload. Scaling would require adding worker queues, model artifact storage, authentication, and clustered deployments.

## Trade-offs
The project prioritizes clarity and correctness for an assignment over production-grade orchestration. That makes the code easier to review while still implementing a realistic model registry and deployment workflow.
