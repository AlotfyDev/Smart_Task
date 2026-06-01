# Wave 3: json_schema.py + parser.py + repository.py

## Dependency
- Depends on: Wave 2 (schema.py + models.py)
- Required by: Wave 4 (importer + exporter + wave_manager)

## Targets
- `smart_task/json_schema/` (package: `__init__.py` + `schemas.py` + `validators.py` + `compatibility.py`)
- `smart_task/parser/` (package: `__init__.py` + `parsing.py` + `front_matter.py`)
- `smart_task/repository/` (package: `__init__.py` + `crud.py` + `queries.py` + `connection.py`)

## Scope

Implement JSON Schema validation for artifacts, JSON ↔ dataclass parsing, and the SQLite repository layer with full CRUD.

## json_schema.py

### `TICKET_JSON_SCHEMA: dict`

JSON Schema (draft-07) for ticket artifacts. Must match `MicroTaskTicket` fields exactly:

```json
{
  "$schema": "http://json-schema.org/draft-07/schema#",
  "title": "MicroTaskTicket",
  "type": "object",
  "properties": {
    "id":                { "type": "string", "pattern": "^TASK-[A-Z]{2,4}-\\d{3}$" },
    "title":             { "type": "string" },
    "objective":         { "type": "string" },
    "spec_context":      { "type": "string" },
    "dependencies":      { "type": "array", "items": { "type": "string" } },
    "file_targets":      { "type": "array", "items": { "type": "string" } },
    "acceptance_criteria": { "type": "array", "items": { "type": "string" } },
    "verification_method": { "type": "string" },
    "phase":             { "type": "integer", "enum": [1, 2, 3] },
    "priority":          { "type": "string", "enum": ["High", "Medium", "Low"] },
    "estimated_effort":  { "type": "string", "enum": ["S", "M", "L", "XL"] },
    "tags":              { "type": "array", "items": { "type": "string" } },
    "wave_id":           { "type": "string" },
    "assignee":          { "type": "string" },
    "status":            { "type": "string", "enum": ["pending", "in_progress", "completed", "blocked", "cancelled"] }
  },
  "required": ["id", "title", "objective", "phase", "priority", "estimated_effort", "status"]
}
```

### `WAVE_JSON_SCHEMA: dict`

JSON Schema for wave artifacts.

### `MAPPING_JSON_SCHEMA: dict`

JSON Schema for topic→ticket mapping files.

### `validate_ticket(data: dict) -> tuple[bool, list[str]]`

Returns `(is_valid, error_messages)`. Uses `jsonschema.validate()` or manual validation (don't add `jsonschema` dependency unless needed — manual dict checking is fine).

### `validate_wave(data: dict) -> tuple[bool, list[str]]`

### `validate_mapping(data: dict) -> tuple[bool, list[str]]`

## parser.py

### `class TicketParser`

| Method | Signature | Description |
|--------|-----------|-------------|
| `parse_ticket_file` | `(path: Path) -> MicroTaskTicket` | Reads JSON file, validates, returns dataclass |
| `parse_wave_file` | `(path: Path) -> TaskWave` | Same for wave |
| `serialize_ticket` | `(ticket: MicroTaskTicket) -> dict` | Dataclass → validated dict |
| `serialize_wave` | `(wave: TaskWave) -> dict` | Same for wave |
| `write_artifact` | `(path: Path, data: dict) -> None` | Writes JSON to file (pretty-printed, utf-8) |

### Error handling
- File not found → raise `FileNotFoundError`
- Invalid JSON → raise `json.JSONDecodeError`
- Schema validation failure → raise `ValueError` with concatenated error messages

## repository.py

### `class TicketRepository`

| Method | Signature | Description |
|--------|-----------|-------------|
| `__init__` | `(db_path: Path, auto_create: bool = True)` | Connect, optionally ensure schema |
| `insert_ticket` | `(ticket: MicroTaskTicket) -> None` | INSERT INTO micro_task_tickets |
| `insert_tickets_batch` | `(tickets: list[MicroTaskTicket]) -> int` | Batch insert in transaction, returns count |
| `insert_wave` | `(wave: TaskWave) -> None` | INSERT INTO task_waves |
| `get_ticket` | `(ticket_id: str) -> MicroTaskTicket \| None` | SELECT by id |
| `get_wave` | `(wave_id: str) -> TaskWave \| None` | SELECT by id |
| `list_tickets` | `(phase: int \| None, status: str \| None, wave_id: str \| None) -> list[MicroTaskTicket]` | Filtered query |
| `list_waves` | `(phase: int \| None, status: str \| None) -> list[TaskWave]` | Filtered query |
| `update_ticket_status` | `(ticket_id: str, status: str, **kwargs) -> None` | UPDATE status + optional fields (review_notes, blocker_reason, completed_at) |
| `update_wave_status` | `(wave_id: str, status: str) -> None` | UPDATE status |
| `delete_ticket` | `(ticket_id: str) -> bool` | DELETE by id, returns True if deleted |
| `count_tickets` | `(phase: int \| None, status: str \| None) -> int` | COUNT query |
| `get_ready_tickets` | `(phase: int, limit: int = 10) -> list[MicroTaskTicket]` | Tickets whose dependencies' statuses are all 'completed', ordered by priority |
| `close` | `() -> None` | Close connection |
| `__enter__` / `__exit__` | | Context manager |

### Batch insert implementation

```python
def insert_tickets_batch(self, tickets: list[MicroTaskTicket]) -> int:
    self._conn.execute("BEGIN")
    try:
        rows = [t.to_row() for t in tickets]
        self._conn.executemany("INSERT OR IGNORE INTO micro_task_tickets (...) VALUES (?, ?, ...)", rows)
        self._conn.execute("COMMIT")
    except Exception:
        self._conn.execute("ROLLBACK")
        raise
    return len(rows)
```

### `get_ready_tickets` — dependency-aware query

Reads `dependencies` JSON field, parses it, checks if all listed ticket IDs have `status = 'completed'`.

## Verification

| # | Criterion |
|---|-----------|
| 1 | All 3 files importable: `python -c "from smart_task.json_schema import *; from smart_task.parser import *; from smart_task.repository import *"` |
| 2 | `TICKET_JSON_SCHEMA` validates a well-formed ticket dict, rejects a malformed one |
| 3 | `TicketParser.parse_ticket_file` round-trips: serialize → write → read → same dict |
| 4 | `TicketRepository` insert + get + list + update cycle works on a temp DB |
| 5 | `get_ready_tickets` correctly filters by dependency completion |

## Delivery
Three packages (11 files total):
- `smart_task/json_schema/` — `__init__.py`, `schemas.py`, `validators.py`, `compatibility.py`
- `smart_task/parser/` — `__init__.py`, `parsing.py`, `front_matter.py`
- `smart_task/repository/` — `__init__.py`, `crud.py`, `queries.py`, `connection.py`
