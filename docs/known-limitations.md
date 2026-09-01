# Known Limitations

This project is deliberately scoped to a representative MLOps assignment implementation, not a full enterprise platform.

## Scope limits
- Monitoring and metrics are simulated values rather than ingesting live telemetry from a serving system.
- Deployment actions are synchronous and not processed through a real queue or async worker.
- Role-based access control and authentication are intentionally excluded from the vertical slice.
- Not designed for multi-region or high-scale production workloads.

## Operational assumptions
- The default local database uses SQLite for ease of development and testing.
- Docker Compose uses PostgreSQL for a more realistic containerized deployment profile.
- The project focuses on engineering quality, domain modeling, and workflow correctness instead of advanced ML orchestration.
