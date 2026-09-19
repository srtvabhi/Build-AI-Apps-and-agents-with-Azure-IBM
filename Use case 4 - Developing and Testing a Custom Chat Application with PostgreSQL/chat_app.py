"""Terminal chat agent for querying Azure Database for PostgreSQL."""

from __future__ import annotations

import json
import os
from pathlib import Path
from typing import Any

from dotenv import load_dotenv
from openai import OpenAI

from database import get_database_schema, run_read_only_query


APP_DIRECTORY = Path(__file__).resolve().parent
INSTRUCTIONS_FILE = APP_DIRECTORY / "prompts" / "system_instructions.txt"
MAX_TOOL_ROUNDS = 6

TOOLS = [
    {
        "type": "function",
        "name": "get_database_schema",
        "description": (
            "Inspect available PostgreSQL schemas, tables, columns, and data types. "
            "Call this before writing SQL when the schema is not already known."
        ),
        "parameters": {"type": "object", "properties": {}, "additionalProperties": False},
        "strict": True,
    },
    {
        "type": "function",
        "name": "run_read_only_query",
        "description": (
            "Run one read-only PostgreSQL SELECT query. Results are time-limited "
            "and capped to a safe number of rows."
        ),
        "parameters": {
            "type": "object",
            "properties": {
                "query": {
                    "type": "string",
                    "description": "One PostgreSQL SELECT statement using the inspected schema.",
                }
            },
            "required": ["query"],
            "additionalProperties": False,
        },
        "strict": True,
    },
]


def required_environment(name: str) -> str:
    value = os.getenv(name, "").strip()
    if not value:
        raise RuntimeError(f"Missing required environment variable: {name}")
    return value


class FoundryPostgresAgent:
    def __init__(self) -> None:
        endpoint = required_environment("AZURE_OPENAI_ENDPOINT").rstrip("/")
        self.deployment = os.getenv("AZURE_OPENAI_DEPLOYMENT", "gpt-5").strip()
        self.client = OpenAI(
            base_url=endpoint,
            api_key=required_environment("AZURE_OPENAI_API_KEY"),
        )
        self.instructions = INSTRUCTIONS_FILE.read_text(encoding="utf-8")
        self.previous_response_id: str | None = None

    def reset(self) -> None:
        self.previous_response_id = None

    @staticmethod
    def _call_tool(name: str, arguments: dict[str, Any]) -> dict[str, Any]:
        if name == "get_database_schema":
            return get_database_schema()
        if name == "run_read_only_query":
            return run_read_only_query(arguments["query"])
        raise ValueError(f"Unknown tool requested: {name}")

    def ask(self, user_message: str) -> str:
        request: dict[str, Any] = {
            "model": self.deployment,
            "instructions": self.instructions,
            "input": user_message,
            "tools": TOOLS,
        }
        if self.previous_response_id:
            request["previous_response_id"] = self.previous_response_id

        response = self.client.responses.create(**request)

        for _ in range(MAX_TOOL_ROUNDS):
            tool_calls = [item for item in response.output if item.type == "function_call"]
            if not tool_calls:
                self.previous_response_id = response.id
                return response.output_text.strip() or "The agent returned no text."

            tool_outputs = []
            for call in tool_calls:
                try:
                    arguments = json.loads(call.arguments or "{}")
                    result = self._call_tool(call.name, arguments)
                except Exception as error:
                    result = {"error": str(error)}

                tool_outputs.append(
                    {
                        "type": "function_call_output",
                        "call_id": call.call_id,
                        "output": json.dumps(result),
                    }
                )

            response = self.client.responses.create(
                model=self.deployment,
                instructions=self.instructions,
                previous_response_id=response.id,
                input=tool_outputs,
                tools=TOOLS,
            )

        raise RuntimeError("The agent exceeded the maximum number of tool rounds.")


def main() -> None:
    load_dotenv(APP_DIRECTORY / ".env")

    print("\nFoundry PostgreSQL Chat")
    print("Ask a question about your database in plain English.")
    print("Commands: /schema, /reset, /exit\n")

    try:
        agent = FoundryPostgresAgent()
    except Exception as error:
        print(f"Configuration error: {error}")
        print("Copy .env.example to .env and provide the required credentials.")
        return

    while True:
        try:
            user_message = input("You > ").strip()
        except (EOFError, KeyboardInterrupt):
            print("\nGoodbye.")
            break

        if not user_message:
            continue
        if user_message.lower() in {"/exit", "exit", "quit"}:
            print("Goodbye.")
            break
        if user_message.lower() == "/reset":
            agent.reset()
            print("Conversation history cleared.\n")
            continue
        if user_message.lower() == "/schema":
            try:
                print(json.dumps(get_database_schema(), indent=2))
            except Exception as error:
                print(f"Database error: {error}")
            print()
            continue

        try:
            answer = agent.ask(user_message)
            print(f"\nAgent > {answer}\n")
        except Exception as error:
            print(f"\nRequest failed: {error}\n")


if __name__ == "__main__":
    main()
