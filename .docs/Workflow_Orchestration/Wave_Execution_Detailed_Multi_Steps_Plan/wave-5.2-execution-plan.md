# Wave 5.2 Execution Plan: MCP Network Server (SSE)

**Generated:** 2026-06-01
**Status:** READY FOR IMPLEMENTATION
**Dependency:** Wave 5.1 (MCP Local) COMPLETE

---

## Configuration

### MCP Network Server Configuration

| Parameter | Source | Default | Description |
|-----------|--------|---------|-------------|
| `--host` | CLI argument | `127.0.0.1` | Bind address |
| `--port` | CLI argument | `8100` | Bind port |
| `--db-path` | CLI argument | `smart_task.db` | SQLite database path |
| `SMART_TASK_DB_PATH` | Environment variable | — | DB path override |
| `find_free_port()` | `utils.port` module | OS ephemeral | Dynamic port allocation (fallback or automation) |

---

## Critical Gaps Analysis

### Current State Issues

| Component | Current Implementation | Spec Requirement | Gap |
|-----------|----------------------|-----------------|-----|
| `smart_task/mcp_network/` | **DOES NOT EXIST** | Full MCP network server with SSE transport | ❌ MISSING MODULE |
| `starlette` dependency | Not in `pyproject.toml` | ASGI web framework for SSE routes | ❌ MISSING DEPENDENCY |
| `uvicorn` dependency | Not in `pyproject.toml` | ASGI server for HTTP | ❌ MISSING DEPENDENCY |
| SSE transport | Not available | `SseServerTransport` wiring | ❌ NOT WIRED |

### Specific Issues Identified

1. **Missing Module:** `mcp_network/` directory does not exist
2. **No SSE Server Infrastructure:**
   - No Starlette app with SSE route
   - No `SseServerTransport` instance
   - No Uvicorn runner
3. **No Network Tool Wiring:**
   - Need to register same 11 tools for `"smart-task-network"` server
   - Need to wire tools to shared handlers from `mcp_local.handlers`
4. **Missing Dependencies:**
   - `starlette` not in `pyproject.toml`
   - `uvicorn` not in `pyproject.toml`

---

## Step 1: Add Dependencies

### Tasks

- [ ] Add to `pyproject.toml`:
  ```toml
  dependencies = [
      ...,
      "starlette",
      "uvicorn",
  ]
  ```
- [ ] Run `pip install -e .` to install

---

## Step 2: Create `smart_task/mcp_network/__init__.py`

### Tasks

- [ ] `run_network_server(db_path: str, host: str, port: int) -> None`:
  - Create `TicketRepository` with `db_path`
  - Create `WaveManager` with repo
  - Create Starlette app with SSE routes (calls `create_sse_app(repo, wm)`)
  - Run via `uvicorn.run(app, host=host, port=port)`
- [ ] Port resolution at startup:
  - If `--port` is `0` or `"auto"`: call `find_free_port()` to get a dynamic port (OS ephemeral)
  - Default `--port` is `8100`; user can always override
  - Log the resolved port: `"MCP Network server listening on {host}:{port}"`
  - Still wrap bind in try/except for race-condition safety
- [ ] `main()`: Parse args (`--host`, `--port`, `--db-path`), call `run_network_server()`
- [ ] Register CLI entry point in `pyproject.toml`:
  - `smart-task-mcp-network = "smart_task.mcp_network:main"`

---

## Step 3: Create `smart_task/mcp_network/network_server.py`

### Tasks

- [ ] `create_sse_app(repo: TicketRepository, wm: WaveManager) -> Starlette`:
  1. Create MCP `Server("smart-task-network")`
  2. Register all 11 tools using `mcp.server.Server.tool()` decorator
  3. Create `SseServerTransport("/messages")` instance
  4. Define routes:
     - `GET /sse` → SSE endpoint
     - `POST /messages` → message handler
  5. Return `Starlette` app with routes

### Tool Registration

Each tool follows the same pattern as Wave 5.1 (same handlers, same error handling):

```python
from smart_task.mcp_local.handlers import (
    handle_init_database,
    handle_import_topics,
    handle_list_tickets,
    handle_get_ticket,
    handle_create_wave,
    handle_assign_tickets,
    handle_show_wave,
    handle_list_waves,
    handle_export_wave,
    handle_update_ticket_status,
    handle_get_project_stats,
)
```

### SSE Server Boilerplate

```python
from mcp.server import Server
from mcp.server.sse import SseServerTransport
from starlette.applications import Starlette
from starlette.routing import Route


def create_sse_app(repo, wm) -> Starlette:
    app = Server("smart-task-network")

    @app.tool()
    async def init_database(db_path: str = "smart_task.db") -> str:
        try:
            return handle_init_database(repo, db_path)
        except ValueError as e:
            raise McpError(ErrorData(code=-32602, message=str(e)))
        except Exception as e:
            raise McpError(ErrorData(code=-32603, message=str(e)))

    # ... 10 more tools ...

    sse = SseServerTransport("/messages")

    async def handle_sse(request):
        async with sse.connect_sse(
            request.scope, request.receive, request._send
        ) as streams:
            await app.run(
                streams[0], streams[1],
                app.create_initialization_options()
            )

    return Starlette(routes=[
        Route("/sse", endpoint=handle_sse),
        Route("/messages", endpoint=sse.handle_post_message, methods=["POST"]),
    ])
```

---

## Step 4: Create `smart_task/mcp_network/__main__.py`

### Tasks

- [ ] File content:
  ```python
  from smart_task.mcp_network import main
  main()
  ```

---

## Step 5: Verification

| # | Criterion | Test |
|---|-----------|------|
| 1 | Package importable | `python -c "from smart_task.mcp_network import create_sse_app"` |
| 2 | Server starts | `python -c "from smart_task.mcp_network import run_network_server"` |
| 3 | SSE endpoint responds | `curl http://127.0.0.1:8100/sse` returns SSE headers |
| 4 | POST /messages accepts | `curl -X POST http://127.0.0.1:8100/messages -d '...'` returns 200 |
| 5 | Tool via SSE works | Send `list_tools` request → receives 11 tools in response |
| 6 | init_database via SSE | Send tool call → DB file created with schema |
| 7 | Unknown route returns 404 | `curl http://127.0.0.1:8100/nonexistent` → 404 |
| 8 | Port configurable via `--port` | Start with `--port 9090` → server binds to 9090 | Port configuration works, not just default |
| 9 | Dynamic port with `--port 0` | Start with `--port 0` → server binds to an OS-assigned port, logs it | `find_free_port()` integration works |
| 10 | Graceful shutdown | SIGTERM → server exits within 2 seconds |

---

## File-Level Modular Architecture

| Module | File Decomposition | Rationale |
|--------|-------------------|-----------|
| `mcp_network/` | `__init__.py` (facade + entry point) → `__main__.py` (`python -m` support) → `network_server.py` (SSE server + Starlette app + tool registration) | 3 distinct concerns: entry/facade, `python -m` launcher, network server infrastructure |

---

## Test Strategy

### Philosophy
- **No gap masking** — if a capability is missing, fix the architecture, don't paper over it with trivial tests
- Every test MUST validate a real capability, not just "runs without error"
- All tests are runnable via `python -m pytest tests/ -v`

### Smoke Tests (end-to-end capability validation)
| # | Smoke Test | Validates |
|---|-----------|-----------|
| 1 | `python -c "from smart_task.mcp_network import create_sse_app, run_network_server"` | Package importable without errors |
| 2 | `create_sse_app(repo, wm)` returns `Starlette` instance with routes `/sse` and `/messages` | SSE app creation works |
| 3 | Start server → `curl http://127.0.0.1:8100/sse` returns `text/event-stream` content type | SSE endpoint responds correctly |
| 4 | Send `list_tools` JSON-RPC to SSE endpoint → response contains 11 tool names | All tools registered and reachable via SSE |
| 5 | `handle_init_database` via network creates valid SQLite DB | Network transport delivers tool calls correctly |

### Behavioral Tests (capability-revealing, BDD-style)
| # | Behaviour | Given | When | Then |
|---|-----------|-------|------|------|
| 1 | SSE transport delivers tool response | Server running on `127.0.0.1:8100` | Client opens SSE connection and sends valid tool call via POST | Response delivered on SSE stream within 5 seconds |
| 2 | Invalid params return MCP error -32602 via network | Server running | Tool called with invalid param (e.g. `status="bad"`) | MCP error code `-32602` returned on SSE stream |
| 3 | HTTP 404 for unknown route | Server running | `GET /unknown` requested | HTTP 404 response returned |
| 4 | Multiple concurrent clients | Server running | Two clients open SSE connections simultaneously | Both receive correct responses independently |
| 5 | Server name is `smart-task-network` | Server instance created | Inspect `server.name` | Returns `"smart-task-network"` |
| 6 | Shared handlers work identically | Wave 5.1 completed, same handlers imported | Same tool call via network as via local | Results are identical |

### Gap -> Architecture Fix Rule
If a test reveals a missing capability (e.g. "no SSE error for network timeout"):

1. **DO NOT** write a test that passes trivially (e.g. `assert True`)
2. **DO NOT** skip the test with `@pytest.mark.skip`
3. **INSTEAD**: Identify the architectural layer where the gap belongs
   - Transport concern → `network_server.py`
   - Tool wiring concern → `network_server.py` (tool decorators)
   - Handler concern → `smart_task/mcp_local/handlers.py`
4. Implement the capability at the correct layer
5. Then the test passes naturally

### Test Files
| File | Scope |
|------|-------|
| `tests/test_mcp_network.py` | SSE app creation, route registration, handler integration, HTTP error handling |

---

## Dependencies Verification

- [ ] Wave 5.1 must be complete (`smart_task.mcp_local.handlers` available)
- [ ] `starlette` + `uvicorn` added to `pyproject.toml`
- [ ] No circular imports (`mcp_network` imports from `mcp_local.handlers` only)
- [ ] All `smart_task.models`, `smart_task.repository` imports work
- [ ] SSE transport correctly wired with MCP SDK
- [ ] `pyproject.toml` CLI entry point registered: `smart-task-mcp-network`
