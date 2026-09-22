# Lab Guide: Modernize Code with a Microsoft Foundry Agent

## Launch the lab

Before starting this use case, launch the following lab from your training
portal:

**Build AI agents with portal and VS Code**

## Lab overview

In this portal-only lab, you will build and test a single Code Modernization
Agent in Microsoft Foundry. No Python SDK application is required. The agent
uses enterprise knowledge sources to analyze legacy code, identify technical
debt and security risks, recommend incremental improvements, generate unit
tests, and produce a phased migration roadmap.

Estimated duration: **60–90 minutes**

## Objective

Build a grounded Microsoft Foundry agent that produces safe, practical, and
evidence-based modernization guidance for legacy source code while preserving
documented business behavior.

After completing this lab, you will be able to:

- Create and configure a prompt agent in the Foundry portal.
- Ground the agent with enterprise architecture, security, and coding standards.
- Analyze a realistic legacy customer-service application.
- Separate confirmed findings from assumptions and risks requiring verification.
- Generate refactored code, unit tests, and an incremental migration plan.
- Evaluate the response for accuracy, grounding, safety, and completeness.

## Business scenario

The included Python application represents a legacy retail customer-service
workflow. It validates product returns, calculates refunds, creates support
cases, updates inventory, writes operational logs, sends a simulated customer
notification, and exports a daily report.

The sample deliberately contains legacy design and implementation issues for
the agent to identify. Do not connect it to production systems or use real
customer data.

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
    +-- Web Search, when available and approved
    |
    v
Modernization Report
    +-- Current behavior
    +-- Architecture and technical-debt findings
    +-- Security findings
    +-- Refactored code
    +-- Unit tests
    +-- Migration and rollback plan
    +-- Sources and assumptions
```

## Lab artifacts

```text
LabGuide.md
knowledge/
  application_architecture_guidelines.md
  dotnet_8_migration_guide.md
  enterprise_security_standards.md
  java_modernization_guide.md
  python_coding_standards.md
samples/
  legacy_customer_service.py
evaluation_checklist.md
```

- Upload only the five files in `knowledge/` as agent knowledge sources.
- Use `samples/legacy_customer_service.py` as the code-analysis input.
- Use `evaluation_checklist.md` to score the final responses.
- The agent instructions and all test prompts are included in this guide.

## Prerequisites

- An Azure subscription.
- Access to a Microsoft Foundry project.
- Permission to deploy a model and create an agent.
- A GPT-5 or GPT-5.1 deployment supported in the selected region.
- The files included in this use-case folder.

> Model availability and portal labels can change. Use the equivalent model and
> portal options provided by your instructor when the displayed names differ.

## Task 1: Create or open a Foundry project

1. Open [Microsoft Foundry](https://ai.azure.com/) and sign in.
2. Create a new project or open an existing lab project.
3. If creating a project, use a recognizable name such as:

   ```text
   CodeModernizationProject
   ```

4. Select the Azure subscription, Foundry resource, resource group, and a
   supported region assigned by the lab.
5. Wait for project creation to complete.
6. Confirm that the project home page opens successfully.

## Task 2: Deploy a model

1. Open **Discover** > **Models**, or the equivalent model catalog page.
2. Select an available `GPT-5` or `GPT-5.1` model.
3. Review its model card, region availability, quota, and responsible-AI policy.
4. Deploy the model using the settings assigned by the lab.
5. Wait until the deployment succeeds.
6. Open the deployment in the playground to confirm it is available.

## Task 3: Create the Code Modernization Agent

1. Open **Build** > **Agents**.
2. Select **Create agent**.
3. Configure the agent:

   ```text
   Agent name: Code Modernization Agent
   Model:      GPT-5 or GPT-5.1 deployment
   ```

4. Keep the agent page open for the instruction configuration in Task 4.

## Task 4: Configure the agent instructions

Copy the complete instruction block below and paste it into the agent's
**Instructions** field.

```text
You are the Code Modernization Agent for an enterprise engineering team. Your
job is to review legacy source code and produce safe, practical, evidence-based
modernization guidance.

CORE RESPONSIBILITIES

1. Explain what the submitted code does in plain language.
2. Identify architecture problems, technical debt, maintainability issues,
   performance concerns, reliability gaps, and security risks.
3. Recommend incremental modernization that preserves business behavior.
4. Produce corrected or refactored code when enough context is available.
5. Generate unit tests for the current behavior and proposed implementation.
6. Create a phased migration roadmap with verification and rollback steps.

GROUNDING RULES

- Treat uploaded enterprise standards as the primary source of truth.
- Cite the filename and relevant heading for every policy-based recommendation.
- Use web search only for current vendor documentation or security advisories.
- Clearly label web-derived guidance and include its URL and access date.
- Never invent a policy, dependency version, vulnerability identifier, API, or
  compatibility claim.
- If required context is missing, state the assumption and ask a focused
  question instead of guessing.
- If sources conflict, follow the enterprise standard and describe the conflict.

ANALYSIS WORKFLOW

1. Identify the language, framework, runtime, dependencies, entry points, and
   observable behavior.
2. Summarize the current design and business purpose.
3. List findings with severity: Critical, High, Medium, Low, or Informational.
4. For each finding, include evidence, impact, recommendation, and validation.
5. Separate mandatory security fixes from optional modernization improvements.
6. Prefer small, reversible changes over an unsupported full rewrite.
7. Preserve public contracts unless the user explicitly approves a breaking
   change.
8. Generate tests before or alongside behavior-changing refactoring.
9. Define deployment, monitoring, rollback, and success criteria.

SECURITY RULES

- Never reproduce secrets found in submitted code. Replace them with
  [REDACTED] and recommend secret rotation.
- Do not recommend disabling TLS validation, authentication, authorization,
  input validation, auditing, or dependency verification.
- Flag injection, insecure deserialization, weak cryptography, exposed secrets,
  missing authorization, path traversal, SSRF, unsafe file handling, sensitive
  logging, and vulnerable or unsupported dependencies.
- Distinguish confirmed vulnerabilities from risks that require verification.

REQUIRED FULL-REPORT FORMAT

Use these headings in this exact order:

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

For findings, use a table with: ID, severity, evidence, impact, recommendation,
and validation. Do not claim that generated code is production-ready until it
has been compiled, tested, scanned, and reviewed by a human.
```

Select **Save** after the complete block has been added.

## Task 5: Add the enterprise knowledge sources

1. Add **Knowledge Search** or **File Search** to the agent. The exact label
   depends on the portal version.
2. Upload these five supported Markdown files from `knowledge/`:

   - `application_architecture_guidelines.md`
   - `dotnet_8_migration_guide.md`
   - `enterprise_security_standards.md`
   - `java_modernization_guide.md`
   - `python_coding_standards.md`

3. Wait until every file has finished uploading and indexing.
4. Verify that all five sources are attached to the agent.
5. Save the agent again.

Do not upload secrets, passwords, access tokens, connection strings, private
production source code, or customer data.

## Task 6: Configure optional web search

1. Enable **Web Search** only when it is available and permitted by your
   organization.
2. Keep enterprise knowledge as the primary authority.
3. Require the agent to label web-derived guidance and provide the URL and
   access date.

Web search is useful for current vendor documentation and security advisories,
but it must not silently override approved enterprise standards.

## Task 7: Run the initial modernization test

1. Open the agent playground.
2. Attach `samples/legacy_customer_service.py`, or paste its content into the
   conversation if file attachment is unavailable.
3. Submit this prompt:

   ```text
   Analyze this code and provide a modernization plan.
   ```

4. Confirm that the response explains the code before proposing changes.
5. Confirm that recommendations cite the uploaded enterprise standards.
6. Verify that the agent does not expose secrets or claim untested code is
   production-ready.

## Task 8: Run the complete test scenarios

Run the following scenarios one at a time. Keep the same sample code attached
when the prompt refers to “this code.”

### Scenario 1: Complete modernization assessment

```text
Analyze this code and provide a complete modernization report. Ground your
recommendations in the uploaded enterprise standards. Include modern Python
code, unit tests, a phased migration roadmap, risks, and rollback guidance.
```

Expected themes include separation of concerns, parameterized database access,
transaction safety, decimal currency handling, structured logging, privacy,
dependency injection, tests, and an incremental migration plan.

Run this follow-up prompt:

```text
Compare the proposed modernized solution with the original legacy code. Create
a Before versus After table covering architecture, security, maintainability,
reliability, testability, performance, and operations. For every improvement,
identify the original evidence, the change, the benefit, and how a developer
should verify it. List behavior that must remain unchanged, unresolved risks,
and assumptions. Then self-score this response against every criterion in the
evaluation checklist using 0, 1, or 2, and cite evidence for each score.
```

### Scenario 2: Security review

```text
Perform a security-focused review of this code. Separate confirmed findings
from risks that require more context. For each finding provide severity,
evidence, impact, remediation, and a verification test.
```

The response should distinguish verified problems from risks that require
configuration, runtime, dependency, or infrastructure evidence.

Run this follow-up prompt:

```text
Compare the security of the proposed code with the original legacy code. Create
a table with finding, original evidence, old risk, remediation, new protection,
verification test, and residual risk. Do not mark an issue fixed unless the
proposed code or configuration provides evidence. Self-score the security,
evidence, secrets-handling, and validation criteria from the evaluation
checklist using 0, 1, or 2, with a reason for each score.
```

### Scenario 3: Unit-test generation

```text
Generate unit tests that characterize the current behavior and tests for the
proposed implementation. Cover success, boundary, and failure cases. State any
assumptions about the test framework.
```

The tests should preserve the current business behavior before validating the
proposed refactoring.

Run this follow-up prompt:

```text
Explain how the generated tests improve confidence compared with the original
legacy code. Create a coverage table for success, boundary, failure, security,
transaction, and rollback scenarios. Map every test to the behavior or risk it
validates, identify remaining coverage gaps, and state which tests characterize
old behavior versus proposed behavior. Self-score the unit-test and
behavior-preservation criteria using 0, 1, or 2, with evidence.
```

### Scenario 4: Documentation generation

```text
Create developer documentation for the current component and the proposed
modernized component. Include purpose, public contract, dependencies, examples,
limitations, and migration notes.
```

The response should clearly separate the current and proposed designs.

Run this follow-up prompt:

```text
Compare the documentation available for the original code with the documentation
created for the modernized solution. List what is now clearer about purpose,
public contracts, dependencies, examples, limitations, operations, migration,
and rollback. Identify undocumented assumptions and information that still
requires confirmation. Self-score the code-understanding, assumptions, and
migration-documentation criteria using 0, 1, or 2, with evidence.
```

### Scenario 5: Grounding challenge

```text
Which enterprise standards support each recommendation? Cite the filename and
heading. If the uploaded documents do not support a claim, label it as an
assumption or a web-derived recommendation.
```

The agent should cite real uploaded sources and must not invent missing policy.

Run this follow-up prompt:

```text
Audit your modernization recommendations for grounding. Produce a table with
recommendation, source filename, source heading, supporting evidence, and source
type: enterprise standard, web guidance, or assumption. Identify recommendations
that are unsupported or conflict with enterprise policy and correct them. Then
self-score the grounding, citation, and source-separation criteria using 0, 1,
or 2, with evidence.
```

### Scenario 6: Insufficient-context test

```text
Recommend a production database and deployment architecture for this class.
```

The agent should ask for workload, data, availability, compliance, and hosting
requirements instead of inventing them.

Run this follow-up prompt:

```text
Evaluate how your response handled missing context compared with making an
unsupported architecture recommendation. List every missing decision input,
why it matters, the question that must be answered, and which design choices it
could change. Identify any assumptions you made and retract unsupported claims.
Self-score the assumptions, evidence, architecture, and non-fabrication criteria
using 0, 1, or 2, with evidence.
```

## Task 9: Review the required response structure

A complete modernization response must contain these sections in order:

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

For every finding, verify that the agent supplies:

- An identifier and severity.
- Evidence from the submitted code.
- Business or technical impact.
- A recommended correction.
- A validation method or test.

## Task 10: Evaluate the agent

The agent can generate a draft evaluation, but its self-score is not an
independent quality decision. A learner, instructor, or code reviewer must
verify the cited evidence and enter the final scores in the checklist.

1. Open `evaluation_checklist.md`.
2. Ask the agent to generate a complete draft checklist:

   ```text
   Evaluate your latest response using every criterion in
   evaluation_checklist.md. Return a Markdown table with criterion, score from
   0 to 2, exact evidence from your response, weakness, and required improvement.
   Calculate the total out of 24. Apply all mandatory failure conditions. Do not
   award a point when evidence is missing, and do not modify your original answer
   while scoring it.
   ```

3. Independently review the agent's proposed scores and evidence.
4. Enter the verified scores in `evaluation_checklist.md`.
5. Calculate the final score out of `24`.
6. Apply the suggested result band.
7. Fail the result regardless of score if the response:

   - Fabricates a source.
   - Exposes a secret.
   - Recommends disabling a required security control.
   - Presents untested generated code as production-ready.
   - Omits rollback guidance for a high-risk change.

8. Revise the instructions, knowledge sources, or prompt when the response does
   not meet the acceptance criteria, and then rerun the failed scenario.

## Task 11: Present the demonstration

Use this sequence for the final demonstration:

1. Show the configured Code Modernization Agent.
2. Show the five indexed enterprise knowledge sources.
3. Attach the legacy customer-service sample.
4. Run the complete modernization assessment.
5. Review the architecture and security findings.
6. Review the proposed refactored code.
7. Review the generated unit tests.
8. Review the phased migration and rollback plan.
9. Show the knowledge citations and assumptions.
10. Present the evaluation score.

## Attachment limits and safe handling

- Each file must remain under 200 MB and 2 million tokens.
- A knowledge source can contain up to 10,000 files.
- This lab uses `.md` and `.py`, which are supported attachment types.
- Never upload secrets, credentials, private production code, or customer data.
- Replace sensitive values with safe placeholders before submitting code.

## Completion criteria

- The agent explains the supplied legacy code correctly.
- Findings are separated by severity and supported with evidence.
- Policy-based recommendations cite the uploaded filename and heading.
- Web-derived guidance is clearly labeled and linked.
- Refactored code preserves documented business behavior.
- Unit tests cover success, boundary, and failure paths.
- The migration plan is phased, testable, and includes rollback guidance.
- Missing context causes the agent to ask questions instead of guessing.
- The final response passes the mandatory evaluation conditions.

## Expected outcome

You have created a grounded, single-agent code-modernization workflow in the
Microsoft Foundry portal. The agent can analyze the supplied legacy application,
produce structured modernization guidance, generate code and tests, cite the
approved enterprise standards, and provide a controlled migration and rollback
plan for human engineering review.
