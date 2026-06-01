"""
SQLite schema migration support for the smart_task system.
"""

from __future__ import annotations

import sqlite3

from smart_task.schema.ddl import (
    CREATE_TICKETS_TABLE_SQL,
    CREATE_WAVES_TABLE_SQL,
    CREATE_MAPPINGS_TABLE_SQL,
    INDEX_SQL_STATEMENTS,
)


CURRENT_SCHEMA_VERSION: int = 1


def ensure_schema(conn: sqlite3.Connection) -> None:
    """Idempotently create all tables, indexes, and run pending migrations."""
    conn.execute("""
        CREATE TABLE IF NOT EXISTS schema_version (
            version INTEGER PRIMARY KEY,
            applied_at TEXT NOT NULL DEFAULT (datetime('now')),
            description TEXT NOT NULL DEFAULT ''
        )
    """)
    conn.commit()
    cursor = conn.execute("SELECT COALESCE(MAX(version), 0) FROM schema_version")
    current_version = cursor.fetchone()[0]

    if current_version < CURRENT_SCHEMA_VERSION:
        _apply_migrations(conn, current_version)
    elif current_version == 0:
        # No migrations run yet, but we need to ensure tables exist
        _apply_migrations(conn, 0)


def _apply_migrations(conn: sqlite3.Connection, from_version: int) -> None:
    """Apply schema migrations sequentially from from_version to CURRENT_SCHEMA_VERSION."""
    migrations: dict[int, list[str]] = {
        1: [
            CREATE_TICKETS_TABLE_SQL,
            CREATE_WAVES_TABLE_SQL,
            CREATE_MAPPINGS_TABLE_SQL,
            *INDEX_SQL_STATEMENTS,
        ],
    }

    for version in range(from_version + 1, CURRENT_SCHEMA_VERSION + 1):
        statements = migrations.get(version, [])
        for stmt in statements:
            conn.execute(stmt)
        conn.execute(
            "INSERT INTO schema_version (version, description) VALUES (?, ?)",
            (version, f"Migration v{version}"),
        )
    conn.commit()
