# Use Case 4: Custom Chat Application with PostgreSQL

## Objective

Develop and test a terminal-based custom chat application that uses a GPT-5
deployment in Microsoft Foundry to translate business questions into safe,
read-only PostgreSQL queries and explain the database results.

## Architecture

```text
User in the VS Code terminal
    |
    v
Python chat application
    |
    v
GPT-5 deployment through the Azure OpenAI v1 endpoint
    |
    +-- get_database_schema tool
    |       |
    |       v
    |   PostgreSQL table and column metadata
    |
    +-- run_read_only_query tool
            |
            v
        SQL validation, read-only transaction,
        statement timeout, and row limit
            |
            v
Azure Database for PostgreSQL over TLS
    |
    v
Grounded answer and SQL displayed in the terminal
```

## Project files

```text
chat_app.py                     Terminal chat and GPT-5 tool-calling loop
database.py                     PostgreSQL schema and read-only query tools
prompts/system_instructions.txt Agent behavior and safety instructions
tests/test_database.py          SQL safety tests
sample_questions.txt            Example business questions
requirements.txt                Python dependencies
.env.example                    Configuration template without secrets
.gitignore                      Prevents credentials and local files in Git
```

## Security design

- Database credentials and the model key are loaded from a local `.env` file.
- `.env` is ignored by Git and must never be uploaded.
- Generated SQL is restricted to one `SELECT` statement.
- Every query runs inside a PostgreSQL read-only transaction.
- Query runtime and returned rows are limited.
- Use a dedicated PostgreSQL login with `CONNECT`, `USAGE`, and `SELECT` only.
- Do not use a database administrator account outside a short-lived lab.

The controls in the application provide defense in depth, but database
permissions remain the strongest boundary.

## 1. Open the project in VS Code

Open a PowerShell terminal in this folder:

```powershell
cd "Use case 4 - Developing and Testing a Custom Chat Application with PostgreSQL"
```

## 2. Create and activate a virtual environment

```powershell
py -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
pip install -r requirements.txt
```

If script activation is blocked for the current PowerShell session:

```powershell
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
.\.venv\Scripts\Activate.ps1
```

## 3. Configure credentials locally

Create the local configuration file:

```powershell
Copy-Item .env.example .env
```

Open `.env` in VS Code and replace only these placeholders:

```text
AZURE_OPENAI_API_KEY=your-real-model-key
PGPASSWORD=your-real-database-password
```

The provided Azure endpoint, GPT-5 deployment name, PostgreSQL host, port,
database, username, and TLS mode are already represented in `.env.example`.
Do not add quotation marks unless they are part of the actual credential.

## 4. Test database connectivity and schema access

Start the application:

```powershell
python chat_app.py
```

At the prompt, enter:

```text
/schema
```

A successful connection displays the available user tables and columns. If it
fails, confirm that Azure PostgreSQL networking permits your public IP address,
the password is correct, and TLS is required.

## 5. Chat with the database

Example:

```text
You > Show the five tables with the most rows.

Agent > [Explanation based on the returned database result]
SQL used: SELECT ...
```

Useful commands:

```text
/schema  Display database schema without using the model
/reset   Start a new model conversation
/exit    Close the application
```

## 6. Run tests

```powershell
pytest -q
```

The automated tests confirm that read-only queries and CTEs are accepted while
updates, deletes, DDL, empty SQL, and multiple statements are rejected.

## Expected result

The user can ask a business question in plain English from the VS Code terminal.
GPT-5 inspects the schema, produces a read-only PostgreSQL query, executes it
through the controlled database tool, and prints a grounded explanation plus
the SQL used. The application never sends the database password to the model.
