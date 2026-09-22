# Use Case 3: Modernize Code with a Microsoft Foundry Agent

This is a portal-only lab. It creates one Code Modernization Agent in the
Microsoft Foundry portal; no Python SDK application is required.

## Launch the lab

Before starting this use case, launch the following lab from your training
portal:

**Build AI agents with portal and VS Code**

## Objective

Build a grounded agent that can analyze legacy source code, explain behavior,
identify technical debt and security risks, propose modern code, generate unit
tests, and produce a phased migration roadmap.

## Sample business problem

The included Python application represents a legacy retail customer-service
workflow. It validates product returns, calculates refunds, creates support
cases, updates inventory, writes operational logs, sends a simulated customer
notification, and exports a daily report. The sample deliberately contains
legacy design and implementation issues for the agent to identify and improve;
do not connect it to production systems or real customer data.

## Architecture

```text
Developer
    |
    v
Microsoft Foundry Agent Playground
    |
    v
Code Modernization Agent
    |
    +-- GPT-5 or GPT-5.1 model deployment
    |
    +-- Knowledge Search / File Search
    |       |
    |       +-- .NET 8 Migration Guide
    |       +-- Java Modernization Guide
    |       +-- Python Coding Standards
    |       +-- Enterprise Security Standards
    |       +-- Application Architecture Guidelines
    |
    +-- Web Search
    |
    v
Modernization Result
    +-- Legacy-code explanation
    +-- Technical-debt and security findings
    +-- Refactored code and unit tests
    +-- Phased migration roadmap
```

## Portal-ready artifacts

All attachment artifacts use file extensions accepted by the agent.

```text
agent_instructions.md
knowledge/
  application_architecture_guidelines.md
  dotnet_8_migration_guide.md
  enterprise_security_standards.md
  java_modernization_guide.md
  python_coding_standards.md
samples/
  legacy_customer_service.py
evaluation_checklist.md
test_scenarios.md
```

Upload only the five files in `knowledge/` as grounding sources. Paste the
contents of `agent_instructions.md` into the agent's **Instructions** field.
Use the files in `samples/` and the prompts in `test_scenarios.md` for testing.

## Foundry portal procedure

1. Open [Microsoft Foundry](https://ai.azure.com/) and sign in.
2. Create or select a project such as `CodeModernizationProject`.
3. Deploy `GPT-5` or `GPT-5.1`, depending on regional availability and quota.
4. Open **Build → Agents** and create `Code Modernization Agent`.
5. Select the deployed model.
6. Open `agent_instructions.md`, copy all its content, and paste it into the
   agent's **Instructions** field.
7. Add **Knowledge Search** or **File Search** (the label depends on the portal
   version).
8. Upload all five `.md` files from `knowledge/` and wait for indexing.
9. Enable **Web Search** if it is available and permitted by your organization.
10. Save the agent.
11. Attach or paste `samples/legacy_customer_service.py` into the playground
    and use the modernization prompt from `test_scenarios.md`.
12. Score the response using `evaluation_checklist.md`.

## Expected response sections

Every full modernization response should contain:

1. Executive Summary
2. Current Behavior
3. Architecture and Technical Debt
4. Security Findings
5. Modernization Recommendations
6. Refactored Code
7. Unit Tests
8. Migration Roadmap
9. Risks and Rollback Plan
10. Sources and Assumptions

## Attachment limits

- Each file must remain under 200 MB and 2 million tokens.
- A knowledge source can contain up to 10,000 files.
- This lab uses `.md` and `.py`, both supported by the agent.
- Do not upload secrets, passwords, access tokens, connection strings, private
  source code, or customer data.

## Completion criteria

- The agent explains the supplied legacy code correctly.
- Findings are separated by severity and supported by evidence.
- Recommendations cite the uploaded knowledge sources.
- Refactored code preserves documented behavior.
- Generated unit tests cover success, boundary, and failure paths.
- The migration plan is phased, testable, and includes rollback guidance.
- Web-derived claims include URLs and are distinguished from enterprise policy.
