"""
SSE server wiring — creates a FastMCP app with SSE transport.

Imports handlers from ``smart_task.mcp_local.handlers`` (no duplication).
Uses FastMCP.run(transport="sse") for simplified SSE server setup.
"""

from __future__ import annotations

import logging

from mcp import McpError
from mcp.server import FastMCP
from mcp.types import ErrorData

from smart_task.mcp_local.handlers import (
    handle_assign_tickets,
    handle_create_wave,
    handle_export_wave,
    handle_get_project_stats,
    handle_get_ticket,
    handle_import_topics,
    handle_init_database,
    handle_list_tickets,
    handle_list_waves,
    handle_show_wave,
    handle_update_ticket_status,
)

logger = logging.getLogger(__name__)


def create_sse_app(repo, wm, host: str = "127.0.0.1", port: int = 8100) -> FastMCP:
    app = FastMCP("smart-task-network", host=host, port=port)

    # ------------------------------------------------------------------
    @app.tool()
    async def init_database(db_path: str = "smart_task.db") -> str:
        try:
            return handle_init_database(repo, db_path)
        except ValueError as e:
            raise McpError(ErrorData(code=-32602, message=str(e)))
        except Exception:
            logger.exception("init_database failed")
            raise McpError(ErrorData(code=-32603, message=str(e)))

    # ------------------------------------------------------------------
    @app.tool()
    async def import_topics(topic_dir: str, mappings: str) -> str:
        try:
            return handle_import_topics(repo, topic_dir, mappings)
        except ValueError as e:
            raise McpError(ErrorData(code=-32602, message=str(e)))
        except Exception:
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
            return handle_list_tickets(repo, phase, status, wave_id)
        except ValueError as e:
            raise McpError(ErrorData(code=-32602, message=str(e)))
        except Exception:
            logger.exception("list_tickets failed")
            raise McpError(ErrorData(code=-32603, message=str(e)))

    # ------------------------------------------------------------------
    @app.tool()
    async def get_ticket(ticket_id: str) -> str:
        try:
            return handle_get_ticket(repo, ticket_id)
        except ValueError as e:
            raise McpError(ErrorData(code=-32602, message=str(e)))
        except Exception:
            logger.exception("get_ticket failed")
            raise McpError(ErrorData(code=-32603, message=str(e)))

    # ------------------------------------------------------------------
    @app.tool()
    async def create_wave(wave_id: str, phase: int, description: str) -> str:
        try:
            return handle_create_wave(wm, wave_id, phase, description)
        except ValueError as e:
            raise McpError(ErrorData(code=-32602, message=str(e)))
        except Exception:
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
            return handle_assign_tickets(wm, wave_id, count, strategy)
        except ValueError as e:
            raise McpError(ErrorData(code=-32602, message=str(e)))
        except Exception:
            logger.exception("assign_tickets failed")
            raise McpError(ErrorData(code=-32603, message=str(e)))

    # ------------------------------------------------------------------
    @app.tool()
    async def show_wave(wave_id: str) -> str:
        try:
            return handle_show_wave(wm, wave_id)
        except ValueError as e:
            raise McpError(ErrorData(code=-32602, message=str(e)))
        except Exception:
            logger.exception("show_wave failed")
            raise McpError(ErrorData(code=-32603, message=str(e)))

    # ------------------------------------------------------------------
    @app.tool()
    async def list_waves(phase: int | None = None) -> str:
        try:
            return handle_list_waves(repo, phase)
        except ValueError as e:
            raise McpError(ErrorData(code=-32602, message=str(e)))
        except Exception:
            logger.exception("list_waves failed")
            raise McpError(ErrorData(code=-32603, message=str(e)))

    # ------------------------------------------------------------------
    @app.tool()
    async def export_wave(
        wave_id: str, format: str = "markdown", output_dir: str = "."
    ) -> str:
        try:
            return handle_export_wave(repo, wm, wave_id, format, output_dir)
        except ValueError as e:
            raise McpError(ErrorData(code=-32602, message=str(e)))
        except Exception:
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
            return handle_update_ticket_status(
                repo, ticket_id, status, notes, blocker
            )
        except ValueError as e:
            raise McpError(ErrorData(code=-32602, message=str(e)))
        except Exception:
            logger.exception("update_ticket_status failed")
            raise McpError(ErrorData(code=-32603, message=str(e)))

    # ------------------------------------------------------------------
    @app.tool()
    async def get_project_stats() -> str:
        try:
            return handle_get_project_stats(wm)
        except ValueError as e:
            raise McpError(ErrorData(code=-32602, message=str(e)))
        except Exception:
            logger.exception("get_project_stats failed")
            raise McpError(ErrorData(code=-32603, message=str(e)))

    return app
