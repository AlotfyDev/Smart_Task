# Wave 5.2: MCP Network Server (SSE)

## Dependency
- Depends on: Wave 5.1 (MCP Local — shares handlers and tool definitions)
- Required by: Wave 5.3 (Agentic Workflow — deferred), Wave 6 (topic import via network)

## Target
`smart_task/mcp_network/` (new package)

## Scope

Implement an **MCP Network Server** that exposes smart_task's 11 tools via **SSE (Server-Sent Events) transport** over HTTP. This enables remote AI clients to interact with smart_task across a network boundary.

The server shares the same **handler implementations** as Wave 5.1 (`smart_task.mcp_local.handlers`) — no duplication of business logic. The only additions are:

1. SSE transport wiring (Starlette app + Uvicorn server)
2. Network configuration (`--host`, `--port`)
3. CORS or security headers (if needed)

## Architecture

```
AI Client (remote — Claude Code, Cursor, Cline)
  │
  ├── HTTP SSE ──── http://host:port/sse
  │       POST ──── http://host:port/messages
  │
smart_task/mcp_network/
  ├── network_server.py   ← SSE server + Starlette app + tool wiring
  └── __init__.py         ← Facade (run_network_server, main)
  │
  ├── smart_task/mcp_local/handlers.py  ← shared handlers (imported)
  │
  └── smart_task core ────── Wave 1-5 modules
```

### Design Decision: handler reuse

Wave 5.2 **imports handlers** from `smart_task.mcp_local.handlers` rather than duplicating them. Rationale:

- The handler logic is identical (delegation to repository / wave_manager)
- Duplication would create a maintenance burden (11 handlers × 2 = 22 to keep in sync)
- The dependency is explicit: Wave 5.1 must complete before Wave 5.2 begins

If separation ever becomes necessary, handlers can be extracted to a shared `smart_task/mcp/` module.

## Transport

- **SSE (Server-Sent Events)** over HTTP
- Client opens a long-lived SSE connection at `GET /sse`
- Client sends JSON-RPC messages via `POST /messages`
- Server responds with JSON-RPC responses on the SSE stream
- Uses MCP Python SDK's `SseServerTransport`

## Tools

Identical to Wave 5.1 — all 11 tools:

| MCP Tool | Maps to |
|----------|---------|
| `init_database` | `ensure_schema()` |
| `import_topics` | `TopicToTicketImporter.import_all()` |
| `list_tickets` | `TicketRepository.list_tickets()` |
| `get_ticket` | `TicketRepository.get_ticket()` |
| `create_wave` | `WaveManager.create_wave()` |
| `assign_tickets` | `WaveManager.assign_tickets()` |
| `show_wave` | `WaveManager.get_wave_summary()` |
| `list_waves` | `TicketRepository.list_waves()` |
| `export_wave` | `WaveExporter.export_to_files()` |
| `update_ticket_status` | `TicketRepository.update_ticket_status()` |
| `get_project_stats` | `WaveManager.get_project_summary()` |

## Implementation Notes

### Dependencies

- `mcp>=1.0.0` (already in pyproject.toml from Wave 5.1)
- `starlette` — ASGI web framework for SSE routes
- `uvicorn` — ASGI server for HTTP + WebSocket

### Error Handling

- Return MCP error codes identical to Wave 5.1:
  - `-32602` — Invalid params (validation failure)
  - `-32603` — Internal error (DB corruption, etc.)
- HTTP 404 for unknown routes
- HTTP 405 for invalid methods on known routes

### Configuration

**Every parameter is configurable at startup.** The defaults are safe and convenient but never a substitute for explicit configuration. Users MUST be able to override each parameter independently.

| Parameter | Source | Default | Description |
|-----------|--------|---------|-------------|
| `--host` | CLI argument | `127.0.0.1` | Bind address (configurable, not fixed) |
| `--port` | CLI argument | `8100` | Bind port (configurable, not fixed) |
| `--db-path` | CLI argument | `smart_task.db` | SQLite database path (configurable) |
| `SMART_TASK_DB_PATH` | Environment variable | — | Alternative to `--db-path` |

Example: connecting to a specific port on a remote host:

```bash
smart-task-mcp-network --host 0.0.0.0 --port 9090 --db-path /data/project.db
```

### Port Utility

Use `utils.port.find_free_port()` for dynamic port allocation when the default `8100` is unavailable or when automation needs a guaranteed free port:

```python
from utils.port import find_free_port

port = find_free_port(preferred_range=(8000, 9000))
# or let the OS assign one:
port = find_free_port()
```

### Security

- Default bind: `127.0.0.1` (localhost only) — no external access risk
- `--host 0.0.0.0` allowed but documented as "expose to network"
- No authentication in this wave (can be added later if needed)

### Entry Point

```bash
smart-task-mcp-network --host 0.0.0.0 --port 8100 --db-path ./project.db
```

## Verification

| # | Criterion |
|---|-----------|
| 1 | `mcp_network` package importable without errors |
| 2 | Server starts and listens on configured host:port |
| 3 | `GET /sse` returns SSE response with correct headers |
| 4 | `POST /messages` accepts JSON-RPC and returns response on SSE stream |
| 5 | `init_database` tool creates a valid SQLite DB via SSE transport |
| 6 | `list_tickets` returns `[]` on fresh DB via SSE transport |
| 7 | `GET /nonexistent` returns 404 |
| 8 | Graceful shutdown on SIGTERM within 2 seconds |

## Delivery

Package: `smart_task/mcp_network/` (3 files: `__init__.py`, `__main__.py`, `network_server.py`)
Dependencies added: `starlette`, `uvicorn`
