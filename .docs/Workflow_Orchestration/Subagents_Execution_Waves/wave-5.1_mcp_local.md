# Wave 5.1: MCP Local Server (stdio)

## Dependency
- Depends on: Wave 5 (CLI)
- Required by: Wave 5.2 (MCP Network/SSE), Wave 6 (topic import via MCP)

## Target
`smart_task/mcp_local/` (new package)

## Scope

Implement a **Model Context Protocol (MCP) server** that exposes smart_task's capabilities as granular MCP tools via **stdio transport only**. This enables AI clients (Claude Code, Cursor, Cline, etc.) to interact with smart_task directly — without shell commands — using structured tool calls.

The server is **thin**: no business logic. Each tool delegates to the existing repository layer from Waves 1-5.

## Architecture

```
AI Client (Claude Code / Cursor / Cline)
  │
  ├── MCP stdio protocol ──── stdin/stdout
  │
smart_task/mcp_local/
  ├── local_server.py   ← MCP stdio server + transport config
  ├── tools.py          ← Tool registrations
  ├── handlers.py       ← Handler implementations (thin wrappers)
  └── __init__.py       ← Facade (run_local_server, create_local_server)
  │
  └── smart_task core ────── Wave 1-5 modules
```

## Tools

Each tool maps to **one atomic operation** from the smart_task domain:

| MCP Tool | Maps to | Description |
|----------|---------|-------------|
| `init_database` | `ensure_schema()` | Create DB + schema at given path |
| `import_topics` | `TopicToTicketImporter.import_all()` | Import topic files → tickets using mappings |
| `list_tickets` | `TicketRepository.list_tickets()` | List tickets with phase/status/wave filters |
| `get_ticket` | `TicketRepository.get_ticket()` | Full details of a single ticket |
| `create_wave` | `WaveManager.create_wave()` | Create a new wave |
| `assign_tickets` | `WaveManager.assign_tickets()` | Assign tickets to a wave (with strategy) |
| `show_wave` | `WaveManager.get_wave_summary()` | Wave metadata + ticket details |
| `list_waves` | `TicketRepository.list_waves()` | List all waves with optional phase filter |
| `export_wave` | `WaveExporter.export_to_files()` | Export wave as markdown/JSON files |
| `update_ticket_status` | `TicketRepository.update_ticket_status()` | Change ticket status + notes/blocker |
| `get_project_stats` | `WaveManager.get_project_summary()` | Project statistics |

### Tool Design Principles

1. **Each tool is self-contained** — receives all needed parameters (no shared state between calls)
2. **Input validation** — validate parameters before delegation; return descriptive errors as MCP error messages
3. **Output as structured data** — return JSON strings (the AI client handles parsing)
4. **Stateless** — no session context; the server is stateless between invocations

## Transport

- **stdio protocol** only in this wave
- Server reads JSON-RPC messages from stdin, writes responses to stdout
- Uses `mcp` Python SDK's stdio transport

## Implementation Notes

### Dependencies

- `mcp` Python package (PyPI: `mcp>=1.0.0`)
- All existing smart_task dependencies remain unchanged

### Error Handling

- Return MCP error codes for:
  - `-32602` — Invalid params (validation failure)
  - `-32603` — Internal error (DB corruption, etc.)
- Graceful shutdown on SIGTERM/SIGINT

### Configuration

- `--db-path` parameter at server startup (or env var `SMART_TASK_DB_PATH`)
- Default DB path: `smart_task.db` in current directory

### Entry Point

- CLI entry point: `smart-task-mcp-local = "smart_task.mcp_local:main"`
- Launches stdio server for MCP client to connect

## Verification

| # | Criterion |
|---|-----------|
| 1 | `mcp_local` package importable without errors |
| 2 | Server starts and accepts stdio connection |
| 3 | `init_database` tool creates a valid SQLite DB |
| 4 | `list_tickets` returns `[]` on fresh DB |
| 5 | `create_wave` + `show_wave` round-trip returns correct wave data |
| 6 | `assign_tickets` with strategy parameter produces correct assignments |
| 7 | `update_ticket_status` with invalid status returns MCP error |
| 8 | Each tool registered and responds to `list_tools` request |

## Delivery

Package: `smart_task/mcp_local/` (4 files: `__init__.py`, `local_server.py`, `tools.py`, `handlers.py`)
