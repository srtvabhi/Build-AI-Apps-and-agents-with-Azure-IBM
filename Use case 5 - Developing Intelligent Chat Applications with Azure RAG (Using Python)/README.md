# Use Case 5: Developing Intelligent Chat Applications with Azure RAG (Using Python)

## Lab we will complete

In this use case, we will complete the following hands-on lab:

**[Integrate an AI agent with Foundry IQ](https://gsi.learnondemand.net/Lab/81356?instructionSetLang=en&classId=770602)**

## Why Foundry IQ is well suited for RAG

A language model is limited by the information available when it was trained and
cannot automatically know current organizational data. Retrieval-Augmented
Generation (RAG) solves this knowledge problem by connecting agents to relevant,
up-to-date information at query time. The retrieved evidence grounds the model's
answer without requiring the model to be retrained.

Foundry IQ strengthens this approach by providing a shared knowledge platform
that multiple agents can access. Instead of implementing separate retrieval logic
and duplicate indexes for every agent, teams can connect agents to governed and
reusable knowledge bases.

With Foundry IQ, we can:

- Connect agents to real-time or frequently updated organizational information.
- Provide a shared knowledge platform that multiple agents can use consistently.
- Configure knowledge-base data sources such as Azure AI Search, Azure Blob
  Storage, SharePoint, and Microsoft OneLake.
- Configure agent instructions to control when retrieval occurs, keep answers
  grounded in retrieved evidence, and produce consistent source citations.
- Separate enterprise knowledge from the model so content can be updated without
  retraining or redeploying the model.

## Objective

Develop an intelligent Python chat application that connects to a Microsoft
Foundry prompt agent grounded with Foundry IQ.

The solution will:

1. Create a Microsoft Foundry project and a `product-expert-agent`.
2. Store three Contoso product PDF files in Azure Blob Storage.
3. Connect the storage data to a Foundry IQ knowledge base through Azure AI Search.
4. Add the Foundry IQ knowledge-base tool to the agent.
5. Require user approval before the agent performs each knowledge-base lookup.
6. Connect to the saved agent from Python using the Microsoft Foundry SDK.
7. Maintain a conversation and support follow-up questions.
8. Display grounded answers and available source citations in the terminal.

This is Retrieval-Augmented Generation (RAG), not model fine-tuning. The model is
not retrained on the PDFs. Foundry IQ retrieves relevant content at query time,
and the agent uses that evidence to prepare its answer.

## Business scenario

Contoso sells outdoor camping and hiking products. Customers and employees need
accurate answers about tents, backpacks, and camping accessories. A general model
may not know the current product catalog, so the application grounds the agent in
Contoso product documents and allows the user to approve every external knowledge
lookup.

## Lab architecture

### Knowledge preparation

```text
Contoso product ZIP
        |
        | extract three PDF files
        v
+--------------------------+
| Azure Blob Storage       |
| contosoproducts container|
+--------------------------+
        |
        | Foundry IQ knowledge source
        v
+--------------------------+
| Azure AI Search          |
| search and indexing      |
+--------------------------+
        |
        v
+--------------------------+
| Foundry IQ knowledge base|
| ks-contosoproducts source|
+--------------------------+
        |
        | knowledge-base tool
        v
+--------------------------+
| product-expert-agent     |
+--------------------------+
```

### Runtime question-and-answer flow

```text
User in VS Code terminal
        |
        | question
        v
+-------------------------+
| agent_client.py         |
| - AIProjectClient       |
| - Conversations API     |
| - Responses API         |
+-------------------------+
        |
        | agent reference
        v
+-------------------------+
| product-expert-agent    |
| GPT-5 + instructions    |
+-------------------------+
        |
        | mcp_approval_request
        v
+-------------------------+
| User approval prompt    |
| approve or deny lookup  |
+-------------------------+
        |
        | approved request
        v
+-------------------------+
| Foundry IQ KB tool      |
| retrieves product facts |
+-------------------------+
        |
        v
+-------------------------+
| Azure AI Search index   |
| grounded PDF evidence   |
+-------------------------+
        |
        | evidence and references
        v
+-------------------------+
| Foundry agent response  |
+-------------------------+
        |
        | answer and available citations
        v
Python terminal
```

## Main Azure resources

| Resource | Purpose |
|---|---|
| Microsoft Foundry project | Contains the model, prompt agent, and project endpoint. |
| GPT-5 deployment | Generates agent responses from retrieved evidence. |
| Embedding deployment | Converts document content and queries into searchable representations. |
| Azure Storage account | Stores the three Contoso product PDF files. |
| `contosoproducts` container | Holds the source product documents. |
| Azure AI Search | Provides the search resource used by Foundry IQ. |
| Foundry IQ knowledge base | Retrieves information from the configured product source. |
| `product-expert-agent` | Answers product questions through its knowledge-base tool. |

## Prerequisites

- An Azure subscription with permission to create AI, Search, and Storage resources
- Visual Studio Code
- Git
- Azure CLI
- Python 3.13
- Basic knowledge of Python and the Microsoft Foundry portal

Python 3.14 is not currently supported by all dependencies used in the source lab.
The Microsoft exercise was tested with Python 3.13.12.

## Task 1: Create the Foundry project

1. Open [Microsoft Foundry](https://ai.azure.com).
2. Sign in and enable the **New Foundry** experience.
3. Select **Create a new project**.
4. Enter a name such as `agent-iq-lab`.
5. Select or create the Foundry resource, subscription, resource group, and region.
6. Create the project and wait for its home page to open.

Model availability and quota vary by region. Select another supported region if
the required deployments cannot be created in the first region.

## Task 2: Create the product expert agent

1. In the project, select **Build** > **Agents** > **Create agent**.
2. Name the agent `product-expert-agent`.
3. Use the default deployed chat model, typically `gpt-5`.
4. Configure instructions similar to:

```text
You are Contoso's outdoor camping and hiking product assistant.
Always search the connected knowledge base for product or catalog questions.
Answer only from relevant retrieved information and cite the sources.
If relevant information is not found, say so clearly.
```

5. Save the agent configuration.

## Task 3: Create the Azure AI Search resource

1. In the agent's **Knowledge** section, select **Add** > **Connect to Foundry IQ**.
2. Select **Connect to an AI Search resource** and create a resource.
3. Use the same subscription, resource group, and region as the Foundry project.
4. Use the Free tier when available; otherwise select Basic.
5. Complete creation using the remaining values specified by the active lab.

If creation fails in Foundry, use the provided link to create the resource in the
Azure portal.

## Task 4: Upload the product documents

1. Download the
   [Contoso product files](https://github.com/MicrosoftLearning/mslearn-ai-agents/raw/main/Labfiles/04-integrate-agent-with-foundry-iq/data/contoso-products.zip).
2. Extract the ZIP file. It contains three product PDF documents.
3. In the Azure portal, create a Storage account in the same resource group and
   region as the project.
4. Use Standard performance and locally redundant storage.
5. Create a blob container named `contosoproducts`.
6. Upload all three extracted PDF files.

## Task 5: Configure the Foundry IQ knowledge base

1. Open the Azure AI Search resource.
2. Under **Security + networking** > **Keys**, set API access control to **Both**.
3. Return to Foundry, refresh the page, and open **Knowledge**.
4. Select **Create a knowledge base** and choose **Azure Blob Storage**.
5. Configure the knowledge source:

```text
Name: ks-contosoproducts
Description: Contoso product catalog items
Container: contosoproducts
Authentication: API Key
Content extraction mode: minimal
Embedding model: available embedding deployment, typically text-embedding-3-small
Chat completions model: available chat deployment, typically gpt-5
```

6. Create the source, select the chat completion model for the knowledge base,
   and save it.
7. Refresh until the knowledge source status is **Active**.
8. From **Knowledge** > **Manage** > **Connected resources**, edit the Search
   connection authentication and save one of the Azure AI Search keys.

Key authentication follows the Microsoft exercise. For a production solution,
prefer identity-based authentication and least-privilege RBAC when supported.

## Task 6: Connect and test the knowledge base

1. Return to **Build** > **Agents** and open `product-expert-agent`.
2. Add Foundry IQ in the agent's **Knowledge** section.
3. Select the connection and knowledge base created earlier.
4. Test questions such as:

```text
What types of tents does Contoso offer?
Tell me about which backpacks are available in XL.
What camping accessories are available?
```

Verify that answers use product information and provide citations or references
when available. Record the agent name and project endpoint for the Python app.

## Task 7: Require approval for knowledge lookups

The Foundry portal enables the knowledge tool without approval by default. The lab
uses the **Foundry Toolkit for VS Code** to change this behavior.

1. Install Microsoft's **Foundry Toolkit** extension in VS Code.
2. Sign in and set the Foundry project as the default project.
3. Under **Prompt Agents**, open `product-expert-agent` in Agent Builder.
4. In **Tools**, locate the tool whose name begins with `kb-knowledgebase`.
5. Open its ellipsis menu and select **Ask for approval for all tools**.
6. Save the change.

The portal may also add Web Search or show a separate Azure AI Search tool. The
approval must be configured on the `kb-knowledgebase...` tool because that is the
tool used for Foundry IQ retrieval.

## Task 8: Prepare the Python application

The official starter files are located in:

```text
Labfiles/04-integrate-agent-with-foundry-iq/Python
```

They include:

```text
.env
agent_client.py
requirements.txt
```

Configure `.env`:

```dotenv
PROJECT_ENDPOINT=https://YOUR-FOUNDRY-RESOURCE.services.ai.azure.com/api/projects/YOUR-PROJECT
AGENT_NAME=product-expert-agent
```

The official requirements are:

```text
azure-ai-projects==2.3.0
azure-identity
python-dotenv
openai<3
```

`openai<3` is pinned because the exercise version of `azure-ai-projects` expects
the earlier HTTP client dependency.

## Task 9: Understand the Python integration

The completed `agent_client.py` performs these operations:

1. Loads `PROJECT_ENDPOINT` and `AGENT_NAME` from `.env`.
2. Authenticates with `DefaultAzureCredential`.
3. Creates an `AIProjectClient` for the Foundry project.
4. Gets the OpenAI client from the project client.
5. Retrieves the saved agent by name.
6. Creates a conversation using `conversations.create()`.
7. Adds user messages with `conversations.items.create()`.
8. Calls `responses.create()` with an `agent_reference`.
9. Detects every `mcp_approval_request` returned by the agent.
10. Shows the server and tool arguments, then asks the user to approve or deny.
11. Adds an `mcp_approval_response` to the conversation.
12. Repeats until no approval requests remain, then displays the answer.
13. Stores client-side history for the `history` command.

The approval logic must use a loop because an agent may request no approvals, one
approval, or multiple approvals during a single user turn.

The official exercise uses synchronous `responses.create()` calls. Streaming is
not part of the provided starter implementation and should be treated as an
optional enhancement rather than a required lab result.

## Task 10: Create the virtual environment

Open a VS Code PowerShell terminal in the Python application folder:

```powershell
py -3.13 -m venv labenv
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
.\labenv\Scripts\Activate.ps1
python -m pip install --upgrade pip
pip install -r requirements.txt
```

Sign in to Azure:

```powershell
az login
az account show
```

If multiple tenants are available, use `az login --tenant <tenant-id>` and select
the subscription containing the Foundry project.

## Task 11: Run and test the application

Run:

```powershell
python agent_client.py
```

Test these scenarios:

```text
What types of outdoor products does Contoso offer?
Tell me about the weatherproof features of your tents.
What's the difference between your daypacks and expedition backpacks?
What camping accessories would you recommend for a weekend hiking trip?
How much do those items typically cost?
```

When the application displays an approval request, review the server and tool
arguments and enter `yes` to permit the knowledge lookup. Use `history` to display
the conversation and `quit` to exit.

## Validation checklist

- The Python client connects to `product-expert-agent` by name.
- A conversation is created and reused for follow-up questions.
- The agent requests approval through `mcp_approval_request` before retrieval.
- Approving creates an `mcp_approval_response` and permits the lookup.
- Denying the request does not silently execute the knowledge lookup.
- Answers are based on the three Contoso product PDFs.
- Citations or source references are shown when returned by the service.
- `history` displays the client-side conversation history.
- Errors are handled without exposing secrets.

## Expected outcome

You will have a Python conversational application that calls a saved Microsoft
Foundry agent. The agent searches a Foundry IQ knowledge base backed by Azure AI
Search and Contoso PDFs in Azure Blob Storage. Users remain in control of external
knowledge access through MCP approval prompts, and answers are grounded in the
configured product content.

## Clean up

When the exercise is complete, delete the lab resource group if the resources are
no longer required. This removes the Foundry, Azure AI Search, and Storage
resources and prevents unnecessary charges.
