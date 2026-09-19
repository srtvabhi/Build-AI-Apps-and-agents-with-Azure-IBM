"""Safe PostgreSQL tools exposed to the chat agent."""

from __future__ import annotations

import os
import re
from contextlib import contextmanager
from datetime import date, datetime
from decimal import Decimal
from typing import Any, Iterator
from uuid import UUID

import psycopg
import sqlparse
from psycopg.rows import dict_row


FORBIDDEN_SQL = re.compile(
    r"\b(ALTER|ANALYZE|CALL|COMMENT|COPY|CREATE|DELETE|DO|DROP|EXECUTE|"
    r"GRANT|INSERT|MERGE|REFRESH|REINDEX|REVOKE|TRUNCATE|UPDATE|VACUUM)\b",
    re.IGNORECASE,
)


def _required(name: str) -> str:
    value = os.getenv(name, "").strip()
    if not value:
        raise RuntimeError(f"Missing required environment variable: {name}")
    return value


def _positive_int(name: str, default: int, maximum: int) -> int:
    raw_value = os.getenv(name, str(default))
    try:
        value = int(raw_value)
    except ValueError as exc:
        raise RuntimeError(f"{name} must be an integer") from exc
    if value < 1 or value > maximum:
        raise RuntimeError(f"{name} must be between 1 and {maximum}")
    return value


@contextmanager
def database_connection() -> Iterator[psycopg.Connection]:
    """Open a TLS PostgreSQL connection without exposing its credentials."""
    connection = psycopg.connect(
        host=_required("PGHOST"),
        port=_positive_int("PGPORT", 5432, 65535),
        dbname=_required("PGDATABASE"),
        user=_required("PGUSER"),
        password=_required("PGPASSWORD"),
        sslmode=os.getenv("PGSSLMODE", "require"),
        connect_timeout=10,
        row_factory=dict_row,
    )
    try:
        yield connection
    finally:
        connection.close()


def validate_read_only_sql(query: str) -> str:
    """Accept one SELECT statement and reject mutating or administrative SQL."""
    cleaned = query.strip()
    if not cleaned:
        raise ValueError("The SQL query is empty.")

    statements = [statement for statement in sqlparse.parse(cleaned) if str(statement).strip()]
    if len(statements) != 1:
        raise ValueError("Only one SQL statement is allowed per request.")

    statement = statements[0]
    if statement.get_type() != "SELECT":
        raise ValueError("Only SELECT queries and read-only CTE queries are allowed.")

    if FORBIDDEN_SQL.search(cleaned):
        raise ValueError("The query contains a prohibited SQL operation.")

    return cleaned.rstrip(";").strip()


def _json_value(value: Any) -> Any:
    if value is None or isinstance(value, (str, int, float, bool)):
        return value
    if isinstance(value, Decimal):
        return str(value)
    if isinstance(value, (date, datetime)):
        return value.isoformat()
    if isinstance(value, UUID):
        return str(value)
    if isinstance(value, (bytes, bytearray, memoryview)):
        return f"<binary data: {len(value)} bytes>"
    return str(value)


def get_database_schema() -> dict[str, Any]:
    """Return user-table and column metadata without returning business data."""
    schema_query = """
        SELECT
            c.table_schema,
            c.table_name,
            c.column_name,
            c.data_type,
            c.is_nullable
        FROM information_schema.columns AS c
        WHERE c.table_schema NOT IN ('pg_catalog', 'information_schema')
        ORDER BY c.table_schema, c.table_name, c.ordinal_position
    """

    with database_connection() as connection:
        with connection.transaction():
            connection.execute("SET TRANSACTION READ ONLY")
            connection.execute(
                "SELECT set_config('statement_timeout', %s, true)",
                (str(_positive_int("DB_STATEMENT_TIMEOUT_MS", 10000, 60000)),),
            )
            rows = connection.execute(schema_query).fetchall()

    tables: dict[str, list[dict[str, str]]] = {}
    for row in rows:
        table_name = f"{row['table_schema']}.{row['table_name']}"
        tables.setdefault(table_name, []).append(
            {
                "column": row["column_name"],
                "type": row["data_type"],
                "nullable": row["is_nullable"],
            }
        )

    return {"table_count": len(tables), "tables": tables}


def run_read_only_query(query: str) -> dict[str, Any]:
    """Execute model-generated SQL inside a read-only, time-limited transaction."""
    safe_query = validate_read_only_sql(query)
    maximum_rows = _positive_int("MAX_QUERY_ROWS", 100, 500)
    wrapped_query = f"SELECT * FROM ({safe_query}) AS agent_result LIMIT %s"

    with database_connection() as connection:
        with connection.transaction():
            connection.execute("SET TRANSACTION READ ONLY")
            connection.execute(
                "SELECT set_config('statement_timeout', %s, true)",
                (str(_positive_int("DB_STATEMENT_TIMEOUT_MS", 10000, 60000)),),
            )
            cursor = connection.execute(wrapped_query, (maximum_rows + 1,))
            rows = cursor.fetchall()

    truncated = len(rows) > maximum_rows
    rows = rows[:maximum_rows]
    serializable_rows = [
        {column: _json_value(value) for column, value in row.items()} for row in rows
    ]
    return {
        "sql": safe_query,
        "row_count": len(serializable_rows),
        "truncated": truncated,
        "rows": serializable_rows,
    }
