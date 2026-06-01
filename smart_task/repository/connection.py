"""
Database connection management and schema initialization.
"""

import sqlite3
from pathlib import Path
from typing import Any

from smart_task.schema import ensure_schema


def get_connection(db_path: Path) -> sqlite3.Connection:
    """Create and return a SQLite connection with proper configuration."""
    conn = sqlite3.connect(str(db_path))
    conn.execute("PRAGMA foreign_keys = ON")
    conn.row_factory = sqlite3.Row
    return conn


def init_database(db_path: Path) -> sqlite3.Connection:
    """
    Initialize database with schema.

    Returns:
        Connection with schema ensured
    """
    conn = get_connection(db_path)
    ensure_schema(conn)
    return conn


class DatabaseConnection:
    """Context manager for database connections."""

    def __init__(self, db_path: Path, auto_create: bool = True) -> None:
        self._db_path = db_path
        self._auto_create = auto_create
        self._conn: sqlite3.Connection | None = None

    def __enter__(self) -> sqlite3.Connection:
        self._conn = init_database(self._db_path) if self._auto_create else get_connection(self._db_path)
        return self._conn

    def __exit__(self, exc_type: Any, exc_val: Any, exc_tb: Any) -> None:
        if self._conn:
            self._conn.close()
            self._conn = None

    @property
    def connection(self) -> sqlite3.Connection | None:
        return self._conn