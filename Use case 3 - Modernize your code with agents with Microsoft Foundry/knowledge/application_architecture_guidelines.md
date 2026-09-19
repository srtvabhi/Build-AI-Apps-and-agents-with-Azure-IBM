# Enterprise Application Architecture Guidelines

## Principles

- Preserve clear business-domain boundaries.
- Keep presentation, application, domain, and infrastructure responsibilities
  separated where application complexity justifies those layers.
- Prefer explicit contracts and dependency direction toward business logic.
- Minimize shared mutable state and hidden coupling.
- Design external calls with timeouts, bounded retries, and observability.

## Modernization approach

- Begin with discovery, dependency mapping, and measurable baselines.
- Use the strangler pattern for high-risk systems that cannot be replaced in one
  release.
- Extract components only when a clear ownership or scaling boundary exists.
- Avoid replacing a monolith with distributed services that preserve the same
  tight coupling.
- Record significant decisions in Architecture Decision Records.

## Data and APIs

- Define versioned contracts and backward-compatibility expectations.
- Make write operations idempotent where retries are possible.
- Plan database changes using expand-and-contract migrations.
- Define ownership, retention, privacy classification, backup, and recovery.

## Operational requirements

- Use structured logs, metrics, traces, correlation identifiers, health checks,
  and actionable alerts.
- Define service-level indicators before optimizing performance.
- Include capacity limits, dependency failure behavior, deployment strategy,
  rollback criteria, and disaster-recovery expectations.

## Review checklist

Recommendations must state the problem being solved, alternatives considered,
tradeoffs, migration dependencies, measurable success criteria, and rollback
plan.
