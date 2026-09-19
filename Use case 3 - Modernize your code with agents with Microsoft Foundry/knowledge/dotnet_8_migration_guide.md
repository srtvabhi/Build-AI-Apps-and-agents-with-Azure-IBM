# Enterprise .NET 8 Migration Guide

## Scope

Use this guide when modernizing supported C# and .NET applications to .NET 8.
Validate vendor support and application dependencies before migration.

## Required assessment

- Record the current target framework, SDK, runtime, hosting model, packages,
  operating system, database, authentication mechanism, and deployment model.
- Identify unsupported frameworks, deprecated APIs, Windows-only dependencies,
  binary dependencies, and packages without a compatible release.
- Establish baseline build results, unit tests, integration tests, performance,
  error rate, and resource usage before making changes.

## Modernization standards

- Prefer SDK-style project files and explicit nullable reference-type settings.
- Replace non-generic collections such as `ArrayList` with generic collections
  such as `List<T>` to gain type safety and reduce casting.
- Use dependency injection for replaceable services and external integrations.
- Use asynchronous APIs for genuine I/O operations; do not add `async` without
  an asynchronous dependency.
- Use structured logging and never log secrets or unnecessary personal data.
- Treat compiler warnings as migration work items; do not suppress them without
  a documented reason.
- Pin and scan NuGet dependencies and remove unused packages.

## Testing and release

- Add characterization tests before changing unclear legacy behavior.
- Add unit, integration, authentication, authorization, and failure-path tests.
- Use incremental migration, feature flags, canary deployment, and measurable
  health checks where the application risk warrants them.
- Keep a tested rollback artifact and compatible database rollback strategy.

## Acceptance criteria

The application builds on the approved .NET 8 SDK, passes its automated tests,
has no unapproved critical or high security findings, meets baseline service
levels, and has documented rollback procedures.
