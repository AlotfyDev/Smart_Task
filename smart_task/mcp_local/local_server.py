"""
MCP server wiring — creates FastMCP("smart-task-local") and registers 11 tools.

Each tool is a thin decorator-wrapped function that:
   1. Validates parameters
   2. Calls the corresponding handler from handlers.py
   3. Returns JSON string or raises McpError
"""

from __future__ import annotations

import logging

from mcp import McpError
from mcp.server import FastMCP
from mcp.types import ErrorData

from smart_task.mcp_local import handlers

logger = logging.getLogger(__name__)


def build_server(repo, wm) -> FastMCP:
    app = FastMCP("smart-task-local")

    # ------------------------------------------------------------------
    @app.tool()
    async def init_database(db_path: str = "smart_task.db") -> str:
        try:
            return handlers.handle_init_database(repo, db_path)
        except ValueError as e:
            raise McpError(ErrorData(code=-32602, message=str(e)))
        except Exception as e:
            logger.exception("init_database failed")
            raise McpError(ErrorData(code=-32603, message=str(e)))

    # ------------------------------------------------------------------
    @app.tool()
    async def import_topics(topic_dir: str, mappings: str) -> str:
        try:
            return handlers.handle_import_topics(repo, topic_dir, mappings)
        except ValueError as e:
            raise McpError(ErrorData(code=-32602, message=str(e)))
        except Exception as e:
            logger.exception("import_topics failed")
            raise McpError(ErrorData(code=-32603, message=str(e)))

    # ------------------------------------------------------------------
    @app.tool()
    async def list_tickets(
        phase: int | None = None,
        status: str | None = None,
        wave_id: str | None = None,
    ) -> str:
        try:
            return handlers.handle_list_tickets(repo, phase, status, wave_id)
        except ValueError as e:
            raise McpError(ErrorData(code=-32602, message=str(e)))
        except Exception as e:
            logger.exception("list_tickets failed")
            raise McpError(ErrorData(code=-32603, message=str(e)))

    # ------------------------------------------------------------------
    @app.tool()
    async def get_ticket(ticket_id: str) -> str:
        try:
            return handlers.handle_get_ticket(repo, ticket_id)
        except ValueError as e:
            raise McpError(ErrorData(code=-32602, message=str(e)))
        except Exception as e:
            logger.exception("get_ticket failed")
            raise McpError(ErrorData(code=-32603, message=str(e)))

    # ------------------------------------------------------------------
    @app.tool()
    async def create_wave(wave_id: str, phase: int, description: str) -> str:
        try:
            return handlers.handle_create_wave(wm, wave_id, phase, description)
        except ValueError as e:
            raise McpError(ErrorData(code=-32602, message=str(e)))
        except Exception as e:
            logger.exception("create_wave failed")
            raise McpError(ErrorData(code=-32603, message=str(e)))

    # ------------------------------------------------------------------
    @app.tool()
    async def assign_tickets(
        wave_id: str,
        count: int | None = None,
        strategy: str = "by_dependency",
    ) -> str:
        try:
            return handlers.handle_assign_tickets(wm, wave_id, count, strategy)
        except ValueError as e:
            raise McpError(ErrorData(code=-32602, message=str(e)))
        except Exception as e:
            logger.exception("assign_tickets failed")
            raise McpError(ErrorData(code=-32603, message=str(e)))

    # ------------------------------------------------------------------
    @app.tool()
    async def show_wave(wave_id: str) -> str:
        try:
            return handlers.handle_show_wave(wm, wave_id)
        except ValueError as e:
            raise McpError(ErrorData(code=-32602, message=str(e)))
        except Exception as e:
            logger.exception("show_wave failed")
            raise McpError(ErrorData(code=-32603, message=str(e)))

    # ------------------------------------------------------------------
    @app.tool()
    async def list_waves(phase: int | None = None) -> str:
        try:
            return handlers.handle_list_waves(repo, phase)
        except ValueError as e:
            raise McpError(ErrorData(code=-32602, message=str(e)))
        except Exception as e:
            logger.exception("list_waves failed")
            raise McpError(ErrorData(code=-32603, message=str(e)))

    # ------------------------------------------------------------------
    @app.tool()
    async def export_wave(
        wave_id: str, format: str = "markdown", output_dir: str = "."
    ) -> str:
        try:
            return handlers.handle_export_wave(repo, wm, wave_id, format, output_dir)
        except ValueError as e:
            raise McpError(ErrorData(code=-32602, message=str(e)))
        except Exception as e:
            logger.exception("export_wave failed")
            raise McpError(ErrorData(code=-32603, message=str(e)))

    # ------------------------------------------------------------------
    @app.tool()
    async def update_ticket_status(
        ticket_id: str,
        status: str,
        notes: str | None = None,
        blocker: str | None = None,
    ) -> str:
        try:
            return handlers.handle_update_ticket_status(
                repo, ticket_id, status, notes, blocker
            )
        except ValueError as e:
            raise McpError(ErrorData(code=-32602, message=str(e)))
        except Exception as e:
            logger.exception("update_ticket_status failed")
            raise McpError(ErrorData(code=-32603, message=str(e)))

    # ------------------------------------------------------------------
    @app.tool()
    async def get_project_stats() -> str:
        try:
            return handlers.handle_get_project_stats(wm)
        except ValueError as e:
            raise McpError(ErrorData(code=-32602, message=str(e)))
        except Exception as e:
            logger.exception("get_project_stats failed")
            raise McpError(ErrorData(code=-32603, message=str(e)))

    return app
