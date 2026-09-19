# Lab: Build a Code Modernization Agent in Microsoft Foundry (Single-Agent, Portal-Only Approach)

## Lab Overview

In this lab, you will build a **Code Modernization Agent** using Microsoft Foundry that can:

- Analyze legacy code
- Explain code functionality
- Identify technical debt
- Detect security risks
- Recommend modernization improvements
- Generate unit tests
- Create a migration roadmap

### Estimated Duration
**60-90 Minutes**

### Skills Covered

- Azure AI Foundry Agent Service
- Prompt Engineering
- Knowledge Grounding (RAG)
- Tool Configuration
- Agent Testing and Evaluation

---

# Architecture

```text
User
  |
  v
Code Modernization Agent
  |
  +--> Code Analysis
  +--> Security Review
  +--> Refactoring Suggestions
  +--> Unit Test Generation
  +--> Migration Roadmap
```

---

# Task 1: Create a Foundry Project

### Step 1
Sign in to:

```text
https://ai.azure.com
```

### Step 2
Create a new project:

```text
Project Name:
CodeModernizationProject
```

### Step 3
Select your Azure subscription and AI Foundry Hub.

### Step 4
Wait for project creation to complete.

Expected Result:

```text
CodeModernizationProject created successfully.
```

---

# Task 2: Deploy a Model

### Step 1
Navigate to:

```text
Models + Endpoints
```

### Step 2
Deploy one of the following models:

```text
GPT-5.1
```

or

```text
GPT-5
```

### Step 3
Accept default deployment settings.

Expected Result:

```text
Model deployment completed.
```

---

# Task 3: Create the Agent

### Step 1
Navigate to:

```text
Build
→ Agents
```

### Step 2
Select:

```text
Create New Agent
```

### Step 3
Configure:

```text
Agent Name:
Code Modernization Agent

Model:
GPT-5 or GPT-5.1
```

---

# Task 4: Configure Agent Instructions

Open `agent_instructions.md` and paste its complete contents into the agent's
**Instructions** field.

---

# Task 5: Add Knowledge Sources

Upload the following supported Markdown files from `knowledge/`:

- `dotnet_8_migration_guide.md`
- `java_modernization_guide.md`
- `python_coding_standards.md`
- `enterprise_security_standards.md`
- `application_architecture_guidelines.md`

Wait until every file has finished indexing before testing the agent.

---

# Task 6: Enable Tools

Enable:

- Knowledge Search
- Web Search

---

# Task 7: Test the Agent

Use the supported C# sample file at `samples/legacy_customer_service.cs`, or
paste its contents into the playground.

Sample Code:

```csharp
public class CustomerService
{
    public ArrayList GetCustomers()
    {
        ArrayList customers = new ArrayList();
        return customers;
    }
}
```

Prompt:

```text
Analyze this code and provide a modernization plan.
```

---

# Task 8: Review Output

Verify:

- Executive Summary
- Architecture Analysis
- Security Findings
- Modernization Recommendations
- Refactored Code
- Unit Tests
- Migration Roadmap

---

# Task 9: Additional Scenarios

Run every prompt in `test_scenarios.md`:

1. Complete Modernization Assessment
2. Security Review
3. Unit Test Generation
4. Documentation Generation
5. Grounding Challenge
6. Insufficient-Context Test

Score the responses using `evaluation_checklist.md`.

---

# Task 10: Demo Story

1. Upload legacy code
2. Analyze application
3. Review findings
4. Modernize code
5. Generate tests
6. Create migration roadmap

---

# Success Criteria

✅ Code Understanding

✅ Security Review

✅ Code Refactoring

✅ Unit Test Generation

✅ Migration Planning

✅ Knowledge Grounding

✅ Web Search Integration

✅ Foundry Single-Agent Implementation

---

# Included Lab Artifacts

- `README.md` - complete portal workflow and architecture
- `agent_instructions.md` - production-oriented agent instructions
- `knowledge/*.md` - five grounding documents in supported format
- `samples/legacy_customer_service.cs` - legacy source-code sample
- `test_scenarios.md` - repeatable test prompts
- `evaluation_checklist.md` - objective scoring rubric

Only upload the five files under `knowledge/` to Knowledge/File Search. Paste
the instructions into the portal field, and use the sample and test files from
the playground. Do not upload secrets or confidential production source code.
