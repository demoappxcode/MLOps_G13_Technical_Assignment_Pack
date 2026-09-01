# ADR-001: Use SQLite for local development and PostgreSQL for containerized runtime

## Status
Accepted

## Context
The project needs a simple, review-friendly persistence setup for both local execution and containerized deployment without requiring heavy operational setup. The assignment also expects Docker packaging and a production-like database configuration.

## Decision
Use SQLite as the default database for local development and configuration-based Postgres for Docker-based runtime. The application reads the `DATABASE_URL` from environment variables, allowing local and containerized setups to share the same code path.

## Alternatives Considered
- PostgreSQL everywhere: stronger production realism, but heavier local setup and slower startup for simple development.
- In-memory storage: easy to prototype, but not realistic for persistence and API validation.

## Consequences
### Positive
- fast local iteration
- simple developer setup
- easy Docker parity for a real database service
- clean separation between local and runtime configuration

### Negative
- local SQLite differs semantically from Postgres for some edge cases
- the project intentionally remains lightweight rather than production-grade

## Follow-up Actions
- add migration tooling for schema versioning in a real production rollout
- expand environment configuration for auth and secret management
- connect the worker to a real async job system if deployment orchestration grows
