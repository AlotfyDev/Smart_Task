# Wave 5.1 Execution Plan: MCP Local Server (stdio)

**Generated:** 2026-06-01
**Status:** READY FOR IMPLEMENTATION
**Dependency:** Wave 5 (CLI) COMPLETE

---

## Configuration

### MCP Local Server Configuration

| Parameter | Source | Description | Default |
|-----------|--------|-------------|---------|
| `--db-path` | CLI argument | SQLite database path | `smart_task.db` |
| `SMART_TASK_DB_PATH` | Environment variable | DB path override | — |
| `list_changed_tree` | `create_local_server()` | Tree change callback (optional) | `None` |

---

## Critical Gaps Analysis

### Current State Issues

| Component | Current Implementation | Spec Requirement | Gap |
|-----------|----------------------|-----------------|-----|
| `smart_task/mcp_local/` | **DOES NOT EXIST** | Full MCP local server with 11 tools | ❌ MISSING MODULE |
| `mcp` dependency | Not in `pyproject.toml` | `mcp>=1.0.0` | ❌ MISSING DEPENDENCY |

### Specific Issues Identified

1. **Missing Module:** `mcp_local/` directory does not exist
2. **No Server Infrastructure:**
   - No stdio `Server` instance creation
   - No stdio transport wiring
   - No tool registration mechanism
3. **No Tool Handlers:**
   - 11 tool handlers need implementation (thin wrappers over repository/wave_manager)
   - Input validation for each tool's parameters
   - Error handling with proper MCP error codes
4. **Missing Dependency:**
   - `mcp` not in `pyproject.toml` dependencies

---

## Step 1: Add `mcp` Dependency

### Tasks

- [ ] Add to `pyproject.toml`: `dependencies = [..., "mcp>=1.0.0"]`
- [ ] Run `pip install -e .` to install

---

## Step 2: Create `smart_task/mcp_local/__init__.py`

### Tasks

- [ ] `run_local_server(db_path: str) -> None`: Entry point to create and run stdio server
  - Create `TicketRepository` with `db_path`
  - Create `WaveManager` with repo
  - Call `create_local_server(repo, wave_manager)`
  - Run stdio transport loop via `mcp.server.stdio.stdio_server()`
- [ ] `create_local_server(repo: TicketRepository, wm: WaveManager) -> Server`:
  - Create MCP `Server("smart-task-local")`
  - Register all 11 tools via `server.tool()` decorator
  - Return configured server
- [ ] `main()`: Parse args, call `run_local_server()`
- [ ] Register CLI entry point in `pyproject.toml`:
  - `smart-task-mcp-local = "smart_task.mcp_local:main"`

---

## Step 3: Implement Tool Handlers in `smart_task/mcp_local/handlers.py`

### Tasks

Each handler is a thin wrapper:

- [ ] **`handle_init_database(repo, db_path: str) -> str`**
  - Call `repo.ensure_schema()`
  - Return `{"status": "ok", "db_path": db_path}` as JSON

- [ ] **`handle_import_topics(repo, topic_dir: str, mappings: str) -> str`**
  - Instantiate `TopicToTicketImporter`
  - Call `import_all(Path(topic_dir), Path(mappings))`
  - Return `{"status": "ok", "tickets_imported": count}`

- [ ] **`handle_list_tickets(repo, phase: int | None, status: str | None, wave_id: str | None) -> str`**
  - Call `repo.list_tickets(phase=phase, status=status, wave_id=wave_id)`
  - Return JSON array of ticket dicts

- [ ] **`handle_get_ticket(repo, ticket_id: str) -> str`**
  - Call `repo.get_ticket(ticket_id)`
  - Return JSON ticket dict or raise error if not found

- [ ] **`handle_create_wave(wm, wave_id: str, phase: int, description: str) -> str`**
  - Call `wm.create_wave(wave_id, phase, description)`
  - Return wave dict as JSON

- [ ] **`handle_assign_tickets(wm, wave_id: str, count: int | None, strategy: str) -> str`**
  - Call `wm.assign_tickets(wave_id, count=count, strategy=strategy)`
  - Return `{"wave_id": wave_id, "assigned": count}`

- [ ] **`handle_show_wave(wm, wave_id: str) -> str`**
  - Call `wm.get_wave_summary(wave_id)`
  - Return JSON dict

- [ ] **`handle_list_waves(repo, phase: int | None) -> str`**
  - Call `repo.list_waves(phase=phase)`
  - Return JSON array

- [ ] **`handle_export_wave(repo, wm, wave_id: str, format: str, output_dir: str) -> str`**
  - Instantiate `WaveExporter`
  - Call `export_to_files(wave_id, Path(output_dir), format)`
  - Return `{"files": [file_paths]}`

- [ ] **`handle_update_ticket_status(repo, ticket_id: str, status: str, notes: str | None, blocker: str | None) -> str`**
  - Validate status is one of `pending|in_progress|completed|blocked|cancelled`
  - Call `repo.update_ticket_status(ticket_id, status, review_notes=notes, blocker_reason=blocker)`
  - Return updated ticket JSON

- [ ] **`handle_get_project_stats(wm) -> str`**
  - Call `wm.get_project_summary()`
  - Return JSON dict

### Handler Error Convention

- Handler raises `ValueError` for invalid input → caught by tool wrapper → returns MCP error `-32602`
- Handler raises `RuntimeError` for system errors → returns MCP error `-32603`
- Handler returns JSON string in all success cases

---

## Step 4: Define Tool Metadata in `smart_task/mcp_local/tools.py`

### Tasks

- [ ] Define tool name, description, and JSON Schema for each tool's parameters
- [ ] Each tool defined with:
  - `name`: snake_case tool name
  - `description`: Clear description of what the tool does
  - `input_schema`: JSON Schema object for parameters

### Tool Definitions Structure

```python
TOOL_DEFINITIONS = {
    "init_database": {
        "description": "Initialize SQLite database with smart_task schema",
        "input_schema": {
            "type": "object",
            "properties": {
                "db_path": {"type": "string", "description": "Path to SQLite DB file"}
            },
            "required": []
        }
    },
    # ... 10 more tools
}
```

---

## Step 5: Wire Server in `smart_task/mcp_local/local_server.py`

### Tasks

- [ ] Create `Server("smart-task-local")` instance
- [ ] Register all 11 tools using `mcp.server.Server.tool()` decorator
- [ ] Each tool wrapper:
  1. Parse parameters from MCP arguments
  2. Call corresponding handler
  3. Catch `ValueError` → MCP error `-32602`
  4. Catch `Exception` → MCP error `-32603`
  5. Return result as `TextContent` with MIME type `application/json`
- [ ] Wire stdio transport via `mcp.server.stdio.stdio_server()`
- [ ] Handle SIGTERM/SIGINT for graceful shutdown
- [ ] Register `list_tools` handler (auto-provided by MCP SDK)

### Server Boilerplate Pattern

```python
app = Server("smart-task-local")

@app.tool()
async def init_database(db_path: str = "smart_task.db") -> str:
    """Initialize SQLite database with smart_task schema."""
    try:
        return handle_init_database(repo, db_path)
    except ValueError as e:
        raise McpError(ErrorData(code=-32602, message=str(e)))
    except Exception as e:
        raise McpError(ErrorData(code=-32603, message=str(e)))
```

---

## Step 6: Verification

| # | Criterion | Test |
|---|-----------|------|
| 1 | Package importable | `python -c "from smart_task.mcp_local import create_local_server"` |
| 2 | Server initializes | `python -c "from smart_task.mcp_local import create_local_server; s=create_local_server(...); print(s.name)"` |
| 3 | 11 tools registered | `list_tools` response contains all 11 tool names |
| 4 | `init_database` creates DB | Run tool → DB file exists with schema |
| 5 | `list_tickets` empty result | On fresh DB → returns `[]` |
| 6 | `create_wave` + `show_wave` round-trip | Create → show → returns matching data |
| 7 | `update_ticket_status` invalid | Invalid status → MCP error `-32602` |
| 8 | `list_waves` default | No waves → returns `[]` |
| 9 | `export_wave` file creation | Export → output file exists on disk |
| 10 | `get_project_stats` structure | Returns dict with `total_tickets` key |

---

## File-Level Modular Architecture

| Module | File Decomposition | Rationale |
|--------|-------------------|-----------|
| `mcp_local/` | `__init__.py` (facade + entry point) → `local_server.py` (stdio MCP server + tool registration) → `tools.py` (tool metadata + schemas) → `handlers.py` (handler implementations) | 4 distinct concerns: orchestration/facade, server infrastructure, tool definitions, business handlers |

---

## Test Strategy

### Philosophy
- **No gap masking** — if a capability is missing, fix the architecture, don't paper over it with trivial tests
- Every test MUST validate a real capability, not just "runs without error"
- All tests are runnable via `python -m pytest tests/ -v`

### Smoke Tests (end-to-end capability validation)
| # | Smoke Test | Validates |
|---|-----------|-----------|
| 1 | `python -c "from smart_task.mcp_local import create_local_server, run_local_server"` | All sub-modules importable without errors |
| 2 | `create_local_server(repo, wm)` returns `Server` instance with name `"smart-task-local"` | Server creation works |
| 3 | Server `list_tools` returns 11 tools with correct names | All tools registered |
| 4 | `handle_init_database` creates valid SQLite DB with tables | Database initialization via MCP |
| 5 | `handle_list_tickets` on fresh repo returns `{"tickets": []}` | Empty query returns valid structure |
| 6 | `handle_create_wave` + `handle_show_wave` round-trip | Wave lifecycle via MCP tools |
| 7 | `handle_update_ticket_status` with invalid status raises `ValueError` | Validation in handler |

### Behavioral Tests (capability-revealing, BDD-style)
| # | Behaviour | Given | When | Then |
|---|-----------|-------|------|------|
| 1 | All 11 tools respond | Server running | `list_tools` request | Response contains tools with names matching spec: `init_database`, `import_topics`, `list_tickets`, `get_ticket`, `create_wave`, `assign_tickets`, `show_wave`, `list_waves`, `export_wave`, `update_ticket_status`, `get_project_stats` |
| 2 | Invalid params return MCP error -32602 | Server running | Tool called with invalid param (e.g. `status="invalid_status"`) | MCP error with code `-32602` returned |
| 3 | System error returns MCP error -32603 | Corrupt DB file | Any tool accessing DB | MCP error with code `-32603` returned |
| 4 | Tool output is JSON | Any tool returns successfully | Inspect response content | Content type is `application/json`, parseable by `json.loads()` |
| 5 | Stateless between calls | Tool call A modifies data | Tool call B reads same data | Tool B sees the changes from tool A |
| 6 | Graceful shutdown | Server running with stdio | SIGTERM received | Server exits cleanly within 2 seconds |

### Gap -> Architecture Fix Rule
If a test reveals a missing capability (e.g. "no validation for tool parameters"):

1. **DO NOT** write a test that passes trivially (e.g. `assert True`)
2. **DO NOT** skip the test with `@pytest.mark.skip`
3. **INSTEAD**: Identify the architectural layer where the gap belongs
   - Tool registration concern → `tools.py`
   - Handler logic concern → `handlers.py`
   - Input validation concern → `handlers.py`
4. Implement the capability at the correct layer
5. Then the test passes naturally

### Test Files
| File | Scope |
|------|-------|
| `tests/test_mcp_local.py` | Server creation, tool registration, handler unit tests, error handling, stdio smoke test |

---

## Dependencies Verification

- [ ] Wave 5 must be complete (CLI, all repository functions available)
- [ ] `mcp>=1.0.0` added to `pyproject.toml`
- [ ] No circular imports (`mcp_local` doesn't import from CLI)
- [ ] All `smart_task.models`, `smart_task.repository` imports work
- [ ] Repository pattern properly integrated with server lifecycle
