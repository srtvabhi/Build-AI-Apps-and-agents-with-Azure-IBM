# Use Case 6: Autonomous Multi-Agent Employee Onboarding Orchestration

## Complete the Microsoft Foundry lab first

Before developing this use case, complete the following hands-on lab:

**[Develop a multi-agent solution](https://gsi.learnondemand.net/Lab/81355?instructionSetLang=en&classId=770602)**

The lab introduces multi-agent concepts and prepares the Microsoft Foundry
environment used by the Python implementations in this folder.

## Objective

Build and compare two streamed multi-agent workflows for employee onboarding:

1. A **sequential orchestration**, in which five specialist agents work one after
   another and each agent receives the preceding context.
2. A **hybrid parallel orchestration**, in which HR validates the employee first,
   IT, Learning, and Manager planning then run concurrently, and Reporting waits
   for all three results before creating the final readiness report.

Both implementations stream agent output to the VS Code terminal, allowing the
user to see progress without waiting for the complete workflow to finish.

The solution creates proposed onboarding plans only. It does not create real
accounts, order devices, grant permissions, enroll courses, or schedule meetings.

## Agent responsibilities

| Agent | Responsibility |
|---|---|
| HR Agent | Validates the employee record and identifies missing or invalid data. |
| IT Agent | Proposes identity, equipment, application, access, and security setup. |
| Learning Agent | Proposes compliance and role-specific training with owners and due dates. |
| Manager Agent | Creates the first-week schedule, introductions, and initial assignment. |
| Reporting Agent | Consolidates readiness, dependencies, risks, and outstanding actions. |

## Sequential orchestration architecture

```text
Employee onboarding request
            |
            v
      +-------------+
      |  HR Agent   |
      +-------------+
            |
            v
      +-------------+
      |  IT Agent   |
      +-------------+
            |
            v
      +----------------+
      | Learning Agent |
      +----------------+
            |
            v
      +---------------+
      | Manager Agent |
      +---------------+
            |
            v
      +-----------------+
      | Reporting Agent |
      +-----------------+
            |
            v
Final onboarding report in the terminal
```

In this design, every agent waits for the previous agent. It is useful when each
stage depends strictly on all preceding work, but total execution time is longer.

## Hybrid parallel orchestration architecture

```text
Employee onboarding request
            |
            v
      +-------------+
      |  HR Agent   |
      +-------------+
            |
            | HR-validated employee context
            v
  +---------+----------+----------+
  |                    |          |
  v                    v          v
+----------+   +----------------+  +---------------+
| IT Agent |   | Learning Agent |  | Manager Agent |
+----------+   +----------------+  +---------------+
  |                    |          |
  +---------+----------+----------+
            |
            v
   Merge specialist results
      (technical step only)
            |
            v
      +-----------------+
      | Reporting Agent |
      +-----------------+
            |
            v
Final onboarding report in the terminal
```

HR remains first because specialists should use validated employee data.
Reporting remains last because it needs every specialist result. Only IT,
Learning, and Manager run in parallel because their planning work is independent
after HR validation.

## Project files

```text
on-boarding(sequential).py  Five agents executed sequentially
on-boarding(parallel).py    HR -> three parallel agents -> Reporting
requirements.txt            Required Python packages
.env.example                Safe configuration template
LabGuide.md                 Lab and implementation guide
```

The local `.env` and `.venv` folders are intentionally excluded from GitHub.

## Prerequisites

- Python 3.11 or later
- Visual Studio Code
- Azure CLI
- Access to a Microsoft Foundry project
- A deployed model such as `gpt-5`
- Permission to invoke the project and model

## Task 1: Sign in to Azure

Open a PowerShell terminal in VS Code and run:

```powershell
az login
az account show
```

The scripts use `AzureCliCredential`, so the active Azure CLI identity must have
access to the Microsoft Foundry project.

## Task 2: Create and activate a virtual environment

Navigate to this Use Case 6 folder, and then run:

```powershell
py -m venv .venv
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
pip install -r requirements.txt
```

After activation, `(.venv)` should appear at the beginning of the terminal prompt.

## Task 3: Configure the Foundry project

Create a local `.env` file from the template:

```powershell
Copy-Item .env.example .env
```

Open `.env` and enter your project endpoint and model deployment name:

```dotenv
AZURE_AI_PROJECT_ENDPOINT=https://YOUR-FOUNDRY-RESOURCE.services.ai.azure.com/api/projects/YOUR-PROJECT
AZURE_AI_MODEL_DEPLOYMENT_NAME=gpt-5
```

Do not place API keys, passwords, or other secrets in GitHub. These scripts use
Azure CLI authentication and do not require an API key in the source code.

## Task 4: Run the sequential workflow

```powershell
python "on-boarding(sequential).py"
```

Expected execution order:

```text
HR -> IT -> Learning -> Manager -> Reporting
```

Each response streams to the terminal before the next agent begins.

## Task 5: Run the hybrid parallel workflow

```powershell
python "on-boarding(parallel).py"
```

Expected execution order:

```text
HR -> [IT + Learning + Manager concurrently] -> Reporting
```

The three specialist outputs may appear in a different order on each run because
they execute concurrently. Every streamed line includes the producing agent's
name. Reporting starts only after all three specialists complete.

## How the code works

### Sequential implementation

`SequentialBuilder` receives the five agents in execution order. The output of
each agent becomes context for the next agent. Calling `workflow.run(...,
stream=True)` emits incremental response updates that are immediately flushed to
the terminal.

### Hybrid parallel implementation

`WorkflowBuilder` creates an explicit graph:

- `add_fan_out_edges` sends the HR-validated context to IT, Learning, and Manager.
- The three agents execute concurrently.
- `add_fan_in_edges` waits for all three results.
- `merge_parallel_results` packages the shared HR context and specialist results.
- Reporting receives the merged context and produces the final report.

The merge function is a technical workflow step, not an additional AI agent.

## Expected outcome

After completing this use case, you will be able to:

- Define role-specific Foundry agents with clear responsibilities.
- Compare sequential and parallel multi-agent execution.
- Implement fan-out and synchronized fan-in orchestration.
- Preserve validated context across agent handoffs.
- Stream labeled agent responses in the terminal.
- Produce a consolidated onboarding readiness report.

To leave the virtual environment, run:

```powershell
deactivate
```

## Troubleshooting

### Azure authentication fails

Run `az login` again and verify the correct subscription with `az account show`.
Confirm that the signed-in identity can access the Foundry project.

### Configuration is missing

Confirm that `.env` exists in this folder and contains both required variables.
Do not add quotation marks unless they are part of the value.

### Model deployment is not found

Confirm that `AZURE_AI_MODEL_DEPLOYMENT_NAME` exactly matches the deployment name
shown in the Microsoft Foundry portal.

### Parallel output order changes

This is expected. Concurrent agents complete at different times, while the final
Reporting Agent always waits for all three specialist results.
