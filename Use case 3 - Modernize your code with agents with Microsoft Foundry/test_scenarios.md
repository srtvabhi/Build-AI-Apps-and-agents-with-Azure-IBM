# Code Modernization Agent Test Scenarios

## Scenario 1: Complete modernization assessment

Attach or paste `samples/legacy_customer_service.cs`, then ask:

```text
Analyze this code and provide a complete modernization report. Ground your
recommendations in the uploaded enterprise standards. Include refactored .NET 8
code, unit tests, a phased migration roadmap, risks, and rollback guidance.
```

Expected themes include generic collections, explicit customer types, behavior
preservation, tests, and an incremental migration plan.

## Scenario 2: Security review

```text
Perform a security-focused review of this code. Separate confirmed findings
from risks that require more context. For each finding provide severity,
evidence, impact, remediation, and a verification test.
```

## Scenario 3: Unit tests

```text
Generate unit tests that characterize the current behavior and tests for the
proposed implementation. Cover success, boundary, and failure cases. State any
assumptions about the test framework.
```

## Scenario 4: Documentation

```text
Create developer documentation for the current component and the proposed
modernized component. Include purpose, public contract, dependencies, examples,
limitations, and migration notes.
```

## Scenario 5: Grounding challenge

```text
Which enterprise standards support each recommendation? Cite the filename and
heading. If the uploaded documents do not support a claim, label it as an
assumption or a web-derived recommendation.
```

## Scenario 6: Insufficient context

```text
Recommend a production database and deployment architecture for this class.
```

The agent should ask for workload, data, availability, compliance, and hosting
requirements instead of inventing them.
