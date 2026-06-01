"""
SQL DDL strings for the smart_task database schema.

This module is standalone — no imports from smart_task.xxx.
"""

from __future__ import annotations


CREATE_TICKETS_TABLE_SQL: str = """
CREATE TABLE IF NOT EXISTS micro_task_tickets (
    id                  TEXT PRIMARY KEY,

    -- Traceability
    source_spec         TEXT NOT NULL,
    source_topic_file   TEXT NOT NULL,
    source_line_range   TEXT NOT NULL,
    topic_sequence      INTEGER NOT NULL DEFAULT 1,

    -- Content
    title               TEXT NOT NULL,
    objective           TEXT NOT NULL,
    spec_context        TEXT NOT NULL,

    -- Dependencies & Targets
    dependencies        TEXT NOT NULL DEFAULT '[]',
    file_targets        TEXT NOT NULL DEFAULT '[]',

    -- Verification
    acceptance_criteria TEXT NOT NULL DEFAULT '[]',
    verification_method TEXT NOT NULL DEFAULT '',

    -- Review
    review_notes        TEXT,
    blocker_reason      TEXT,

    -- Organization
    phase               INTEGER NOT NULL CHECK (phase IN (1, 2, 3)),
    priority            TEXT NOT NULL CHECK (priority IN ('High', 'Medium', 'Low')),
    estimated_effort    TEXT NOT NULL CHECK (estimated_effort IN ('S', 'M', 'L', 'XL')),
    tags                TEXT NOT NULL DEFAULT '[]',

    -- Assignment
    assignee            TEXT,
    wave_id             TEXT,

    -- Lifecycle
    status              TEXT NOT NULL DEFAULT 'pending'
                        CHECK (status IN ('pending', 'in_progress', 'completed', 'blocked', 'cancelled')),
    created_at          TEXT NOT NULL DEFAULT (datetime('now')),
    updated_at          TEXT NOT NULL DEFAULT (datetime('now')),
    completed_at        TEXT
);
"""

CREATE_WAVES_TABLE_SQL: str = """
CREATE TABLE IF NOT EXISTS task_waves (
    id              TEXT PRIMARY KEY,
    phase           INTEGER NOT NULL CHECK (phase IN (1, 2, 3)),
    description     TEXT NOT NULL,
    ticket_count    INTEGER NOT NULL DEFAULT 0,
    status          TEXT NOT NULL DEFAULT 'pending'
                    CHECK (status IN ('pending', 'active', 'completed')),
    created_at      TEXT NOT NULL DEFAULT (datetime('now')),
    completed_at    TEXT
);
"""

CREATE_MAPPINGS_TABLE_SQL: str = """
CREATE TABLE IF NOT EXISTS topic_to_ticket_mapping (
    id              INTEGER PRIMARY KEY AUTOINCREMENT,
    source_topic_file TEXT NOT NULL,
    sequence        INTEGER NOT NULL,
    title_template  TEXT NOT NULL,
    objective_template TEXT NOT NULL,
    phase           INTEGER NOT NULL CHECK (phase IN (1, 2, 3)),
    effort          TEXT NOT NULL CHECK (effort IN ('S', 'M', 'L', 'XL')),
    tags            TEXT NOT NULL DEFAULT '[]',
    UNIQUE(source_topic_file, sequence)
);
"""

INDEXES_SQL: str = """
CREATE INDEX IF NOT EXISTS idx_tickets_status ON micro_task_tickets(status);
CREATE INDEX IF NOT EXISTS idx_tickets_phase ON micro_task_tickets(phase);
CREATE INDEX IF NOT EXISTS idx_tickets_wave ON micro_task_tickets(wave_id);
CREATE INDEX IF NOT EXISTS idx_tickets_priority ON micro_task_tickets(priority);
CREATE INDEX IF NOT EXISTS idx_waves_phase ON task_waves(phase);
CREATE INDEX IF NOT EXISTS idx_mapping_topic ON topic_to_ticket_mapping(source_topic_file);
"""

INDEX_SQL_STATEMENTS: list[str] = [
    "CREATE INDEX IF NOT EXISTS idx_tickets_status ON micro_task_tickets(status)",
    "CREATE INDEX IF NOT EXISTS idx_tickets_phase ON micro_task_tickets(phase)",
    "CREATE INDEX IF NOT EXISTS idx_tickets_wave ON micro_task_tickets(wave_id)",
    "CREATE INDEX IF NOT EXISTS idx_tickets_priority ON micro_task_tickets(priority)",
    "CREATE INDEX IF NOT EXISTS idx_waves_phase ON task_waves(phase)",
    "CREATE INDEX IF NOT EXISTS idx_mapping_topic ON topic_to_ticket_mapping(source_topic_file)",
]


def get_ddl_statement(table_name: str) -> str:
    """Return the DDL statement for a given table name."""
    table_map = {
        "micro_task_tickets": CREATE_TICKETS_TABLE_SQL,
        "task_waves": CREATE_WAVES_TABLE_SQL,
        "topic_to_ticket_mapping": CREATE_MAPPINGS_TABLE_SQL,
    }
    try:
        return table_map[table_name]
    except KeyError:
        raise KeyError(f"Unknown table: {table_name!r}. Expected one of {list(table_map)}") from None
