# Test Strategy

## Unit Tests
The project relies on the domain behavior encoded in the API layer and model state transitions rather than deep isolated unit tests for every method. The validation focuses on lifecycle rules such as approval gates, duplicate detection, and environment checks.

## API Tests
The main suite verifies the high-value behaviors:
- model creation and version registration
- invalid production deployment without approval
- retry and rollback of deployments
- health endpoint response

These tests are implemented with FastAPI TestClient and a database fixture that clears records before and after each test to ensure isolation.

## Integration Tests
The implementation is integration-oriented because the service persists model and deployment records in SQLAlchemy and validates end-to-end workflow logic through the API stack.

## Angular Tests
The frontend includes a simple component smoke test that asserts the app instance is created and the dashboard title is exposed. The UI logic is also designed to integrate with backend endpoints for model and deployment operations.

## End-to-End Scenario
Register model → register version → approve → deploy → retry or roll back → inspect the timeline.

## CI, Coverage and Limitations
The repository is setup for CI-style validation with automated backend test execution and Angular build validation. Coverage is intentionally targeted at the assignment workflows rather than broad synthetic test generation, and the project is designed to remain lightweight and reviewable.
