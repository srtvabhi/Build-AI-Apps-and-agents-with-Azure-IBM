"""Minimal GPT-5 chat application for Azure Database for PostgreSQL."""

import json

from openai import OpenAI

from database import get_database_schema, run_read_only_query


# Replace the two placeholders locally before running the application.
AZURE_OPENAI_ENDPOINT = "https://kyndrl77777777.openai.azure.com/openai/v1"
AZURE_OPENAI_API_KEY = "PASTE_YOUR_AZURE_OPENAI_KEY_HERE"
AZURE_OPENAI_DEPLOYMENT = "gpt-5"

POSTGRES_CONFIG = {
    "host": "pg-foundry-demo-001.postgres.database.azure.com",
    "port": 5432,
    "dbname": "postgres",
    "user": "pgadmin",
    "password": "PASTE_YOUR_POSTGRES_PASSWORD_HERE",
    "sslmode": "require",
}

INSTRUCTIONS = """
You are a PostgreSQL data assistant. Answer business questions using the
connected database. Inspect the schema before querying it. Use only SELECT
queries, never invent tables or results, avoid unnecessary personal data, and
include the SQL used in the final answer. Never reveal credentials.
"""

TOOLS = [
    {
        "type": "function",
        "name": "get_database_schema",
        "description": "Get PostgreSQL tables, columns, and data types.",
        "parameters": {"type": "object", "properties": {}, "additionalProperties": False},
        "strict": True,
    },
    {
        "type": "function",
        "name": "run_read_only_query",
        "description": "Run one read-only PostgreSQL SELECT query.",
        "parameters": {
            "type": "object",
            "properties": {
                "query": {"type": "string", "description": "A PostgreSQL SELECT query."}
            },
            "required": ["query"],
            "additionalProperties": False,
        },
        "strict": True,
    },
]


def call_tool(name, arguments):
    if name == "get_database_schema":
        return get_database_schema(POSTGRES_CONFIG)
    if name == "run_read_only_query":
        return run_read_only_query(POSTGRES_CONFIG, arguments["query"])
    return {"error": "Unknown tool"}


def get_chat_response(client, question, previous_response_id=None):
    request = {
        "model": AZURE_OPENAI_DEPLOYMENT,
        "instructions": INSTRUCTIONS,
        "input": question,
        "tools": TOOLS,
    }
    if previous_response_id:
        request["previous_response_id"] = previous_response_id

    response = client.responses.create(**request)

    for _ in range(5):
        tool_calls = [item for item in response.output if item.type == "function_call"]
        if not tool_calls:
            return response.output_text, response.id

        outputs = []
        for tool_call in tool_calls:
            try:
                result = call_tool(tool_call.name, json.loads(tool_call.arguments or "{}"))
            except Exception as error:
                result = {"error": str(error)}

            outputs.append(
                {
                    "type": "function_call_output",
                    "call_id": tool_call.call_id,
                    "output": json.dumps(result, default=str),
                }
            )

        response = client.responses.create(
            model=AZURE_OPENAI_DEPLOYMENT,
            instructions=INSTRUCTIONS,
            previous_response_id=response.id,
            input=outputs,
            tools=TOOLS,
        )

    return "The request exceeded the tool-call limit.", response.id


def main():
    if "PASTE_YOUR" in AZURE_OPENAI_API_KEY or "PASTE_YOUR" in POSTGRES_CONFIG["password"]:
        print("Add your Azure OpenAI key and PostgreSQL password in chat_app.py.")
        return

    client = OpenAI(base_url=AZURE_OPENAI_ENDPOINT, api_key=AZURE_OPENAI_API_KEY)
    previous_response_id = None

    print("PostgreSQL GPT-5 Chat (type 'exit' to stop)\n")
    while True:
        question = input("You > ").strip()
        if question.lower() in {"exit", "quit"}:
            break
        if not question:
            continue

        try:
            answer, previous_response_id = get_chat_response(
                client, question, previous_response_id
            )
            print(f"\nAssistant > {answer}\n")
        except Exception as error:
            print(f"\nError: {error}\n")


if __name__ == "__main__":
    main()
