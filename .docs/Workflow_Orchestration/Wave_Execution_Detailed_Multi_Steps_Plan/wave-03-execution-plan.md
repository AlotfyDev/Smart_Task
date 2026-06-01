# Wave 3 Execution Plan: json_schema.py + parser.py + repository.py

**Generated:** 2026-05-31  
**Status:** READY FOR IMPLEMENTATION  
**Dependency:** Wave 2 (schema.py + models.py) COMPLETE

---

## Configuration

### Path Configuration

Smart task modules use configurable paths via:

| Source | Description |
|--------|-------------|
| CLI `--db-path` | Database file path override |
| CLI `--topic-dir` | Topic files directory |
| CLI `--mappings` | Mapping rules JSON file |
| `SMART_TASK_DB_PATH` env var | Default database location |
| `load_config()` defaults | Standard fallback paths |

---

## Critical Gaps Analysis

### Current State Issues

| Component | Current Implementation | Spec Requirement | Gap |
|-----------|---------------------|-----------------|-----|
| `json_schema/__init__.py` | Stub methods (`return True`), wrong schema fields | Full validation with correct schemas | ❌ SCHEMA FIELDS MISMATCH, NO REAL VALIDATION |
| `parser/__init__.py` | Stub methods (`...`) | Full TicketParser implementation | ❌ COMPLETELY UNIMPLEMENTED |
| `repository/__init__.py` | Stub methods (`...`) | Full TicketRepository implementation | ❌ COMPLETELY UNIMPLEMENTED |

### Specific Issues Identified

1. **JSON Schema Field Mismatches:**
   - Uses `ticket_id` instead of `id`
   - Uses `failed/skipped` status values instead of `blocked/cancelled`
   - Missing `source_spec`, `source_topic_file`, `source_line_range`, `topic_sequence` fields
   - Missing array validation for `dependencies`, `file_targets`, `acceptance_criteria`

2. **Validation Function Signatures Wrong:**
   - Returns `bool` instead of `tuple[bool, list[str]]`

3. **Parser/Repository: Zero Implementation**
   - Only method signatures present
   - No business logic

---

## Step 1: Fix `smart_task/json_schema/__init__.py`

### Tasks

- [ ] Correct `TICKET_JSON_SCHEMA` field names to match `MicroTaskTicket` exactly:
  - `id` (pattern `^TASK-[A-Z]{2,4}-\d{3}$`)
  - `title`, `objective`, `spec_context`
  - `dependencies`, `file_targets` (arrays of strings)
  - `acceptance_criteria`, `verification_method`
  - `review_notes`, `blocker_reason`
  - `phase` (enum 1,2,3), `priority` (enum High/Medium/Low)
  - `estimated_effort` (enum S/M/L/XL), `tags` (array)
  - `assignee`, `wave_id`, `status` (enum pending/in_progress/completed/blocked/cancelled)

- [ ] Fix status enum: remove `failed/skipped`, use `blocked/cancelled`

- [ ] Implement `validate_ticket(data: dict) -> tuple[bool, list[str]]`:
  - Manual validation (no jsonschema dependency)
  - Return validation errors for each failed check

- [ ] Implement `validate_wave(data: dict) -> tuple[bool, list[str]]`

- [ ] Implement `validate_mapping(data: dict) -> tuple[bool, list[str]]`

---

## Step 2: Implement `smart_task/parser/__init__.py`

### Tasks

- [ ] `parse_ticket_file(path: Path) -> MicroTaskTicket`:
  - Read JSON file
  - Call `validate_ticket()`
  - If invalid: raise `ValueError` with concatenated errors
  - Return `MicroTaskTicket.from_dict(data)`

- [ ] `parse_wave_file(path: Path) -> TaskWave`:
  - Read JSON file, validate, return TaskWave

- [ ] `serialize_ticket(ticket: MicroTaskTicket) -> dict`:
  - Call `ticket.to_dict()`, validate, return

- [ ] `serialize_wave(wave: TaskWave) -> dict`:
  - Call `wave.to_dict()`, validate, return

- [ ] `write_artifact(path: Path, data: dict) -> None`:
  - Pretty-print JSON with UTF-8 encoding

### Error Handling

- [ ] File not found → raise `FileNotFoundError`
- [ ] Invalid JSON → raise `json.JSONDecodeError`
- [ ] Schema validation failure → raise `ValueError`

---

## Step 3: Implement `smart_task/repository/__init__.py`

### Tasks

- [ ] `__init__(self, db_path: Path, auto_create: bool = True)`:
  - Store `db_path`
  - If `auto_create`: call `ensure_schema()` on new connection

- [ ] `__enter__()` / `__exit__()` - Context manager

- [ ] `insert_ticket(self, ticket) -> None`: Single INSERT

- [ ] `insert_tickets_batch(self, tickets) -> int`: Transaction

- [ ] `insert_wave(self, wave) -> None`

- [ ] `get_ticket(self, ticket_id)`: SELECT by id

- [ ] `get_wave(self, wave_id)`: SELECT by id

- [ ] `list_tickets(self, phase, status, wave_id)`: Filtered SELECT

- [ ] `list_waves(self, phase, status)`: Filtered SELECT

- [ ] `update_ticket_status(self, ticket_id, status, **kwargs)`: UPDATE

- [ ] `update_wave_status(self, wave_id, status)`: UPDATE

- [ ] `delete_ticket(self, ticket_id) -> bool`: DELETE

- [ ] `count_tickets(self, phase, status) -> int`: COUNT query

- [ ] `get_ready_tickets(self, phase, limit) -> list`: Dependency-aware query

- [ ] `close(self)`: Close connection

---

## Step 4: Integration Verification

| # | Criterion |
|---|-----------|
| 1 | All 3 files importable without errors |
| 2 | `TICKET_JSON_SCHEMA` validates well-formed ticket, rejects malformed one |
| 3 | `TicketParser` round-trip works (serialize → write → read) |
| 4 | `TicketRepository` insert + get + list + update cycle on temp DB |
| 5 | `get_ready_tickets` correctly filters by dependency completion |

---

## File Structure

```
smart_task/
├── json_schema/
│   ├── __init__.py          # Facade — re-exports from sub-modules
│   ├── schemas.py           # TICKET_JSON_SCHEMA, WAVE_JSON_SCHEMA, MAPPING_JSON_SCHEMA
│   ├── validators.py        # validate_ticket(), validate_wave(), validate_mapping()
│   └── compatibility.py     # Version migration helpers (schema v1→v2→…)
├── parser/
│   ├── __init__.py          # Facade — re-exports TicketParser
│   ├── parsing.py           # TicketParser main logic (JSON I/O, serialisation)
│   └── front_matter.py      # YAML front-matter extraction from topic .md files
└── repository/
    ├── __init__.py          # Facade — re-exports TicketRepository
    ├── crud.py              # INSERT / UPDATE / DELETE operations
    ├── queries.py           # SELECT / COUNT operations with filters
    └── connection.py        # Connection management, context manager, schema init
```

---

## Test Strategy

### Philosophy
- **No gap masking** — if a capability is missing, fix the architecture, don't paper over it with trivial tests
- Every test MUST validate a real capability, not just "runs without error"
- All tests are runnable via `python -m pytest tests/ -v`

### Smoke Tests (end-to-end capability validation)
| # | Smoke Test | Validates |
|---|-----------|-----------|
| 1 | `python -c "from smart_task.json_schema import *; from smart_task.parser import *; from smart_task.repository import *"` | All modules importable without circular dependency errors |
| 2 | `validate_ticket(valid_dict)` returns `(True, [])` | Schema accepts well-formed data |
| 3 | `validate_ticket(invalid_dict)` returns `(False, [...])` with specific error messages | Schema rejects malformed data with meaningful feedback |
| 4 | Round-trip: `serialize_ticket(t) → dict → write_artifact` then `parse_ticket_file` → same `MicroTaskTicket` | Round-trip guarantee |
| 5 | `TicketRepository` on temp DB: insert → get → list → update → delete cycle | Full CRUD lifecycle |
| 6 | `insert_tickets_batch([t1, t2, t3])` in transaction | Batch atomicity |

### Behavioral Tests (capability-revealing, BDD-style)
| # | Behaviour | Given | When | Then |
|---|-----------|-------|------|------|
| 1 | Status state machine | ticket status="in_progress" | update_status("completed") | status="completed" |
| 2 | Reject invalid transition | ticket status="pending" | update_status("cancelled") | status="cancelled" (valid) |
| 3 | Reject dependency cycle | ticket depends on TASK-XXX-999 | get_ready_tickets() | ticket NOT in ready list |
| 4 | Dependency resolution | ticket T2 depends on T1 → T1 completed | get_ready_tickets() | T2 IS in ready list |
| 5 | Malformed ID rejection | ticket id="BAD-NAME" | validate_ticket() | returns False with "id" in errors |
| 6 | Empty acceptance_criteria rejection | ticket status="completed", acceptance_criteria=[] | validate_ticket() | returns False |
| 7 | Wave status cascade | all wave tickets completed | update_wave_status("completed") | valid transition |

### Gap → Architecture Fix Rule
If a test reveals a missing capability (e.g. "no validation for X"):

1. **DO NOT** write a test that passes trivially (e.g. `assert True`)
2. **DO NOT** skip the test with `@pytest.mark.skip`
3. **INSTEAD**: Identify the architectural layer where the gap belongs
   - Schema concern → `json_schema/validators.py`
   - Data access concern → `repository/queries.py`
   - Business logic concern → `parser/parsing.py`
4. Implement the capability at the correct layer
5. Then the test passes naturally

### Test Files
| File | Scope |
|------|-------|
| `tests/test_json_schema.py` | Schema definitions + validation functions |
| `tests/test_parser.py` | TicketParser (parse, serialize, round-trip) |
| `tests/test_repository.py` | TicketRepository (CRUD, queries, batch) |

---

## File-Level Modular Architecture

| Module | File Decomposition | Rationale |
|--------|-------------------|-----------|
| `json_schema/` | `__init__.py` (orchestration) → `schemas.py` (schema definitions) → `validators.py` (validation logic) → `compatibility.py` (compatibility checks) | 4 distinct concerns — schema definition, validation rules, compatibility, and orchestration MUST be separated |
| `parser/` | `__init__.py` (orchestration) → `parsing.py` (main parsing logic) → `front_matter.py` (front-matter extraction) | Front-matter parsing is a separate concern from general markdown parsing |
| `repository/` | `__init__.py` (orchestration) → `crud.py` (CRUD operations) → `queries.py` (query logic) → `connection.py` (DB connection management) | 3 architectural layers — connection management (infra), CRUD (repository), queries (read model) |

---

## Dependencies Verification

- [x] Wave 2 complete (schema.py, models.py)
- [ ] All imports from `smart_task.models` and `smart_task.schema` work
- [ ] No circular imports created