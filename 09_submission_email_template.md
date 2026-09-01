Subject: MLOps Technical Assignment Submission – G13

Hi Team,

Role level:
G13

GitHub repository:
[https://github.com/<your-org>/<your-repo>](https://github.com/demoappxcode/MLOps_G13_Technical_Assignment_Pack/blob/main/09_submission_email_template.md)

Architecture summary:
This submission implements a complete MLOps control center with a FastAPI backend, Angular dashboard, SQLAlchemy persistence, deployment lifecycle logic, Docker packaging, and automated validation. The system manages models, versions, approvals, deployment retries, and rollback flows in a simple but realistic operational design.

Run command:
```bash
docker compose up --build
```

Test command:
```bash
cd backend
python -m pytest tests -q -o pythonpath=backend
```

Demo:
Local backend: http://localhost:8000/docs
Local frontend: http://localhost:4200

Known limitations:
- no production authentication or RBAC
- deployment actions are simulated state transitions rather than live infrastructure orchestration
- local runtime uses SQLite by default, while Docker is configured for PostgreSQL

Estimated effort:
Approximately 12-16 hours including implementation, validation, and documentation.

Regards,
Candidate Name
