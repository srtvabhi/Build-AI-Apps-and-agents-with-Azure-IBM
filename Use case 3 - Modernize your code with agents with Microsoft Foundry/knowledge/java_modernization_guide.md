# Enterprise Java Modernization Guide

## Scope

Use this guide for Java application modernization. Select the target Java LTS
version according to the organization's supported-runtime catalog.

## Assessment

- Inventory the JDK, application server, build tool, frameworks, libraries,
  database drivers, deployment platform, and external interfaces.
- Identify unsupported JDKs, obsolete Java EE APIs, proprietary application
  server dependencies, reflection-heavy code, and vulnerable dependencies.
- Capture baseline tests, latency, throughput, memory, CPU, and startup time.

## Modernization standards

- Upgrade in controlled stages: JDK, build tooling, dependencies, framework,
  and deployment platform.
- Prefer generics over raw collections and immutable data where practical.
- Migrate `javax.*` to `jakarta.*` only when the selected framework version
  requires it and all dependencies are compatible.
- Use dependency injection, explicit interfaces at external boundaries, and
  centralized exception handling.
- Use parameterized database access and validate untrusted input.
- Use structured logs with correlation identifiers and no secrets.
- Pin dependencies and run software-composition analysis in CI.

## Testing and rollout

- Preserve behavior with characterization and contract tests.
- Add unit, integration, security, concurrency, and failure-path tests.
- Validate garbage collection, memory, thread usage, and connection pools.
- Release incrementally with telemetry, rollback criteria, and compatible data
  migrations.
