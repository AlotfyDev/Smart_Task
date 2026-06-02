"""
Tool definitions — metadata and input JSON Schemas for all 11 MCP tools.

Each entry describes one tool for documentation and future schema-driven
validation.  The actual server wiring lives in local_server.py; the handler
implementations live in handlers.py.
"""

from __future__ import annotations

TOOL_DEFINITIONS: dict[str, dict] = {
    "init_database": {
        "description": "Initialize SQLite database with smart_task schema",
        "input_schema": {
            "type": "object",
            "properties": {
                "db_path": {
                    "type": "string",
                    "description": "Path to SQLite database file (default: smart_task.db)",
                }
            },
        },
    },
    "import_topics": {
        "description": "Import topic files into tickets using mapping rules",
        "input_schema": {
            "type": "object",
            "properties": {
                "topic_dir": {
                    "type": "string",
                    "description": "Directory containing topic .md files",
                },
                "mappings": {
                    "type": "string",
                    "description": "Path to topic-to-ticket mapping JSON file",
                },
            },
            "required": ["topic_dir", "mappings"],
        },
    },
    "list_tickets": {
        "description": "List tickets with optional phase / status / wave filters",
        "input_schema": {
            "type": "object",
            "properties": {
                "phase": {
                    "type": "integer",
                    "description": "Filter by phase (1, 2, or 3)",
                },
                "status": {
                    "type": "string",
                    "description": "Filter by status (pending|in_progress|completed|blocked|cancelled)",
                    "enum": ["pending", "in_progress", "completed", "blocked", "cancelled"],
                },
                "wave_id": {
                    "type": "string",
                    "description": "Filter by wave ID",
                },
            },
        },
    },
    "get_ticket": {
        "description": "Get full details of a single ticket by ID",
        "input_schema": {
            "type": "object",
            "properties": {
                "ticket_id": {
                    "type": "string",
                    "description": "Ticket ID (e.g. TASK-IDM-001)",
                },
            },
            "required": ["ticket_id"],
        },
    },
    "create_wave": {
        "description": "Create a new wave for grouping tickets",
        "input_schema": {
            "type": "object",
            "properties": {
                "wave_id": {
                    "type": "string",
                    "description": "Unique wave identifier (e.g. wave-7)",
                },
                "phase": {
                    "type": "integer",
                    "description": "Phase number (1, 2, or 3)",
                    "enum": [1, 2, 3],
                },
                "description": {
                    "type": "string",
                    "description": "Human-readable wave description",
                },
            },
            "required": ["wave_id", "phase", "description"],
        },
    },
    "assign_tickets": {
        "description": "Assign pending tickets to a wave using a strategy",
        "input_schema": {
            "type": "object",
            "properties": {
                "wave_id": {
                    "type": "string",
                    "description": "Target wave ID",
                },
                "count": {
                    "type": "integer",
                    "description": "Number of tickets to assign (default: all ready)",
                },
                "strategy": {
                    "type": "string",
                    "description": "Assignment strategy",
                    "enum": ["by_dependency", "by_priority", "balanced"],
                    "default": "by_dependency",
                },
            },
            "required": ["wave_id"],
        },
    },
    "show_wave": {
        "description": "Show wave metadata and ticket summary",
        "input_schema": {
            "type": "object",
            "properties": {
                "wave_id": {
                    "type": "string",
                    "description": "Wave ID to inspect",
                },
            },
            "required": ["wave_id"],
        },
    },
    "list_waves": {
        "description": "List all waves with optional phase filter",
        "input_schema": {
            "type": "object",
            "properties": {
                "phase": {
                    "type": "integer",
                    "description": "Filter by phase (1, 2, or 3)",
                },
            },
        },
    },
    "export_wave": {
        "description": "Export a wave as markdown or JSON files",
        "input_schema": {
            "type": "object",
            "properties": {
                "wave_id": {
                    "type": "string",
                    "description": "Wave ID to export",
                },
                "format": {
                    "type": "string",
                    "description": "Output format",
                    "enum": ["markdown", "json"],
                    "default": "markdown",
                },
                "output_dir": {
                    "type": "string",
                    "description": "Output directory (default: current dir)",
                    "default": ".",
                },
            },
            "required": ["wave_id"],
        },
    },
    "update_ticket_status": {
        "description": "Update a ticket's status with optional notes or blocker reason",
        "input_schema": {
            "type": "object",
            "properties": {
                "ticket_id": {
                    "type": "string",
                    "description": "Ticket ID to update",
                },
                "status": {
                    "type": "string",
                    "description": "New status value",
                    "enum": ["pending", "in_progress", "completed", "blocked", "cancelled"],
                },
                "notes": {
                    "type": "string",
                    "description": "Review notes (optional)",
                },
                "blocker": {
                    "type": "string",
                    "description": "Blocker reason (sets status to blocked)",
                },
            },
            "required": ["ticket_id", "status"],
        },
    },
    "get_project_stats": {
        "description": "Get project-level statistics (totals by phase, status, priority)",
        "input_schema": {
            "type": "object",
            "properties": {},
        },
    },
}
