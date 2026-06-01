# Wave 2: schema.py + models.py

## Dependency
- Depends on: Wave 1 (config.py)
- Required by: Wave 3 (json_schema.py + parser.py + repository.py)

## Targets
- `smart_task/schema.py`
- `smart_task/models.py`

## Scope

Implement the SQL DDL schema and Python dataclass models for the micro-task ticket system. This is the data layer foundation.

## schema.py

### `CREATE_TICKETS_TABLE_SQL`

```sql
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
```

### `CREATE_WAVES_TABLE_SQL`

```sql
CREATE TABLE IF NOT EXISTS task_waves (
    id              TEXT PRIMARY KEY,
    phase           INTEGER NOT NULL,
    description     TEXT NOT NULL,
    ticket_count    INTEGER NOT NULL DEFAULT 0,
    status          TEXT NOT NULL DEFAULT 'pending'
                    CHECK (status IN ('pending', 'active', 'completed')),
    created_at      TEXT NOT NULL DEFAULT (datetime('now')),
    completed_at    TEXT
);
```

### `CREATE_MAPPINGS_TABLE_SQL`

```sql
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
```

### `INDEXES_SQL`

```sql
CREATE INDEX IF NOT EXISTS idx_tickets_status     ON micro_task_tickets(status);
CREATE INDEX IF NOT EXISTS idx_tickets_phase      ON micro_task_tickets(phase);
CREATE INDEX IF NOT EXISTS idx_tickets_wave       ON micro_task_tickets(wave_id);
CREATE INDEX IF NOT EXISTS idx_tickets_priority   ON micro_task_tickets(priority);
CREATE INDEX IF NOT EXISTS idx_waves_phase        ON task_waves(phase);
CREATE INDEX IF NOT EXISTS idx_mapping_topic      ON topic_to_ticket_mapping(source_topic_file);
```

### `ensure_schema(conn: sqlite3.Connection) -> None`

Creates all tables and indexes if they don't exist. Uses `schema_version` table for migration tracking.

### `CURRENT_SCHEMA_VERSION: int = 1`

### `_apply_migrations(conn, from_version: int) -> None`

Sequential migration runner. For v1, creates all tables from scratch.

## models.py

### `class MicroTaskTicket`

Complete dataclass mirroring the SQL schema. Must include:

- `to_dict() -> dict` — for JSON serialization (handles JSON-list fields: json.dumps lists, etc.)
- `from_dict(data: dict) -> MicroTaskTicket` — factory method
- `to_row() -> tuple` — for SQL parameterized insertion (matches column order of the INSERT)
- `validate() -> list[str]` — returns list of validation errors (empty = valid)

### `class TaskWave`

Dataclass for `task_waves` table, same patterns (to_dict, from_dict, to_row, validate).

### `class TopicToTicketMapping`

Dataclass for `topic_to_ticket_mapping` table, same patterns.

All dataclasses must use `@dataclass` decorator with proper type annotations.

## Verification

| # | Criterion |
|---|-----------|
| 1 | `python -c "from smart_task.schema import ensure_schema; from smart_task.models import MicroTaskTicket, TaskWave"` succeeds |
| 2 | `ensure_schema()` creates all 4 tables in an in-memory SQLite DB |
| 3 | All CHECK constraints work on valid/invalid inputs |
| 4 | `MicroTaskTicket.to_dict()` followed by `MicroTaskTicket.from_dict()` round-trips correctly |
| 5 | `MicroTaskTicket.validate()` returns empty list for valid ticket, non-empty for invalid |

## Delivery
Two files: `smart_task/schema.py`, `smart_task/models.py` (both complete)
