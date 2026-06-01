"""
SQLite database schema and migration support for the smart_task system.

Exports
-------
- CREATE_TICKETS_TABLE_SQL   : DDL for micro_task_tickets
- CREATE_WAVES_TABLE_SQL     : DDL for task_waves
- CREATE_MAPPINGS_TABLE_SQL  : DDL for topic_to_ticket_mapping
- INDEXES_SQL                : DDL for all indexes
- CURRENT_SCHEMA_VERSION     : integer version constant
- ensure_schema              : idempotent schema initialisation
- _apply_migrations          : sequential migration runner
- get_ddl_statement          : helper to retrieve DDL for a specific table
"""

from smart_task.schema.ddl import (
    CREATE_TICKETS_TABLE_SQL,
    CREATE_WAVES_TABLE_SQL,
    CREATE_MAPPINGS_TABLE_SQL,
    INDEXES_SQL,
    INDEX_SQL_STATEMENTS,
    get_ddl_statement,
)
from smart_task.schema.migration import (
    CURRENT_SCHEMA_VERSION,
    ensure_schema,
    _apply_migrations,
)

__all__ = [
    "CREATE_TICKETS_TABLE_SQL",
    "CREATE_WAVES_TABLE_SQL",
    "CREATE_MAPPINGS_TABLE_SQL",
    "INDEXES_SQL",
    "INDEX_SQL_STATEMENTS",
    "CURRENT_SCHEMA_VERSION",
    "ensure_schema",
    "_apply_migrations",
    "get_ddl_statement",
]
