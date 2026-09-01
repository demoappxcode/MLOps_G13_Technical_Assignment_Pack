# MLOps Control Center

A complete MLOps assignment implementation with a Python FastAPI backend, Angular frontend, SQLAlchemy persistence, deployment workflow logic, Docker packaging, and automated test coverage.

## Overview

This repository delivers a lightweight model lifecycle platform that supports:
- model registration and versioning
- approval gates for production deployment
- staging and production deployment workflows
- retry and rollback operations
- metrics surface for monitoring readiness
- Angular dashboard for operational visibility

## Stack

- Backend: Python 3.13+, FastAPI, SQLAlchemy, Pydantic
- Frontend: Angular 17, TypeScript, RxJS
- Storage: SQLite by default for local development, PostgreSQL-ready configuration for Docker
- Packaging: Docker Compose for application, worker, and database services

## Quick start

### Local backend

```bash
cd backend
python -m venv .venv
. .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -r requirements.txt
python -m pytest tests -q -o pythonpath=backend
uvicorn app.main:app --reload --port 8000
```

### Local frontend

```bash
cd frontend
npm install
npm run build
npm start
```

### Docker

```bash
docker compose up --build
```

Then open:
- backend API: http://localhost:8000/docs
- frontend UI: http://localhost:4200

## Project structure

```text
backend/
  app/
    database.py
    main.py
    models.py
    schemas.py
    worker.py
  tests/
    test_api.py
frontend/
  src/app/
  package.json
.docker-compose.yml
.env.example
README.md
```

## Verified status

The current project build was validated with:
- backend tests: `4 passed`
- frontend production build: succeeded

## Known limitations

- The app is intentionally focused on the assignment scope and does not include full multi-tenant auth or production-grade model serving infrastructure.
- Deployment actions are simulated state changes, not real external orchestration.
- Local development defaults to SQLite; Docker config uses PostgreSQL for a closer production-style setup.

## Submission note

This repository was built to satisfy the G13 MLOps assignment expectations with working Python APIs, Angular UI, persistence, deployment lifecycle logic, and test coverage.
