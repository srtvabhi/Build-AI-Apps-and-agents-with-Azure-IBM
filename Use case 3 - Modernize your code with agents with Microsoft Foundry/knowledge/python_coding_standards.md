# Enterprise Python Coding Standards

## Runtime and dependencies

- Use an organization-approved supported Python version.
- Create an isolated virtual environment for every application.
- Declare direct dependencies in `requirements.txt` or `pyproject.toml` and use
  an approved locking process for reproducible builds.
- Remove unused dependencies and scan packages for known vulnerabilities.

## Code quality

- Follow PEP 8 naming and formatting conventions.
- Add type annotations to public functions and important domain models.
- Keep functions focused, minimize global mutable state, and separate business
  logic from I/O and framework code.
- Use context managers for files, connections, and other managed resources.
- Catch specific exceptions. Preserve diagnostic context and avoid silent
  exception handling.

## Security

- Never embed credentials in source code. Use managed identity or an approved
  secret store.
- Validate untrusted input and use parameterized database operations.
- Avoid `eval`, `exec`, unsafe deserialization, shell commands built from user
  input, and unvalidated filesystem paths.
- Do not disable TLS certificate validation.
- Avoid logging credentials, tokens, personal data, or complete request bodies.

## Testing

- Use automated unit tests for success, boundary, and error paths.
- Use integration tests for external services and contract tests for APIs.
- Mock only external boundaries; do not mock the behavior being tested.
- Require review, linting, tests, dependency scanning, and secret scanning in CI.
