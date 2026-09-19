"""Minimal read-only PostgreSQL tools used by chat_app.py."""

import re

import psycopg
import sqlparse
from psycopg.rows import dict_row


BLOCKED_SQL = re.compile(
    r"\b(ALTER|CALL|COPY|CREATE|DELETE|DROP|GRANT|INSERT|MERGE|REVOKE|"
    r"TRUNCATE|UPDATE|VACUUM)\b",
    re.IGNORECASE,
)


def validate_read_only_sql(query):
    query = query.strip()
    statements = [item for item in sqlparse.parse(query) if str(item).strip()]

    if len(statements) != 1:
        raise ValueError("Only one SQL statement is allowed.")
    if statements[0].get_type() != "SELECT":
        raise ValueError("Only SELECT queries are allowed.")
    if BLOCKED_SQL.search(query):
        raise ValueError("The query contains a blocked SQL operation.")

    return query.rstrip(";").strip()


def connect(config):
    return psycopg.connect(
        **config,
        connect_timeout=10,
        row_factory=dict_row,
    )


def get_database_schema(config):
    sql = """
        SELECT table_schema, table_name, column_name, data_type
        FROM information_schema.columns
        WHERE table_schema NOT IN ('pg_catalog', 'information_schema')
        ORDER BY table_schema, table_name, ordinal_position
    """

    with connect(config) as connection:
        with connection.transaction():
            connection.execute("SET TRANSACTION READ ONLY")
            rows = connection.execute(sql).fetchall()

    tables = {}
    for row in rows:
        table = f"{row['table_schema']}.{row['table_name']}"
        tables.setdefault(table, []).append(
            {"column": row["column_name"], "type": row["data_type"]}
        )
    return {"tables": tables}


def run_read_only_query(config, query):
    query = validate_read_only_sql(query)
    limited_query = f"SELECT * FROM ({query}) AS result LIMIT 101"

    with connect(config) as connection:
        with connection.transaction():
            connection.execute("SET TRANSACTION READ ONLY")
            connection.execute("SET LOCAL statement_timeout = '10s'")
            rows = connection.execute(limited_query).fetchall()

    return {
        "sql": query,
        "rows": rows[:100],
        "row_count": min(len(rows), 100),
        "truncated": len(rows) > 100,
    }
